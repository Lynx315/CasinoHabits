import streamlit as st
import streamlit.components.v1 as components
import random
import time
from collections import Counter
import json

st.set_page_config(page_title="Slot Machine Habit System", page_icon="🎰")

# --- Initialization & State Management ---
if 'jar' not in st.session_state:
    st.session_state.jar = []
if 'active_tier' not in st.session_state:
    st.session_state.active_tier = 0
if 'bonus_active' not in st.session_state:
    st.session_state.bonus_active = False
initial_sidebar_state="expanded"

# Keys for the config/setup
CONFIG_KEYS = ['habit_name', 'clip_value', 't1_reward', 't2_reward', 't3_reward', 'jackpot_reward']

# --- Sidebar: Casino Memory Card ---
with st.sidebar:
    st.header("💾 Casino Memory Card")
    st.write("Save your progress and rewards config.")
    
    # Load Game
    uploaded_file = st.file_uploader("Load your save file (.json)", type="json")
    if uploaded_file is not None:
        if st.button("Load Data"):
            try:
                data = json.load(uploaded_file)
                # Sync Progress
                st.session_state.jar = data.get('jar', [])
                st.session_state.active_tier = data.get('active_tier', 0)
                st.session_state.bonus_active = data.get('bonus_active', False)
                # Sync Config
                for key in CONFIG_KEYS:
                    if key in data:
                        st.session_state[key] = data[key]
                        
                st.success("Everything synced! 🎰")
                time.sleep(1.2)
                st.rerun()
            except Exception:
                st.error("Invalid save file.")

    st.divider()
    
    # Save Game
    save_data = {
        'jar': st.session_state.jar,
        'active_tier': st.session_state.active_tier,
        'bonus_active': st.session_state.bonus_active,
        # Adding config items to the save file
        'habit_name': st.session_state.get('habit_name', ""),
        'clip_value': st.session_state.get('clip_value', 1),
        't1_reward': st.session_state.get('t1_reward', ""),
        't2_reward': st.session_state.get('t2_reward', ""),
        't3_reward': st.session_state.get('t3_reward', ""),
        'jackpot_reward': st.session_state.get('jackpot_reward', "")
    }
    
    st.download_button(
        label="Download Save File",
        data=json.dumps(save_data),
        file_name="my_casino_save.json",
        mime="application/json"
    )

# --- Main UI ---
st.title("🎰 The Slot Machine Habit System")

# --- 1. Setup & Rewards ---
st.header("1. Setup Your Casino")
col1, col2 = st.columns(2)
with col1:
    # binds the input  to st.session_state for saving/loading
    st.text_input("What is your habit?", placeholder="e.g., 15 Burpees", key="habit_name")
    st.number_input("Clip Value ($)", min_value=1, key="clip_value")
with col2:
    st.text_input("Tier 1 Reward", placeholder="e.g., 10 mins YouTube", key="t1_reward")
    st.text_input("Tier 2 Reward", placeholder="e.g., 1 episode of show", key="t2_reward")
    st.text_input("Tier 3 Reward", placeholder="e.g., Buy a $20 game", key="t3_reward")
    st.text_input("Jackpot Reward", placeholder="e.g., Full day off", key="jackpot_reward")

# Mapping rewards
rewards_map = {
    'Tier 1': st.session_state.get('t1_reward', ""),
    'Tier 2': st.session_state.get('t2_reward', ""),
    'Tier 3': st.session_state.get('t3_reward', ""),
    'Jackpot': st.session_state.get('jackpot_reward', "")
}

st.divider()

# --- 2.Clip Logic (The Jar) ---
st.header("2. The Jar")
COLORS = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Gold']

if st.button("Draw Clip (I did the habit!)"):
    drawn_color = random.choice(COLORS)
    st.session_state.jar.append(drawn_color)
    if drawn_color == 'Gold':
        st.success("🌟 You drew a GOLD clip! Instant Tier 3 available.")
    else:
        st.info(f"You drew a {drawn_color} clip!")

clip_counts = Counter(st.session_state.jar)
current_val = st.session_state.get('clip_value', 1)
st.write(f"**Clips in Jar:** {len(st.session_state.jar)} (Total Value: ${len(st.session_state.jar) * current_val})")

metric_cols = st.columns(len(COLORS))
for idx, color in enumerate(COLORS):
    with metric_cols[idx]:
        st.metric(label=color, value=clip_counts.get(color, 0))

st.subheader("Cash In Clips")
st.write(f"**Currently Active Tier:** {st.session_state.active_tier}")

cash_col1, cash_col2 = st.columns(2)
with cash_col1:
    available_colors = [c for c in COLORS if c in st.session_state.jar]
    if not available_colors:
        st.selectbox("Select color to cash in:", ["Jar is empty"], disabled=True)
        cash_color = None
    else:
        cash_color = st.selectbox("Select color to cash in:", available_colors)

with cash_col2:
    if st.button("Cash In", disabled=(not available_colors)):
        if cash_color == 'Gold':
            st.session_state.jar.remove('Gold')
            st.session_state.active_tier = 3
            st.success("Cashed in 1 Gold Clip! Tier 3 unlocked!")
            st.rerun()
        else:
            count = clip_counts.get(cash_color, 0)
            if count >= 3:
                for _ in range(3): st.session_state.jar.remove(cash_color)
                st.session_state.active_tier = 3
            elif count >= 2:
                for _ in range(2): st.session_state.jar.remove(cash_color)
                st.session_state.active_tier = 2
            elif count >= 1:
                st.session_state.jar.remove(cash_color)
                st.session_state.active_tier = 1
            st.rerun()

st.divider()

# --- Helpers for Pretty Animations ---
def get_slot_html(content, highlight=False):
    bg_color = "#FF4B4B" if highlight else "#1E1E24"
    text_color = "white"
    border = "3px solid #FF4B4B" if highlight else "3px solid #555"
    return f"""
    <div style='text-align: center; background-color: {bg_color}; padding: 25px; 
                border-radius: 15px; color: {text_color}; border: {border}; 
                box-shadow: 0 4px 8px rgba(0,0,0,0.2); transition: 0.3s;'>
        <h1 style='margin: 0; font-family: monospace; letter-spacing: 5px;'>{content}</h1>
    </div>
    <br>
    """

SLOT_SYMBOLS = {'Tier 1': '🍒', 'Tier 2': '🍋', 'Tier 3': '🔔', 'Bonus': '⭐', 'Jackpot': '💎'}
ALL_EMOJIS = list(SLOT_SYMBOLS.values()) + ['🍉', '7️⃣', '🍇']
MAIN_WHEEL_OPTIONS = ['Tier 1', 'Tier 2', 'Tier 3', 'Bonus', 'Jackpot']
MAIN_WHEEL_WEIGHTS = [40, 30, 20, 8, 2]

# --- 3. The Main Wheel ---
st.header("3. The Main Wheel")

if st.button("🎰 SPIN THE WHEEL", use_container_width=True):
    if st.session_state.active_tier == 0:
        st.warning("You need to cash in clips to unlock tiers before spinning!")
        st.stop()
        
    result = random.choices(MAIN_WHEEL_OPTIONS, MAIN_WHEEL_WEIGHTS, k=1)[0]
    target_symbol = SLOT_SYMBOLS[result]
    spin_placeholder = st.empty()
    
    for i in range(30):
        r1 = target_symbol if i >= 10 else random.choice(ALL_EMOJIS)
        r2 = target_symbol if i >= 20 else random.choice(ALL_EMOJIS)
        r3 = target_symbol if i >= 29 else random.choice(ALL_EMOJIS)
        spin_placeholder.markdown(get_slot_html(f"{r1} | {r2} | {r3}"), unsafe_allow_html=True)
        time.sleep(0.08)
    
    spin_placeholder.markdown(get_slot_html(f"{target_symbol} | {target_symbol} | {target_symbol}", highlight=True), unsafe_allow_html=True)
    time.sleep(0.5)
    spin_placeholder.markdown(get_slot_html(f"✨ {result.upper()} ✨", highlight=True), unsafe_allow_html=True)
    
    if result == 'Bonus':
        st.balloons()
        st.session_state.bonus_active = True
    elif result == 'Jackpot':
        st.balloons()
        st.success(f"🎉 JACKPOT! You win: {rewards_map['Jackpot']}")
        st.session_state.active_tier = 0 
    else:
        st.success(f"🎁 You win: {rewards_map.get(result, 'Nothing yet!')}")
        st.session_state.active_tier = 0 

st.divider()
st.caption("### ⚠️ THE NAKED RULE")
st.caption("Never do these rewards 'naked' again — only through the system.")

# --- Footer: Credits & Resources ---
st.markdown("### 🏗️ Credits & Resources")
st.info("This system was created by **SpoonfedStudy**.")
link_col1, link_col2 = st.columns(2)
with link_col1: st.markdown("📂 **[Download PDF](https://spoonfedstudy.kit.com/casinohabit)**")
with link_col2: st.markdown("🎥 **[Watch YouTube](https://youtu.be/Qji8_5XgMW4?si=xjZ1tFuNFLB6jJhg)**")
st.warning("DISCLAIMER: This is a fan-made project. " \
"The system used here was created by SpoonfedStudy. We have no official association with him and this project is not monetized. If you enjoy this system, please go support the original creator on his channel or download the official system PDF.")
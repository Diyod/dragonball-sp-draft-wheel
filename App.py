import streamlit as st
import pandas as pd
import random
import time  # Added for spin animation

# Load character data
@st.cache_data
def load_characters():
    df = pd.read_csv("characters.csv")
    return df

df = load_characters()

# App Title
st.title("Dragon Ball Sparking Zero - Lucky Draft")

# Initialize session state for players
if 'player_count' not in st.session_state:
    st.session_state.player_count = 2  # Default number of players
    
if 'players' not in st.session_state:
    st.session_state.players = {}
    for i in range(st.session_state.player_count):
        st.session_state.players[i] = {
            'name': f"Player {i+1}",
            'remaining_dp': 15,
            'drafted_team': []
        }

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    new_player_count = st.number_input("Number of Players", min_value=1, max_value=8, value=st.session_state.player_count)
    
    # Update player count if changed
    if new_player_count != st.session_state.player_count:
        # Add new players if count increased
        for i in range(st.session_state.player_count, new_player_count):
            st.session_state.players[i] = {
                'name': f"Player {i+1}",
                'remaining_dp': 15,
                'drafted_team': []
            }
        
        # Remove players if count decreased
        if new_player_count < st.session_state.player_count:
            for i in range(new_player_count, st.session_state.player_count):
                if i in st.session_state.players:
                    del st.session_state.players[i]
        
        st.session_state.player_count = new_player_count
    
    # Reset all button
    if st.button("Reset All Players"):
        for i in range(st.session_state.player_count):
            if i in st.session_state.players:
                st.session_state.players[i]['remaining_dp'] = 15
                st.session_state.players[i]['drafted_team'] = []
        st.rerun()

# Create player columns for the UI
cols = st.columns(st.session_state.player_count)

# Display each player in their own column
for i, col in enumerate(cols):
    if i < st.session_state.player_count and i in st.session_state.players:
        player = st.session_state.players[i]
        
        with col:
            # Name input
            player['name'] = st.text_input("Player Name", player['name'], key=f"name_{i}")
            
            # Show remaining DP
            st.subheader(f"Remaining DP: {player['remaining_dp']}")
            
            # Filter available characters based on DP
            available_chars = df[df['DP'] <= player['remaining_dp']]
            
            # Status area
            status_area = st.empty()
            
            # Spin button
            if available_chars.empty:
                status_area.warning("No characters left!")
                spin_disabled = True
            else:
                spin_disabled = False
                
            if st.button("Spin the Wheel!", key=f"spin_{i}", disabled=spin_disabled):
                status_area = st.empty()  # Ensure local placeholder for each player spin
                if not available_chars.empty:
                    spin_list = available_chars['Name'].tolist()
                    for _ in range(30):
                        status_area.markdown(f"### {random.choice(spin_list)}")
                        time.sleep(0.05)

                    selected = available_chars.sample(1).iloc[0]
                    status_area.markdown(f"### 🌟 {selected['Name']} 🌟")
                    time.sleep(0.5)

                    player['drafted_team'].append(f"{selected['Name']} (DP: {selected['DP']})")
                    player['remaining_dp'] -= selected['DP']
            
            # Show Drafted Team
            st.subheader("Team:")
            if 'drafted_team' in player:
                for idx, char in enumerate(player['drafted_team'], start=1):
                    st.write(f"{idx}. {char}")
            
            # Reset button for this player
            if st.button("Reset", key=f"reset_{i}"):
                player['remaining_dp'] = 15
                player['drafted_team'] = []
                st.rerun()

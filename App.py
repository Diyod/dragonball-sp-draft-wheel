import streamlit as st
import pandas as pd
import time
import random

# Animation duration (seconds) - change this value to adjust animation speed
ANIMATION_DURATION = 2
ANIMATION_STEPS = 10  # How many "flashes" of different characters to show

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
    # Create a dictionary for each player with their own state
    st.session_state.players = {}
    for i in range(st.session_state.player_count):
        st.session_state.players[i] = {
            'name': f"Player {i+1}",
            'remaining_dp': 15,
            'drafted_team': [],
            'animation_step': 0,
            'final_selection': None
        }

# Ensure all player entries have the required fields
for i in range(st.session_state.player_count):
    if i not in st.session_state.players:
        st.session_state.players[i] = {
            'name': f"Player {i+1}",
            'remaining_dp': 15,
            'drafted_team': [],
            'animation_step': 0,
            'final_selection': None
        }
    # Make sure all required fields exist
    fields = ['name', 'remaining_dp', 'drafted_team', 'animation_step', 'final_selection']
    for field in fields:
        if field not in st.session_state.players[i]:
            if field == 'name':
                st.session_state.players[i][field] = f"Player {i+1}"
            elif field == 'remaining_dp':
                st.session_state.players[i][field] = 15
            elif field == 'drafted_team':
                st.session_state.players[i][field] = []
            elif field == 'animation_step':
                st.session_state.players[i][field] = 0
            elif field == 'final_selection':
                st.session_state.players[i][field] = None

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
                'drafted_team': [],
                'animation_step': 0,
                'final_selection': None
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
                st.session_state.players[i]['animation_step'] = 0
                st.session_state.players[i]['final_selection'] = None
        st.rerun()

# Create player columns for the UI
cols = st.columns(st.session_state.player_count)

# Process animations and selections
for i in range(st.session_state.player_count):
    if i in st.session_state.players:
        player = st.session_state.players[i]
        
        # Handle animation for this player
        if 'animation_step' in player and player['animation_step'] > 0:
            if player['animation_step'] < ANIMATION_STEPS:
                # Still animating - increment step
                player['animation_step'] += 1
                time.sleep(ANIMATION_DURATION / ANIMATION_STEPS)  # Small delay between steps
                st.rerun()
            else:
                # Animation complete - finalize selection
                available_chars = df[df['DP'] <= player['remaining_dp']]
                if not available_chars.empty:
                    if player['final_selection'] is None:
                        player['final_selection'] = available_chars.sample(1).iloc[0]
                    
                    # Apply the selection
                    selected = player['final_selection']
                    player['drafted_team'].append(f"{selected['Name']} (DP: {selected['DP']})")
                    player['remaining_dp'] -= selected['DP']
                    player['animation_step'] = 0
                    player['final_selection'] = None
                    st.rerun()

# Display each player in their own column
for i, col in enumerate(cols):
    if i < st.session_state.player_count and i in st.session_state.players:
        player = st.session_state.players[i]
        
        with col:
            # Name input
            if 'name' in player:
                player['name'] = st.text_input("Player Name", player['name'], key=f"name_{i}")
            else:
                player['name'] = st.text_input("Player Name", f"Player {i+1}", key=f"name_{i}")
            
            # Show remaining DP
            if 'remaining_dp' in player:
                st.subheader(f"Remaining DP: {player['remaining_dp']}")
            else:
                st.subheader("Remaining DP: 15")
                player['remaining_dp'] = 15
            
            # Animation placeholder
            animation_container = st.container()
            
            with animation_container:
                # Filter available characters based on DP
                available_chars = df[df['DP'] <= player['remaining_dp']]
                
                # Show animation or final result
                if 'animation_step' in player and player['animation_step'] > 0:
                    # During animation - show random characters
                    if not available_chars.empty:
                        # Pick random characters to display
                        random_char = available_chars.sample(1).iloc[0]
                        st.markdown(f"### 🎲 {random_char['Name']} (DP: {random_char['DP']}) 🎲")
                    else:
                        st.warning("No characters available!")
                        player['animation_step'] = 0
                else:
                    # No animation running - show default message
                    st.markdown("### Ready to spin!")
            
            # Spin button
            if available_chars.empty:
                st.warning("No characters left!")
                spin_disabled = True
            else:
                spin_disabled = 'animation_step' in player and player['animation_step'] > 0
                
            if st.button("Spin the Wheel!", key=f"spin_{i}", disabled=spin_disabled):
                if not available_chars.empty and ('animation_step' not in player or player['animation_step'] == 0):
                    # Start animation
                    player['animation_step'] = 1
                    # Pre-determine the final character for consistency
                    player['final_selection'] = available_chars.sample(1).iloc[0]
                    st.rerun()
            
            # Show Drafted Team
            st.subheader("Team:")
            if 'drafted_team' in player:
                for idx, char in enumerate(player['drafted_team'], start=1):
                    st.write(f"{idx}. {char}")
            else:
                player['drafted_team'] = []
            
            # Reset button for this player
            if st.button("Reset", key=f"reset_{i}"):
                player['remaining_dp'] = 15
                player['drafted_team'] = []
                player['animation_step'] = 0
                player['final_selection'] = None
                st.rerun()

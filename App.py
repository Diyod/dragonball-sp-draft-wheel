import streamlit as st
import pandas as pd
import time
import random

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
    st.session_state.players = {
        i: {
            'name': f"Player {i+1}",
            'remaining_dp': 15,
            'drafted_team': [],
            'is_spinning': False,
            'spin_result': None,
            'animation_placeholder': None
        } for i in range(st.session_state.player_count)
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
                'drafted_team': [],
                'is_spinning': False,
                'spin_result': None,
                'animation_placeholder': None
            }
        
        # Remove players if count decreased
        if new_player_count < st.session_state.player_count:
            for i in range(new_player_count, st.session_state.player_count):
                if i in st.session_state.players:
                    del st.session_state.players[i]
        
        st.session_state.player_count = new_player_count
    
    # Animation speed setting
    animation_duration = st.slider("Animation Duration (seconds)", min_value=1, max_value=5, value=3)
    
    # Reset all button
    if st.button("Reset All Players"):
        for i in range(st.session_state.player_count):
            st.session_state.players[i]['remaining_dp'] = 15
            st.session_state.players[i]['drafted_team'] = []
            st.session_state.players[i]['is_spinning'] = False
            st.session_state.players[i]['spin_result'] = None
        st.rerun()

# Create player columns for the UI
cols = st.columns(st.session_state.player_count)

# Display each player in their own column
for i, col in enumerate(cols):
    if i < st.session_state.player_count:
        player = st.session_state.players[i]
        
        with col:
            # Name input
            player['name'] = st.text_input("Player Name", player['name'], key=f"name_{i}")
            
            # Show remaining DP
            st.subheader(f"Remaining DP: {player['remaining_dp']}")
            
            # Create a placeholder for animation
            animation_placeholder = st.empty()
            player['animation_placeholder'] = animation_placeholder
            
            # Filter available characters based on DP
            available_chars = df[df['DP'] <= player['remaining_dp']]
            
            # Display current animation or result
            if player['is_spinning']:
                # Create animation effect
                with animation_placeholder.container():
                    # Show random characters during animation
                    sample_chars = available_chars.sample(min(5, len(available_chars)))
                    st.markdown("**Spinning...**")
                    for _, char_row in sample_chars.iterrows():
                        st.markdown(f"**{char_row['Name']} (DP: {char_row['DP']})**")
                
                # Finish the animation after a delay
                time.sleep(animation_duration / 5)  # Split animation into 5 phases
                
                if animation_duration <= 0:
                    # Animation finished
                    selected = available_chars.sample(1).iloc[0]
                    player['spin_result'] = selected
                    player['is_spinning'] = False
                    player['drafted_team'].append(f"{selected['Name']} (DP: {selected['DP']})")
                    player['remaining_dp'] -= selected['DP']
                    st.rerun()
            
            elif player['spin_result'] is not None:
                # Show the final result
                with animation_placeholder.container():
                    st.success(f"Selected: **{player['spin_result']['Name']}** (DP: {player['spin_result']['DP']})")
                
                # Reset spin result for next spin
                player['spin_result'] = None
            
            # Spin button for this player
            if available_chars.empty:
                st.warning("No characters left!")
                spin_disabled = True
            else:
                spin_disabled = False
                
            if st.button("Spin the Wheel!", key=f"spin_{i}", disabled=spin_disabled or player['is_spinning']):
                if not available_chars.empty and not player['is_spinning']:
                    player['is_spinning'] = True
                    st.session_state.animation_duration = animation_duration
                    st.rerun()
            
            # Show Drafted Team
            st.subheader("Team:")
            for idx, char in enumerate(player['drafted_team'], start=1):
                st.write(f"{idx}. {char}")
            
            # Reset button for this player
            if st.button("Reset", key=f"reset_{i}"):
                player['remaining_dp'] = 15
                player['drafted_team'] = []
                player['is_spinning'] = False
                player['spin_result'] = None
                st.rerun()

import streamlit as st
import pandas as pd

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
            'drafted_team': []
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
            st.session_state.players[i]['remaining_dp'] = 15
            st.session_state.players[i]['drafted_team'] = []
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
            
            # Filter available characters based on DP
            available_chars = df[df['DP'] <= player['remaining_dp']]
            
            # Spin button for this player
            if available_chars.empty:
                st.warning("No characters left!")
                spin_disabled = True
            else:
                spin_disabled = False
                
            if st.button("Spin the Wheel!", key=f"spin_{i}", disabled=spin_disabled):
                if not available_chars.empty:
                    selected = available_chars.sample(1).iloc[0]
                    player['drafted_team'].append(f"{selected['Name']} (DP: {selected['DP']})")
                    player['remaining_dp'] -= selected['DP']
                    st.session_state.players[i] = player  # Update player data
            
            # Show Drafted Team
            st.subheader("Team:")
            for idx, char in enumerate(player['drafted_team'], start=1):
                st.write(f"{idx}. {char}")
            
            # Reset button for this player
            if st.button("Reset", key=f"reset_{i}"):
                player['remaining_dp'] = 15
                player['drafted_team'] = []
                st.session_state.players[i] = player  # Update player data
                st.rerun()

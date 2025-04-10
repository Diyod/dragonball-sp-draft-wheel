import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="DB Sparking Zero - Tournament Draft", page_icon="🔥", layout="wide")

# Load characters
df = pd.read_csv("characters.csv")

st.markdown("""
    <style>
        .title {
            font-size:50px;
            color: orange;
            text-align: center;
            font-weight: bold;
        }
        .player-name {
            font-size:24px;
            color: #00BFFF;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Dragon Ball Sparking Zero - Tournament Draft</div>', unsafe_allow_html=True)

if 'players' not in st.session_state:
    st.session_state.players = {}

col1, col2 = st.columns([2, 1])

with col1:
    player_name = st.text_input("Enter Player Name")
    if st.button("Add Player") and player_name:
        if player_name not in st.session_state.players:
            st.session_state.players[player_name] = {"remaining_dp": 15, "drafted_team": []}

with col2:
    if st.button("Reset All"):
        st.session_state.players = {}
        st.rerun()

st.markdown("---")

# Display players dynamically
for player in st.session_state.players.keys():
    player_data = st.session_state.players[player]

    with st.container():
        st.markdown(f'<div class="player-name">{player}</div>', unsafe_allow_html=True)
        st.write(f"Remaining DP: {player_data['remaining_dp']}")

        available_chars = df[df['DP'] <= player_data['remaining_dp']]

        colA, colB = st.columns(2)

        with colA:
            if not available_chars.empty:
                if st.button(f"Spin the Wheel ({player})"):
                    selected = available_chars.sample(1).iloc[0]
                    player_data['drafted_team'].append(selected['Name'])
                    player_data['remaining_dp'] -= selected['DP']
                    st.rerun()
            else:
                st.warning("No characters left with enough DP!")

        with colB:
            if st.button(f"Reset {player}"):
                st.session_state.players[player] = {"remaining_dp": 15, "drafted_team": []}
                st.rerun()

        st.write("Drafted Team:")
        for idx, char_name in enumerate(player_data['drafted_team'], start=1):
            char_dp = df[df['Name'] == char_name]['DP'].values[0]
            st.write(f"{idx}. {char_name} (DP: {char_dp})")

        st.markdown("---")

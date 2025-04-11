import streamlit as st
import pandas as pd
import random
import pickle
import os

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
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Dragon Ball Sparking Zero - Tournament Draft</div>', unsafe_allow_html=True)

SAVE_FILE = 'players.pkl'

# Load saved players if exist
if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, 'rb') as f:
        st.session_state.players = pickle.load(f)

if 'players' not in st.session_state:
    st.session_state.players = {}

player_colors = ["#00BFFF", "#FF1493", "#32CD32", "#FFA500", "#FF4500", "#9400D3"]

with st.form(key='add_player_form', clear_on_submit=True):
    new_player_name = st.text_input("Enter Player Name")
    submitted = st.form_submit_button("Add Player")

    if submitted and new_player_name:
        player_name = new_player_name.strip()
        if player_name and player_name not in st.session_state.players:
            st.session_state.players[player_name] = {"remaining_dp": 15, "drafted_team": []}
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(st.session_state.players, f)

if st.button("Reset All Drafts"):
    for player in st.session_state.players.keys():
        st.session_state.players[player] = {"remaining_dp": 15, "drafted_team": []}
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(st.session_state.players, f)
    st.rerun()

if st.button("Remove All Players"):
    st.session_state.players = {}
    with open(SAVE_FILE, 'wb') as f:
        pickle.dump(st.session_state.players, f)
    st.rerun()

st.markdown("---")

if len(st.session_state.players) > 0:
    player_columns = st.columns(len(st.session_state.players))

    for idx, (player, col) in enumerate(zip(st.session_state.players.keys(), player_columns)):
        player_data = st.session_state.players[player]
        color = player_colors[idx % len(player_colors)]

        with col:
            st.markdown(f'<div class="player-name" style="color:{color}">{player}</div>', unsafe_allow_html=True)
            st.write(f"Remaining DP: {player_data['remaining_dp']}")

            available_chars = df[df['DP'] <= player_data['remaining_dp']]

            if not available_chars.empty:
                if st.button(f"Spin ({player})"):
                    selected = available_chars.sample(1).iloc[0]
                    player_data['drafted_team'].append(selected['Name'])
                    player_data['remaining_dp'] -= selected['DP']
                    with open(SAVE_FILE, 'wb') as f:
                        pickle.dump(st.session_state.players, f)
                    st.rerun()
            else:
                st.warning("No characters left with enough DP!")

            if st.button(f"Reset {player}"):
                st.session_state.players[player] = {"remaining_dp": 15, "drafted_team": []}
                with open(SAVE_FILE, 'wb') as f:
                    pickle.dump(st.session_state.players, f)
                st.rerun()

            st.write("Drafted Team:")
            for idx, char_name in enumerate(player_data['drafted_team'], start=1):
                char_dp = df[df['Name'] == char_name]['DP'].values[0]
                st.write(f"{idx}. {char_name} (DP: {char_dp})")

st.markdown("---")

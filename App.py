import streamlit as st
import pandas as pd
import random

# Load character data
@st.cache_data
def load_characters():
    df = pd.read_csv("characters.csv")
    return df

df = load_characters()

# App Title
st.title("Dragon Ball Sparking! Zero - Lucky Draft")

# Session State
if 'remaining_dp' not in st.session_state:
    st.session_state.remaining_dp = 15
if 'drafted_team' not in st.session_state:
    st.session_state.drafted_team = []

# Show remaining DP
st.subheader(f"Remaining DP: {st.session_state.remaining_dp}")

# Filter available characters based on DP
available_chars = df[df['DP'] <= st.session_state.remaining_dp]

if available_chars.empty:
    st.warning("No characters left with enough DP!")
else:
   if st.button("Spin the Wheel!"):
    selected = available_chars.sample(1).iloc[0]
    st.session_state.drafted_team.append(selected['Name'])
    st.session_state.remaining_dp -= selected['DP']
    st.rerun()  # Force refresh after spin


# Show Drafted Team
st.subheader("Your Drafted Team:")
for idx, char in enumerate(st.session_state.drafted_team, start=1):
    st.write(f"{idx}. {char}")

# Reset Button
if st.button("Reset"):
    st.session_state.remaining_dp = 15
    st.session_state.drafted_team = []
    st.experimental_rerun()

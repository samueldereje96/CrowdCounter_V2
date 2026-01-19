import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh
from matplotlib.dates import DateFormatter

DB_PATH = "data/occupancy.db"
TEMP_THRESHOLD = 26
REFRESH_INTERVAL = 2  # seconds

# --------------------------
# FUNCTIONS
# --------------------------
def read_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM occupancy_logs ORDER BY timestamp DESC LIMIT 100", conn)
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[::-1]  # reverse to chronological order
    return df

def get_ac_state(temp, threshold):
    return "ON" if temp >= threshold else "OFF"

# --------------------------
# DASHBOARD LAYOUT
# --------------------------
st.set_page_config(page_title="Crowd Counter Dashboard", layout="wide")
st.title("Crowd Counter Dashboard")
st.subheader("Live occupancy, temperature & AC status")

# --- Adjust AC temperature threshold on main page ---
TEMP_THRESHOLD = st.slider("AC Temperature Threshold (°C)", 20, 30, TEMP_THRESHOLD)
st.markdown("---")

# Auto-refresh
st_autorefresh(interval=REFRESH_INTERVAL * 1000, limit=None, key="dashboard_autorefresh")

df = read_db()

if df.empty:
    st.warning("No data in DB yet")
else:
    # --------------------------
    # Live metrics
    # --------------------------
    current_count = df['current_count'].iloc[-1]
    avg_occupancy = df['avg_occupancy'].iloc[-1]
    max_occupancy = df['max_occupancy'].iloc[-1]
    temperature = df['temperature'].iloc[-1]
    ac_state = get_ac_state(temperature, TEMP_THRESHOLD)
    limit_exceeded = max_occupancy > 1  # example logic

    # --- Metrics in columns with color-coded boxes ---
    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("Current Count", current_count, "green" if current_count <= 1 else "red"),
        ("Average Occupancy", f"{avg_occupancy:.2f}", "green" if avg_occupancy <= 1 else "red"),
        ("Max Occupancy", max_occupancy, "green" if not limit_exceeded else "red"),
        ("Temperature (°C)", f"{temperature:.1f}", "red" if ac_state=="ON" else "green"),
        ("AC State", ac_state, "red" if ac_state=="ON" else "green")
    ]
    for col, (label, value, color) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.markdown(
                f"""
                <div style="border:2px solid {color}; border-radius:10px; padding:15px; text-align:center; background-color:#f0f0f0;">
                    <h4 style="margin:0;">{label}</h4>
                    <p style="font-size:24px; margin:5px 0; font-weight:bold;">{value}</p>
                </div>
                """, unsafe_allow_html=True
            )

    st.markdown("---")

    # --------------------------
    # Charts in two columns
    # --------------------------
    chart_col1, chart_col2 = st.columns(2)

    # Occupancy plot
    with chart_col1:
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(df['timestamp'], df['current_count'], label="Current Count", color="blue", linewidth=2)
        ax.plot(df['timestamp'], df['avg_occupancy'], label="Average Occupancy", color="green", linewidth=2)
        ax.set_ylabel("People Count")
        ax.set_title("Occupancy Over Time")
        ax.legend()
        ax.grid(True)
        date_form = DateFormatter("%H:%M:%S")
        ax.xaxis.set_major_formatter(date_form)
        st.pyplot(fig)

    # Temperature plot
    with chart_col2:
        fig, ax = plt.subplots(figsize=(6,4))
        ax.plot(df['timestamp'], df['temperature'], label="Temperature", color="red", linewidth=2)
        ax.axhline(TEMP_THRESHOLD, color="orange", linestyle="--", label="AC Threshold")
        ax.set_ylabel("Temperature (°C)")
        ax.set_xlabel("Time")
        ax.set_title("Temperature Over Time")
        ax.legend()
        ax.grid(True)
        ax.xaxis.set_major_formatter(date_form)
        st.pyplot(fig)

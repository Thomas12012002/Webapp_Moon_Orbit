import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image

# Load images for Earth and Moon
earth_image = Image.open("earth.jpg")  # Replace with a real Earth image
moon_image = Image.open("moon.jpg")  # Replace with a real Moon image

# Constants
MOON_ORBIT_RADIUS = 384400  # Average Earth-Moon distance in km
MOON_ORBIT_PERIOD = 27.32  # in days
MOON_PHASES = [
    "🌑 New Moon", "🌒 Waxing Crescent", "🌓 First Quarter", "🌔 Waxing Gibbous",
    "🌕 Full Moon", "🌖 Waning Gibbous", "🌗 Last Quarter", "🌘 Waning Crescent"
]

# Function to calculate Moon's position in orbit
def calculate_moon_position(day):
    angle = 2 * np.pi * (day / MOON_ORBIT_PERIOD)  # Orbital position in radians
    x = MOON_ORBIT_RADIUS * np.cos(angle)  # x-coordinate in orbit
    y = MOON_ORBIT_RADIUS * np.sin(angle)  # y-coordinate in orbit
    return x, y

# Function to determine lunar phase
def determine_moon_phase(day):
    phase_index = int((day / MOON_ORBIT_PERIOD * 8) % 8)
    return MOON_PHASES[phase_index]

# Function to plot the Moon orbit with sunlight coming from the east
def plot_moon_orbit(current_day):
    # Calculate Moon position
    moon_x, moon_y = calculate_moon_position(current_day)
    moon_phase = determine_moon_phase(current_day)

    # Set up the figure
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_facecolor("black")
    ax.set_xlim(-450000, 450000)
    ax.set_ylim(-450000, 450000)

    # Add Earth with texture
    earth_box = OffsetImage(earth_image, zoom=0.15)
    earth_ab = AnnotationBbox(earth_box, (0, 0), frameon=False)
    ax.add_artist(earth_ab)

    # Draw Moon's orbit
    orbit = plt.Circle((0, 0), MOON_ORBIT_RADIUS, color="white", linestyle="--", fill=False)
    ax.add_artist(orbit)

    # Add Moon with texture
    moon_box = OffsetImage(moon_image, zoom=0.05)
    moon_ab = AnnotationBbox(moon_box, (moon_x, moon_y), frameon=False)
    ax.add_artist(moon_ab)

    # Add Cardinal Directions (N, E, S, W) in red
    cardinal_directions = {
        "N": (0, MOON_ORBIT_RADIUS + 50000),
        "E": (MOON_ORBIT_RADIUS + 50000, 0),
        "S": (0, -MOON_ORBIT_RADIUS - 50000),
        "W": (-MOON_ORBIT_RADIUS - 50000, 0),
    }
    for direction, (x, y) in cardinal_directions.items():
        ax.text(x, y, direction, color="red", fontsize=14, ha="center", va="center", fontweight="bold")

    # Annotate Moon phase
    ax.annotate(f"Phase: {moon_phase}",
                xy=(moon_x, moon_y),
                xytext=(moon_x + 50000, moon_y + 50000),
                color="#FFD700",  # Bright yellow color
                fontsize=12,
                arrowprops=dict(facecolor="white", arrowstyle='->'))

    # Draw Sunlight Arrow (coming from the east)
    arrow_start_x = MOON_ORBIT_RADIUS + 100000  # Position of the Sun (east)
    arrow_end_x = 0  # Pointing toward Earth
    for offset in [-50000, 0, 50000]:  # Three arrows aligned vertically
        ax.annotate("",
                    xy=(arrow_end_x, offset),  # Toward Earth
                    xytext=(arrow_start_x, offset),  # From the Sun
                    arrowprops=dict(facecolor="yellow", edgecolor="yellow", arrowstyle="->", lw=2))

    # Title
    ax.set_title("Moon Orbit Simulation 🌕", color="white", fontsize=14)
    ax.tick_params(colors="white")
    ax.spines[:].set_color("white")

    return fig, moon_phase

# Streamlit app layout
st.set_page_config(layout="wide")
st.title("🌍 Moon Orbit Simulation 🌕")

# Sidebar parameters with icons
with st.sidebar:
    st.header("🛠️ Simulation Controls")
    if "current_day" not in st.session_state:
        st.session_state.current_day = 0.0
    increment = st.button("➕ Increase Day")
    reset = st.button("🔄 Reset Day")
    if increment:
        st.session_state.current_day += 1
        if st.session_state.current_day > MOON_ORBIT_PERIOD:
            st.session_state.current_day = 0.0
    if reset:
        st.session_state.current_day = 0.0
    current_day = st.session_state.current_day
    st.write(f"📅 **Current Day**: {current_day:.1f}")

# Simulation logic
fig, moon_phase = plot_moon_orbit(current_day)
st.pyplot(fig)

# Display Moon phase with explanation
st.markdown(
    f"""
    <div style="background-color:#1E1E1E; padding:10px; border-radius:5px; text-align:center;">
        <h3 style="color:#FFD700;">🌕 Current Lunar Phase</h3>
        <p style="color:white; font-size:16px;">{moon_phase}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Explanation and details
with st.container():
    st.markdown("""
    ## 📖 About the Simulation
    This app simulates the Moon's orbit around Earth. The Moon's position and phase are calculated based on the day in its orbit.

    ### 🌑 Lunar Phases:
    - **New Moon**: The Moon is between Earth and the Sun, and its dark side faces Earth.
    - **Full Moon**: The Moon is opposite the Sun, and its illuminated side faces Earth.
    - **Crescent and Gibbous Phases**: The Moon is partly illuminated as it transitions between New and Full phases.
    - **Quarter Phases**: Half of the Moon's surface is visible (First and Last Quarter).

    ### Features:
    - **Sunlight Source**: The Sun is positioned to the east.
    - **Cardinal Directions (N, E, S, W)**: Displayed in red for orientation.
    - **Day Control**: Use the buttons to increment or reset the day.
    - **Orbit Period**: 27.32 days.
    """)

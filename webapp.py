import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

# Load images for Earth and Moon
earth_image = Image.open("earth.jpg")  # Earth image file
moon_texture = Image.open("moon.jpg")  # Moon image file

# Constants
MOON_ORBIT_RADIUS = 384400  # Average Earth-Moon distance in km
MOON_ORBIT_PERIOD = 27.32  # in days
EARTH_ROTATION_PERIOD = 24  # in hours
MOON_PHASES = [
    "🌑 New Moon", "🌒 Waxing Crescent", "🌓 First Quarter", "🌔 Waxing Gibbous",
    "🌕 Full Moon", "🌖 Waning Gibbous", "🌗 Last Quarter", "🌘 Waning Crescent"
]

TIME_ZONES = {
    "GMT": 0,
    "New York (EST)": -5,
    "London (GMT)": 0,
    "Beijing (CST)": 8,
    "Sydney (AEDT)": 11,
}

# Function to calculate Moon's position in orbit
def calculate_moon_position(day):
    angle = 2 * np.pi * (day / MOON_ORBIT_PERIOD)  # Orbital position in radians
    x = MOON_ORBIT_RADIUS * np.cos(angle)  # x-coordinate in orbit
    y = MOON_ORBIT_RADIUS * np.sin(angle)  # y-coordinate in orbit
    return x, y, angle

# Function to determine lunar phase
def determine_moon_phase(day):
    phase_index = int((day / MOON_ORBIT_PERIOD * 8) % 8)
    return MOON_PHASES[phase_index]

# Function to create a lit Moon image
def create_moon_image(moon_angle):
    moon_image = moon_texture.copy()
    draw = ImageDraw.Draw(moon_image)
    width, height = moon_image.size

    # Calculate lit area based on the phase
    lit_ratio = 0.5 * (1 + np.cos(moon_angle))  # Fraction of the Moon illuminated
    lit_width = int(lit_ratio * width)

    # Shade the shadowed area
    draw.rectangle([lit_width, 0, width, height], fill="black")
    return moon_image

# Function to plot the Moon orbit and Earth
def plot_moon_orbit(current_day, time_zone_offset):
    # Calculate Moon position
    moon_x, moon_y, moon_angle = calculate_moon_position(current_day)
    moon_phase = determine_moon_phase(current_day)

    # Calculate time of day
    current_hour = (current_day * EARTH_ROTATION_PERIOD / MOON_ORBIT_PERIOD + time_zone_offset) % EARTH_ROTATION_PERIOD
    formatted_time = f"{int(current_hour):02d}:{int((current_hour % 1) * 60):02d}"

    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ax.set_facecolor("black")

    # Dynamically adjust axis limits based on Moon's orbit and Earth
    orbit_limit = MOON_ORBIT_RADIUS * 1.2
    ax.set_xlim(-orbit_limit, orbit_limit)
    ax.set_ylim(-orbit_limit, orbit_limit)

    # Draw Earth
    ax.imshow(earth_image, extent=[-20000, 20000, -20000, 20000])

    # Draw Moon's orbit
    orbit = plt.Circle((0, 0), MOON_ORBIT_RADIUS, color="white", linestyle="--", fill=False)
    ax.add_artist(orbit)

    # Add Moon
    ax.imshow(moon_texture, extent=[moon_x - 15000, moon_x + 15000, moon_y - 15000, moon_y + 15000])

    # Add Cardinal Directions
    directions = {"N": (0, orbit_limit - 50000), 
                  "E": (orbit_limit - 50000, 0), 
                  "S": (0, -orbit_limit + 50000), 
                  "W": (-orbit_limit + 50000, 0)}
    for label, (dx, dy) in directions.items():
        ax.text(dx, dy, label, color="red", fontsize=14, ha="center", va="center", fontweight="bold")

    # Add time of day in the lower-right corner
    ax.text(orbit_limit - 100000, -orbit_limit + 50000, f"Time: {formatted_time}",
            color="white", fontsize=14, ha="right", va="center", fontweight="bold")

    # Title
    ax.set_title("Moon Orbit Simulation 🌕", color="white", fontsize=14)

    return fig, moon_phase, formatted_time

# Streamlit layout
st.set_page_config(layout="wide")
st.title("🌍 Moon Orbit Simulation 🌕")

# Sidebar controls
with st.sidebar:
    st.header("🛠️ Controls")

    # Time zone selection
    time_zone = st.selectbox("🌐 Select Your Location", list(TIME_ZONES.keys()))
    time_zone_offset = TIME_ZONES[time_zone]

    # Day control
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

# Moon phase and lit Moon image
moon_phase = determine_moon_phase(current_day)
lit_moon_image = create_moon_image(2 * np.pi * (current_day / MOON_ORBIT_PERIOD))
st.image(lit_moon_image, caption=f"Moon Phase: {moon_phase}", width=300)

# Orbit and time simulation
fig, moon_phase, formatted_time = plot_moon_orbit(current_day, time_zone_offset)
st.pyplot(fig)

# Explanation
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

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
EARTH_RADIUS = 20000  # Radius of Earth in the visualization
MOON_RADIUS = 15000  # Radius of Moon in the visualization
STICKMAN_SIZE = 2000  # Size of the stickman around Earth
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

# Initialize Streamlit session state variables
if "current_day" not in st.session_state:
    st.session_state.current_day = 0.0
if "person_position" not in st.session_state:
    st.session_state.person_position = 0  # Angle (0 = Noon, 90 = 6 PM, etc.)
if "time_zone_offset" not in st.session_state:
    st.session_state.time_zone_offset = TIME_ZONES["GMT"]

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

# Function to calculate time of day based on stickman's position
def calculate_time_of_day(person_position, time_zone_offset):
    # Convert Earth's rotation (angle) to a 24-hour clock
    hour = ((person_position % 360) / 360 * 24 + time_zone_offset) % 24  # Adjust for time zone
    formatted_time = f"{int(hour):02d}:{int((hour % 1) * 60):02d}"  # HH:MM format
    return formatted_time

# Function to create a lit Moon image
def create_moon_image(moon_angle):
    """Generate a Moon image with the lit side dynamically based on its phase."""
    moon_image = moon_texture.copy()
    draw = ImageDraw.Draw(moon_image)
    width, height = moon_image.size

    # Calculate the illuminated area of the Moon based on the phase
    lit_ratio = 0.5 * (1 + np.cos(moon_angle))  # Fraction of the Moon illuminated
    lit_width = int(lit_ratio * width)

    # Shade the shadowed area
    draw.rectangle([lit_width, 0, width, height], fill="black")
    return moon_image

# Function to draw a stickman
def draw_stickman(ax, x, y, size):
    """Draws a stickman at the given x, y position with a specific size."""
    # Head (circle)
    head = plt.Circle((x, y + size * 0.5), size * 0.2, color="yellow", fill=True)
    ax.add_artist(head)

    # Body (line)
    ax.plot([x, x], [y, y + size * 0.5], color="yellow", lw=2)

    # Arms (line)
    ax.plot([x - size * 0.3, x + size * 0.3], [y + size * 0.25, y + size * 0.25], color="yellow", lw=2)

    # Legs (lines)
    ax.plot([x, x - size * 0.2], [y, y - size * 0.3], color="yellow", lw=2)
    ax.plot([x, x + size * 0.2], [y, y - size * 0.3], color="yellow", lw=2)

# Function to plot the Moon orbit, Earth, and stickman
def plot_moon_orbit(current_day, person_position, time_zone_offset):
    # Calculate Moon position
    moon_x, moon_y, moon_angle = calculate_moon_position(current_day)
    moon_phase = determine_moon_phase(current_day)

    # Set up the figure
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")
    ax.set_facecolor("black")

    # Dynamically adjust axis limits based on Moon's orbit and Earth
    orbit_limit = MOON_ORBIT_RADIUS * 1.2
    ax.set_xlim(-orbit_limit, orbit_limit)
    ax.set_ylim(-orbit_limit, orbit_limit)

    # Draw Earth
    ax.imshow(earth_image, extent=[-EARTH_RADIUS, EARTH_RADIUS, -EARTH_RADIUS, EARTH_RADIUS])

    # Draw Moon's orbit
    orbit = plt.Circle((0, 0), MOON_ORBIT_RADIUS, color="white", linestyle="--", fill=False)
    ax.add_artist(orbit)

    # Add Moon
    lit_moon_image = create_moon_image(moon_angle)
    ax.imshow(lit_moon_image, extent=[moon_x - MOON_RADIUS, moon_x + MOON_RADIUS, moon_y - MOON_RADIUS, moon_y + MOON_RADIUS])

    # Add Cardinal Directions
    directions = {"N": (0, orbit_limit - 50000), 
                  "E": (orbit_limit - 50000, 0), 
                  "S": (0, -orbit_limit + 50000), 
                  "W": (-orbit_limit + 50000, 0)}
    for label, (dx, dy) in directions.items():
        ax.text(dx, dy, label, color="red", fontsize=14, ha="center", va="center", fontweight="bold")

    # Calculate stickman's position
    person_angle_rad = np.deg2rad(person_position)
    person_x = EARTH_RADIUS * np.cos(person_angle_rad)
    person_y = EARTH_RADIUS * np.sin(person_angle_rad)

    # Draw stickman
    draw_stickman(ax, person_x, person_y, STICKMAN_SIZE)

    # Add time of day in the lower-right corner
    formatted_time = calculate_time_of_day(person_position, time_zone_offset)
    ax.text(orbit_limit - 100000, -orbit_limit + 50000, f"Time: {formatted_time}",
            color="white", fontsize=14, ha="right", va="center", fontweight="bold")

    # Title
    ax.set_title("Moon Orbit Simulation 🌕", color="white", fontsize=14)

    return fig, moon_phase, lit_moon_image

# Streamlit layout
st.set_page_config(layout="wide")
st.title("🌍 Moon Orbit Simulation 🌕")

# Sidebar controls
with st.sidebar:
    st.header("🛠️ Controls")

    # Add Day Button
    if st.button("➕ Add Day"):
        st.session_state.current_day += 1
        if st.session_state.current_day > MOON_ORBIT_PERIOD:
            st.session_state.current_day = 0.0

    # Spin the Earth Button
    if st.button("🌍 Spin the Earth"):
        st.session_state.person_position += 30  # Rotate by 30 degrees clockwise
        if st.session_state.person_position >= 360:
            st.session_state.person_position = 0

    # Time Zone Selection
    time_zone = st.selectbox("🌐 Select Time Zone", list(TIME_ZONES.keys()))
    st.session_state.time_zone_offset = TIME_ZONES[time_zone]

    # Reset Button
    if st.button("🔄 Reset"):
        st.session_state.current_day = 0.0
        st.session_state.person_position = 0

# Orbit and time simulation
fig, moon_phase, lit_moon_image = plot_moon_orbit(
    st.session_state.current_day, st.session_state.person_position, st.session_state.time_zone_offset
)

# Display the lit Moon image in the upper-left corner
st.image(lit_moon_image, caption=f"Moon Phase: {moon_phase}", width=300)

# Display the orbit and time simulation
st.pyplot(fig)

# Explanation Section
st.markdown(f"""
## 📖 About the Simulation
### Current Moon Phase: **{moon_phase}**

- **Moon Phase Visualization**: The Moon dynamically reflects its lit and shadowed sides in the orbit chart and the upper-left corner.
- **Add Day Button**: Advances the Moon's orbit by 1 day, changing its position and phase.
- **Spin the Earth Button**: Rotates the Earth clockwise, moving the stickman and updating the local time dynamically.
- **Yellow Stickman**: Represents a person on Earth. Their position determines the local time zone.

---

### 🌑 Lunar Phases Explained:
1. **New Moon**: The Moon is between the Earth and the Sun, and its dark side faces the Earth.
2. **First Quarter**: Half of the Moon's surface is visible as it orbits Earth.
3. **Full Moon**: The Moon is opposite the Sun, and its illuminated side faces the Earth.
4. **Last Quarter**: Half of the Moon's surface is visible in the opposite orientation.

Enjoy exploring the Moon's phases and Earth's rotation!
""")

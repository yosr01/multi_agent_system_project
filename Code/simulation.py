import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from io import BytesIO
from model import City, PublicTransport, Passenger, Simulation

# Define the city
city = City(10, 10, bus_stops=[(1, 0), (3, 9), (2, 2), (5, 9), (2, 7), (5, 1), (1, 5), (0, 8)])

# Create buses
bus1 = PublicTransport(id=1, route=[(1, 0), (2, 7), (3, 9), (5, 9)], city=city)
bus2 = PublicTransport(id=2, route=[(2, 2), (1, 5), (0, 8), (5, 1)], city=city)

# Create the simulation
simulation = Simulation(city, buses=[bus1, bus2], passengers=[])

# Function to create and add random passengers during the simulation
def add_random_passenger(simulation):
    """Randomly add a passenger to the simulation."""
    if random.random() < 0.1:  # 10% chance to add a passenger each frame
        passenger_id = len(simulation.passengers) + 1  # Unique ID for the new passenger
        start_pos = random.choice(city.bus_stops)
        destination = random.choice(city.bus_stops)
        passenger = Passenger(id=passenger_id, current_position=start_pos, destination=destination)
        simulation.passengers.append(passenger)
        return passenger  # Return the newly added passenger
    return None
" comment me please from here"
# Create the plot figure and axis for animation
fig, ax = plt.subplots(figsize=(8, 8))

# Set axis limits and grid
ax.set_xlim(0, city.width - 1)
ax.set_ylim(0, city.height - 1)
ax.set_aspect('equal', adjustable='box')
ax.grid(True)

# Plot bus stops in green
stop_x, stop_y = zip(*city.bus_stops)
ax.scatter(stop_x, stop_y, color='green', label='Bus Stops', s=100, marker='o')

# Plot blocked routes in red
def plot_blocked_routes():
    for start, end in city.blocked_routes:
        start_x, start_y = start
        end_x, end_y = end
        ax.plot([start_x, end_x], [start_y, end_y], color='red', linestyle='-', linewidth=2, label="Blocked Route")

# Plot initial blocked routes
plot_blocked_routes()

# Initialize the buses on the plot
bus_markers = [ax.scatter(bus.position[0], bus.position[1], color='blue', s=150, marker='^') for bus in simulation.buses]

# Initialize the passenger markers list
passenger_markers = []

def update(frame):
    # Add a random passenger at each frame
    new_passenger = add_random_passenger(simulation)
    
    # Run a simulation step
    simulation.run_step()

    # Update bus positions on the plot
    bus_positions = [bus.position for bus in simulation.buses]
    for i, bus in enumerate(bus_positions):
        bus_markers[i].set_offsets(bus)

    # Update passenger positions on the plot
    passenger_positions = [passenger.current_position for passenger in simulation.passengers]

    # If a new passenger was added, add their marker
    if new_passenger:
        new_marker = ax.scatter(new_passenger.current_position[0], new_passenger.current_position[1], color='pink', s=150, marker='x')
        passenger_markers.append(new_marker)

    # Update all passenger markers
    for i, passenger in enumerate(passenger_positions):
        passenger_markers[i].set_offsets(passenger)

    # Clear the old blocked routes before plotting new ones
    for line in ax.lines:  # Remove all previous blocked route lines
        line.remove()

    # Redraw the blocked routes (now updated)
    plot_blocked_routes()

    # Update the plot title
    ax.set_title(f"Simulation Step: {frame + 1}")

    return bus_markers + passenger_markers  # Return the updated artists for the frame

# Create the animation using FuncAnimation
ani = animation.FuncAnimation(fig, update, frames=100, interval=500, repeat=False)

# Display the animation (in a non-GUI backend)
plt.show()
 
"to here to look at the browser simulation"




""" 
                                Browser Simulation
# /////////////////////////////////////////////////////////////////////////////////////
# Function to plot the city grid, buses, and passengers
def plot_city(city, simulation):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Set axis limits and grid
    ax.set_xlim(0, city.width - 1)
    ax.set_ylim(0, city.height - 1)
    ax.set_aspect('equal', adjustable='box')
    ax.grid(True)

    # Plot bus stops in green
    stop_x, stop_y = zip(*city.bus_stops)
    ax.scatter(stop_x, stop_y, color='green', label='Bus Stops', s=100, marker='o')

    # Plot blocked routes in red
    for start, end in city.blocked_routes:
        start_x, start_y = start
        end_x, end_y = end
        ax.plot([start_x, end_x], [start_y, end_y], color='red', linestyle='-', linewidth=2, label="Blocked Route")

    # Initialize the buses on the plot
    bus_markers = [ax.scatter(bus.position[0], bus.position[1], color='blue', s=150, marker='^') for bus in simulation.buses]

    
    # Add a random passenger at each frame
    new_passenger = add_random_passenger(simulation)

    # Run a simulation step
    simulation.run_step()

    # Update bus positions on the plot
    bus_positions = [bus.position for bus in simulation.buses]
    for i, bus in enumerate(bus_positions):
        bus_markers[i].set_offsets(bus)

    # Update passenger positions on the plot
    passenger_positions = [passenger.current_position for passenger in simulation.passengers]

    # If a new passenger was added, add their marker
    if new_passenger:
        new_marker = ax.scatter(new_passenger.current_position[0], new_passenger.current_position[1], color='pink', s=150, marker='x')

    # Update all passenger markers
    passenger_markers = []
    for passenger in simulation.passengers:
        new_marker = ax.scatter(passenger.current_position[0], passenger.current_position[1], color='pink', s=150, marker='x')
        passenger_markers.append(new_marker)

    # Update the plot title
    ax.set_title(f"Simulation Step")

    # Save the plot to a file (in memory)
    img_io = BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close(fig)
    return img_io """
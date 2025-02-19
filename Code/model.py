import heapq
from typing import List, Tuple
import random
class City:
    def __init__(self, width: int, height: int, bus_stops: List[Tuple[int, int]]):
        self.width = width
        self.height = height
        self.bus_stops = bus_stops
        self.blocked_routes = {}  # Store blocked routes as a dictionary with (start, end) -> (block_duration, counter)
    def is_valid_position(self, position: Tuple[int, int]) -> bool:
        """Check if the position is within the bounds of the city."""
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def is_route_blocked(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Check if the route is blocked."""
        if (start, end) in self.blocked_routes:
            # If the route is blocked, check if it should remain blocked
            block_duration, counter = self.blocked_routes[(start, end)]
            if counter >= block_duration:
                # Unblock the route after reaching the duration
                self.unblock_route(start, end)
            return counter < block_duration  # Return True if the route is still blocked
        return False

    def block_route(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Block a route between two points with a random block duration."""
        block_duration = random.randint(2, 8)  # Block for a random number of steps between 2 and 8
        self.blocked_routes[(start, end)] = (block_duration, 0)  # Initialize counter at 0
        print(f"Blocked route between {start} and {end} for {block_duration} steps.")

    def unblock_route(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Unblock a route between two points."""
        if (start, end) in self.blocked_routes:
            del self.blocked_routes[(start, end)]
            print(f"Unblocked route between {start} and {end}.")
    
    def update_blocked_routes(self):
        """Increment the counter for each blocked route and unblock if necessary."""
        to_unblock = []
        for (start, end), (duration, counter) in self.blocked_routes.items():
            if counter >= duration:
                to_unblock.append((start, end))
            else:
                self.blocked_routes[(start, end)] = (duration, counter + 1)
        
        # Unblock routes after they have been blocked for enough time
        for start, end in to_unblock:
            self.unblock_route(start, end)


def dijkstra(start: Tuple[int, int], goal: Tuple[int, int], city: City) -> List[Tuple[int, int]]:
    """Find the shortest path using Dijkstra's algorithm, avoiding blocked routes if they exist."""
    pq = []
    heapq.heappush(pq, (0, start))  # Distance to the start is 0
    distances = {start: 0}
    predecessors = {start: None}

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right

    # A set of all blocked points (including intermediate points along blocked routes)
    blocked_points = set()
    for start, end in city.blocked_routes:
        x1, y1 = start
        x2, y2 = end

        # Get the direction of movement (either horizontal or vertical)
        dx = 1 if x2 > x1 else -1 if x2 < x1 else 0
        dy = 1 if y2 > y1 else -1 if y2 < y1 else 0

        current = start
        while current != end:
            blocked_points.add(current)
            current = (current[0] + dx, current[1] + dy)
        blocked_points.add(end)  # Add the endpoint as well

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current == goal:
            # Reconstruct the path from start to goal
            path = []
            while current is not None:
                path.append(current)
                current = predecessors[current]
            return path[::-1]  # Reverse to get start -> goal path

        for dx, dy in directions:
            neighbor = (current[0] + dx, current[1] + dy)

            if not city.is_valid_position(neighbor) or neighbor in blocked_points:
                # Skip invalid positions or blocked positions
                continue

            tentative_dist = current_dist + 1
            if neighbor not in distances or tentative_dist < distances[neighbor]:
                distances[neighbor] = tentative_dist
                predecessors[neighbor] = current
                heapq.heappush(pq, (tentative_dist, neighbor))

    return []  # No path found


class PublicTransport:
    def __init__(self, id, route, city):
        self.id = id
        self.route = route
        self.city = city
        self.position = route[0]  # Start at the first stop
        self.route_index = 0
        self.passengers = []
        self.path = []
        self.served_stops = 0  # Track how many stops the bus has served
        self.total_passenger_loads = 0  # Track the number of passengers boarded and dropped off
        self.timings = []  # Track the time taken to complete each cycle

    def move(self):
        target_stop = self.route[self.route_index]

        if self.position == target_stop:
            # Move to the next stop on the route (looping back to the start)
            self.route_index = (self.route_index + 1) % len(self.route)
            target_stop = self.route[self.route_index]
            self.served_stops += 1  # Increment served stop count
        
        # Calculate the path using Dijkstra
        path = dijkstra(self.position, target_stop, self.city)
        
        if path and len(path) > 1:
            # Move to the next position on the path
            self.position = path[1]
        else:
            print(f"Bus {self.id} cannot move to {target_stop}. No valid path found due to blocked routes.")
            if self.route_index > 0:
                previous_stop = self.route[self.route_index - 1]
            else:
                previous_stop = self.route[-1]
            
            print(f"Bus {self.id} is going back to the previous stop {previous_stop}.")
            self.position = previous_stop
            self.route_index = (self.route_index - 1) % len(self.route)  # Go back in the route
        
        # Track the passengers
        self.total_passenger_loads += len(self.passengers)  # Count passengers being transported

    def board_passenger(self, passenger):
        """Board a passenger onto the bus."""
        self.passengers.append(passenger)
        passenger.on_bus = self

class Passenger:
    def __init__(self, id: int, current_position: Tuple[int, int], destination: Tuple[int, int]):
        self.id = id
        self.current_position = current_position
        self.destination = destination
        self.on_bus = None
        self.target_stop = None  # The stop to reach in order to board a bus
        self.waiting_time = 0  # Track how many steps the passenger has been waiting
        self.max_waiting_time = 5  # The threshold of steps before the passenger considers moving
        self.journey_complete = False  # Track if the passenger's journey is complete
        self.start_time = None  # Track when the passenger starts their journey
        self.end_time = None  # Track when the passenger reaches their destination

    def find_nearest_stop(self, bus_routes: List[List[Tuple[int, int]]]):
        """Find the nearest bus stop that helps reach the destination."""
        if self.journey_complete:
            return  # If the journey is complete, do nothing

        min_distance = float('inf')
        nearest_stop = None
        for route in bus_routes:
            # Check if the route leads to the destination
            if self.destination in route:
                for stop in route:
                    # Calculate the distance from the current position to the stop
                    distance = abs(stop[0] - self.current_position[0]) + abs(stop[1] - self.current_position[1])
                    
                    # If this stop is closer than the previous one, update the nearest stop
                    if distance < min_distance:
                        min_distance = distance
                        nearest_stop = stop

        self.target_stop = nearest_stop  # Set the nearest stop as the target stop
        if nearest_stop:
            print(f"Passenger {self.id} is moving towards the nearest stop at {nearest_stop}.")
        else:
            print(f"No suitable bus stop found for Passenger {self.id} to reach the destination.")

    def get_off_bus(self):
        """Allow passenger to get off the bus."""
        if self.on_bus:
            print(f"Passenger {self.id} is getting off the bus at {self.on_bus.position}.")
            self.on_bus.passengers.remove(self)
            self.on_bus = None
            self.journey_complete = False  # The passenger is still in the journey
        else:
            print(f"Passenger {self.id} is not on any bus.")

    def move_towards(self, target: Tuple[int, int]):
        """Move one step closer to the target position (nearest bus stop)."""
        if self.journey_complete:
            return  # If the journey is complete, do nothing

        x1, y1 = self.current_position
        x2, y2 = target
        if x1 != x2:
            new_x = x1 + (1 if x1 < x2 else -1)
        else:
            new_x = x1
        
        if y1 != y2:
            new_y = y1 + (1 if y1 < y2 else -1)
        else:
            new_y = y1
        
        # Update position only if it's moving towards the target
        if (new_x, new_y) != self.current_position:
            self.current_position = (new_x, new_y)
            print(f"Passenger {self.id} is moving towards {self.target_stop}.")
        else:
            print(f"Passenger {self.id} reached their target stop at {self.current_position}.")

    def update(self, buses: List[PublicTransport], step_count: int):
        """Update passenger state, either moving towards a stop or staying on a bus."""
        if self.journey_complete:
            return  # If the journey is complete, do nothing

        if self.on_bus:
            # Passenger is on a bus
            self.current_position = self.on_bus.position
            
            # Check if the passenger has reached their destination
            if self.current_position == self.destination:
                if self.end_time is None:  # Record end time when reaching destination
                    self.end_time = step_count
                print(f"Passenger {self.id} disembarked at {self.destination}.")
                self.on_bus.passengers.remove(self)
                self.on_bus = None
                self.journey_complete = True  # Mark the journey as complete
            else:
                # Check if the bus is not going to the passenger's destination
                if self.destination not in self.on_bus.route:
                    print(f"Passenger {self.id} is on the wrong bus at {self.current_position}.")
                    # Get off at the next stop on the route and look for the next bus stop closer to the destination
                    next_stop = self.on_bus.next_stop(self.current_position)
                    self.current_position = next_stop
                    print(f"Passenger {self.id} got off at {next_stop}.")
                    self.on_bus.passengers.remove(self)
                    self.on_bus = None

                    # Find the next bus stop to board the right bus
                    self.find_nearest_stop([bus.route for bus in buses])
                    self.waiting_time = 0  # Reset the waiting time

        else:
            if not self.target_stop:
                # If target stop is not set, find the nearest stop
                self.find_nearest_stop([bus.route for bus in buses])

            if self.current_position != self.target_stop:
                # Move towards the target bus stop
                self.move_towards(self.target_stop)
            else:
                print(f"Passenger {self.id} reached the bus stop at {self.current_position} and is waiting.")
                
                # Increment the waiting time
                self.waiting_time += 1

                # Check if the passenger has been waiting for too long
                if self.waiting_time > self.max_waiting_time:
                    print(f"Passenger {self.id} has been waiting for too long at {self.current_position}. They are considering moving to another stop.")
                    
                    # Optionally: Start moving towards another stop (or do some other behavior)
                    self.find_nearest_stop([bus.route for bus in buses])  # Update target stop (this can be more advanced)

                    # Reset waiting time
                    self.waiting_time = 0

                # Try to board a bus, only if the passenger is at a bus stop
                for bus in buses:
                    if self.current_position == bus.position and self not in bus.passengers:
                        if self.destination in bus.route:
                            bus.board_passenger(self)
                            print(f"Passenger {self.id} boarded Bus {bus.id} at stop {bus.position}.")
                            # Set the start time when the passenger boards the bus
                            if self.start_time is None:
                                self.start_time = step_count  # Use step_count directly
                            break
        
        # Prevent passenger from moving after reaching destination
        if self.current_position == self.destination:
            print(f"Passenger {self.id} has reached their destination {self.destination} and is no longer moving.")
            self.journey_complete = True
    def get_travel_time(self):
        """Calculate the time taken for the passenger to complete their journey."""
        if self.start_time is not None and self.end_time is not None:
            return self.end_time - self.start_time
        return None
    def on_bus_route_blocked(self, blocked_routes):
        """Check if the bus route the passenger is on is blocked and take necessary actions."""
        if self.on_bus:  # Check if the passenger is on a bus
            for start, end in blocked_routes:
                # Check if the bus is on a blocked route
                if self.on_bus.position == start or self.on_bus.position == end:
                    print(f"Passenger {self.id} is on a bus with a blocked route!")
                    self.get_off_bus()  # Passenger could get off or take other action
                    break

def add_random_blocked_route(city: City):
    """Randomly block a route in the city, ensuring it avoids stops and spans at least 4 cells."""
    max_blocked_routes = random.randint(0,4)  # Random number of blocked routes, less than 5
    if len(city.blocked_routes) >= max_blocked_routes:
        return
    # Generate potential start and end points for blocking
    valid_points = [
        (x, y) for x in range(city.width) for y in range(city.height)
        if (x, y) not in city.bus_stops  # Avoid bus stops
    ]

    # Randomly choose a start point
    start = random.choice(valid_points)
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # Horizontal/Vertical directions

    # Generate potential end points ensuring a minimum distance of 4 cells
    candidates = [
        (start[0] + dx * d, start[1] + dy * d)
        for dx, dy in directions
        for d in range(4, 7)  # Minimum distance of 4
        if city.is_valid_position((start[0] + dx * d, start[1] + dy * d))
    ]

    if not candidates:
        print("No valid routes to block.")
        return

    # Randomly choose an end point from valid candidates
    end = random.choice(candidates)
    city.block_route(start, end)
    print(f"Blocked route between {start} and {end}.")


class Simulation:
    def __init__(self, city, buses, passengers):
        self.city = city
        self.buses = buses
        self.passengers = passengers
        self.step_count = 0
        self.unblock_counter = 0  # Variable to track steps until unblocking
        self.total_passenger_transport = 0  # Track number of passengers transported

    def run_step(self):
        self.step_count += 1
        self.unblock_counter += 1  # Increment unblock counter with each step

        # Add a disturbance every 5 steps, but ensure fewer than 5 blocked routes
        if self.step_count % 5 == 0:
            add_random_blocked_route(self.city)

        random_fixed = random.randint(25, 40)
      
        if self.step_count % random_fixed == 0:
            print(f"Routes fixed at step {self.step_count}.")
            self.city.update_blocked_routes()  # Unblock routes that have expired based on their duration
            # Alternatively, unblock manually based on duration or counter
            for start, end in list(self.city.blocked_routes):
                self.city.unblock_route(start, end)  # Manually unblock each route
            self.unblock_counter = 0  # Reset the unblock counter after unblocking all routes

        # Check for blocked routes and passengers get off if necessary
        for bus in self.buses:
            bus.move()
            for passenger in bus.passengers:
                passenger.on_bus_route_blocked(self.city.blocked_routes)  # Check if the bus route is blocked

        # Update passengers (those not on a bus will move towards their destination)
        for passenger in self.passengers:
            passenger.update(self.buses, self.step_count)  # Pass step_count here
            if passenger.journey_complete:
                self.total_passenger_transport += 1  # Increment total number of passengers transported

        self.print_state()

    def print_state(self):
        """Print the state of the simulation."""
        vehicle_metrics = {
            "served_stops": 0,
            "total_passenger_loads": 0,
            "timings": [],
        }

        for bus in self.buses:
            print(f"Bus {bus.id} at {bus.position} with {len(bus.passengers)} passengers.")
            vehicle_metrics["served_stops"] += bus.served_stops
            vehicle_metrics["total_passenger_loads"] += bus.total_passenger_loads
            vehicle_metrics["timings"].append(bus.timings)

        for passenger in self.passengers:
            print(f"Passenger {passenger.id} at {passenger.current_position} with target {passenger.target_stop}.")

        # Print blocked routes
        self.print_blocked_routes()

        # Print travel times for passengers after simulation ends
        if self.step_count >= 100:
            for passenger in self.passengers:
                travel_time = passenger.get_travel_time()
                if travel_time is not None:
                    print(f"Passenger {passenger.id} took {travel_time} steps to reach their destination.")
                else:
                    print(f"Passenger {passenger.id} has not completed their journey yet.")
        
        # Final System Metrics
        self.print_system_metrics(vehicle_metrics)

    def print_system_metrics(self, vehicle_metrics):
        """Print the system metrics."""
        total_throughput = self.total_passenger_transport  # Total passengers transported
        grid_utilization = self.calculate_grid_utilization()

        print("\nSimulation Summary:")
        print(f"Total throughput: {total_throughput} passengers.")
        print(f"Average grid utilization: {grid_utilization}%")
        print(f"Total number of people transported: {self.total_passenger_transport}")
        print(f"Vehicle Metrics:")
        print(f"  - Total bus stops served: {vehicle_metrics['served_stops']}")
        print(f"  - Total passenger loads: {vehicle_metrics['total_passenger_loads']}")

    def print_blocked_routes(self):
        """Helper function to print blocked routes."""
        print("Blocked routes:", self.city.blocked_routes)

    def calculate_grid_utilization(self):
        """Calculate the grid utilization based on occupied cells by buses."""
        occupied_cells = set()
        for bus in self.buses:
            occupied_cells.add(bus.position)
        
        # Calculate grid utilization as the percentage of occupied cells
        grid_size = self.city.width * self.city.height
        occupied_percentage = (len(occupied_cells) / grid_size) * 100
        return occupied_percentage




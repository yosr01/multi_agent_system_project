import time
from threading import Thread
import webbrowser
from server import app
from simulation import simulation

def start_simulation():
    """Run the simulation steps in the background."""
    while True:
        simulation.run_step()  # Run one step of the simulation
        time.sleep(0.05)  # Delay between simulation steps (50 milliseconds)

def open_browser():
    """Open the default web browser to the app's home page."""
    time.sleep(1)  # Give Flask some time to start
    webbrowser.open("http://127.0.0.1:5000/")

if __name__ == "__main__":
    # Start Flask app in a separate thread
    server_thread = Thread(target=lambda: app.run(debug=False, use_reloader=False))
    server_thread.daemon = True  # Ensure the server thread doesn't block the main program
    server_thread.start()

    # Start the simulation in a separate thread
    simulation_thread = Thread(target=start_simulation)
    simulation_thread.daemon = True  # Ensure the simulation thread doesn't block the main program
    simulation_thread.start()

    # Open the browser
    open_browser()

    # Keep the main program alive while threads run
    while True:
        time.sleep(1)  # Main thread does nothing but ensures both threads stay alive

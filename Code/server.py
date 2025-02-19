from flask import Flask, render_template, Response
from simulation import simulation, plot_city,city
app = Flask(__name__)


@app.route('/')
def index():
    # Render the main page with a canvas to show the plot
    return render_template('index.html')

@app.route('/simulate_step')
def simulate_step():
    # Perform one simulation step (you can add logic for passenger movement here)
    img_io = plot_city(city, simulation)
    return Response(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
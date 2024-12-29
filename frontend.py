from flask import Flask, render_template_string, request
import pandas as pd

from vae_main import run_for_frontend
from frontend_templates import *


app = Flask(__name__)  # Initialize the Flask app

def chunk_list(lst, n):
    """Split a list into chunks of size n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


### Frontend routes here
@app.route("/", methods=["GET"])
def index():
    # Group genres into chunks of n for display
    return render_template_string(main_page, genre_chunks=list(chunk_list(genres, (n:=3))))

@app.route("/output", methods=["POST"])
def output():
    output = pd.DataFrame()
    error_message = None
    
    # Get form data
    genres_selected = request.form.getlist("genres")
    avg_rating = request.form.get("avg_rating")
    num_votes = request.form.get("votes_num")

    # Ensure at least one genre is selected
    if not genres_selected:
        error_message = "You must select at least one genre."

    # Validate and process avg_rating
    try:
        avg_rating = float(avg_rating)
        if not (0 <= avg_rating <= 10):
            error_message = "Avg. Rating must be between 0 and 10."
    except (ValueError, TypeError):
        error_message = "Invalid Avg. Rating input."

    # Validate and process num_votes
    try:
        num_votes = int(num_votes)
        if not (0 <= num_votes <= 1000):
            error_message = "Number of votes must be non-negative."
    except (ValueError, TypeError):
        error_message = "Invalid Number of Votes input."

    # Mock output if there are no errors
    if not error_message:
        try:
            output = run_for_frontend(genres_selected, avg_rating, num_votes)

        except Exception as e:
            error_message = f"Error generating recommendations: {str(e)}"

    return render_template_string(
        output_page,
        output=output.to_html(index=False) if not error_message else None,
        error_message=error_message
    )

@app.route("/info")
def info():
    return render_template_string(info_page)

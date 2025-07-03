from flask import Flask, render_template_string, request, jsonify
import pandas as pd

from vae_main import run_for_frontend
from frontend_templates import genres


app = Flask(__name__)  # Initialize the Flask app

def chunk_list(lst, n):
    """Split a list into chunks of size n."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Modern, stylistic UI templates (no Bootstrap)
main_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flick Finder</title>
  <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
      background: linear-gradient(120deg, #f6f8fc 0%, #e3e9f7 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow-x: hidden;
    }
    /* Decorative background shapes */
    .bg-shape {
      position: absolute;
      border-radius: 50%;
      filter: blur(32px);
      opacity: 0.18;
      z-index: 0;
    }
    .bg-shape1 {
      width: 340px; height: 340px;
      background: #6c63ff;
      top: -80px; left: -120px;
    }
    .bg-shape2 {
      width: 260px; height: 260px;
      background: #4f8cff;
      bottom: -100px; right: -80px;
    }
    .header {
      position: relative;
      z-index: 2;
      background: transparent;
      color: #22223b;
      text-align: center;
      margin-bottom: 0.2rem;
    }
    .logo {
      font-family: 'Montserrat', Arial, sans-serif;
      font-size: 2.7rem;
      font-weight: 700;
      letter-spacing: 2px;
      color: #4f8cff;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.7rem;
      margin-bottom: 0.2rem;
      text-shadow: 0 2px 12px #b3c6ff33;
    }
    .logo-icon {
      font-size: 2.2rem;
      color: #6c63ff;
      filter: drop-shadow(0 2px 8px #6c63ff33);
    }
    .subtitle {
      font-size: 1.1rem;
      color: #6c63ff;
      font-weight: 600;
      margin-bottom: 0.7rem;
      letter-spacing: 0.5px;
    }
    .divider {
      width: 60px;
      height: 4px;
      background: linear-gradient(90deg, #4f8cff 0%, #6c63ff 100%);
      border-radius: 2px;
      margin: 0.7rem auto 1.2rem auto;
      box-shadow: 0 2px 8px #4f8cff33;
    }
    .container {
      margin: 0 auto;
      max-width: 480px;
      background: #fff;
      border-radius: 1.5rem;
      box-shadow: 0 8px 40px rgba(80,80,180,0.13);
      padding: 2.5rem 2rem 2rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      align-items: center;
      animation: fadeInUp 1.1s;
      z-index: 2;
      position: relative;
      transition: box-shadow 0.25s;
    }
    .container:hover {
      box-shadow: 0 16px 56px rgba(80,80,180,0.18);
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(40px); }
      to { opacity: 1; transform: none; }
    }
    .section-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #22223b;
      margin-bottom: 0.5rem;
      text-align: center;
    }
    .genres {
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      justify-content: center;
      margin-bottom: 1rem;
    }
    .genre-checkbox {
      display: none;
    }
    .genre-label {
      display: inline-block;
      padding: 0.5rem 1.1rem;
      border-radius: 2rem;
      background: #f2f2f7;
      color: #22223b;
      font-size: 1rem;
      cursor: pointer;
      border: 1.5px solid #e0e0e0;
      transition: background 0.25s, color 0.25s, border 0.25s, transform 0.18s;
      user-select: none;
      box-shadow: 0 1px 4px rgba(80,80,180,0.04);
      margin-bottom: 0.2rem;
    }
    .genre-label:hover {
      background: #e0e7ff;
      color: #4f8cff;
      transform: scale(1.07);
      border: 1.5px solid #b3c6ff;
    }
    .genre-checkbox:checked + .genre-label {
      background: linear-gradient(90deg, #4f8cff 0%, #6c63ff 100%);
      color: #fff;
      border: 1.5px solid #4f8cff;
      transform: scale(1.09);
      box-shadow: 0 2px 8px rgba(80,80,180,0.13);
    }
    .form-group {
      display: flex;
      flex-direction: column;
      gap: 0.3rem;
      margin-bottom: 1.2rem;
      width: 100%;
      align-items: center;
    }
    .input {
      padding: 0.7rem 1rem;
      border-radius: 0.7rem;
      border: 1.5px solid #e0e0e0;
      font-size: 1rem;
      background: #f8fafc;
      transition: border 0.2s, box-shadow 0.2s;
      width: 100%;
      max-width: 260px;
      text-align: center;
    }
    .input:focus {
      outline: none;
      border: 1.5px solid #4f8cff;
      background: #fff;
      box-shadow: 0 2px 8px rgba(80,80,180,0.10);
    }
    .submit-btn {
      width: 100%;
      max-width: 260px;
      padding: 0.9rem 0;
      border-radius: 1.2rem;
      border: none;
      background: linear-gradient(90deg, #4f8cff 0%, #6c63ff 100%);
      color: #fff;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(80,80,180,0.08);
      transition: background 0.2s, box-shadow 0.2s, transform 0.18s;
      margin-top: 0.5rem;
    }
    .submit-btn:hover {
      background: linear-gradient(90deg, #6c63ff 0%, #4f8cff 100%);
      box-shadow: 0 4px 16px rgba(80,80,180,0.13);
      transform: scale(1.04);
    }
    .info-link {
      color: #4f8cff;
      text-align: center;
      display: block;
      margin-top: 0.5rem;
      text-decoration: none;
      font-size: 1rem;
      transition: color 0.2s;
    }
    .info-link:hover {
      color: #22223b;
      text-decoration: underline;
    }
    @media (max-width: 600px) {
      .container { padding: 1.2rem 0.5rem; }
      .header { font-size: 1.3rem; }
    }
    .loading-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(246, 248, 252, 0.95);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: opacity 0.3s;
      font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    }
    .loading-title {
      font-size: 1.5rem;
      font-weight: 700;
      color: #4f8cff;
      margin-bottom: 1.2rem;
      letter-spacing: 1px;
    }
    .progress-bar-bg {
      width: 320px;
      max-width: 80vw;
      height: 22px;
      background: #e0e7ff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 8px #b3c6ff33;
      margin-bottom: 1.2rem;
    }
    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #4f8cff 0%, #6c63ff 100%);
      width: 0%;
      border-radius: 12px 0 0 12px;
      transition: width 0.2s;
    }
    .progress-label {
      font-size: 1.1rem;
      color: #22223b;
      font-weight: 600;
      margin-top: 0.2rem;
      letter-spacing: 1px;
    }
    .results-section {
      width: 100%;
      max-width: 600px;
      margin: 2rem auto 0 auto;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 1.5rem;
    }
    .results-list {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 1.2rem;
      margin-top: 1rem;
    }
    .result-card {
      background: linear-gradient(90deg, #f8fafc 60%, #e3e9f7 100%);
      border-radius: 1.2rem;
      box-shadow: 0 2px 16px rgba(80,80,180,0.10);
      padding: 1.2rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1.2rem;
      transition: box-shadow 0.2s, transform 0.18s;
      border: 1.5px solid #e0e7ff;
      position: relative;
      animation: fadeInCard 0.7s;
    }
    @keyframes fadeInCard {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: none; }
    }
    .result-rank {
      font-size: 2.1rem;
      font-weight: 700;
      color: #4f8cff;
      min-width: 2.5rem;
      text-align: center;
      flex-shrink: 0;
      text-shadow: 0 2px 8px #b3c6ff33;
    }
    .result-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }
    .result-title {
      font-size: 1.15rem;
      font-weight: 600;
      color: #22223b;
      margin-bottom: 0.1rem;
    }
    .result-genre {
      font-size: 0.95rem;
      color: #888;
      margin-top: 0.1rem;
      font-style: italic;
    }
    .result-score {
      font-size: 0.98rem;
      color: #6c63ff;
      font-weight: 500;
      margin-top: 0.1rem;
    }
    .error {
      background: #ffeaea;
      color: #b00020;
      border-radius: 0.7rem;
      padding: 1rem 1.2rem;
      font-size: 1.1rem;
      margin-bottom: 1rem;
      border: 1.5px solid #ffb3b3;
      text-align: center;
      animation: fadeInError 0.7s;
    }
    @keyframes fadeInError {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: none; }
    }
    .spinner-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(246, 248, 252, 0.95);
      z-index: 9999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      transition: opacity 0.3s;
      font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
      display: none;
    }
    .spinner {
      border: 6px solid #e0e7ff;
      border-top: 6px solid #4f8cff;
      border-radius: 50%;
      width: 60px;
      height: 60px;
      animation: spin 1s linear infinite;
      margin-bottom: 1.2rem;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    .spinner-message {
      font-size: 1.2rem;
      color: #4f8cff;
      font-weight: 600;
      letter-spacing: 1px;
    }
  </style>
</head>
<body>
  <div class="bg-shape bg-shape1"></div>
  <div class="bg-shape bg-shape2"></div>
  <header class="header">
    <div class="logo"><span class="logo-icon">&#127909;</span> Flick Finder</div>
    <div class="subtitle">Find your next favorite movie</div>
    <div class="divider"></div>
  </header>
  <form class="container" method="POST" action="/output" id="recommendation-form">
    <div>
      <div class="section-title">Select Genres <span style="font-size:0.9em; color:#888;">(at least 1)</span>:</div>
      <div class="genres">
        {% for chunk in genre_chunks %}
          {% for genre in chunk %}
            <input class="genre-checkbox" type="checkbox" id="genre_{{ genre }}" name="genres" value="{{ genre }}">
            <label class="genre-label" for="genre_{{ genre }}">{{ genre }}</label>
          {% endfor %}
        {% endfor %}
      </div>
    </div>
    <div class="form-group">
      <label class="section-title" for="avg_rating">Avg. Rating (0-10):</label>
      <input class="input" type="number" id="avg_rating" name="avg_rating" step="0.1" min="0" max="10" required>
    </div>
    <div class="form-group">
      <label class="section-title" for="votes_num">Number of Votes (0-1000):</label>
      <input class="input" type="number" id="votes_num" name="votes_num" min="0" max="1000" required>
    </div>
    <button class="submit-btn" type="submit">Get Recommendations</button>
    <a class="info-link" href="/info">More Information</a>
  </form>
  <div class="spinner-overlay" id="spinner-overlay">
    <div class="spinner"></div>
    <div class="spinner-message">Loading recommendations...</div>
  </div>
  <script>
    const form = document.getElementById('recommendation-form');
    const spinner = document.getElementById('spinner-overlay');
    form.addEventListener('submit', function() {
      spinner.style.display = 'flex';
    });
  </script>
</body>
</html>
'''

output_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flick Finder - Results</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
      background: linear-gradient(120deg, #f6f8fc 0%, #e3e9f7 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      animation: fadeInBody 1.2s;
    }
    @keyframes fadeInBody {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .header {
      background: #22223b;
      color: #fff;
      padding: 1.2rem 0;
      text-align: center;
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: 2px;
      border-radius: 1.5rem 1.5rem 0 0;
      width: 100%;
      max-width: 600px;
      box-shadow: 0 2px 12px rgba(34,34,59,0.07);
      margin: 0 auto;
      animation: slideDown 0.8s;
    }
    @keyframes slideDown {
      from { transform: translateY(-40px); opacity: 0; }
      to { transform: none; opacity: 1; }
    }
    .container {
      margin: 0 auto;
      max-width: 600px;
      background: #fff;
      border-radius: 0 0 1.5rem 1.5rem;
      box-shadow: 0 4px 32px rgba(80,80,180,0.10);
      padding: 2.5rem 2rem 2rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      align-items: center;
      animation: fadeInUp 1.1s;
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(40px); }
      to { opacity: 1; transform: none; }
    }
    .section-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #22223b;
      margin-bottom: 0.5rem;
      text-align: center;
    }
    .error {
      background: #ffeaea;
      color: #b00020;
      border-radius: 0.7rem;
      padding: 1rem 1.2rem;
      font-size: 1.1rem;
      margin-bottom: 1rem;
      border: 1.5px solid #ffb3b3;
      text-align: center;
      animation: fadeInError 0.7s;
    }
    @keyframes fadeInError {
      from { opacity: 0; transform: scale(0.95); }
      to { opacity: 1; transform: none; }
    }
    .results-list {
      width: 100%;
      display: flex;
      flex-direction: column;
      gap: 1.2rem;
      margin-top: 1rem;
    }
    .result-card {
      background: linear-gradient(90deg, #f8fafc 60%, #e3e9f7 100%);
      border-radius: 1.2rem;
      box-shadow: 0 2px 16px rgba(80,80,180,0.10);
      padding: 1.2rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 1.2rem;
      transition: box-shadow 0.2s, transform 0.18s;
      border: 1.5px solid #e0e7ff;
      position: relative;
      animation: fadeInCard 0.7s;
    }
    @keyframes fadeInCard {
      from { opacity: 0; transform: translateY(20px); }
      to { opacity: 1; transform: none; }
    }
    .result-rank {
      font-size: 2.1rem;
      font-weight: 700;
      color: #4f8cff;
      min-width: 2.5rem;
      text-align: center;
      flex-shrink: 0;
      text-shadow: 0 2px 8px #b3c6ff33;
    }
    .result-info {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 0.2rem;
    }
    .result-title {
      font-size: 1.15rem;
      font-weight: 600;
      color: #22223b;
      margin-bottom: 0.1rem;
    }
    .result-genre {
      font-size: 0.95rem;
      color: #888;
      margin-top: 0.1rem;
      font-style: italic;
    }
    .result-score {
      font-size: 0.98rem;
      color: #6c63ff;
      font-weight: 500;
      margin-top: 0.1rem;
    }
    .back-btn {
      display: inline-block;
      margin-top: 1.2rem;
      padding: 0.7rem 2.2rem;
      border-radius: 1.2rem;
      border: none;
      background: linear-gradient(90deg, #4f8cff 0%, #6c63ff 100%);
      color: #fff;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(80,80,180,0.08);
      transition: background 0.2s, box-shadow 0.2s, transform 0.18s;
      text-decoration: none;
    }
    .back-btn:hover {
      background: linear-gradient(90deg, #6c63ff 0%, #4f8cff 100%);
      box-shadow: 0 4px 16px rgba(80,80,180,0.13);
      transform: scale(1.04);
    }
    @media (max-width: 600px) {
      .container { padding: 1.2rem 0.5rem; }
      .header { font-size: 1.3rem; }
      .result-card { flex-direction: column; align-items: flex-start; gap: 0.5rem; }
      .result-rank { font-size: 1.5rem; }
    }
  </style>
</head>
<body>
  <div class="header">Flick Finder</div>
  <div class="container">
    <div class="section-title">Recommendations</div>
    {% if error_message %}
      <div class="error">{{ error_message }}</div>
    {% endif %}
    {% if output is not none and output|length > 0 %}
      <div class="results-list">
        {% for row in output.iterrows() %}
          {% set rec = row[1] %}
          <div class="result-card">
            <div class="result-rank">{{ rec['Rank'] }}</div>
            <div class="result-info">
              <div class="result-title">{{ rec['Movie'] }}</div>
              {% if 'Genre(s)' in rec %}
                <div class="result-genre">{{ rec['Genre(s)'] }}</div>
              {% endif %}
              <div class="result-score">Similarity Score: {{ '%.3f' % rec['Similarity Score'] }}</div>
            </div>
          </div>
        {% endfor %}
      </div>
    {% elif not error_message %}
      <div class="error">No recommendations found for your criteria.</div>
    {% endif %}
    <a class="back-btn" href="/">Back to Home</a>
  </div>
</body>
</html>
'''

info_page = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flick Finder - Info</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
      background: linear-gradient(120deg, #f6f8fc 0%, #e3e9f7 100%);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      animation: fadeInBody 1.2s;
    }
    @keyframes fadeInBody {
      from { opacity: 0; }
      to { opacity: 1; }
    }
    .header {
      background: #22223b;
      color: #fff;
      padding: 1.2rem 0;
      text-align: center;
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: 2px;
      border-radius: 1.5rem 1.5rem 0 0;
      width: 100%;
      max-width: 480px;
      box-shadow: 0 2px 12px rgba(34,34,59,0.07);
      margin: 0 auto;
      animation: slideDown 0.8s;
    }
    @keyframes slideDown {
      from { transform: translateY(-40px); opacity: 0; }
      to { transform: none; opacity: 1; }
    }
    .container {
      margin: 0 auto;
      max-width: 480px;
      background: #fff;
      border-radius: 0 0 1.5rem 1.5rem;
      box-shadow: 0 4px 32px rgba(80,80,180,0.10);
      padding: 2.5rem 2rem 2rem 2rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
      align-items: center;
      animation: fadeInUp 1.1s;
    }
    @keyframes fadeInUp {
      from { opacity: 0; transform: translateY(40px); }
      to { opacity: 1; transform: none; }
    }
    .section-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #22223b;
      margin-bottom: 0.5rem;
      text-align: center;
    }
    .info-list {
      list-style: none;
      padding: 0;
      margin: 1.2rem 0 0 0;
      color: #444;
      font-size: 1.05rem;
    }
    .info-list li {
      margin-bottom: 0.7rem;
      padding-left: 1.2rem;
      position: relative;
    }
    .info-list li:before {
      content: '\2022';
      color: #4f8cff;
      font-weight: bold;
      display: inline-block;
      width: 1em;
      margin-left: -1em;
    }
    .back-btn {
      display: inline-block;
      margin-top: 1.2rem;
      padding: 0.7rem 2.2rem;
      border-radius: 1.2rem;
      border: none;
      background: linear-gradient(90deg, #4f8cff 0%, #6c63ff 100%);
      color: #fff;
      font-size: 1.1rem;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 2px 8px rgba(80,80,180,0.08);
      transition: background 0.2s, box-shadow 0.2s, transform 0.18s;
      text-decoration: none;
    }
    .back-btn:hover {
      background: linear-gradient(90deg, #6c63ff 0%, #4f8cff 100%);
      box-shadow: 0 4px 16px rgba(80,80,180,0.13);
      transform: scale(1.04);
    }
    @media (max-width: 600px) {
      .container { padding: 1.2rem 0.5rem; }
      .header { font-size: 1.3rem; }
    }
  </style>
</head>
<body>
  <div class="header">Flick Finder</div>
  <div class="container">
    <div class="section-title">About Flick Finder</div>
    <ul class="info-list">
      <li>Choose one or more genres</li>
      <li>Set your preferred average rating (0-10)</li>
      <li>Set the minimum number of votes (0-1000)</li>
      <li>Get a list of recommended movies!</li>
    </ul>
    <a class="back-btn" href="/">Back to Home</a>
  </div>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    return render_template_string(main_page, genre_chunks=list(chunk_list(genres, (n:=3))))

@app.route("/output", methods=["POST"])
def output():
    output = pd.DataFrame()
    error_message = None
    genres_selected = request.form.getlist("genres")
    avg_rating = request.form.get("avg_rating")
    num_votes = request.form.get("votes_num")
    if not genres_selected:
        error_message = "You must select at least one genre."
    try:
        avg_rating = float(avg_rating)
        if not (0 <= avg_rating <= 10):
            error_message = "Avg. Rating must be between 0 and 10."
    except (ValueError, TypeError):
        error_message = "Invalid Avg. Rating input."
    try:
        num_votes = int(num_votes)
        if not (0 <= num_votes <= 1000):
            error_message = "Number of votes must be non-negative."
    except (ValueError, TypeError):
        error_message = "Invalid Number of Votes input."
    if not error_message:
        try:
            output = run_for_frontend(genres_selected, avg_rating, num_votes)
        except Exception as e:
            error_message = f"Error generating recommendations: {str(e)}"
    output_df = output if (not error_message and not output.empty) else None
    return render_template_string(
        output_page,
        output=output_df,
        error_message=error_message
    )

@app.route("/info")
def info():
    return render_template_string(info_page)

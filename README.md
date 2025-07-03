# 🎬 Flick Finder: Movie Recommendation Application

Flick Finder is a modern, user-friendly web application that recommends movies based on your favorite genres, desired average rating, and number of votes. Powered by a Variational Autoencoder (VAE) model, it delivers personalized movie suggestions with a beautiful, responsive UI.

---

## 🚀 Features
- **Modern, clean UI** with genre selection, rating, and votes input
- **Fast recommendations** using a pre-trained VAE model (PyTorch)
- **Results displayed as stylish cards** with movie title, genre(s), and similarity score
- **Loading spinner** for user feedback during processing
- **Error handling** and input validation
- **Easy to run locally** (no cloud dependencies)

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask, PyTorch, Pandas, scikit-learn
- **Frontend:** HTML, CSS, JavaScript (vanilla, no frameworks)
- **Model:** Variational Autoencoder (VAE)

---

## ⚡ Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/your-username/movie_recommendation_application.git
cd movie_recommendation_application
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Train the model
If you want to retrain the model, set `TRAIN_REQUIRED = True` in `website.py` and run:
```bash
python website.py
```
Then set `TRAIN_REQUIRED = False` for normal use.

### 4. Run the application
```bash
python website.py
```

### 5. Open in your browser
Go to [http://localhost:8080](http://localhost:8080)

---

## ✨ Usage
1. Select one or more genres.
2. Enter your desired average rating (0-10) and number of votes (0-1000).
3. Click **Get Recommendations**.
4. View your top 5 movie recommendations on a beautiful results page.

---

## 📁 Project Structure
```
movie_recommendation_application/
├── data/                  # Movie and user data CSVs
├── vae_main.py            # VAE model and recommendation logic
├── frontend.py            # Flask app and UI templates
├── website.py             # App entry point
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── ...
```

---

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.

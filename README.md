# Movie-Recommendation-System
# 🎬 MovieMate AI – Movie Recommendation & Sentiment Analysis System

**MovieMate AI** is a Flask-based web application that allows users to explore movies, view detailed movie information, and perform sentiment as well as emotion analysis on movie reviews. It integrates with the **TMDB API** for movie data and utilizes **TextBlob** and **DeepFace** for analyzing sentiments and emotions.

---

## 🚀 Features

- 🔍 Search for movies by title  
- 📝 View detailed movie information (poster, overview, genres, rating)  
- 💬 Sentiment analysis on movie reviews (Positive, Negative, Neutral)  
- 😊 Emotion detection using DeepFace  
- 🎨 Clean and responsive web UI with Bootstrap  
- 📊 Real-time emotion/sentiment breakdown for each movie  

---

## 🧰 Technologies Used

- **Flask** – Web framework  
- **TMDB API** – Fetch movie data  
- **TextBlob** – Sentiment analysis  
- **DeepFace** – Emotion recognition  
- **HTML/CSS & Bootstrap** – Frontend design  
- **JavaScript & jQuery** – Client-side interactions

---

## 📁 Project Structure

```
Movie-Recommendation-System/
│
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── static/                    # CSS, JS, images
│   ├── css/
│   └── js/
├── templates/                 # HTML templates
│   ├── index.html
│   └── result.html
└── README.md                  # Project documentation
```

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/SureshB2938/Movie-Recommendation-System.git
cd Movie-Recommendation-System
```

### 2. Install Python Dependencies

Ensure Python 3.7+ is installed:

```bash
python --version
```

#### Option 1: Install dependencies manually

```bash
pip install flask
pip install requests
pip install textblob
pip install deepface
```

#### Option 2: Install using `requirements.txt`

```bash
pip install -r requirements.txt
```

### 3. TMDB API Key Setup

- Get your API key from [TMDB Developer Portal](https://www.themoviedb.org/documentation/api).
- Open `app.py` and **replace** `'your_tmdb_api_key'` with your actual API key:

```python
API_KEY = 'your_actual_tmdb_api_key'
```

### 4. Run the Application

```bash
python app.py
```

Open your browser and navigate to:  
👉 **http://127.0.0.1:5000**

---

## 👨‍💻 Contributing

Contributions are welcome!

1. Fork the repository  
2. Create a feature branch (`git checkout -b new-feature`)  
3. Commit your changes (`git commit -m 'Add new feature'`)  
4. Push the branch (`git push origin new-feature`)  
5. Open a Pull Request 🎉  

---

## 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## 📩 Support

For questions, suggestions, or issues, feel free to:

- Open an issue on GitHub  
- Contact the developer at: **sure8928@gmail.com**

---

**Thank you for using MovieMate AI!**  
💡 *Explore. Analyze. Enjoy the Movies.*

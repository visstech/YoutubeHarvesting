📊 YouTube Channel Data Analysis App

A Streamlit-based data engineering and analytics application that extracts, stores, and analyzes YouTube channel data using the YouTube Data API v3, PostgreSQL, and interactive visualizations.

🚀 Project Overview 

This application allows users to:

Fetch YouTube channel and video data using a video URL
Collect data for multiple channels (up to 10)
Store data in a PostgreSQL database
Perform SQL-based analytics queries
Visualize insights using Plotly charts
View comments from videos and channels
🎯 Features
🔹 Data Extraction (YouTube API)
Channel details (name, views, description, subscribers, status)
Video details (title, views, likes, comments, duration, etc.)
Playlist details
Comments from videos
Channel-level video list
🔹 Data Storage (PostgreSQL)

Automatically creates and manages tables:

video
channel
playlist
comments

Supports:

Insert with ON CONFLICT handling
Relational mapping between tables
🔹 Data Analysis (SQL Queries)

Predefined analytical questions:

Video names with channel names
Channel with most videos
Top 10 most viewed videos
Comment counts per video
Most liked videos
Likes vs dislikes per video
Total views per channel
Channels with videos in 2024
Average video duration per channel
Most commented videos
🔹 Visualization (Plotly + Streamlit)
Bar charts (horizontal & vertical)
Line charts
Pie charts
Styled tables with gradients
🛠️ Tech Stack
Python 3.x
Streamlit (UI framework)
Google YouTube Data API v3
PostgreSQL
SQLAlchemy
Pandas
Plotly & Matplotlib
isodate
📂 Project Structure
youtube-data-analysis/
│
├── app.py                  # Main Streamlit application
├── requirements.txt        # Dependencies
├── README.md               # Project documentation
└── .streamlit/
    └── secrets.toml       # API keys (not pushed to GitHub)
⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/your-username/youtube-data-analysis.git
cd youtube-data-analysis
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Configure API Key

Create .streamlit/secrets.toml:

[google]
api_key = "YOUR_YOUTUBE_API_KEY"
4️⃣ Setup PostgreSQL Database

Update credentials in the code:

DB_NAME = 'postgres'
DB_USER = 'postgres'
DB_PASSWORD = 'your_password'
DB_HOST = 'localhost'
DB_PORT = '5432'
5️⃣ Run the Application
streamlit run app.py
📊 How It Works
Step 1:

Enter a YouTube video URL

Step 2:

Click Save to Database

Fetches data from YouTube API
Stores in PostgreSQL
Step 3:

Use sidebar options:

Fetch analytical results
View charts
Analyze channel performance
📈 Sample Visualizations
Top Viewed Videos
Likes Distribution
Channel-wise Views
Comment Analysis
Video Duration Insights
🔐 Security Notes
Never expose your API key in GitHub
Use Streamlit secrets for credentials
Secure PostgreSQL access
📌 Future Improvements
MongoDB integration (NoSQL support)
Dashboard authentication system
Real-time YouTube updates
Export analytics to CSV/PDF
Machine Learning-based video trend prediction
👨‍💻 Author

Senthilkumar
📅 Created: 10-Nov-2024

⭐ If you like this project

Give it a ⭐ on GitHub and share it!

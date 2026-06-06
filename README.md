🎬 YouTube Data Analytics Dashboard

🚀 A powerful Streamlit-based analytics platform to extract, store, and visualize YouTube channel data using YouTube Data API v3 + PostgreSQL.

🌟 Live Capabilities

✔ Extract YouTube channel & video data using URL
✔ Store up to 10 channels in PostgreSQL
✔ Perform SQL-based analytics queries
✔ Interactive dashboards with Plotly charts
✔ View video comments & engagement metrics
✔ Real-time data exploration interface

📸 Dashboard Preview

(Add screenshot here for better GitHub attraction)

![App Screenshot](assets/dashboard.png)
🧰 Tech Stack
Technology	Purpose
Streamlit	Web UI
Python	Backend Logic
YouTube API v3	Data Extraction
PostgreSQL	Data Storage
SQLAlchemy	DB Connection
Plotly	Data Visualization
Pandas	Data Processing
📊 Key Analytics Features
🔹 Channel Insights
Channel name, views, description
Total videos & playlists
Channel-level statistics
🔹 Video Insights
Views, likes, dislikes, comments
Video duration analysis
Engagement metrics
🔹 Comment Analytics
Top commented videos
Comment author tracking
Engagement comparison
📈 Visual Dashboards
📊 Popular Visualizations
📌 Top 10 Most Viewed Videos
📌 Channel-wise Total Views
📌 Like vs Dislike Comparison
📌 Comment Distribution
📌 Average Video Duration Analysis
🗄️ Database Schema
📦 Tables Created
video
channel
playlist
comments
⚙️ Installation Guide
1️⃣ Clone Repository
git clone https://github.com/your-username/youtube-analytics.git
cd youtube-analytics
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Add API Key

Create .streamlit/secrets.toml

[google]
api_key = "YOUR_YOUTUBE_API_KEY"
4️⃣ Configure Database
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
5️⃣ Run App
streamlit run app.py
📊 Sample UI Flow
1️⃣ Enter YouTube URL
2️⃣ Click "Save to Database"
3️⃣ Data is stored in PostgreSQL
4️⃣ Select analytics question
5️⃣ View charts + insights
🚀 Future Enhancements

✨ AI-based video performance prediction
✨ Multi-channel comparison dashboard
✨ Export reports (PDF/Excel)
✨ Login authentication system
✨ Cloud deployment (Streamlit Cloud / AWS)

👨‍💻 Developer

Senthilkumar
📅 Created: 10-Nov-2024

⭐ Support

If you like this project:

⭐ Star the repository
🍴 Fork it
🔔 Share with others

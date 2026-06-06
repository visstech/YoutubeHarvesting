🚀 YouTube Data Analytics Platform

A scalable data engineering and analytics platform that extracts, stores, and visualizes YouTube channel insights using YouTube Data API v3, PostgreSQL, and Streamlit.

🧠 Problem Statement

Modern content creators and analysts need a unified system to:

Extract structured YouTube data
Store and manage multi-channel datasets
Perform analytics using SQL
Visualize engagement trends

This project solves that by building a full-stack data pipeline + analytics dashboard.

⚙️ System Architecture
YouTube API
    ↓
Data Extraction Layer (Python)
    ↓
Processing Layer (Pandas, isodate)
    ↓
Database Layer (PostgreSQL)
    ↓
Analytics Layer (SQL Queries)
    ↓
Visualization Layer (Plotly + Streamlit)
🌟 Key Features
📥 Extract YouTube channel & video data using URL
🗄️ Store up to 10 channels in PostgreSQL database
🔗 Relational schema for videos, channels, playlists, comments
📊 SQL-based analytical query engine
📈 Interactive dashboards using Plotly
💬 Comment-level sentiment and engagement tracking
⚡ Real-time data exploration interface
🧰 Tech Stack
Layer	Technology
Frontend	Streamlit
Backend	Python
API	YouTube Data API v3
Database	PostgreSQL
ORM	SQLAlchemy
Visualization	Plotly, Matplotlib
Data Processing	Pandas, isodate
🗄️ Database Design
📌 Tables

Channel

channel_id (PK)
channel_name
channel_views
description
status

Video

video_id (PK)
title
views, likes, dislikes
duration
published_date

Playlist

playlist_id (PK)
channel_id (FK)

Comments

comment_id (PK)
video_id (FK)
comment_text
author
timestamp
📊 Analytics Engine

The system supports advanced SQL analytics:

🔹 Core Insights
Top viewed videos
Most liked videos
Comment-heavy videos
Channel performance ranking
Average video duration per channel
Year-based publishing trends
📈 Sample Dashboards
📊 Engagement Analysis
Views vs Likes vs Comments comparison
Top 10 performing videos
📉 Channel Performance
Total views per channel
Video upload distribution
💬 Comment Analysis
Most discussed videos
Comment frequency per channel
🖥️ UI Preview

Add screenshot here for maximum impact

![Dashboard Preview](assets/dashboard.png)
🚀 Getting Started
1️⃣ Clone Repository
git clone https://github.com/your-username/youtube-analytics.git
cd youtube-analytics
2️⃣ Install Dependencies
pip install -r requirements.txt
3️⃣ Configure API Key

Create .streamlit/secrets.toml

[google]
api_key = "YOUR_YOUTUBE_API_KEY"
4️⃣ Setup PostgreSQL
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"
5️⃣ Run Application
streamlit run app.py
📌 Project Workflow
User Input (YouTube URL)
        ↓
Extract Channel & Video Data
        ↓
Store in PostgreSQL
        ↓
Run SQL Analytics Queries
        ↓
Render Interactive Dashboards
📊 Example Insights Generated
📌 Top 10 most viewed videos across channels
📌 Channel with highest engagement
📌 Average video duration comparison
📌 Comment-to-view ratio analysis
🔐 Security Best Practices
API keys stored in Streamlit secrets
No hardcoded credentials
ON CONFLICT handling in DB inserts
Parameterized SQL queries
🚀 Future Enhancements
🤖 AI-based video performance prediction
🧠 Sentiment analysis on comments
☁️ Cloud deployment (AWS / GCP)
📤 Export analytics to PDF/Excel
📡 Real-time YouTube streaming updates
👨‍💻 Author

Senthilkumar
📅 Created: Nov 2024
💼 Role: Software Engineer | Data & AI Enthusiast

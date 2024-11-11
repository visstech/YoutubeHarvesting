import streamlit as st
from googleapiclient.discovery import build
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os

# Set up YouTube API client
API_KEY = 'AIzaSyCIz8mGnDFN2aurj65cKNoCwnrQ1d-t5gY'
youtube = build('youtube', 'v3', developerKey=API_KEY)

video_url = st.text_input("Enter your Youtube url here") #  
#api_key = 'AIzaSyCIz8mGnDFN2aurj65cKNoCwnrQ1d-t5gY'


def get_channel_id(API_KEY, video_url):
    # Extract video ID from the YouTube URL
    if video_url is not None:
        video_id = video_url.split("v=")[-1]

        # Initialize the YouTube API client
        youtube = build('youtube', 'v3', developerKey=API_KEY)

        # Retrieve video details
        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()

        # Extract the channel ID
        if "items" in response and len(response['items']) > 0:
            channel_id = response['items'][0]['snippet']['channelId']
            return channel_id,video_id
        else:
            return "Channel ID not found"

print('url length:',len(video_url))
if len(video_url) > 0 :
  channel_id,video_id = get_channel_id(API_KEY, video_url)


def get_channel_details(API_KEY, channel_id):
    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Request for channel details
    request = youtube.channels().list(
        part='snippet,statistics,contentDetails,status,topicDetails',
        id=channel_id
    )
    response = request.execute()
    
    if 'items' in response and len(response['items']) > 0:
        channel_info = response['items'][0]
        
        # Extract channel details
        channel_data = {
            "Channel ID": channel_info['id'],
            "Channel Name": channel_info['snippet']['title'],
            "Channel Type": channel_info['kind'],  # General type of resource (usually 'youtube#channel')
            "Channel Views": channel_info['statistics']['viewCount'],
            "Channel Description": channel_info['snippet']['description'],
            "Channel Status": channel_info['status']['privacyStatus']
        }
        return channel_data
    else:
        return "Channel not found or invalid channel ID."


# Function to get playlists of a channel
def get_channel_playlists(API_KEY, channel_id):
    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Request for playlists in the channel
    request = youtube.playlists().list(
        part='snippet',
        channelId=channel_id,
        maxResults=50  # Adjust as needed, max 50 at a time
    )
    response = request.execute()
    
    playlists = []
    
    # Extract playlist details
    if 'items' in response:
        for item in response['items']:
            playlists.append({
                "Playlist ID": item['id'],
                "Channel ID": item['snippet']['channelId'],
                "Playlist Name": item['snippet']['title']
            })
    else:
        return "No playlists found or invalid channel ID."
    
    return playlists
 
# Function to get comments from a video
def get_video_comments(API_KEY, video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    comments = []

    # Request to get comments
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=10  # Limiting to 10 comments per video for demo; adjust as needed
    )
    response = request.execute()

    # Extract relevant comment details
    for item in response.get('items', []):
        comment = item['snippet']['topLevelComment']['snippet']
        comments.append({
            "Comment ID": item['id'],
            "Video ID": video_id,
            "Comment Text": comment['textDisplay'],
            "Comment Author": comment['authorDisplayName'],
            "Comment Published Date": comment['publishedAt']
        })
    return comments


# PostgreSQL connection details
DB_NAME = 'postgres' #'your_database_name'
DB_USER = 'postgres' #'your_username'
DB_PASSWORD = 'PostViss' #'your_password'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Function to connect to PostgreSQL
def connect_to_db():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
    )
    return conn

# Function to create table if not exists
def create_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS youtube_videos (
            video_id VARCHAR(50) PRIMARY KEY,
            playlist_id VARCHAR(50),
            title TEXT,
            description TEXT,
            published_date TIMESTAMP,
            view_count BIGINT,
            like_count BIGINT,
            dislike_count BIGINT,
            favorite_count BIGINT,
            comment_count BIGINT,
            duration VARCHAR(20),
            thumbnail_url TEXT,
            caption_status BOOLEAN
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Channel (
            channel_id VARCHAR(255) PRIMARY KEY,
            channel_name VARCHAR(255),
            channel_type  VARCHAR(255),
            channel_views  BIGINT,
            channel_description TEXT,            
            channel_status VARCHAR(255)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Playlist (
            playlist_id VARCHAR(255) PRIMARY KEY,
            channel_id VARCHAR(255) ,
            playlist_name  VARCHAR(255)
        )
    ''') 
    
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS Comments (
            comment_id  VARCHAR(255) PRIMARY KEY,
            video_id    VARCHAR(255),
            comment_text TEXT,
            comment_author VARCHAR(255),
            comment_published_date TIMESTAMP
            )
            ''' ) 
    
    conn.commit()
    cursor.close()
    conn.close()

# Function to get video details from YouTube API
def get_video_details(video_id):
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=video_id
    )
    response = request.execute()
    video = response['items'][0]
    
    details = {
        "video_id": video_id,
        "playlist_id": None,  # Update if you want to include playlist data
        "title": video["snippet"]["title"],
        "description": video["snippet"]["description"],
        "published_date": datetime.strptime(video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
        "view_count": int(video["statistics"].get("viewCount", 0)),
        "like_count": int(video["statistics"].get("likeCount", 0)),
        "dislike_count": int(video["statistics"].get("dislikeCount", 0)),
        "favorite_count": int(video["statistics"].get("favoriteCount", 0)),
        "comment_count": int(video["statistics"].get("commentCount", 0)),
        "duration": video["contentDetails"]["duration"],
        "thumbnail_url": video["snippet"]["thumbnails"]["high"]["url"],
        "caption_status": video["contentDetails"].get("caption", False)
    }
    return details

# Function to insert data into PostgreSQL
def insert_video_details(details):
    conn = connect_to_db()
    cursor = conn.cursor()
    insert_query = '''
        INSERT INTO youtube_videos (
            video_id, playlist_id, title, description, published_date, view_count, 
            like_count, dislike_count, favorite_count, comment_count, 
            duration, thumbnail_url, caption_status
        ) VALUES (
            %(video_id)s, %(playlist_id)s, %(title)s, %(description)s, %(published_date)s, %(view_count)s, 
            %(like_count)s, %(dislike_count)s, %(favorite_count)s, %(comment_count)s, 
            %(duration)s, %(thumbnail_url)s, %(caption_status)s
        ) ON CONFLICT (video_id) DO NOTHING
    '''
    cursor.execute(insert_query, details)
    conn.commit()
    cursor.close()
    conn.close()


def insert_channel_details(channel_details):
    conn = connect_to_db()
    cursor = conn.cursor()
    insert_query = '''
        INSERT INTO Channel (
            channel_id, channel_name, channel_type, channel_views, channel_description, channel_status
        ) VALUES (
            %(Channel ID)s, %(Channel Name)s, %(Channel Type)s, %(Channel Views)s, %(Channel Description)s, %(Channel Status)s
        ) ON CONFLICT (channel_id) DO NOTHING
    '''
    cursor.execute(insert_query, channel_details)
    conn.commit()
    cursor.close()
    conn.close()

def insert_playlist_details(playlist_details):
    conn = connect_to_db()
    cursor = conn.cursor()
    insert_query = '''
        INSERT INTO Playlist (
            playlist_id, channel_id, playlist_name
        ) VALUES (
            %(Playlist ID)s, %(Channel ID)s, %(Playlist Name)s
        ) ON CONFLICT (playlist_id) DO NOTHING
    '''
    #cursor.execute(insert_query, playlist_details)
    for details in playlist_details:
        cursor.execute(insert_query, details)
    conn.commit()
    cursor.close()
    conn.close()



def insert_comments_details(comments_details):
    conn = connect_to_db()
    cursor = conn.cursor()
    insert_query = '''
        INSERT INTO Comments (
            comment_id, video_id, comment_text,comment_author,comment_published_date
        ) VALUES (
            %(Comment ID)s, %(Video ID)s, %(Comment Text)s, %(Comment Author)s, %(Comment Published Date)s
        ) ON CONFLICT (comment_id) DO NOTHING
    '''
  
    for details in comments_details:
        cursor.execute(insert_query, details)
    conn.commit()
    cursor.close()
    conn.close()



# Streamlit UI
st.title("YouTube Video Details Fetcher")

#video_id = st.text_input("Enter YouTube Video ID:")

if st.button("Fetch Video Details"):
    if video_id and channel_id:
        create_table()
        details = get_video_details(video_id)
        channel_id,video_id = get_channel_id(API_KEY, video_url)
        channel_details = get_channel_details(API_KEY, channel_id)
        playlist_details = get_channel_playlists(API_KEY, channel_id)
        comments_details = get_video_comments(API_KEY, video_id)
    
        print('channel_details:\n',channel_details)
        print('comments_details:\n',comments_details)
        insert_video_details(details)
        insert_channel_details(channel_details)
        insert_playlist_details(playlist_details)
        insert_comments_details(comments_details)
        
        # Display video details
        st.write("**Title:**", details["title"])
        st.write("**Description:**", details["description"])
        st.write("**Published Date:**", details["published_date"])
        st.write("**View Count:**", details["view_count"])
        st.write("**Like Count:**", details["like_count"])
        st.write("**Dislike Count:**", details["dislike_count"])
        st.write("**Favorite Count:**", details["favorite_count"])
        st.write("**Comment Count:**", details["comment_count"])
        st.write("**Duration:**", details["duration"])
        st.write("**Thumbnail:**")
        st.image(details["thumbnail_url"])
        st.write("**Caption Status:**", "Available" if details["caption_status"] else "Not Available")
        
        st.success("Video details fetched and saved to the database!")
    else:
        st.error("Please enter a valid video ID.")

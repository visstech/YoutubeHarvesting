import streamlit as st
from googleapiclient.discovery import build
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os
import pandas as pd 
from streamlit_custom_notification_box import custom_notification_box as scnb
from sqlalchemy import create_engine

#ackground Image
#st.markdown(
#    """
#    <style>
#    .stApp {
#        background-image: url('https://static8.depositphotos.com/1000152/1020/i/450/depositphotos_10200176-stock-photo-beach-and-tropical-sea.jpg');
#        background-size: cover;
#        background-position: center;
#        opacity: 0.9;
#    }
#    </style>
#    """,
#    unsafe_allow_html=True
#)

# Define the background color CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #d6eaf8; /* Choose any color code */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set sidebar background image
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background-image: url("https://images.pexels.com/photos/381739/pexels-photo-381739.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1");
        background-size: cover;
        background-position: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Set up YouTube API client

API_KEY = 'AIzaSyCIz8mGnDFN2aurj65cKNoCwnrQ1d-t5gY'
youtube = build('youtube', 'v3', developerKey=API_KEY)
st.markdown("<h1 style='color:DarkSlateGray'>Youtube Harvesting Application developed by Vi.S.Senthilkumar </h1>", unsafe_allow_html=True)
video_url = st.text_input("Enter your Youtube url here") #  
st.markdown(" ### Enter your Youtube url in the above input box to get detailed information about the youtube channel")
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
            "Channel Status": channel_info['status']['privacyStatus'],
             "Channel video id":video_id #newly added.
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
        videoId=video_id 
        #maxResults=100  # Limiting to 10 comments per video for demo; adjust as needed
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
        CREATE TABLE IF NOT EXISTS video(
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
            channel_status VARCHAR(255),
            channel_video_id VARCHAR(255)
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
        INSERT INTO video (
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
            channel_id, channel_name, channel_type, channel_views, channel_description, channel_status,channel_video_id
        ) VALUES (
            %(Channel ID)s, %(Channel Name)s, %(Channel Type)s, %(Channel Views)s, %(Channel Description)s, %(Channel Status)s, %(Channel video id)s
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

def AlertBox(wht_msg):
    styles = {'material-icons':{'color': '#FF0000'},
            'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
            'notification-text': {'':''},
            'close-button':{'':''},
            'link':{'':''}}

    scnb(icon='info', 
        textDisplay=wht_msg, 
        externalLink='', 
        url='#', 
        styles=styles, 
        key="foo")

# Function to connect to PostgreSQL and fetch data
def get_data():
    # Connect to the PostgreSQL database
    engine = onn = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}') #connect_to_db()
    #create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    
    # Query to fetch data
    query = ''' select channel_name,channel_video_id,COUNT(COMMENT_ID) from channel n,comments c
              where n.channel_video_id = c.video_id
              group by channel_name,channel_video_id ''' # Replace 'your_table_name' with the actual table name
    
    # Fetch data into a DataFrame
    data = pd.read_sql(query, engine)
    return data




# Streamlit UI
st.title("YouTube Video Details")


st.markdown("""
    <style>
    .stButton > button {
        color: white;
        background-color: #6200EE;
        font-size: 18px;
        padding: 8px 20px;
        border-radius: 10px;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #3700B3;
    }
    </style>
""", unsafe_allow_html=True)

#video_id = st.text_input("Enter YouTube Video ID:")

if st.sidebar.button("Save in database") : #and len(video_url) > 0 :
    if len(video_url) == 0 :
        st.warning("Please enter URL to get youtube vido deatils to store in the database")
    elif video_id and channel_id:
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
        
        #st.success("Video details fetched and saved to the database!")
        AlertBox("Video details fetched and saved to the database!")
    else:
        st.error("Please enter a valid URL.")

# Function to get video IDs from a channel
def get_channel_videos(API_KEY, channel_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=20,  # Limiting to 10 videos for demo; adjust as needed
        type="video"
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    return video_ids
        

# Fetch and display comments when button is clicked

if st.sidebar.button("Show Comments") :
    if len(video_url) == 0 :
       st.sidebar.write('Please input the url and try again')
    elif API_KEY and channel_id:
        try:
            st.write("Fetching video IDs from channel...")
            video_ids = get_channel_videos(API_KEY, channel_id)
            all_comments = []

            for video_id in video_ids:
                st.write(f"Fetching comments for Video ID: {video_id}")
                comments = get_video_comments(API_KEY, video_id)
                all_comments.extend(comments)

            if all_comments:
                st.subheader("Channel Comments")
                for comment in all_comments:
                    st.write(f"**Comment ID**: {comment['Comment ID']}")
                    st.write(f"**Video ID**: {comment['Video ID']}")
                    st.write(f"**Comment Text**: {comment['Comment Text']}")
                    st.write(f"**Comment Author**: {comment['Comment Author']}")
                    st.write(f"**Comment Published Date**: {comment['Comment Published Date']}")
                    st.write("---")
            else:
                st.error("No comments found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please provide both API Key and Channel ID.")

if st.sidebar.button('Get comments and channel detail') :
    if len(video_url) == 0 :
       st.sidebar.write('Please input the url and try again')
    else:
        # Display data in Streamlit
        st.title("Channel, video id and it's corresponding comments count")
        data = get_data()
        st.write(data)
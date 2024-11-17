import streamlit as st
from googleapiclient.discovery import build
import psycopg2
from psycopg2 import sql
from datetime import datetime
import os
import pandas as pd 
from streamlit_custom_notification_box import custom_notification_box as scnb
from sqlalchemy import create_engine
import isodate
import logging
logging.getLogger("streamlit").setLevel(logging.ERROR) # to ignore the warrnings 


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


# Inject custom CSS for styling the input label
st.markdown(
    """
    <style>
    label {
        font-size: 20px; /* Adjust font size of the label */
        font-weight: bold; /* Make the label bold (optional) */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set up YouTube API client

API_KEY = 'AIzaSyCIz8mGnDFN2aurj65cKNoCwnrQ1d-t5gY'
youtube = build('youtube', 'v3', developerKey=API_KEY)
#st.markdown("<h1 style='color:DarkSlateGray'>Youtube Harvesting Application developed by Vi.S.Senthilkumar </h1>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="
        border: 5px solid #4CAF50; 
        border-radius: 20px; 
        padding: 20px; 
        background-color: #f9f9f9;
        color: #333;
        font-size: 30px;
    ">
        <p><b></b> <h3 style='color:DarkSlateGray'>Youtube Harvesting Application developed by Vi.S.Senthilkumar.</h3></p>
    </div>
    """,
    unsafe_allow_html=True
)
video_url = st.text_input("Enter your Youtube url here") #  
#st.markdown(" ### Enter your Youtube url in the above input box to get detailed information about the youtube channel")

st.markdown(
    """
    <div style="
        border: 5px solid #4CAF50; 
        border-radius: 20px; 
        padding: 20px; 
        background-color: #f9f9f9;
        color: #333;
        font-size: 30px;
    ">
        <p><b></b> <h4 style='color:DarkSlateGray'>Enter your Youtube url in the above input box to get detailed information about the youtube channel.</h4></p>
    </div>
    """,
    unsafe_allow_html=True
)
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
        videoId=video_id,
        maxResults=100  # Limiting to 10 comments per video for demo; adjust as needed
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
            duration BIGINT,
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
    #Added on 17-NOV-2024
    channel_response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()
    
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Step 2: Get video IDs from the uploads playlist
    video_ids = []
    next_page_token = None

    while True:
        playlist_response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in playlist_response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = playlist_response.get('nextPageToken')
        if not next_page_token:
            break

    # Step 3: Get video durations
    durations = {}
    for i in range(0, len(video_ids), 50):
        video_response = youtube.videos().list(
            part="contentDetails",
            id=",".join(video_ids[i:i+50])
        ).execute()

        for item in video_response['items']:
            video_id = video_id #item['id']
            duration_iso = item['contentDetails']['duration']
            duration_seconds = isodate.parse_duration(duration_iso).total_seconds()
            durations[video_id] = duration_seconds
           # st.write(durations[video_id])
   #End of code added on 17-Nov-2024.
    
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
        "duration": durations[video_id] ,#video["contentDetails"]["duration"],
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
    st.write('Duriation :',details['duration'])
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
def get_data(question_no):
    # Connect to the PostgreSQL database
    engine = onn = create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}') #connect_to_db()
    #create_engine(f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    
    # Query to fetch data
    query1 = ''' 
                SELECT title "Video Name ",CHANNEL_NAME "Channel Name" FROM VIDEO,CHANNEL
                WHERE CHANNEL_video_ID = VIDEO_ID'''
                
    query2 = ''' SELECT CHANNEL_NAME,COUNT(playlist_id) AS VIDEO_COUNT
                    FROM CHANNEL,playlist
                    WHERE playlist.channel_id = channel.channel_id
                    GROUP BY CHANNEL_NAME
                    ORDER BY VIDEO_COUNT DESC
                    LIMIT 1;
             '''             
    query3 = '''  SELECT Title "Video Name", CHANNEL_NAME "Channel", view_count View
                FROM video,channel
                WHERE CHANNEL_video_ID = VIDEO_ID
                ORDER BY view DESC
                LIMIT 10; 
            '''    
    query4 = '''SELECT Title "Video Name", COUNT(comment_id) AS comment_count
                FROM comments
                JOIN video ON comments.video_id = video.video_id
                GROUP BY Title
                ORDER BY comment_count DESC;
             '''      
    query5 = ''' SELECT TITLE "Video Name", channel_name "Channel Name", like_count Likes
                FROM video,CHANNEL
                WHERE CHANNEL_video_ID = VIDEO_ID
                ORDER BY like_count DESC
                LIMIT 1;
             '''        
                        
    query11 = ''' select channel_name,channel_video_id,COUNT(COMMENT_ID) from channel n,comments c
              where n.channel_video_id = c.video_id
              group by channel_name,channel_video_id ''' # Replace 'your_table_name' with the actual table name
    
    query6 = '''
            SELECT title video_name, like_count, dislike_count
            FROM video'''        
            
    query7 = ''' SELECT channel_name, SUM(view_count) AS total_views
                FROM video ,CHANNEL
                WHERE CHANNEL_video_ID = VIDEO_ID
                GROUP BY channel_name;
             '''        
    query8 = ''' SELECT DISTINCT channel_name
            FROM video,channel
            WHERE CHANNEL_video_ID = VIDEO_ID
            AND EXTRACT(YEAR FROM video.published_date) = 2024;    
             '''         
             
    query9 = ''' SELECT channel_name , avg(duration) AS avg_duration
                    FROM video ,CHANNEL
                    WHERE CHANNEL_video_ID = VIDEO_ID
                    GROUP BY channel_name
                    ORDER BY avg_duration DESC;
             '''         
    query10  = '''SELECT TITLE video_name, channel_name, COUNT(comment_id) AS comment_count
                    FROM comments
                    JOIN video ON comments.video_id = video.video_id
                    JOIN CHANNEL ON CHANNEL_video_ID = video.VIDEO_ID
                    GROUP BY video_name, channel_name
                    ORDER BY comment_count DESC
                    LIMIT 1;    
               '''         
    st.write('Question is:',question) 
    
    # Fetch data into a DataFrame
    if question_no == '1' :
       data = pd.read_sql(query1, engine)
    elif  question_no == '2' :
       data = pd.read_sql(query2, engine)
    elif  question_no == '3' :
       data = pd.read_sql(query3, engine)
    elif  question_no == '4' :
       data = pd.read_sql(query4, engine)
    elif  question_no == '5' :
       data = pd.read_sql(query5, engine)
    elif  question_no == '6' :
       data = pd.read_sql(query6, engine)
    elif  question_no == '7' :
       data = pd.read_sql(query7, engine)       
    elif  question_no == '8' :
       data = pd.read_sql(query8, engine)        
    elif  question_no == '9' :
       data = pd.read_sql(query9, engine) 
    elif question_no == '10' :
       data = pd.read_sql(query10, engine) 
    else:
        st.write('Please choose the correct question')      
    return data




# Streamlit UI



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
        st.title("YouTube Video Details")
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
            st.write("Fetching Comments from channel...")
            video_ids = get_channel_videos(API_KEY, channel_id)
            all_comments = []

            for video_id in video_ids:
                #st.write(f"Fetching comments for Video ID: {video_id}")
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

# Inject custom CSS to style the selectbox
st.markdown(
    """
    <style>
    /* Adjust the font size of the selectbox label */
    div[data-testid="stSelectbox"] > label {
        font-size: 50px; /* Change this value to your desired font size */
        font-weight: bold; /* Optional: Add bold style */
        color: #ff6600; /* Optional: Change the text color */
    }
    </style>
    """,
    unsafe_allow_html=True
)
        
question = st.sidebar.selectbox('Select your Question in the below options',("1. Names of all the videos and their corresponding channels",
                                                                  "2. Channels with the most number of videos and how many they have",
                                                                  "3. Top 10 most viewed videos and their respective channels",
                                                                  "4. Number of comments on each video and their corresponding video names",
                                                                  "5. Videos with the highest number of likes and their corresponding channel names",
                                                                  "6. Total likes and dislikes for each video and their corresponding video names",
                                                                  "7. Total number of views for each channel and their corresponding channel names",
                                                                  "8. Names of all channels that published videos in 2024",
                                                                  "9. Average duration of all videos in each channel and their corresponding channel names",
                                                                  "10. Videos with the highest number of comments and their corresponding channel names"))        

# Extract the question number from the selected option
question_number = question.split(".")[0]  # Splits the string and takes the first part
question = question.split(".")[1]  # Splits the string and takes the first part

if st.sidebar.button('Get comments and channel detail') :
    if len(video_url) == 0 :
       st.sidebar.write('Please input the url and try again')
    else:
        # Display data in Streamlit
        #st.title("Channel, video id and it's corresponding comments count")
        data = get_data(question_number)
        st.write(data)
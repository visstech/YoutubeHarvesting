#pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client streamlit pandas

import streamlit as st

from googleapiclient.discovery import build
import pandas as pd
import datetime
from datetime import timedelta
import isodate  # Import the isodate library

#st.title('Youtube Harvesting App developed by Senthilkumar')
st.markdown("<h1 style='color:blue;'>Youtube Harvesting App developed by Senthilkumar</h1>", unsafe_allow_html=True)
video_url = st.text_input("Enter your Youtube url here") #  
api_key = 'AIzaSyCIz8mGnDFN2aurj65cKNoCwnrQ1d-t5gY'


def get_channel_id(api_key, video_url):
    # Extract video ID from the YouTube URL
    if video_url is not None:
        video_id = video_url.split("v=")[-1]

        # Initialize the YouTube API client
        youtube = build('youtube', 'v3', developerKey=api_key)

        # Retrieve video details
        request = youtube.videos().list(
            part='snippet',
            id=video_id
        )
        response = request.execute()

        # Extract the channel ID
        if "items" in response and len(response['items']) > 0:
            channel_id = response['items'][0]['snippet']['channelId']
            return channel_id
        else:
            return "Channel ID not found"

print('url length:',len(video_url))
if len(video_url) > 0 :
  channel_id = get_channel_id(api_key, video_url)

  print(f"Channel ID: {channel_id}")
  
def get_channel_details(api_key, channel_id):
    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)
    
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

# Replace 'YOUR_API_KEY' with your actual API key as a plain string
#api_key = 'YOUR_API_KEY'
#channel_id = 'UCoTqLtgspGTZ15KkYfeyA2Q'  # Example channel ID
if len(video_url) > 0 :
   print('Coming here')
   channel_details = get_channel_details(api_key, channel_id)

   print("Channel Details:")
   for key, value in channel_details.items():
        print(f"{key}: {value}")

if st.button("Get Channel Details"):
    if api_key and channel_id:
        try:
            channel_details = get_channel_details(api_key, channel_id)
            if isinstance(channel_details, dict):
                st.subheader("Channel Details")
                for key, value in channel_details.items():
                    st.write(f"**{key}**: {value}")
            else:
                st.error(channel_details)
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please provide both API Key and Channel ID.")
 
 
 
 # Function to get playlists of a channel
def get_channel_playlists(api_key, channel_id):
    # Initialize the YouTube API client
    youtube = build('youtube', 'v3', developerKey=api_key)
    
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

if len(video_url) > 0 :
    playlists_data = get_channel_playlists(api_key, channel_id)
    print(playlists_data)
    if len(playlists_data) > 0 :
       Playlist_df = pd.DataFrame(playlists_data)
       st.title('Vieo Playlist information:')
       st.write(Playlist_df)    



# Function to get video IDs from a channel
def get_channel_videos(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        part="id",
        channelId=channel_id,
        maxResults=20,  # Limiting to 10 videos for demo; adjust as needed
        type="video"
    )
    response = request.execute()

    video_ids = [item['id']['videoId'] for item in response.get('items', [])]
    return video_ids

# Function to get comments from a video
def get_video_comments(api_key, video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
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

# Streamlit app UI
st.title("YouTube Channel Comments Viewer")

# Input fields for API key and Channel ID
#api_key = st.text_input("Enter your YouTube API Key:", type="password")
#channel_id = st.text_input("Enter YouTube Channel ID:")

# Fetch and display comments when button is clicked
if st.button("Get Channel Comments"):
    if api_key and channel_id:
        try:
            st.write("Fetching video IDs from channel...")
            video_ids = get_channel_videos(api_key, channel_id)
            all_comments = []

            for video_id in video_ids:
                st.write(f"Fetching comments for Video ID: {video_id}")
                comments = get_video_comments(api_key, video_id)
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
        





# Function to get video details from a channel
def get_channel_videos_dtl(api_key, channel_id):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Step 1: Get playlist ID of the channel's uploaded videos
    channel_request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    channel_response = channel_request.execute()
    
    # Extract the upload playlist ID
    uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Step 2: Get video IDs from the playlist
    playlist_items_request = youtube.playlistItems().list(
        part="snippet",
        playlistId=uploads_playlist_id,
        maxResults=10  # Limiting for demo purposes, adjust as needed
    )
    playlist_items_response = playlist_items_request.execute()
    
    video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_items_response['items']]
    
    # Step 3: Get video details
    videos = []
    video_details_request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    )
    video_details_response = video_details_request.execute()
    
    # Extract details for each video
    for item in video_details_response['items']:
        # Parse the duration using isodate library
        duration = isodate.parse_duration(item['contentDetails']['duration'])
        duration_str = str(duration)

        videos.append({
            "Video ID": item['id'],
            "Playlist ID": uploads_playlist_id,
            "Video Name": item['snippet']['title'],
            "Video Description": item['snippet']['description'],
            "Published Date": item['snippet']['publishedAt'],
            "View Count": item['statistics'].get('viewCount', '0'),
            "Like Count": item['statistics'].get('likeCount', '0'),
            "Dislike Count": item['statistics'].get('dislikeCount', '0'),
            "Favorite Count": item['statistics'].get('favoriteCount', '0'),
            "Comment Count": item['statistics'].get('commentCount', '0'),
            "Duration": duration_str,
            "Thumbnail": item['snippet']['thumbnails']['high']['url'],
            "Caption Status": item['contentDetails'].get('caption', 'false')
        })
    return videos

# Streamlit app UI
st.title("YouTube Channel Videos Viewer")

# Input fields for API key and Channel ID
#api_key = st.text_input("Enter your YouTube API Key:", type="password")
#channel_id = st.text_input("Enter YouTube Channel ID:")

# Fetch and display video details when button is clicked
if st.button("Get Channel Videos"):
    if api_key and channel_id:
        try:
            videos = get_channel_videos_dtl(api_key, channel_id)
            
            if videos:
                st.subheader("Channel Videos")
                for video in videos:
                    st.write(f"**Video ID**: {video['Video ID']}")
                    st.write(f"**Playlist ID**: {video['Playlist ID']}")
                    st.write(f"**Video Name**: {video['Video Name']}")
                    st.write(f"**Description**: {video['Video Description']}")
                    st.write(f"**Published Date**: {video['Published Date']}")
                    st.write(f"**View Count**: {video['View Count']}")
                    st.write(f"**Like Count**: {video['Like Count']}")
                    st.write(f"**Dislike Count**: {video['Dislike Count']}")
                    st.write(f"**Favorite Count**: {video['Favorite Count']}")
                    st.write(f"**Comment Count**: {video['Comment Count']}")
                    st.write(f"**Duration**: {video['Duration']}")
                    st.write(f"**Thumbnail**: {video['Thumbnail']}")
                    st.image(video['Thumbnail'])
                    st.write(f"**Caption Status**: {video['Caption Status']}")
                    st.write("---")
            else:
                st.error("No videos found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please provide both API Key and Channel ID.")
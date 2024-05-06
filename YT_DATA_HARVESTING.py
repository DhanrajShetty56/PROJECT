#importing important libraries
from googleapiclient.discovery import build
import pymongo
import pandas as pd
import psycopg2
import streamlit as st

#API connection
def Api_connect():
    Api_Id = "AIzaSyDleyUBU7KGANE6uVrq6ZF_CI4UIpWdvgc"
    api_service_name ="youtube"
    api_version = "v3"

    youtube = build(api_service_name,api_version,developerKey =Api_Id)

    return youtube

youtube = Api_connect()


##Get Channel Information

def get_channel_info(Channel_id):
    request = youtube.channels().list(                                          
                part= "snippet,contentDetails,statistics",
                id = Channel_id
    )
    response = request.execute()


    for i in response['items']:
        data = dict(Channel_Name= i['snippet']['title'],
                    Channel_Id= i['id'],
                    Subscribers= i['statistics']['subscriberCount'],
                    Views = i['statistics']['viewCount'],
                    Channel_description = i ['snippet'] ['description'],
                    Total_videos =i['statistics']['videoCount'],
                    playlist_id = i['contentDetails']['relatedPlaylists']['uploads'])
    return data

## To get video_id
def get_videos_ids(channel_id):

    video_ids =[]

    response = youtube.channels().list(id = channel_id,
                                    part = 'contentDetails').execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_Page_Token = None 

    while True:
        response1 = youtube.playlistItems().list(
                                        part = 'snippet',
                                        playlistId = playlist_id,
                                        maxResults=50,
                                        pageToken=next_Page_Token).execute()

        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_Page_Token =response1.get('nextPageToken')

        if next_Page_Token is None:
            break
    return video_ids

# To get video details

def get_video_details(Videos_Ids):

    video_details =[]

    for video in Videos_Ids:
        request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id= video
            )
        response = request.execute()

        for i in response['items']:
            data=dict(
                       Channel_Name = i['snippet']['channelTitle'],
                        Channel_Ids= i['snippet']['channelId'],
                        Video_Id = i['id'],
                        Video_Name = i['snippet']['title'],
                        Video_Description = i['snippet']['description'],
                        PublishedAt =i['snippet']['publishedAt'],
                        View_Count =i['statistics']['viewCount'],
                        Like_Count =i['statistics'].get('likeCount'),
                        Favorite_Count=i['statistics'].get('favoriteCount'),
                        Comment_Count =i['statistics'].get('commentCount'),
                        Duration=i['contentDetails']['duration'],
                        Thumbnail=i ['snippet']['thumbnails']['default']['url'],
                        Caption_Status =i ['contentDetails']['caption']
            )
            video_details.append(data)

    return video_details

# To get comment details

def get_commentdetails(Videos_Ids):

    Comment_data= []

    for video in Videos_Ids:
        try:
            next_page= None
            while True:
                    request = youtube.commentThreads().list(
                            part="snippet",
                            videoId= video,
                            maxResults= 100,
                            pageToken= next_page
                        )
                    response_commentdetails = request.execute()


                    for i in response_commentdetails['items']:
                        co_data= dict(
                        Comment_Id= i['id'],
                        Video_id=i['snippet']['videoId'],
                        Comment_Text= i['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author= i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_PublishedAt= i['snippet']['topLevelComment']['snippet']['publishedAt']
                        )
                        Comment_data.append(co_data)

                    if "nextPageToken" in response_commentdetails:
                        next_page = response_commentdetails["nextPageToken"]
                    else:
                        break 
        except:
         pass
    return Comment_data

# Connecting to MongoDB

client = pymongo.MongoClient("mongodb+srv://dhanraj56:DJtvkxxvzd54qzF4@cluster0.0xjsjhm.mongodb.net/")

db1 = client['youtube']
mycol = db1["Channel details"]


def Alldetails(Channel_id):
    Channel_details = get_channel_info(Channel_id)
    Video_id = get_videos_ids(Channel_id)
    Video_Details = get_video_details(Video_id)
    Comment_details = get_commentdetails(Video_id)


    mycol.insert_one({"Channal_info": Channel_details, "video_info": Video_Details, "comment_info":Comment_details})

    return 'Data has been uploaded into MongoDB Successfully'


# Creating channel table in postgres

def channel_table():

    db_1=psycopg2.connect(host='localhost',
                            user='postgres',
                            password='9867335172$Ss',
                            database='youtube',
                            port= '5432')

    cursor = db_1.cursor()


    

    Drop_query = ''' DROP TABLE IF EXISTS channels'''

    cursor.execute(Drop_query)
    db_1.commit()

    create_query='''CREATE TABLE IF NOT EXISTS channels(Channel_Name varchar(100),
                                                    Channel_Id varchar(100) primary key,
                                                    Subscription_Count bigint,
                                                    Channel_Views bigint,
                                                    Channel_Description text,
                                                    Total_videos int,
                                                    Playlist_Id varchar(100))'''

    cursor.execute(create_query)
    db_1.commit()

    # Fetching channel data from MongoDB 

    Ch_list =[]

    db1 = client["youtube"]
    mycol = db1["Channel details"]

    for ch_data in mycol.find({},{"_id":0,"Channal_info": 1}):
        Ch_list.append(ch_data['Channal_info'])

    df = pd.DataFrame(Ch_list)


    for index,row in df.iterrows():
            insert_query= '''INSERT INTO channels (Channel_Name,
                                                Channel_Id,
                                                Subscription_Count,
                                                Channel_Views,
                                                Channel_Description,
                                                Total_videos,
                                                Playlist_Id)

                                                VALUES(%s,%s,%s,%s,%s,%s,%s)'''
            
            value=(row['Channel_Name'],
                row['Channel_Id'],
                row['Subscribers'],
                row['Views'],
                row['Channel_description'],
                row['Total_videos'],
                row['playlist_id'])
        
            cursor.execute(insert_query,value)
            db_1.commit()


# Creating Video table in postgres

def video_table():

        db_1=psycopg2.connect(host='localhost',
                        user='postgres',
                        password='9867335172$Ss',
                        database='youtube',
                        port= '5432')

        cursor = db_1.cursor()

        # Creating Video table in postgres

        Drop_query = ''' DROP TABLE IF EXISTS videos'''

        cursor.execute(Drop_query)
        db_1.commit()

        create_query='''CREATE TABLE IF NOT EXISTS videos(Channel_Name  varchar(100),
                                                        Channel_Ids varchar(50),
                                                        Video_Id  varchar(50) primary key,
                                                        Video_Name  varchar(100),
                                                        Video_Description text ,
                                                        PublishedAt timestamp,
                                                        View_Count bigint,
                                                        Like_Count bigint,
                                                        Favorite_Count int,
                                                        Comment_Count bigint, 
                                                        Duration interval,
                                                        Thumbnail varchar(100),
                                                        Caption_Status varchar(50)
                                                        )'''

        cursor.execute(create_query)
        db_1.commit()

        # Fetching videos data from MongoDB

        Videos_data =[]
        mycol = db1["Channel details"]

        for vid_data in mycol.find({},{'_id':0,'video_info':1}):
                for i in vid_data['video_info']:
                        Videos_data.append(i)

        df2 = pd.DataFrame(Videos_data)

        #Inserting videos table in postgres

        for index,row in df2.iterrows():

                insert_query= '''INSERT INTO videos(Channel_Name,
                                        Channel_Ids,
                                        Video_Id ,
                                        Video_Name ,
                                        Video_Description ,
                                        PublishedAt,
                                        View_Count ,
                                        Like_Count ,
                                        Favorite_Count ,
                                        Comment_Count , 
                                        Duration ,
                                        Thumbnail ,
                                        Caption_Status
                                        )

                                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

                value = (
                    row['Channel_Name'],
                    row['Channel_Ids'],
                    row['Video_Id'],
                    row['Video_Name'],
                    row['Video_Description'],
                    row['PublishedAt'],
                    row['View_Count'],
                    row['Like_Count'],
                    row['Favorite_Count'],
                    row['Comment_Count'],
                    row['Duration'],
                    row['Thumbnail'],
                    row['Caption_Status']
                    )
                
                cursor.execute(insert_query,value)
                db_1.commit()

# Creating comment table in postgres
        
def comment_table():

    db_1=psycopg2.connect(host='localhost',
                            user='postgres',
                            password='9867335172$Ss',
                            database='youtube',
                            port= '5432')

    cursor = db_1.cursor()


    Drop_query = ''' DROP TABLE IF EXISTS comment'''

    cursor.execute(Drop_query)
    db_1.commit()

    create_query='''CREATE TABLE IF NOT EXISTS comment(Comment_Id varchar(200) primary key,
                                                        Video_id varchar(100),
                                                        Comment_Text text,
                                                        Comment_Author varchar(150),
                                                        Comment_PublishedAt timestamp)'''

    cursor.execute(create_query)
    db_1.commit()

    # Fetching comment data from MongoDB

    Comment_data =[]
    mycol = db1["Channel details"]

    for Com_data in mycol.find({},{'_id':0,'comment_info':1}):
        for i in Com_data ['comment_info']:
            Comment_data.append(i)

    df3 = pd.DataFrame(Comment_data)
    df3.drop_duplicates(inplace = True)

    #Inserting videos table in postgres

    for index,row in df3.iterrows():
        
        insert_query= '''INSERT INTO comment(Comment_Id,
                                            Video_id,
                                            Comment_Text,
                                            Comment_Author,
                                            Comment_PublishedAt
                                            )

                                                    
                                            VALUES(%s,%s,%s,%s,%s)'''

        value = (
                row['Comment_Id'],
                row['Video_id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_PublishedAt'],
                )
                
        cursor.execute(insert_query,value)
        db_1.commit()


def table():
    
    channel_table()
    video_table()
    comment_table()

    return ('Table has been created in SQL Successfully')

def show_channel_details():
    Ch_list =[]
    mycol = db1["Channel details"]

    for ch_data in mycol.find({},{"_id":0,"Channal_info": 1}):
        Ch_list.append(ch_data['Channal_info'])

    df = st.dataframe(Ch_list)

def show_video_details():
    Videos_data =[]
    mycol = db1["Channel details"]

    for vid_data in mycol.find({},{'_id':0,'video_info':1}):
            for i in vid_data['video_info']:
                    Videos_data.append(i)
    df = st.dataframe(Videos_data)

def show_comment_details():
    Comment_data =[]
    mycol = db1["Channel details"]

    for Com_data in mycol.find({},{'_id':0,'comment_info':1}):
        for i in Com_data ['comment_info']:
            Comment_data.append(i)
    df = st.dataframe(Comment_data)

#STREAMLIT
st.set_page_config(
    page_title='YOUTUBE DATA HARVESTING AND WAREHOUSING PROJECT',
    layout="wide"
    )
  
st.title(':rainbow[YOUTUBE DATA HARVESTING AND WAREHOUSING]')

with st.sidebar:
     st.title(':blue[This application allows users to access and analyze data from multiple YouTube channels]')
     st.header('The application has the following features:')
     st.markdown('- Ability to input a YouTube channel ID and retrieve all the relevant data using Google API')
     st.markdown('- Option to store the data in a MongoDB database as a data lake')
     st.markdown('- Ability to collect data from YouTube channels and store them in the data lake by clicking a button')
     st.markdown('- Option to select a channel name and migrate its data from the data lake to a SQL database as tables')
     st.markdown('- Ability to search and retrieve data from the SQL database using different search options')

channel_id=st.text_input("Enter the channel ID: ")


if st.button("Click to fetch and store channel details"):

    channel_data=[]
    col1= db1["Channel details"]

    for cha_data in col1.find({},{'_id':0,'Channal_info':1}):
        channel_data.append(cha_data['Channal_info']['Channel_Id'])

    if channel_id in channel_data:
        st.error('Channel details already exists in the database')

    else:
        insert=Alldetails(channel_id)
        st.success(insert)

if st.button('Migrate the data to SQL'):
    table=table()
    st.success(table)


show_table = st.radio('Select the table to display',('Channels','Videos','Comments'), horizontal= True)

if show_table == 'Channels':
    show_channel_details()

if show_table == 'Videos':
    show_video_details()

if show_table == 'Comments':
    show_comment_details()

# SQL Connection to fetch query

db_1=psycopg2.connect(host='localhost',
                        user='postgres',
                        password='9867335172$Ss',
                        database='youtube',
                        port= '5432')

cursor = db_1.cursor()

questions=st.selectbox("Select your questions",
                       ('1. All the videos and their corresponding channels',
                        '2. Channels with the most number of videos',
                        '3. The top 10 most viewed videos',
                        '4. Comment count of each videos',
                        '5. Video with highest likes',
                        '6. Like count of each videos',
                        '7. Views count of each videos',
                        '8. The names of all the channels that have published videos in the year 2023',
                        '9. The average duration of all videos in each channel',
                        '10. Videos that have highest number of comments')) 

if questions == '1. All the videos and their corresponding channels':
    query1= '''SELECT  video_name, channel_name FROM videos'''
    cursor.execute(query1)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Video Name','Channel Name'])

    st.write(df)

elif questions == '2. Channels with the most number of videos':
    query2= '''SELECT channel_name,total_videos FROM channels 
               ORDER BY total_videos DESC'''
    
    cursor.execute(query2)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Channel Name','Total Videos'])

    st.write(df)

elif questions == '3. The top 10 most viewed videos':
    query3= '''SELECT channel_name, video_name,view_count FROM videos 
                ORDER BY view_count DESC 
                LIMIT 10'''
    
    cursor.execute(query3)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Channel Name','Video Name','Total Views'])

    st.write(df)

elif questions == '4. Comment count of each videos':
    query4= '''SELECT channel_name, video_name,comment_count FROM videos 
                ORDER BY comment_count desc'''
    
    cursor.execute(query4)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Channel Name','Video Name','Total Comment'])

    st.write(df)

elif questions == '5. Video with highest likes':
    query5= '''SELECT channel_name,video_name, like_count FROM videos
               ORDER BY like_count DESC
               LIMIT 10'''
    
    cursor.execute(query5)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Channel Name','Video Name','Total Likes'])

    st.write(df)

elif questions == '6. Like count of each videos':
    query6= '''SELECT video_name, like_count FROM videos
               ORDER BY like_count DESC'''
    
    cursor.execute(query6)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Video Name','Total Likes'])

    st.write(df)

elif questions == '7. Views count of each videos':
    query7= '''SELECT video_name, view_count FROM videos
               ORDER BY view_count DESC'''
    
    cursor.execute(query7)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Video Name','Total Views'])

    st.write(df)


elif questions == '8. The names of all the channels that have published videos in the year 2023':
    query8= '''SELECT channel_name,video_name,publishedat FROM videos 
                WHERE EXTRACT (YEAR FROM publishedat) = 2023 '''
    
    cursor.execute(query8)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Channel Name','Video Name','Published date'])

    st.write(df)

elif questions == '9. The average duration of all videos in each channel':
    query9= '''SELECT channel_name,AVG(duration) AS Average  FROM videos 
                GROUP BY channel_name
                ORDER BY Average DESC'''
    
    cursor.execute(query9)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Channel Name','Average Duration'])

    temp=[]

    for index,row in df.iterrows():
        name = row['Channel Name']
        Duration= (str(row['Average Duration']))
        temp.append(dict(Channel_name= name,Average_Duration= Duration))

    df_new=pd.DataFrame(temp)
    df_new.rename(columns={'Channel_name':'Channel Name','Average_Duration':'Average Duration'},inplace=True)

    st.write(df_new)

elif questions == '10. Videos that have highest number of comments':
    query10= '''SELECT video_name, comment_count FROM videos
                ORDER BY comment_count DESC
                LIMIT 10'''
    
    cursor.execute(query10)
    db_1.commit()

    table_1= cursor.fetchall()
    df=pd.DataFrame(table_1,columns=['Video Name','Total Comments'])

    st.write(df)

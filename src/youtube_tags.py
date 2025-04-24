import googleapiclient.discovery
import time
import os
import pandas as pd


def count_occurrences(input_list: list):
    export_dict = {
    'Keywords': [], 
    'Occurrences': []
    }

    for item in input_list:
        if item not in export_dict.get('Keywords'): # Add keyword to dictonary IF it does not already exist
            export_dict['Keywords'].append(item)
            export_dict['Occurrences'].append(1)
        elif item in export_dict.get('Keywords'): # Increase the number of occurrences IF the keyword already exists
            index_of_keyword = export_dict['Keywords'].index(item)
            export_dict['Occurrences'][index_of_keyword] += 1
     
    return export_dict

def save_dataframe_as(article_name: str, outgoing_dataframe: pd): # Create a unique username for collected data in the same directory as the script
    timestamp = time.strftime('%Y%m%d%H%M%S')
    file_name = article_name + '-' + timestamp + '.csv'
    directory_path = os.path.dirname(__file__)
    file_path = os.path.join(directory_path, file_name)

    try:
        pd.DataFrame(outgoing_dataframe).to_csv(file_path, index=False)
        print(f"File has been saved as: {file_path}")
    except Exception as e:
        print(f"An error occured when saving the data:\n {e}")

def main():
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "api_key"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)
    
    # Take in user Input
    user_query = str(input("Enter your YouTube search query: "))

    # Search for content based on user input
    search_request = youtube.search().list(
        part="snippet",
        maxResults=25,
        q=user_query
    )
    search_response = search_request.execute()

    # Grab videoIds from the API output and convert them to a string for the video request 
    video_ids = []

    search_response_items = search_response['items']
    for x in search_response_items:
        if x['id']['kind'] == 'youtube#video':
            video_ids.append(x['id']['videoId'])

    delimiter = ','
    video_ids_string = delimiter.join(video_ids)

    # Youtube Video information request
    video_request = youtube.videos().list(
        part="snippet",
        id=video_ids_string
    )
    video_response = video_request.execute()


    video_tags = [] # List to later add video tags to

    # Collect tags from searched videos
    video_request_items = video_response['items']
    for item in video_request_items:
        if 'tags' in item['snippet']:
            for tag in item['snippet']['tags']:
                video_tags.append(tag)

    tag_occurrences = count_occurrences(video_tags)
    outgoing_dataframe = pd.DataFrame(tag_occurrences)
    save_dataframe_as(user_query, outgoing_dataframe)
 

if __name__ == "__main__":
    main()
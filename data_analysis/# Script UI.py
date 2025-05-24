# Script UI


import googleapiclient.discovery
import tkinter as tk
import requests
import pandas as pd
import time
import os
from bs4 import BeautifulSoup

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

def clean_data(string_to_test: str): # Returns true if the input string does not match any words in the list of disqualifier keywords
    disqualifier_keywords = [
        'Add images or other media for use on Wikipedia',
        'Articles related to current events',
        'Category:',
        'Download this page as a PDF file',
        'Edit interlanguage links',
        'Edit section:',
        'Edit this at Wikidata',
        'File:',
        'Guides to browsing Wikipedia',
        'Guidance on how to use and edit Wikipedia',
        'Help:',
        'How to contact Wikipedia',
        'Information on how to cite this page',
        'Learn about Wikipedia and how it works',
        'Learn how to edit Wikipedia',
        'Geographic coordinate system',
        'More information about this page',
        'Portal:',
        'Permanent link to this revision of this page',
        'Special:',
        'You are encouraged to create an account and log in; however, it is not mandatory',
        'commons:',
        'foundation:',
        'Wikipedia:',
        'The hub for editors',
        'This is a featured article. Click here for more information.',
        'Template talk:',
        'Template:',
        '(identifier)',
        '[c]',
        '[e]',
        '[f]',
        '[g]',
        '[h]',
        '[j]',
        '[k]',
        '[n]',
        '[o]',
        '[p]',
        '[r]',
        '[t]',
        '[u]',
        '[x]',
        '[y]',
        '[z]',
    ]
    
    for keyword in disqualifier_keywords:
        if keyword in string_to_test:
            return False
    return True

def get_articles_in_subreddit(markup: str):
    soup = BeautifulSoup(markup, 'html.parser')
    list_of_articles = []

    content_table = soup.find_all('div')

    for div in content_table:
        if div.has_attr('data-fullname'):
            article = div['data-fullname']
            list_of_articles.append(article[3:])
    
    return list_of_articles

def get_authors_in_comments(markup: str):
    soup = BeautifulSoup(markup, 'html.parser')
    list_of_authors = []

    content_table = soup.find_all('div')

    for div in content_table:
        if div.has_attr('data-author'):
            list_of_authors.append(div['data-author'])
    
    return list_of_authors



def get_reddit_authors(subreddit: str):
    bearer_token = 'api_key'
    headers = {"Authorization": bearer_token, "User-Agent": "homework-data-collector (by /u/Intrepid_Mistake_305)"}

    list_of_all_authors = []
    
    search_response = requests.get(f"https://oauth.reddit.com/r/{subreddit}/best", headers=headers, params={"limit": "10"})
    list_of_articles = get_articles_in_subreddit(search_response.text)

    for article in list_of_articles:
        author_response = requests.get(f"https://oauth.reddit.com/r/{subreddit}/comments/{article}", headers=headers)
        new_author_list = get_authors_in_comments(author_response.text)
        list_of_all_authors.extend(new_author_list)

    author_occurrances = count_occurrences(list_of_all_authors)
    outgoing_dataframe = pd.DataFrame(author_occurrances)
    save_dataframe_as(subreddit, outgoing_dataframe)

def get_youtube_tags(user_query: str):
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "api_key"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)
    
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

def get_wikipedia_keywords(user_query: str):
    # Grab the HTML page of the specified website
    response = requests.get(user_query)
    response_as_html = response.text
    soup = BeautifulSoup(response_as_html, 'html.parser')

    # Collect contents of the title tag and remove ' - Wikipedia'
    title_of_page = soup.head.title.contents[0]
    title_proper = title_of_page[:-12]

    title_list = []

    main_wikipedia_article = soup.find('div', attrs={'id':'bodyContent'})

    for link in main_wikipedia_article.find_all('a'):
        link_title = link.get('title') # Get the text associated with a link

        if isinstance(link_title, str): # Remove empty variables
                
            if clean_data(link_title): # Remove text that is not related to the searched subject

                title_list.append(link_title)

    keyword_occurrences = count_occurrences(title_list)
    outgoing_dataframe = pd.DataFrame(keyword_occurrences)

    save_dataframe_as(title_proper, outgoing_dataframe)

def fetch_osint_news(keywords:str, languages="en", limit=5):
    """
    Fetch open-source news data from the Mediastack API.
    Filters by keyword and language.
    """
    api_key = "api_key"
    url = "http://api.mediastack.com/v1/news"
    params = {
        'access_key': api_key,
        'keywords': keywords,
        'languages': languages,
        'limit': limit,
    }

    output_text = ''

    print(f"Fetching news about '{keywords}'...\n")
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        articles = data.get('data', [])
        
        if not articles:
            output_text += "No news articles found.\n"
            return

        for i, article in enumerate(articles, start=1):
            output_text += f"--- Article {i} ---\n"
            output_text += f"Title       : {article.get('title')}\n"
            output_text += f"Source      : {article.get('source')}\n"
            output_text += f"Published At: {article.get('published_at')}\n"
            output_text += f"URL         : {article.get('url')}\n"
            output_text += f"Description : {article.get('description')}\n\n"

    else:
        output_text += "Failed to fetch news.\n"
        output_text += "Status Code:" + response.status_code
        output_text += "Response:" + response.text

    #print(output_text)

    timestamp = time.strftime('%Y%m%d%H%M%S')
    file_name = keywords + '-' + timestamp + '.txt'
    directory_path = os.path.dirname(__file__)
    file_path = os.path.join(directory_path, file_name)

    try:
        with open(file_path, 'x', encoding="utf-8") as f:
            f.write(output_text)
        print(f"File has been saved as: {file_path}")
    except Exception as e:
        print(f"An error occured when saving the data:\n {e}")


def run_selected_search(search_to_run: int, entry: tk.Entry):
    user_input = entry.get()

    match search_to_run:
        case 0:
            get_reddit_authors(user_input)
        case 1:
            get_youtube_tags(user_input)
        case 2:
            get_wikipedia_keywords(user_input)
        case 3:
            fetch_osint_news(user_input)

def update_gui(root: tk.Tk, button_pressed: int):
    root.geometry('800x400')

    l1_scripted_output = [
        'Enter the Subreddit you would like to scrape commenter names from: ', 
        'Enter the topic to search for associated tags on YouTube: ', 
        'Enter the Wikipedia URL you would like to scrape keywords from: ', 
        'Enter the topic you want to search for recent news articles on: ',
        ]

    l1 = tk.Label(root, text=l1_scripted_output[button_pressed])
    e1 = tk.Entry(root)
    b1 = tk.Button(root, text='Search!', background='grey', command=lambda s=button_pressed, e=e1: run_selected_search(s,e))
    f1 = tk.Label(root, text='Search results will be saved to the directory this script is located in.')

    l1.grid(row=0, column=2, sticky='s')
    e1.grid(row=1, column=2, sticky='new', padx=5)
    b1.grid(row=2, column=2)
    f1.grid(row=3, column=2, sticky='nsew')
    
    root.columnconfigure(2, weight=6)

def main():
    root = tk.Tk()
    root.geometry('400x400')

    b1 = tk.Button(root, text='Vocal Reddit Commentors', background='grey', command=lambda g=root, n=0: update_gui(g,n))
    b2 = tk.Button(root, text='YouTube Tag Association', background='white', command=lambda g=root, n=1: update_gui(g,n))
    b3 = tk.Button(root, text='Wikipedia Page Keywords', background='yellow', command=lambda g=root, n=2: update_gui(g,n))
    b4 = tk.Button(root, text='Recent Cybersecurity News', background='green', command=lambda g=root, n=3: update_gui(g,n))

    b1.grid(row=0, column=0, sticky='nsew', padx=5, pady=5, rowspan=2)
    b2.grid(row=0, column=1, sticky='nsew', padx=5, pady=5, rowspan=2)
    b3.grid(row=2, column=0, sticky='nsew', padx=5, pady=5, rowspan=2)
    b4.grid(row=2, column=1, sticky='nsew', padx=5, pady=5, rowspan=2)

    root.rowconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)
    root.rowconfigure(2, weight=1)
    root.rowconfigure(3, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    root.mainloop()

if __name__ == "__main__":
    main()
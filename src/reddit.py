# Reddit Script
# https://www.reddit.com/dev/api#POST_api_comment

import requests
import pandas as pd
import time
import os
from bs4 import BeautifulSoup

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

def main():
    bearer_token = 'api_key'
    headers = {"Authorization": bearer_token, "User-Agent": "homework-data-collector (by /u/Intrepid_Mistake_305)"}

    list_of_all_authors = []
    
    subreddit = str(input("Enter the Subreddit you would like to scrape keywords from: "))

    #region Search Query
    search_response = requests.get(f"https://oauth.reddit.com/r/{subreddit}/best", headers=headers, params={"limit": "10"})
    list_of_articles = get_articles_in_subreddit(search_response.text)
    #endregion

    #region Comment Authors
    for article in list_of_articles:
        author_response = requests.get(f"https://oauth.reddit.com/r/{subreddit}/comments/{article}", headers=headers)
        new_author_list = get_authors_in_comments(author_response.text)
        list_of_all_authors.extend(new_author_list)
    #endregion

    author_occurrances = count_occurrences(list_of_all_authors)
    outgoing_dataframe = pd.DataFrame(author_occurrances)
    save_dataframe_as(subreddit, outgoing_dataframe)

if __name__ == "__main__":
    main()
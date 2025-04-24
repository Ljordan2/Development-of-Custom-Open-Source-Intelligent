import requests
import pandas as pd
import os
import time
from bs4 import BeautifulSoup


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
    user_query = str(input("Enter the Wikipedia URL you would like to scrape keywords from: "))

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

if __name__ == "__main__":
    main()
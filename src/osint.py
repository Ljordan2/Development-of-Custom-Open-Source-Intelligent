import requests
import time
import os



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



if __name__ == "__main__":
    fetch_osint_news(keywords="Cybersecurity")
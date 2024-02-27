import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


def search_recipe(title):
    from urllib.parse import quote_plus
    search_url = f"https://www.bing.com/images/search?q={quote_plus(title)}"
    response = requests.get(search_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
    image_tag = soup.find('img', {'class': 'mimg'})  # This class name is hypothetical and likely incorrect
    if image_tag and 'src' in image_tag.attrs:
        return image_tag['src']
    return None

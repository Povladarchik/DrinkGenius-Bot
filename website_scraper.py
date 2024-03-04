import os
import requests
import sqlite3
from bs4 import BeautifulSoup

DATABASE_PATH = os.environ.get('DATABASE_PATH')
URL = "https://us.inshaker.com/cocktails?random_page=60"

def counter(func):
    def counter_wrapper(*args, **kwargs):
        counter_wrapper.count += 1
        print(f'Number of calls: {counter_wrapper.count}')
        return func(*args, **kwargs)
    counter_wrapper.count = 0
    return counter_wrapper


def fetch_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch content from {url}")


def extract_cocktail_details(soup):
    # Ingredients
    ingredients = []
    for ingredient in soup.find('table').find_all('tr')[1:]:
        name = ingredient.a.text.replace('\xa0', ' ')
        amount = ingredient.find(class_='amount').text
        unit = ingredient.find(class_='unit').text
        ingredients.append(f'• {name} {amount} {unit}')
    ingredients = '\n'.join(ingredients)

    # Recipe
    steps = [f"{i}) {step.text}" for i, step in enumerate(soup.find('ul', class_='steps').find_all('li'), start=1)]
    steps = '\n'.join(steps)

    # Attributes
    title = soup.find('h1', class_='common-name').text
    tags = soup.find('ul', class_='tags').find_all('li')
    degree, taste, base, category = [tag.text for tag in tags[:4]]

    # Images 
    div_tag = soup.find('div', class_='common-image-frame')
    image_url = "https://us.inshaker.com" + div_tag.get('lazy-bg')
    img_data = requests.get(image_url).content

    return img_data, title, ingredients, steps, degree, taste, base, category

@counter
def update_database(cursor, cocktail_details):
    cursor.execute('''INSERT INTO Cocktails (image, name, ingredients, recipe, degree, taste, base, category)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', cocktail_details)


def create_database():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Cocktails (
                      id INTEGER PRIMARY KEY,
                      image BLOB NOT NULL,
                      name TEXT NOT NULL,
                      ingredients TEXT NOT NULL,
                      recipe TEXT NOT NULL,
                      degree TEXT NOT NULL,
                      taste TEXT NOT NULL,
                      base TEXT NOT NULL,
                      category TEXT NOT NULL)''')

    connection.commit()
    connection.close()
    print('Database was created successfully!')


def main():
    create_database()

    page_content = fetch_page_content(URL)
    soup = BeautifulSoup(page_content, "html5lib")

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    for cocktail in soup.find_all('div', class_='cocktail-item'):
        link = cocktail.find('a').get('href')
        cocktail_url = 'https://us.inshaker.com' + link
        cocktail_page_content = fetch_page_content(cocktail_url)
        cocktail_soup = BeautifulSoup(cocktail_page_content, "html5lib")
        cocktail_details = extract_cocktail_details(cocktail_soup)
        update_database(cursor, cocktail_details)

    connection.commit()
    connection.close()
    print('Connection was closed')


if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import psycopg2
import os
import shutil
from zipfile import ZipFile
from datetime import datetime

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname="techcrunch_articles",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Create tables if they don't exist
cur.execute('''CREATE TABLE IF NOT EXISTS articles
             (id SERIAL PRIMARY KEY, title TEXT, author TEXT, keyword TEXT, content TEXT, date TIMESTAMP)''')

# Target website URL
url = 'https://techcrunch.com/'

# Get the main page of the website
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Extract necessary information from the main page
articles = soup.find_all('article')

# Store information in the PostgreSQL database
for article in articles:
    title = article.find('h3', class_='mini-view__item__title').text.strip()
    author = article.find('p', class_='fi-main-block__byline').text.strip()
    content = "not defined yet"
    date = datetime.now()

    # Insert data into the database (if not duplicate)
    cur.execute("SELECT * FROM articles WHERE title=%s AND author=%s AND content=%s", (title, author, content))
    if not cur.fetchone():
        cur.execute("INSERT INTO articles (title, author, content, date) VALUES (%s, %s, %s, %s)", (title, author, content, date))
        conn.commit()

# Create output folder and HTML report file
output_folder_name = f"techcrunch_{datetime.now().strftime('%Y-%m-%d')}"
os.makedirs(output_folder_name, exist_ok=True)

with open(os.path.join(output_folder_name, 'report.html'), 'w') as file:
    file.write("<html><body>")
    file.write("<h1>Articles from TechCrunch</h1>")
    cur.execute("SELECT * FROM articles")
    for row in cur.fetchall():
        file.write(f"<h2>{row[1]}</h2>")
        file.write(f"<p>Author: {row[2]}</p>")
        file.write(f"<p>{row[4]}</p>")
    file.write("</body></html>")

# Compress files
shutil.make_archive(output_folder_name, 'zip', output_folder_name)

# Display path to the compressed file
print("Output folder path:", os.path.abspath(output_folder_name + '.zip'))

# Close connection to the database
conn.close()

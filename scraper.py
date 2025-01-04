import requests
from bs4 import BeautifulSoup
import re
import json

def preprocess_and_parse_json(json_string):
    # Remove JavaScript-style comments (single-line and multi-line)
    json_string = re.sub(r'//.*?\n|/\*.*?\*/', '', json_string, flags=re.S)
    
    # Ensure proper URL formatting (fix malformed URLs)
    json_string = re.sub(r'https?:/{2,}', 'https://', json_string)  # Replace multiple slashes with 'https://'

    # Fix truncated fields with placeholders
    json_string = re.sub(r'"image-portrait":\s*"https:', r'"image-portrait": "https://placeholder.com/image.jpg",', json_string)
    json_string = re.sub(r'"image-landscape":\s*"https:', r'"image-landscape": "https://placeholder.com/image.jpg",', json_string)

    # Fix missing commas between fields
    json_string = re.sub(r'(":[^,]*?)(")', r'\1,\2', json_string)

    # Replace single quotes with double quotes for JSON compatibility
    json_string = re.sub(r"(?<!\\)'", '"', json_string)  # Handles only unescaped single quotes

    # Fix any unintended escape sequences
    json_string = json_string.replace("\\\\", "\\")

    try:
        # Parse the cleaned JSON string
        parsed_data = json.loads(json_string)
        return parsed_data
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        print("Problematic JSON snippet:", json_string[:500])  # Show the first 500 characters of the JSON
        return None


    
def fetch_yrc_movie_data():

    yrc_url = 'https://www.yrccinemas.com/' 

    try:
        # Fetch the HTML content of the page
        response = requests.get(yrc_url)
        response.raise_for_status()
        html_content = response.text

        # Parse the HTML content with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the <script> tag containing movie data
        script_tag = soup.find('script', string=re.compile(r'var theme ='))
        if not script_tag:
            print("No relevant <script> tag found.")
            return

        # Extract the JavaScript object from the script content
        script_content = script_tag.string
        movie_data_match = re.search(r"movieData\s*=\s*(\{.*?\});", script_content, re.DOTALL)
        if not movie_data_match:
            print("Movie data not found in the script tag.")
            return

        # Extract the JavaScript-style JSON string
        movie_data_js = movie_data_match.group(1)

        # Preprocess and parse the JSON string
        movie_data = preprocess_and_parse_json(movie_data_js)
        if not movie_data:
            return

        ## Convert JavaScript-style JSON to Python-compatible JSON
        #movie_data_json = re.sub(r"'", '"', movie_data_js)  # Replace single quotes with double quotes
        #print(movie_data_json)
        #movie_data = json.loads(movie_data_json)

        # Extract and print movie details
        for date, movies in movie_data.items():
            print(f"Date: {date}")
            for movie in movies:
                print("Title:", movie.get('title'))
                print("Release Date:", movie.get('releaseDate'))
                print("Duration:", movie.get('duration'))
                print("Rating:", movie.get('rating'))
                print("Director:", movie.get('director'))
                print("Actors:", movie.get('actors'))
                print("Times:")
                for time in movie.get('times', []):
                    print(f"  - Time: {time.get('time')}, Sold Out: {time.get('isSoldOut')}, Booking Link: {time.get('bookingLink')}")
                print("Portrait Image:", movie.get('image-portrait'))
                print("Landscape Image:", movie.get('image-landscape'))
                print("---")
    except requests.exceptions.RequestException as e:
        print("Error fetching the URL:", e)
    except json.JSONDecodeError as e:
        print("Error parsing JSON data:", e)

fetch_yrc_movie_data()
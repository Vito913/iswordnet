import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_soup(url: str) -> BeautifulSoup:
    """Get BeautifulSoup object with delay to prevent overloading"""
    time.sleep(1)  # 2 second delay between requests
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.content, 'html.parser')


def extract_dialect_words(soup: BeautifulSoup) -> dict[str, list[str]]:
    """Extract dialect variations from the table"""
    table = soup.find('table', class_='prikaz-rijeci')
    if not table:
        return {}
    
    # Get region names from headers
    headers = []
    for th in table.find_all('th'):
        link = th.find('a')
        headers.append(link.get('title') if link else '')
    
    # Extract words for each region
    words_by_region = {}
    for header, td in zip(headers, table.find('tbody').find_all('td')):
        # Get all text content, including spans
        cell_contents = td.contents
        words = []
        current_word = ""
        
        for content in cell_contents:
            if content.name == 'br':
                if current_word:
                    words.append(current_word.strip())
                    current_word = ""
            elif content.name == 'span':
                # For span elements, just get the text content
                current_word += content.get_text()
            else:
                # For regular text nodes
                current_word += str(content)
        
        # Add last word if exists
        if current_word:
            words.append(current_word.strip())
            
        # Clean up words
        words = [w for w in words if w and w != '-']  # Remove empty entries and dashes
        words_by_region[header] = words if words else ['']
        
    return words_by_region

def process_words(input_csv: str, output_csv: str):
    """Process words from input CSV and create dialect dictionary"""
    # Read input CSV
    df = pd.read_csv("./data/" + input_csv)
    
    # Initialize results dictionary
    results = []
    
    for _, row in df.iterrows():
        try:
            soup = get_soup(row['link'])
            dialect_words = extract_dialect_words(soup)
            
            # Create entry with Croatian word and dialect variations
            entry = {'croatian_word': row['word']}
            entry.update({k: '/'.join(v) for k, v in dialect_words.items()})
            results.append(entry)
            
            print(f"Processed: {row['word']}")
            
        except Exception as e:
            print(f"Error processing {row['word']}: {str(e)}")
    
    # Convert to DataFrame and save
    result_df = pd.DataFrame(results)
    result_df.to_csv("./data/" + output_csv, index = False, encoding = 'utf-8-sig')


if __name__ == '__main__':
    input_csv = 'istrian_words_20241208_202841.csv'
    output_csv = 'istrian_dialect_dictionary.csv'
    process_words(input_csv, output_csv)
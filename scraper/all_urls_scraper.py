import csv
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    return webdriver.Chrome(options=options)

def get_page(driver, url: str) -> None:
    time.sleep(1)
    driver.get(url)


def get_letter_links(driver) -> list[str]:
    try:
        letter_elements = driver.find_elements(By.CSS_SELECTOR, "p a[href*='/pretrazivanje/1/']")
        return [elem.get_attribute("href") for elem in letter_elements]
    except NoSuchElementException:
        return []
    

def get_words_from_page(driver) -> list[tuple[str, str]]:
    words = []
    try:
        results = driver.find_element(By.ID, "rezultati-pretrazivanja")
        word_elements = results.find_elements(By.TAG_NAME, "a")
        
        for element in word_elements:
            word_text = element.text.strip()
            word_link = element.get_attribute("href")
            if word_text and word_link:
                words.append((word_text, word_link))
    except NoSuchElementException:
        return words
    return words

def get_next_page(driver) -> str | None:
    try:
        next_link = driver.find_element(By.CSS_SELECTOR, "a[title='Sljedeca']")
        next_url = next_link.get_attribute("href")
        # Verify if next page URL is different from current
        if next_url == driver.current_url:
            return None
        return next_url
    except NoSuchElementException:
        return None

def scrape_letter(url: str, max_pages: int = 20) -> list[tuple[str, str]]:
    driver = setup_driver()
    all_words = []
    current_url = url
    visited_urls = set()
    page_count = 0
    
    try:
        while current_url and page_count < max_pages:
            if current_url in visited_urls:
                print(f"Already visited {current_url}, stopping")
                break
                
            print(f"Scraping {current_url}")
            visited_urls.add(current_url)
            get_page(driver, current_url)
            
            words = get_words_from_page(driver)
            all_words.extend(words)
            
            current_url = get_next_page(driver)
            page_count += 1
            
    finally:
        driver.quit()
        
    return all_words

def save_to_csv(words: list[tuple[str, str]], mode: str = 'a') -> None:
    """Save words to a single CSV file, appending by default"""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = data_dir / f"istrian_words_{timestamp}.csv"
    
    # Create file with headers if it doesn't exist
    if mode == 'w' or not filepath.exists():
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['word', 'link'])
    
    # Append words
    with open(filepath, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(words)

def scrape_all_letters() -> list[tuple[str, str]]:
    driver = setup_driver()
    all_words = []
    processed_letters = set()
    
    try:
        driver.get("https://www.istarski-rjecnik.com/pretrazivanje/1/A/")
        letter_links = get_letter_links(driver)
        
        for letter_url in letter_links:
            if letter_url in processed_letters:
                continue
            
            letter = letter_url.split('/')[-1]
            print(f"Processing letter {letter}")
            
            words = scrape_letter(letter_url)
            all_words.extend(words)
            
            # Save words after each letter
            save_to_csv(words)
            processed_letters.add(letter_url)
            
    finally:
        driver.quit()
        
    return all_words


if __name__ == '__main__':
    words = scrape_all_letters()
    print(f"Found {len(words)} words")
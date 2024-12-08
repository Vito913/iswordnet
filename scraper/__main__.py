from pathlib import Path
import logging
from all_urls_scraper import scrape_all_letters
from webpage_scraper import process_words

def setup_logging() -> None:
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )

def get_unprocessed_files() -> list[tuple[str, str]]:
    """Get pairs of (input_file, output_file) that need processing"""
    data_dir = Path("./data")
    data_dir.mkdir(exist_ok=True)
    
    # Get all CSV files
    input_files = [f for f in data_dir.glob("istrian_words_*.csv")]
    processed_files = set(f.stem for f in data_dir.glob("istrian_dialect_*.csv"))
    
    # For each input file, create output filename and check if needs processing
    unprocessed = []
    for input_file in input_files:
        output_file = f"istrian_dialect_{input_file.stem[14:]}.csv"
        if output_file not in processed_files:
            unprocessed.append((input_file.name, output_file))
    
    return unprocessed

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check for existing files
    unprocessed = get_unprocessed_files()
    
    # If no files exist, run initial scraper
    if not unprocessed:
        logger.info("No input files found. Running initial scraper...")
        scrape_all_letters()
        unprocessed = get_unprocessed_files()
    
    # Process each unprocessed file
    for input_file, output_file in unprocessed:
        try:
            logger.info(f"Processing {input_file} -> {output_file}")
            process_words(input_file, output_file)
            logger.info(f"Successfully processed {input_file}")
        except Exception as e:
            logger.error(f"Error processing {input_file}: {str(e)}")

if __name__ == '__main__':
    main()
"""
Author: Samuel Grigg
Last Updated: 12/30/2025

Datasets: https://data.transportation.gov/browse?sortBy=relevance&pageSize=20&category=Trucking+and+Motorcoaches&limitTo=datasets

Notes:


"""

# For reading the config file
import json
import sys
from pathlib import Path

# For logging errors
import logging

# For reading/writing to sheets
import gspread



"""
Gets the directory where the executable (or script) is located.
"""
def get_runtime_dir() -> Path:
    if getattr(sys, "frozen", False): # if it has been bundled into an exe
        return Path(sys.executable).parent # the config file lives next to the exe
    else: # otherwise when running in dev mode, the config is in the same directory
        return Path(__file__).parent


"""
Loads the config file as a dictionary
"""
def load_config(filename="config.json") -> dict:
    config_path = get_runtime_dir() / filename # gives the full path of the config file

    if not config_path.exists():
        raise FileNotFoundError(f"Missing config file: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


"""
Logs errors
"""
def setup_logging(log_name="run.log") -> None:
    log_path = get_runtime_dir() / log_name # gives the full path of the log file

    logging.basicConfig( # Sets the format of the log file
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s", # shows logging with the timestamp, logging level, and message
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"), # if you want to rewrite the file every time, add mode="w"
            logging.StreamHandler()  # shows output if run manually
        ]
    )


def main() -> None:
    # Set up error logging
    setup_logging()
    logging.info("Program started")

    # Read config.json
    config = load_config()
    logging.info("Config loaded successfully")

    # Read input from sheets (list of dot numbers)
    input_data = read_from_sheets(config)
    logging.info("Data read successfully")
    dot_numbers = [row["dot_number"] for row in input_data] # list of dot numbers

    # Feed dot number list to API and store data
    scraper_data = run_scraper(config, dot_numbers)
    logging.info("API called successfully")

    # Parse data for legibility and organization
    parsed_data = scraper_data

    # Write data back to sheets
    write_to_sheets(config, parsed_data)
    logging.info("Data written successfully")

    logging.info("Program finished successfully")


"""
Reads the contents of the google sheet and returns a list of dicts
where each dict is the contents of one row. Key/value pairs are the 
header/contents of the cell e.g. {"dot_number": 123, "name": "ACME INC"}
"""
def read_from_sheets(config) -> list[dict]:
    spreadsheet_id = config["spreadsheet_id"]
    sheet_name = config["sheet_name"]
    service_account_file = config["service_account_file"]

    gc = gspread.service_account(filename=service_account_file) # uses the service account to access the sheet
    sheet = gc.open_by_key(spreadsheet_id) # contains data for the whole sheet
    worksheet = sheet.worksheet(sheet_name) # contains data for the specified worksheet
    data = worksheet.get_all_records() # list of dicts containing the contents of the worksheet

    if not data: # Log a warning if the sheet is empty
        logging.warning("No rows found in sheet")

    return data


"""

"""
def run_scraper(config, dot_numbers) -> list[dict]:
    app_token = config["app_token"]
    return None


"""

"""
def write_to_sheets(config) -> None:
    spreadsheet_id = config["spreadsheet_id"]
    sheet_name = config["sheet_name"]
    return None


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error occurred") # shows the full traceback for the error
        print(f"ERROR: {e}") # Makes it visible if run manually
        sys.exit(1) # Tells Task Scheduler that it failed
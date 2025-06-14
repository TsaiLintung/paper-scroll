"""Module for fetching works from Crossref API for a given ISSN and date range."""

import time
import requests
import json
import os

DIR = "/Users/lttsai/Documents/GitHub/paper-scroll"

def fetch_crossref_journal_year(journal_issn, year):
    """
    Fetch all works from Crossref API for a given ISSN and year.

    Args:
        journal_issn (str): ISSN of the journal.
        year (int): Year for which to fetch works.
    
    Returns:
        list: List of works fetched from Crossref API.
    """

    items = []
    cursor = "*"
    batch_size = 200
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    while True:
        url = (
            f"https://api.crossref.org/journals/"
            f"{journal_issn}/works/"
            f"?filter=from-pub-date:{start_date},until-pub-date:{end_date}"
            f"&rows={batch_size}&cursor={cursor}"
        )
        resp = requests.get(url, timeout=100)
        data = resp.json()
        message = data.get("message", {})
        batch = message.get("items", [])
        items.extend(batch)
        next_cursor = message.get("next-cursor")
        if not next_cursor or not batch:
            break
        cursor = next_cursor
        time.sleep(1)  # be polite to the API
    return items

def fetch_crossref(journals, start_year, end_year):
    """Fetch works from Crossref API for a list of journals and a date range."""

    for journal in journals:
        for year in range(start_year, end_year + 1):    
            issn = journal["issn"]
            name = journal["name"]

            output_path = f"{DIR}/data/{name}-{year}.json"
            if os.path.exists(output_path):
                print(f"Data for Journal {journal['name']} in year {year} already exists. Skipping...")
                continue

            items = fetch_crossref_journal_year(issn, year)

            data = {
                "issn": issn,
                "name": name,
                "year": year,
                "items": items
            }
            
        
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Fetched {len(items)} items for Journal {name} in year {year}")

def update_journals(e = None):
    print("Updating journals...")
    with open(f"{DIR}/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    start_year = config["start_year"]
    end_year = config["end_year"]
    journals = config["journals"]
    fetch_crossref(journals, start_year, end_year)
    print("Journals updated.")
"""Module for fetching works from Crossref API for a given ISSN and date range."""

import time
import requests
import os
import json
import random

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
        resp = requests.get(url, timeout=10)
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
            items = fetch_crossref_journal_year(issn, year)

            data = {
                "issn": issn,
                "name": name,
                "year": year,
                "items": items
            }
            
            output_path = f"data/{name}-{year}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"Fetched {len(items)} items for Journal {name} in year {year}")

def fetch_openalex(doi):
    """Fetch metadata from OpenAlex API for a given DOI."""
    
    url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=tsaidondon@gmail.com"
    resp = requests.get(url, timeout=10)
    if resp.status_code == 200:
        return resp.json()
    else:
        print(f"Error fetching data for DOI {doi}: {resp.status_code}")
        return None

def print_random_paper():

    data_dir = "data"
    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
    if not files:
        print("No data files found. Please run fetch first.")
    else:
        file_path = os.path.join(data_dir, random.choice(files))
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
        if not items:
            print("No papers found in the selected file.")
        else:
            paper = random.choice(items)
            print_paper(paper)

def print_paper(pap):
    """Prints the title, DOI, and abstract of a paper."""

    doi = pap.get("DOI")
    paper = fetch_openalex(doi)
    if paper:
        title = paper.get("title", "No title available")

        print(f"Title: {title}")
        print(f"DOI: {doi}")

        abstract_inverted_index = paper.get("abstract_inverted_index", "")
        if abstract_inverted_index:
            words_positions = []
            for word, positions in abstract_inverted_index.items():
                for pos in positions:
                    words_positions.append((pos, word))
            words_positions.sort()
            # Join words in order of their positions
            abstract = " ".join(word for _, word in words_positions)
            print(f"Abstract: {abstract}\n")
    else:
        print("Paper metadata not found.")


if __name__ == "__main__":

    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    action = input("Enter 'fetch' to fetch data or 'read' to display a random paper: ").strip().lower()

    journals = config["journals"]
    start_year = config["start_year"]
    end_year = config["end_year"]

    if action == "fetch":
        fetch_crossref(journals, start_year, end_year)
    elif action == "read":
        while True:
            print_random_paper()
            user_input = input("Press Enter to see another paper, or 'q' to quit: ").strip().lower()
            if user_input == "q":
                break
    else:
        print("Invalid action. Please enter 'fetch' or 'read'.")
    

   

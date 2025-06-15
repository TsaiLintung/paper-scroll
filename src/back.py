"""Module for fetching works from Crossref API for a given ISSN and date range."""

import time
import json
import os
import random
import requests

DIR = "/Users/lttsai/Documents/GitHub/paper-scroll"

class Backend:
    """Backend class to handle fetching and processing of journal data from Crossref API."""
    def __init__(self, data_dir=DIR):
        self.data_dir = data_dir

    def _fetch_crossref_journal_year(self, journal_issn, year):
        """
        Fetch all works from Crossref API for a given ISSN and year.
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

    def _fetch_crossref(self, journals, start_year, end_year):
        """Fetch works from Crossref API for a list of journals and a date range."""
        for journal in journals:
            for year in range(start_year, end_year + 1):
                issn = journal["issn"]
                name = journal["name"]

                output_path = f"{self.data_dir}/data/{name}-{year}.json"
                if os.path.exists(output_path):
                    print(f"Data for Journal {name} in year {year} already exists. Skipping...")
                    continue

                items = self._fetch_crossref_journal_year(issn, year)

                data = {
                    "issn": issn,
                    "name": name,
                    "year": year,
                    "items": items
                }

                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                print(f"Fetched {len(items)} items for Journal {name} in year {year}")

    def update_journals(self):
        """Update journals by fetching data from Crossref API."""

        print("Updating journals...")
        with open(f"{self.data_dir}/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        start_year = config["start_year"]
        end_year = config["end_year"]
        journals = config["journals"]
        self._fetch_crossref(journals, start_year, end_year)
        print("Journals updated.")

    def get_random_doi(self):
        """Get a random DOI from the data directory."""
        
        files = [f for f in os.listdir(os.path.join(DIR, "data")) if f.endswith(".json")]
        file_path = os.path.join(os.path.join(DIR, "data"), random.choice(files))
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
        item = random.choice(items)
        return item.get("DOI")
    
    def fetch_openalex(self, doi):
        """Fetch metadata from OpenAlex API for a given DOI."""

        url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=tsaidondon@gmail.com"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Error fetching data for DOI {doi}: {resp.status_code}")
            self.data = {}
            return
        data = resp.json()

        # parse abstract from abstract_inverted_index
        abstract_inverted_index = data.get("abstract_inverted_index")
        if abstract_inverted_index:
            words_positions = []
            for word, positions in abstract_inverted_index.items():
                for pos in positions:
                    words_positions.append((pos, word))
            words_positions.sort()
            abstract = " ".join(word for _, word in words_positions)
        else:
            abstract = ""

        data["abstract"] = abstract
        return data
    
    def get_random_paper(self): 
        """Get a random paper with valid metadata."""
        
        valid = False
        while not valid:
            doi = self.get_random_doi()
            paper_data = self.fetch_openalex(doi)
            paper = Paper(doi, paper_data)
            valid = paper.valid
        return paper
    
class Paper:
    def __init__(self, doi, data):

        self.doi = doi
        self.data = data
        self.valid = bool(self.data.get("abstract")) and bool(self.data.get("authorships"))

    def get(self, key):
        return self.data.get(key, "Not Available")
   
    def get_subtitle(self):
        year = self.get("publication_year")
        journal = self.get("primary_location").get("source").get("display_name", "")
        authors = self.get("authorships")
        
        authors = ", ".join(author["author"]["display_name"] for author in authors)
        year_authors = f"{year} · {authors}" if year and authors else ""
        text = "\n".join(filter(None, [year_authors, journal]))
        return text

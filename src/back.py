"""Module for fetching works from Crossref API for a given ISSN and date range."""

import time
import json
import os
import random
import requests
import flet as ft

from paper import Paper

DEFAULT_CONFIG = {
    "start_year": 2021,
    "end_year": 2021,
    "text_size": 16,
    "journals": [
        {"name": "aer", "issn": "0002-8282"}
    ]
}
DEFAULT_PAPER = {"DOI": "10.1038/s41586-020-2649-2"}

class Backend:
    """Backend class to handle fetching and processing of journal data from Crossref API."""
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.starred_dir = os.path.join(self.data_dir, "starred")
        self.journal_dir = os.path.join(self.data_dir, "journals")
        self.config_path = os.path.join(self.data_dir, "config.json")
        self._handle_directories()

        # load configuration
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        self.config = config

        # load papers 
        self._load_papers()

        # UI components depending on backend state
        self.progress_bar = ft.ProgressBar(value=0, width=400, visible=False)
        self.message = ft.Text("")

    def _handle_directories(self):
        for path in [self.data_dir, self.starred_dir, self.journal_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

        if not os.path.exists(self.config_path):
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
            print(f"Created default config at {self.config_path}")

    def update_config(self, field, value):
        """Update a specific field in the configuration."""
        if field not in self.config:
            print(f"Field '{field}' not found in configuration.")
            return
        self.config[field] = value
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        print("Configuration saved.")

    def add_journal(self, name, issn):
        """Add a new journal to the configuration."""
  
        new_journal = {"name": name, "issn": issn}
        self.config["journals"].append(new_journal)
        self.update_config("journals", self.config["journals"])
        print(f"Added journal: {name} with ISSN: {issn}")

    def remove_journal(self, issn):
        """Remove a journal from the configuration by its ISSN."""
        journals = self.config["journals"]
        for journal in journals:
            if journal["issn"] == issn:
                journals.remove(journal)
                self.update_config("journals", journals)
                print(f"Removed journal with ISSN: {issn}")
                break
        self.update_config("journals", journals)

    def _load_papers(self):
        """Update the list of papers from the data directory."""
        self.papers = []
        for filename in os.listdir(self.journal_dir):
            file_path = os.path.join(self.journal_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.papers.extend(data.get("items", []))

        if self.papers == []:
            self.papers.append(DEFAULT_PAPER)

    # Fetching works from Crossref API ----------------------------
       
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
        self.message.value = "Fetching journals from Crossref API..."
        self.message.update()

        to_fetch = []
        for journal in journals:
            for year in range(start_year, end_year + 1):
                issn = journal["issn"]
                name = journal["name"]
                output_path = f"{self.journal_dir}/{name}-{year}.json"
                if os.path.exists(output_path):
                    continue
                else: 
                    to_fetch.append((journal, year, output_path))

        self.progress_bar.visible = True
        self.progress_bar.value = 0

        for journal, year, output_path in to_fetch:
            issn = journal["issn"]
            name = journal["name"]

            items = self._fetch_crossref_journal_year(issn, year)
            items = [{"DOI": item.get("DOI")} for item in items]

            data = {
                "issn": issn,
                "name": name,
                "year": year,
                "items": items
            }

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.progress_bar.value += 1 / len(to_fetch)
            self.progress_bar.update()
            mes = f"Fetched {len(items)} papers for journal '{name}' ({issn}) in {year}."
            print(mes)
            self.message.value = mes
            self.message.update()

        self.progress_bar.visible = False
        self.progress_bar.update()
        self.message.value = "All journals updated."
        self.message.update()

    def update_journals(self, e = None):
        """Update journals by fetching data from Crossref API."""

        print("Updating journals...")
        
        start_year = self.config["start_year"]
        end_year = self.config["end_year"]
        journals = self.config["journals"]

        # get the current indexed journal-years, remove onces not in config
        for filename in os.listdir(self.journal_dir):
            parts = filename.split("-")
            journal_name = "-".join(parts[:-1])
            year = parts[-1].replace(".json", "")
            file_path = os.path.join(self.journal_dir, filename)
            to_remove = journal_name not in [j["name"] for j in journals] or not year.isdigit() or not (start_year <= int(year) <= end_year)
            if to_remove :
                os.remove(file_path)
                print(f"Removed outdated journal data: {filename}")

        # add papers from the current config
        self._fetch_crossref(journals, start_year, end_year)
        self._load_papers()
        print("Journals updated.")

    # load papers ----------------------------
    
    def get_random_paper(self): 
        """Get a random paper with valid metadata."""

        valid = False
        while not valid:
            doi = random.choice(self.papers).get("DOI")
            url = f"https://api.openalex.org/works/https://doi.org/{doi}" # example: https://api.openalex.org/works/W2741809807
            resp = requests.get(url, timeout=10)
            if resp.status_code != 200:
                print(f"Error fetching data for DOI {doi}: {resp.status_code}")
                continue
            paper = Paper(resp.json(), self.starred_dir)
            valid = paper.valid

        return paper
    
    def get_starred_papers(self):

        starred_dois = []
        for filename in os.listdir(self.starred_dir):
            doi = filename.replace('.json', '').replace('_', '/')
            starred_dois.append(doi)

        starred_papers = []
        for doi in starred_dois:
            doi_filename = f"{doi.replace('/', '_')}.json"
            output_path = os.path.join(self.starred_dir, doi_filename)
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                starred_papers.append(Paper(data, self.starred_dir))
        return starred_papers
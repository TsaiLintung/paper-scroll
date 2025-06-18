"""Module for fetching works from Crossref API for a given ISSN and date range."""

import time
import json
import os
import random
import threading

import requests
import flet as ft

from src.paper import Paper


DEFAULT_CONFIG = {
    "start_year": 2021,
    "end_year": 2021,
    "text_size": 16,
    "email": "",
    "zotero_key": "",
    "zotero_id": "",
    "journals": [
        {"name": "aer", "issn": "0002-8282"}
    ]
}
DEFAULT_PAPER = {"DOI": "10.1038/s41586-020-2649-2"}

class Backend:
    """Backend class to handle fetching and processing of journal data from Crossref API."""
    def __init__(self, data_dir: str):
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
        self._load_indexed_papers()
        self._buffer_thread = None
        self._paper_buffer = []

        # UI components depending on backend state
        self.progress_bar = ft.ProgressBar(value=0, width=400, visible=False)
        self.message = ft.Text("")

        self.current_paper = None
        self.last_papers = []


    def _handle_directories(self):
        for path in [self.data_dir, self.starred_dir, self.journal_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

        if not os.path.exists(self.config_path):
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
            print(f"Created default config at {self.config_path}")

    # settings management ----------------------------

    def update_config(self, field: str, value):
        """Update a specific field in the configuration."""
        if field not in self.config:
            print(f"Field '{field}' not found in configuration.")
            return
        self.config[field] = value
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        print("Configuration saved.")

    def add_journal(self, name: str, issn: str):
        """Add a new journal to the configuration."""
  
        new_journal = {"name": name, "issn": issn}
        self.config["journals"].append(new_journal)
        self.update_config("journals", self.config["journals"])
        print(f"Added journal: {name} with ISSN: {issn}")

    def remove_journal(self, issn: str):
        """Remove a journal from the configuration by its ISSN."""
        journals = self.config["journals"]
        for journal in journals:
            if journal["issn"] == issn:
                journals.remove(journal)
                self.update_config("journals", journals)
                print(f"Removed journal with ISSN: {issn}")
                break
        self.update_config("journals", journals)

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
            time.sleep(0.5)  # be polite to the API
        return items

    def _fetch_crossref(self, journals, start_year, end_year):
        """Fetch works from Crossref API for a list of journals and a date range."""
        self.message.value = "Fetching journals from Crossref API..."
        self.message.update()

        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.progress_bar.update()

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
        self._load_indexed_papers()
        print("Journals updated.")

    # load papers ----------------------------

    def _load_indexed_papers(self):
        """Update the list of papers from the data directory."""
        self.papers = []
        for filename in os.listdir(self.journal_dir):
            file_path = os.path.join(self.journal_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.papers.extend(data.get("items", []))

        if self.papers == []:
            self.papers.append(DEFAULT_PAPER)

    def get_last_paper(self):
        """Get and pop the last paper from the last_papers list."""
        if not self.last_papers:
            return None
        paper = self.last_papers.pop()
        return paper
    
    def _load_random_paper(self):
        """Fetch a random paper with valid metadata from OpenAlex."""
        while True:
            doi = random.choice(self.papers).get("DOI")
            url = f"https://api.openalex.org/works/https://doi.org/{doi}" #https://api.openalex.org/works/W2741809807
            if self.config.get("email"):
                url += f"?mailto={self.config['email']}"
            try:
                resp = requests.get(url, timeout=100)
                time.sleep(1)  # be polite to the API
                if resp.status_code != 200:
                    print(f"Error fetching data for DOI {doi}: {resp.status_code}")
                    continue
                paper = Paper(resp.json())
                if paper.valid:
                    print(f"Fetched paper with DOI: {doi}")
                    return paper
            except Exception as e:
                print(f"Exception fetching paper: {e}")
                continue
            
    def _ensure_buffer(self):
        """Ensure the buffer has at least 5 papers asynchronously."""

        BUFFER_SIZE = 10
        def buffer_worker():
            while len(self._paper_buffer) < BUFFER_SIZE:
                paper = self._load_random_paper()
                self._paper_buffer.append(paper)
        if not self._buffer_thread or not self._buffer_thread.is_alive():
            self._buffer_thread = threading.Thread(target=buffer_worker, daemon=True)
            self._buffer_thread.start()

    def get_random_paper(self):
        """Get a random paper from buffer, then refill buffer asynchronously."""

        if not self._paper_buffer:
            paper = self._load_random_paper()
            self._paper_buffer.append(paper)    
        paper = self._paper_buffer.pop(0)
        self.last_papers.append(self.current_paper)
        self.current_paper = paper
        self._ensure_buffer() # Start async refill
        return paper
    
    # handle stars ----------------

    def get_paper_star_dir(self, paper: Paper):
        """Get the directory path for a starred paper."""
        doi = paper.get("doi").replace("https://doi.org/", "").replace("/", "_")
        return os.path.join(self.starred_dir, f"{doi}.json")
    
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
                starred_papers.append(Paper(data))
        return starred_papers
    
    def is_starred(self, paper: Paper):
        """Check if a paper is starred by checking if its file exists."""
        return os.path.exists(self.get_paper_star_dir(paper))
    
    def on_star_change(self, paper, new_status: bool):
        if new_status:
            self.star(paper)
        else:
            self.unstar(paper)
      
    def star(self, paper: Paper):
        """Star a paper by adding it to the history."""
        paper_dir = self.get_paper_star_dir(paper)
        if not self.is_starred(paper):
            with open(paper_dir, "w", encoding="utf-8") as f:
                json.dump(paper.data, f, ensure_ascii=False, indent=2)
            print(f"Starred paper with dir: {paper_dir}")
        else:
            print(f"Paper with dir: {paper_dir} is already starred.")

    def unstar(self, paper: Paper):
        """Unstar a paper by removing it from the history."""
        dir = self.get_paper_star_dir(paper)
        if self.is_starred(paper):
            os.remove(dir)
            print(f"Unstarred paper with dir: {dir}")
        else:
            print(f"Paper with DOI: {dir} is not starred.")

    # export to Zotero ----------------

    def export_paper_to_zotero(self, paper: Paper):

        library_id = self.config.get("zotero_id")
        api_key = self.config.get("zotero_key")

        if not library_id or not api_key:
            print("Zotero credentials missing.")
            return

        base_url = f"https://api.zotero.org/users/{library_id}/items"
        headers = {
            "Zotero-API-Key": api_key,
            "Content-Type": "application/json"
        }

        item = {
                "itemType": "journalArticle",
                "title": paper.get("title", ""),
                "abstractNote": paper.get("abstract", ""),
                "publicationTitle": paper.get("primary_location", {}).get("source", {}).get("display_name", ""),
                "volume": paper.get("biblio", {}).get("volume", ""),
                "issue": paper.get("biblio", {}).get("issue", ""),
                "pages": self._format_pages(paper),
                "date": paper.get("publication_date", ""),
                "journalAbbreviation": paper.get("primary_location", {}).get("source", {}).get("display_name", ""),
                "language": paper.get("language", ""),
                "DOI": paper.get("doi", "").replace("https://doi.org/", ""),
                "ISSN": self._get_issn(paper),
                "url": paper.get("primary_location", {}).get("landing_page_url", ""),
                "creators": self._extract_creators(paper),
                "tags": [],
                "collections": [],
                "relations": {}
            }

        try:
            response = requests.post(base_url, headers=headers, data=json.dumps([item]))
            if response.status_code == 200:
                key = response.json()["success"]["0"]
                print(f"Exported paper '{paper.get('title', '')}' to Zotero (key: {key})")
            else:
                print(f"Failed to export '{paper.get('title', '')}': {response.status_code} {response.text}")
        except Exception as ex:
            print(f"Error exporting '{paper.get('title', '')}': {ex}")

    def export_starred_to_zetero(self, e: ft.ControlEvent):
        for paper in self.get_starred_papers():
            self.export_paper_to_zotero(paper)

    def _format_pages(self, paper):
        first = paper.get("biblio", {}).get("first_page", "")
        last = paper.get("biblio", {}).get("last_page", "")
        if first and last:
            return f"{first}-{last}"
        return first or ""

    def _get_issn(self, paper):
        issns = paper.get("primary_location", {}).get("source", {}).get("issn", [])
        return issns[0] if issns else ""

    def _extract_creators(self, paper):
        creators = []
        for author in paper.get("authorships", []):
            name = author.get("author", {}).get("display_name", "")
            if name:
                parts = name.split(" ", 1)
                creators.append({
                    "creatorType": "author",
                    "firstName": parts[0],
                    "lastName": parts[1] if len(parts) > 1 else ""
                })
        return creators
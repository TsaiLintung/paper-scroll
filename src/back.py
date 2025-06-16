"""Module for fetching works from Crossref API for a given ISSN and date range."""

import time
import json
import os
import random
import requests

class Backend:
    """Backend class to handle fetching and processing of journal data from Crossref API."""
    def __init__(self, data_dir, config):
        self.data_dir = data_dir
        self.starred_dir = os.path.join(self.data_dir, "starred")
        self.config = config
        self._update_papers()

    def _update_papers(self):
        """Update the list of papers from the data directory."""
        self.papers = []
        data_dir = os.path.join(self.data_dir, "journals")
        for filename in os.listdir(data_dir):
            file_path = os.path.join(data_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.papers.extend(data.get("items", []))

        
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

                output_path = f"{self.data_dir}/journals/{name}-{year}.json"
                if os.path.exists(output_path):
                    print(f"Data for Journal {name} in year {year} already exists. Skipping...")
                    continue

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

                print(f"Fetched {len(items)} items for Journal {name} in year {year}")

    def update_journals(self, e = None):
        """Update journals by fetching data from Crossref API."""

        print("Updating journals...")
        
        start_year = self.config["start_year"]
        end_year = self.config["end_year"]
        journals = self.config["journals"]
        self._fetch_crossref(journals, start_year, end_year)
        self._update_papers()
        print("Journals updated.")

    def get_random_doi(self):
        """Get a random DOI from the data directory."""
        if self.papers == []:
            return "https://doi.org/10.7717/peerj.4375"  # Default DOI if no papers are available
        item = random.choice(self.papers)
        return item.get("DOI")
    
    def fetch_openalex(self, doi):
        """Fetch metadata from OpenAlex API for a given DOI."""
        # example: https://api.openalex.org/works/W2741809807

        url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=tsaidondon@gmail.com"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Error fetching data for DOI {doi}: {resp.status_code}")
            self.data = {}
            return
        return resp.json()
    
    def get_random_paper(self): 
        """Get a random paper with valid metadata."""

        valid = False
        while not valid:
            doi = self.get_random_doi()
            paper_data = self.fetch_openalex(doi)
            paper = Paper(paper_data, self.starred_dir)
            valid = paper.valid

        return paper
    
    def get_starred_dois(self):
        result = []
        for filename in os.listdir(self.starred_dir):
            doi = filename.replace('.json', '').replace('_', '/')
            result.append(doi)
        return result
    
    def get_starred_papers(self):
        starred_papers = []
        for doi in self.get_starred_dois():
            doi_filename = f"{doi.replace('/', '_')}.json"
            output_path = os.path.join(self.starred_dir, doi_filename)
            with open(output_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                starred_papers.append(Paper(data, self.starred_dir))
        return starred_papers
    
class Paper:
    def __init__(self, data, parent_dir):
        self.data = data
        self.doi = data.get("doi", "")
        self.data["abstract"] = self._get_abstract()
        self.data["subtitle"] = self._get_subtitle()
        self.valid = bool(self.data.get("abstract")) and bool(self.data.get("authorships"))

        doi_filename = f"{self.doi.replace('/', '_')}.json"
        self.dir = os.path.join(parent_dir, doi_filename)

    def get(self, key):
        return self.data.get(key, "Not Available")
    
    def is_starred(self):
        return os.path.exists(self.dir)
    
    def star(self):
        """Star a paper by adding it to the history."""
        doi = self.get("doi")
        if not self.is_starred():
            with open(self.dir, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Starred paper with DOI: {doi}")
        else:
            print(f"Paper with DOI: {doi} is already starred.")

    def unstar(self):
        """Unstar a paper by removing it from the history."""
        if self.is_starred():
            os.remove(self.dir)
            print(f"Unstarred paper with DOI: {self.doi}")
        else:
            print(f"Paper with DOI: {self.doi} is not starred.")
   
    def _get_subtitle(self):
        year = self.get("publication_year")
        journal = self.get("primary_location").get("source").get("display_name", "")
        authors = self.get("authorships")
        authors = ", ".join(author["author"]["display_name"] for author in authors)
        year_authors = f"{year} · {authors}" if year and authors else ""
        text = "\n".join(filter(None, [year_authors, journal]))
        return text

    def _get_abstract(self):
        abstract_inverted_index = self.data.get("abstract_inverted_index")
        if abstract_inverted_index:
            words_positions = []
            for word, positions in abstract_inverted_index.items():
                for pos in positions:
                    words_positions.append((pos, word))
            words_positions.sort()
            abstract = " ".join(word for _, word in words_positions)
        else:
            abstract = ""
        return abstract

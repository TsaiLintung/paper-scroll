import requests
import os
import json
import random

DIR = "/Users/lttsai/Documents/GitHub/paper-scroll"


class Paper:
    def __init__(self, doi=None):
        if doi: 
            self.doi = doi
        else:
            self.doi = self.get_random_doi()
        self.fetch_openalex()

    def fetch_openalex(self):
        doi = self.doi
        """Fetch metadata from OpenAlex API for a given DOI."""
        url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=tsaidondon@gmail.com"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Error fetching data for DOI {doi}: {resp.status_code}")
            self.data = {}
            return
        paper = resp.json()


        # parse abstract from abstract_inverted_index
        abstract_inverted_index = paper.get("abstract_inverted_index")
        if abstract_inverted_index:
            words_positions = []
            for word, positions in abstract_inverted_index.items():
                for pos in positions:
                    words_positions.append((pos, word))
            words_positions.sort()
            abstract = " ".join(word for _, word in words_positions)
        else:
            abstract = ""

        paper["abstract"] = abstract
        self.data = paper

        self.valid = bool(self.data.get("abstract")) and bool(self.data.get("authorships"))

    def get(self, key):
        return self.data.get(key, "Not Available")

    def get_random_doi(self):
        
        files = [f for f in os.listdir(os.path.join(DIR, "data")) if f.endswith(".json")]
        if not files:
            return None
        file_path = os.path.join(os.path.join(DIR, "data"), random.choice(files))
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", [])
        if not items:
            return None
        item = random.choice(items)
        return item.get("DOI")

    def get_subtitle(self):
        year = self.get("publication_year")
        journal = self.get("primary_location").get("source").get("display_name", "")
        authors = self.get("authorships")
        
        authors = ", ".join(author["author"]["display_name"] for author in authors)
        year_authors = f"{year} · {authors}" if year and authors else ""
        text = "\n".join(filter(None, [year_authors, journal]))
        return text

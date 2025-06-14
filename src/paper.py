import flet as ft

import requests
import os
import json
import random

class Paper:
    def __init__(self, doi=None):
        self.data = {}
        if doi:
            self.fetch_openalex(doi)
        else:
            random_doi = self.get_random_doi()
            if random_doi:
                self.fetch_openalex(random_doi)

    def fetch_openalex(self, doi):
        """Fetch metadata from OpenAlex API for a given DOI."""
        url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=tsaidondon@gmail.com"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"Error fetching data for DOI {doi}: {resp.status_code}")
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

    def get(self, key):
        return self.data.get(key, "Not Available")

    def get_random_doi(self):
        data_dir = "data"
        files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
        if not files:
            return None
        file_path = os.path.join(data_dir, random.choice(files))
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

class PaperDisplay(ft.Card):
    """
    A container for displaying paper information including title, DOI, and abstract.
    """

    def __init__(self):
        super().__init__()
        
        # setup displays
        self.title = ft.Text(value="", selectable=True, weight=ft.FontWeight.BOLD)
        self.link = ft.TextButton(
            text="",
            url="",
            style=ft.ButtonStyle(
                padding=10,
                bgcolor=None,
                color=ft.Colors.BLACK,
                overlay_color=None,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
            width=None,  # Let width shrink to fit text
            height=None,
            expand=False,
        )
        self.subtitle = ft.Text(value="", selectable=True)
        self.abstract = ft.Text(value="", selectable=True)
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        title=self.title,
                        subtitle=self.subtitle,
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    ft.Container(
                        content=self.abstract,
                        padding=ft.Padding(10, 10, 10, 10),
                    ),
                    self.link
                ],
                expand=True,
            ),
            padding=10,
            expand=True,
        )
        self.shadow_color = ft.Colors.ON_SURFACE_VARIANT

        # init 
        self.paper = Paper()

    def update_display(self):
        self.title.value = self.paper.get("title")
        doi = self.paper.get("doi")
        self.link.text = doi
        self.link.url = doi
        self.abstract.value = self.paper.get("abstract")
        self.subtitle.value = self.paper.get_subtitle()
        self.update()

    def update_random(self):
        self.paper = Paper()
        self.update_display()

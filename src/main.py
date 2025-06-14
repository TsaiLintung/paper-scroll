import os
import json
import random
import textwrap
import requests

import flet as ft

def fetch_openalex(doi):
    """Fetch metadata from OpenAlex API for a given DOI."""
    
    url = f"https://api.openalex.org/works/https://doi.org/{doi}?mailto=tsaidondon@gmail.com"
    resp = requests.get(url, timeout=10)
    if resp.status_code != 200:
        print(f"Error fetching data for DOI {doi}: {resp.status_code}")
        return None
    paper = resp.json()

    abstract_inverted_index = paper.get("abstract_inverted_index", "")
    if abstract_inverted_index:
        words_positions = []
        for word, positions in abstract_inverted_index.items():
            for pos in positions:
                words_positions.append((pos, word))
        words_positions.sort()
        abstract = " ".join(word for _, word in words_positions)

    linewidth = 80
    wrapper = textwrap.TextWrapper(width=linewidth)
    wrapped_abstract = wrapper.fill(text=abstract)
    paper["abstract"] = wrapped_abstract
    return paper
        

def get_random_doi():
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


def main(page: ft.Page):
    page.title = "paperscrool"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    title = ft.Text(value="", selectable=True, width=600)
    doi_text = ft.Text(value="", selectable=True, width=600)
    abstract = ft.Text(value="", selectable=True, width=600)

    def update_paper(e):
        doi = get_random_doi()
        paper = fetch_openalex(doi)
        if paper:
            title.value = paper.get("title", "No title available")
            doi_text.value = doi
            abstract.value = paper.get("abstract", "No abstract available")

        page.update()

    page.add(
        ft.Column([
            ft.IconButton(ft.Icons.ADD, on_click=update_paper),
            title, 
            doi_text, 
            abstract
        ])
    )

ft.app(main)

import flet as ft
from back import fetch_openalex, get_random_doi


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

import flet as ft
from back import fetch_openalex, get_random_doi

class PaperInfo(ft.Card):
    """
    A container for displaying paper information including title, DOI, and abstract.
    """

    def __init__(self):
        super().__init__()
        self.title = ft.Text(value="", selectable=True, weight=ft.FontWeight.BOLD)
        self.doi_text = ft.TextButton(
            text="",
            url="",
            style=ft.ButtonStyle(
                padding=0,
                bgcolor=None,
                color=ft.Colors.BLUE,
                overlay_color=ft.Colors.BLUE_100,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
        )
        self.abstract = ft.Text(value="", selectable=True)
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        title=self.title,
                        subtitle=self.doi_text,
                        bgcolor=ft.Colors.GREY_200,
                    ),
                    ft.Container(
                        content=self.abstract,
                        padding=ft.Padding(10, 10, 10, 10),
                    ),
                ],
                expand=True,
            ),
            padding=10,
            expand=True,
        )
        self.shadow_color = ft.Colors.ON_SURFACE_VARIANT

    def update_paper(self, paper):
        self.title.value = paper.get("title", "No title available")
        doi = paper.get("doi", "No DOI available")
        self.doi_text.text = doi
        self.doi_text.url = doi
        self.abstract.value = paper.get("abstract", "No abstract available")
        self.update()

def main(page: ft.Page):
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.START

    paper_info = PaperInfo()

    def update_paper(e):
        doi = get_random_doi()
        paper = fetch_openalex(doi)
        if paper:
            paper_info.update_paper(paper)

    page.add(
        ft.Column([
            ft.ElevatedButton(text="Paper", on_click=update_paper),
            paper_info
        ], expand=True)
    )

ft.app(main)

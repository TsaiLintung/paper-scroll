import flet as ft


class PaperDisplay(ft.Card):
    """
    A container for displaying paper information including title, DOI, and abstract.
    """

    def __init__(self, backend):
        super().__init__()

        self.backend = backend

        self.title = ft.Text(value="", selectable=True, weight=ft.FontWeight.BOLD)
        self.subtitle = ft.Text(value="", selectable=True, font_family="Noto Serif")
        self.abstract = ft.Text(
            value="",
            selectable=True,
            font_family="Noto Serif",
            max_lines=8,
            overflow=ft.TextOverflow.VISIBLE,
        )

        self.link = ft.IconButton(
            icon=ft.Icons.LINK,
            tooltip="Open DOI",
            url="",
            style=ft.ButtonStyle(
                bgcolor=None,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
            expand=False,
        )

        self.pdf = ft.IconButton(
            icon=ft.Icons.CLOSE,  # Default to a cross icon
            tooltip="Download PDF",
            url="",
            style=ft.ButtonStyle(
                bgcolor=None,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
            expand=False,
        )

        self.alex_link = ft.IconButton(
            icon=ft.Icons.WEB_STORIES,
            tooltip="Open OpenAlex",
            url="",
            style=ft.ButtonStyle(
                bgcolor=None,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
            expand=False,
        )

        self.star = ft.IconButton(
            icon=ft.Icons.STAR_BORDER,
            tooltip="Star this paper",
            style=ft.ButtonStyle(
                bgcolor=None,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
            expand=False,
            on_click=lambda e: self.backend.star_paper(self.paper),
        )

        bottom_row = [self.link, self.pdf, self.alex_link, self.star]

        self.content = ft.Container(
            content=ft.Column(
                [
                    self.title,
                    self.subtitle,
                    ft.Divider(),
                    self.abstract,
                    ft.Divider(),
                    ft.Row(bottom_row, alignment=ft.MainAxisAlignment.START),
                ]
            ),
            padding=20,
        )

    def update_random(self, e=None):
        paper = self.backend.get_random_paper()
        self.update_paper(paper)

    def update_paper(self, paper):
        """
        Update the display with new paper information.
        """
        self.paper = paper
        self.title.value = paper.get("display_name")
        self.link.url = self.paper.get("doi")
        self.alex_link.url = paper.get("id")
        self.abstract.value = paper.get("abstract")
        self.subtitle.value = paper.get("subtitle")

        if paper.get("open_access").get("is_oa", False):
            self.pdf.icon = ft.Icons.DOWNLOAD
            self.pdf.url = paper.get("open_access").get("oa_url", "")
        else:
            self.pdf.icon = ft.Icons.CLOSE
            self.pdf.url = ""

        self.update()

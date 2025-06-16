import flet as ft


class PaperDisplay(ft.Card):
    """
    A container for displaying paper information including title, DOI, and abstract.
    """

    def __init__(self, paper):
        super().__init__()

        self.paper = paper

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
            selected_icon=ft.Icons.STAR,
            selected=False,
            tooltip="Star this paper",
            style=ft.ButtonStyle(
                bgcolor=None,
                alignment=ft.Alignment(-1, 0),  # Left align
            ),
            expand=False,
            on_click=self._star
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

    def _star(self, e = None):
        if self.paper.is_starred():
            self.star.selected = False
            self.paper.unstar()
        else: 
            self.star.selected = True
            self.paper.star()
            
        self.update()

    def update_paper(self, paper = None):
        """
        Update the display with new paper information.
        """
        if paper is not None:
            self.paper = paper
        self.title.value = paper.get("display_name")
        self.link.url = self.paper.get("doi")
        self.alex_link.url = paper.get("id")
        self.abstract.value = paper.get("abstract")
        self.subtitle.value = paper.get("subtitle")

        self.star.selected = self.paper.is_starred()

        if paper.get("open_access").get("is_oa", False):
            self.pdf.icon = ft.Icons.DOWNLOAD
            self.pdf.url = paper.get("open_access").get("oa_url", "")
        else:
            self.pdf.icon = ft.Icons.CLOSE
            self.pdf.url = ""

        self.update()

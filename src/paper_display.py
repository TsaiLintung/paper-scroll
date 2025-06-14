import flet as ft
from paper import Paper

class PaperDisplay(ft.Card):
    """
    A container for displaying paper information including title, DOI, and abstract.
    """

    def __init__(self):
        super().__init__()
        
        # setup displays
        self.title = ft.Text(value="", selectable=True, weight=ft.FontWeight.BOLD)
        
        self.subtitle = ft.Text(value="", selectable=True, font_family = "Noto Serif")
        self.abstract = ft.Text(value="", selectable=True, font_family="Noto Serif", max_lines=8, overflow=ft.TextOverflow.VISIBLE)

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

        bottom_row = [self.link, self.pdf]
        
        self.content = ft.Container(
            content=ft.Column(
                [
                    self.title,
                    self.subtitle,
                    ft.Divider(),
                    self.abstract,
                    ft.Divider(),
                    ft.Row(
                        bottom_row,
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                expand=True,
            ),
            padding=20,
            expand=True,
        )

        # init 
        self.paper = Paper()

    def update_display(self):
        self.title.value = self.paper.get("title")
        doi = self.paper.get("doi")
        self.link.url = doi
        self.abstract.value = self.paper.get("abstract")
        self.subtitle.value = self.paper.get_subtitle()

        if self.paper.get("open_access").get("is_oa", False):
            self.pdf.icon = ft.Icons.DOWNLOAD
            self.pdf.url = self.paper.get("open_access").get("oa_url", "")
        else: 
            self.pdf.icon = ft.Icons.CLOSE
            self.pdf.url = ""

        self.update()

    def update_random(self, e = None):
        
        # Keep fetching random papers until we get one with a non-empty abstract
        while True:
            self.paper = Paper()

            if getattr(self.paper, "valid", False):
                break
            print(f"Invalid paper: {self.paper.get('title')}, retrying...")
        self.update_display()
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
        self.subtitle = ft.Text(value="", selectable=True, font_family = "Noto Serif")
        self.abstract = ft.Text(value="", selectable=True, font_family = "Noto Serif")
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        title=self.title,
                        subtitle=self.subtitle,
                    ),
                    ft.Divider(),
                    ft.Container(
                        content=self.abstract,
                        padding=ft.Padding(15, 0, 0, 15),
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            self.link,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                expand=True,
            ),
            padding=10,
            expand=True,
        )

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

    def update_random(self, e = None):
        
        # Keep fetching random papers until we get one with a non-empty abstract
        while True:
            self.paper = Paper()

            if self.paper.valid:
                break
            print("Invalid paper, fetching another...")
        self.update_display()

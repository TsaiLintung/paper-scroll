import flet as ft


class PaperDisplay(ft.Card):
    """
    A container for displaying paper information including title, DOI, and abstract.
    """

    def __init__(self, paper, condensed=False):
        super().__init__()

        self.paper = paper
        self.persistent = False

        self.title = ft.Text(value="", selectable=True, weight=ft.FontWeight.BOLD)
        self.subtitle = ft.Text(
            value="", selectable=True, font_family="Noto Serif", 
            max_lines=2)
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
            on_click=self._star,
        )

        # Condense button
        self.condensed = condensed
        self.condense_btn = ft.IconButton(
            icon=None,
            tooltip=None,
            on_click=self.toggle_condense,
            style=ft.ButtonStyle(
            bgcolor=None,
            alignment=ft.Alignment(-1, 0),
            ),
            expand=False
        )
        
        self.divider1 = ft.Divider()
        self.divider2 = ft.Divider()
        self.bottom_row = ft.Row(
            [self.link, self.pdf, self.alex_link],
            alignment=ft.MainAxisAlignment.START,
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Column([self.title, self.subtitle], expand=True),
                            ft.Row([self.star,self.condense_btn]),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),  # Align row content to the right
                    self.divider1,
                    self.abstract,
                    self.divider2,
                    self.bottom_row,
                ]
            ),
            padding=15,
        )

        if self.condensed:
            self._to_condensed()
        else:
            self._to_expanded()

    def _to_condensed(self):
        """
        Convert the display to a condensed view.
        """
        self.abstract.visible = False
        self.divider1.visible = False
        self.divider2.visible = False
        self.link.visible = False
        self.pdf.visible = False
        self.alex_link.visible = False
        self.condense_btn.icon = ft.Icons.UNFOLD_MORE
        self.condense_btn.tooltip = "Expand"

    def _to_expanded(self):
        """
        Convert the display to an expanded view.
        """
        self.abstract.visible = True
        self.divider1.visible = True
        self.divider2.visible = True
        self.link.visible = True
        self.pdf.visible = True
        self.alex_link.visible = True
        self.condense_btn.icon = ft.Icons.UNFOLD_LESS
        self.condense_btn.tooltip = "Condense"

    def toggle_condense(self, e=None):
        self.condensed = not self.condensed
        if self.condensed:
            self._to_condensed()
        else:
            self._to_expanded()
        self.update()

    def _star(self, e=None):
        if self.paper.is_starred():
            self.star.selected = False
            self.paper.unstar()
            if not self.persistent:
                self.visible = False
        else:
            self.star.selected = True
            self.paper.star()
            self.persistent = True  
        self.update()


    def update_paper(self, paper=None):
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


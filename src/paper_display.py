import flet as ft
from paper import Paper
from back import Backend


class PaperDisplay(ft.Card):
    def __init__(self, backend: Backend, paper: Paper, is_main: bool):
        super().__init__(
            elevation=4,
            color=ft.Colors.SURFACE,
            surface_tint_color=ft.Colors.SURFACE_TINT,
            margin=ft.margin.symmetric(horizontal=10, vertical=6),
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        self.backend = backend
        self.paper = paper
        self.is_main = is_main

        self.title = ft.Text(value="", selectable=True, weight=ft.FontWeight.BOLD)

        self.year_journal = ft.Text(
            value="",
            selectable=True,
            font_family="Noto Serif",
            size=14,
            color=ft.Colors.with_opacity(0.75, ft.Colors.ON_SURFACE),
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.authors = ft.Text(
            value="",
            selectable=True,
            font_family="Noto Serif",
            size=14,
            color=ft.Colors.with_opacity(0.75, ft.Colors.ON_SURFACE),
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.abstract = ft.Text(
            value="", selectable=True, font_family="Noto Serif", size=14, max_lines=8
        )

        icon_style = ft.ButtonStyle(
            padding=ft.padding.symmetric(horizontal=6),
            shape=ft.RoundedRectangleBorder(radius=8),
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
        )

        self.link = ft.IconButton(
            icon=ft.Icons.LINK,
            tooltip="Open DOI",
            url="",
            style=icon_style,
        )

        self.pdf = ft.IconButton(
            icon=ft.Icons.CLOUD_DOWNLOAD,
            tooltip="Download PDF",
            url="",
            style=icon_style,
        )

        self.alex_link = ft.IconButton(
            icon=ft.Icons.WEB_STORIES,
            tooltip="Open OpenAlex",
            url="",
            style=icon_style,
        )

        self.star = ft.IconButton(
            icon=ft.Icons.STAR_BORDER,
            selected_icon=ft.Icons.STAR,
            selected=False,
            tooltip="Star this paper",
            style=icon_style,
            on_click=self._star,
        )

        self.condensed = not is_main
        self.basic_buttons = [self.star]
        self.extended_buttons = [self.link, self.alex_link, self.pdf]

        self.bottom_row = ft.Row(
            controls=self.basic_buttons + self.extended_buttons,
            alignment=ft.MainAxisAlignment.START,
            # wrap=True,
            spacing=10,
        )

        self.divider1 = ft.Divider(height=10, color=ft.Colors.TRANSPARENT)
        self.divider2 = ft.Divider(height=10, color=ft.Colors.TRANSPARENT)

        self.title_column = ft.Column(
            [self.title, ft.Column([self.year_journal, self.authors], spacing=0)],
            spacing=5,
            expand=True,
        )
        self.title_row = ft.Row(
            [self.title_column], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.content = ft.Container(
            content=ft.Column(
                [
                    self.title_row,
                    self.abstract,
                    self.bottom_row,
                ],
                spacing=10,
            ),
            padding=15,
            on_click=self.toggle_condense,
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
        self.link.visible = False
        self.pdf.visible = False
        self.alex_link.visible = False

        self.bottom_row.controls = []
        self.title_row.controls = [self.star, self.title_column]

    def _to_expanded(self):
        """
        Convert the display to an expanded view.
        """
        self.abstract.visible = True
        self.link.visible = True
        self.pdf.visible = True
        self.alex_link.visible = True

        self.bottom_row.controls = self.basic_buttons + self.extended_buttons
        self.title_row.controls = [self.title_column]

    def toggle_condense(self, e=None):
        if self.is_main:
            return
        self.condensed = not self.condensed
        if self.condensed:
            self._to_condensed()
        else:
            self._to_expanded()
        self.update()

    def _star(self, e=None):
        if self.backend.is_starred(self.paper):
            self.star.selected = False
            self.backend.unstar(self.paper)
            if not self.is_main:
                self.visible = False
        else:
            self.star.selected = True
            self.backend.star(self.paper)
        self.update()

    def before_update(self):
        """
        Update the display with new paper information.
        """

        paper = self.paper
        self.title.value = paper.get("display_name")
        self.link.url = self.paper.get("doi")
        self.alex_link.url = paper.get("id")
        self.abstract.value = paper.get("abstract")
        self.year_journal.value = paper.get("year_journal")
        self.authors.value = paper.get("authors_joined")

        self.star.selected = self.backend.is_starred(self.paper)

        if paper.get("open_access").get("is_oa", False):
            self.pdf.icon = ft.Icons.DOWNLOAD
            self.pdf.url = paper.get("open_access").get("oa_url", "")
        else:
            self.pdf.icon = ft.Icons.CLOSE
            self.pdf.url = ""

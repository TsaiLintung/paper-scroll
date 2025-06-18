import flet as ft
from src.paper import Paper

class PaperDisplay(ft.Container):
    def __init__(self, paper: Paper, starred: bool, on_star_change=None):
        super().__init__(
            bgcolor=ft.Colors.SURFACE
        )

        self.on_star_change = on_star_change
        self.paper = paper

        self.title = ft.Text(value="", selectable=True, theme_style=ft.TextThemeStyle.TITLE_MEDIUM)

        self.year_journal = ft.Text(
            value="",
            selectable=True,
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self.authors = ft.Text(
            value="",
            selectable=True,
            theme_style=ft.TextThemeStyle.BODY_SMALL,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        self.abstract = ft.Text(
            value="", selectable=True, theme_style=ft.TextThemeStyle.BODY_MEDIUM
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
            selected=starred,
            tooltip="Star this paper",
            style=icon_style,
            on_click=self._star,
        )

        self.title_star = ft.IconButton(
            icon=ft.Icons.STAR_BORDER,
            selected_icon=ft.Icons.STAR,
            selected=starred,
            tooltip="Star this paper",
            style=icon_style,
            on_click=self._star,
        )

        self.condensed = False
        self.basic_buttons = [self.star]
        self.extended_buttons = [self.link, self.alex_link, self.pdf]

        self.bottom_row = ft.Row(
            controls=self.basic_buttons + self.extended_buttons,
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
        )

        self.title_column = ft.Column(
            [self.title, ft.Column([self.year_journal, self.authors], spacing=0)],
            spacing=5,
            expand=True,
        )

        
        self.title_row = ft.Row(
            [self.title_star, self.title_column], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.content = ft.Column(
            [
                self.title_row,
                self.abstract,
                self.bottom_row,
            ],
            spacing=10,
        )
        self.padding = 15
        self.on_click = self.toggle_condense

        if self.condensed:
            self.to_condensed()
        else:
            self.to_expanded()

    def to_condensed(self):
        """
        Convert the display to a condensed view.
        """
        self.title_star.visible = True
        self.bottom_row.visible = False
        self.abstract.visible = False
        

    def to_expanded(self):
        """
        Convert the display to an expanded view.
        """
        self.title_star.visible = False
        self.bottom_row.visible = True
        self.abstract.visible = True

    def toggle_condense(self, e=None):
        
        self.condensed = not self.condensed
        if self.condensed:
            self.to_condensed()
        else:
            self.to_expanded()
        self.update()

    def _star(self, e=None):
        new_status = not self.star.selected  # Toggle
        self.star.selected = new_status
        self.title_star.selected = new_status

        if self.on_star_change:
            self.on_star_change(self.paper, new_status)

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

        if paper.get("open_access").get("is_oa", False):
            self.pdf.icon = ft.Icons.DOWNLOAD
            self.pdf.url = paper.get("open_access").get("oa_url", "")
        else:
            self.pdf.icon = ft.Icons.CLOSE
            self.pdf.url = ""

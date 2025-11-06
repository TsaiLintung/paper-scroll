from .paper import Paper

import flet as ft


class PaperDisplay(ft.Container):
    def __init__(self, paper: Paper):
        super().__init__(
            bgcolor=ft.Colors.with_opacity(0.98, ft.Colors.SURFACE),
            padding=15,
            margin=ft.margin.symmetric(vertical=6),
            border_radius=ft.border_radius.all(12),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 4),
            ),
        )

        self.paper = paper

        self.title_link = ft.TextButton(
            text="",
            style=ft.ButtonStyle(
                padding=0,
                overlay_color=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
            ),
            url="",
        )
        self.title_link.content = ft.Text(
            value="",
            selectable=False,
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

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
            value="",
            selectable=True,
            theme_style=ft.TextThemeStyle.BODY_MEDIUM,
        )

        self.meta_column = ft.Column(
            [self.year_journal, self.authors], spacing=0, expand=True
        )

        self.title_column = ft.Column(
            [self.title_link, self.meta_column], spacing=5, expand=True
        )

        self.content = ft.Column(
            [self.title_column, self.abstract],
            spacing=10,
        )

    def before_update(self):
        paper = self.paper
        title = paper.get("display_name") or paper.get("title", "")
        doi = paper.get("doi") or ""
        self.title_link.content.value = title
        self.title_link.url = doi
        self.abstract.value = paper.get("abstract")
        self.year_journal.value = paper.get("year_journal")
        self.authors.value = paper.get("authors_joined")

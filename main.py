from frontend.paper_display import PaperDisplay
from frontend.api_client import ApiClient, BackendUnavailableError
from frontend.settings import Settings

from frontend.ui import MyDivider, PAGE_PADDING, MyTheme, FONTS

import time

import flet as ft


class ExploreView(ft.Container):
    def __init__(self, backend: ApiClient, settings: Settings):
        super().__init__()
        self.backend = backend
        self.settings = settings
        self.settings.expand = True
        self.settings.scroll = ft.ScrollMode.AUTO
        self.bgcolor = ft.Colors.TRANSPARENT
        self.current_index = 0
        self.is_loading = False
        self.expand = True

        self.paper_scroll = ft.Column(
            controls=[],
            on_scroll=self.on_paper_scroll,
            scroll=ft.ScrollMode.HIDDEN,
            on_scroll_interval=100,
        )
        self.paper_scroll.expand = True
        settings_header = ft.Row(
            controls=[
                ft.Text("Settings", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Close settings",
                    on_click=self.toggle_settings,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
        settings_body = ft.Container(
            content=self.settings,
            expand=True,
            padding=0,
            alignment=ft.alignment.top_left,
        )
        self.settings_container = ft.Container(
            content=ft.Column(
                controls=[
                    settings_header,
                    MyDivider(),
                    settings_body,
                ],
                spacing=12,
                expand=True,
            ),
            width=460,
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.border_radius.all(16),
        )
        self.settings_overlay = ft.Stack(
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                ),
                ft.Container(
                    content=self.settings_container,
                    alignment=ft.alignment.center,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=16, vertical=24),
                ),
            ],
            expand=True,
            visible=False,
        )
        self.paper_layer = ft.Container(
            content=self.paper_scroll,
            padding=PAGE_PADDING,
            expand=True,
        )
        self.content = ft.Stack(
            controls=[
                self.paper_layer,
                self.settings_overlay,
            ],
            expand=True,
        )
        self.padding = ft.padding.all(0)

        self.load_more_papers()

    def load_more_papers(self):
        error_displayed = False
        for _ in range(3):
            try:
                paper = self.backend.get_random_paper()
            except BackendUnavailableError as exc:
                if not error_displayed:
                    self._notify_backend_error(str(exc))
                    error_displayed = True
                break
            self.paper_scroll.controls.append(PaperDisplay(paper))
            self.paper_scroll.controls.append(MyDivider())
            self.current_index += 1
        if error_displayed and not self.paper_scroll.controls:
            self.paper_scroll.controls.append(
                ft.Text("Backend unavailable. Start the API server and retry.")
            )

    def refresh_papers(self):
        if self.is_loading:
            return
        self.is_loading = True
        self.paper_scroll.controls.clear()
        self.current_index = 0
        self.load_more_papers()
        self.paper_scroll.scroll_to(0, 0)
        if self.page:
            self.page.update()
        self.is_loading = False

    def on_paper_scroll(self, e: ft.ScrollEvent):
        if e.pixels >= e.max_scroll_extent - 100 and not self.is_loading:
            self.is_loading = True
            self.load_more_papers()
            if self.page:
                self.page.update()
            self.is_loading = False

    def _notify_backend_error(self, message: str):
        if self.page:
            snackbar = ft.SnackBar(ft.Text(message))
            self.page.snack_bar = snackbar
            snackbar.open = True
            self.page.update()
        else:
            print(message)

    def toggle_settings(self, _=None):
        self.settings_overlay.visible = not self.settings_overlay.visible
        if self.page:
            self.page.update()
        else:
            self.update()


def main(page: ft.Page):
    api_client = ApiClient()

    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.padding = 0
    page.fonts = FONTS
    page.theme = MyTheme(int(api_client.config.get("text_size", 16)))
    page.window.title_bar_hidden = True

    settings = Settings(api_client)
    explore_view = ExploreView(api_client, settings)

    def refresh_action(_):
        explore_view.refresh_papers()

    def settings_action(_):
        explore_view.toggle_settings()

    page.appbar = ft.AppBar(
        title=ft.Text("PAPERSCROLL", theme_style=ft.TextThemeStyle.TITLE_LARGE),
        center_title=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh papers",
                            on_click=refresh_action,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            tooltip="Toggle settings",
                            on_click=settings_action,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=4,
                ),
                padding=ft.padding.only(right=12),
            )
        ],
    )

    api_client.set_status_callback(settings.set_bk_status)
    if not api_client.available:
        settings.set_bk_status(("Backend unavailable. Start the API server.", 0.0))

    page.add(explore_view)

    print(f"Time to set up the page: {time.time() - start_time:.2f} seconds")


start_time = time.time()

ft.app(main, assets_dir="assets")

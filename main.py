from frontend.paper_display import PaperDisplay
from frontend.api_client import ApiClient, BackendUnavailableError
from frontend.settings import Settings

from frontend.ui import MyDivider, PAGE_PADDING, MyTheme, FONTS

import time

import flet as ft


class ExploreView(ft.Container):
    def __init__(self, backend: ApiClient):
        super().__init__()
        self.backend = backend
        self.bgcolor = ft.Colors.TRANSPARENT
        self.current_index = 0
        self.is_loading = False

        self.paper_scroll = ft.Column(
            controls=[],
            on_scroll=self.on_paper_scroll,
            scroll=ft.ScrollMode.HIDDEN,
            on_scroll_interval=100,
        )
        self.refresh_papers_button = ft.FloatingActionButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh papers",
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            on_click=lambda _: self.refresh_papers(),
        )
        self.content = ft.Stack(
            controls=[
                self.paper_scroll,
                ft.Container(
                    self.refresh_papers_button,
                    alignment=ft.alignment.bottom_right,
                    padding=20,
                    right=0,
                    bottom=0,
                    expand=True,
                ),
            ],
        )
        self.padding = PAGE_PADDING

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


def main(page: ft.Page):
    api_client = ApiClient()

    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = FONTS
    page.theme = MyTheme(int(api_client.config.get("text_size", 16)))
    page.window.title_bar_hidden = True

    explore_view = ExploreView(api_client)
    settings = Settings(api_client)
    settings_view = ft.Container(
        content=settings,
        alignment=ft.alignment.top_left,
        expand=True,
        padding=ft.padding.only(left=10, right=10, top=10, bottom=-5),
    )

    page.appbar = ft.AppBar(
        title=ft.Text("PAPERSCROLL", theme_style=ft.TextThemeStyle.TITLE_LARGE),
        center_title=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )

    main_content = ft.Container(content=None, expand=True, padding=-5)
    nav = ft.NavigationBar(
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.EXPLORE_OUTLINED,
                selected_icon=ft.Icons.EXPLORE,
                label="Explore",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ],
    )

    def route_change(_):
        route = page.route
        if route == "/settings":
            main_content.content = settings_view
            nav.selected_index = 1
        else:
            main_content.content = explore_view
            nav.selected_index = 0
        page.update()

    def nav_change(e: ft.ControlEvent):
        if e.control.selected_index == 1:
            page.go("/settings")
        else:
            page.go("/")

    page.on_route_change = route_change
    nav.on_change = nav_change

    api_client.set_status_callback(settings.set_bk_status)
    if not api_client.available:
        settings.set_bk_status(("Backend unavailable. Start the API server.", 0.0))

    page.add(main_content)
    page.add(nav)
    page.go("/")

    print(f"Time to set up the page: {time.time() - start_time:.2f} seconds")


start_time = time.time()

ft.app(main, assets_dir="assets")

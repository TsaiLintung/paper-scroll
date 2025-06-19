from src.paper_display import PaperDisplay
from src.back import Backend
from src.settings import Settings

from src.ui import MyDivider, PAGE_PADDING, MyTheme, FONTS

import os
import time

import flet as ft

class StaredPapers(ft.Column):

    def __init__(self, backend: Backend):
        super().__init__()
        self.backend = backend
        self.controls = []
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.expand = True
        self.scroll=ft.ScrollMode.ALWAYS

    # this is called when the page is loaded
    def before_update(self):

        self.controls = []
        starred_papers = self.backend.get_starred_papers()
        for paper in starred_papers:
            paper_display = PaperDisplay(paper, True, self.backend.on_star_change, self.backend.export_paper_to_zotero)
            paper_display.to_condensed()
            self.controls.append(paper_display)
            self.controls.append(MyDivider())

class ExploreView(ft.Container):

    def __init__(self, backend: Backend):
        super().__init__()
        self.bgcolor = ft.Colors.TRANSPARENT
        self.backend = backend

        self.current_index = 0
        self.paper_scroll = ft.Column(
            controls=[],
            on_scroll=self.on_paper_scroll, 
            scroll=ft.ScrollMode.HIDDEN,
            on_scroll_interval=100       
        )
        self.refresh_papers_button = ft.FloatingActionButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh papers",
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            on_click=lambda _: self.refresh_papers()
        )

        self.content = ft.Stack(
            controls=[
                self.paper_scroll, 
                ft.Container(self.refresh_papers_button, alignment = ft.alignment.bottom_right, padding = 20, right = 0, bottom = 0, expand = True)],
        )
        self.is_loading = False

        self.load_more_papers()
        self.padding = PAGE_PADDING

    def load_more_papers(self):
        """
        Load more papers when the user scrolls to the bottom.
        """
        for _ in range(3):
            paper = self.backend.get_random_paper()
            self.paper_scroll.controls.append(PaperDisplay(paper, False, self.backend.on_star_change, self.backend.export_paper_to_zotero))
            self.paper_scroll.controls.append(MyDivider())
            self.current_index += 1 

    def refresh_papers(self):
        """
        Refresh the paper list when user scrolls up hard.
        """
        self.is_loading = True
        self.paper_scroll.controls.clear()
        self.current_index = 0
        
        self.load_more_papers()
        self.paper_scroll.scroll_to(0, 0)  # Scroll to the top 
        self.page.update()
        self.is_loading = False

    def on_paper_scroll(self, e: ft.ScrollEvent):
        """
        Handle the scroll event to load more papers when the user scrolls to the bottom,
        and refresh when user scrolls up hard.
        """

        if e.pixels >= e.max_scroll_extent - 100:
            if not self.is_loading:
                self.is_loading = True
                self.load_more_papers()
                self.page.update()
                self.is_loading = False

 
class MyNavBar(ft.NavigationBar):

    def __init__(self, page):
        super().__init__(
            bgcolor = ft.Colors.SURFACE_CONTAINER_HIGHEST
        )
        self.page = page
        self.destinations = [
            ft.NavigationBarDestination(
                icon=ft.Icons.EXPLORE_OUTLINED,
                selected_icon=ft.Icons.EXPLORE,
                label="Explore",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.STAR_BORDER,
                selected_icon=ft.Icons.STAR,
                label="Starred",
                
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Settings",
            ),
        ]

        self.on_change = self._nav_change
        self.selected_index = 0

    def _nav_change(self, e: ft.ControlEvent):
        if e.control.selected_index == 0:
            self.page.go("/")
        elif e.control.selected_index == 1:
            self.page.go("/starred")
        elif e.control.selected_index == 2:
            self.page.go("/settings")

def main(page: ft.Page):

    data_dir = os.getenv("FLET_APP_STORAGE_DATA")

    def set_bk_status(status):
        """
        Set the backend status message.
        """
        settings.set_bk_status(status)
        page.update()

    bk = Backend(data_dir, set_bk_status)

    # Set up the page
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.fonts = FONTS
    page.theme = MyTheme(int(bk.config.get("text_size")))
    page.window.title_bar_hidden = True
    # Explore view ---------

    explore_view = ExploreView(bk)
    # Starred view ---------

    starred_papers_column = StaredPapers(bk)
    starred_view = ft.Container(
        content=starred_papers_column,
        alignment=ft.alignment.center, 
        padding=PAGE_PADDING,
    )

    # settings view
    settings = Settings(bk)
    settings_view = ft.Container(
        content=settings,
        alignment=ft.alignment.top_left,
        expand=True,
        padding = ft.padding.only(left=10, right=10, top=10, bottom=-5)
    )
   
    # App Bar ------------

    page.appbar = ft.AppBar(
        title=ft.Text("PAPERSCROLL", theme_style=ft.TextThemeStyle.TITLE_LARGE),
        center_title=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
    )

    # Navigation ---------

    main_content = ft.Container(content=None, expand=True, padding=-5)
    nav = MyNavBar(page)

    def route_change(e):
        route = page.route
        if route == "/":
            main_content.content = explore_view
            nav.selected_index = 0
        elif route == "/starred":
            main_content.content = starred_view
            nav.selected_index = 1
        elif route == "/settings":
            main_content.content = settings_view
            nav.selected_index = 2
        page.update()

    page.on_route_change = route_change

    page.add(main_content)
    page.add(nav)
    page.go("/")

    print(f"Time to set up the page: {time.time() - start_time:.2f} seconds")

start_time = time.time()

ft.app(main, assets_dir = "assets") #, 

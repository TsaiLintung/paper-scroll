from src.paper_display import PaperDisplay
from src.back import Backend
from src.settings import Settings

import os
import time

import flet as ft

PAGE_PADDING = ft.padding.only(left=10, right=10, top=10, bottom=10)

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
            paper_display = PaperDisplay(paper, True, self.backend.on_star_change)
            paper_display.to_condensed()
            self.controls.append(paper_display)

class ExploreView(ft.Container):

    def __init__(self, backend: Backend):
        super().__init__()
        self.backend = backend

        self.current_index = 0
        self.paper_scroll = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.HIDDEN, 
            on_scroll=self.on_paper_scroll, 
            on_scroll_interval = 100       
        )

        self.content = self.paper_scroll

        self.is_loading = False
        self.load_more_papers()
        self.padding = PAGE_PADDING

    def load_more_papers(self):
        """
        Load more papers when the user scrolls to the bottom.
        """
        for _ in range(3):
            paper = self.backend.get_random_paper()
            self.paper_scroll.controls.append(PaperDisplay(paper, False, self.backend.on_star_change))
            self.current_index += 1 
        
    def on_paper_scroll(self, e: ft.ScrollEvent):
        """
        Handle the scroll event to load more papers when the user scrolls to the bottom.
        """
        if e.pixels < e.max_scroll_extent - 100:
            return
        if self.is_loading:
            return
        self.is_loading = True
        self.load_more_papers()
        self.page.update() # don't let page spam updates
        self.is_loading = False

class MyNavBar(ft.NavigationBar):

    def __init__(self, page):
        super().__init__()
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
    bk = Backend(data_dir)

    # Set up the page
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#924046"
    page.theme = ft.Theme(
        font_family="Noto Sans",
        color_scheme_seed=ft.Colors.RED,
        use_material3=True,
        text_theme = ft.TextTheme(
            title_medium=ft.TextStyle(size=int(bk.config.get("text_size"))+2, color=ft.Colors.ON_SURFACE, weight=ft.FontWeight.BOLD, font_family="Noto Sans"),
            body_medium=ft.TextStyle(size=bk.config.get("text_size"), color=ft.Colors.ON_SURFACE, font_family="Noto Serif"), 
            body_small=ft.TextStyle(size=bk.config.get("text_size"), color=ft.Colors.with_opacity(0.75, ft.Colors.ON_SURFACE), font_family="Noto Serif"),
        )
    )
    # Explore view ---------

    explore_view = ExploreView(bk)
    # Starred view ---------
    
    zotero_button = ft.FloatingActionButton(
        icon=ft.Icons.ARCHIVE,
        tooltip="Export to Zotero",
        bgcolor=ft.Colors.SURFACE, 
        on_click=bk.export_starred_to_zetero
    )

    starred_papers_column = StaredPapers(bk)
    starred_view = ft.Container(
        content=ft.Stack([starred_papers_column, ft.Row([ft.Column([zotero_button], alignment=ft.MainAxisAlignment.END)], alignment=ft.MainAxisAlignment.END)]),
        alignment=ft.alignment.center, 
        padding=PAGE_PADDING,
    )

    # settings view
    settings = Settings(bk)
    settings_view =  ft.Container(
        content=settings,
        alignment=ft.alignment.center,
        expand=True,
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

ft.app(main) #, 

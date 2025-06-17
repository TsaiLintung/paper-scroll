
import os
import time

import flet as ft

from paper_display import PaperDisplay
from back import Backend
from settings import Settings

class StaredPapers(ft.Column):

    def __init__(self, backend: Backend):
        super().__init__()
        self.backend = backend
        self.controls = []
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.AUTO

    # this is called when the page is loaded
    def before_update(self):

        self.controls = []
        starred_papers = self.backend.get_starred_papers()
        for paper in starred_papers:
            self.controls.append(PaperDisplay(self.backend, paper, is_main=False))

class ExploreView(ft.Column):

    def __init__(self, backend: Backend):
        super().__init__()
        self.backend = backend

        refresh = ft.FloatingActionButton(
            icon=ft.Icons.REFRESH,
            tooltip="Get another random paper",
            on_click=self.get_new_paper,
            bgcolor=ft.Colors.SURFACE
        )

        self.last = ft.FloatingActionButton(
            icon=ft.Icons.CLOSE,
            tooltip="Back to last paper",
            on_click=self.back_to_last_paper,
            bgcolor=ft.Colors.SURFACE, 
            disabled=True
        )
        self.controls = [
            PaperDisplay(self.backend, self.backend.get_random_paper(), is_main=True),
            ft.Row([self.last, refresh], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ]
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def get_new_paper(self, e=None):
        self.controls[0] = PaperDisplay(self.backend, self.backend.get_random_paper(), is_main=True)
        self.last.icon = ft.Icons.ARROW_BACK
        self.last.disabled = False
        self.update()
        
    def back_to_last_paper(self, e=None):
        last_paper = self.backend.get_last_paper()
        if last_paper:
            self.controls[0] = PaperDisplay(self.backend, last_paper, is_main=True)
        else: 
            self.last.icon = ft.Icons.CLOSE
            self.last.disabled = True
        self.update()



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
            body_medium=ft.TextStyle(size=bk.config.get("text_size"), color =ft.Colors.BLACK),
        )
    )
    # Explore view ---------

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            if nav.selected_index == 0:
                explore_view.get_new_paper()
        page.update()

    page.on_keyboard_event = on_keyboard
    explore_view = ExploreView(bk)
    # Starred view ---------

    starred_papers_column = StaredPapers(bk)
    starred_view = ft.Container(
        content=starred_papers_column,
        alignment=ft.alignment.center,
        expand=True,
    )

    # settings view
    settings = Settings(bk)
    settings_view =  ft.Container(
        content=settings,
        alignment=ft.alignment.center,
        expand=True,
    )
   
    # Navigation ---------
    main_content = ft.Container(content=None, expand=True)
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

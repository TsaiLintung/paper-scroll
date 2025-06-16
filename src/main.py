import flet as ft
import os
from paper_display import PaperDisplay
from back import Backend
from settings import Settings

class StaredPapers(ft.Column):

    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.controls = []
        self.alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.scroll = ft.ScrollMode.AUTO

    def before_update(self):

        self.controls = []
        starred_papers = self.backend.get_starred_papers()
        for paper in starred_papers:
            self.controls.append(PaperDisplay(self.backend, condensed=True))
        for i, paper in enumerate(starred_papers):
            self.controls[i].update_paper(paper)

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

    def _nav_change(self, e):
        if e.control.selected_index == 0:
            self.page.go("/")
        elif e.control.selected_index == 1:
            self.page.go("/starred")
        elif e.control.selected_index == 2:
            self.page.go("/settings")


def main(page: ft.Page):

    # Set up the page
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#924046"
    page.theme = ft.Theme(
        font_family="Noto Sans",
        color_scheme_seed=ft.Colors.RED,
        use_material3=True,
    )

    # the single backend instance
    data_dir = os.getenv("FLET_APP_STORAGE_DATA")

    # create folders if not exists: ~/data/journals, ~/data/starred
    for folder in ["journals", "starred"]:
        path = os.path.join(data_dir, folder)
        if not os.path.exists(path):
            os.makedirs(path)

    bk = Backend(data_dir)

    # Explore view ---------

    def update_random_paper():
        paper = bk.get_random_paper()
        main_paper_display.update_paper(paper)
        page.update()

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            if nav.selected_index == 0:
                update_random_paper()
        page.update()

    page.on_keyboard_event = on_keyboard

    main_paper_display = PaperDisplay(bk)
    explore_view = ft.Column(
        [main_paper_display],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

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

    update_random_paper()

ft.app(main)

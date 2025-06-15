import flet as ft
import os
from paper_display import PaperDisplay
from back import Backend
import json


with open("config.json", "r") as f:
    CONFIG = json.load(f)

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
    app_dir = os.getenv("FLET_APP_STORAGE_DATA")
    bk = Backend(app_dir, CONFIG)

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            main_paper_display.update_random()
        page.update()
    page.on_keyboard_event = on_keyboard

    #
    main_paper_display = PaperDisplay(bk)
    explore_view = ft.Column(
                [
                    main_paper_display
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Function to update the history view when a new paper is starred
    history_papers_column = ft.Column(
        [
            ft.Text("Starred Papers", size=20),
            main_paper_display
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO,
    )
    history_view = ft.Container(
        content=history_papers_column,
        alignment=ft.alignment.center,
        expand=True,
    )
    
    def update_history_view():
        history_papers_column.controls = []
        for paper in bk.star_papers:
            history_papers_column.controls.append(PaperDisplay(bk))
        page.update()
        for i, paper in enumerate(bk.star_papers):
            history_papers_column.controls[i].update_paper(paper)
        page.update()
       


    # settings view
    update = ft.FloatingActionButton(icon=ft.Icons.UPDATE, on_click=bk.update_journals)
    settings_view = ft.Container(
        content=update,
        alignment=ft.alignment.center,
        expand=True,
    )

    # Main content container
    main_content = ft.Container(content=None, expand=True)

    # Navigation Bar

    def nav_change(e):
        if e.control.selected_index == 0:
            page.go("/")
        elif e.control.selected_index == 1:
            page.go("/history")
        elif e.control.selected_index == 2:
            page.go("/settings")

    navigation_bar = ft.NavigationBar(
        destinations=[
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
        ],
        on_change=nav_change,
        selected_index=0,
    )

    def route_change(e):
        route = page.route
        if route == "/":
            main_content.content = explore_view
            navigation_bar.selected_index = 0
        elif route == "/history":
            main_content.content = history_view
            navigation_bar.selected_index = 1
            update_history_view()
        elif route == "/settings":
            main_content.content = settings_view
            navigation_bar.selected_index = 2
        page.update()

    page.on_route_change = route_change

    page.add(main_content)
    page.add(navigation_bar)
    page.go("/")

    main_paper_display.update_random()


ft.app(main)

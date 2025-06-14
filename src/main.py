import flet as ft
import os
from paper_display import PaperDisplay
from back import Backend

CONFIG = {
    "start_year": 2023,
    "end_year": 2024,
    "journals": [
        {"name": "aer", "issn": "0002-8282"},
        {"name": "qje", "issn": "0033-5533"},
        {"name": "jpe", "issn": "0022-3808"},
        {"name": "restud", "issn": "0034-6527"},
        {"name": "ecma", "issn": "0012-9682"},
    ],
}


def main(page: ft.Page):
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#924046"
    page.window_width = 600

    app_dir = os.getenv("FLET_APP_STORAGE_DATA")

    

    page.theme = ft.Theme(
        font_family="Noto Sans",
        color_scheme_seed=ft.Colors.RED,
        use_material3=True,
    )

    # the single backend instance
    bk = Backend(app_dir, CONFIG)
    paper_display = PaperDisplay(bk)

    def update_random(e = None):
        paper = bk.get_random_paper()
        paper_display.update_paper(paper)

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            update_random()
        page.update()

    page.on_keyboard_event = on_keyboard

    def open_settings(e):
        # Placeholder for settings dialog
        pass

    def get_hisory(e):
        # Placeholder for history dialog
        pass

    sett = ft.FloatingActionButton(icon=ft.Icons.SETTINGS, on_click=open_settings)
    roll = ft.FloatingActionButton(icon=ft.Icons.ARROW_FORWARD, on_click=update_random)
    history = ft.FloatingActionButton(
        icon=ft.Icons.HISTORY,
        on_click=get_hisory)
    update = ft.FloatingActionButton(icon=ft.Icons.UPDATE, on_click=bk.update_journals)
    page.add(
        ft.Column(
            [
                paper_display,
                ft.Row(
                    [roll,update],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
            ]
        ),
    )
    page.add()

    # Load a paper at startup
    update_random()


ft.app(main)

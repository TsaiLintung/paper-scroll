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

    app_dir = os.getenv("FLET_APP_STORAGE_DATA")

    bk = Backend(app_dir, CONFIG)

    page.theme = ft.Theme(
        font_family="Noto Sans",
        color_scheme_seed=ft.Colors.RED,
        use_material3=True,
    )

    paper_display = PaperDisplay()

    def update_random():
        paper = bk.get_random_paper()
        paper_display.update_paper(paper)

    def on_keyboard(e: ft.KeyboardEvent): 
        if e.key == "Enter":
            update_random()
        if e.key == "U":
            bk.update_journals()
        page.update()

    page.on_keyboard_event = on_keyboard
    page.add(
        ft.Column(
            [
                paper_display
            ],
        )
    )

    # Load a paper at startup
    update_random()

ft.app(main)

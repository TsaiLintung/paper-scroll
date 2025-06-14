import flet as ft
from paper_display import PaperDisplay
from back import update_journals


def main(page: ft.Page):
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#924046"

    page.theme = ft.Theme(
        font_family="Noto Sans",
        color_scheme_seed=ft.Colors.RED,
        use_material3=True,
    )


    paper_info = PaperDisplay()

    def on_keyboard(e: ft.KeyboardEvent): 
        if e.key == "Enter":
            paper_info.update_random()
        if e.key == "U":
            update_journals()

    page.on_keyboard_event = on_keyboard
    page.add(
        ft.Column(
            [
                paper_info,
            ],
        )
    )

    # Load a paper at startup
    paper_info.update_random()

ft.app(main, assets_dir="asset")

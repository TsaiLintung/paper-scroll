import flet as ft
from paper_display import PaperDisplay
from back import Backend

# SET YOUR DATA DIRECTORY HERE
DIR = "/Users/lttsai/Documents/GitHub/paper-scroll"

def main(page: ft.Page):
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#924046"

    bk = Backend(DIR)

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

ft.app(main, assets_dir="asset")

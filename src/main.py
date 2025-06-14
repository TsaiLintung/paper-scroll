import flet as ft
from paper import PaperDisplay
from back import update_journals

def main(page: ft.Page):
    page.title = "paperscroll"
    page.vertical_alignment = ft.MainAxisAlignment.START

    paper_info = PaperDisplay()

    def update_paper(e=None):
        paper_info.update_random()

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            update_paper()

    page.on_keyboard_event = on_keyboard
    page.add(
        ft.Column([
            ft.Row([ft.ElevatedButton(text="Paper", on_click=update_paper),
                    ft.ElevatedButton(text="Update", on_click=update_journals)
                    ]),
            paper_info
        ], expand=True)
    )

ft.app(main)




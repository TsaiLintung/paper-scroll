import flet as ft


# Spacing scale shared across the app to keep visual rhythm consistent.
SPACE_XS = 4
SPACE_SM = 8
SPACE_MD = 12
SPACE_LG = 16
SPACE_XL = 24


class MyDivider(ft.Divider):
    """
    My custom divider class
    """
    def __init__(self):
        super().__init__(
            height=SPACE_LG,
            thickness=1,
            color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
        )
        
PAGE_PADDING = ft.padding.symmetric(horizontal=SPACE_XL, vertical=SPACE_LG)

FONTS = {
    "app title": "font/NotoSerif-Bold.ttf", 
    "title": "font/NotoSans-Bold.ttf", 
    "content": "font/NotoSerif-Regular.ttf"
}

class MyTheme(ft.Theme):
    """
    My custom theme class
    """
    def __init__(self, text_size: int):
        super().__init__(
            font_family="content",
            color_scheme_seed=ft.Colors.RED,
            use_material3=True,
            text_theme=ft.TextTheme(
                title_large=ft.TextStyle(size=text_size+4, color=ft.Colors.ON_SURFACE, font_family="app title", letter_spacing=1.5),
                title_medium=ft.TextStyle(size=text_size+2, color=ft.Colors.ON_SURFACE, font_family="title"),
                body_medium=ft.TextStyle(size=text_size, color=ft.Colors.ON_SURFACE, font_family="content"), 
                body_small=ft.TextStyle(size=text_size, color=ft.Colors.with_opacity(0.75, ft.Colors.ON_SURFACE), font_family="content"),
            )
        )

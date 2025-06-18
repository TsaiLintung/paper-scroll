import flet as ft
from src.back import Backend


class AddJournal(ft.Row): 
    def __init__(self, backend: Backend, call_submit_journal):
        super().__init__(wrap = True, spacing=12)

        self.backend = backend
        self.call_submit_journal = call_submit_journal

        self.journal_name_field = ft.TextField(
            label="Journal Name", value="", max_length=10, width = 150
        )

        self.issn_field = ft.TextField(
            label="ISSN", value="", max_length=9, width = 150
        )

        self.controls = [
            self.journal_name_field,
            self.issn_field,
            ft.TextButton(
                text="Add",
                tooltip="Add journal",
                on_click=self.self_submit_journal,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=8),
                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
                ),
            ),
        ]

    def self_submit_journal(self, e: ft.ControlEvent):
        journal_name = self.journal_name_field.value.strip()
        issn = self.issn_field.value.strip()

        if not issn or not issn.replace("-", "").isdigit() or len(issn) not in [8, 9]:
            self.issn_field.error_text = "Invalid"
            self.update()
            return
        if not journal_name:
            self.journal_name_field.error_text = "Can't be empty"
            self.update()
            return

        # Check if the journal already exists
        if issn in [j["issn"] for j in self.backend.config["journals"]]:
            self.issn_field.error_text = "Duplicated"
            self.update()
            return

        if journal_name in [j["name"] for j in self.backend.config["journals"]]:
            self.journal_name_field.error_text = "Duplicated"
            self.update()
            return

        e.control.error_text = None
        self.call_submit_journal(journal_name, issn)
   
        
class ConfigField(ft.TextField):
    def __init__(self, backend: Backend, field: str):
        super().__init__(
            label=field.replace("_", " ").title(),
            value=backend.config.get(field),
            width=200,
            on_submit=self.submit_field,
        )
        self.error_text = None
        self.field = field
        self.backend = backend
    
    def submit_field(self, e: ft.ControlEvent):
        self.backend.update_config(self.field, e.control.value)

class Settings(ft.Column):
    def __init__(self, backend: Backend):
        super().__init__()
        self.backend = backend

        update = ft.TextButton(
            text="Update",
            on_click=self.backend.update_journals,
            style=ft.ButtonStyle(
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
        )

        textfield_style = dict(width=150)

        # Year range fields
        start_year = ft.TextField(
            label="Start year",
            value=self.backend.config["start_year"],
            max_length=4,
            on_submit=lambda e: self.submit_year(e, "start_year"),
            **textfield_style,
        )
        end_year = ft.TextField(
            label="End year",
            value=self.backend.config["end_year"],
            max_length=4,
            on_submit=lambda e: self.submit_year(e, "end_year"),
            **textfield_style,
        )
        year_range = ft.Row(
            [start_year, end_year], wrap=True, spacing=12
        )

        # Add journal fields
        
        add_journal = AddJournal(backend, self.submit_journal)

        self.journals_row = ft.Row(self.get_journal_chip_row(), wrap=True, spacing=8)

        card_style = dict(
            elevation=2,
            color=ft.Colors.SURFACE,
            surface_tint_color=ft.Colors.SURFACE_TINT,
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        text_fields = ["text_size", "email", "zotero_id", "zotero_key"]
        text_fields_row = []
        for field in text_fields:
            text_fields_row.append(
                ConfigField(
                    backend=self.backend,
                    field=field
                )
            )

        self.other_fields = ft.Row(
            text_fields_row,
            wrap=True
        )

        self.controls = [
            ft.Card(
                **card_style,
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Papers", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
                            year_range,
                            add_journal,
                            self.journals_row,
                            ft.Row(
                                [
                                    update,
                                    ft.Column(
                                        [
                                            self.backend.message,
                                            self.backend.progress_bar,
                                        ]
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                        spacing=16,
                    ),
                ),
            ),
            ft.Card(
                **card_style,
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        [
                            ft.Row([ft.Text("Other", theme_style=ft.TextThemeStyle.TITLE_MEDIUM)], alignment=ft.MainAxisAlignment.START), 
                            self.other_fields
                        ], 
                        spacing=16
                    )
                ),
            ),
        ]

        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20

    def submit_journal(self, journal_name: str, issn: str):
        self.backend.add_journal(journal_name, issn)
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

    def get_journal_chip_row(self):

        journal_chips = []
        for journal in self.backend.config["journals"]:
            journal_chips.append(
                ft.Chip(
                    label=ft.Text(journal.get("name") + ": " + journal.get("issn")),
                    on_delete=lambda e: self.remove_journal(
                        journal.get("issn")
                    ),  # remove journal
                )
            )
        return journal_chips

    def submit_year(self, e: ft.ControlEvent, field: str):
        if not (e.control.value.isdigit() and 1000 <= int(e.control.value) <= 9999):
            e.control.error_text = "Enter a valid year"
            self.update()
            return
        e.control.error_text = None
        self.update()
        e.control.value = int(e.control.value)  # ensure integer format
        self.backend.update_config(field, e.control.value)

    

    def remove_journal(self, issn: str):
        self.backend.remove_journal(issn)
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

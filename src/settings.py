import flet as ft
from back import Backend


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
        journal_name_field = ft.TextField(
            label="Journal Name", value="", max_length=10, **textfield_style
        )
        issn_field = ft.TextField(
            label="ISSN", value="", max_length=9, **textfield_style
        )
        add_journal = ft.Row(
            [
                journal_name_field,
                issn_field,
                ft.TextButton(
                    text="Add",
                    tooltip="Add journal",
                    on_click=self.submit_journal,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.ON_SURFACE),
                    ),
                ),
            ],
            wrap=True,
            spacing=12,
        )

        self.journals_row = ft.Row(self.get_journal_chip_row(), wrap=True, spacing=8)

        card_style = dict(
            elevation=2,
            color=ft.Colors.SURFACE,
            surface_tint_color=ft.Colors.SURFACE_TINT,
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        self.controls = [
            ft.Card(
                **card_style,
                content=ft.Container(
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text("Papers", weight=ft.FontWeight.BOLD, size=16),
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
                        controls=[
                            ft.Text("Other", weight=ft.FontWeight.BOLD, size=16),
                            ft.TextField(
                                label="Font size",
                                value=self.backend.config.get("text_size"),
                                max_length=2,
                                width=150,
                                on_submit=lambda e: self.backend.update_config(
                                    "text_size", e.control.value
                                ),
                            ),
                            ft.TextField(
                                label="Email",
                                value=self.backend.config.get("email"),
                                on_submit=lambda e: self.backend.update_config(
                                    "email", e.control.value
                                ),
                            ),
                        ],
                        spacing=16,
                    ),
                ),
            ),
        ]

        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20

    def get_journal_chip_row(self):

        journal_chips = []
        for journal in self.backend.config["journals"]:
            journal_chips.append(
                ft.Chip(
                    label=ft.Text(journal.get("issn")),
                    leading=ft.Text(journal.get("name")),
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

    def submit_journal(self, e: ft.ControlEvent):
        journal_name = e.control.parent.controls[1].value.strip()
        issn = e.control.parent.controls[2].value.strip()

        if not issn or not issn.replace("-", "").isdigit() or len(issn) not in [8, 9]:
            e.control.parent.controls[2].error_text = "Invalid"
            self.update()
            return
        if not journal_name:
            e.control.parent.controls[1].error_text = "Can't be empty"
            self.update()
            return

        # Check if the journal already exists
        if issn in [j["issn"] for j in self.backend.config["journals"]]:
            e.control.parent.controls[2].error_text = "Duplicated"
            self.update()
            return

        if journal_name in [j["name"] for j in self.backend.config["journals"]]:
            e.control.parent.controls[1].error_text = "Duplicated"
            self.update()
            return

        e.control.error_text = None
        self.backend.add_journal(journal_name, issn)
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

    def remove_journal(self, issn: str):
        self.backend.remove_journal(issn)
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

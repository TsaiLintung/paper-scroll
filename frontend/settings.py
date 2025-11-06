from .api_client import ApiClient, BackendUnavailableError
from .ui import MyDivider

import flet as ft

class AddJournal(ft.Row):
    def __init__(self, backend: ApiClient, call_submit_journal):
        super().__init__(wrap=True, spacing=12)

        self.backend = backend
        self.call_submit_journal = call_submit_journal

        self.journal_name_field = ft.TextField(
            label="Journal Name", value="", max_length=10, width=150
        )

        self.issn_field = ft.TextField(label="ISSN", value="", max_length=9, width=150)

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
    def __init__(self, backend: ApiClient, field: str):
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
        try:
            self.backend.update_config(self.field, e.control.value)
        except BackendUnavailableError as exc:
            self.error_text = str(exc)
            self.update()


class Settings(ft.Column):
    def __init__(self, backend: ApiClient):
        super().__init__(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=15,
            scroll=ft.ScrollMode.AUTO
        )

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
        year_range = ft.Row([start_year, end_year], wrap=True, spacing=12)

        # Add journal fields

        add_journal = AddJournal(backend, self.submit_journal)

        self.journals_row = ft.Row(self.get_journal_chip_row(), wrap=True, spacing=8)

        text_fields = ["text_size", "email", "zotero_id", "zotero_key"]
        text_fields_row = []
        for field in text_fields:
            text_fields_row.append(ConfigField(backend=self.backend, field=field))

        self.other_fields = ft.Row(text_fields_row, wrap=True)

        # Message from backend 

        self.backend_status = ft.Column(
            [
                ft.Text("Pending."),
                ft.ProgressBar(value=0)
            ], 
            visible=True, 
            expand=True
        )

        # Assembling the settings controls

        self.controls = [
            ft.Text("Papers", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            year_range,
            add_journal,
            self.journals_row,
            ft.Row(
                [
                    update,
                    self.backend_status
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            MyDivider(),
            ft.Text("Other", theme_style=ft.TextThemeStyle.TITLE_MEDIUM),
            self.other_fields,
        ]

    def submit_journal(self, journal_name: str, issn: str):
        try:
            self.backend.add_journal(journal_name, issn)
        except BackendUnavailableError as exc:
            self._notify_backend_error(str(exc))
            return
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
        try:
            self.backend.update_config(field, e.control.value)
        except BackendUnavailableError as exc:
            e.control.error_text = str(exc)
            self.update()

    def remove_journal(self, issn: str):
        try:
            self.backend.remove_journal(issn)
        except BackendUnavailableError as exc:
            self._notify_backend_error(str(exc))
            return
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

    def set_bk_status(self, status): 
        """
        Change the UI corresponding to the backend status.
        """
        self.backend_status.controls[0].value = status[0]
        self.backend_status.controls[1].value = status[1]
        self.update()
        if self.page:
            self.page.update()

    def _notify_backend_error(self, message: str):
        self.backend_status.controls[0].value = message
        self.backend_status.controls[1].value = 0
        self.update()
        if self.page:
            snackbar = ft.SnackBar(ft.Text(message))
            self.page.snack_bar = snackbar
            snackbar.open = True
            self.page.update()

import flet as ft


class Settings(ft.Column):

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

        update = ft.TextButton(text="Update", on_click=self.backend.update_journals)

        # set year range
        start_year = ft.TextField(
            label="Start year",
            value=self.backend.config["start_year"],
            max_length=4,
            width=150,
            on_submit=lambda e: self.submit_year(e, "start_year"),
        )
        end_year = ft.TextField(
            label="End year",
            value=self.backend.config["end_year"],
            max_length=4,
            width=150,
            on_submit=lambda e: self.submit_year(e, "end_year"),
        )
        year_range = ft.Row([start_year, end_year], wrap=True)

        # add journal
        journal_name_field = ft.TextField(
            label="Journal Name", value="", max_length=10, width=150
        )
        issn_field = ft.TextField(label="ISSN", value="", max_length=9, width=150)
        add_journal = ft.Row(
            [
                journal_name_field,
                issn_field,
                ft.IconButton(icon=ft.Icons.ADD, on_click=self.submit_journal),
            ],
            wrap=True,
        )

        # the row for displaying journals

        self.journals_row = ft.Row(self.get_journal_chip_row(), wrap=True)

        self.controls = [
            ft.Card(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text("Years", weight=ft.FontWeight.BOLD),
                            year_range,
                            ft.Divider(),
                            ft.Text("Journals", weight=ft.FontWeight.BOLD),
                            self.journals_row,
                            add_journal,
                            ft.Divider(),
                            self.backend.message,
                            self.backend.progress_bar
                        ]
                    ),
                    padding=15,
                )
            )
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

    def submit_year(self, e, field):
        if not (e.control.value.isdigit() and 1000 <= int(e.control.value) <= 9999):
            e.control.error_text = "Enter a valid year"
            self.update()
            return
        e.control.error_text = None
        self.update()
        e.control.value = int(e.control.value)  # ensure integer format
        self.backend.update_config(field, e.control.value)

    def submit_journal(self, e):
        journal_name = e.control.parent.controls[0].value.strip()
        issn = e.control.parent.controls[1].value.strip()

        if (not issn
            or not issn.replace("-", "").isdigit()
            or len(issn) not in [8, 9]
        ):
            e.control.parent.controls[1].error_text = "Invalid"
            self.update()
            return
        if not journal_name:
            e.control.parent.controls[0].error_text = "Can't be empty"
            self.update()
            return
        
        # Check if the journal already exists
        if issn in [j["issn"] for j in self.backend.config["journals"]]:
            e.control.parent.controls[1].error_text = "Duplicated"
            self.update()
            return

        if journal_name in [j["name"] for j in self.backend.config["journals"]]:
            e.control.parent.controls[0].error_text = "Duplicated"
            self.update()
            return
        
        e.control.error_text = None
        self.backend.add_journal(journal_name, issn)
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

    def remove_journal(self, issn):
        self.backend.remove_journal(issn)
        self.journals_row.controls = self.get_journal_chip_row()
        self.update()

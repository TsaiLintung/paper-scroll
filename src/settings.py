import flet as ft


class Settings(ft.Column):

    def __init__(self, backend):
        super().__init__()
        self.backend = backend

        update = ft.TextButton(text="Update", on_click=self.backend.update_journals)


        # set year range
        start_year = ft.TextField(
            label="Start year", value=self.backend.config["start_year"], 
            max_length=4,
            width = 150
        )
        end_year = ft.TextField(
            label="End year", value=self.backend.config["end_year"], 
            max_length=4,
            width = 150
        )
        year_range = ft.Row([start_year, end_year], wrap = True)

        #add journal
        add_journal = ft.Row(
            [
                
                ft.TextField(label="Journal Name", value="", max_length=10, width=150),
                ft.TextField(label="ISSN", value="", max_length=9, width = 150),
                ft.IconButton(icon=ft.Icons.ADD, on_click=lambda e: None)  # placeholder
            ], 
            wrap=True
        )

        journals = []
        for journal in self.backend.config["journals"]:
            journals.append(
                ft.Chip(
                    label=ft.Text(journal.get("issn")),
                    leading=ft.Text(journal.get("name")),
                    on_delete=lambda e: None,  # placeholder
                )
            )

        self.controls = [
            ft.Card(
                ft.Container(
                    ft.Column(
                        [
                            ft.Text("Years", weight=ft.FontWeight.BOLD),
                            year_range,
                            ft.Divider(),
                            ft.Text("Journals", weight=ft.FontWeight.BOLD),
                            ft.Row(journals, wrap=True),
                            ft.Divider(),
                            ft.Text("Add Journal", weight=ft.FontWeight.BOLD),
                            add_journal, 
                            ft.Divider(),
                            update
                        ]),
                        padding=15
                    )
                )]
                
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.scroll = ft.ScrollMode.AUTO
        self.spacing = 20

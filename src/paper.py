import os
import json

class Paper:
    def __init__(self, data):
        self.data = data
        self.doi = data.get("doi", "")
        self.data["abstract"] = self._get_abstract()
        self.data["subtitle"] = self._get_subtitle()
        self.valid = bool(self.data.get("abstract")) and bool(self.data.get("authorships"))

    def get(self, key, default=None):
        """Get a value from the paper data, returning default if not found."""
        return self.data.get(key, default)
   
    def _get_subtitle(self):
        year = self.get("publication_year")
        journal = self.get("primary_location").get("source").get("display_name", "")
        authors = self.get("authorships")
        authors = ", ".join(author["author"]["display_name"] for author in authors)
        year_journal = f"{year} · {journal}" if year and authors else ""
        text = "\n".join(filter(None, [year_journal, authors]))
        return text

    def _get_abstract(self):
        abstract_inverted_index = self.data.get("abstract_inverted_index")
        if abstract_inverted_index:
            words_positions = []
            for word, positions in abstract_inverted_index.items():
                for pos in positions:
                    words_positions.append((pos, word))
            words_positions.sort()
            abstract = " ".join(word for _, word in words_positions)
        else:
            abstract = ""
        return abstract

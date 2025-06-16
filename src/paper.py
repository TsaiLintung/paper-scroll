import os
import json

class Paper:
    def __init__(self, data, parent_dir):
        self.data = data
        self.doi = data.get("doi", "")
        self.data["abstract"] = self._get_abstract()
        self.data["subtitle"] = self._get_subtitle()
        self.valid = bool(self.data.get("abstract")) and bool(self.data.get("authorships"))

        doi_filename = f"{self.doi.replace('/', '_')}.json"
        self.dir = os.path.join(parent_dir, doi_filename)

    def get(self, key):
        return self.data.get(key, "Not Available")
    
    def is_starred(self):
        return os.path.exists(self.dir)
    
    def star(self):
        """Star a paper by adding it to the history."""
        doi = self.get("doi")
        if not self.is_starred():
            with open(self.dir, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"Starred paper with DOI: {doi}")
        else:
            print(f"Paper with DOI: {doi} is already starred.")

    def unstar(self):
        """Unstar a paper by removing it from the history."""
        if self.is_starred():
            os.remove(self.dir)
            print(f"Unstarred paper with DOI: {self.doi}")
        else:
            print(f"Paper with DOI: {self.doi} is not starred.")
   
    def _get_subtitle(self):
        year = self.get("publication_year")
        journal = self.get("primary_location").get("source").get("display_name", "")
        authors = self.get("authorships")
        authors = ", ".join(author["author"]["display_name"] for author in authors)
        year_authors = f"{year} · {authors}" if year and authors else ""
        text = "\n".join(filter(None, [year_authors, journal]))
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

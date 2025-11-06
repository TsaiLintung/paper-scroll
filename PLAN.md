
## UI & Visual Improvement Opportunities
- Reintroduce a subtle backdrop tint behind the floating settings panel so the Explore list visually recedes when the overlay is open (`main.py:95`).
- Allow the settings container height to adapt or scroll instead of the fixed `height=520`, which clips content on smaller windows (`main.py:62`).
- Add spacing or margin around `PaperDisplay` cards so successive entries do not feel crowded against the divider lines (`frontend/paper_display.py:18`).
- Consider lighter surface colors or elevation to distinguish cards from the page background; currently `ft.Colors.SURFACE` can blend with the default theme (`frontend/paper_display.py:18`).
- Align the app bar actions with a small right padding to avoid icons hugging the window edge (`main.py:178`).
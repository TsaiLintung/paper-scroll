# Settings Redesign Plan

- **Baseline Audit**  
  - Capture current layout/screenshots with settings open on desktop and web targets.  
  - Inventory every control, grouping by domain (papers sync, journals, app display, diagnostics).  
  - Note interaction pain points (overlay padding, inconsistent spacing, status feedback location).

- **Information Architecture (IA)**  
  - Define primary sections (e.g., *Papers*, *Journals*, *Notifications*, *Appearance*, *Diagnostics*).  
  - Decide which controls collapse or move to secondary dialogs (e.g., add journal form).  
  - Specify responsive behaviour rules for narrow vs. wide layouts.

- **Layout Concepts**  
  - Sketch two low-fidelity wireframes using Flet primitives:  
    1. Split-pane layout with persistent left navigation.  
    2. Card-based accordion with progressive disclosure.  
  - Evaluate pros/cons, especially discoverability and vertical scroll length.

- **Visual Hierarchy & Styling**  
  - Establish consistent margins, column widths, and typography scale derived from theme tokens.  
  - Introduce reusable components (section header, field group container, action footer).  
  - Plan tone adjustments (background shade, divider usage, iconography).

- **Interaction & Feedback**  
  - Define micro-interactions: button states, validation, async loading indicators.  
  - Centralize backend status banner with inline spinner and toast fallbacks.  
  - Ensure keyboard accessibility (tab order, focus outlines, enter-to-submit).

- **Implementation Roadmap**  
  - Phase 1: Refactor settings module into subcomponents + data models.  
  - Phase 2: Apply new layout containers, update overlays, ensure responsive behaviour.  
  - Phase 3: Polish visuals, add tests (UI smoke, backend status).  
  - Phase 4: Document UX decisions in repo wiki and update screenshots/assets.

- **Validation Checklist**  
  - Run manual QA on desktop/web, verify overlay coverage and scroll boundaries.  
  - Confirm backend config mutations persist and error handling still surfaces.  
  - Collect feedback from users/stakeholders before final polish pass.

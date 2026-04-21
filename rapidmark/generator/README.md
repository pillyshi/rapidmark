# RapidMark Generator

Frontend annotation tool module built with Vue.js 3 + Vuetify.

## Overview

RapidMark Generator is a frontend module that produces interactive NER annotation tools as single HTML files. It uses Vue.js 3 Composition API and Vuetify 3 to provide a clean, responsive UI.

## Features

- **NER Annotation**: Select text spans and assign labels with a click
- **Hierarchical Labels**: Two-level label hierarchy (parent → child)
- **Progress Tracking**: Visualize annotation completion across all texts
- **Single-file Output**: Entire app (HTML + CSS + JS) packed into one HTML file via `vite-plugin-singlefile`
- **Result Embedding**: Pre-load existing annotations at build time via `__RESULT_CONFIG__`
- **Export / Import**: Download results as JSON; upload results to resume annotation

## Architecture

```
src/
├── App.vue                         # Root component
├── main.js                         # Entry point
├── components/
│   ├── Header.vue                  # App bar (upload / download)
│   ├── Main.vue                    # Layout container
│   ├── main/
│   │   ├── Content.vue             # Text display area
│   │   └── Sidebar.vue             # Sidebar layout
│   ├── main/content/
│   │   ├── ContentHeader.vue       # Current text ID
│   │   ├── ContentText.vue         # Annotatable text with highlights
│   │   ├── ContentFooter.vue       # Navigation and status controls
│   │   └── content-text/
│   │       └── SelectionOverlay.vue # Label picker popup
│   └── sidebar/
│       ├── Progress.vue            # Overall progress bar
│       └── workspace/
│           ├── Entity.vue          # Entity list for current text
│           └── Comment.vue         # Comment panel (placeholder)
├── composables/
│   ├── useTask.ts                  # Task configuration state
│   ├── useEntity.ts                # Entity CRUD
│   ├── useLabel.ts                 # Label tree helpers
│   ├── useStatus.ts                # Per-text annotation status
│   ├── useResult.ts                # Load results into state
│   ├── useEntityHighlight.ts       # Hover highlight state
│   └── useEntitySelection.ts      # Multi-select state
└── plugins/
    └── vuetify.js                  # Vuetify configuration
```

## Data Flow

Task and result data are injected at build time as global constants:

- `__TASK_CONFIG__` — task definition and texts (always set)
- `__RESULT_CONFIG__` — pre-existing annotation results (set when `--result` is passed to `rapidmark build`)

Both are set via the `define` option in `vite.config.js`.

## Development

```bash
cd rapidmark/generator
npm install
npm run dev      # Start dev server with sample task data
npm run build    # Production build (single HTML file)
npm run test     # Run unit tests
```

## Result Format

```json
{
  "taskInfo": {
    "taskType": "ner",
    "taskId": "news_ner",
    "taskTitle": "News Article NER",
    "exportedAt": "2025-01-01T00:00:00.000Z",
    "exportFormat": "unified_v1"
  },
  "results": {
    "doc1": {
      "status": "completed",
      "attributes": {},
      "entities": [
        { "id": "e1", "start": 0, "end": 9, "text": "Apple Inc", "label": "organization" }
      ]
    }
  }
}
```

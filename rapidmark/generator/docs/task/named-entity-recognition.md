# Named Entity Recognition (NER) — Annotation Guide

## Overview

RapidMark supports Named Entity Recognition tasks. Annotators select text spans and assign labels to mark entities such as persons, organizations, and locations.

## How to Annotate

### 1. Select a text span

1. Click and drag over the text you want to annotate
2. A label picker popup appears above the selection
3. Click the desired label to create the entity

### 2. Manage entities

- Created entities are highlighted in the text with the label's color
- The **Entities** panel in the sidebar lists all entities for the current text
- Click the delete icon next to an entity to remove it

### 3. Hierarchical labels

When labels have a parent-child hierarchy, the label picker shows only root labels. Child labels of the selected root can be picked from the sub-list.

### 4. Navigation and status

Use the **Prev / Next** buttons at the bottom to move between texts.

Mark each text with one of the following statuses:

| Status | Description |
|--------|-------------|
| Pending | Not yet annotated (default) |
| Done | Annotation complete |
| Exclude | Text should be excluded from the dataset |

The **Next incomplete** button jumps to the next text still in "Pending" status.

### 5. Export results

Click the **Download** button (↓ icon) in the toolbar to save results as a `.result.rapidmark.json` file.

### 6. Upload results

Click the **Upload** button (↑ icon) to load a previously exported result file and resume annotation.

## Label Colors

Each root label is assigned a distinct color automatically. Child labels inherit the parent's color with a lighter shade.

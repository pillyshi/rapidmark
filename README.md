# RapidMark

Fast and efficient NER annotation tool.

## Features

- **NER Annotation**: Named Entity Recognition with hierarchical label support
- **Modern Web Interface**: Vue.js-based annotation interface with intuitive UX
- **Worker Support**: Personalized annotation workflows for individual workers
- **Result Embedding**: Embed existing results into HTML for easy review and correction
- **Result Merging**: Inter-annotator agreement and result consolidation
- **Caching System**: Efficient generator setup with intelligent caching

## Installation

Install RapidMark using pip:

```bash
pip install rapidmark
```

Or install from source using Poetry:

```bash
git clone https://github.com/pillyshi/rapidmark-public.git
cd rapidmark-public
poetry install
```

## Requirements

- Python 3.12+
- Node.js 16+ (for building annotation interfaces)
- npm

## Quick Start

1. **Create a new NER task**:
   ```bash
   rapidmark init --name my-task
   ```

2. **Build annotation tool**:
   ```bash
   rapidmark build my-task.rapidmark.json --worker alice
   ```

3. **Open the generated HTML file** in your browser and start annotating!

## Usage

### Initialize New Tasks

```bash
# Create NER task
rapidmark init --name entity-extraction

# Include text files from directory
rapidmark init --name my-task --texts ./documents/
```

### Build Annotation Tools

```bash
# Worker-specific build
rapidmark build task.rapidmark.json --worker alice

# Embed existing results (for review or correction)
rapidmark build task.rapidmark.json --worker alice --result alice.result.rapidmark.json

# Custom output location
rapidmark build task.rapidmark.json --worker alice --output annotation-tool.html
```

The `--result` option embeds annotation results directly into the HTML file, so the
worker only needs a single file — no manual upload step required. The worker can also
correct the pre-loaded annotations and re-export.

### Merge Results

```bash
# Merge all results in directory
rapidmark merge --result-dir ./results/

# With strategy options
rapidmark merge --result-dir ./results/ --strategy majority --min-agreement 0.6
```

### Other Commands

```bash
# Show help and available commands
rapidmark info

# Clean generator cache
rapidmark clean
```

## Task Configuration

RapidMark uses JSON configuration files to define annotation tasks:

```json
{
  "definition": {
    "id": "news_ner",
    "name": "News Article NER",
    "type": "ner",
    "labels": [
      {"id": "person", "name": "Person"},
      {"id": "organization", "name": "Organization"},
      {"id": "location", "name": "Location"}
    ]
  },
  "texts": [
    {"id": "doc1", "content": "Apple Inc. was founded by Steve Jobs in Cupertino."}
  ]
}
```

## Python SDK

Define tasks programmatically:

```python
from rapidmark import RapidmarkLabel, RapidmarkTaskDefinition, RapidmarkText, RapidmarkTask

task = RapidmarkTask(
    definition=RapidmarkTaskDefinition(
        id="news_ner",
        name="News Article NER",
        labels=[
            RapidmarkLabel(id="person", name="Person"),
            RapidmarkLabel(id="organization", name="Organization"),
            RapidmarkLabel(id="location", name="Location"),
        ],
    ),
    texts=[
        RapidmarkText(id="doc1", content="Apple Inc. was founded by Steve Jobs."),
    ],
)
task.save("news_ner.rapidmark.json")
```

See `examples/ner/` for more usage examples.

## Development

```bash
git clone https://github.com/pillyshi/rapidmark-public.git
cd rapidmark-public
poetry install
poetry run rapidmark --help
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

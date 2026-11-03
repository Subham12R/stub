# stub

A small Python file analyzer. It walks the AST to report functions, imports, and size, then optionally sends that report plus the source to Gemini for a CodeRabbit-style review.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- A Gemini API key (only if you use `--ai`)

## Setup

```bash
uv sync
cp .env.example .env
```

Put your key in `.env`:

```
GEMINI_API_KEY=your-key-here
```

`.env` is gitignored. Do not commit it.

## Usage

Static report only:

```bash
uv run python main.py sample.py
```

Static report plus Gemini review:

```bash
uv run python main.py sample.py --ai
```

Replace `sample.py` with any `.py` file.

The static report includes:

- Non-empty, non-comment line count
- Functions and their argument names
- Longest function (by source span)
- Imports

`--ai` needs `GEMINI_API_KEY` in the environment or `.env`. If the key is missing, the CLI prints the static report and an error instead of a review.

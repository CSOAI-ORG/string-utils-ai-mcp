# String Utils Ai

> By [MEOK AI Labs](https://meok.ai) — MEOK AI Labs MCP Server

String Utils AI MCP Server

## Installation

```bash
pip install string-utils-ai-mcp
```

## Usage

```bash
# Run standalone
python server.py

# Or via MCP
mcp install string-utils-ai-mcp
```

## Tools

### `slugify`
Convert text to a URL-friendly slug.

**Parameters:**
- `text` (str)
- `separator` (str)
- `max_length` (int)
- `lowercase` (bool)

### `camel_to_snake`
Convert between camelCase, snake_case, kebab-case, and PascalCase.

**Parameters:**
- `text` (str)
- `direction` (str)

### `truncate_smart`
Smartly truncate text at word boundaries with a suffix.

**Parameters:**
- `text` (str)
- `max_length` (int)
- `suffix` (str)
- `preserve_words` (bool)

### `extract_numbers`
Extract all numbers from text.

**Parameters:**
- `text` (str)
- `include_decimals` (bool)
- `include_negative` (bool)


## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## Links

- **Website**: [meok.ai](https://meok.ai)
- **GitHub**: [CSOAI-ORG/string-utils-ai-mcp](https://github.com/CSOAI-ORG/string-utils-ai-mcp)
- **PyPI**: [pypi.org/project/string-utils-ai-mcp](https://pypi.org/project/string-utils-ai-mcp/)

## License

MIT — MEOK AI Labs

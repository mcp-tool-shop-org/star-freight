# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |
| < 1.0   | No        |

## Reporting a Vulnerability

Star Freight is a single-player offline game with no network features,
no telemetry, no user accounts, and no data collection.

If you find a security issue in the build or packaging:

1. **Do not** open a public issue
2. Email: 64996768+mcp-tool-shop@users.noreply.github.com
3. Include: description, reproduction steps, and affected version
4. Expected response: within 7 days

## Threat Model

- **No network access**: Game runs entirely offline
- **No secrets**: No API keys, tokens, or credentials
- **No telemetry**: No data leaves the user's machine
- **No user accounts**: Save files are local only
- **Dependencies**: Typer, Rich, Textual (all well-maintained, no native code)

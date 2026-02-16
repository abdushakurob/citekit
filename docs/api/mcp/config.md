# MCP Configuration

You can configure CiteKit to work with any MCP-compliant AI agent or IDE.

## Claude Desktop

Add CiteKit to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "citekit": {
      "command": "python",
      "args": ["-m", "citekit.cli", "serve"]
    }
  }
}
```

---

## Cursor / Cline / Roo Code

Most modern IDE extensions support MCP via custom command execution.

1.  Open the MCP settings in your IDE.
2.  Add a new server named **CiteKit**.
3.  **Command**: `python`
4.  **Args**: `["-m", "citekit.cli", "serve"]`

---

## CLI Options for `serve`

The `serve` command supports the following environment variables and flags through the SDK and CLI:

### Storage & Output
By default, CiteKit looks for maps in `.resource_maps/` and saves output to `.citekit_output/`. You can change these by setting up a `CiteKitClient` configuration, though the `serve` command currently uses defaults.

### Remote execution (Npx)
If you don't want to install CiteKit globally, you can run the JS MCP server via npx:

```bash
npx -y citekit serve
```

---

## Troubleshooting

-   **Path Errors**: Ensure `python` or `node` is in your system `PATH`.
-   **Permission Errors**: AI agents running MCP servers require permission to write to the `outputDir`. Ensure the directory is writable by the process.
-   **Missing Maps**: If `listResources` returns an empty array, run `citekit ingest` on some files first!

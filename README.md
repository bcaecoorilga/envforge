# envforge

> Snapshot, diff, and restore environment variable sets across dev, staging, and production.

---

## Installation

```bash
pip install envforge
```

Or with [pipx](https://pypa.github.io/pipx/):

```bash
pipx install envforge
```

---

## Usage

```bash
# Capture a snapshot of the current environment
envforge snapshot save --name dev

# Diff two snapshots
envforge snapshot diff dev staging

# Restore an environment from a snapshot
envforge snapshot restore staging --export

# List all saved snapshots
envforge snapshot list
```

**Example diff output:**

```
~ DATABASE_URL   postgres://localhost/dev  →  postgres://prod-host/app
+ NEW_RELIC_KEY  (not set)                →  abc123xyz
- DEBUG          true                     →  (not set)
```

Snapshots are stored locally in `~/.envforge/snapshots/` as encrypted JSON files. Use `--output` to specify a custom path.

---

## Configuration

| Option | Default | Description |
|---|---|---|
| `--format` | `json` | Output format (`json`, `dotenv`, `yaml`) |
| `--mask` | `false` | Mask sensitive values in output |
| `--encrypt` | `true` | Encrypt snapshot files at rest |

---

## License

MIT © [envforge contributors](https://github.com/yourusername/envforge)
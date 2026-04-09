# envdiff

A lightweight CLI tool to compare `.env` files across environments and surface missing or mismatched keys.

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourusername/envdiff.git
cd envdiff
pip install -e .
```

## Usage

Compare two `.env` files:

```bash
envdiff .env.local .env.production
```

Compare multiple environment files:

```bash
envdiff .env.dev .env.staging .env.prod
```

### Example Output

```
Missing keys:
  .env.production: DATABASE_URL, REDIS_HOST
  .env.local: STRIPE_WEBHOOK_SECRET

Mismatched values (same key, different values):
  DEBUG: .env.local="true" | .env.production="false"
  LOG_LEVEL: .env.local="debug" | .env.production="info"

Common keys: 12
```

### Options

```bash
envdiff --help                    # Show all available options
envdiff --ignore-values FILE1 FILE2   # Only check for missing keys
envdiff --json FILE1 FILE2        # Output results as JSON
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
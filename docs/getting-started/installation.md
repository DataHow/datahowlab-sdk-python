# Installation

## Requirements

- Python 3.11 or higher
- DataHowLab API Key

## Install via pip

```bash
pip install datahowlab-sdk
```

## Install via uv

```bash
uv add datahowlab-sdk
```

## Install via Poetry

```bash
poetry add datahowlab-sdk
```

## Optional Dependencies

### Documentation Tools

If you want to build the documentation locally:

```bash
pip install datahowlab-sdk[docs]
```

### Development Tools

If you want to contribute to the SDK:

```bash
pip install datahowlab-sdk[dev]
```

## Verify Installation

```python
from dhl_sdk import DataHowLabClient

# Should print version information
import dhl_sdk
print(dhl_sdk.__version__)
```

## Next Steps

Continue to the [Quick Start](quick-start.md) guide to start using the SDK.

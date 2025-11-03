# Client Initialization

Learn how to initialize and configure the DataHowLab SDK client.

## Basic Initialization

```python
from dhl_sdk import DataHowLabClient

client = DataHowLabClient(
    api_key="your-api-key",
    base_url="https://yourdomain.datahowlab.ch/"
)
```

## Environment Variables

You can set the API key via environment variable:

```bash
export DHL_API_KEY="your-api-key"
```

Then initialize without the api_key parameter:

```python
client = DataHowLabClient(
    base_url="https://yourdomain.datahowlab.ch/"
)
```

## Configuration Options

### Request Timeout

Configure request timeouts (default is 30 seconds):

```python
client = DataHowLabClient(
    api_key="your-api-key",
    base_url="https://yourdomain.datahowlab.ch/",
    timeout=60  # 60 seconds
)
```

For more details, see the [API Reference](../api/client.md).

# DataHowLab's SDK

DataHowLab SDK is a software development kit designed to simplify and streamline
the integration of some functionalities of DataHowLab's into a simple Python
package.

This SDK provides a convenient and efficient way to interact with DataHowLab's
API, allowing you to easily access and use your models and data.

- **Data Exporting**
  - Access all the information about your data
  - Get information and your Products, Variables, Recipes and Experiments
  - Export the data associated with each Experiments

- **Data Importing**
  - Create new Products
  - Create new Variables
  - Create new Recipes
  - Create new Experiments

- **Model Predictions**
  - Using your models trained on DataHowLab, compute new predictions for your
    new data just by accessing the model.
  - The model can be accessed by selecting the Project and the Model you want to
    use.
  - The data will be validated prior to the prediction.

## Prerequisites

- **Python:** Ensure that you have Python installed (version 3.9 or higher) on
  your system.
- **API Key** Make sure you have a valid DataHowLab API Key.

## Installation

### From PyPI

Assuming that you have a supported version of Python installed, you can install
datahowlab-sdk from PyPI with:

```bash
$ pip install datahowlab-sdk
```

### From Source

1. **Install Poetry** If you don't have Poetry installed, you can do it using
   `pipx`:

```bash
$ pipx install poetry
```

For more detailed installation instructions, you can refer to the
[Poetry documentation](https://python-poetry.org/docs/#installation).

2. **Clone the Repository**: You'll need to clone this project's repository to
   your local machine. You can do this using `git`:

```bash
# Example code for installation
$ git clone https://github.com/DataHow/datahowlab-sdk-python.git
$ cd your-repo
```

4. **Install Project Dependencies**: Use Poetry to install the project's
   dependencies. Poetry will read the `pyproject.toml` file and set up your
   project environment:

```bash
$ poetry install
```

5. **Activate Virtual Environment (Optional)**: Poetry creates a virtual
   environment for your project. You can activate it using the following
   command:

```bash
$ poetry shell
```

## Usage

For comprehensive example scripts, check the [examples/](examples/) directory.

For an interactive notebook guide, check [examples.ipynb](examples.ipynb)

For an overview of all the validations that the SDK performs when importing
data, check [validations.md](validations.md)

### Importing Package

```python
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

# Load API key from DHL_API_KEY environment variable
key = APIKeyAuthentication()

# Initialize client with your DataHowLab instance URL
client = DataHowLabClient(auth_key=key, base_url="https://yourdomain.datahowlab.ch/")
```

### Data Accessing

```python
# Access products
products = client.get_products(code="PROD")
product = next(products)

# Get experiments for a product
experiments = client.get_experiments(product_id=product.id)
experiment = next(experiments)

# Get experiment data in compatibility format
# Returns: {variable_code: {"values": [...], "timestamps": [...]}}
exp_data = experiment.get_data_compat()

# Access related entities
variables = experiment.get_variables()
product = experiment.get_product()

# Access projects and models
projects = client.get_projects(name="My Project")
project = next(projects)
models = list(project.get_models())
```

For complete working examples, see [examples/data_access_compat.py](examples/data_access_compat.py) (recommended) or [examples/data_access.py](examples/data_access.py) (OpenAPI format)

### Data Importing

```python
from dhl_sdk.entities.product import ProductRequest
from openapi_client.models.process_format_code import ProcessFormatCode

# Create a product (code must be <= 10 characters)
product_request = ProductRequest.new(
    name="Example Product",
    code="EXPROD",
    description="Product created via SDK",
    process_format=ProcessFormatCode.MAMMAL,
    tags={"source": "sdk"}
)
product = product_request.create(client)
```

**Note**: Variable and experiment creation are currently affected by an OpenAPI deserialization issue. See [KNOWN_ISSUES.md](KNOWN_ISSUES.md) for details.

For a working example, see [examples/product_creation.py](examples/product_creation.py)

### Model Predictions

```python
from openapi_client.models.model_type import ModelType

# Get a project and find a successful model
projects = client.get_projects(name="My Project")
project = next(projects)

models = [m for m in project.get_models(model_type=ModelType.PROPAGATION) if m.success]
model = models[0]

# Get experiment data from the model to use as input
model_experiments = list(model.get_experiments())
model_exp = model_experiments[0]
exp_data = model_exp.get_data_compat()

# Prepare inputs from experiment data
model_vars = list(model.get_variables())
input_vars = [v for v in model_vars if v.input_type != "none"]

inputs = {}
timestamps = []
for var in input_vars:
    if var.code in exp_data:
        data = exp_data[var.code]
        inputs[var.code] = data['values']
        if not timestamps:
            timestamps = data['timestamps']

# Make predictions
predictions = model.predict_compat(inputs, timestamps, timestamps_unit="s")

# Access predicted values (returns dict with variable codes as keys)
for var_code, values in predictions.items():
    print(f"{var_code}: {values[0]:.2f} -> {values[-1]:.2f}")
```

For a complete working example, see [examples/model_prediction_compat.py](examples/model_prediction_compat.py)

## Configuration

### SSL/TLS Certificates

When dealing with on-premises deployments, it's common to encounter scenarios
where self-signed certificates or certificates issued by custom certification
authorities (CAs) are used. These certificates ensure secure communication
within the internal network, but they are not recognized by default by the
standard certificate authorities that browsers and software libraries trust.

Therefore, when making HTTPS requests to endpoints secured with these
certificates, you need to explicitly tell your software to trust them. The SDK
currently supports two ways to do this.

#### Option 1: using the truststore library

This should be the preferred option in scenarios where the certificate has been
signed by a custom CA that is trusted on the machine where your application is
running (e.g. your company laptop/server/workstation).

[Truststore](https://pypi.org/project/truststore/) is a library which exposes
native system certificate stores (ie "trust stores") and allows you to trust
certificates issued by CAs already present in your native system trust store.

Make sure to add `truststore` to your project dependencies or install it with
`pip install truststore`. Then import the package and inject the system trust
store at the beginning of your application, before you inizialize the
`DataHowLabClient`:

```python
import truststore
truststore.inject_into_ssl()

from dhl_sdk import DataHowLabClient, APIKeyAuthentication

key = APIKeyAuthentication("<KEY>")
dhl_url = "<URL>"

client = DataHowLabClient(auth_key=key, base_url=dhl_url)
```

#### Option 2: using the `verify_ssl` option

If you're dealing with self-signed certificates that are not trusted by any CA,
`DataHowLabClient` exposes a `verify_ssl` option to point to the certificate
file or to entirely disable SSL/TLS verification.

> :warning: Disabling SSL/TLS verification can expose you to significant
> security risks. Use this option only if you are working in a trusted network

Assuming you have a self-signed certificate file named `certificate.pem`, use
the following code to import it in your application to verify your requests.

```python
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

key = APIKeyAuthentication("<KEY>")
dhl_url = "<URL>"
cert_path = 'path/to/certificate.pem'

client = DataHowLabClient(auth_key=key, base_url=dhl_url, verify_ssl=cert_path)
```

Alternatively, set `verify_ssl` to `False` (default value is `True`) to disable
SSL/TLS verification.

```python
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

key = APIKeyAuthentication("<KEY>")
dhl_url = "<URL>"

client = DataHowLabClient(auth_key=key, base_url=dhl_url, verify_ssl=False)
```


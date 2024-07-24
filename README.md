# DataHowLab's SDK

DataHowLab SDK is a software development kit designed to simplify and streamline 
the integration of some functionalities of DataHowLab's into a simple Python package. 

This SDK provides a convenient and efficient way to interact with DataHowLab's API, 
allowing you to easily access and use your models and data.

* **Data Exporting**
  * Access all the information about your data
  * Get information and your Products, Variables, Recipes and Experiments
  * Export the data associated with each Experiments

* **Data Importing**
  * Create new Products
  * Create new Variables
  * Create new Recipes
  * Create new Experiments

* **Model Predictions**
  * Using your models trained on DataHowLab, compute new predictions for your new data just by accessing the model.
  * The model can be accessed by selecting the Project and the Model you want to use.
  * The data will be validated prior to the prediction.

## Prerequisites

- **Python:** Ensure that you have Python installed (version 3.9 or higher) on your system.
- **API Key** Make sure you have a valid DataHowLab API Key.

## Installation

### From PyPI

Assuming that you have a supported version of Python installed, you can install datahowlab-sdk from PyPI with: 

```bash
$ pip install datahowlab-sdk
```

### From Source

1. **Install Poetry** If you don't have Poetry installed, you can do it using `pipx`:

```bash 
$ pipx install poetry
```

For more detailed installation instructions, you can refer to the [Poetry documentation](https://python-poetry.org/docs/#installation).

2. **Clone the Repository**: You'll need to clone this project's repository to your local machine. You can do this using `git`:

```bash
# Example code for installation
$ git clone https://github.com/DataHow/datahowlab-sdk-python.git
$ cd your-repo
```

4. **Install Project Dependencies**: Use Poetry to install the project's dependencies. Poetry will read the `pyproject.toml` file and set up your project environment:

```bash 
$ poetry install
```

5. **Activate Virtual Environment (Optional)**: Poetry creates a virtual environment for your project. You can activate it using the following command:
```bash 
$ poetry shell
```

## Usage

For a more comprehensive example guide, check [HERE](examples.ipynb)

### Importing Package

```python
import numpy as np
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

# DHL_API_KEY env var is loaded from the .env file or added directly as an argument here 
key = APIKeyAuthentication()

# This is an example. Change this line to your DataHowLab Instance
your_url = "https://yourdomain.datahowlab.ch/"
client = DataHowLabClient(auth_key=key, base_url=your_url)
```

### Data Accessing 

```python
# You can access each entity in the DataBase by using the `get_*entity*` method, i.e. 
experiments = client.get_experiments(name="experiment name")
recipes = client.get_recipes(name="recipe name")
products = client.get_products(code="PROD")
variables = client.get_variables(code="VAR1")


# All this methods will result in a Iterable objects. For example, to access each experiment, use the `next(experiments)` method.
experiment = next(experiments)

# Once you find your experiment of interest, you can download the data of that experiment by referencing your `client`
experiment_data = experiment.get_data(client)
```


### Data Importing

```python
from dhl_sdk.db_entities import Product, Variable, Experiment, VariableCategorical, VariableNumeric

# In order to import a new experiment, you first need to get or create the correspoding variables and product. 
# You can get the data using the previous methods. 

product = Product.new(name="ExampleSDK", code="SDKPr", description="Example Product")

variable1 = Variable.new(code="EXv1", name="Example Variable 1", description="This is an example X variable", measurement_unit="l", variable_group="X Variables", variable_type=VariableNumeric())
variable2 = Variable.new(code="EXv2", name="Example Variable 2", description="This is an example Z variable", measurement_unit="n", variable_group="Z Variables", variable_type=VariableCategorical())

# In order to import the new entities to the DB, you can use the `create` method of the client.
product = client.create(product)
variable1 = client.create(variable1)
variable2 = client.create(variable2)


# for the data associated with the new experiment, you can create it using a dictionary form, with the {"variable code": {"timestamps": [], "values": []}}
run_data = {
            "EXv1": {
                "timestamps": [
                    0,
                    86400,
                    172800,

                ],
                "values": [
                    5.1,
                    3.5,
                    1.3,
                ]
            },
            "EXv2": {
                "timestamps": [
                    0],
                "values": [
                    "A"]

            }
}

experiment = Experiment.new(name="SDK EXP", description="new experiment test for sdk", product=product, variables=[variable1, variable2], data_type="run", data=run_data, variant="run", start_time="2020-09-21T08:45:50Z", end_time="2020-10-05T08:45:50Z")

#if all validations are successful, your new experiment will be uploaded to the database using:
client.create(experiment)
```


### Model Predictions

```python
# `client.get_projects()` is called to retrieve a list of projects. 
# You can filter the projects by name if you include `name=project_name` and project type `spectroscopy/cultivation`. 
projects = client.get_projects(name="project_name", project_type="spectroscopy")

# This will result in a Iterable object. To access each project, use the `next(projects)` function.
project = next(projects)

# Once you find your project of interest, you can access all the models
models = project.get_models(name="Test model")

#If you want to check all the models inside a project, just list the models and select from there
list_of_models = list(models)
model = list_of_models[2]

# Now you just need some data. Here is an example how to load data from an example.csv file using numpy
# make sure your array only contains the values and not other information, like labels
data = np.genfromtxt("example.csv", delimiter=',')

# next, use the selected model to predict you outputs using the loaded spectra
predictions = model.predict(data)

```

## Configuration
### SSL/TLS Certificates
When dealing with on-premises deployments, it's common to encounter scenarios where self-signed certificates
or certificates issued by custom certification authorities (CAs) are used.
These certificates ensure secure communication within the internal network, but they are not recognized by default
by the standard certificate authorities that browsers and software libraries trust.

Therefore, when making HTTPS requests to endpoints secured with these certificates, you need to explicitly tell
your software to trust them. The SDK currently supports two ways to do this.

#### Option 1: using the truststore library
This should be the preferred option in scenarios where the certificate has been signed by a custom CA that is trusted
on the machine where your application is running (e.g. your company laptop/server/workstation).

[Truststore](https://pypi.org/project/truststore/) is a library which exposes native system
certificate stores (ie "trust stores") and allows you to trust certificates issued by CAs already present in your
native system trust store.

Make sure to add `truststore` to your project dependencies or install it with `pip install truststore`.
Then import the package and inject the system trust store at the beginning of your application, before you inizialize
the `DataHowLabClient`:
```python
import truststore
truststore.inject_into_ssl()

from dhl_sdk import DataHowLabClient, APIKeyAuthentication

key = APIKeyAuthentication("<KEY>")
dhl_url = "<URL>"

client = DataHowLabClient(auth_key=key, base_url=dhl_url)
```

#### Option 2: using the `verify_ssl` option
If you're dealing with self-signed certificates that are not trusted by any CA, `DataHowLabClient`
exposes a `verify_ssl` option to point to the certificate file or to entirely disable SSL/TLS verification.

> :warning: Disabling SSL/TLS verification can expose you to significant security risks.
Use this option only if you are working in a trusted network

Assuming you have a self-signed certificate file named `certificate.pem`, use the following code to import it in your
application to verify your requests.

```python
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

key = APIKeyAuthentication("<KEY>")
dhl_url = "<URL>"
cert_path = 'path/to/certificate.pem'

client = DataHowLabClient(auth_key=key, base_url=dhl_url, verify_ssl=cert_path)
```

Alternatively, set `verify_ssl` to `False` (default value is `True`) to disable SSL/TLS verification.
```python
from dhl_sdk import DataHowLabClient, APIKeyAuthentication

key = APIKeyAuthentication("<KEY>")
dhl_url = "<URL>"

client = DataHowLabClient(auth_key=key, base_url=dhl_url, verify_ssl=False)
```
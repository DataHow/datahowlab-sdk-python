# DataHowLab Prediction SDK

DHL_SDK is a software development kit (SDK) designed to simplify and streamline the integration 
of DataHowLab's Prediction capabilities into a simple Python package. 

This SDK provides a convenient and efficient way to interact with DataHowLab's API, enabling access to the 
Projects and Models created, as well as making predictions using these models with new sets of data.

## Prerequisites

- **Python:** Ensure that you have Python installed (version 3.9 or higher) on your system.
- **API Key** Make sure you have a valid DataHowLab API Key. 

## Installation

1. **Install Poetry** If you don't have Poetry installed, you can do it using `pipx`:

```bash 
$ pip install poetry
```

For more detailed installation instructions, you can refer to the [Poetry documentation](https://python-poetry.org/docs/#installation).

2. **Clone the Repository**: You'll need to clone this project's repository to your local machine. You can do this using `git`:

```bash
# Example code for installation
$ git clone https://github.com/DataHow/DHL_SDK.git
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

```python
import numpy as np
from dhl_sdk import SpectraHowClient, APIKeyAuthentication

# DHL_API_KEY env var is loaded from the .env file or added directly as an argument here 
key = APIKeyAuthentication()
your_url = "https://yourdomain.datahowlab.ch/"
client = SpectraHowClient(auth_key=key, base_url=your_url)

# `client.get_projects()` is called to retrieve a list of projects. You can filter the projects by name if you include `name=project_name`. 
projects = client.get_projects(name="project_name")

# This will result in a Iterable object. To access each project, use the `next(projects)` function.
project = next(projects)

# Once you find your project of interest, you can access all the models
models = project.get_models(name="Test model")

#If you want to check all the models inside a project, just list the models and select from there
list_of_models = list(models)
model = list_of_models[2]

# Now you just need some data. Here is an example how to load data from an example.csv file using numpy
# make sure your array only contains the values and not other information, like labels
spectra = np.genfromtxt("example.csv", delimiter=',')

# next, use the selected model to predict you outputs using the loaded spectra
predictions = model.predict(spectra)

```

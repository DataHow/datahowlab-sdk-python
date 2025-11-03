"""Pytest fixtures for integration testing with mock API responses."""

from typing import Any
from unittest.mock import patch

import pytest

# =============================================================================
# Sample API Response Data
# =============================================================================

SAMPLE_PRODUCT = {
    "id": "prod-123",
    "code": "PROD1",
    "name": "Test Product",
    "description": "A test product",
    "processFormat": "mammalian",
}

SAMPLE_VARIABLE_NUMERIC = {
    "id": "var-123",
    "code": "TEMP",
    "name": "Temperature",
    "measurementUnit": "°C",
    "group": {"id": "group-x", "code": "X_VARS", "name": "X Variables"},
    "variant": "numeric",
    "numeric": {
        "min": 0.0,
        "max": 100.0,
        "default": 25.0,
        "interpolation": "linear",
    },
    "description": "Process temperature",
}

SAMPLE_VARIABLE_CATEGORICAL = {
    "id": "var-456",
    "code": "PHASE",
    "name": "Process Phase",
    "measurementUnit": "n",
    "group": {"id": "group-z", "code": "Z_VARS", "name": "Z Variables"},
    "variant": "categorical",
    "categorical": {
        "categories": ["Init", "Growth", "Production", "Harvest"],
        "strict": True,
        "default": "Init",
    },
}

SAMPLE_VARIABLE_LOGICAL = {
    "id": "var-789",
    "code": "PUMP_ON",
    "name": "Pump Status",
    "measurementUnit": "bool",
    "group": {"id": "group-x", "code": "X_VARS", "name": "X Variables"},
    "variant": "logical",
    "logical": {"default": False},
}

SAMPLE_VARIABLE_FLOW = {
    "id": "var-flow-1",
    "code": "FEED",
    "name": "Feed Flow",
    "measurementUnit": "L/h",
    "group": {"id": "group-flows", "code": "FLOWS", "name": "Flows"},
    "variant": "flow",
    "flow": {
        "flowType": "conti",
        "references": [{"measurement": "FLOW_RATE", "concentration": "FEED_CONC"}],
        "stepSize": 60,
        "volumeVariable": "VOLUME_VAR",
    },
}

SAMPLE_VARIABLE_SPECTRUM = {
    "id": "var-spec-1",
    "code": "SPEC1",
    "name": "Spectrum",
    "measurementUnit": "AU",
    "group": {"id": "group-y", "code": "Y_VARS", "name": "Y Variables"},
    "variant": "spectrum",
    "spectrum": {
        "xAxis": {
            "dimension": 100,
            "unit": "nm",
            "min": 400.0,
            "max": 700.0,
            "label": "Wavelength",
        },
        "yAxis": {"label": "Absorbance"},
    },
}

SAMPLE_EXPERIMENT = {
    "id": "exp-123",
    "name": "Test Experiment",
    "description": "A test experiment",
    "product": {"id": "prod-123"},
    "variables": [{"id": "var-123"}, {"id": "var-456"}],
    "processFormat": "mammalian",
    "variant": "run",
    "startTime": "2025-01-01T00:00:00Z",
    "endTime": "2025-01-02T00:00:00Z",
    "instances": [
        {"column": "TEMP", "fileId": "file-123"},
        {"column": "PHASE", "fileId": "file-123"},
    ],
}

SAMPLE_EXPERIMENT_DATA = {
    "timeseries": {
        "TEMP": {
            "timestamps": [1735689600, 1735776000],
            "values": [25.5, 26.0],
        },
        "PHASE": {
            "timestamps": [1735689600],
            "values": ["Init"],
        },
    }
}

SAMPLE_RECIPE = {
    "id": "recipe-123",
    "name": "Test Recipe",
    "description": "A test recipe",
    "product": {"id": "prod-123"},
    "variables": [{"id": "var-123"}],
    "duration": 3600,
    "instances": [{"column": "TEMP", "fileId": "file-456"}],
}

SAMPLE_PROJECT = {
    "id": "proj-123",
    "name": "Test Project",
    "projectType": "cultivation",  # Changed to cultivation as default
    "processFormat": "mammalian",
    "processUnitId": "04a324da-13a5-470b-94a1-bda6ac87bb86",  # cultivation ID
    "product": {"id": "prod-123"},
}

SAMPLE_PROJECT_SPECTROSCOPY = {
    "id": "proj-456",
    "name": "Spectroscopy Project",
    "projectType": "spectroscopy",
    "processFormat": "mammalian",
    "processUnitId": "373c173a-1f23-4e56-874e-90ca4702ec0d",  # spectroscopy ID
    "product": {"id": "prod-123"},
}

SAMPLE_MODEL = {
    "id": "model-123",
    "name": "Test Model",
    "status": "ready",
    "modelType": "propagation",  # Cultivation propagation model
    "project": {"id": "proj-123"},
}

SAMPLE_MODEL_HISTORICAL = {
    "id": "model-789",
    "name": "Historical Model",
    "status": "ready",
    "modelType": "historical",  # Cultivation historical model
    "project": {"id": "proj-123"},
}

SAMPLE_MODEL_SPECTROSCOPY = {
    "id": "model-456",
    "name": "Spectroscopy Model",
    "status": "ready",
    "modelType": "spectra",
    "project": {"id": "proj-456"},
}

SAMPLE_DATASET = {
    "id": "dataset-123",
    "name": "Test Dataset",
    "project": {"id": "proj-123"},
}

SAMPLE_PREDICTION_OUTPUT = {
    "predictions": {"OUTPUT1": [1.0, 2.0], "OUTPUT2": [3.0, 4.0]},
    "confidenceIntervals": {"OUTPUT1": {"lower": [0.9, 1.9], "upper": [1.1, 2.1]}},
    "metadata": {"modelId": "model-123", "modelName": "Test Model"},
}

SAMPLE_FILE_UPLOAD_RESPONSE = {
    "id": "file-new-123",
    "name": "test_file",
    "type": "runData",
}


# =============================================================================
# Mock Response Helper
# =============================================================================


class MockResponse:
    """Mock HTTP response object."""

    def __init__(
        self,
        json_data: Any = None,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        text: str = "",
        content: bytes = b"",
    ):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers or {}
        self.text = text
        self.content = content
        self.ok = 200 <= status_code < 300

    def json(self):
        if self.json_data is None:
            raise ValueError("No JSON data")
        return self.json_data

    def raise_for_status(self):
        if not self.ok:
            raise Exception(f"HTTP {self.status_code}")


# =============================================================================
# Mock API Request Handler
# =============================================================================


class MockAPIHandler:
    """Handles mock API requests and returns appropriate responses."""

    def __init__(self):
        self.call_history: list[dict[str, Any]] = []
        self.products: dict[str, dict] = {}
        self.variables: dict[str, dict] = {}
        self.experiments: dict[str, dict] = {}
        self.recipes: dict[str, dict] = {}
        self.projects: dict[str, dict] = {}
        self.models: dict[str, dict] = {}
        self.datasets: dict[str, dict] = {}
        self.files: dict[str, dict] = {}

        # Pre-populate with sample data
        self.products[SAMPLE_PRODUCT["id"]] = SAMPLE_PRODUCT
        self.variables[SAMPLE_VARIABLE_NUMERIC["id"]] = SAMPLE_VARIABLE_NUMERIC
        self.variables[SAMPLE_VARIABLE_CATEGORICAL["id"]] = SAMPLE_VARIABLE_CATEGORICAL
        self.variables[SAMPLE_VARIABLE_LOGICAL["id"]] = SAMPLE_VARIABLE_LOGICAL
        self.variables[SAMPLE_VARIABLE_FLOW["id"]] = SAMPLE_VARIABLE_FLOW
        self.variables[SAMPLE_VARIABLE_SPECTRUM["id"]] = SAMPLE_VARIABLE_SPECTRUM
        self.experiments[SAMPLE_EXPERIMENT["id"]] = SAMPLE_EXPERIMENT
        self.recipes[SAMPLE_RECIPE["id"]] = SAMPLE_RECIPE
        self.projects[SAMPLE_PROJECT["id"]] = SAMPLE_PROJECT
        self.projects[SAMPLE_PROJECT_SPECTROSCOPY["id"]] = SAMPLE_PROJECT_SPECTROSCOPY
        # Order matters! Tests use models[0], so historical must come first
        self.models[SAMPLE_MODEL_HISTORICAL["id"]] = SAMPLE_MODEL_HISTORICAL
        self.models[SAMPLE_MODEL["id"]] = SAMPLE_MODEL
        self.models[SAMPLE_MODEL_SPECTROSCOPY["id"]] = SAMPLE_MODEL_SPECTROSCOPY
        self.datasets[SAMPLE_DATASET["id"]] = SAMPLE_DATASET

    def handle_request(self, method: str, url: str, **kwargs) -> MockResponse:
        """Route request to appropriate handler based on URL and method."""
        self.call_history.append({"method": method, "url": url, "kwargs": kwargs})

        # Parse query params from URL
        from urllib.parse import parse_qs, urlparse

        parsed_url = urlparse(url)
        query_params = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}
        kwargs["params"] = query_params

        # Products
        if "/products" in url and method == "GET":
            return self._handle_list_products(kwargs)
        elif "/products" in url and method == "POST":
            return self._handle_create_product(kwargs)

        # Variables
        elif "/variables" in url and method == "GET":
            return self._handle_list_variables(kwargs)
        elif "/variables" in url and method == "POST":
            return self._handle_create_variable(kwargs)

        # Experiments
        elif "/experiments/" in url and method == "GET":
            return self._handle_get_experiment(url)
        elif "/experiments" in url and method == "GET":
            return self._handle_list_experiments(kwargs)
        elif "/experiments" in url and method == "POST":
            return self._handle_create_experiment(kwargs)

        # Recipes
        elif "/recipes" in url and method == "GET":
            return self._handle_list_recipes(kwargs)
        elif "/recipes" in url and method == "POST":
            return self._handle_create_recipe(kwargs)

        # Projects
        elif "/projects" in url and method == "GET":
            return self._handle_list_projects(kwargs)

        # Models
        elif "/models" in url and method == "GET":
            return self._handle_list_models(kwargs)
        elif "/predict" in url and method == "POST":
            return self._handle_predict(url, kwargs)

        # Groups
        elif "/groups" in url and method == "GET":
            return self._handle_get_groups()

        # Datasets
        elif "/datasets" in url and method == "GET":
            return self._handle_list_datasets(kwargs)

        # Files
        elif "/files" in url and "/data" in url and method == "GET":
            return self._handle_get_file_data(url)
        elif "/files" in url and "/data" in url and method == "PUT":
            return self._handle_put_file_data(url, kwargs)
        elif "/files" in url and method == "POST":
            return self._handle_create_file(kwargs)

        # Default
        return MockResponse(json_data={"error": "Not found"}, status_code=404)

    def _handle_list_products(self, kwargs) -> MockResponse:
        products = list(self.products.values())
        params = kwargs.get("params", {})
        if "filterBy[code]" in params:
            products = [p for p in products if params["filterBy[code]"] in p["code"]]
        return MockResponse(json_data=products)

    def _handle_create_product(self, kwargs) -> MockResponse:
        data = kwargs.get("json", {})
        product_id = f"prod-{len(self.products) + 1}"
        product = {
            "id": product_id,
            "code": data.get("code"),
            "name": data.get("name"),
            "description": data.get("description", ""),
            "processFormat": data.get("processFormat", "mammalian"),
        }
        self.products[product_id] = product
        return MockResponse(json_data=product, status_code=201)

    def _handle_list_variables(self, kwargs) -> MockResponse:
        variables = list(self.variables.values())
        params = kwargs.get("params", {})

        # Handle filterBy[code] parameter
        if "filterBy[code]" in params:
            code_filter = params["filterBy[code]"]
            variables = [v for v in variables if code_filter in v["code"]]

        # Handle filterBy[group._id] parameter (by group name)
        if "filterBy[group._id]" in params:
            group_id = params["filterBy[group._id]"]
            variables = [
                v for v in variables if v.get("group", {}).get("id") == group_id
            ]

        # Handle filterBy[variant] parameter
        if "filterBy[variant]" in params:
            variables = [
                v for v in variables if v["variant"] == params["filterBy[variant]"]
            ]

        return MockResponse(json_data=variables)

    def _handle_create_variable(self, kwargs) -> MockResponse:
        data = kwargs.get("json", {})
        var_id = f"var-{len(self.variables) + 1}"
        variable = {
            "id": var_id,
            "code": data.get("code"),
            "name": data.get("name"),
            "measurementUnit": data.get("measurementUnit"),
            "variableGroup": data.get("variableGroup"),
            "variant": data.get("variant"),
            "description": data.get("description", ""),
        }
        # Add variant-specific data
        variant = data.get("variant")
        if variant in data:
            variable[variant] = data[variant]
        self.variables[var_id] = variable
        return MockResponse(json_data=variable, status_code=201)

    def _handle_get_experiment(self, url) -> MockResponse:
        exp_id = url.split("/experiments/")[1].split("/")[0]
        if exp_id in self.experiments:
            return MockResponse(json_data=self.experiments[exp_id])
        return MockResponse(json_data={"error": "Not found"}, status_code=404)

    def _handle_list_experiments(self, kwargs) -> MockResponse:
        experiments = list(self.experiments.values())
        params = kwargs.get("params", {})
        if "name" in params:
            experiments = [e for e in experiments if params["name"] in e["name"]]
        if "product" in params:
            experiments = [
                e for e in experiments if e["product"]["id"] == params["product"]
            ]
        return MockResponse(json_data=experiments)

    def _handle_create_experiment(self, kwargs) -> MockResponse:
        data = kwargs.get("json", {})
        exp_id = f"exp-{len(self.experiments) + 1}"
        experiment = {
            "id": exp_id,
            "name": data.get("name"),
            "description": data.get("description", ""),
            "product": data.get("product"),
            "variables": data.get("variables", []),
            "processFormat": data.get("processFormat", "mammalian"),
            "variant": data.get("variant"),
            "instances": data.get("instances", []),
        }
        if "startTime" in data:
            experiment["startTime"] = data["startTime"]
        if "endTime" in data:
            experiment["endTime"] = data["endTime"]
        self.experiments[exp_id] = experiment
        return MockResponse(json_data=experiment, status_code=201)

    def _handle_list_recipes(self, kwargs) -> MockResponse:
        recipes = list(self.recipes.values())
        params = kwargs.get("params", {})
        if "name" in params:
            recipes = [r for r in recipes if params["name"] in r["name"]]
        return MockResponse(json_data=recipes)

    def _handle_create_recipe(self, kwargs) -> MockResponse:
        data = kwargs.get("json", {})
        recipe_id = f"recipe-{len(self.recipes) + 1}"
        recipe = {
            "id": recipe_id,
            "name": data.get("name"),
            "description": data.get("description", ""),
            "product": data.get("product"),
            "variables": data.get("variables", []),
            "duration": data.get("duration"),
            "instances": data.get("instances", []),
        }
        self.recipes[recipe_id] = recipe
        return MockResponse(json_data=recipe, status_code=201)

    def _handle_list_projects(self, kwargs) -> MockResponse:
        projects = list(self.projects.values())
        params = kwargs.get("params", {})
        if "name" in params:
            projects = [p for p in projects if params["name"] in p["name"]]
        if "projectType" in params:
            projects = [
                p for p in projects if p["projectType"] == params["projectType"]
            ]
        # Filter by processUnitId (sent by client)
        if "filterBy[processUnitId]" in params:
            unit_id = params["filterBy[processUnitId]"]
            projects = [p for p in projects if p.get("processUnitId") == unit_id]
        return MockResponse(json_data=projects)

    def _handle_list_models(self, kwargs) -> MockResponse:
        models = list(self.models.values())
        params = kwargs.get("params", {})
        if "name" in params:
            models = [m for m in models if params["name"] in m["name"]]
        # Filter by project ID (sent by client as filterBy[projectId])
        if "filterBy[projectId]" in params:
            project_id = params["filterBy[projectId]"]
            models = [m for m in models if m["project"]["id"] == project_id]
        # Note: modelType is already set correctly in the model data
        return MockResponse(json_data=models)

    def _handle_get_groups(self) -> MockResponse:
        """Return available variable groups"""
        groups = [
            {"id": "group-x", "code": "X_VARS", "name": "X Variables"},
            {"id": "group-y", "code": "Y_VARS", "name": "Y Variables"},
            {"id": "group-z", "code": "Z_VARS", "name": "Z Variables"},
            {"id": "group-flows", "code": "FLOWS", "name": "Flows"},
        ]
        return MockResponse(json_data=groups)

    def _handle_predict(self, url, kwargs) -> MockResponse:
        return MockResponse(json_data=SAMPLE_PREDICTION_OUTPUT, status_code=200)

    def _handle_list_datasets(self, kwargs) -> MockResponse:
        datasets = list(self.datasets.values())
        params = kwargs.get("params", {})
        if "project" in params:
            datasets = [d for d in datasets if d["project"]["id"] == params["project"]]
        return MockResponse(json_data=datasets)

    def _handle_get_file_data(self, url) -> MockResponse:
        file_id = url.split("/files/")[1].split("/")[0]
        # Check if file exists
        if file_id in self.files:
            file_info = self.files[file_id]
            # Return stored data if available, otherwise sample data
            data = file_info.get("data", SAMPLE_EXPERIMENT_DATA)
            return MockResponse(
                json_data=data,
                headers={"content-type": "application/json"},
            )
        elif file_id in ["file-123", "file-456"]:
            # Known static files
            return MockResponse(
                json_data=SAMPLE_EXPERIMENT_DATA,
                headers={"content-type": "application/json"},
            )
        return MockResponse(json_data={"error": "Not found"}, status_code=404)

    def _handle_create_file(self, kwargs) -> MockResponse:
        data = kwargs.get("json", {})
        file_id = f"file-{len(self.files) + 1}"
        file_data = {
            "id": file_id,
            "name": data.get("name"),
            "type": data.get("type"),
            "data": None,  # Data uploaded separately via PUT
        }
        self.files[file_id] = file_data
        return MockResponse(json_data=file_data, status_code=201)

    def _handle_put_file_data(self, url, kwargs) -> MockResponse:
        """Store file data from PUT request"""
        file_id = url.split("/files/")[1].split("/")[0]
        if file_id in self.files:
            # Store the uploaded data
            self.files[file_id]["data"] = kwargs.get("json", kwargs.get("data", {}))
        return MockResponse(status_code=204)


# =============================================================================
# Pytest Fixtures
# =============================================================================


@pytest.fixture
def mock_api():
    """Create a mock API handler for testing."""
    return MockAPIHandler()


@pytest.fixture
def mock_requests(mock_api):
    """Patch requests library to use mock API."""
    with patch("requests.Session.request") as mock_request:
        mock_request.side_effect = (
            lambda method, url, **kwargs: mock_api.handle_request(method, url, **kwargs)
        )
        yield mock_request


@pytest.fixture
def client(mock_requests):
    """Create a DataHowLabClient with mocked requests."""
    from dhl_sdk import DataHowLabClient

    return DataHowLabClient(
        api_key="test-api-key", base_url="https://test.datahowlab.ch", timeout=30.0
    )


@pytest.fixture
def sample_product():
    """Return sample product data."""
    return SAMPLE_PRODUCT.copy()


@pytest.fixture
def sample_variable_numeric():
    """Return sample numeric variable data."""
    return SAMPLE_VARIABLE_NUMERIC.copy()


@pytest.fixture
def sample_variable_categorical():
    """Return sample categorical variable data."""
    return SAMPLE_VARIABLE_CATEGORICAL.copy()


@pytest.fixture
def sample_experiment():
    """Return sample experiment data."""
    return SAMPLE_EXPERIMENT.copy()


@pytest.fixture
def sample_recipe():
    """Return sample recipe data."""
    return SAMPLE_RECIPE.copy()


@pytest.fixture
def sample_project():
    """Return sample project data."""
    return SAMPLE_PROJECT.copy()


@pytest.fixture
def sample_model():
    """Return sample model data."""
    return SAMPLE_MODEL.copy()

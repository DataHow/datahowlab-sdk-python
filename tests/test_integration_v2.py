"""Integration tests for DataHowLabClient v2 with mocked API."""

from datetime import datetime

import pytest
from pydantic import ValidationError as PydanticValidationError

from dhl_sdk import (
    CategoricalVariable,
    DataHowLabClient,
    ExperimentData,
    FlowReference,
    FlowVariable,
    HistoricalPredictionInput,
    LogicalVariable,
    NumericVariable,
    PropagationPredictionInput,
    SpectraData,
    SpectraExperimentData,
    SpectraPredictionInput,
    SpectrumAxis,
    SpectrumVariable,
    TimeseriesData,
    ValidationError,
)

# =============================================================================
# Product Tests
# =============================================================================


def test_create_product(client):
    """Test product creation workflow."""
    product = client.create_product(
        code="TEST1",
        name="Test Product",
        description="A test product",
        process_format="mammalian",
    )

    assert product.id is not None
    assert product.code == "TEST1"
    assert product.name == "Test Product"
    assert product.description == "A test product"
    assert product.process_format == "mammalian"


def test_list_products(client):
    """Test product listing."""
    products = client.list_products()
    assert len(products) >= 1
    assert all(hasattr(p, "id") for p in products)
    assert all(hasattr(p, "code") for p in products)


def test_list_products_with_filter(client):
    """Test product listing with code filter."""
    products = client.list_products(code="PROD1")
    assert len(products) >= 1
    assert all("PROD1" in p.code for p in products)


# =============================================================================
# Variable Tests - All Types
# =============================================================================


def test_create_numeric_variable(client):
    """Test numeric variable creation."""
    variable = client.create_variable(
        code="TEMP",
        name="Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100, default=25, interpolation="linear"),
        description="Process temperature",
    )

    assert variable.id is not None
    assert variable.code == "TEMP"
    assert variable.type.kind == "numeric"
    assert variable.type.min == 0
    assert variable.type.max == 100


def test_create_categorical_variable(client):
    """Test categorical variable creation."""
    variable = client.create_variable(
        code="PHASE",
        name="Process Phase",
        unit="n",
        group="Z Variables",
        type=CategoricalVariable(
            categories=["Init", "Growth", "Production", "Harvest"],
            strict=True,
            default="Init",
        ),
    )

    assert variable.id is not None
    assert variable.code == "PHASE"
    assert variable.type.kind == "categorical"
    assert len(variable.type.categories) == 4


def test_create_logical_variable(client):
    """Test logical variable creation."""
    variable = client.create_variable(
        code="PUMP_ON",
        name="Pump Status",
        unit="bool",
        group="X Variables",
        type=LogicalVariable(default=False),
    )

    assert variable.id is not None
    assert variable.code == "PUMP_ON"
    assert variable.type.kind == "logical"


def test_create_flow_variable(client):
    """Test flow variable creation."""
    variable = client.create_variable(
        code="FEED",
        name="Feed Flow",
        unit="L/h",
        group="Flows",
        type=FlowVariable(
            flow_type="conti",
            references=[
                FlowReference(measurement="FLOW_RATE", concentration="FEED_CONC")
            ],
            step_size=60,
        ),
    )

    assert variable.id is not None
    assert variable.code == "FEED"
    assert variable.type.kind == "flow"
    assert variable.type.flow_type == "conti"


def test_create_spectrum_variable(client):
    """Test spectrum variable creation."""
    variable = client.create_variable(
        code="SPEC1",
        name="Spectrum",
        unit="AU",
        group="Y Variables",
        type=SpectrumVariable(
            x_axis=SpectrumAxis(dimension=100, unit="nm", min=400, max=700),
            y_axis=SpectrumAxis(label="Absorbance"),
        ),
    )

    assert variable.id is not None
    assert variable.code == "SPEC1"
    assert variable.type.kind == "spectrum"
    assert variable.type.x_axis.dimension == 100


def test_list_variables(client):
    """Test variable listing."""
    variables = client.list_variables()
    assert len(variables) >= 1
    assert all(hasattr(v, "id") for v in variables)
    assert all(hasattr(v, "type") for v in variables)


def test_list_variables_with_filters(client):
    """Test variable listing with filters."""
    # Filter by code
    variables = client.list_variables(code="TEMP")
    assert len(variables) >= 1
    assert all("TEMP" in v.code for v in variables)

    # Filter by group
    variables = client.list_variables(group="X Variables")
    assert len(variables) >= 1
    assert all(v.group == "X Variables" for v in variables)


def test_list_variables_parses_all_types(client):
    """Test that list_variables correctly parses all variable types."""
    variables = client.list_variables()

    # Find each type
    numeric = next((v for v in variables if v.type.kind == "numeric"), None)
    categorical = next((v for v in variables if v.type.kind == "categorical"), None)
    logical = next((v for v in variables if v.type.kind == "logical"), None)
    flow = next((v for v in variables if v.type.kind == "flow"), None)
    spectrum = next((v for v in variables if v.type.kind == "spectrum"), None)

    # Verify parsing
    assert numeric is not None
    assert numeric.type.min == 0
    assert numeric.type.max == 100

    assert categorical is not None
    assert len(categorical.type.categories) == 4

    assert logical is not None
    assert logical.type.default is False

    assert flow is not None
    assert flow.type.flow_type == "conti"
    assert len(flow.type.references) == 1

    assert spectrum is not None
    assert spectrum.type.x_axis.dimension == 100


# =============================================================================
# Experiment Tests
# =============================================================================


def test_create_experiment_standard(client, sample_product):
    """Test standard time-series experiment creation."""
    # First get product and variables
    products = client.list_products(code="PROD1")
    product = products[0]

    variables = client.list_variables()
    var1 = next(v for v in variables if v.code == "TEMP")
    var2 = next(v for v in variables if v.code == "PHASE")

    experiment = client.create_experiment(
        name="Test Experiment",
        description="A test experiment",
        product=product,
        variables=[var1, var2],
        data=ExperimentData(
            variant="run",
            start_time=datetime(2025, 1, 1, 0, 0, 0),
            end_time=datetime(2025, 1, 2, 0, 0, 0),
            timeseries={
                "TEMP": TimeseriesData(
                    timestamps=[1735689600, 1735776000], values=[25.5, 26.0]
                ),
                "PHASE": TimeseriesData(timestamps=[1735689600], values=["Init"]),
            },
        ),
    )

    assert experiment.id is not None
    assert experiment.name == "Test Experiment"
    assert experiment.variant == "run"


def test_create_experiment_with_id_strings(client):
    """Test experiment creation using ID strings instead of objects."""
    experiment = client.create_experiment(
        name="Test Experiment 2",
        product="prod-123",  # ID string
        variables=["var-123", "var-456"],  # ID strings
        data=ExperimentData(
            variant="run",
            start_time=datetime(2025, 1, 1),
            end_time=datetime(2025, 1, 2),
            timeseries={"TEMP": TimeseriesData(timestamps=[1735689600], values=[25.5])},
        ),
    )

    assert experiment.id is not None


def test_create_spectra_experiment(client):
    """Test spectra experiment creation."""
    products = client.list_products()
    product = products[0]

    variables = client.list_variables()
    spec_var = next(v for v in variables if v.type.kind == "spectrum")
    temp_var = next(v for v in variables if v.code == "TEMP")

    experiment = client.create_experiment(
        name="Spectra Experiment",
        product=product,
        variables=[spec_var, temp_var],
        data=SpectraExperimentData(
            variant="run",
            spectra=SpectraData(
                timestamps=[1, 2, 3],
                values=[
                    [1.0, 1.1, 1.2, 1.3, 1.4],
                    [1.1, 1.2, 1.3, 1.4, 1.5],
                    [1.0, 1.1, 1.2, 1.3, 1.4],
                ],
            ),
            inputs={"TEMP": [25.0, 26.0, 25.5]},
        ),
    )

    assert experiment.id is not None
    assert experiment.name == "Spectra Experiment"


def test_list_experiments(client):
    """Test experiment listing."""
    experiments = client.list_experiments()
    assert len(experiments) >= 1
    assert all(hasattr(e, "id") for e in experiments)


def test_list_experiments_with_filters(client):
    """Test experiment listing with filters."""
    experiments = client.list_experiments(name="Test")
    assert len(experiments) >= 1
    assert all("Test" in e.name for e in experiments)


def test_get_experiment_data(client):
    """Test experiment data retrieval."""
    experiments = client.list_experiments()
    experiment = experiments[0]

    data = client.get_experiment_data(experiment)

    assert isinstance(data, dict)
    assert len(data) >= 1

    # Check structure
    for _var_code, var_data in data.items():
        assert "timestamps" in var_data
        assert "values" in var_data
        assert len(var_data["timestamps"]) == len(var_data["values"])


def test_get_experiment_data_with_id_string(client):
    """Test experiment data retrieval using ID string."""
    data = client.get_experiment_data("exp-123")
    assert isinstance(data, dict)


# =============================================================================
# Recipe Tests
# =============================================================================


def test_create_recipe(client):
    """Test recipe creation."""
    products = client.list_products()
    product = products[0]

    variables = client.list_variables()
    var = next(v for v in variables if v.code == "TEMP")

    recipe = client.create_recipe(
        name="Test Recipe",
        description="A test recipe",
        product=product,
        variables=[var],
        duration=3600,
        data={
            "TEMP": TimeseriesData(
                timestamps=[0, 1800, 3600], values=[25.0, 26.0, 25.5]
            )
        },
    )

    assert recipe.id is not None
    assert recipe.name == "Test Recipe"
    assert recipe.duration == 3600


def test_list_recipes(client):
    """Test recipe listing."""
    recipes = client.list_recipes()
    assert len(recipes) >= 1
    assert all(hasattr(r, "id") for r in recipes)


def test_list_recipes_with_filters(client):
    """Test recipe listing with filters."""
    recipes = client.list_recipes(name="Test")
    assert len(recipes) >= 1


# =============================================================================
# Project, Model, and Dataset Tests
# =============================================================================


def test_list_projects(client):
    """Test project listing."""
    projects = client.list_projects()
    assert len(projects) >= 1
    assert all(hasattr(p, "id") for p in projects)


def test_list_projects_with_filters(client):
    """Test project listing with filters."""
    projects = client.list_projects(project_type="spectroscopy")
    assert len(projects) >= 1
    assert all(p.project_type == "spectroscopy" for p in projects)


def test_list_models(client):
    """Test model listing."""
    projects = client.list_projects()
    project = projects[0]

    models = client.list_models(project)
    assert len(models) >= 1
    assert all(hasattr(m, "id") for m in models)


def test_list_models_with_filters(client):
    """Test model listing with filters."""
    projects = client.list_projects()
    project = projects[0]

    models = client.list_models(project, name="Test")
    assert len(models) >= 1


def test_model_is_ready_property(client):
    """Test Model.is_ready property."""
    projects = client.list_projects()
    project = projects[0]

    models = client.list_models(project)
    model = models[0]

    assert model.is_ready is True  # Sample model has status="ready"


def test_list_datasets(client):
    """Test dataset listing."""
    projects = client.list_projects()
    project = projects[0]

    datasets = client.list_datasets(project)
    assert len(datasets) >= 1
    assert all(hasattr(d, "id") for d in datasets)


# =============================================================================
# Prediction Tests
# =============================================================================


def test_predict_spectra(client):
    """Test spectra model prediction."""
    projects = client.list_projects(project_type="spectroscopy")
    project = projects[0]

    models = client.list_models(project)
    model = models[0]

    predictions = model.predict(
        client,
        SpectraPredictionInput(
            spectra=[[1.0, 1.1, 1.2, 1.3, 1.4], [1.1, 1.2, 1.3, 1.4, 1.5]],
            inputs={"INPUT1": [42.0, 43.0]},
        ),
    )

    assert predictions.outputs is not None
    assert "OUTPUT1" in predictions.outputs
    assert len(predictions.outputs["OUTPUT1"]) == 2


def test_predict_propagation(client):
    """Test cultivation propagation model prediction."""
    projects = client.list_projects()
    project = projects[0]

    models = client.list_models(project)
    # Find propagation model
    model = next((m for m in models if m.model_type == "propagation"), models[0])

    predictions = model.predict(
        client,
        PropagationPredictionInput(
            timestamps=[0, 24, 48, 72],
            unit="h",
            inputs={"INITIAL_DENSITY": [1.0e6], "FEED_RATE": [0, 2.0, 2.0, 2.0]},
            confidence=0.8,
        ),
    )

    assert predictions.outputs is not None


def test_predict_historical(client):
    """Test cultivation historical model prediction."""
    projects = client.list_projects()
    project = projects[0]

    models = client.list_models(project)
    # Find historical model
    model = next((m for m in models if m.model_type == "historical"), models[0])

    predictions = model.predict(
        client,
        HistoricalPredictionInput(
            timestamps=[86400, 172800, 259200],
            steps=[0, 1, 2],
            unit="s",
            inputs={"VAR1": [42.0], "VAR2": [0.3], "VAR3": [0, 2, 3]},
            confidence=0.8,
        ),
    )

    assert predictions.outputs is not None


# =============================================================================
# Error Handling Tests
# =============================================================================


def test_validation_error_on_invalid_product_code(client):
    """Test that validation error is raised for invalid product code."""
    with pytest.raises(ValidationError):
        client.create_product(code="", name="Test")


def test_validation_error_on_invalid_timestamps(client):
    """Test that validation error is raised for invalid timestamps."""
    with pytest.raises(PydanticValidationError, match="sorted"):
        TimeseriesData(timestamps=[3, 1, 2], values=[1.0, 2.0, 3.0])


def test_validation_error_on_mismatched_lengths(client):
    """Test validation error for mismatched timestamp/value lengths."""
    with pytest.raises(PydanticValidationError, match="must match"):
        TimeseriesData(timestamps=[1, 2, 3], values=[1.0, 2.0])


def test_validation_error_on_negative_timestamps(client):
    """Test validation error for negative timestamps."""
    with pytest.raises(PydanticValidationError, match="non-negative"):
        TimeseriesData(timestamps=[1, -2, 3], values=[1.0, 2.0, 3.0])


# =============================================================================
# Full Workflow Integration Tests
# =============================================================================


def test_full_workflow_product_to_experiment(client):
    """Test complete workflow: create product, variables, and experiment."""
    # 1. Create product
    product = client.create_product(
        code="WORK1", name="Workflow Product", process_format="mammalian"
    )
    assert product.id is not None

    # 2. Create variables
    temp_var = client.create_variable(
        code="WTEMP",
        name="Workflow Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100),
    )
    assert temp_var.id is not None

    phase_var = client.create_variable(
        code="WPHASE",
        name="Workflow Phase",
        unit="n",
        group="Z Variables",
        type=CategoricalVariable(categories=["A", "B", "C"]),
    )
    assert phase_var.id is not None

    # 3. Create experiment
    experiment = client.create_experiment(
        name="Workflow Experiment",
        product=product,
        variables=[temp_var, phase_var],
        data=ExperimentData(
            variant="run",
            start_time=datetime(2025, 1, 1),
            end_time=datetime(2025, 1, 3),
            timeseries={
                "WTEMP": TimeseriesData(
                    timestamps=[1735689600, 1735776000], values=[25.0, 26.0]
                ),
                "WPHASE": TimeseriesData(timestamps=[1735689600], values=["A"]),
            },
        ),
    )
    assert experiment.id is not None

    # 4. Retrieve experiment data
    data = client.get_experiment_data(experiment)
    assert "WTEMP" in data or "TEMP" in data  # Mock returns TEMP


def test_full_workflow_recipe_creation(client):
    """Test complete workflow for recipe creation."""
    # 1. Get existing product and variable
    products = client.list_products()
    product = products[0]

    variables = client.list_variables()
    var = variables[0]

    # 2. Create recipe
    recipe = client.create_recipe(
        name="Workflow Recipe",
        product=product,
        variables=[var],
        duration=7200,
        data={
            var.code: TimeseriesData(
                timestamps=[0, 3600, 7200], values=[20.0, 25.0, 20.0]
            )
        },
    )
    assert recipe.id is not None

    # 3. List and verify
    recipes = client.list_recipes(name="Workflow")
    assert len(recipes) >= 1


def test_full_workflow_prediction(client):
    """Test complete workflow for model prediction."""
    # 1. List projects - get spectroscopy project for spectra prediction
    projects = client.list_projects(project_type="spectroscopy")
    assert len(projects) >= 1
    project = projects[0]

    # 2. List models
    models = client.list_models(project)
    assert len(models) >= 1
    model = models[0]

    # 3. Check model is ready
    assert model.is_ready

    # 4. Make prediction
    predictions = model.predict(
        client,
        SpectraPredictionInput(spectra=[[1.0, 2.0, 3.0]], inputs={"INPUT1": [42.0]}),
    )
    assert predictions.outputs is not None
    assert predictions.metadata is not None


# =============================================================================
# Edge Cases and Robustness Tests
# =============================================================================


def test_empty_list_results(client, mock_api):
    """Test handling of empty list results."""
    # Clear all products
    mock_api.products.clear()

    products = client.list_products()
    assert products == []


def test_experiment_with_samples_variant(client):
    """Test experiment creation with samples variant."""
    products = client.list_products()
    product = products[0]

    variables = client.list_variables()
    var = variables[0]

    experiment = client.create_experiment(
        name="Samples Experiment",
        product=product,
        variables=[var],
        data=ExperimentData(
            variant="samples",
            timeseries={
                var.code: TimeseriesData(
                    timestamps=[1, 2, 3], values=[10.5, 11.2, 10.8]
                )
            },
        ),
    )

    assert experiment.id is not None
    assert experiment.variant == "samples"


def test_client_with_ssl_options():
    """Test client initialization with SSL options."""
    # Without mock (just test initialization)
    client1 = DataHowLabClient(
        api_key="test", base_url="https://test.com", verify_ssl=False
    )
    assert client1 is not None

    client2 = DataHowLabClient(
        api_key="test", base_url="https://test.com", verify_ssl="/path/to/cert.pem"
    )
    assert client2 is not None

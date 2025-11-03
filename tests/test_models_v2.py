"""Unit tests for dhl_sdk.models module."""

import pytest
from pydantic import ValidationError

from dhl_sdk.models import (
    Dataset,
    Experiment,
    Model,
    Product,
    Project,
    Recipe,
    Variable,
)
from dhl_sdk.types import (
    CategoricalVariable,
    FlowReference,
    FlowVariable,
    LogicalVariable,
    NumericVariable,
    SpectrumAxis,
    SpectrumVariable,
)

# =============================================================================
# Product Model Tests
# =============================================================================


def test_product_creation():
    """Test Product model creation."""
    product = Product(
        id="prod-123",
        code="PROD1",
        name="Test Product",
        description="A test product",
        process_format="mammalian",
    )
    assert product.id == "prod-123"
    assert product.code == "PROD1"
    assert product.name == "Test Product"
    assert product.process_format == "mammalian"


def test_product_code_validation():
    """Test Product code validation."""
    # Empty code should fail
    with pytest.raises(ValidationError):
        Product(code="", name="Test")

    # Code too long should fail
    with pytest.raises(ValidationError):
        Product(code="VERYLONGCODE123", name="Test")

    # Valid code should work
    product = Product(code="VALID", name="Test")
    assert product.code == "VALID"


def test_product_code_uppercase():
    """Test that Product code is converted to uppercase."""
    product = Product(code="prod1", name="Test")
    assert product.code == "PROD1"


def test_product_code_stripped():
    """Test that Product code is stripped of whitespace."""
    product = Product(code="  PROD1  ", name="Test")
    assert product.code == "PROD1"


def test_product_defaults():
    """Test Product default values."""
    product = Product(code="TEST", name="Test Product")
    assert product.description == ""
    assert product.process_format == "mammalian"
    assert product.id is None


def test_product_process_format_validation():
    """Test Product process_format validation."""
    # Valid formats
    product1 = Product(code="TEST", name="Test", process_format="mammalian")
    assert product1.process_format == "mammalian"

    product2 = Product(code="TEST", name="Test", process_format="microbial")
    assert product2.process_format == "microbial"

    # Invalid format should fail
    with pytest.raises(ValidationError):
        Product(code="TEST", name="Test", process_format="invalid")


# =============================================================================
# Variable Model Tests
# =============================================================================


def test_variable_creation_numeric():
    """Test Variable creation with numeric type."""
    variable = Variable(
        id="var-123",
        code="TEMP",
        name="Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100, default=25),
        description="Process temperature",
    )
    assert variable.id == "var-123"
    assert variable.code == "TEMP"
    assert variable.type.kind == "numeric"
    assert variable.type.min == 0


def test_variable_creation_categorical():
    """Test Variable creation with categorical type."""
    variable = Variable(
        code="PHASE",
        name="Phase",
        unit="n",
        group="Z Variables",
        type=CategoricalVariable(categories=["A", "B", "C"]),
    )
    assert variable.type.kind == "categorical"
    assert len(variable.type.categories) == 3


def test_variable_creation_logical():
    """Test Variable creation with logical type."""
    variable = Variable(
        code="PUMP",
        name="Pump",
        unit="bool",
        group="X Variables",
        type=LogicalVariable(),
    )
    assert variable.type.kind == "logical"


def test_variable_creation_flow():
    """Test Variable creation with flow type."""
    variable = Variable(
        code="FEED",
        name="Feed",
        unit="L/h",
        group="Flows",
        type=FlowVariable(
            flow_type="conti",
            references=[FlowReference(measurement="FLOW_RATE")],
            step_size=60,
        ),
    )
    assert variable.type.kind == "flow"
    assert variable.type.flow_type == "conti"


def test_variable_creation_spectrum():
    """Test Variable creation with spectrum type."""
    variable = Variable(
        code="SPEC",
        name="Spectrum",
        unit="AU",
        group="Y Variables",
        type=SpectrumVariable(
            x_axis=SpectrumAxis(dimension=100), y_axis=SpectrumAxis()
        ),
    )
    assert variable.type.kind == "spectrum"
    assert variable.type.x_axis.dimension == 100


def test_variable_code_validation():
    """Test Variable code validation."""
    # Empty code should fail
    with pytest.raises(ValidationError):
        Variable(
            code="", name="Test", unit="U", group="X Variables", type=NumericVariable()
        )

    # Code too long should fail
    with pytest.raises(ValidationError):
        Variable(
            code="VERYLONGVARIABLECODE",
            name="Test",
            unit="U",
            group="X Variables",
            type=NumericVariable(),
        )


def test_variable_code_uppercase():
    """Test that Variable code is converted to uppercase."""
    variable = Variable(
        code="temp", name="Test", unit="U", group="X Variables", type=NumericVariable()
    )
    assert variable.code == "TEMP"


def test_variable_defaults():
    """Test Variable default values."""
    variable = Variable(
        code="TEST", name="Test", unit="U", group="X Variables", type=NumericVariable()
    )
    assert variable.description == ""
    assert variable.id is None


# =============================================================================
# Experiment Model Tests
# =============================================================================


def test_experiment_creation():
    """Test Experiment model creation."""
    experiment = Experiment(
        id="exp-123",
        name="Test Experiment",
        description="A test experiment",
        product="prod-123",
        variables=["var-123", "var-456"],
        process_format="mammalian",
        variant="run",
    )
    assert experiment.id == "exp-123"
    assert experiment.name == "Test Experiment"
    assert experiment.variant == "run"


def test_experiment_name_validation():
    """Test Experiment name validation."""
    # Empty name should fail
    with pytest.raises(ValidationError):
        Experiment(name="", product="prod-123", variables=[], variant="run")

    # Valid name should work
    experiment = Experiment(
        name="Valid Experiment", product="prod-123", variables=[], variant="run"
    )
    assert experiment.name == "Valid Experiment"


def test_experiment_defaults():
    """Test Experiment default values."""
    experiment = Experiment(
        name="Test", product="prod-123", variables=[], variant="run"
    )
    assert experiment.description == ""
    assert experiment.process_format == "mammalian"
    assert experiment.id is None


def test_experiment_variant_validation():
    """Test Experiment variant validation."""
    # Valid variants
    exp1 = Experiment(name="Test", product="prod-123", variables=[], variant="run")
    assert exp1.variant == "run"

    exp2 = Experiment(name="Test", product="prod-123", variables=[], variant="samples")
    assert exp2.variant == "samples"

    # Invalid variant should fail
    with pytest.raises(ValidationError):
        Experiment(name="Test", product="prod-123", variables=[], variant="invalid")


# =============================================================================
# Recipe Model Tests
# =============================================================================


def test_recipe_creation():
    """Test Recipe model creation."""
    recipe = Recipe(
        id="recipe-123",
        name="Test Recipe",
        description="A test recipe",
        product="prod-123",
        variables=["var-123"],
        duration=3600,
    )
    assert recipe.id == "recipe-123"
    assert recipe.name == "Test Recipe"
    assert recipe.duration == 3600


def test_recipe_name_validation():
    """Test Recipe name validation."""
    # Empty name should fail
    with pytest.raises(ValidationError):
        Recipe(name="", product="prod-123", variables=[])

    # Valid name should work
    recipe = Recipe(name="Valid Recipe", product="prod-123", variables=[])
    assert recipe.name == "Valid Recipe"


def test_recipe_defaults():
    """Test Recipe default values."""
    recipe = Recipe(name="Test", product="prod-123", variables=[])
    assert recipe.description == ""
    assert recipe.duration is None
    assert recipe.id is None


def test_recipe_duration_validation():
    """Test Recipe duration validation."""
    # Negative duration should fail
    with pytest.raises(ValidationError):
        Recipe(name="Test", product="prod-123", variables=[], duration=-100)

    # Zero duration should be valid
    recipe = Recipe(name="Test", product="prod-123", variables=[], duration=0)
    assert recipe.duration == 0

    # Positive duration should be valid
    recipe = Recipe(name="Test", product="prod-123", variables=[], duration=3600)
    assert recipe.duration == 3600


# =============================================================================
# Project Model Tests
# =============================================================================


def test_project_creation():
    """Test Project model creation."""
    project = Project(
        id="proj-123",
        name="Test Project",
        project_type="spectroscopy",
        process_format="mammalian",
        product="prod-123",
    )
    assert project.id == "proj-123"
    assert project.name == "Test Project"
    assert project.project_type == "spectroscopy"


def test_project_type_validation():
    """Test Project type validation."""
    # Valid types
    proj1 = Project(
        name="Test",
        project_type="spectroscopy",
        process_format="mammalian",
        product="prod-123",
    )
    assert proj1.project_type == "spectroscopy"

    proj2 = Project(
        name="Test",
        project_type="cultivation",
        process_format="mammalian",
        product="prod-123",
    )
    assert proj2.project_type == "cultivation"

    # Invalid type should fail
    with pytest.raises(ValidationError):
        Project(
            name="Test",
            project_type="invalid",
            process_format="mammalian",
            product="prod-123",
        )


def test_project_process_format_validation():
    """Test Project process_format validation."""
    # Valid formats
    proj1 = Project(
        name="Test",
        project_type="spectroscopy",
        process_format="mammalian",
        product="prod-123",
    )
    assert proj1.process_format == "mammalian"

    proj2 = Project(
        name="Test",
        project_type="spectroscopy",
        process_format="microbial",
        product="prod-123",
    )
    assert proj2.process_format == "microbial"

    # Invalid format should fail
    with pytest.raises(ValidationError):
        Project(
            name="Test",
            project_type="spectroscopy",
            process_format="invalid",
            product="prod-123",
        )


# =============================================================================
# Model Model Tests
# =============================================================================


def test_model_creation():
    """Test Model model creation."""
    model = Model(
        id="model-123",
        name="Test Model",
        status="ready",
        model_type="spectra",
        project="proj-123",
    )
    assert model.id == "model-123"
    assert model.name == "Test Model"
    assert model.status == "ready"
    assert model.model_type == "spectra"


def test_model_is_ready_property():
    """Test Model is_ready property."""
    # Ready model
    model1 = Model(
        name="Test", status="ready", model_type="spectra", project="proj-123"
    )
    assert model1.is_ready is True

    # Not ready model
    model2 = Model(
        name="Test", status="training", model_type="spectra", project="proj-123"
    )
    assert model2.is_ready is False

    # Failed model
    model3 = Model(
        name="Test", status="failed", model_type="spectra", project="proj-123"
    )
    assert model3.is_ready is False


def test_model_type_validation():
    """Test Model type validation."""
    # Valid types
    model1 = Model(
        name="Test", status="ready", model_type="spectra", project="proj-123"
    )
    assert model1.model_type == "spectra"

    model2 = Model(
        name="Test", status="ready", model_type="propagation", project="proj-123"
    )
    assert model2.model_type == "propagation"

    model3 = Model(
        name="Test", status="ready", model_type="historical", project="proj-123"
    )
    assert model3.model_type == "historical"

    # Invalid type should fail
    with pytest.raises(ValidationError):
        Model(name="Test", status="ready", model_type="invalid", project="proj-123")


# =============================================================================
# Dataset Model Tests
# =============================================================================


def test_dataset_creation():
    """Test Dataset model creation."""
    dataset = Dataset(id="dataset-123", name="Test Dataset", project="proj-123")
    assert dataset.id == "dataset-123"
    assert dataset.name == "Test Dataset"
    assert dataset.project == "proj-123"


def test_dataset_name_validation():
    """Test Dataset name validation."""
    # Empty name should fail
    with pytest.raises(ValidationError):
        Dataset(name="", project="proj-123")

    # Valid name should work
    dataset = Dataset(name="Valid Dataset", project="proj-123")
    assert dataset.name == "Valid Dataset"


def test_dataset_defaults():
    """Test Dataset default values."""
    dataset = Dataset(name="Test", project="proj-123")
    assert dataset.id is None


# =============================================================================
# Model Serialization Tests
# =============================================================================


def test_product_to_dict():
    """Test Product model_dump()."""
    product = Product(
        id="prod-123",
        code="PROD1",
        name="Test Product",
        description="Test",
        process_format="mammalian",
    )
    data = product.model_dump(exclude_none=True)
    assert data["id"] == "prod-123"
    assert data["code"] == "PROD1"


def test_variable_to_dict():
    """Test Variable model_dump()."""
    variable = Variable(
        id="var-123",
        code="TEMP",
        name="Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100),
    )
    data = variable.model_dump(exclude_none=True)
    assert data["id"] == "var-123"
    assert data["type"]["kind"] == "numeric"


def test_experiment_to_dict():
    """Test Experiment model_dump()."""
    experiment = Experiment(
        id="exp-123",
        name="Test Experiment",
        product="prod-123",
        variables=["var-123"],
        variant="run",
    )
    data = experiment.model_dump(exclude_none=True)
    assert data["id"] == "exp-123"
    assert data["variant"] == "run"


# =============================================================================
# Model Comparison Tests
# =============================================================================


def test_product_equality():
    """Test Product equality comparison."""
    prod1 = Product(id="prod-123", code="PROD1", name="Test")
    prod2 = Product(id="prod-123", code="PROD1", name="Test")
    prod3 = Product(id="prod-456", code="PROD1", name="Test")

    assert prod1 == prod2
    assert prod1 != prod3


def test_variable_equality():
    """Test Variable equality comparison."""
    var1 = Variable(
        id="var-123",
        code="TEMP",
        name="Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100),
    )
    var2 = Variable(
        id="var-123",
        code="TEMP",
        name="Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100),
    )
    var3 = Variable(
        id="var-456",
        code="TEMP",
        name="Temperature",
        unit="°C",
        group="X Variables",
        type=NumericVariable(min=0, max=100),
    )

    assert var1 == var2
    assert var1 != var3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

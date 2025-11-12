import unittest
from unittest.mock import Mock

from openapi_client.models.categorical_scalar import CategoricalScalar
from openapi_client.models.logical_scalar import LogicalScalar
from openapi_client.models.model_experiment import ModelExperiment as OpenAPIModelExperiment
from openapi_client.models.numerical_scalar import NumericalScalar
from openapi_client.models.numerical_time_series import NumericalTimeSeries
from openapi_client.models.scalars_data import ScalarsData
from openapi_client.models.tabularized_data_model_output import TabularizedDataModelOutput
from openapi_client.models.tabularized_experiment_data import TabularizedExperimentData
from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData

from dhl_sdk.entities.model import Model
from dhl_sdk.entities.model_experiment import ModelExperiment
from tests.entities._fixtures import (
    create_model,
    create_model_experiment,
    create_model_variable,
    create_product,
    EXPERIMENT_ID,
    MODEL_ID,
    PRODUCT_ID,
    VAR_1_ID,
    VAR_2_ID,
    VAR_3_ID,
)


class TestModelExperiment(unittest.TestCase):
    api_model_experiment: OpenAPIModelExperiment
    model: Model

    def setUp(self):
        self.api_model_experiment = create_model_experiment(
            id=EXPERIMENT_ID,
            displayName="Test Model Experiment",
            productId=PRODUCT_ID,
            description="A test model experiment",
        )
        api_model = create_model(id=MODEL_ID)
        mock_api = Mock()
        self.model = Model(api_model, mock_api)

    def test_init(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertIsNotNone(model_experiment)

    def test_str(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        result = str(model_experiment)
        self.assertEqual(result, "ModelExperiment(Test Model Experiment)")

    def test_id_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertEqual(model_experiment.id, EXPERIMENT_ID)

    def test_display_name_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertEqual(model_experiment.display_name, "Test Model Experiment")

    def test_product_id_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertEqual(model_experiment.product_id, PRODUCT_ID)

    def test_description_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertEqual(model_experiment.description, "A test model experiment")

    def test_start_time_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertIsNotNone(model_experiment.start_time)
        self.assertEqual(model_experiment.start_time, "2024-01-01T00:00:00Z")

    def test_start_time_property_none(self):
        mock_api = Mock()
        self.api_model_experiment.start_time = None
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertIsNone(model_experiment.start_time)

    def test_variant_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertIsNotNone(model_experiment.variant)
        self.assertEqual(model_experiment.variant, "run")

    def test_used_for_training_property(self):
        mock_api = Mock()
        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        self.assertIsNotNone(model_experiment.used_for_training)
        self.assertEqual(model_experiment.used_for_training, True)

    def test_tags_property(self):
        mock_api = Mock()
        api_model_experiment = create_model_experiment(tags={"batch": "B001", "status": "validated"})
        model_experiment = ModelExperiment(api_model_experiment, self.model, mock_api)
        tags = model_experiment.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(tags["batch"], "B001")
        self.assertEqual(tags["status"], "validated")

    def test_tags_property_empty(self):
        mock_api = Mock()
        api_model_experiment = create_model_experiment(tags=None)
        model_experiment = ModelExperiment(api_model_experiment, self.model, mock_api)
        tags = model_experiment.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_tags_property_empty_dict(self):
        mock_api = Mock()
        api_model_experiment = create_model_experiment(tags={})
        model_experiment = ModelExperiment(api_model_experiment, self.model, mock_api)
        tags = model_experiment.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_get_data(self):
        # Create mock tabularized data
        timeseries_data_1 = TabularizedTimeSeriesData(actual_instance=NumericalTimeSeries(values=[5.0, 6.0]))
        timeseries_data_2 = TabularizedTimeSeriesData(actual_instance=NumericalTimeSeries(values=[10.0, 11.0]))

        mock_data = TabularizedExperimentData(
            timestamps=[0, 3600],
            data={
                VAR_1_ID: TabularizedDataModelOutput(actual_instance=timeseries_data_1),
                VAR_2_ID: TabularizedDataModelOutput(actual_instance=timeseries_data_2),
            },
        )

        mock_api = Mock()
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.return_value = mock_data

        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        result = model_experiment.get_data()

        self.assertEqual(result, mock_data)
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.assert_called_once_with(
            model_id=MODEL_ID, experiment_id=EXPERIMENT_ID
        )

    def test_get_data_compat_timeseries_only(self):
        """Test get_data_compat with only timeseries variables (group X)."""
        from dhl_sdk.entities.model_variable import ModelVariable

        # Create mock timeseries data
        timeseries_data_1 = TabularizedTimeSeriesData(actual_instance=NumericalTimeSeries(values=[1.0, 2.0, 3.0]))
        timeseries_data_2 = TabularizedTimeSeriesData(actual_instance=NumericalTimeSeries(values=[10.0, 11.0, 12.0]))

        mock_tabularized_data = TabularizedExperimentData(
            timestamps=[0, 3600, 7200],
            data={
                VAR_1_ID: TabularizedDataModelOutput(actual_instance=timeseries_data_1),
                VAR_2_ID: TabularizedDataModelOutput(actual_instance=timeseries_data_2),
            },
        )

        # Create mock model variables with group X (timeseries)
        mock_var_1_api = create_model_variable(id=VAR_1_ID, code="A", group="X")
        mock_var_2_api = create_model_variable(id=VAR_2_ID, code="B", group="X")
        mock_var_1 = ModelVariable(mock_var_1_api)
        mock_var_2 = ModelVariable(mock_var_2_api)

        # Mock the model's get_variables method
        mock_model = Mock()
        mock_model.id = MODEL_ID
        mock_model.get_variables.return_value = [mock_var_1, mock_var_2]

        mock_api = Mock()
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.return_value = mock_tabularized_data

        model_experiment = ModelExperiment(self.api_model_experiment, mock_model, mock_api)
        result = model_experiment.get_data_compat()

        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("A", result)
        self.assertIn("B", result)

        # Timeseries variables should have timestamps from top-level
        self.assertEqual(result["A"], {"values": [1.0, 2.0, 3.0], "timestamps": [0, 3600, 7200]})
        self.assertEqual(result["B"], {"values": [10.0, 11.0, 12.0], "timestamps": [0, 3600, 7200]})

    def test_get_data_compat_scalars_only(self):
        """Test get_data_compat with only scalar variables (groups Y, Z)."""
        from dhl_sdk.entities.model_variable import ModelVariable

        # Create mock scalar data
        scalar_data_1 = ScalarsData(actual_instance=NumericalScalar(value=42.5))
        scalar_data_2 = ScalarsData(actual_instance=NumericalScalar(value=100.0))

        mock_tabularized_data = TabularizedExperimentData(
            timestamps=[0, 3600, 7200],  # Top-level timestamps (not used for scalars)
            data={
                VAR_1_ID: TabularizedDataModelOutput(actual_instance=scalar_data_1),
                VAR_2_ID: TabularizedDataModelOutput(actual_instance=scalar_data_2),
            },
        )

        # Create mock model variables with groups Z and Y (scalars)
        mock_var_1_api = create_model_variable(id=VAR_1_ID, code="ScalarZ", group="Z")
        mock_var_2_api = create_model_variable(id=VAR_2_ID, code="ScalarY", group="Y")
        mock_var_1 = ModelVariable(mock_var_1_api)
        mock_var_2 = ModelVariable(mock_var_2_api)

        # Mock the model's get_variables method
        mock_model = Mock()
        mock_model.id = MODEL_ID
        mock_model.get_variables.return_value = [mock_var_1, mock_var_2]

        mock_api = Mock()
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.return_value = mock_tabularized_data

        model_experiment = ModelExperiment(self.api_model_experiment, mock_model, mock_api)
        result = model_experiment.get_data_compat()

        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("ScalarZ", result)
        self.assertIn("ScalarY", result)

        # Scalars should be converted to timeseries with timestamps=[0]
        self.assertEqual(result["ScalarZ"], {"values": [42.5], "timestamps": [0]})
        self.assertEqual(result["ScalarY"], {"values": [100.0], "timestamps": [0]})

    def test_get_data_compat_mixed_timeseries_and_scalars(self):
        """Test get_data_compat with mixed timeseries (X) and scalar (Y, Z) variables."""
        from dhl_sdk.entities.model_variable import ModelVariable

        # Create mock data with both timeseries and scalars
        timeseries_data = TabularizedTimeSeriesData(actual_instance=NumericalTimeSeries(values=[1.0, 2.0, 3.0]))
        scalar_data_z = ScalarsData(actual_instance=NumericalScalar(value=50.0))
        scalar_data_y = ScalarsData(actual_instance=NumericalScalar(value=75.0))

        mock_tabularized_data = TabularizedExperimentData(
            timestamps=[0, 3600, 7200],
            data={
                VAR_1_ID: TabularizedDataModelOutput(actual_instance=timeseries_data),
                VAR_2_ID: TabularizedDataModelOutput(actual_instance=scalar_data_z),
                VAR_3_ID: TabularizedDataModelOutput(actual_instance=scalar_data_y),
            },
        )

        # Create mock model variables with different groups
        mock_var_1_api = create_model_variable(id=VAR_1_ID, code="TimeseriesX", group="X")
        mock_var_2_api = create_model_variable(id=VAR_2_ID, code="ScalarZ", group="Z")
        mock_var_3_api = create_model_variable(id=VAR_3_ID, code="ScalarY", group="Y")
        mock_var_1 = ModelVariable(mock_var_1_api)
        mock_var_2 = ModelVariable(mock_var_2_api)
        mock_var_3 = ModelVariable(mock_var_3_api)

        # Mock the model's get_variables method
        mock_model = Mock()
        mock_model.id = MODEL_ID
        mock_model.get_variables.return_value = [mock_var_1, mock_var_2, mock_var_3]

        mock_api = Mock()
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.return_value = mock_tabularized_data

        model_experiment = ModelExperiment(self.api_model_experiment, mock_model, mock_api)
        result = model_experiment.get_data_compat()

        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("TimeseriesX", result)
        self.assertIn("ScalarZ", result)
        self.assertIn("ScalarY", result)

        # Timeseries should have timestamps from top-level
        self.assertEqual(result["TimeseriesX"], {"values": [1.0, 2.0, 3.0], "timestamps": [0, 3600, 7200]})

        # Scalars should be converted to timeseries with timestamps=[0]
        self.assertEqual(result["ScalarZ"], {"values": [50.0], "timestamps": [0]})
        self.assertEqual(result["ScalarY"], {"values": [75.0], "timestamps": [0]})

    def test_get_data_compat_categorical_scalar(self):
        """Test get_data_compat with categorical scalar."""
        from dhl_sdk.entities.model_variable import ModelVariable

        # Create mock categorical scalar data
        scalar_data = ScalarsData(actual_instance=CategoricalScalar(value="Category_A"))

        mock_tabularized_data = TabularizedExperimentData(
            timestamps=[0, 3600],
            data={
                VAR_1_ID: TabularizedDataModelOutput(actual_instance=scalar_data),
            },
        )

        # Create mock model variable
        mock_var_1_api = create_model_variable(id=VAR_1_ID, code="CatScalar", group="Y")
        mock_var_1 = ModelVariable(mock_var_1_api)

        # Mock the model's get_variables method
        mock_model = Mock()
        mock_model.id = MODEL_ID
        mock_model.get_variables.return_value = [mock_var_1]

        mock_api = Mock()
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.return_value = mock_tabularized_data

        model_experiment = ModelExperiment(self.api_model_experiment, mock_model, mock_api)
        result = model_experiment.get_data_compat()

        # Verify result
        self.assertIn("CatScalar", result)
        self.assertEqual(result["CatScalar"], {"values": ["Category_A"], "timestamps": [0]})

    def test_get_data_compat_logical_scalar(self):
        """Test get_data_compat with logical scalar."""
        from dhl_sdk.entities.model_variable import ModelVariable

        # Create mock logical scalar data
        scalar_data = ScalarsData(actual_instance=LogicalScalar(value=True))

        mock_tabularized_data = TabularizedExperimentData(
            timestamps=[0, 3600],
            data={
                VAR_1_ID: TabularizedDataModelOutput(actual_instance=scalar_data),
            },
        )

        # Create mock model variable
        mock_var_1_api = create_model_variable(id=VAR_1_ID, code="LogicalScalar", group="Z")
        mock_var_1 = ModelVariable(mock_var_1_api)

        # Mock the model's get_variables method
        mock_model = Mock()
        mock_model.id = MODEL_ID
        mock_model.get_variables.return_value = [mock_var_1]

        mock_api = Mock()
        mock_api.get_model_experiment_data_api_v1_models_model_id_experiments_experiment_id_data_get.return_value = mock_tabularized_data

        model_experiment = ModelExperiment(self.api_model_experiment, mock_model, mock_api)
        result = model_experiment.get_data_compat()

        # Verify result
        self.assertIn("LogicalScalar", result)
        self.assertEqual(result["LogicalScalar"], {"values": [True], "timestamps": [0]})

    def test_get_variables(self):
        from dhl_sdk.entities.model_variable import ModelVariable

        mock_api = Mock()
        mock_var_1_api = create_model_variable(id=VAR_1_ID, code="VAR_1")
        mock_var_2_api = create_model_variable(id=VAR_2_ID, code="VAR_2")
        mock_var_3_api = create_model_variable(id=VAR_3_ID, code="VAR_3")
        mock_var_1 = ModelVariable(mock_var_1_api)
        mock_var_2 = ModelVariable(mock_var_2_api)
        mock_var_3 = ModelVariable(mock_var_3_api)

        # Mock the model's get_variables method
        mock_model = Mock()
        mock_model.id = MODEL_ID
        mock_model.get_variables.return_value = [mock_var_1, mock_var_2, mock_var_3]

        model_experiment = ModelExperiment(self.api_model_experiment, mock_model, mock_api)
        result = list(model_experiment.get_variables())

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], ModelVariable)
        self.assertIsInstance(result[1], ModelVariable)
        self.assertIsInstance(result[2], ModelVariable)

    def test_get_product(self):
        from dhl_sdk.entities.product import Product

        mock_api = Mock()
        mock_product = create_product(id=PRODUCT_ID, name="Test Product", code="TEST_PROD")
        mock_api.get_product_by_id_api_v1_products_product_id_get.return_value = mock_product

        model_experiment = ModelExperiment(self.api_model_experiment, self.model, mock_api)
        result = model_experiment.get_product()

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Product)
        self.assertEqual(result.id, PRODUCT_ID)
        self.assertEqual(result.name, "Test Product")
        mock_api.get_product_by_id_api_v1_products_product_id_get.assert_called_once_with(product_id=PRODUCT_ID)

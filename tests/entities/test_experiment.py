import unittest
from datetime import datetime
from unittest.mock import Mock

from openapi_client.models.experiment import Experiment as OpenAPIExperiment
from openapi_client.models.process_unit_code import ProcessUnitCode

from dhl_sdk.entities.experiment import Experiment, ExperimentRequest
from dhl_sdk.entities.product import Product
from tests.entities._fixtures import (
    create_experiment,
    create_product,
    create_variable,
    EXPERIMENT_ID,
    PRODUCT_ID,
    VAR_1_ID,
    VAR_2_ID,
    VAR_3_ID,
)


class TestExperiment(unittest.TestCase):
    api_experiment: OpenAPIExperiment

    def setUp(self):
        self.api_experiment = create_experiment(
            id=EXPERIMENT_ID,
            displayName="Test Experiment",
            productId=PRODUCT_ID,
            description="A test experiment",
            variableIds=[VAR_1_ID, VAR_2_ID, VAR_3_ID],
        )

    def test_init(self):
        experiment = Experiment(self.api_experiment)
        self.assertIsNotNone(experiment)

    def test_str(self):
        experiment = Experiment(self.api_experiment)
        result = str(experiment)
        self.assertEqual(result, "Experiment(Test Experiment)")

    def test_id_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertEqual(experiment.id, EXPERIMENT_ID)

    def test_display_name_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertEqual(experiment.display_name, "Test Experiment")

    def test_product_id_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertEqual(experiment.product_id, PRODUCT_ID)

    def test_variable_ids_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertIsNotNone(experiment.variable_ids)
        self.assertIsInstance(experiment.variable_ids, list)
        self.assertEqual(len(experiment.variable_ids), 3)
        self.assertIn(VAR_1_ID, experiment.variable_ids)
        self.assertIn(VAR_2_ID, experiment.variable_ids)
        self.assertIn(VAR_3_ID, experiment.variable_ids)

    def test_description_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertEqual(experiment.description, "A test experiment")

    def test_start_time_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertIsNotNone(experiment.start_time)
        self.assertEqual(experiment.start_time, "2024-01-01T00:00:00Z")

    def test_start_time_property_none(self):
        self.api_experiment.start_time = None
        experiment = Experiment(self.api_experiment)
        self.assertIsNone(experiment.start_time)

    def test_variant_property(self):
        experiment = Experiment(self.api_experiment)
        self.assertIsNotNone(experiment.variant)
        self.assertEqual(experiment.variant, "run")

    def test_get_data(self):
        mock_value_1 = {"format": "timeseries", "type": "numeric", "values": [5.0, 6.0], "timestamps": [1704067200, 1704070800]}
        mock_value_2 = {"format": "timeseries", "type": "numeric", "values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]}
        mock_data = {
            VAR_1_ID: mock_value_1,
            VAR_2_ID: mock_value_2,
        }

        mock_api = Mock()
        mock_api.get_experiment_data_api_v1_experiments_experiment_id_data_get.return_value = mock_data

        experiment = Experiment(self.api_experiment)
        result = experiment.get_data(mock_api)

        self.assertEqual(result, mock_data)
        mock_api.get_experiment_data_api_v1_experiments_experiment_id_data_get.assert_called_once_with(experiment_id=EXPERIMENT_ID)

    def test_get_data_compat(self):
        mock_value_1 = {"format": "timeseries", "type": "numeric", "values": [1.0, 2.0], "timestamps": [1704067200, 1704070800]}
        mock_value_2 = {"format": "timeseries", "type": "numeric", "values": [5.0, 6.0], "timestamps": [1704067200, 1704070800]}
        mock_value_3 = {"format": "timeseries", "type": "numeric", "values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]}
        mock_data = {
            VAR_1_ID: mock_value_1,
            VAR_2_ID: mock_value_2,
            VAR_3_ID: mock_value_3,
        }

        mock_var_1 = create_variable(id=VAR_1_ID, code="A", group="Z")
        mock_var_2 = create_variable(id=VAR_2_ID, code="B", group="Y")
        mock_var_3 = create_variable(id=VAR_3_ID, code="C", group="X")

        def get_variable_side_effect(variable_id):
            if variable_id == VAR_1_ID:
                return mock_var_1
            elif variable_id == VAR_2_ID:
                return mock_var_2
            elif variable_id == VAR_3_ID:
                return mock_var_3
            return None

        mock_api = Mock()
        mock_api.get_experiment_data_api_v1_experiments_experiment_id_data_get.return_value = mock_data
        mock_api.get_variable_by_id_api_v1_variables_variable_id_get.side_effect = get_variable_side_effect

        experiment = Experiment(self.api_experiment)
        result = experiment.get_data_compat(mock_api)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn("A", result)
        self.assertIn("B", result)
        self.assertIn("C", result)
        self.assertEqual(result["A"], {"values": [1.0, 2.0], "timestamps": [1704067200, 1704070800]})
        self.assertEqual(result["B"], {"values": [5.0, 6.0], "timestamps": [1704067200, 1704070800]})
        self.assertEqual(result["C"], {"values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]})

    def test_get_variables(self):
        from dhl_sdk.entities.variable import Variable
        from tests.entities._fixtures import create_variable

        mock_api = Mock()
        mock_var_1 = create_variable(id=VAR_1_ID, code="VAR_1")
        mock_var_2 = create_variable(id=VAR_2_ID, code="VAR_2")
        mock_var_3 = create_variable(id=VAR_3_ID, code="VAR_3")

        def get_variable_side_effect(variable_id):
            if variable_id == VAR_1_ID:
                return mock_var_1
            elif variable_id == VAR_2_ID:
                return mock_var_2
            elif variable_id == VAR_3_ID:
                return mock_var_3
            return None

        mock_api.get_variable_by_id_api_v1_variables_variable_id_get.side_effect = get_variable_side_effect

        experiment = Experiment(self.api_experiment)
        result = experiment.get_variables(mock_api)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], Variable)
        self.assertIsInstance(result[1], Variable)
        self.assertIsInstance(result[2], Variable)
        self.assertEqual(mock_api.get_variable_by_id_api_v1_variables_variable_id_get.call_count, 3)

    def test_get_product(self):
        from dhl_sdk.entities.product import Product
        from tests.entities._fixtures import create_product

        mock_api = Mock()
        mock_product = create_product(id=PRODUCT_ID, name="Test Product", code="TEST_PROD")
        mock_api.get_product_by_id_api_v1_products_product_id_get.return_value = mock_product

        experiment = Experiment(self.api_experiment)
        result = experiment.get_product(mock_api)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Product)
        self.assertEqual(result.id, PRODUCT_ID)
        self.assertEqual(result.name, "Test Product")
        mock_api.get_product_by_id_api_v1_products_product_id_get.assert_called_once_with(product_id=PRODUCT_ID)


class TestExperimentRequest(unittest.TestCase):
    def setUp(self):
        api_product = create_product(id=PRODUCT_ID, name="Test Product", code="TEST_PROD")
        self.product = Product(api_product)

    def test_new(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
        )
        self.assertIsNotNone(request)

    def test_new_with_subunit(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            subunit="A",
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
        )
        self.assertIsNotNone(request)

    def test_new_with_tags(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
            tags={"tag1": "value1"},
        )
        self.assertIsNotNone(request)

    def test_new_with_extra(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
            extra={"extra1": "value1"},
        )
        self.assertIsNotNone(request)

    def test_new_with_multiple_variables(self):
        data = {
            VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]},
            VAR_2_ID: {"type": "timeseries", "values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]},
        }

        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data=data,
        )
        self.assertIsNotNone(request)

    def test_str(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
        )
        result = str(request)
        self.assertEqual(result, "ExperimentRequest(TEST_PROD-New Experiment)")

    def test_str_with_subunit(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            subunit="A",
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
        )
        result = str(request)
        self.assertEqual(result, "ExperimentRequest(TEST_PROD-New Experiment-A)")

    def test_create(self):
        mock_api = Mock()
        created_experiment = create_experiment(
            id="exp-456",
            displayName="TEST_PROD-Created Experiment",
            productId=PRODUCT_ID,
            description="Created experiment",
        )
        mock_api.create_experiment_api_v1_experiments_post.return_value = created_experiment

        request = ExperimentRequest.new(
            name="Created Experiment",
            description="Created experiment",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]}},
        )
        experiment = request.create(mock_api)

        self.assertIsInstance(experiment, Experiment)
        self.assertEqual(experiment.id, "exp-456")
        self.assertEqual(experiment.display_name, "TEST_PROD-Created Experiment")
        mock_api.create_experiment_api_v1_experiments_post.assert_called_once()

    def test_create_with_all_fields(self):
        mock_api = Mock()
        created_experiment = create_experiment(
            id="exp-789",
            displayName="TEST_PROD-Full Experiment-B",
            productId=PRODUCT_ID,
            description="Full experiment with all fields",
        )
        mock_api.create_experiment_api_v1_experiments_post.return_value = created_experiment

        request = ExperimentRequest.new(
            name="Full Experiment",
            description="Full experiment with all fields",
            product=self.product,
            subunit="B",
            process_unit=ProcessUnitCode.BR,
            start_time=datetime(2024, 1, 1, 0, 0, 0),
            end_time=datetime(2024, 1, 1, 12, 0, 0),
            data={
                VAR_1_ID: {"type": "timeseries", "values": [5.5, 6.5], "timestamps": [1704067200, 1704070800]},
                VAR_2_ID: {"type": "timeseries", "values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]},
            },
            tags={"tag1": "value1", "tag2": "value2"},
            extra={"extra1": "value1"},
        )
        experiment = request.create(mock_api)

        self.assertIsInstance(experiment, Experiment)
        self.assertEqual(experiment.id, "exp-789")
        self.assertEqual(experiment.display_name, "TEST_PROD-Full Experiment-B")
        mock_api.create_experiment_api_v1_experiments_post.assert_called_once()

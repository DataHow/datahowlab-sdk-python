import unittest
from unittest.mock import Mock

from openapi_client.models.experiment import Experiment as OpenAPIExperiment
from openapi_client.models.process_unit_code import ProcessUnitCode
from openapi_client.models.run_details import RunDetails
from openapi_client.models.samples_details import SamplesDetails
from openapi_client.models.variantdetails import Variantdetails
from openapi_client.models.variantdetails1 import Variantdetails1

from dhl_sdk.entities.experiment import Experiment, ExperimentRequest
from dhl_sdk.entities.product import Product
from tests.entities._fixtures import (
    create_experiment,
    create_product,
    create_variable,
    create_raw_experiment_data_value,
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
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertIsNotNone(experiment)

    def test_str(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        result = str(experiment)
        self.assertEqual(result, "Experiment(Test Experiment)")

    def test_id_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertEqual(experiment.id, EXPERIMENT_ID)

    def test_display_name_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertEqual(experiment.display_name, "Test Experiment")

    def test_product_id_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertEqual(experiment.product_id, PRODUCT_ID)

    def test_variable_ids_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertIsNotNone(experiment.variable_ids)
        self.assertIsInstance(experiment.variable_ids, list)
        self.assertEqual(len(experiment.variable_ids), 3)
        self.assertIn(VAR_1_ID, experiment.variable_ids)
        self.assertIn(VAR_2_ID, experiment.variable_ids)
        self.assertIn(VAR_3_ID, experiment.variable_ids)

    def test_description_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertEqual(experiment.description, "A test experiment")

    def test_process_unit_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertEqual(experiment.process_unit, ProcessUnitCode.BR)

    def test_variant_details_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertIsNotNone(experiment.variant_details)
        self.assertIsInstance(experiment.variant_details, Variantdetails)
        self.assertIsInstance(experiment.variant_details.actual_instance, RunDetails)

    def test_extra_property(self):
        mock_api = Mock()
        api_experiment = create_experiment(extra={"key1": "value1", "key2": 42})
        experiment = Experiment(api_experiment, mock_api)
        extra = experiment.extra
        self.assertIsNotNone(extra)
        self.assertIsInstance(extra, dict)
        self.assertEqual(extra["key1"], "value1")  # pyright: ignore[reportOptionalSubscript] - Checked above
        self.assertEqual(extra["key2"], 42)  # pyright: ignore[reportOptionalSubscript] - Checked above

    def test_extra_property_none(self):
        mock_api = Mock()
        api_experiment = create_experiment(extra=None)
        experiment = Experiment(api_experiment, mock_api)
        self.assertIsNone(experiment.extra)

    def test_variant_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertIsNotNone(experiment.variant)
        self.assertEqual(experiment.variant, "run")

    def test_variant_property_samples(self):
        mock_api = Mock()
        api_experiment = create_experiment(variantDetails=Variantdetails(actual_instance=SamplesDetails()))
        experiment = Experiment(api_experiment, mock_api)
        self.assertEqual(experiment.variant, "samples")

    def test_start_time_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertIsNotNone(experiment.start_time)
        self.assertEqual(experiment.start_time, "2024-01-01T00:00:00Z")

    def test_start_time_property_samples_variant(self):
        mock_api = Mock()
        api_experiment = create_experiment(variantDetails=Variantdetails(actual_instance=SamplesDetails()))
        experiment = Experiment(api_experiment, mock_api)
        self.assertIsNone(experiment.start_time)

    def test_end_time_property(self):
        mock_api = Mock()
        experiment = Experiment(self.api_experiment, mock_api)
        self.assertIsNotNone(experiment.end_time)
        self.assertEqual(experiment.end_time, "2024-01-01T12:00:00Z")

    def test_end_time_property_samples_variant(self):
        mock_api = Mock()
        api_experiment = create_experiment(variantDetails=Variantdetails(actual_instance=SamplesDetails()))
        experiment = Experiment(api_experiment, mock_api)
        self.assertIsNone(experiment.end_time)

    def test_tags_property(self):
        mock_api = Mock()
        api_experiment = create_experiment(tags={"batch": "B001", "location": "lab1"})
        experiment = Experiment(api_experiment, mock_api)
        tags = experiment.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(tags["batch"], "B001")
        self.assertEqual(tags["location"], "lab1")

    def test_tags_property_empty(self):
        mock_api = Mock()
        api_experiment = create_experiment(tags=None)
        experiment = Experiment(api_experiment, mock_api)
        tags = experiment.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_tags_property_empty_dict(self):
        mock_api = Mock()
        api_experiment = create_experiment(tags={})
        experiment = Experiment(api_experiment, mock_api)
        tags = experiment.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_get_data(self):
        mock_value_1 = {"format": "timeseries", "type": "numeric", "values": [5.0, 6.0], "timestamps": [1704067200, 1704070800]}
        mock_value_2 = {"format": "timeseries", "type": "numeric", "values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]}
        mock_data = {
            VAR_1_ID: mock_value_1,
            VAR_2_ID: mock_value_2,
        }

        mock_api = Mock()
        mock_api.get_experiment_data_api_v1_experiments_experiment_id_data_get.return_value = mock_data

        experiment = Experiment(self.api_experiment, mock_api)
        result = experiment.get_data()

        self.assertEqual(result, mock_data)
        mock_api.get_experiment_data_api_v1_experiments_experiment_id_data_get.assert_called_once_with(experiment_id=EXPERIMENT_ID)

    def test_get_data_compat(self):
        # Create proper OpenAPI objects
        mock_value_1 = create_raw_experiment_data_value([1.0, 2.0], [1704067200, 1704070800])
        mock_value_2 = create_raw_experiment_data_value([5.0, 6.0], [1704067200, 1704070800])
        mock_value_3 = create_raw_experiment_data_value([10.0, 11.0], [1704067200, 1704070800])
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

        experiment = Experiment(self.api_experiment, mock_api)
        result = experiment.get_data_compat()

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

        experiment = Experiment(self.api_experiment, mock_api)
        result = experiment.get_variables()

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

        experiment = Experiment(self.api_experiment, mock_api)
        result = experiment.get_product()

        self.assertIsNotNone(result)
        self.assertIsInstance(result, Product)
        self.assertEqual(result.id, PRODUCT_ID)
        self.assertEqual(result.name, "Test Product")
        mock_api.get_product_by_id_api_v1_products_product_id_get.assert_called_once_with(product_id=PRODUCT_ID)


class TestExperimentRequest(unittest.TestCase):
    product: Product

    def setUp(self):
        api_product = create_product(id=PRODUCT_ID, name="Test Product", code="TEST_PROD")
        mock_api = Mock()
        self.product = Product(api_product, mock_api)

    def test_new(self):
        variant_details = Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z"))
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            variant_details=variant_details,
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
        )
        self.assertIsNotNone(request)

    def test_new_with_subunit(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            subunit="A",
            process_unit=ProcessUnitCode.BR,
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
        )
        self.assertIsNotNone(request)

    def test_new_with_tags(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
            tags={"tag1": "value1"},
        )
        self.assertIsNotNone(request)

    def test_new_with_extra(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
            extra={"extra1": "value1"},
        )
        self.assertIsNotNone(request)

    def test_new_with_multiple_variables(self):
        data = {
            VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800]),
            VAR_2_ID: create_raw_experiment_data_value([10.0, 11.0], [1704067200, 1704070800]),
        }

        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data=data,
        )
        self.assertIsNotNone(request)

    def test_str(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            process_unit=ProcessUnitCode.BR,
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
        )
        result = str(request)
        self.assertEqual(result, "ExperimentRequest(New Experiment)")

    def test_str_with_subunit(self):
        request = ExperimentRequest.new(
            name="New Experiment",
            description="New experiment description",
            product=self.product,
            subunit="A",
            process_unit=ProcessUnitCode.BR,
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
        )
        result = str(request)
        self.assertEqual(result, "ExperimentRequest(New Experiment)")

    def test_create(self):
        mock_api = Mock()
        mock_client = Mock()
        mock_client.api = mock_api
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
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800])},
        )
        experiment = request.create(mock_client)

        self.assertIsInstance(experiment, Experiment)
        self.assertEqual(experiment.id, "exp-456")
        self.assertEqual(experiment.display_name, "TEST_PROD-Created Experiment")
        mock_api.create_experiment_api_v1_experiments_post.assert_called_once()

    def test_create_with_all_fields(self):
        mock_api = Mock()
        mock_client = Mock()
        mock_client.api = mock_api
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
            variant_details=Variantdetails(actual_instance=RunDetails(startTime="2024-01-01T00:00:00Z", endTime="2024-01-01T12:00:00Z")),
            data={
                VAR_1_ID: create_raw_experiment_data_value([5.5, 6.5], [1704067200, 1704070800]),
                VAR_2_ID: create_raw_experiment_data_value([10.0, 11.0], [1704067200, 1704070800]),
            },
            tags={"tag1": "value1", "tag2": "value2"},
            extra={"extra1": "value1"},
        )
        experiment = request.create(mock_client)

        self.assertIsInstance(experiment, Experiment)
        self.assertEqual(experiment.id, "exp-789")
        self.assertEqual(experiment.display_name, "TEST_PROD-Full Experiment-B")
        mock_api.create_experiment_api_v1_experiments_post.assert_called_once()

    def test_from_compat_data(self):
        from dhl_sdk.entities.variable import Variable
        from openapi_client.models.numeric_details import NumericDetails
        from openapi_client.models.categorical_details import CategoricalDetails

        # Create mock variables with different types
        mock_var_1 = create_variable(id=VAR_1_ID, code="TEMP", variantDetails=Variantdetails1(actual_instance=NumericDetails()))
        mock_var_2 = create_variable(id=VAR_2_ID, code="STATUS", variantDetails=Variantdetails1(actual_instance=CategoricalDetails()))

        variables = [Variable(mock_var_1), Variable(mock_var_2)]

        # Compat data format
        compat_data = {
            "TEMP": {"values": [10.0, 11.0, 12.0], "timestamps": [1704067200, 1704070800, 1704074400]},
            "STATUS": {"values": ["ON", "OFF", "ON"], "timestamps": [1704067200, 1704070800, 1704074400]},
        }

        # Convert to OpenAPI format
        result = ExperimentRequest.from_compat_data(variables, compat_data)

        # Verify result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        self.assertIn(VAR_1_ID, result)
        self.assertIn(VAR_2_ID, result)

        # Check VAR_1 (numeric) - access through wrapped structure
        var1_wrapped = result[VAR_1_ID]
        assert var1_wrapped is not None  # Type narrowing
        assert var1_wrapped.actual_instance is not None  # Type narrowing
        var1_data = var1_wrapped.actual_instance.actual_instance
        assert var1_data is not None  # Type narrowing
        self.assertEqual(var1_data.format, "timeseries")
        self.assertEqual(var1_data.type, "numeric")
        self.assertEqual(var1_data.values, [10.0, 11.0, 12.0])
        self.assertEqual(var1_data.timestamps, [1704067200, 1704070800, 1704074400])

        # Check VAR_2 (categorical) - access through wrapped structure
        var2_wrapped = result[VAR_2_ID]
        assert var2_wrapped is not None  # Type narrowing
        assert var2_wrapped.actual_instance is not None  # Type narrowing
        var2_data = var2_wrapped.actual_instance.actual_instance
        self.assertIsNotNone(var2_data)
        assert var2_data is not None  # Type narrowing
        self.assertEqual(var2_data.format, "timeseries")
        self.assertEqual(var2_data.type, "categorical")
        self.assertEqual(var2_data.values, ["ON", "OFF", "ON"])
        self.assertEqual(var2_data.timestamps, [1704067200, 1704070800, 1704074400])

    def test_from_compat_data_with_flow_variant(self):
        from dhl_sdk.entities.variable import Variable
        from openapi_client.models.flow_details import FlowDetails
        from openapi_client.models.flow_type import FlowType

        # Create mock variable with flow type
        mock_var_1 = create_variable(
            id=VAR_1_ID, code="FLOW_RATE", variantDetails=Variantdetails1(actual_instance=FlowDetails(type=FlowType.CONTI))
        )

        variables = [Variable(mock_var_1)]

        # Compat data format
        compat_data = {
            "FLOW_RATE": {"values": [1.0, 2.0, 3.0], "timestamps": [1704067200, 1704070800, 1704074400]},
        }

        # Convert to OpenAPI format
        result = ExperimentRequest.from_compat_data(variables, compat_data)

        # Verify result - flow should be treated as numeric
        var1_wrapped = result[VAR_1_ID]
        assert var1_wrapped is not None  # Type narrowing
        assert var1_wrapped.actual_instance is not None  # Type narrowing
        var1_data = var1_wrapped.actual_instance.actual_instance
        assert var1_data is not None  # Type narrowing
        self.assertEqual(var1_data.format, "timeseries")
        self.assertEqual(var1_data.type, "numeric")
        self.assertEqual(var1_data.values, [1.0, 2.0, 3.0])

    def test_from_compat_data_non_unique_codes(self):
        from dhl_sdk.entities.variable import Variable
        from openapi_client.models.numeric_details import NumericDetails

        # Create mock variables with the same code
        mock_var_1 = create_variable(id=VAR_1_ID, code="TEMP", variantDetails=Variantdetails1(actual_instance=NumericDetails()))
        mock_var_2 = create_variable(
            id=VAR_2_ID,
            code="TEMP",  # Duplicate code
            variantDetails=Variantdetails1(actual_instance=NumericDetails()),
        )

        variables = [Variable(mock_var_1), Variable(mock_var_2)]

        # Compat data format
        compat_data = {
            "TEMP": {"values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]},
        }

        # Should raise ValueError for non-unique codes
        with self.assertRaises(ValueError) as context:
            _ = ExperimentRequest.from_compat_data(variables, compat_data)

        self.assertIn("Non-unique variable code", str(context.exception))

    def test_from_compat_data_spectra_not_supported(self):
        from dhl_sdk.entities.variable import Variable
        from openapi_client.models.spectrum_details import SpectrumDetails

        # Create mock variable with spectrum type
        mock_var_1 = create_variable(id=VAR_1_ID, code="SPECTRUM", variantDetails=Variantdetails1(actual_instance=SpectrumDetails()))

        variables = [Variable(mock_var_1)]

        # Compat data format
        compat_data = {
            "SPECTRUM": {"values": [1.0, 2.0], "timestamps": [1704067200, 1704070800]},
        }

        # Should raise ValueError for spectra variant
        with self.assertRaises(NotImplementedError) as context:
            _ = ExperimentRequest.from_compat_data(variables, compat_data)

        self.assertIn("Spectra variant is not supported", str(context.exception))

    def test_from_compat_data_unknown_variable_code(self):
        from dhl_sdk.entities.variable import Variable
        from openapi_client.models.numeric_details import NumericDetails

        # Create mock variable
        mock_var_1 = create_variable(id=VAR_1_ID, code="TEMP", variantDetails=Variantdetails1(actual_instance=NumericDetails()))

        variables = [Variable(mock_var_1)]

        # Compat data format with unknown variable code
        compat_data = {
            "UNKNOWN_VAR": {"values": [10.0, 11.0], "timestamps": [1704067200, 1704070800]},
        }

        # Should raise ValueError for unknown variable code
        with self.assertRaises(ValueError) as context:
            _ = ExperimentRequest.from_compat_data(variables, compat_data)

        self.assertIn("Variable code 'UNKNOWN_VAR' not found", str(context.exception))

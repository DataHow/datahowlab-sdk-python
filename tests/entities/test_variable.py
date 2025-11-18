import unittest
from unittest.mock import Mock

from openapi_client.models.variable import Variable as OpenAPIVariable
from openapi_client.models.variantdetails1 import Variantdetails1

from dhl_sdk.entities.variable import Variable, VariableRequest
from tests.entities._fixtures import create_variable


class TestVariable(unittest.TestCase):
    api_variable: OpenAPIVariable

    def setUp(self):
        self.api_variable = create_variable(
            id="var-123",
            name="Test Variable",
            code="TEST_VAR",
            description="A test variable",
            measurementUnit="g/L",
            group="Process",
        )

    def test_init(self):
        variable = Variable(self.api_variable)
        self.assertIsNotNone(variable)

    def test_str(self):
        variable = Variable(self.api_variable)
        result = str(variable)
        self.assertEqual(result, "Variable(code=TEST_VAR, group=Process, measurementUnit=g/L)")

    def test_str_no_group_or_unit(self):
        api_variable = create_variable(
            id="var-456",
            name="Test Variable 2",
            code="TEST_VAR_2",
            description="Another test variable",
            measurementUnit="",
            group="",
        )
        variable = Variable(api_variable)
        result = str(variable)
        self.assertEqual(result, "Variable(code=TEST_VAR_2, group=, measurementUnit=)")

    def test_id_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.id, "var-123")

    def test_name_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.name, "Test Variable")

    def test_code_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.code, "TEST_VAR")

    def test_description_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.description, "A test variable")

    def test_measurement_unit_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.measurement_unit, "g/L")

    def test_group_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.group, "Process")

    def test_variant_details_property(self):
        variable = Variable(self.api_variable)
        self.assertIsNotNone(variable.variant_details)

    def test_variant_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.variant, "numeric")

    def test_variant_property_categorical(self):
        from openapi_client.models.categorical_details import CategoricalDetails
        from openapi_client.models.variantdetails1 import Variantdetails1

        api_variable = create_variable(variantDetails=Variantdetails1(actual_instance=CategoricalDetails()))
        variable = Variable(api_variable)
        self.assertEqual(variable.variant, "categorical")

    def test_variant_property_logical(self):
        from openapi_client.models.logical_details import LogicalDetails
        from openapi_client.models.variantdetails1 import Variantdetails1

        api_variable = create_variable(variantDetails=Variantdetails1(actual_instance=LogicalDetails()))
        variable = Variable(api_variable)
        self.assertEqual(variable.variant, "logical")

    def test_variant_property_flow(self):
        from openapi_client.models.flow_details import FlowDetails
        from openapi_client.models.flow_type import FlowType
        from openapi_client.models.variantdetails1 import Variantdetails1

        api_variable = create_variable(variantDetails=Variantdetails1(actual_instance=FlowDetails(type=FlowType.CONTI)))
        variable = Variable(api_variable)
        self.assertEqual(variable.variant, "flow")

    def test_variant_property_spectrum(self):
        from openapi_client.models.spectrum_details import SpectrumDetails
        from openapi_client.models.variantdetails1 import Variantdetails1

        api_variable = create_variable(variantDetails=Variantdetails1(actual_instance=SpectrumDetails()))
        variable = Variable(api_variable)
        self.assertEqual(variable.variant, "spectrum")

    def test_aggregation_property(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.aggregation, "none")

    def test_aggregation_property_first(self):
        from openapi_client.models.group_aggregation import GroupAggregation

        api_variable = create_variable(aggregation=GroupAggregation.FIRST)
        variable = Variable(api_variable)
        self.assertEqual(variable.aggregation, "first")

    def test_tags_property_none(self):
        variable = Variable(self.api_variable)
        self.assertEqual(variable.tags, {})

    def test_tags_property_dict(self):
        self.api_variable.tags = {"key": "value"}
        variable = Variable(self.api_variable)
        self.assertEqual(variable.tags, {"key": "value"})


class TestVariableRequest(unittest.TestCase):
    def test_new(self):
        from openapi_client.models.numeric_details import NumericDetails

        request = VariableRequest.new(
            name="New Variable",
            code="NEW_VAR",
            description="New variable description",
            measurement_unit="mg/L",
            group="Quality",
            variant_details=Variantdetails1(actual_instance=NumericDetails()),
        )
        self.assertIsNotNone(request)

    def test_new_with_tags(self):
        from openapi_client.models.numeric_details import NumericDetails

        request = VariableRequest.new(
            name="New Variable",
            code="NEW_VAR",
            description="New variable description",
            measurement_unit="mg/L",
            group="Quality",
            variant_details=Variantdetails1(actual_instance=NumericDetails()),
            tags={"tag1": "value1"},
        )
        self.assertIsNotNone(request)

    def test_str(self):
        from openapi_client.models.numeric_details import NumericDetails

        request = VariableRequest.new(
            name="New Variable",
            code="NEW_VAR",
            description="New variable description",
            measurement_unit="mg/L",
            group="Quality",
            variant_details=Variantdetails1(actual_instance=NumericDetails()),
        )
        result = str(request)
        self.assertEqual(result, "VariableRequest(code=NEW_VAR, group=Quality, measurementUnit=mg/L)")

    def test_create(self):
        from openapi_client.models.numeric_details import NumericDetails

        mock_api = Mock()
        mock_client = Mock()
        mock_client.api = mock_api
        created_variable = create_variable(
            id="var-456",
            name="Created Variable",
            code="CREATED_VAR",
            description="Created variable",
            measurementUnit="g/L",
            group="Process",
        )
        mock_api.create_variable_api_v1_variables_post.return_value = created_variable

        request = VariableRequest.new(
            name="Created Variable",
            code="CREATED_VAR",
            description="Created variable",
            measurement_unit="g/L",
            group="Process",
            variant_details=Variantdetails1(actual_instance=NumericDetails()),
        )
        variable = request.create(mock_client)

        self.assertIsInstance(variable, Variable)
        self.assertEqual(variable.id, "var-456")
        self.assertEqual(variable.name, "Created Variable")
        mock_api.create_variable_api_v1_variables_post.assert_called_once()

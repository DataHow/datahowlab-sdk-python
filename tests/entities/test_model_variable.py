import unittest

from dhl_sdk.entities.model_variable import ModelVariable
from tests.entities._fixtures import create_model_variable, VARIABLE_ID


class TestModelVariable(unittest.TestCase):
    def test_init(self):
        api_model_variable = create_model_variable()
        model_variable = ModelVariable(api_model_variable)
        self.assertIsNotNone(model_variable)

    def test_str(self):
        api_model_variable = create_model_variable(code="TEST_VAR", group="X", measurementUnit="g/L")
        model_variable = ModelVariable(api_model_variable)
        result = str(model_variable)
        self.assertEqual(result, "ModelVariable(TEST_VAR, X, g/L)")

    def test_id_property(self):
        api_model_variable = create_model_variable(id=VARIABLE_ID)
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.id, VARIABLE_ID)

    def test_name_property(self):
        api_model_variable = create_model_variable(name="Test Variable Name")
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.name, "Test Variable Name")

    def test_code_property(self):
        api_model_variable = create_model_variable(code="CODE_123")
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.code, "CODE_123")

    def test_description_property(self):
        api_model_variable = create_model_variable(description="Test description")
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.description, "Test description")

    def test_measurement_unit_property(self):
        api_model_variable = create_model_variable(measurementUnit="mol/L")
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.measurement_unit, "mol/L")

    def test_group_property(self):
        api_model_variable = create_model_variable(group="Y")
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.group, "Y")

    def test_variant_property(self):
        api_model_variable = create_model_variable()
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.variant, "numeric")

    def test_input_type_property(self):
        api_model_variable = create_model_variable()
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.input_type, "scalar")

    def test_output_type_property(self):
        api_model_variable = create_model_variable()
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.output_type, "fullTimeseries")

    def test_disposition_property(self):
        api_model_variable = create_model_variable(disposition="output")
        model_variable = ModelVariable(api_model_variable)
        self.assertEqual(model_variable.disposition, "output")

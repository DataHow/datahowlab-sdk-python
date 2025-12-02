import unittest

from openapi_client.models.variable_variant import VariableVariant

from dhl_sdk.entities.variable_group import VariableGroup
from tests.entities._fixtures import create_variable_group


class TestVariableGroup(unittest.TestCase):
    def test_init(self):
        api_group = create_variable_group()
        group = VariableGroup(api_group)
        self.assertIsNotNone(group)

    def test_str(self):
        api_group = create_variable_group(name="My Group", code="MY_GROUP")
        group = VariableGroup(api_group)
        result = str(group)
        self.assertEqual(result, "VariableGroup(name=My Group, code=MY_GROUP)")

    def test_id_property(self):
        api_group = create_variable_group(id="group-456")
        group = VariableGroup(api_group)
        self.assertEqual(group.id, "group-456")

    def test_name_property(self):
        api_group = create_variable_group(name="Temperature Group")
        group = VariableGroup(api_group)
        self.assertEqual(group.name, "Temperature Group")

    def test_code_property(self):
        api_group = create_variable_group(code="TEMP_GRP")
        group = VariableGroup(api_group)
        self.assertEqual(group.code, "TEMP_GRP")

    def test_description_property(self):
        api_group = create_variable_group(description="A group for temperature variables")
        group = VariableGroup(api_group)
        self.assertEqual(group.description, "A group for temperature variables")

    def test_tags_property(self):
        api_group = create_variable_group(tags={"manufacturer": "example", "location": "plant1"})
        group = VariableGroup(api_group)
        tags = group.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(tags["manufacturer"], "example")
        self.assertEqual(tags["location"], "plant1")

    def test_tags_property_empty(self):
        api_group = create_variable_group(tags=None)
        group = VariableGroup(api_group)
        tags = group.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_tags_property_empty_dict(self):
        api_group = create_variable_group(tags={})
        group = VariableGroup(api_group)
        tags = group.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_variable_variants_property(self):
        api_group = create_variable_group(variableVariants=[VariableVariant.NUMERIC, VariableVariant.LOGICAL])
        group = VariableGroup(api_group)
        variants = group.variable_variants
        assert variants is not None  # Type narrowing for type checker
        self.assertIsInstance(variants, list)
        self.assertEqual(len(variants), 2)
        self.assertEqual(variants[0], VariableVariant.NUMERIC)
        self.assertEqual(variants[1], VariableVariant.LOGICAL)

    def test_variable_variants_property_single(self):
        api_group = create_variable_group(variableVariants=[VariableVariant.SPECTRUM])
        group = VariableGroup(api_group)
        variants = group.variable_variants
        assert variants is not None  # Type narrowing for type checker
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0], VariableVariant.SPECTRUM)

    def test_variable_variants_property_none(self):
        api_group = create_variable_group(variableVariants=None)
        group = VariableGroup(api_group)
        variants = group.variable_variants
        self.assertIsNone(variants)

    def test_variable_variants_property_all_types(self):
        all_variants = [
            VariableVariant.NUMERIC,
            VariableVariant.CATEGORICAL,
            VariableVariant.LOGICAL,
            VariableVariant.SPECTRUM,
            VariableVariant.FLOW,
        ]
        api_group = create_variable_group(variableVariants=all_variants)
        group = VariableGroup(api_group)
        variants = group.variable_variants
        assert variants is not None  # Type narrowing for type checker
        self.assertEqual(len(variants), 5)
        for variant in all_variants:
            self.assertIn(variant, variants)

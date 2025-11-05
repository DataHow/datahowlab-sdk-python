import unittest
from unittest.mock import Mock

from dhl_sdk.entities.model import Model
from tests.entities._fixtures import (
    create_model,
    create_model_experiment,
    create_model_variable,
    EXPERIMENT_ID,
    MODEL_ID,
    PRODUCT_ID,
    VAR_1_ID,
    VAR_2_ID,
)


class TestModel(unittest.TestCase):
    def test_init(self):
        api_model = create_model()
        model = Model(api_model)
        self.assertIsNotNone(model)

    def test_str(self):
        api_model = create_model(name="Test Model", type="historical")
        model = Model(api_model)
        result = str(model)
        self.assertEqual(result, "Model(Test Model, historical)")

    def test_id_property(self):
        api_model = create_model(id=MODEL_ID)
        model = Model(api_model)
        self.assertEqual(model.id, MODEL_ID)

    def test_name_property(self):
        api_model = create_model(name="My Model")
        model = Model(api_model)
        self.assertEqual(model.name, "My Model")

    def test_description_property(self):
        api_model = create_model(description="Model description")
        model = Model(api_model)
        self.assertEqual(model.description, "Model description")

    def test_status_property(self):
        api_model = create_model()
        model = Model(api_model)
        self.assertEqual(model.status, "success")

    def test_type_property(self):
        api_model = create_model()
        model = Model(api_model)
        self.assertEqual(model.type, "historical")

    def test_project_id_property(self):
        api_model = create_model(projectId="project-123")
        model = Model(api_model)
        self.assertEqual(model.project_id, "project-123")

    def test_dataset_id_property(self):
        api_model = create_model(datasetId="dataset-456")
        model = Model(api_model)
        self.assertEqual(model.dataset_id, "dataset-456")

    def test_variant_property(self):
        api_model = create_model(variant="Stepwise GP")
        model = Model(api_model)
        self.assertEqual(model.variant, "Stepwise GP")

    def test_step_size_property(self):
        api_model = create_model(stepSize=3600)
        model = Model(api_model)
        self.assertEqual(model.step_size, 3600)

    def test_success_property_true(self):
        api_model = create_model()  # Default status is SUCCESS
        model = Model(api_model)
        self.assertTrue(model.success)

    def test_success_property_false(self):
        from openapi_client.models.model_status import ModelStatus

        api_model = create_model(status=ModelStatus.FAILED)
        model = Model(api_model)
        self.assertFalse(model.success)

    def test_get_variables(self):
        from dhl_sdk.entities.model_variable import ModelVariable

        mock_api = Mock()
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="VAR_1")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="VAR_2")

        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model)
        result = list(model.get_variables(mock_api))

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ModelVariable)
        self.assertIsInstance(result[1], ModelVariable)
        self.assertEqual(result[0].code, "VAR_1")
        self.assertEqual(result[1].code, "VAR_2")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.assert_called_once_with(model_id=MODEL_ID, skip=0, limit=10)

    def test_get_variables_pagination(self):
        """Test that get_variables handles pagination."""
        mock_api = Mock()
        mock_vars_page1 = [create_model_variable(id=f"var-{i}", code=f"VAR_{i}") for i in range(10)]
        mock_vars_page2 = [create_model_variable(id=f"var-{i + 10}", code=f"VAR_{i + 10}") for i in range(5)]

        mock_api.get_model_variables_api_v1_models_model_id_variables_get.side_effect = [
            mock_vars_page1,
            mock_vars_page2,
        ]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model)

        result = list(model.get_variables(mock_api))

        # Should get all variables across both pages
        self.assertEqual(len(result), 15)
        # Should have made 2 API calls
        self.assertEqual(mock_api.get_model_variables_api_v1_models_model_id_variables_get.call_count, 2)

    def test_get_experiments(self):
        from dhl_sdk.entities.model_experiment import ModelExperiment

        mock_api = Mock()
        mock_exp_1 = create_model_experiment(id=EXPERIMENT_ID, displayName="Experiment 1", productId=PRODUCT_ID)
        mock_exp_2 = create_model_experiment(id="exp-2", displayName="Experiment 2", productId=PRODUCT_ID)

        mock_api.get_model_experiments_api_v1_models_model_id_experiments_get.return_value = [mock_exp_1, mock_exp_2]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model)
        result = list(model.get_experiments(mock_api))

        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], ModelExperiment)
        self.assertIsInstance(result[1], ModelExperiment)
        self.assertEqual(result[0].display_name, "Experiment 1")
        self.assertEqual(result[1].display_name, "Experiment 2")
        mock_api.get_model_experiments_api_v1_models_model_id_experiments_get.assert_called_once_with(model_id=MODEL_ID, skip=0, limit=10)

    def test_get_experiments_pagination(self):
        """Test that get_experiments handles pagination."""
        mock_api = Mock()
        mock_exps_page1 = [create_model_experiment(id=f"exp-{i}", displayName=f"Experiment {i}", productId=PRODUCT_ID) for i in range(10)]
        mock_exps_page2 = [
            create_model_experiment(id=f"exp-{i + 10}", displayName=f"Experiment {i + 10}", productId=PRODUCT_ID) for i in range(5)
        ]

        mock_api.get_model_experiments_api_v1_models_model_id_experiments_get.side_effect = [
            mock_exps_page1,
            mock_exps_page2,
        ]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model)

        result = list(model.get_experiments(mock_api))

        # Should get all experiments across both pages
        self.assertEqual(len(result), 15)
        # Should have made 2 API calls
        self.assertEqual(mock_api.get_model_experiments_api_v1_models_model_id_experiments_get.call_count, 2)

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
        mock_api = Mock()
        api_model = create_model()
        model = Model(api_model, mock_api)
        self.assertIsNotNone(model)

    def test_str(self):
        mock_api = Mock()
        api_model = create_model(name="Test Model", type="historical")
        model = Model(api_model, mock_api)
        result = str(model)
        self.assertEqual(result, "Model(Test Model, historical)")

    def test_id_property(self):
        mock_api = Mock()
        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)
        self.assertEqual(model.id, MODEL_ID)

    def test_name_property(self):
        mock_api = Mock()
        api_model = create_model(name="My Model")
        model = Model(api_model, mock_api)
        self.assertEqual(model.name, "My Model")

    def test_description_property(self):
        mock_api = Mock()
        api_model = create_model(description="Model description")
        model = Model(api_model, mock_api)
        self.assertEqual(model.description, "Model description")

    def test_status_property(self):
        mock_api = Mock()
        api_model = create_model()
        model = Model(api_model, mock_api)
        self.assertEqual(model.status, "success")

    def test_type_property(self):
        mock_api = Mock()
        api_model = create_model()
        model = Model(api_model, mock_api)
        self.assertEqual(model.type, "historical")

    def test_project_id_property(self):
        mock_api = Mock()
        api_model = create_model(projectId="project-123")
        model = Model(api_model, mock_api)
        self.assertEqual(model.project_id, "project-123")

    def test_dataset_id_property(self):
        mock_api = Mock()
        api_model = create_model(datasetId="dataset-456")
        model = Model(api_model, mock_api)
        self.assertEqual(model.dataset_id, "dataset-456")

    def test_variant_property(self):
        mock_api = Mock()
        api_model = create_model(variant="Stepwise GP")
        model = Model(api_model, mock_api)
        self.assertEqual(model.variant, "Stepwise GP")

    def test_step_size_property(self):
        mock_api = Mock()
        api_model = create_model(stepSize=3600)
        model = Model(api_model, mock_api)
        self.assertEqual(model.step_size, 3600)

    def test_success_property_true(self):
        mock_api = Mock()
        api_model = create_model()  # Default status is SUCCESS
        model = Model(api_model, mock_api)
        self.assertTrue(model.success)

    def test_success_property_false(self):
        from openapi_client.models.model_status import ModelStatus

        mock_api = Mock()
        api_model = create_model(status=ModelStatus.FAILED)
        model = Model(api_model, mock_api)
        self.assertFalse(model.success)

    def test_tags_property(self):
        mock_api = Mock()
        api_model = create_model(tags={"environment": "production", "version": "v2"})
        model = Model(api_model, mock_api)
        tags = model.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(tags["environment"], "production")
        self.assertEqual(tags["version"], "v2")

    def test_tags_property_empty(self):
        mock_api = Mock()
        api_model = create_model(tags=None)
        model = Model(api_model, mock_api)
        tags = model.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_tags_property_empty_dict(self):
        mock_api = Mock()
        api_model = create_model(tags={})
        model = Model(api_model, mock_api)
        tags = model.tags
        self.assertIsInstance(tags, dict)
        self.assertEqual(len(tags), 0)

    def test_references_property(self):
        from openapi_client.models.model_reference import ModelReference
        from openapi_client.models.model_type import ModelType

        mock_api = Mock()
        ref1 = ModelReference(type=ModelType.PROPAGATION, modelId="model-123")
        ref2 = ModelReference(type=ModelType.HISTORICAL, modelId="model-456")
        api_model = create_model(references=[ref1, ref2])
        model = Model(api_model, mock_api)
        references = model.references
        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 2)
        self.assertEqual(references[0].model_id, "model-123")
        self.assertEqual(references[1].model_id, "model-456")

    def test_references_property_empty(self):
        mock_api = Mock()
        api_model = create_model(references=None)
        model = Model(api_model, mock_api)
        references = model.references
        self.assertIsInstance(references, list)
        self.assertEqual(len(references), 0)

    def test_get_variables(self):
        from dhl_sdk.entities.model_variable import ModelVariable

        mock_api = Mock()
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="VAR_1")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="VAR_2")

        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)
        result = list(model.get_variables())

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
        model = Model(api_model, mock_api)

        result = list(model.get_variables())

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
        model = Model(api_model, mock_api)
        result = list(model.get_experiments())

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
        model = Model(api_model, mock_api)

        result = list(model.get_experiments())

        # Should get all experiments across both pages
        self.assertEqual(len(result), 15)
        # Should have made 2 API calls
        self.assertEqual(mock_api.get_model_experiments_api_v1_models_model_id_experiments_get.call_count, 2)

    def test_predict_basic(self):
        """Test basic predict functionality with time series data."""
        from openapi_client.models.numerical_time_series import NumericalTimeSeries
        from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData
        from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()
        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        # Create inputs
        inputs = {
            VAR_1_ID: TabularizedDataModelInput(TabularizedTimeSeriesData(NumericalTimeSeries(values=[1.0, 2.0, 3.0]))),
        }
        timestamps = [0, 60, 120]

        # Mock response
        predicted_ts = PredictedNumericalTimeSeries(values=[10.0, 11.0, 12.0])
        mock_response = PredictionResponse(
            timestamps=timestamps, predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        # Call predict
        result = model.predict(inputs, timestamps)

        # Verify
        self.assertIsInstance(result, PredictionResponse)
        self.assertEqual(result.timestamps, timestamps)
        self.assertIn(VAR_2_ID, result.predictions)
        mock_api.model_prediction_api_v1_models_model_id_predict_post.assert_called_once()

    def test_predict_with_config(self):
        """Test predict with ModelPredictionConfig."""
        from openapi_client.models.numerical_time_series import NumericalTimeSeries
        from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData
        from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.model_prediction_config import ModelPredictionConfig

        mock_api = Mock()
        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {
            VAR_1_ID: TabularizedDataModelInput(TabularizedTimeSeriesData(NumericalTimeSeries(values=[1.0, 2.0, 3.0]))),
        }
        timestamps = [0, 60, 120]
        config = ModelPredictionConfig(starting_timestamp=60, model_confidence=90)  # pyright: ignore[reportCallIssue]

        mock_response = PredictionResponse(timestamps=timestamps, predictions={})
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        _ = model.predict(inputs, timestamps, config)

        # Verify config was passed
        call_args = mock_api.model_prediction_api_v1_models_model_id_predict_post.call_args
        self.assertIsNotNone(call_args)
        payload = call_args.kwargs["prediction_payload"]
        self.assertEqual(payload.config.model_confidence, 90)
        self.assertEqual(payload.config.starting_timestamp, 60)

    def test_predict_model_not_ready(self):
        """Test predict raises error when model is not ready."""
        from openapi_client.models.model_status import ModelStatus
        from openapi_client.models.numerical_time_series import NumericalTimeSeries
        from openapi_client.models.tabularized_time_series_data import TabularizedTimeSeriesData
        from openapi_client.models.tabularized_data_model_input import TabularizedDataModelInput

        mock_api = Mock()
        api_model = create_model(id=MODEL_ID, status=ModelStatus.FAILED, name="Failed Model")
        model = Model(api_model, mock_api)

        inputs = {
            VAR_1_ID: TabularizedDataModelInput(TabularizedTimeSeriesData(NumericalTimeSeries(values=[1.0]))),
        }
        timestamps = [0]

        with self.assertRaises(ValueError) as context:
            _ = model.predict(inputs, timestamps)

        self.assertIn("Failed Model", str(context.exception))
        self.assertIn("not ready for prediction", str(context.exception))

    def test_predict_compat_time_series(self):
        """Test predict_compat with time series inputs."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()

        # Mock get_variables to return variable mappings
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="Temperature", variant="numeric")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Glucose", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        # Mock predict response
        predicted_ts = PredictedNumericalTimeSeries(values=[10.0, 11.0, 12.0])
        mock_response = PredictionResponse(
            timestamps=[0, 60, 120], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        # Legacy format: use variable codes
        inputs = {"Temperature": [25.0, 26.0, 27.0]}
        timestamps = [0, 60, 120]

        result = model.predict_compat(inputs, timestamps)

        # Verify legacy format output
        self.assertIsInstance(result, dict)
        self.assertIn("Glucose", result)
        self.assertEqual(result["Glucose"], [10.0, 11.0, 12.0])

    def test_predict_compat_scalar_to_list(self):
        """Test predict_compat converts scalars to single-element lists."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_scalar import PredictedNumericalScalar
        from openapi_client.models.predicted_scalars_data import PredictedScalarsData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()

        mock_var_1 = create_model_variable(id=VAR_1_ID, code="pH", variant="numeric")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Result", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        # Mock scalar prediction
        predicted_scalar = PredictedNumericalScalar(value=7.5)
        mock_response = PredictionResponse(
            timestamps=None, predictions={VAR_2_ID: PredictedDataModel(PredictedScalarsData(predicted_scalar))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        # Single-element list treated as scalar
        inputs = {"pH": [7.0]}
        timestamps = [0]

        result = model.predict_compat(inputs, timestamps)

        # Scalar output converted to single-element list
        self.assertIsInstance(result, dict)
        self.assertIn("Result", result)
        self.assertEqual(result["Result"], [7.5])

    def test_predict_compat_categorical_variant(self):
        """Test predict_compat with categorical variables."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.categorical_time_series import CategoricalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()

        mock_var_1 = create_model_variable(id=VAR_1_ID, code="FeedType", variant="categorical")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Status", variant="categorical")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_cat = CategoricalTimeSeries(values=["Good", "Good", "Excellent"])
        mock_response = PredictionResponse(
            timestamps=[0, 60, 120], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_cat))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"FeedType": ["TypeA", "TypeA", "TypeB"]}
        timestamps = [0, 60, 120]

        result = model.predict_compat(inputs, timestamps)

        self.assertIn("Status", result)
        self.assertEqual(result["Status"], ["Good", "Good", "Excellent"])

    def test_predict_compat_logical_variant(self):
        """Test predict_compat with logical variables."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.logical_time_series import LogicalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()

        mock_var_1 = create_model_variable(id=VAR_1_ID, code="IsFed", variant="logical")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="IsActive", variant="logical")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_logical = LogicalTimeSeries(values=[True, True, False])
        mock_response = PredictionResponse(
            timestamps=[0, 60, 120], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_logical))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"IsFed": [True, False, False]}
        timestamps = [0, 60, 120]

        result = model.predict_compat(inputs, timestamps)

        self.assertIn("IsActive", result)
        self.assertEqual(result["IsActive"], [True, True, False])

    def test_predict_compat_flow_variant(self):
        """Test predict_compat treats flow variables as numeric."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()

        mock_var_1 = create_model_variable(id=VAR_1_ID, code="FeedRate", variant="flow")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Concentration", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_ts = PredictedNumericalTimeSeries(values=[5.0, 5.5, 6.0])
        mock_response = PredictionResponse(
            timestamps=[0, 60, 120], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"FeedRate": [1.0, 1.5, 2.0]}
        timestamps = [0, 60, 120]

        result = model.predict_compat(inputs, timestamps)

        self.assertIn("Concentration", result)
        self.assertEqual(result["Concentration"], [5.0, 5.5, 6.0])

    def test_predict_compat_spectrum_raises_error(self):
        """Test predict_compat raises NotImplementedError for spectrum variables."""
        mock_api = Mock()

        mock_var_spectrum = create_model_variable(id=VAR_1_ID, code="Spectrum", variant="spectrum")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_spectrum]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"Spectrum": [[1.0, 2.0, 3.0]]}
        timestamps = [0]

        with self.assertRaises(NotImplementedError) as context:
            _ = model.predict_compat(inputs, timestamps)

        self.assertIn("Spectrum variables are not yet supported", str(context.exception))

    def test_predict_compat_unknown_variable_code(self):
        """Test predict_compat raises error for unknown variable code."""
        mock_api = Mock()

        mock_var = create_model_variable(id=VAR_1_ID, code="KnownVar", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var]

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"UnknownVar": [1.0, 2.0, 3.0]}
        timestamps = [0, 60, 120]

        with self.assertRaises(ValueError) as context:
            _ = model.predict_compat(inputs, timestamps)

        self.assertIn("Variable code 'UnknownVar' not found", str(context.exception))

    def test_predict_compat_model_not_ready(self):
        """Test predict_compat raises error when model is not ready."""
        from openapi_client.models.model_status import ModelStatus

        mock_api = Mock()
        api_model = create_model(id=MODEL_ID, status=ModelStatus.RUNNING, name="Training Model")
        model = Model(api_model, mock_api)

        inputs = {"Temperature": [25.0]}
        timestamps = [0]

        with self.assertRaises(ValueError) as context:
            _ = model.predict_compat(inputs, timestamps)

        self.assertIn("Training Model", str(context.exception))
        self.assertIn("not ready for prediction", str(context.exception))

    def test_predict_compat_timestamps_unit_seconds(self):
        """Test predict_compat with timestamps in seconds."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="Temperature", variant="numeric")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Glucose", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_ts = PredictedNumericalTimeSeries(values=[10.0, 11.0, 12.0])
        mock_response = PredictionResponse(
            timestamps=[0, 60, 120], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"Temperature": [25.0, 26.0, 27.0]}
        timestamps = [0, 60, 120]

        result = model.predict_compat(inputs, timestamps, timestamps_unit="s")

        # Verify timestamps were passed as-is (already in seconds)
        call_args = mock_api.model_prediction_api_v1_models_model_id_predict_post.call_args
        payload = call_args.kwargs["prediction_payload"]
        self.assertEqual(payload.timestamps, [0, 60, 120])
        self.assertIn("Glucose", result)

    def test_predict_compat_timestamps_unit_minutes(self):
        """Test predict_compat converts minutes to seconds."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="Temperature", variant="numeric")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Glucose", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_ts = PredictedNumericalTimeSeries(values=[10.0, 11.0, 12.0])
        mock_response = PredictionResponse(
            timestamps=[0, 60, 120], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"Temperature": [25.0, 26.0, 27.0]}
        timestamps = [0, 1, 2]  # Minutes

        result = model.predict_compat(inputs, timestamps, timestamps_unit="m")

        # Verify timestamps were converted to seconds (minutes * 60)
        call_args = mock_api.model_prediction_api_v1_models_model_id_predict_post.call_args
        payload = call_args.kwargs["prediction_payload"]
        self.assertEqual(payload.timestamps, [0, 60, 120])
        self.assertIn("Glucose", result)

    def test_predict_compat_timestamps_unit_hours(self):
        """Test predict_compat converts hours to seconds."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="Temperature", variant="numeric")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Glucose", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_ts = PredictedNumericalTimeSeries(values=[10.0, 11.0])
        mock_response = PredictionResponse(
            timestamps=[0, 3600], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"Temperature": [25.0, 26.0]}
        timestamps = [0, 1]  # Hours

        result = model.predict_compat(inputs, timestamps, timestamps_unit="h")

        # Verify timestamps were converted to seconds (hours * 3600)
        call_args = mock_api.model_prediction_api_v1_models_model_id_predict_post.call_args
        payload = call_args.kwargs["prediction_payload"]
        self.assertEqual(payload.timestamps, [0, 3600])
        self.assertIn("Glucose", result)

    def test_predict_compat_timestamps_unit_days(self):
        """Test predict_compat converts days to seconds."""
        from openapi_client.models.prediction_response import PredictionResponse
        from openapi_client.models.predicted_numerical_time_series import PredictedNumericalTimeSeries
        from openapi_client.models.predicted_time_series_data import PredictedTimeSeriesData
        from openapi_client.models.predicted_data_model import PredictedDataModel

        mock_api = Mock()
        mock_var_1 = create_model_variable(id=VAR_1_ID, code="Temperature", variant="numeric")
        mock_var_2 = create_model_variable(id=VAR_2_ID, code="Glucose", variant="numeric")
        mock_api.get_model_variables_api_v1_models_model_id_variables_get.return_value = [mock_var_1, mock_var_2]

        predicted_ts = PredictedNumericalTimeSeries(values=[10.0, 11.0])
        mock_response = PredictionResponse(
            timestamps=[0, 86400], predictions={VAR_2_ID: PredictedDataModel(PredictedTimeSeriesData(predicted_ts))}
        )
        mock_api.model_prediction_api_v1_models_model_id_predict_post.return_value = mock_response

        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"Temperature": [25.0, 26.0]}
        timestamps = [0, 1]  # Days

        result = model.predict_compat(inputs, timestamps, timestamps_unit="d")

        # Verify timestamps were converted to seconds (days * 86400)
        call_args = mock_api.model_prediction_api_v1_models_model_id_predict_post.call_args
        payload = call_args.kwargs["prediction_payload"]
        self.assertEqual(payload.timestamps, [0, 86400])
        self.assertIn("Glucose", result)

    def test_predict_compat_timestamps_unit_invalid(self):
        """Test predict_compat raises error for invalid timestamps_unit."""
        mock_api = Mock()
        api_model = create_model(id=MODEL_ID)
        model = Model(api_model, mock_api)

        inputs = {"Temperature": [25.0]}
        timestamps = [0]

        with self.assertRaises(ValueError) as context:
            _ = model.predict_compat(inputs, timestamps, timestamps_unit="invalid")

        self.assertIn("Invalid timestamps_unit 'invalid'", str(context.exception))
        self.assertIn("Must be one of: s, m, h, d", str(context.exception))

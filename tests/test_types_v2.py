"""Tests for dhl_sdk.types module"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from dhl_sdk.types import (
    CategoricalVariable,
    ExperimentData,
    FlowReference,
    FlowVariable,
    HistoricalPredictionInput,
    LogicalVariable,
    NumericVariable,
    PredictionOutput,
    PropagationPredictionInput,
    SpectraData,
    SpectraExperimentData,
    SpectraPredictionInput,
    SpectrumAxis,
    SpectrumVariable,
    TimeseriesData,
)

# =============================================================================
# Variable Type Tests
# =============================================================================


def test_numeric_variable():
    """Test NumericVariable creation and validation"""
    var = NumericVariable(min=0, max=100, default=50)
    assert var.kind == "numeric"
    assert var.min == 0
    assert var.max == 100
    assert var.default == 50


def test_categorical_variable():
    """Test CategoricalVariable creation"""
    var = CategoricalVariable(categories=["A", "B", "C"], strict=True, default="A")
    assert var.kind == "categorical"
    assert var.categories == ["A", "B", "C"]
    assert var.strict is True


def test_logical_variable():
    """Test LogicalVariable creation"""
    var = LogicalVariable(default=True)
    assert var.kind == "logical"
    assert var.default is True


def test_flow_variable():
    """Test FlowVariable creation and validation"""
    ref = FlowReference(measurement="VAR1", concentration="VAR2")
    var = FlowVariable(flow_type="conti", references=[ref], step_size=60)
    assert var.kind == "flow"
    assert var.flow_type == "conti"
    assert len(var.references) == 1


def test_flow_variable_requires_step_size_for_continuous():
    """Test that continuous flow types require step_size"""
    ref = FlowReference(measurement="VAR1")

    with pytest.raises(ValidationError, match="step_size required"):
        FlowVariable(
            flow_type="conti",
            references=[ref],
            step_size=None,  # Missing!
        )


def test_spectrum_variable():
    """Test SpectrumVariable creation"""
    var = SpectrumVariable(
        x_axis=SpectrumAxis(dimension=100, unit="nm", min=400, max=700),
        y_axis=SpectrumAxis(label="Absorbance"),
    )
    assert var.kind == "spectrum"
    assert var.x_axis.dimension == 100


# =============================================================================
# Timeseries Data Tests
# =============================================================================


def test_timeseries_data_basic():
    """Test basic TimeseriesData creation"""
    ts = TimeseriesData(timestamps=[1, 2, 3], values=[1.0, 2.0, 3.0])
    assert len(ts.timestamps) == 3
    assert len(ts.values) == 3


def test_timeseries_data_validates_positive_timestamps():
    """Test that timestamps must be non-negative"""
    with pytest.raises(ValidationError, match="non-negative"):
        TimeseriesData(timestamps=[-1, 1, 2], values=[1.0, 2.0, 3.0])


def test_timeseries_data_validates_sorted_timestamps():
    """Test that timestamps must be sorted"""
    with pytest.raises(ValidationError, match="sorted"):
        TimeseriesData(
            timestamps=[1, 3, 2],  # Not sorted!
            values=[1.0, 2.0, 3.0],
        )


def test_timeseries_data_validates_length_match():
    """Test that values must match timestamps length"""
    with pytest.raises(ValidationError, match="must match"):
        TimeseriesData(
            timestamps=[1, 2, 3],
            values=[1.0, 2.0],  # Too few values!
        )


# =============================================================================
# Experiment Data Tests
# =============================================================================


def test_experiment_data_run_variant():
    """Test ExperimentData with run variant"""
    data = ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1),
        end_time=datetime(2025, 1, 2),
        timeseries={"VAR1": TimeseriesData(timestamps=[1735689600], values=[42.0])},
    )
    assert data.variant == "run"
    assert data.start_time == datetime(2025, 1, 1)


def test_experiment_data_run_requires_times():
    """Test that run variant requires start_time and end_time"""
    with pytest.raises(ValidationError, match="required for variant='run'"):
        ExperimentData(
            variant="run",
            # Missing start_time and end_time!
            timeseries={"VAR1": TimeseriesData(timestamps=[1], values=[1.0])},
        )


def test_experiment_data_samples_variant():
    """Test ExperimentData with samples variant"""
    data = ExperimentData(
        variant="samples",
        timeseries={
            "VAR1": TimeseriesData(timestamps=[1, 2, 3], values=[1.0, 2.0, 3.0])
        },
    )
    assert data.variant == "samples"
    assert data.start_time is None


def test_experiment_data_validates_timestamp_bounds():
    """Test that timestamps must be within start/end time for run variant"""
    with pytest.raises(ValidationError, match="outside.*bounds"):
        ExperimentData(
            variant="run",
            start_time=datetime(2025, 1, 1, 0, 0, 0),  # 1735689600
            end_time=datetime(2025, 1, 2, 0, 0, 0),  # 1735776000
            timeseries={
                "VAR1": TimeseriesData(
                    timestamps=[1735689600, 1735800000],  # Second timestamp is outside!
                    values=[1.0, 2.0],
                )
            },
        )


# =============================================================================
# Spectra Data Tests
# =============================================================================


def test_spectra_data_basic():
    """Test basic SpectraData creation"""
    spectra = SpectraData(
        timestamps=[1, 2, 3], values=[[1.0, 2.0, 3.0], [1.1, 2.1, 3.1], [1.2, 2.2, 3.2]]
    )
    assert len(spectra.values) == 3
    assert len(spectra.values[0]) == 3


def test_spectra_data_validates_uniform_dimensions():
    """Test that all spectra must have same dimension"""
    with pytest.raises(ValidationError, match="same number of wavelengths"):
        SpectraData(
            timestamps=[1, 2],
            values=[[1.0, 2.0, 3.0], [1.1, 2.1]],  # Different lengths!
        )


def test_spectra_data_validates_timestamps_count():
    """Test that timestamps must match spectra count"""
    with pytest.raises(ValidationError, match="must match spectra count"):
        SpectraData(
            timestamps=[1, 2],  # Only 2 timestamps
            values=[[1.0, 2.0], [1.1, 2.1], [1.2, 2.2]],  # But 3 spectra!
        )


def test_spectra_experiment_data():
    """Test SpectraExperimentData creation"""
    data = SpectraExperimentData(
        variant="run",
        spectra=SpectraData(timestamps=[1, 2], values=[[1.0, 2.0], [1.1, 2.1]]),
        inputs={"INPUT1": [42.0, 43.0]},
    )
    assert data.variant == "run"
    assert len(data.spectra.values) == 2


# =============================================================================
# Prediction Input Tests
# =============================================================================


def test_spectra_prediction_input():
    """Test SpectraPredictionInput creation"""
    input_data = SpectraPredictionInput(
        spectra=[[1.0, 2.0, 3.0], [1.1, 2.1, 3.1]], inputs={"INPUT1": [42.0, 43.0]}
    )
    assert len(input_data.spectra) == 2
    assert "INPUT1" in input_data.inputs


def test_propagation_prediction_input():
    """Test PropagationPredictionInput creation"""
    input_data = PropagationPredictionInput(
        timestamps=[0, 24, 48],
        unit="h",
        inputs={"VAR1": [42.0], "VAR2": [0.3, 0.4, 0.5]},
        confidence=0.8,
    )
    assert input_data.unit == "h"
    assert input_data.confidence == 0.8


def test_historical_prediction_input():
    """Test HistoricalPredictionInput creation"""
    input_data = HistoricalPredictionInput(
        timestamps=[86400, 172800],
        steps=[0, 1],
        unit="s",
        inputs={"VAR1": [42.0], "VAR2": [0.3, 0.4]},
    )
    assert len(input_data.steps) == 2


def test_historical_prediction_input_validates_steps_length():
    """Test that steps must match timestamps length"""
    with pytest.raises(ValidationError, match="must match timestamps length"):
        HistoricalPredictionInput(
            timestamps=[1, 2, 3],
            steps=[0, 1],  # Too few steps!
            unit="s",
            inputs={"VAR1": [1.0]},
        )


# =============================================================================
# Prediction Output Tests
# =============================================================================


def test_prediction_output():
    """Test PredictionOutput creation"""
    output = PredictionOutput(
        outputs={"OUTPUT1": [1.0, 2.0], "OUTPUT2": [3.0, 4.0]},
        confidence_intervals={"OUTPUT1": {"lower": [0.9, 1.9], "upper": [1.1, 2.1]}},
        metadata={"model_id": "123", "model_name": "Test Model"},
    )
    assert "OUTPUT1" in output.outputs
    assert output.metadata["model_id"] == "123"


# =============================================================================
# Integration Tests
# =============================================================================


def test_full_experiment_workflow():
    """Test complete experiment data creation workflow"""
    # Create experiment data with multiple variables
    data = ExperimentData(
        variant="run",
        start_time=datetime(2025, 1, 1, 0, 0, 0),
        end_time=datetime(2025, 1, 3, 0, 0, 0),
        timeseries={
            "TEMP": TimeseriesData(
                timestamps=[1735689600, 1735776000], values=[25.5, 26.0]
            ),
            "PH": TimeseriesData(
                timestamps=[1735689600, 1735776000, 1735862400], values=[7.2, 7.1, 7.0]
            ),
            "STATUS": TimeseriesData(timestamps=[1735689600], values=["Running"]),
        },
    )

    # Verify structure
    assert len(data.timeseries) == 3
    assert "TEMP" in data.timeseries
    assert len(data.timeseries["PH"].values) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

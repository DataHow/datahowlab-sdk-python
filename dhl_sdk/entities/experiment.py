# Disable import cycle check: Experiment and Product/Client have bidirectional references
# (those are only relevant for type checking)
# pyright: reportImportCycles=false
from typing import TYPE_CHECKING, Any, final
from typing_extensions import override, TypedDict

if TYPE_CHECKING:
    from dhl_sdk import DataHowLabClient
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.experiment import Experiment as OpenAPIExperiment
    from openapi_client.models.experiment_create import ExperimentCreate
    from openapi_client.models.process_unit_code import ProcessUnitCode
    from openapi_client.models.raw_experiment_data_input_value import RawExperimentDataInputValue
    from openapi_client.models.variantdetails import Variantdetails
    from dhl_sdk.entities.product import Product
    from dhl_sdk.entities.variable import Variable


class CompatDataValue(TypedDict):
    """Compat data format for a single variable."""

    values: list[Any]  # pyright: ignore[reportExplicitAny] - OpenAPI generates StrictFloat/StrictStr/StrictBool without common base
    timestamps: list[Any]  # pyright: ignore[reportExplicitAny] - OpenAPI uses StrictInt which doesn't align with standard int


@final
class Experiment:
    def __init__(self, experiment: "OpenAPIExperiment", api: "DefaultApi"):
        self._experiment = experiment
        self._cached_variables = None
        self._api = api

    @override
    def __str__(self) -> str:
        return f"Experiment({self._experiment.display_name})"

    @property
    def id(self) -> str:
        return self._experiment.id

    @property
    def display_name(self) -> str:
        return self._experiment.display_name

    @property
    def product_id(self) -> str:
        return self._experiment.product_id

    @property
    def variable_ids(self) -> list[str]:
        return self._experiment.variable_ids

    @property
    def description(self) -> str:
        return self._experiment.description

    @property
    def process_unit(self) -> "ProcessUnitCode":
        """Process unit code for the experiment."""
        return self._experiment.process_unit

    @property
    def variant_details(self) -> "Variantdetails":
        """
        Variant-specific details for the experiment.

        Returns
        -------
        Variantdetails
            Union of RunDetails (with start_time/end_time) or SamplesDetails.
        """
        return self._experiment.variant_details

    @property
    def extra(self) -> dict[str, Any] | None:  # pyright: ignore[reportExplicitAny] - Extra metadata accepts arbitrary user data
        """
        Extra experiment metadata.

        Returns
        -------
        dict[str, Any] | None
            Dictionary of extra data or None if not set.
        """
        return self._experiment.extra

    @property
    def variant(self) -> str:
        """
        Extract variant type string from variant_details (backward compatibility).

        Returns
        -------
        str
            'run' for RunDetails variant, 'samples' for SamplesDetails variant.
        """
        from openapi_client.models.run_details import RunDetails
        from openapi_client.models.samples_details import SamplesDetails

        actual = self.variant_details.actual_instance
        if isinstance(actual, RunDetails):
            return "run"
        elif isinstance(actual, SamplesDetails):
            return "samples"
        else:
            return "unknown"

    @property
    def start_time(self) -> str | None:
        """
        Start time of the experiment (only for 'run' variant).

        Returns
        -------
        str | None
            Start time string if variant is RunDetails, None otherwise.
        """
        from openapi_client.models.run_details import RunDetails

        actual = self.variant_details.actual_instance
        if isinstance(actual, RunDetails):
            return actual.start_time
        return None

    @property
    def end_time(self) -> str | None:
        """
        End time of the experiment (only for 'run' variant).

        Returns
        -------
        str | None
            End time string if variant is RunDetails, None otherwise.
        """
        from openapi_client.models.run_details import RunDetails

        actual = self.variant_details.actual_instance
        if isinstance(actual, RunDetails):
            return actual.end_time
        return None

    @property
    def tags(self) -> dict[str, str]:
        """
        Tags associated with the experiment.

        Returns
        -------
        dict[str, str]
            Dictionary of tag key-value pairs. Returns empty dict if no tags.
        """
        return self._experiment.tags or {}

    def get_data(self) -> dict[str, "RawExperimentDataInputValue"]:
        return self._api.get_experiment_data_api_v1_experiments_experiment_id_data_get(experiment_id=self.id)

    def get_data_compat(self) -> dict[str, CompatDataValue | None]:
        raw_data = self.get_data()
        variables = self.get_variables()

        # Create a mapping from variable ID to variable code
        var_id_to_code = {var.id: var.code for var in variables}

        result: dict[str, CompatDataValue | None] = {}
        for var_id, raw_value in raw_data.items():
            var_code = var_id_to_code.get(var_id, var_id)

            actual = raw_value.actual_instance
            if actual is None:
                result[var_code] = None
                continue

            inner = actual.actual_instance
            if inner is None:
                result[var_code] = None
                continue

            result[var_code] = {"values": inner.values, "timestamps": inner.timestamps}

        return result

    def get_variables(self) -> list["Variable"]:
        from dhl_sdk.entities.variable import Variable

        if self._cached_variables is not None:
            return self._cached_variables

        variables: list["Variable"] = []
        for variable_id in self.variable_ids:
            api_variable = self._api.get_variable_by_id_api_v1_variables_variable_id_get(variable_id=variable_id)
            variables.append(Variable(api_variable))
        self._cached_variables = variables
        return variables

    def get_product(self) -> "Product":
        from dhl_sdk.entities.product import Product

        api_product = self._api.get_product_by_id_api_v1_products_product_id_get(product_id=self.product_id)
        return Product(api_product, self._api)


class ExperimentRequest:
    _experiment_create: "ExperimentCreate"

    def __init__(self, experiment_create: "ExperimentCreate"):
        self._experiment_create = experiment_create

    @override
    def __str__(self) -> str:
        return f"ExperimentRequest({self._experiment_create.name})"

    @staticmethod
    def from_compat_data(
        variables: list["Variable"], compat_data: dict[str, CompatDataValue | None]
    ) -> dict[str, "RawExperimentDataInputValue | None"]:
        """
        Convert compat data format to OpenAPI format.

        Args:
            variables: List of variables from the experiment
            compat_data: Data in compat format {variable_code: {"values": [...], "timestamps": [...]}}

        Returns:
            Data in OpenAPI format {variable_id: RawExperimentDataInputValue}

        Raises:
            ValueError: If variable codes are non-unique or if spectra variant is encountered
        """
        from openapi_client.models.numeric_details import NumericDetails
        from openapi_client.models.categorical_details import CategoricalDetails
        from openapi_client.models.flow_details import FlowDetails
        from openapi_client.models.logical_details import LogicalDetails
        from openapi_client.models.spectrum_details import SpectrumDetails
        from openapi_client.models.numerical_time_series_with_timestamps import NumericalTimeSeriesWithTimestamps
        from openapi_client.models.categorical_time_series_with_timestamps import CategoricalTimeSeriesWithTimestamps
        from openapi_client.models.logical_time_series_with_timestamps import LogicalTimeSeriesWithTimestamps
        from openapi_client.models.raw_time_series_data import RawTimeSeriesData
        from openapi_client.models.raw_experiment_data_input_value import RawExperimentDataInputValue

        # Create mapping from variable code to variable
        code_to_variable: dict[str, "Variable"] = {}
        for var in variables:
            if var.code in code_to_variable:
                raise ValueError(f"Non-unique variable code found: {var.code}")
            code_to_variable[var.code] = var

        # Convert compat data to OpenAPI format
        result: dict[str, "RawExperimentDataInputValue | None"] = {}
        for var_code, data in compat_data.items():
            if var_code not in code_to_variable:
                raise ValueError(f"Variable code '{var_code}' not found in provided variables")

            var = code_to_variable[var_code]

            if data is None:
                result[var.id] = None
                continue

            # Determine the type based on variable's variant details
            variant_details = var.variant_details

            if isinstance(variant_details.actual_instance, NumericDetails):
                ts = NumericalTimeSeriesWithTimestamps(values=data["values"], timestamps=data["timestamps"])
                result[var.id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=ts))
            elif isinstance(variant_details.actual_instance, CategoricalDetails):
                ts = CategoricalTimeSeriesWithTimestamps(values=data["values"], timestamps=data["timestamps"])
                result[var.id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=ts))
            elif isinstance(variant_details.actual_instance, LogicalDetails):
                ts = LogicalTimeSeriesWithTimestamps(values=data["values"], timestamps=data["timestamps"])
                result[var.id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=ts))
            elif isinstance(variant_details.actual_instance, FlowDetails):
                # Flow/Feed is also numerical
                ts = NumericalTimeSeriesWithTimestamps(values=data["values"], timestamps=data["timestamps"])
                result[var.id] = RawExperimentDataInputValue(actual_instance=RawTimeSeriesData(actual_instance=ts))
            elif isinstance(variant_details.actual_instance, SpectrumDetails):
                raise NotImplementedError(f"Spectra variant is not supported for variable '{var_code}'")
            else:
                result[var.id] = None

        return result

    @staticmethod
    def new(
        name: str,
        description: str,
        product: "Product",
        process_unit: "ProcessUnitCode",
        variant_details: "Variantdetails",
        data: dict[str, "RawExperimentDataInputValue"],
        subunit: str | None = None,
        tags: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,  # pyright: ignore[reportExplicitAny] - Arbitrary user metadata
    ) -> "ExperimentRequest":
        from openapi_client.models.experiment_create import ExperimentCreate

        experiment_create = ExperimentCreate(
            name=name,
            description=description,
            productId=product.id,
            processUnit=process_unit,
            variantDetails=variant_details,
            data=data,
            subunit=subunit or "",
            tags=tags,
            extra=extra,
        )
        return ExperimentRequest(experiment_create)

    def create(self, client: "DataHowLabClient") -> Experiment:
        from dhl_sdk.error_handler import handle_validation_errors

        @handle_validation_errors
        def _create():
            return client.api.create_experiment_api_v1_experiments_post(experiment_create=self._experiment_create)

        created_experiment = _create()
        return Experiment(created_experiment, client.api)

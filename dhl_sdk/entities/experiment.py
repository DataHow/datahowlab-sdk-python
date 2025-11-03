from datetime import datetime
from typing import TYPE_CHECKING, Any
from typing_extensions import override

if TYPE_CHECKING:
    from openapi_client.api.default_api import DefaultApi
    from openapi_client.models.experiment import Experiment as OpenAPIExperiment
    from openapi_client.models.experiment_create import ExperimentCreate
    from openapi_client.models.process_unit_code import ProcessUnitCode
    from openapi_client.models.raw_experiment_data_input_value import RawExperimentDataInputValue
    from dhl_sdk.entities.product import Product
    from dhl_sdk.entities.variable import Variable


class Experiment:
    _experiment: "OpenAPIExperiment"
    _cached_variables: list["Variable"] | None

    def __init__(self, experiment: "OpenAPIExperiment"):
        self._experiment = experiment
        self._cached_variables = None

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
    def start_time(self) -> str | None:
        return self._experiment.start_time

    @property
    def variant(self) -> str:
        return self._experiment.variant.value

    def get_data(self, api: "DefaultApi") -> dict[str, "RawExperimentDataInputValue"]:
        return api.get_experiment_data_api_v1_experiments_experiment_id_data_get(experiment_id=self.id)

    def get_data_compat(self, api: "DefaultApi") -> dict[str, Any]:
        raw_data = self.get_data(api)
        variables = self.get_variables(api)

        # Create a mapping from variable ID to variable code
        var_id_to_code = {var.id: var.code for var in variables}

        result: dict[str, Any] = {}
        for var_id, raw_value in raw_data.items():
            var_code = var_id_to_code.get(var_id, var_id)
            value_dict = raw_value.to_dict() if hasattr(raw_value, "to_dict") else raw_value
            # Extract only values and timestamps for timeseries
            if isinstance(value_dict, dict) and "values" in value_dict and "timestamps" in value_dict:
                result[var_code] = {"values": value_dict["values"], "timestamps": value_dict["timestamps"]}
            else:
                result[var_code] = value_dict
        return result

    def get_variables(self, api: "DefaultApi") -> list["Variable"]:
        from dhl_sdk.entities.variable import Variable

        if self._cached_variables is not None:
            return self._cached_variables

        variables = []
        for variable_id in self.variable_ids:
            api_variable = api.get_variable_by_id_api_v1_variables_variable_id_get(variable_id=variable_id)
            variables.append(Variable(api_variable))
        self._cached_variables = variables
        return variables

    def get_product(self, api: "DefaultApi") -> "Product":
        from dhl_sdk.entities.product import Product

        api_product = api.get_product_by_id_api_v1_products_product_id_get(product_id=self.product_id)
        return Product(api_product)


class ExperimentRequest:
    _experiment_create: "ExperimentCreate"

    def __init__(self, experiment_create: "ExperimentCreate"):
        self._experiment_create = experiment_create

    @override
    def __str__(self) -> str:
        return f"ExperimentRequest({self._experiment_create.name})"

    @staticmethod
    def new(
        name: str,
        description: str,
        product: "Product",
        process_unit: "ProcessUnitCode",
        start_time: datetime,
        end_time: datetime,
        data: dict[str, "RawExperimentDataInputValue"],
        subunit: str | None = None,
        tags: dict[str, str] | None = None,
        extra: dict[str, Any] | None = None,
    ) -> "ExperimentRequest":
        from openapi_client.models.experiment_create import ExperimentCreate

        display_name_parts = [product.code, name]
        if subunit:
            display_name_parts.append(subunit)
        display_name = "-".join(display_name_parts)

        experiment_create = ExperimentCreate(
            name=display_name,
            description=description,
            productId=product.id,
            subunit=subunit or "",
            processUnit=process_unit,
            startTime=start_time,
            endTime=end_time,
            data=data,
            tags=tags,
            extra=extra,
        )
        return ExperimentRequest(experiment_create)

    def create(self, api: "DefaultApi") -> Experiment:
        created_experiment = api.create_experiment_api_v1_experiments_post(experiment_create=self._experiment_create)
        return Experiment(created_experiment)

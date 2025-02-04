# Validations

## Creating a new Entity

### Product 

```python 
product = Product.new(name="ExampleProduct", code="EXPRD", description="Example Product")
client.create(product)
``` 

* Product `code` and `name` should not be empty
* Product `code` should have between 1 and 6 characters

* If the product is already imported in the DB, the new entity creation will be skipped
* Product `code` and `name` must be unique (no duplicates in the database) 


### Variable

```python 
variable = Variable.new(code="Var1", 
                        name="SDK Variable 1", 
                        description="This is a variable created with the SDK", 
                        measurement_unit="g/l", 
                        variable_group="X Variables", 
                        variable_type=VariableNumeric()
                        )
client.create(variable)
``` 

* Variable `code`, `name`, `measurement_unit` and `variable_group` can't be empty 
* `variable_group` must be valid. Use `variable_groups = Variable.get_valid_variable_groups(client)` to check all valid Variable Groups. 

* If Variable is already imported, the new entity creation will be skipped.
* Variable `code` and `name` must be unique (no duplicates in the database) 
* Measurement Unit is mandatory

If the new Variable is of type `Feeds/Flows` (and you're using the VariableFlow() class), this adds a few extra validations: 

* References are mandatory
* `measurementId` must be the ID of a `X Variable` already imported.
* `concentrationId` must be ID of a `Feed Concentration` variable already imported. 

### Experiment

```python
new_data = {
            "EXv1": {
                "timestamps": [
                    1600674350,
                    1600760750,
                    1600847150,

                ],
                "values": [
                    5.1,
                    3.5,
                    1.3,
                ]
            },
            "EXv2": {
                "timestamps": [
                    1600674350],
                "values": [
                    "A"]

            }
}

new_experiment = Experiment.new(name="Example Experiment",
                                description="new experiment example for sdk",
                                product=product,
                                variables=variables,
                                data_type="run",
                                data=new_data,
                                variant="run",
                                start_time="2020-09-21T08:45:50Z", 
                                end_time="2020-09-30T08:45:50Z")
client.create(new_experiment)
```

Importing a new experiment splits the validation between the new experiment metadata and the data associated with that experiment. So, following the same logic:

#### Experiment Metadata

* Experiment `name` and `description` can't be empty
* Experiment `variant` has to be one of two options (`run` or `samples`). `run` is for time series data and `samples` is for sampled data.
    * If the `variant` is `run`, then the arguments `start_time` and `end_time` are mandatory.
* Experiment `data_type` has to be one of two options (`run` or `spectra`). `run` is for cultivation experiments and `spectra` is for spectra experiments.
* If the Experiment is already present in the DB, the import will be skipped. 
* `product` and all `variables` need to be already present in the DB.
* `data` needs to be in a `dict` format and not be empty. 

#### Experiment data

* If one of the variable codes indicated in the argument `variables` is not present in `data`, an Error will be thrown. 
* Inside each key of the `data` dictionary, a new dictionary must be present with `timestamps` and `values` as mandatory fields.
* If `timestamps` or `values` are missing from any variable, an Error will be thrown. 
* If the data inside `timestamps` or `values` is not a list, then the data format is not valid. Even if we only have one value, it should be inside a list.
* The length of the lists inside `timestamps` and `values` must match. For each `timestamp` we need a `value`.
* The `timestamps` need to be in seconds in Unix time. 
* The `timestamps` need to be sorted. 
* For the `run` variant, all the timestamps must be between the value of `start_time` and `end_time` of the experiment. 

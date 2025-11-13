# Known Issues

## OpenAPI Deserialization Error with Variable Variant Details

**Issue**: When creating or retrieving variables, there is an OpenAPI deserialization error with `Variantdetails` oneOf schema.

**Error Message**:
```
ValueError: Multiple matches found when deserializing the JSON string into Variantdetails with oneOf schemas: CategoricalDetailsOutput, FlowDetailsOutput, LogicalDetailsOutput, NumericDetailsOutput, SpectrumDetailsOutput. Details: 1 validation error for FlowDetailsOutput
type
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

**Root Cause**: The API returns `FlowDetailsOutput` with a nullable `type` field, but the OpenAPI-generated Pydantic models expect a non-null string. This causes the oneOf discriminator to fail to determine the correct variant type.

**Workaround**: 
- Product creation works fine
- Experiment data retrieval works fine  
- Variable and experiment creation with variables currently blocked by this issue

**Fix Required**: 
1. Update the OpenAPI schema (`openapi.json`) to properly define nullable fields in variant details
2. Regenerate the OpenAPI client with: `openapi-generator-cli generate -i openapi.json -g python -o dhl_api`

**Tracking**: This issue affects:
- `client.get_variables()` 
- `VariableRequest.create()`
- `ExperimentRequest.new()` (when using variables that need to be fetched)

**Status**: Pending fix in OpenAPI schema

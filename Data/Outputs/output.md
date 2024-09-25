# Stern/Backoffice Tool Documentation

## Summary
This documentation provides an overview of the processes and tools used within the stern/Backoffice tool for generating Swagger-based API documentation. The latest methods, libraries, and integration points are highlighted, with a special focus on the implementation of `servant-swagger-ui` for local Swagger documentation, feature flags, and various SCIM-related documentations.

## Detailed Analysis

### Latest Information from 2024-07-09 Documents

- **Integration of `servant-swagger-ui`**:
    - The `servant-swagger-ui` has been integrated with the `brig` service to facilitate easier interaction with API documentation.
    - This enables local viewing of Swagger documentation, ensuring users can explore, make requests, and generate client code from the API documentation interactively.

- **SCIM Documentation**:
    - Features related to SCIM, such as the `validateSAMLemails` feature, are thoroughly documented in `docs/reference/spar-braindump.md`.

- **Feature Flags**:
    - Documentation includes notes on specific feature flags, such as `setEmailVisibility`, detailing their usage and implications within the API.

- **Swagger Documentation Instructions**:
    - Detailed instructions on accessing and viewing Swagger documentation locally are provided (referenced as #1388).

- **Cassandra Schema**:
    - Updated `cassandra-schema.cql` files are included, indicating changes and improvements in the database schema.

- **Unused Registration Flow**:
    - Notes are added concerning unused registration flows, which may affect how developers interact with and test the APIs.

### Semi-Automatic Swagger Documentation with Servant (Date: None)
- The system utilizes the `servant-swagger2` library to semi-automatically generate Swagger documentation.
- The use of the `schema-profunctor` library aids in creating "schemas" for the input and output types used in the Servant APIs, which encapsulate the information needed for JSON serialization/deserialization, alongside documentation and metadata for Swagger generation.

### 2023-01-16 Information
- Swagger/OpenAPI documentation in the staging system is accurate and complete up to bots/services and event notification payloads.
- This documentation facilitates three primary uses:
    1. As a reference.
    2. For generating client code.
    3. For interactively exploring the API by making requests.

### Code Snippets and Examples
Here is an example of how `servant-swagger-ui` can be integrated:

```haskell
import Servant
import Servant.Swagger.UI

type API = ...

server :: Server API
server = ...

main :: IO ()
main = run 8080 $ serve (Proxy :: Proxy API) server
```

To view Swagger documentation locally, you might follow these steps:
1. Ensure the `servant-swagger-ui` is properly installed and configured.
2. Run the server and open the provided local URL in your browser.

## Contradictions

**Documents Dated 'None' vs. Other Dated Documents**

- **Semi-Automatic Generation vs. Updates in 2024-07-09**:
    - The "None" dated document discusses semi-automatic Swagger documentation generation using `servant-swagger2`.
    - The latest documents from 2024-07-09 detail the specific integration of `servant-swagger-ui` into the `brig` service, emphasizing how Swagger documentation can be accessed locally.

These points complement rather than contradict they highlight the toolsets (one for generation and the other for visualization and interaction).

**Documents Dated 'None' vs. 2023-01-16**:
- **Completeness of Documentation**:
    - The "None" dated document does not give specifics on the completeness of the Swagger documentation.
    - The 2023-01-16 document assures the completeness up to bots/services and event notification payloads.

By including both these perspectives, users get a detailed understanding of the documentation's completeness and the evolution of tools used.
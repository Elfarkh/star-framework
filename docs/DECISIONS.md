# Decision 001

Date

2026-09-16

Decision

Repository name:
star-framework

Python package:
star

Reason

Allows future STAR implementations while keeping
the package name short.

# Decision 002

Sensor abstraction postponed.

Reason

Follow the Rule of Three.

# Decision 003

## Title

Ship static reference datasets with STAR

## Decision

Static geospatial reference datasets required by the framework (e.g. Landsat WRS-2 grid) will be distributed as part of the STAR package.

## Rationale

These datasets change very rarely and are required by multiple modules. Bundling them with STAR ensures:

- offline functionality,
- reproducibility,
- no external dependencies,
- faster execution.

## Consequences

STAR can determine Landsat tiles without requiring an internet connection.
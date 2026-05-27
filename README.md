# Send OTLP Shim

A simple workloadless charm that lets users manually point to an OTLP endpoint to send data to.

Has three configuration options:
- endpoint: the endpoint (including protocol and port) to send OTLP data to.
- insecure: whether to allow insecure traffic (e.g. https with self signed certificates)
- telemetries: what telemetries are supported by the OTLP endpoint (default to logs, metrics, and traces). Needs a validator to ensure these are the only valid values for this config option.

The OTLP interface is defined in charmlibs, and used in opentelemetry-collector-operator
- opentelemetry-collector-operator: https://github.com/canonical/opentelemetry-collector-operator
- charmlibs: https://github.com/canonical/charmlibs/tree/main/interfaces/otlp
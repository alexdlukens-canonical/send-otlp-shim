# Send OTLP Shim

A simple workloadless charm that lets users manually point to an OTLP endpoint to send data to.

Has three configuration options:
- endpoint: the endpoint (including protocol and port) to send OTLP data to.
- insecure: whether to allow insecure traffic (e.g. https with self signed certificates)
- telemetries: what telemetries are supported by the OTLP endpoint (default to logs, metrics, and traces). Needs a validator to ensure these are the only valid values for this config option.

The OTLP interface is defined in charmlibs, and used in opentelemetry-collector-operator
- opentelemetry-collector-operator: https://github.com/canonical/opentelemetry-collector-operator
- charmlibs: https://github.com/canonical/charmlibs/tree/main/interfaces/otlp

## Implemented behavior

- Provides relation endpoint `receive-otlp` with interface `otlp`.
- Publishes one OTLP endpoint to related applications using `charmlibs.interfaces.otlp.OtlpProvider`.
- Reconciles on `config-changed` and `receive-otlp-relation-joined`.

## Validation rules

- `endpoint` is required and must include a URL scheme and host.
- `telemetries` must be a comma-separated subset of `logs`, `metrics`, `traces`.
- `telemetries` values are normalized to lowercase and deduplicated while preserving order.
- Invalid configuration sets `BlockedStatus` with an actionable message.
- Valid configuration sets `ActiveStatus` and republishes relation data.

## Notes

- Protocol inference currently maps `grpc`/`grpcs` schemes, or port `4317`, to OTLP protocol `grpc`; all other endpoints are published as protocol `http`.
- Unit tests cover config validation, status transitions, and relation data publication.
from __future__ import annotations

import json

from ops import ActiveStatus, BlockedStatus
from ops.testing import Harness

from charm import SendOtlpShimCharm

META = """
name: send-otlp-shim
provides:
    receive-otlp:
        interface: otlp
"""

CONFIG = """
options:
    endpoint:
        type: string
        default: ""
    insecure:
        type: boolean
        default: false
    telemetries:
        type: string
        default: logs,metrics,traces
"""


def test_invalid_endpoint_sets_blocked_status() -> None:
    harness = Harness(SendOtlpShimCharm, meta=META, config=CONFIG)
    harness.begin()
    harness.set_leader(True)

    harness.update_config({"endpoint": "localhost:4317"})

    assert isinstance(harness.model.unit.status, BlockedStatus)
    assert "Invalid endpoint" in harness.model.unit.status.message


def test_invalid_telemetries_sets_blocked_status() -> None:
    harness = Harness(SendOtlpShimCharm, meta=META, config=CONFIG)
    harness.begin()
    harness.set_leader(True)

    harness.update_config(
        {
            "endpoint": "http://collector.example:4318",
            "telemetries": "logs,profiles",
        }
    )

    assert isinstance(harness.model.unit.status, BlockedStatus)
    assert "Invalid telemetries" in harness.model.unit.status.message


def test_valid_config_publishes_otlp_endpoint() -> None:
    harness = Harness(SendOtlpShimCharm, meta=META, config=CONFIG)
    harness.begin()
    harness.set_leader(True)

    relation_id = harness.add_relation("receive-otlp", "otelcol")
    harness.add_relation_unit(relation_id, "otelcol/0")

    harness.update_config(
        {
            "endpoint": "https://collector.example:4318/v1/otlp",
            "insecure": True,
            "telemetries": " traces, metrics, traces,logs ",
        }
    )

    app_data = harness.get_relation_data(relation_id, harness.charm.app.name)
    assert "endpoints" in app_data

    payload = json.loads(app_data["endpoints"])
    assert payload == [
        {
            "protocol": "http",
            "endpoint": "https://collector.example:4318/v1/otlp",
            "telemetries": ["traces", "metrics", "logs"],
            "insecure": True,
        }
    ]
    assert isinstance(harness.model.unit.status, ActiveStatus)


def test_port_4317_infers_grpc_protocol() -> None:
    harness = Harness(SendOtlpShimCharm, meta=META, config=CONFIG)
    harness.begin()
    harness.set_leader(True)

    relation_id = harness.add_relation("receive-otlp", "otelcol")
    harness.add_relation_unit(relation_id, "otelcol/0")

    harness.update_config(
        {
            "endpoint": "http://collector.example:4317",
            "telemetries": "logs,metrics",
        }
    )

    app_data = harness.get_relation_data(relation_id, harness.charm.app.name)
    payload = json.loads(app_data["endpoints"])
    assert payload[0]["protocol"] == "grpc"

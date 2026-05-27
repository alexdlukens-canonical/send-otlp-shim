from __future__ import annotations

import jubilant


CHARM_FILE = "./send-otlp-shim_amd64.charm"


def test_deploy(juju: jubilant.Juju):
    juju.deploy(
        CHARM_FILE,
        config={
            "endpoint": "http://otlp-collector.example.com:4318",
            "telemetries": "logs,metrics,traces",
        },
    )
    juju.wait(jubilant.all_active)

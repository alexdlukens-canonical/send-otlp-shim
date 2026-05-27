#!/usr/bin/env python3

from __future__ import annotations

from typing import Final
from urllib.parse import urlparse

from charmlibs.interfaces.otlp import OtlpProvider
from ops import ActiveStatus, BlockedStatus, CharmBase, EventBase, main

ALLOWED_TELEMETRIES: Final[set[str]] = {"logs", "metrics", "traces"}
RELATION_NAME: Final[str] = "receive-otlp"


class SendOtlpShimCharm(CharmBase):
    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.config_changed, self._reconcile)
        self.framework.observe(self.on[RELATION_NAME].relation_joined, self._reconcile)

    def _reconcile(self, _: EventBase) -> None:
        endpoint = self._endpoint_from_config()
        if endpoint is None:
            self.unit.status = BlockedStatus("Invalid endpoint: include scheme and host")
            return

        telemetries = self._telemetries_from_config()
        if telemetries is None:
            allowed = ",".join(sorted(ALLOWED_TELEMETRIES))
            self.unit.status = BlockedStatus(
                f"Invalid telemetries: use comma-separated values from {allowed}"
            )
            return

        insecure = bool(self.config.get("insecure", False))
        protocol = self._infer_protocol(endpoint)

        OtlpProvider(self, relation_name=RELATION_NAME).add_endpoint(
            protocol=protocol,
            endpoint=endpoint,
            telemetries=telemetries,
            insecure=insecure,
        ).publish()
        self.unit.status = ActiveStatus()

    def _endpoint_from_config(self) -> str | None:
        endpoint = str(self.config.get("endpoint", "")).strip()
        if not endpoint:
            return None

        parsed = urlparse(endpoint)
        if not parsed.scheme or not parsed.hostname:
            return None
        return endpoint

    def _telemetries_from_config(self) -> list[str] | None:
        raw_telemetries = str(self.config.get("telemetries", "")).strip()
        if not raw_telemetries:
            return None

        parsed = [item.strip().lower() for item in raw_telemetries.split(",") if item.strip()]
        if not parsed:
            return None

        if any(item not in ALLOWED_TELEMETRIES for item in parsed):
            return None

        return list(dict.fromkeys(parsed))

    def _infer_protocol(self, endpoint: str) -> str:
        parsed = urlparse(endpoint)
        if parsed.scheme in {"grpc", "grpcs"}:
            return "grpc"

        if parsed.port == 4317:
            return "grpc"

        return "http"


if __name__ == "__main__":
    main(SendOtlpShimCharm)

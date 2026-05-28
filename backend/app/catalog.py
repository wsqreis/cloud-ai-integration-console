from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Protocol

from app.data import CAPABILITY_MAP, INTEGRATIONS, METRICS, WORKFLOWS
from app.models import AutomationFlow, Integration, Overview, OverviewMetric, WorkflowStep


class CatalogAdapter(Protocol):
    def get_integrations(self) -> list[Integration]: ...

    def get_workflows(self) -> list[AutomationFlow]: ...

    def get_overview(self) -> Overview: ...


class StaticCatalogAdapter:
    def get_integrations(self) -> list[Integration]:
        return INTEGRATIONS

    def get_workflows(self) -> list[AutomationFlow]:
        return WORKFLOWS

    def get_overview(self) -> Overview:
        return Overview(
            metrics=METRICS,
            capability_map=CAPABILITY_MAP,
            recommended_next_actions=[
                "Validate degraded connector retry behavior.",
                "Review AI-generated actions before publishing workflow changes.",
                "Add customer-specific mappings after the prototype is approved.",
            ],
        )


class JsonCatalogAdapter:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load(self) -> dict:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return payload

    def get_integrations(self) -> list[Integration]:
        return [Integration.model_validate(item) for item in self._load()["integrations"]]

    def get_workflows(self) -> list[AutomationFlow]:
        workflows: list[AutomationFlow] = []
        for item in self._load()["workflows"]:
            workflows.append(
                AutomationFlow(
                    id=item["id"],
                    title=item["title"],
                    summary=item["summary"],
                    business_value=item["business_value"],
                    systems=item["systems"],
                    steps=[WorkflowStep.model_validate(step) for step in item["steps"]],
                )
            )
        return workflows

    def get_overview(self) -> Overview:
        payload = self._load()
        return Overview(
            metrics=[OverviewMetric.model_validate(metric) for metric in payload["metrics"]],
            capability_map=payload["capability_map"],
            recommended_next_actions=payload["recommended_next_actions"],
        )


def get_catalog_adapter() -> CatalogAdapter:
    catalog_path = Path(os.getenv("APP_CATALOG_PATH", "./data/catalog.json"))
    if catalog_path.exists():
        return JsonCatalogAdapter(catalog_path)
    return StaticCatalogAdapter()


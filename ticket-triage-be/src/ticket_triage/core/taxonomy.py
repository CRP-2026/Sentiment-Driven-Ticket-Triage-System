from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

@dataclass(frozen=True)
class AspectDefinition:
    id: str
    name_vi: str
    description: str
    department: str
    weight: float

class Taxonomy:
    """Quản lý danh mục khía cạnh từ file YAML."""

    def __init__(self, aspects: list[AspectDefinition]):
        self._aspects = {a.id: a for a in aspects}

    @classmethod
    def load_from_yaml(cls, yaml_path: str | Path) -> "Taxonomy":
        path = Path(yaml_path)
        if not path.is_file():
            raise FileNotFoundError(f"Aspects config not found at: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        aspect_items = []
        raw_list = data.get("aspects", [])
        seen_ids = set()

        for item in raw_list:
            aspect_id = str(item["id"]).strip()
            if aspect_id in seen_ids:
                raise ValueError(f"Duplicate aspect ID detected: {aspect_id}")
            seen_ids.add(aspect_id)

            weight = float(item.get("weight", 1.0))
            if not (0.0 <= weight <= 2.0):
                raise ValueError(f"Invalid weight {weight} for aspect {aspect_id}, must be in [0.0, 2.0]")

            aspect_items.append(
                AspectDefinition(
                    id=aspect_id,
                    name_vi=str(item.get("name_vi", aspect_id)),
                    description=str(item.get("description", "")),
                    department=str(item.get("department", "General")),
                    weight=weight,
                )
            )

        return cls(aspect_items)

    def get_aspect(self, aspect_id: str) -> AspectDefinition | None:
        return self._aspects.get(aspect_id)

    def get_all(self) -> list[AspectDefinition]:
        return list(self._aspects.values())

    def get_weight(self, aspect_id: str, default: float = 0.5) -> float:
        defn = self._aspects.get(aspect_id)
        return defn.weight if defn else default

    def to_dict_list(self) -> list[dict[str, Any]]:
        return [
            {
                "id": a.id,
                "name_vi": a.name_vi,
                "description": a.description,
                "department": a.department,
                "weight": a.weight,
            }
            for a in self._aspects.values()
        ]

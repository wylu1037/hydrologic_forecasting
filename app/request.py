from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HandleMapRequest:
    project_id: int
    min_water_depth: Optional[float] = field(default=0)


@dataclass
class HandleStationRequest:
    project_id: int


@dataclass
class RunProjectRequest:
    name: str
    description: str
    forecast_period: int
    upstream_water_level: Optional[list] = field(default=None)
    downstream_water_level: Optional[list] = field(default=None)


@dataclass
class UpdateProjectRequest:
    id: int
    name: Optional[str] = field(default=None)
    description: Optional[str] = field(default=None)
    forecast_period: Optional[int] = field(default=None)


@dataclass
class ExportMapRequest:
    start_time: str
    end_time: str
    project_id: Optional[int] = field(default=None)


@dataclass
class ExportStationRequest:
    start_time: str
    end_time: str
    project_id: Optional[int] = field(default=None)


class RepresentationStationRequest:
    count: int = field(default=10)

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HandleMapRequest:
    project_id: int
    min_water_depth: Optional[float] = field(default=0.1)


@dataclass
class HandleStationRequest:
    project_id: int


@dataclass
class RepresentationStationRequest:
    project_id: Optional[int] = field(default=None)


@dataclass
class RunProjectRequest:
    name: str
    description: str
    forecast_period: int
    start_time: str
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
    project_id: Optional[int] = field(default=None)


@dataclass
class ExportStationRequest:
    project_id: Optional[int] = field(default=None)


@dataclass
class ExportHistoryStationRequest:
    name: str
    project_id: Optional[int] = field(default=None)


@dataclass
class ExportHistoryMapRequest:
    project_id: Optional[int] = field(default=None)

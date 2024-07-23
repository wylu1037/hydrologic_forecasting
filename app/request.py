from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelForecastRequest:
    scheme_name: Optional[str] = field(default=None)
    date_time: Optional[str] = field(default=None)
    step_size: Optional[int] = field(default=None)
    schem_description: Optional[str] = field(default=None)
    args: list[str] = field(default_factory=list)


@dataclass
class HandleMapRequest:
    project_id: int
    min_water_depth: Optional[float] = field(default=0)


@dataclass
class HandleStationRequest:
    project_id: int


@dataclass
class CreateProjectRequest:
    name: str
    description: str
    time_index: int


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

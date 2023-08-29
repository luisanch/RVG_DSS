from dataclasses import dataclass, field
from pydantic import validate_arguments
import numpy as np


@validate_arguments
@dataclass
class CPA:
    d_at_cpa: float
    d_2_cpa: float
    t_2_cpa: float
    x_at_cpa: float
    y_at_cpa: float
    o_x_at_cpa: float
    o_y_at_cpa: float


@validate_arguments
@dataclass
class Safety_Params:
    t_2_r: float
    t_x_at_r: float
    t_y_at_r: float
    x_at_r: float
    y_at_r: float
    d_2_r: float


@dataclass
class AIS_NED:
    po_x: float
    po_y: float
    uo: float
    zo: np.array
    uo_x: float
    uo_y: float
    course: float
    mmsi: str
    cpa: bool = False
    d_at_cpa: float = 0
    d_2_cpa: float = 0
    t_2_cpa: float = 0
    x_at_cpa: float = 0
    y_at_cpa: float = 0
    o_x_at_cpa: float = 0
    o_y_at_cpa: float = 0
    safety_params: bool = False
    t_2_r: float = 0
    t_x_at_r: float = 0
    t_y_at_r: float = 0
    x_at_r: float = 0
    y_at_r: float = 0
    d_2_r: float = 0


@dataclass
class RVG_NED:
    p: np.array
    u: float
    ux: float
    uy: float
    z: np.array
    tq: np.array
    lon: float
    lat: float
    course: float


@dataclass
class ARPA_Data:
    self_course: float = None
    course: float = None
    t_2_cpa: float = None
    lat_o: float = None
    lon_o: float = None
    uo: float = None
    zo: float = None
    d_at_cpa: float = None
    d_2_cpa: float = None
    lat_at_cpa: float = None
    lon_at_cpa: float = None
    lat_o_at_cpa: float = None
    lon_o_at_cpa: float = None
    safety_params: bool = False
    t_2_r: float = None
    lat_o_at_r: float = None
    lon_o_at_r: float = None
    lat_at_r: float = None
    lon_at_r: float = None
    d_2_r: float = None
    safety_radius: float = None


@dataclass
class CBF_Data:
    p: np.array
    maneuver_start: float
    domains: list = field(default_factory=list)
    domain_lines: list = field(default_factory=list)

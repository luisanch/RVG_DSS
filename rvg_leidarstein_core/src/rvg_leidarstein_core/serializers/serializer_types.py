from dataclasses import dataclass, field
from pydantic import validate_arguments
import datetime


@dataclass
class AIS:
    lat: float
    lon: float
    mmsi: str
    message_id: str
    lat_p: float = None
    lon_p: float = None
    course: float = None
    course_history: list = field(default_factory=list)
    filtered_course: float = None
    speed: float = None
    heading: float = None
    pos_history: list = field(default_factory=list)
    lat_history: list = field(default_factory=list)
    lon_history: list = field(default_factory=list)


@validate_arguments
@dataclass
class GPRMC:
    timestamp: datetime.time
    status: str
    lat: float
    lat_dir: str
    lon: float
    lon_dir: str
    spd_over_grnd: float
    true_course: float
    datestamp: datetime.date
    mag_variation: str
    mag_var_dir: str
    mode_indicator: str
    nav_status: str
    message_id: str


@validate_arguments
@dataclass
class GPGGA:
    timestamp: datetime.time
    lat: float
    lat_dir: str
    lon: float
    lon_dir: str
    gps_qual: int
    num_sats: str
    horizontal_dil: str
    altitude: float
    altitude_units: str
    geo_sep: str
    geo_sep_units: str
    age_gps_data: str
    ref_station_id: str
    message_id: str


@validate_arguments
@dataclass
class PSIMSNS:
    msg_type: str
    timestamp: datetime.time
    unknown_1: str
    tcvr_num: str
    tdcr_num: str
    roll_deg: float
    pitch_deg: float
    heave_m: float
    head_deg: float
    empty_1: str
    unknown_2: str
    unknown_3: str
    empty_2: str
    checksum: str
    message_id: str

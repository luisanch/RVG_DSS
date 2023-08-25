#!/usr/bin/env python3
"""
Module: simulation_transform

Description:
This module contains the SimulationTransform class, which provides various methods 
to transform coordinates and units commonly used in simulations.

Classes:
- SimulationTransform: A class for coordinate and unit transformations used in simulations.
"""
import pandas as pd
import math
import pymap3d as pm


class simulation_transform:
    """
    A class for coordinate and unit transformations used in simulations.

    Methods:
    - deg_2_dec: Convert coordinates from degrees, minutes, and decimals to decimal degrees.
    - dec_2_deg: Convert coordinates from decimal degrees to degrees, minutes, and decimals.
    - coords_to_xyz: Convert coordinates (latitude, longitude, altitude) to XYZ (East-North-Up)
                     relative to a specified origin.
    - xyz_to_coords: Convert XYZ (East-North-Up) coordinates relative to a specified origin
                     back to geodetic coordinates (latitude, longitude).
    - kn_to_nms: Convert speed from knots to nautical miles per second.
    - nm_to_deg: Convert distance from nautical miles to degrees of latitude or longitude.
    - m_to_nm: Convert distance from meters to nautical miles.
    - mps_to_kn: Convert speed from meters per second to knots.
    - kn_to_mps: Convert speed from knots to meters per second.

    Attributes:
    - gps_data: DataFrame to store GPS data.
    - attitude_data: DataFrame to store attitude data.
    - nm_in_deg: Conversion factor from nautical miles to degrees of latitude or longitude.
    - m_in_nm: Conversion factor from meters to nautical miles.
    - mps_in_kn: Conversion factor from meters per second to knots.

    Dependencies:
    - pandas: For handling data in DataFrames.
    - math: For mathematical operations.
    - pymap3d: For geodetic and ENU coordinate transformations.
    """

    def __init__(self):
        self.gps_data = pd.DataFrame()
        self.attitude_data = pd.DataFrame()
        self.nm_in_deg = 60
        self.m_in_nm = 1852
        self.mps_in_kn = 0.51444

    def deg_2_dec(self, coord, dir):
        dir = 1
        if dir == "S" or dir == "W":
            dir = -1
        deg = math.trunc(coord / 100)
        dec = (coord / 100 - deg) * (10 / 6)
        return dir * (deg + dec)

    def dec_2_deg(self, coord, direction="lon"):
        dir = ""
        deg = 0

        if direction == "lon":
            if coord < 0:
                dir = "W"
            else:
                dir = "E"
        else:
            if coord < 0:
                dir = "S"
            else:
                dir = "N"

        deg = int(coord)
        deg = deg * 100 + (coord - deg) * 60
        return deg, dir

    def coords_to_xyz(self, northings, eastings, altitude, y_o, x_o, z_o):
        x, y, _ = pm.geodetic2enu(northings, eastings, altitude, y_o, x_o, z_o)
        z = altitude - z_o
        return x, y, z

    def xyz_to_coords(self, x, y, lat_o, lon_o, h_o=0, z=0):
        lat, lon, _ = pm.enu2geodetic(x, y, z, lat_o, lon_o, h_o)
        return lat, lon

    def kn_to_nms(self, kn):
        nms = kn / 3600
        return nms

    def nm_to_deg(self, nm):
        deg = nm / self.nm_in_deg
        return deg

    def m_to_nm(self, m):
        nm = m / self.m_in_nm
        return nm

    def mps_to_kn(self, mps):
        kn = float(mps) * 1.94384449
        return kn

    def kn_to_mps(self, knot):
        return float(knot) * self.mps_in_kn

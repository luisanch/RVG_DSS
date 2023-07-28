import pandas as pd
import math
import pymap3d as pm


class SimulationTransform:
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
        kn = mps * 1.94384449
        return kn

    def kn_to_mps(self, knot):
        return knot * self.mps_in_kn

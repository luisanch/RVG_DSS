#!/usr/bin/env python3
from math import atan2, pi, cos, sin, atan
import numpy as np
from .encounter_classifier_dsm import encounter_classifier_dsm
from .enums import Encounters, Range_Situation


class encounter_classifier:
    """
    The 'encounter_classifier' class is responsible for classifying encounters based on various parameters.
    """
    def __init__(
        self,
        _theta_1=np.deg2rad(20),
        theta_2=np.deg2rad(120),
        d_enter_up_cpa=150,
        t_enter_up_cpa=300,
        t_enter_low_cpa=0,
        d_exit_low_cpa=250,
        t_exit_low_cpa=0,
        t_exit_up_cpa=330,
    ):
        """
        Initialize the encounter_classifier object with the specified parameters.

        Parameters:
            _theta_1 (float): Inner angle threshold in radians. Default is 20 degrees.
            theta_2 (float): Outer angle threshold in radians. Default is 120 degrees.
            d_enter_up_cpa (float): Distance threshold for entering the upper CPA in meters. Default is 150.
            t_enter_up_cpa (float): Time threshold for entering the upper CPA in seconds. Default is 300.
            t_enter_low_cpa (float): Time threshold for entering the lower CPA in seconds. Default is 0.
            d_exit_low_cpa (float): Distance threshold for exiting the lower CPA in meters. Default is 250.
            t_exit_low_cpa (float): Time threshold for exiting the lower CPA in seconds. Default is 0.
            t_exit_up_cpa (float): Time threshold for exiting the upper CPA in seconds. Default is 330.
        """
        self._theta_1 = _theta_1
        self._theta_2 = theta_2
        self._dsm = encounter_classifier_dsm(
            d_enter_up_cpa=d_enter_up_cpa,
            t_enter_up_cpa=t_enter_up_cpa,
            t_enter_low_cpa=t_enter_low_cpa,
            d_exit_low_cpa=d_exit_low_cpa,
            t_exit_low_cpa=t_exit_low_cpa,
            t_exit_up_cpa=t_exit_up_cpa,
        )
        self.encounter = self._dsm.current_state
        self._sector_arcs = [
            2 * _theta_1,
            theta_2 - _theta_1,
            2 * (pi - theta_2),
            theta_2 - _theta_1,
        ]
        self._encounters = {
            1: {
                1: Encounters.HEADON,
                2: Encounters.GIVEWAY,
                3: (
                    Encounters.SAFE,
                    Encounters.OVERTAKING_PORT,
                    Encounters.OVERTAKING_STAR,
                ),
                4: Encounters.STANDON,
            },
            2: {
                1: Encounters.GIVEWAY,
                2: Encounters.GIVEWAY,
                3: (Encounters.SAFE, Encounters.OVERTAKING_STAR),
                4: Encounters.SAFE,
            },
            3: {
                1: (Encounters.SAFE, Encounters.STANDON),
                2: (Encounters.SAFE, Encounters.STANDON),
                3: Encounters.SAFE,
                4: (Encounters.SAFE, Encounters.STANDON),
            },
            4: {
                1: Encounters.STANDON,
                2: Encounters.SAFE,
                3: (Encounters.SAFE, Encounters.OVERTAKING_PORT),
                4: Encounters.STANDON,
            },
        }

    def is_angle_in_range(self, angle_radians, start_range_radians, end_range_radians):
        """
        Check if an angle is within a specified range.

        Parameters:
            angle_radians (float): Angle in radians to be checked.
            start_range_radians (float): Starting angle of the range in radians.
            end_range_radians (float): Ending angle of the range in radians.

        Returns:
            bool: True if the angle is within the range, False otherwise.
        """
        # Normalize the input angle to [0, 2π) radians range
        normalized_angle = angle_radians % (2 * pi)

        # Normalize the range bounds to [0, 2π) radians range
        normalized_start_range = start_range_radians % (2 * pi)
        normalized_end_range = end_range_radians % (2 * np.pi)

        if normalized_start_range <= normalized_end_range:
            # Range does not cross 0 radians
            return normalized_start_range <= normalized_angle <= normalized_end_range
        else:
            # Range crosses 0 radians
            return (normalized_start_range <= normalized_angle) or (
                normalized_angle <= normalized_end_range
            )

    def identify_range_situation(
        self, rvg_course, ts_course, e, e_ts, n, n_ts, u_rvg, u_ts
    ):  
        """
        Identify the range situation based on courses and velocities.

        Parameters:
            rvg_course (float): RVG's course in radians.
            ts_course (float): Target ship's course in radians.
            e (float): RVG's easting coordinate.
            e_ts (float): Target ship's easting coordinate.
            n (float): RVG's northing coordinate.
            n_ts (float): Target ship's northing coordinate.
            u_rvg (float): RVG's velocity.
            u_ts (float): Target ship's velocity.

        Returns:
            Range_Situation: Range situation enum value.
        """
        v_os = np.array([[u_rvg * sin(rvg_course)], [u_rvg * cos(rvg_course)]])
        v_ts = np.array([[u_ts * sin(ts_course)], [u_ts * cos(ts_course)]])
        v_rel = v_ts - v_os
        p_rel = np.array([e_ts - e, n_ts - n])
        prod = p_rel @ v_rel

        if prod >= 0:
            range_situation = Range_Situation.INCREASING
        elif prod < 0:
            range_situation = Range_Situation.CLOSING_IN

        return range_situation


    def get_rbs(self, rvg_course, e, e_ts, n, n_ts):
        """
        Get the Relative Bearing Sector (RBS) based on RVG's course and coordinates.

        Parameters:
            rvg_course (float): RVG's course in radians.
            e (float): RVG's easting coordinate.
            e_ts (float): Target ship's easting coordinate.
            n (float): RVG's northing coordinate.
            n_ts (float): Target ship's northing coordinate.

        Returns:
            int: RBS value representing the sector.
        """
        phi = atan2((e_ts - e), (n_ts - n)) - rvg_course
        rbs = 0

        if self.is_angle_in_range(
            phi, self._theta_1, self._theta_1 + self._sector_arcs[1]
        ):
            rbs = 2
        elif self.is_angle_in_range(
            phi,
            self._theta_1 + self._sector_arcs[1],
            self._theta_1 + self._sector_arcs[1] + +self._sector_arcs[2],
        ):
            rbs = 3
        elif self.is_angle_in_range(
            phi,
            self._theta_1 + self._sector_arcs[1] + self._sector_arcs[2],
            self._theta_1
            + self._sector_arcs[1]
            + self._sector_arcs[2]
            + self._sector_arcs[3],
        ):
            rbs = 4
        elif self.is_angle_in_range(
            phi,
            self._theta_1
            + self._sector_arcs[1]
            + self._sector_arcs[2]
            + self._sector_arcs[3],
            self._theta_1,
        ):
            rbs = 1

        return rbs

    # Situation Sector
    def get_ss(self, ts_course, e, e_ts, n, n_ts):
        """
        Get the Situation Sector (SS) based on target ship's course and coordinates.

        Parameters:
            ts_course (float): Target ship's course in radians.
            e (float): RVG's easting coordinate.
            e_ts (float): Target ship's easting coordinate.
            n (float): RVG's northing coordinate.
            n_ts (float): Target ship's northing coordinate.

        Returns:
            tuple: SS value representing the sector and the sector's bounds.
        """
        phi_ts = atan2((e - e_ts), (n - n_ts))

        theta_11 = self._theta_1 + phi_ts
        theta_22 = self._theta_2 + phi_ts

        if self.is_angle_in_range(ts_course, theta_11, theta_11 + self._sector_arcs[1]):
            ss = 2
        elif self.is_angle_in_range(
            ts_course,
            theta_11 + self._sector_arcs[1],
            theta_11 + self._sector_arcs[1] + +self._sector_arcs[2],
        ):
            ss = 3
        elif self.is_angle_in_range(
            ts_course,
            theta_11 + self._sector_arcs[1] + self._sector_arcs[2],
            theta_11
            + self._sector_arcs[1]
            + self._sector_arcs[2]
            + self._sector_arcs[3],
        ):
            ss = 4
        elif self.is_angle_in_range(
            ts_course,
            theta_11
            + self._sector_arcs[1]
            + self._sector_arcs[2]
            + self._sector_arcs[3],
            theta_11,
        ):
            ss = 1

        return ss, theta_11, theta_22

    def classify_encounter(self, rvg_course, ts_course, e, e_ts, n, n_ts, v_rvg, v_ts):
        """
        Classify the encounter based on various parameters.

        Parameters:
            rvg_course (float): RVG's course in radians.
            ts_course (float): Target ship's course in radians.
            e (float): RVG's easting coordinate.
            e_ts (float): Target ship's easting coordinate.
            n (float): RVG's northing coordinate.
            n_ts (float): Target ship's northing coordinate.
            v_rvg (float): RVG's velocity.
            v_ts (float): Target ship's velocity.

        Returns:
            Encounters: Encounters enum value representing the classification.
        """
        rbs = self.get_rbs(rvg_course=rvg_course, e=e, e_ts=e_ts, n=n, n_ts=n_ts)
        ss, theta_11, theta_22 = self.get_ss(
            ts_course=ts_course, e=e, e_ts=e_ts, n=n, n_ts=n_ts
        )
        range_situation = self.identify_range_situation(
            rvg_course, ts_course, e, e_ts, n, n_ts, v_rvg, v_ts
        )

        encounter = self._encounters[rbs][ss] 

        if type(encounter) is Encounters:
            return encounter
        elif len(encounter) == 2:  # Select between inner and outer circle
            encounter = encounter[range_situation.value]
        else:  # special case for rbs1
            if range_situation == Range_Situation.INCREASING:
                encounter = encounter[0]
            else:
                if self.is_angle_in_range(
                    ts_course, theta_22, theta_22 + (self._sector_arcs[2]) / 2
                ):
                    encounter = encounter[1]
                elif self.is_angle_in_range(
                    ts_course,
                    theta_22 + (self._sector_arcs[2]) / 2,
                    theta_22 + (self._sector_arcs[2]),
                ):
                    encounter = encounter[2]
        return encounter

    def get_encounter_type(
        self, rvg_course, ts_course, e, e_ts, n, n_ts, v_rvg, v_ts, d_at_cpa, t_2_cpa
    ):
        """
        Get the encounter type based on various parameters.

        Parameters:
            rvg_course (float): RVG's course in radians.
            ts_course (float): Target ship's course in radians.
            e (float): RVG's easting coordinate.
            e_ts (float): Target ship's easting coordinate.
            n (float): RVG's northing coordinate.
            n_ts (float): Target ship's northing coordinate.
            v_rvg (float): RVG's velocity.
            v_ts (float): Target ship's velocity.
            d_at
        """
        encounter = self.classify_encounter(
            rvg_course, ts_course, e, e_ts, n, n_ts, v_rvg, v_ts
        )
        self._dsm.update(encounter, d_at_cpa, t_2_cpa)
        self.encounter = self._dsm.current_state  # maybe not necessary
        return self.encounter.id, self.encounter.value

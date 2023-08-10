from math import atan2, pi, cos, sin
import numpy as np
from rvg_leidarstein_core.colav.encounter_classifier_dsm import encounter_classifier_dsm
from rvg_leidarstein_core.colav.enums import Encounters, Range_Situation


class encounter_classifier:
    def __init__(self, theta_1=(20 * pi / 180), theta_2=(120 * pi / 180)):
        self._theta_1 = theta_1
        self._theta_2 = theta_2
        self._dsm = encounter_classifier_dsm()
        self.encounter = encounter_classifier_dsm.current_state
        self._sector_arcs = [
            2 * theta_1,
            theta_2 - theta_1,
            2 * (pi - theta_2),
            theta_2 - theta_1,
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
        v_os = np.array([[u_rvg * cos(rvg_course)], [u_rvg * sin(rvg_course)]])
        v_ts = np.array([[u_ts * cos(ts_course)], [u_ts * sin(ts_course)]])
        v_rel = v_ts - v_os
        p_rel = np.array([n_ts - n, e_ts - e])
        prod = p_rel @ v_rel

        if prod >= 0:
            range_situation = Range_Situation.CLOSING_IN
        elif prod < 0:
            range_situation = Range_Situation.INCREASING

        return range_situation

    # Relative Bearing Sector
    def get_rbs(self, rvg_course, e, e_ts, n, n_ts):
        phi = atan2((e_ts - e), (n_ts - n)) - rvg_course
        rbs = 0

        if self.is_angle_in_range(phi, -self._theta_1, self._theta_1):
            rbs = 1
        elif self.is_angle_in_range(phi, self._theta_1, self._theta_2):
            rbs = 2
        elif self.is_angle_in_range(phi, self._theta_2, -self._theta_2):
            rbs = 3
        elif self.is_angle_in_range(phi, -self._theta_2, -self._theta_1):
            rbs = 4

        return rbs

    # Situation Sector
    def get_ss(self, ts_course, e, e_ts, n, n_ts):
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
        rbs = self.get_rbs(rvg_course, e, e_ts, n, n_ts)
        ss, theta_11, theta_22 = self.get_ss(ts_course, e, e_ts, n, n_ts)
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

    def get_encounter_type(self, rvg_course, ts_course, e, e_ts, n, n_ts, v_rvg, v_ts):
        encounter = self.classify_encounter(
            rvg_course, ts_course, e, e_ts, n, n_ts, v_rvg, v_ts
        )
        v_os = (v_rvg * cos(rvg_course), v_rvg * sin(rvg_course))
        v_ts = (v_ts * cos(ts_course), v_ts * sin(ts_course))
        p = np.array([[e], [n]])
        self._dsm.update(encounter, e_ts, n_ts, v_ts[0], v_ts[1], p, v_os[0], v_os[1])
        self.encounter = encounter_classifier_dsm.current_state  # maybe not necessary
        return self.encounter.id, self.encounter.value

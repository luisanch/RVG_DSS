from statemachine import StateMachine
from statemachine.statemachine import States
from rvg_leidarstein_core.colav.enums import Encounters
from rvg_leidarstein_core.colav.arpa import arpa


class encounter_classifier_dsm(StateMachine):
    def __init__(
        self,
        d_enter_up_cpa=200,
        t_enter_up_cpa=20,
        t_enter_low_cpa=20,
        d_exit_low_cpa=200,
        t_exit_low_cpa=20,
        t_exit_up_cpa=20,
        d_crit=50,
    ):
        super(encounter_classifier_dsm, self).__init__()
        self.arpa = arpa(safety_radius_m=d_crit)
        self._d_enter_up_cpa = d_enter_up_cpa
        self._t_enter_up_cpa = t_enter_up_cpa
        self._t_enter_low_cpa = t_enter_low_cpa
        self._d_exit_low_cpa = d_exit_low_cpa
        self._t_exit_low_cpa = t_exit_low_cpa
        self._t_exit_up_cpa = t_exit_up_cpa
        self._entry = False
        self._exit = False
        self._encounter = Encounters.SAFE

    _ = States.from_enum(Encounters, initial=Encounters.SAFE)

    # Transitions
    safe_to_ot_s = _.SAFE.to(_.OVERTAKING_STAR, cond="guard_safe_to_ot_s")
    safe_to_ot_p = _.SAFE.to(_.OVERTAKING_PORT, cond="guard_safe_to_ot_p")
    safe_to_head_on = _.SAFE.to(_.HEADON, cond="guard_safe_to_head_on")
    safe_to_give_way = _.SAFE.to(_.GIVEWAY, cond="guard_safe_to_give_way")
    safe_to_stand_on = _.SAFE.to(_.STANDON, cond="guard_safe_to_stand_on") 

    ot_s_to_safe = _.OVERTAKING_STAR.to(_.SAFE, cond="guard_any_to_safe")
    ot_p_to_safe = _.OVERTAKING_PORT.to(_.SAFE, cond="guard_any_to_safe")
    head_on_to_safe = _.HEADON.to(_.SAFE, cond="guard_any_to_safe")
    give_way_to_safe = _.GIVEWAY.to(_.SAFE, cond="guard_any_to_safe")
    stand_on_to_safe = _.STANDON.to(_.SAFE, cond="guard_any_to_safe")
    
    # emergency state put on hold for the time being
    # safe_to_emergency = _.SAFE.to(_.EMERGENCY, cond = "")
    # emergency_to_safe = _.EMERGENCY.to(_.SAFE)

    # test
    cycle = safe_to_ot_p | ot_p_to_safe

    def get_critical_parameters(self, po_x, po_y, uo_x, uo_y, p, ux, uy):
        ais_data = {
            "po_x": po_x,
            "po_y": po_y,
            "uo_x": uo_x,
            "uo_y": uo_y,
        }

        gunn_data = {"p": p, "ux": ux, "uy": uy}
        cpa = arpa._get_cpa(gunn_data, ais_data)
        safety_params = arpa._get_safety_params(gunn_data, ais_data)
        return cpa, safety_params

    def update(self, encounter, po_x, po_y, uo_x, uo_y, p, ux, uy):
        cpa, _ = self.get_critical_parameters(self, po_x, po_y, uo_x, uo_y, p, ux, uy)
        # maybe just use safety params
        entry = (cpa["d_at_cpa"] < self._d_enter_up_cpa) and (
            cpa["t_2_cpa"] > self._t_enter_low_cpa
            and cpa["t_2_cpa"] < self._t_enter_up_cpa
        )

        exit = (cpa["d_at_cpa"] >= self._d_exit_low_cpa) or (
            cpa["t_2_cpa"] < self._t_enter_low_cpa
            or cpa["t_2_cpa"] > self._t_enter_up_cpa
        )
        pass

    # guards
    def guard_safe_to_ot_s(self):
        return self._encounter is Encounters.OVERTAKING_STAR and self._entry

    def guard_safe_to_ot_p(self):
        return self._encounter is Encounters.OVERTAKING_PORT and self._entry

    def guard_safe_to_head_on(self):
        return self._encounter is Encounters.HEADON and self._entry

    def guard_safe_to_give_way(self):
        return self._encounter is Encounters.GIVEWAY and self._entry

    def guard_safe_to_stand_on(self):
        return self._encounter is Encounters.STANDON and self._entry

    def guard_any_to_safe(self):
        return self._encounter is Encounters.SAFE or self._exit

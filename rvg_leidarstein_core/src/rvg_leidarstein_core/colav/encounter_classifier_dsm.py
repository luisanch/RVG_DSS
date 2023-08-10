from statemachine import StateMachine
from statemachine.statemachine import States
from .enums import Encounters
from .ARPA import arpa


class encounter_classifier_dsm(StateMachine):
    def __init__(
            self,
            d_enter_up_cpa=200,
            t_enter_up_cpa=300,
            t_enter_low_cpa=0,
            d_exit_low_cpa=250,
            t_exit_low_cpa=0,
            t_exit_up_cpa=330,
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
    safe_to_ot_s = _.SAFE.to(_.OVERTAKING_STAR)
    safe_to_ot_p = _.SAFE.to(_.OVERTAKING_PORT)
    safe_to_head_on = _.SAFE.to(_.HEADON)
    safe_to_give_way = _.SAFE.to(_.GIVEWAY)
    safe_to_stand_on = _.SAFE.to(_.STANDON)

    ot_s_to_safe = _.OVERTAKING_STAR.to(_.SAFE, cond="guard_any_to_safe")
    ot_p_to_safe = _.OVERTAKING_PORT.to(_.SAFE, cond="guard_any_to_safe")
    head_on_to_safe = _.HEADON.to(_.SAFE, cond="guard_any_to_safe")
    give_way_to_safe = _.GIVEWAY.to(_.SAFE, cond="guard_any_to_safe")
    stand_on_to_safe = _.STANDON.to(_.SAFE, cond="guard_any_to_safe")

    # emergency state put on hold for the time being
    # safe_to_emergency = _.SAFE.to(_.EMERGENCY, cond = "")
    # emergency_to_safe = _.EMERGENCY.to(_.SAFE)

    def update(self, encounter, d_at_cpa, t_2_cpa):
        self._encounter = encounter

        self._entry = (d_at_cpa < self._d_enter_up_cpa) and (
            t_2_cpa > self._t_enter_low_cpa and t_2_cpa < self._t_enter_up_cpa
        )

        if self._entry:
            if (
                self.current_state.value is Encounters.SAFE.value
                and self.guard_safe_to_ot_s()
            ):
                self.safe_to_ot_s()
            if (
                self.current_state.value is Encounters.SAFE.value
                and self.guard_safe_to_ot_p()
            ):
                self.safe_to_ot_p()
            if (
                self.current_state.value is Encounters.SAFE.value
                and self.guard_safe_to_head_on()
            ):
                self.safe_to_head_on()
            if (
                self.current_state.value is Encounters.SAFE.value
                and self.guard_safe_to_give_way()
            ):
                self.safe_to_give_way()
            if (
                self.current_state.value is Encounters.SAFE.value
                and self.guard_safe_to_stand_on()
            ):
                self.safe_to_stand_on()

        self._exit = (d_at_cpa >= self._d_exit_low_cpa) or (
            t_2_cpa < self._t_exit_low_cpa or t_2_cpa > self._t_exit_up_cpa
        )

        if self._exit:
            if self.current_state.value is Encounters.OVERTAKING_STAR.value:
                self.ot_s_to_safe()
            if self.current_state.value is Encounters.OVERTAKING_PORT.value:
                self.ot_p_to_safe()
            if self.current_state.value is Encounters.HEADON.value:
                self.head_on_to_safe()
            if self.current_state.value is Encounters.GIVEWAY.value:
                self.give_way_to_safe()
            if self.current_state.value is Encounters.STANDON.value:
                self.stand_on_to_safe()

    # guards
    def guard_safe_to_ot_s(self):
        return (
            self._encounter is Encounters.OVERTAKING_STAR
            and self._entry
            and (self.current_state.value is Encounters.SAFE.value)
        )

    def guard_safe_to_ot_p(self):
        return (
            self._encounter is Encounters.OVERTAKING_PORT
            and self._entry
            and (self.current_state.value is Encounters.SAFE.value)
        )

    def guard_safe_to_head_on(self):
        return (
            self._encounter is Encounters.HEADON
            and self._entry
            and (self.current_state.value is Encounters.SAFE.value)
        )

    def guard_safe_to_give_way(self):
        return (
            self._encounter is Encounters.GIVEWAY
            and self._entry
            and (self.current_state.value is Encounters.SAFE.value)
        )

    def guard_safe_to_stand_on(self):
        return (
            self._encounter is Encounters.STANDON
            and self._entry
            and (self.current_state.value is Encounters.SAFE.value)
        )

    def guard_any_to_safe(self):
        return (self._encounter is Encounters.SAFE or self._exit) and (
            self.current_state.value is not Encounters.SAFE.value
        )

from mesa import Agent
from datetime import datetime


class HospitalBuildingAgent(Agent):
    """
    Агент «Больница» для почасового расчёта энергопотребления с фиксированными параметрами.

    Отопительный сезон: с 15 октября по 15 апреля.
    Итоговое потребление сохраняется в self.consumption (кВт·ч).
    """

    # Доли электропотребления (сумма = 1.0)
    WEIGHTS = {
        "ventilation": 0.22,
        "lighting": 0.10,
        "gdhw": 0.15,
        "medical_eq": 0.09,
        "it_transport": 0.02,
        # Остальная часть (0.42) учитывается в тепловом потреблении
    }

    # Фиксированные параметры здания
    AREA_M2 = 8000             # м², площадь больницы (референс)
    BEDS_TOTAL = 320            # всего коек
    EUI_EL_BASE = 52.0          # кВт·ч/м²·год, электроэнергия
    EUI_HEAT_BASE = 54.0       # кВт·ч/м²·год, тепло (≈0.024·4500)

    def __init__(self, model):
        super().__init__(model)
        self._last_occ: float = None
        self.consumption: float = 0.0  # кВт·ч за последний час

    def step(self) -> None:
        """
        Почасовой шаг: рассчитывает и сохраняет суммарное потребление в self.consumption.
        """
        dt: datetime = self.model.current_datetime
        T_out: float = self.model.current_T_out

        # Загрузка коек
        hosp = max(0.0, min(self.model.hospitalized, self.BEDS_TOTAL))
        occ = hosp / self.BEDS_TOTAL if self.BEDS_TOTAL else 0.0
        d_occ = 0.0 if self._last_occ is None else abs(occ - self._last_occ)

        # Расчёт энергопотребления
        heat_kwh = self._heat_hour(dt, T_out)
        el_kwh = self._electricity_hour(occ, getattr(self.model, 'patients_total', 0))
        total_kwh = heat_kwh + el_kwh

        # Сохраняем результаты
        self.consumption = total_kwh * 1000 

        self._last_occ = occ

        if getattr(self.model, 'verbose', False):
            print(
                f"[Hospital {self.unique_id} {dt:%Y-%m-%d %H}] "
                f"occ={occ:.2f} Δocc={d_occ:.2f} cons={total_kwh:.2f} kWh"
            )

    def _is_heating_season(self, dt: datetime) -> bool:
        """
        Проверяет, находится ли дата в отопительном сезоне (15.10–15.04).
        """
        month = dt.month
        day = dt.day
        # Октябрь
        if month == 10 and day >= 15:
            return True
        # Ноябрь–март
        if 11 <= month <= 3:
            return True
        # Апрель
        if month == 4 and day <= 15:
            return True
        return False

    def _heat_hour(self, dt: datetime, T_out: float) -> float:
        """
        Возвращает часовое тепловое потребление, кВт·ч.
        """
        if not self._is_heating_season(dt):
            return 0.0
        T_base = 18.0
        delta = max(0.0, T_base - T_out)
        # Приводим годовую тепловую энергию к часовому уровню и умножаем на ΔT
        return (self.EUI_HEAT_BASE * self.AREA_M2 / 8760.0) * delta

    def _electricity_hour(self, occupancy: float, patients_total: int) -> float:
        """
        Возвращает часовое электрическое потребление, кВт·ч.
        """
        base = self.EUI_EL_BASE * self.AREA_M2 / 8760.0
        occ_mult = 0.6 + 0.4 * occupancy
        surg_mult = 1.0 + 0.05 * (patients_total / max(1, self.BEDS_TOTAL))

        q_el = 0.0
        for component, weight in self.WEIGHTS.items():
            mult = occ_mult if component in {"ventilation", "lighting"} else 1.0
            if component == "medical_eq":
                mult *= surg_mult
            q_el += weight * mult
        return q_el * base

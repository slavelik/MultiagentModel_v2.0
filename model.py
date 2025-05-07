import os
import pandas as pd
import numpy as np
from datetime import timedelta
from mesa import Model, DataCollector

from EnterpriseBuilding.agent import EnterpriseBuildingAgent
from OfficeBuilding.agent import OfficeBuildingAgent
from HospitalBuilding.agent import HospitalBuildingAgent
from MallBuilding.agent import MallAgent
from ModernResidentialBuilding.agent import ModernResidentialBuildingAgent
from ResidentialBuilding.agent import ResidentialBuildingAgent

class EnergyConsumptionModel(Model):
    """
    Модель для симуляции энергопотребления различных типов зданий-агентов.
    """
    def __init__(
        self,
        n_enterprises=1,
        n_offices=1,
        n_hospitals=1,
        n_malls=1,
        n_modern_residential=1,
        n_residential=1,
        start_datetime=pd.to_datetime('2023-01-01 00:00'),
        weather_path=os.path.join('data', 'environment_data.csv')
    ):
        super().__init__()
        # Текущее время моделирования
        self.current_datetime = start_datetime
        # Загружаем погодные данные (T_out, day_off, WeekStatus, office_population, hospitalized, patients_total)
        self.weather_df = (
            pd.read_csv(weather_path, parse_dates=['datetime'])
              .set_index('datetime')
        )
        # Параметры окружения, обновляются на каждом шаге
        self.current_weather = {}
        self.current_WeekStatus = 'Weekday'
        self.current_day_off = False
        self.current_office_population = 0
        self.hospitalized = 1
        self.patients = 2

        # Количество офисных агентов нужно доступно внутри OfficeBuildingAgent
        self.num_office_agents = n_offices

        # Инициализация агентов
        for _ in range(n_enterprises):
            agent = EnterpriseBuildingAgent(self)
            self.agents.add(agent)
        for _ in range(n_offices):
            agent = OfficeBuildingAgent(self)
            self.agents.add(agent)

        for _ in range(n_hospitals):
            agent = HospitalBuildingAgent(self)
            self.agents.add(agent)

        for _ in range(n_malls):
            agent = MallAgent(self)
            self.agents.add(agent)

        for _ in range(n_modern_residential):
            agent = ModernResidentialBuildingAgent(self)
            self.agents.add(agent)

        for _ in range(n_residential):
            agent = ResidentialBuildingAgent(self)
            self.agents.add(agent)

        # DataCollector: собираем данные моделей и агентов
        self.datacollector = DataCollector(
            model_reporters={
                'datetime': lambda m: m.current_datetime,
                'office_population': lambda m: m.current_office_population,
                'hospitalized':      lambda m: m.hospitalized,
                'patients_total':    lambda m: m.patients
            },
            agent_reporters={
                'AgentType':   lambda a: type(a).__name__,  
                'consumption': lambda a: a.consumption
            }
        )


    def step(self):
        # Обновление переменных окружения из погодного датафрейма
        try:
            row = self.weather_df.loc[self.current_datetime]
            # Температура и другие погодные параметры
            self.current_weather = row.to_dict()
            self.current_T_out = row.get('T_out', 0.0)
            self.current_WeekStatus = row.get('WeekStatus', 'Weekday')
            self.current_day_off = bool(row.get('day_off', False))
            # Специфичные параметры для офисов и больницы
            self.current_office_population = row.get('office_population', 0)
            self.hospitalized = row.get('hospitalized', 0)
            self.patients_total = row.get('patients_total', 0)
        except KeyError:
            # При отсутствии строки — устанавливаем дефолтные значения
            self.current_weather = {'T_out': 0.0}
            self.current_T_out = 0.0
            self.current_WeekStatus = 'Weekday'
            self.current_day_off = False
            self.current_office_population = 0
            self.hospitalized = 0
            self.patients_total = 0
        
        self.datacollector.collect(self)

        for agent in self.agents:
            agent.step()
        # Переходим к следующему часу
        self.current_datetime += timedelta(hours=1)
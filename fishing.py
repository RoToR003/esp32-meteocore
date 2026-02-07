"""
ПРОФЕСІЙНА СИСТЕМА ПРОГНОЗУВАННЯ КЛЮВАННЯ РИБИ
================================================

Використовує всі фізико-математичні моделі з наукового дослідження:
- Фізіологія холоднокровних тварин (Правило Вант-Гоффа)
- Гідрохімія води (розчинений кисень, pH, температура)
- Метеорологічні фактори (тиск, вітер, опади)
- Астрономічні ритми (Місяць, добові цикли, сезони)
- Комплексний Індекс Активності Риби (КІАР)

Автор: Науково-дослідна система іхтіології
Дата: 2026
"""

import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] FISH: %(message)s',
    handlers=[
        logging.FileHandler("fishing_forecast.log"),
        logging.StreamHandler()
    ]
)


# ============================================================================
# КОНСТАНТИ ТА ПАРАМЕТРИ
# ============================================================================

class PhysicalConstants:
    """Фізичні константи води та гідробіології"""
    
    # Властивості води
    WATER_DENSITY = 1000  # кг/м³
    WATER_HEAT_CAPACITY = 4186  # Дж/(кг·°C)
    
    # Газообмін
    HENRY_CONSTANT_O2 = 1.3e-3  # моль/(л·атм) при 25°C
    O2_DIFFUSION_COEF = 2.0e-9  # м²/с
    
    # Гідростатика
    g = 9.81  # м/с²
    WATER_PRESSURE_PER_METER = 76  # мм рт.ст. на 1 метр глибини
    
    # Оптика
    WATER_ALBEDO = 0.06
    LIGHT_EXTINCTION_CLEAR = 0.1  # м⁻¹
    LIGHT_EXTINCTION_TURBID = 5.0  # м⁻¹
    
    # Біологічні константи
    Q10_FISH = 2.2  # Температурний коефіцієнт Вант-Гоффа для риб
    
    # Емпіричні коефіцієнти
    THERMAL_INERTIA_SHALLOW = 0.15  # для мілководдя
    THERMAL_INERTIA_MEDIUM = 0.08   # для середньої глибини
    THERMAL_INERTIA_DEEP = 0.05     # для глибоких водойм
    
    CONDENSATION_HEIGHT_COEF = 122  # м/°C для рівня конденсації
    BAROMETRIC_CRITICAL_CHANGE = 2.5  # мм рт.ст./год критична зміна
    
    AERATION_COEFFICIENT = 0.001  # для аерації вітром
    WIND_TURBULENCE_COEF = 0.001


class FishSpecies(Enum):
    """Види риби"""
    PIKE = "Щука"
    ZANDER = "Судак"
    PERCH = "Окунь"
    CATFISH = "Сом"
    CARP = "Короп"
    CRUCIAN = "Карась"
    BREAM = "Лящ"
    ROACH = "Плітка"
    SILVER_CARP = "Товстолобик"
    GRASS_CARP = "Амур білий"


class LightType(Enum):
    """Тип світлової активності риби"""
    DIURNAL = "денний"      # окунь, плітка
    CREPUSCULAR = "сутінковий"  # щука, лящ, короп
    NOCTURNAL = "нічний"    # судак, сом


# ============================================================================
# ПРОФІЛІ ВИДІВ РИБИ
# ============================================================================

class FishProfile:
    """Профіль виду риби з усіма характеристиками"""
    
    def __init__(self, species: FishSpecies):
        self.species = species
        self._load_profile()
    
    def _load_profile(self):
        """Завантаження характеристик виду з дослідження"""
        
        profiles = {
            FishSpecies.PIKE: {
                'name_ua': 'Щука',
                'name_lat': 'Esox lucius',
                'type': 'хижак',
                'T_opt': 17.0,
                'T_min': 2.0,
                'T_max': 26.0,
                'sigma_T': 4.0,
                'p_opt': 755.0,
                'sigma_p': 12.0,
                'pressure_sensitivity': 0.5,
                'DO_min': 5.0,
                'DO_opt': 8.0,
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 500.0,
                'light_sigma': 2.0,
                'wind_opt': 4.0,
                'moon_amplitude': 0.3,
                'time_peak1': 6.0,
                'time_peak2': 19.0,
                'season_peak': 90,  # день року (кінець березня)
                'season_peak2': 270,  # осінній жор
                'season_amplitude': 0.6,
                'spawn_temp': 6.0,
                'spawn_month': 3  # березень-квітень
            },
            
            FishSpecies.ZANDER: {
                'name_ua': 'Судак',
                'name_lat': 'Sander lucioperca',
                'type': 'хижак',
                'T_opt': 20.0,
                'T_min': 4.0,
                'T_max': 28.0,
                'sigma_T': 4.0,
                'p_opt': 755.0,
                'sigma_p': 10.0,
                'pressure_sensitivity': 0.5,
                'DO_min': 6.0,
                'DO_opt': 9.0,
                'light_type': LightType.NOCTURNAL,
                'light_opt': 50.0,
                'light_critical': 100.0,
                'wind_opt': 3.0,
                'moon_amplitude': 0.55,
                'time_peak1': 23.0,
                'time_peak2': 5.0,
                'season_peak': 180,
                'season_amplitude': 0.5,
                'spawn_temp': 13.5,
                'spawn_month': 5
            },
            
            FishSpecies.PERCH: {
                'name_ua': 'Окунь',
                'name_lat': 'Perca fluviatilis',
                'type': 'хижак',
                'T_opt': 15.0,
                'T_min': 0.0,
                'T_max': 24.0,
                'sigma_T': 5.0,
                'p_opt': 750.0,
                'sigma_p': 17.0,
                'pressure_sensitivity': 0.3,
                'DO_min': 4.0,
                'DO_opt': 7.0,
                'light_type': LightType.DIURNAL,
                'light_opt': 5000.0,
                'wind_opt': 4.0,
                'moon_amplitude': 0.35,
                'time_peak1': 10.0,
                'time_peak2': None,
                'season_peak': 100,
                'season_peak2': 270,
                'season_amplitude': 0.5,
                'spawn_temp': 10.0,
                'spawn_month': 4
            },
            
            FishSpecies.CATFISH: {
                'name_ua': 'Сом',
                'name_lat': 'Silurus glanis',
                'type': 'хижак',
                'T_opt': 23.0,
                'T_min': 10.0,
                'T_max': 30.0,
                'sigma_T': 5.0,
                'p_opt': 750.0,
                'sigma_p': 10.0,
                'pressure_sensitivity': 0.5,
                'DO_min': 3.0,
                'DO_opt': 6.0,
                'light_type': LightType.NOCTURNAL,
                'light_opt': 10.0,
                'light_critical': 100.0,
                'wind_opt': 3.0,
                'moon_amplitude': 0.75,
                'time_peak1': 22.0,
                'time_peak2': 4.0,
                'season_peak': 180,
                'season_amplitude': 0.7,
                'spawn_temp': 20.0,
                'spawn_month': 6
            },
            
            FishSpecies.CARP: {
                'name_ua': 'Короп',
                'name_lat': 'Cyprinus carpio',
                'type': 'мирний',
                'T_opt': 23.0,
                'T_min': 8.0,
                'T_max': 30.0,
                'sigma_T': 4.0,
                'p_opt': 755.0,
                'sigma_p': 10.0,
                'pressure_sensitivity': 0.8,
                'DO_min': 5.0,
                'DO_opt': 7.5,
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 1000.0,
                'light_sigma': 2.0,
                'wind_opt': 4.0,
                'moon_amplitude': 0.45,
                'time_peak1': 7.0,
                'time_peak2': 19.0,
                'season_peak': 150,
                'season_amplitude': 0.5,
                'spawn_temp': 19.0,
                'spawn_month': 5
            },
            
            FishSpecies.CRUCIAN: {
                'name_ua': 'Карась',
                'name_lat': 'Carassius',
                'type': 'мирний',
                'T_opt': 21.0,
                'T_min': 4.0,
                'T_max': 32.0,
                'sigma_T': 6.0,
                'p_opt': 750.0,
                'sigma_p': 20.0,
                'pressure_sensitivity': 0.25,
                'DO_min': 2.0,
                'DO_opt': 6.0,
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 2000.0,
                'light_sigma': 2.0,
                'wind_opt': 3.0,
                'moon_amplitude': 0.25,
                'time_peak1': 6.5,
                'time_peak2': 19.5,
                'season_peak': 165,
                'season_amplitude': 0.4,
                'spawn_temp': 16.0,
                'spawn_month': 5
            },
            
            FishSpecies.BREAM: {
                'name_ua': 'Лящ',
                'name_lat': 'Abramis brama',
                'type': 'мирний',
                'T_opt': 19.0,
                'T_min': 4.0,
                'T_max': 26.0,
                'sigma_T': 4.0,
                'p_opt': 755.0,
                'sigma_p': 10.0,
                'pressure_sensitivity': 0.8,
                'DO_min': 5.0,
                'DO_opt': 7.5,
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 800.0,
                'light_sigma': 2.0,
                'wind_opt': 3.0,
                'moon_amplitude': 0.50,
                'time_peak1': 5.5,
                'time_peak2': 20.5,
                'season_peak': 120,
                'season_peak2': 260,
                'season_amplitude': 0.5,
                'spawn_temp': 14.0,
                'spawn_month': 5
            },
            
            FishSpecies.ROACH: {
                'name_ua': 'Плітка',
                'name_lat': 'Rutilus rutilus',
                'type': 'мирний',
                'T_opt': 17.0,
                'T_min': 4.0,
                'T_max': 26.0,
                'sigma_T': 5.0,
                'p_opt': 752.0,
                'sigma_p': 12.0,
                'pressure_sensitivity': 0.35,
                'DO_min': 4.0,
                'DO_opt': 7.0,
                'light_type': LightType.DIURNAL,
                'light_opt': 6000.0,
                'wind_opt': 4.0,
                'moon_amplitude': 0.30,
                'time_peak1': 10.0,
                'time_peak2': None,
                'season_peak': 90,
                'season_amplitude': 0.4,
                'spawn_temp': 12.0,
                'spawn_month': 4
            },
        }
        
        if self.species in profiles:
            for key, value in profiles[self.species].items():
                setattr(self, key, value)
        else:
            raise ValueError(f"Unknown species: {self.species}")


# ============================================================================
# ГІДРОХІМІЧНІ РОЗРАХУНКИ
# ============================================================================

class WaterChemistry:
    """Гідрохімічні розрахунки"""
    
    @staticmethod
    def oxygen_saturation(temp_celsius: float) -> float:
        """
        Розчинність кисню у воді (мг/л) за температурою.
        Формула з дослідження.
        """
        T = temp_celsius
        DO_sat = 14.652 - 0.41022*T + 0.007991*T**2 - 0.000077774*T**3
        return max(0, DO_sat)
    
    @staticmethod
    def oxygen_with_pressure(DO_sat: float, pressure_mmHg: float) -> float:
        """
        Коригування розчинності кисню на атмосферний тиск.
        Закон Генрі: DO ∝ p
        """
        p_normal = 760.0
        DO_corrected = DO_sat * (pressure_mmHg / p_normal)
        return DO_corrected
    
    @staticmethod
    def oxygen_daily_cycle(hour: float, DO_avg: float, amplitude: float = 1.5) -> float:
        """
        Добовий цикл кисню через фотосинтез.
        Мінімум о 5-6 год, максимум о 15-16 год.
        """
        # t₀ = 5.5 (час мінімуму)
        DO = DO_avg + amplitude * math.sin(2 * math.pi * (hour - 5.5) / 24)
        return max(0, DO)
    
    @staticmethod
    def ph_optimal_coefficient(pH: float, pH_opt: float = 7.5, sigma: float = 1.0) -> float:
        """
        Коефіцієнт активності від pH води.
        Оптимум 7.0-8.5, найкраще 7.5
        """
        K_pH = math.exp(-((pH - pH_opt)**2) / (2 * sigma**2))
        return K_pH
    
    @staticmethod
    def water_temp_forecast(T_water_prev: float, T_air: float, 
                           depth_category: str = 'medium') -> float:
        """
        Прогноз температури води на наступну годину.
        T_w(t+1) = T_w(t) + λ × (T_a(t) - T_w(t))
        """
        lambdas = {
            'shallow': PhysicalConstants.THERMAL_INERTIA_SHALLOW,
            'medium': PhysicalConstants.THERMAL_INERTIA_MEDIUM,
            'deep': PhysicalConstants.THERMAL_INERTIA_DEEP
        }
        
        lambda_val = lambdas.get(depth_category, 0.08)
        T_water_new = T_water_prev + lambda_val * (T_air - T_water_prev)
        return T_water_new
    
    @staticmethod
    def light_intensity_at_depth(surface_lux: float, depth_m: float, 
                                 turbidity: str = 'clear') -> float:
        """
        Закон Бера-Ламберта: I(z) = I₀ × exp(-k × z)
        """
        k_values = {
            'clear': 0.1,
            'moderate': 1.0,
            'turbid': 5.0,
            'very_turbid': 10.0
        }
        
        k = k_values.get(turbidity, 0.5)
        I_depth = surface_lux * math.exp(-k * depth_m)
        return I_depth


# ============================================================================
# РОЗРАХУНОК КОЕФІЦІЄНТІВ КІАР
# ============================================================================

class FishActivityCalculations:
    """Розрахунок всіх коефіцієнтів активності риби"""
    
    @staticmethod
    def K_temperature(T_water: float, profile: FishProfile) -> float:
        """
        Температурний коефіцієнт.
        Гауссівський розподіл навколо оптимуму.
        """
        if T_water < profile.T_min or T_water > profile.T_max:
            # Критичні температури - риба майже не активна
            if T_water < profile.T_min:
                K = 0.1 * (T_water / profile.T_min)**2
            else:
                K = 0.1 * (profile.T_max / T_water)**2
            return max(0, min(1.0, K))
        
        # Нормальний діапазон - гауссіан
        K = math.exp(-((T_water - profile.T_opt)**2) / (2 * profile.sigma_T**2))
        return K
    
    @staticmethod
    def K_pressure(pressure_mmHg: float, pressure_change_3h: float, 
                   profile: FishProfile, pre_storm: bool = False) -> float:
        """
        Баричний коефіцієнт.
        Складається з абсолютного значення та тенденції.
        """
        # Частина 1: Абсолютне значення
        K_abs = math.exp(-((pressure_mmHg - profile.p_opt)**2) / 
                        (2 * profile.sigma_p**2))
        
        # Частина 2: Тенденція (швидкість зміни)
        dp_dt = abs(pressure_change_3h) / 3.0  # мм рт.ст./год
        K_trend = 1.0 - min(1.0, dp_dt / PhysicalConstants.BAROMETRIC_CRITICAL_CHANGE)
        
        # Частина 3: Передгрозова активність (бонус для хижаків)
        K_pre_storm = 1.0
        if pre_storm and -3.0 < pressure_change_3h < -1.5:
            if profile.type == 'хижак':
                K_pre_storm = 1.5
            else:
                K_pre_storm = 1.2
        
        K_pressure = K_abs * K_trend * K_pre_storm
        return max(0, K_pressure)
    
    @staticmethod
    def K_oxygen(DO_current: float, profile: FishProfile) -> float:
        """
        Кисневий коефіцієнт.
        Лінійна залежність між мінімумом та оптимумом.
        """
        if DO_current < profile.DO_min:
            return 0.0  # Асфіксія
        elif DO_current >= profile.DO_opt:
            return 1.0  # Оптимум
        else:
            K = (DO_current - profile.DO_min) / (profile.DO_opt - profile.DO_min)
            return K
    
    @staticmethod
    def K_light(illuminance_lux: float, profile: FishProfile) -> float:
        """
        Світловий коефіцієнт.
        Залежить від типу світлової активності риби.
        """
        if profile.light_type == LightType.DIURNAL:
            # Денні види - чим світліше, тим краще (до оптимуму)
            I_opt = profile.light_opt
            K = min(1.0, illuminance_lux / I_opt)
            
        elif profile.light_type == LightType.CREPUSCULAR:
            # Сутінкові - гауссіан навколо оптимуму
            if illuminance_lux <= 0:
                return 0.3
            I_opt = profile.light_opt
            sigma = profile.light_sigma
            log_I = math.log(max(1, illuminance_lux))
            log_I_opt = math.log(I_opt)
            K = math.exp(-((log_I - log_I_opt)**2) / (2 * sigma**2))
            
        elif profile.light_type == LightType.NOCTURNAL:
            # Нічні - чим темніше, тим краще
            I_critical = profile.light_critical
            K = math.exp(-(illuminance_lux / I_critical)**2)
        
        else:
            K = 0.5  # За замовчуванням
        
        return max(0, min(1.5, K))
    
    @staticmethod
    def K_wind(wind_speed_ms: float, profile: FishProfile) -> float:
        """
        Вітровий коефіцієнт.
        Помірний вітер корисний (аерація), сильний - шкідливий.
        """
        v_opt = profile.wind_opt
        sigma_v = 4.0
        k_aer = 0.02  # Бонус за аерацію
        
        # Гауссіан + бонус за аерацію
        K_base = math.exp(-((wind_speed_ms - v_opt)**2) / (2 * sigma_v**2))
        K_aeration = 1.0 + k_aer * wind_speed_ms
        
        K = K_base * K_aeration
        return max(0, min(1.5, K))
    
    @staticmethod
    def K_moon(moon_phase: float, profile: FishProfile) -> float:
        """
        Місячний коефіцієнт.
        moon_phase: 0 = новий місяць, 0.5 = повний, 1.0 = новий
        """
        A = profile.moon_amplitude
        K = 1.0 + A * math.cos(2 * math.pi * moon_phase)
        return max(0, K)
    
    @staticmethod
    def K_time_of_day(hour: float, profile: FishProfile) -> float:
        """
        Часовий коефіцієнт (циркадний ритм).
        """
        if profile.light_type == LightType.NOCTURNAL:
            # Нічні хижаки - пік опівночі
            t_night = 23.0
            sigma_night = 4.0
            K = 0.3 + 0.7 * math.exp(-((hour - t_night)**2) / (2 * sigma_night**2))
            
        elif profile.time_peak2 is not None:
            # Два піки (ранок і вечір)
            t1 = profile.time_peak1
            t2 = profile.time_peak2
            K = (0.5 + 
                 0.25 * math.sin(2 * math.pi * (hour - t1) / 24) +
                 0.25 * math.sin(2 * math.pi * (hour - t2) / 24))
        else:
            # Один пік (зазвичай денний)
            t1 = profile.time_peak1
            K = 0.6 + 0.4 * math.sin(2 * math.pi * (hour - t1) / 24)
        
        return max(0.2, min(1.0, K))
    
    @staticmethod
    def K_season(day_of_year: int, profile: FishProfile, 
                 spawn_correction: float = 1.0) -> float:
        """
        Сезонний коефіцієнт.
        day_of_year: 1-365
        spawn_correction: поправка на нерест
        """
        d = day_of_year
        d_peak = profile.season_peak
        B = profile.season_amplitude
        
        # Основний сезонний цикл
        K_base = 1.0 + B * math.sin(2 * math.pi * (d - d_peak) / 365)
        
        # Якщо є другий пік (осінній жор)
        if hasattr(profile, 'season_peak2'):
            d_peak2 = profile.season_peak2
            K_peak2 = 1.0 + B * math.sin(2 * math.pi * (d - d_peak2) / 365)
            K_base = max(K_base, K_peak2)
        
        # Поправка на нерест
        K = K_base * spawn_correction
        
        return max(0.1, K)
    
    @staticmethod
    def K_weather(rain_mm_per_hour: float, is_storm: bool, pre_storm: bool,
                  post_storm_hours: float, temp_change_24h: float) -> float:
        """
        Погодний коефіцієнт.
        """
        # Дощ
        if rain_mm_per_hour < 5:
            K_rain = 1.2  # Короткочасний дощ - добре
        elif rain_mm_per_hour < 10:
            K_rain = 1.1  # Помірний
        else:
            K_rain = 0.7  # Злива - погано
        
        if rain_mm_per_hour == 0:
            K_rain = 1.0
        
        # Гроза
        if is_storm:
            K_storm = 0.1  # Під час грози - майже немає активності
        elif pre_storm:
            K_storm = 1.5  # Передгрозова - ЖОР!
        elif 0 < post_storm_hours < 4:
            K_storm = 1.4  # Післягрозова
        else:
            K_storm = 1.0
        
        # Різка зміна температури
        if abs(temp_change_24h) > 5:
            if temp_change_24h < 0:
                K_temp_change = 0.5  # Похолодання
            else:
                K_temp_change = 1.3  # Потепління
        else:
            K_temp_change = 1.0
        
        K = K_rain * K_storm * K_temp_change
        return max(0.1, min(2.0, K))


# ============================================================================
# ГОЛОВНА СИСТЕМА ПРОГНОЗУВАННЯ
# ============================================================================

class FishBiteForecastSystem:
    """Професійна система прогнозування клювання риби"""
    
    def __init__(self, species: FishSpecies):
        self.species = species
        self.profile = FishProfile(species)
        self.calc = FishActivityCalculations()
        self.chem = WaterChemistry()
        
        logging.info("=" * 70)
        logging.info(f"СИСТЕМА ПРОГНОЗУВАННЯ КЛЮВАННЯ: {self.profile.name_ua}")
        logging.info(f"Латинська назва: {self.profile.name_lat}")
        logging.info(f"Тип: {self.profile.type}")
        logging.info("=" * 70)
    
    def calculate_KIAR(self, conditions: Dict) -> Dict:
        """
        Розрахунок Комплексного Індексу Активності Риби (КІАР).
        
        conditions - словник з усіма метеорологічними та гідрологічними параметрами.
        """
        # Витягування параметрів
        T_water = conditions.get('water_temp_celsius', 15.0)
        T_air = conditions.get('air_temp_celsius', 15.0)
        pressure = conditions.get('pressure_mmHg', 755.0)
        pressure_change_3h = conditions.get('pressure_change_3h_mmHg', 0.0)
        DO = conditions.get('dissolved_oxygen_mg_l', None)
        illuminance = conditions.get('illuminance_lux', 5000.0)
        wind_speed = conditions.get('wind_speed_ms', 2.0)
        moon_phase = conditions.get('moon_phase', 0.5)  # 0-1
        hour = conditions.get('hour_of_day', 12.0)  # 0-24
        day_of_year = conditions.get('day_of_year', 180)
        rain = conditions.get('rain_mm_per_hour', 0.0)
        is_storm = conditions.get('is_storm', False)
        pre_storm = conditions.get('pre_storm', False)
        post_storm_hours = conditions.get('post_storm_hours', 99)
        temp_change_24h = conditions.get('temp_change_24h', 0.0)
        pH = conditions.get('pH', 7.5)
        
        # Якщо кисень не вказаний - розраховуємо
        if DO is None:
            DO_sat = self.chem.oxygen_saturation(T_water)
            DO = self.chem.oxygen_with_pressure(DO_sat, pressure)
            DO = self.chem.oxygen_daily_cycle(hour, DO)
        
        # Розрахунок коефіцієнтів
        K_temp = self.calc.K_temperature(T_water, self.profile)
        K_pressure = self.calc.K_pressure(pressure, pressure_change_3h, 
                                         self.profile, pre_storm)
        K_oxygen = self.calc.K_oxygen(DO, self.profile)
        K_light = self.calc.K_light(illuminance, self.profile)
        K_wind = self.calc.K_wind(wind_speed, self.profile)
        K_moon = self.calc.K_moon(moon_phase, self.profile)
        K_time = self.calc.K_time_of_day(hour, self.profile)
        K_season = self.calc.K_season(day_of_year, self.profile)
        K_weather = self.calc.K_weather(rain, is_storm, pre_storm, 
                                       post_storm_hours, temp_change_24h)
        K_pH = self.chem.ph_optimal_coefficient(pH)
        
        # КІАР (мультиплікативна модель)
        KIAR = (K_temp * K_pressure * K_oxygen * K_light * K_wind *
                K_moon * K_time * K_season * K_weather * K_pH) * 100.0
        
        # Обмеження
        KIAR = max(0, min(200, KIAR))
        
        # Інтерпретація
        if KIAR < 20:
            interpretation = "Дуже низька активність - клювання малоймовірне"
            recommendation = "Не рекомендуємо рибалку"
        elif KIAR < 40:
            interpretation = "Низька активність - слабкий клів можливий"
            recommendation = "Клювання буде рідким"
        elif KIAR < 60:
            interpretation = "Помірна активність - середній клів"
            recommendation = "Можна спробувати порибалити"
        elif KIAR < 80:
            interpretation = "Висока активність - хороший клів очікується"
            recommendation = "Хороший час для риболовлі!"
        elif KIAR < 100:
            interpretation = "Дуже висока активність - відмінний клів!"
            recommendation = "Чудовий час для рибалки!"
        else:
            interpretation = "ЕКСТРЕМАЛЬНА АКТИВНІСТЬ - ЖОР!"
            recommendation = "⭐ ТЕРМІН ОВО НА ВОДОЙМУ! Унікальні умови!"
        
        # Результат
        result = {
            'KIAR_percent': round(KIAR, 1),
            'interpretation': interpretation,
            'recommendation': recommendation,
            'coefficients': {
                'K_temperature': round(K_temp, 3),
                'K_pressure': round(K_pressure, 3),
                'K_oxygen': round(K_oxygen, 3),
                'K_light': round(K_light, 3),
                'K_wind': round(K_wind, 3),
                'K_moon': round(K_moon, 3),
                'K_time_of_day': round(K_time, 3),
                'K_season': round(K_season, 3),
                'K_weather': round(K_weather, 3),
                'K_pH': round(K_pH, 3)
            },
            'conditions': conditions,
            'fish_profile': {
                'species': self.profile.name_ua,
                'type': self.profile.type,
                'T_opt': self.profile.T_opt,
                'light_type': self.profile.light_type.value
            }
        }
        
        return result
    
    def print_forecast_report(self, kiar_result: Dict):
        """Виведення детального звіту прогнозу"""
        print("\n" + "=" * 80)
        print(f"ПРОГНОЗ КЛЮВАННЯ: {self.profile.name_ua.upper()} ({self.profile.name_lat})")
        print("=" * 80)
        
        # КІАР
        KIAR = kiar_result['KIAR_percent']
        print(f"\n🎣 КІАР (Комплексний Індекс Активності Риби): {KIAR:.1f}%")
        print(f"📊 Інтерпретація: {kiar_result['interpretation']}")
        print(f"💡 Рекомендація: {kiar_result['recommendation']}")
        
        # Умови
        print("\n🌊 УМОВИ ВОДОЙМИ:")
        print("-" * 80)
        cond = kiar_result['conditions']
        print(f"Температура води: {cond.get('water_temp_celsius', 'N/A'):.1f}°C")
        print(f"Температура повітря: {cond.get('air_temp_celsius', 'N/A'):.1f}°C")
        print(f"Розчинений кисень: {cond.get('dissolved_oxygen_mg_l', 'N/A'):.1f} мг/л")
        print(f"pH води: {cond.get('pH', 7.5):.1f}")
        print(f"Освітленість: {cond.get('illuminance_lux', 'N/A'):.0f} лк")
        
        # Метеорологія
        print("\n🌤️  МЕТЕОРОЛОГІЧНІ УМОВИ:")
        print("-" * 80)
        print(f"Атмосферний тиск: {cond.get('pressure_mmHg', 'N/A'):.1f} мм рт.ст.")
        print(f"Зміна тиску за 3 год: {cond.get('pressure_change_3h_mmHg', 0):.1f} мм рт.ст.")
        print(f"Швидкість вітру: {cond.get('wind_speed_ms', 'N/A'):.1f} м/с")
        print(f"Опади: {cond.get('rain_mm_per_hour', 0):.1f} мм/год")
        
        # Коефіцієнти
        print("\n📈 ДЕТАЛЬНА РОЗБИВКА ФАКТОРІВ:")
        print("-" * 80)
        coeffs = kiar_result['coefficients']
        for name, value in coeffs.items():
            bar = "█" * int(value * 20)
            print(f"{name:.<30} {value:.3f} {bar}")
        
        # Профіль риби
        print("\n🐟 ХАРАКТЕРИСТИКИ ВИДУ:")
        print("-" * 80)
        prof = kiar_result['fish_profile']
        print(f"Тип: {prof['type']}")
        print(f"Оптимальна температура: {prof['T_opt']:.1f}°C")
        print(f"Тип світлової активності: {prof['light_type']}")
        
        print("=" * 80 + "\n")


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def main():
    """Демонстрація роботи системи"""
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 15 + "СИСТЕМА ПРОГНОЗУВАННЯ КЛЮВАННЯ РИБИ" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    # Приклад 1: Літній вечір, короп
    print("\n### ПРИКЛАД 1: Літній вечір, короп ###\n")
    
    carp_forecast = FishBiteForecastSystem(FishSpecies.CARP)
    
    conditions_summer_carp = {
        'water_temp_celsius': 24.0,
        'air_temp_celsius': 28.0,
        'pressure_mmHg': 755.0,
        'pressure_change_3h_mmHg': -0.5,
        'dissolved_oxygen_mg_l': 7.2,
        'illuminance_lux': 8000.0,
        'wind_speed_ms': 3.0,
        'moon_phase': 0.25,  # Перша чверть
        'hour_of_day': 18.0,
        'day_of_year': 166,  # 15 червня
        'rain_mm_per_hour': 0.0,
        'is_storm': False,
        'pre_storm': False,
        'post_storm_hours': 99,
        'temp_change_24h': 2.0,
        'pH': 7.5
    }
    
    result1 = carp_forecast.calculate_KIAR(conditions_summer_carp)
    carp_forecast.print_forecast_report(result1)
    
    # Приклад 2: Передгрозова щука
    print("\n### ПРИКЛАД 2: Передгрозова активність, щука ###\n")
    
    pike_forecast = FishBiteForecastSystem(FishSpecies.PIKE)
    
    conditions_pre_storm_pike = {
        'water_temp_celsius': 16.0,
        'air_temp_celsius': 18.0,
        'pressure_mmHg': 745.0,
        'pressure_change_3h_mmHg': -6.9,  # Швидке падіння!
        'dissolved_oxygen_mg_l': 9.5,
        'illuminance_lux': 3000.0,  # Хмарно
        'wind_speed_ms': 6.0,
        'moon_phase': 0.1,  # Молодий місяць
        'hour_of_day': 14.0,
        'day_of_year': 263,  # 20 вересня (осінній жор)
        'rain_mm_per_hour': 0.0,
        'is_storm': False,
        'pre_storm': True,  # Передгрозова!
        'post_storm_hours': 99,
        'temp_change_24h': -3.0,
        'pH': 7.2
    }
    
    result2 = pike_forecast.calculate_KIAR(conditions_pre_storm_pike)
    pike_forecast.print_forecast_report(result2)
    
    # Приклад 3: Зимовий карась
    print("\n### ПРИКЛАД 3: Зимовий день, карась ###\n")
    
    crucian_forecast = FishBiteForecastSystem(FishSpecies.CRUCIAN)
    
    conditions_winter_crucian = {
        'water_temp_celsius': 3.0,
        'air_temp_celsius': 0.0,
        'pressure_mmHg': 765.0,
        'pressure_change_3h_mmHg': 0.2,
        'dissolved_oxygen_mg_l': 12.0,
        'illuminance_lux': 15000.0,
        'wind_speed_ms': 1.0,
        'moon_phase': 0.5,  # Повний місяць
        'hour_of_day': 12.0,
        'day_of_year': 339,  # 5 грудня
        'rain_mm_per_hour': 0.0,
        'is_storm': False,
        'pre_storm': False,
        'post_storm_hours': 99,
        'temp_change_24h': -1.0,
        'pH': 7.8
    }
    
    result3 = crucian_forecast.calculate_KIAR(conditions_winter_crucian)
    crucian_forecast.print_forecast_report(result3)
    
    # Збереження результатів у JSON
    output_data = {
        'forecast_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'example_1_carp': result1,
        'example_2_pike': result2,
        'example_3_crucian': result3
    }
    
    with open('fishing_forecast_output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4, default=str)
    
    logging.info("Прогнози збережено у fishing_forecast_output.json")
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ПРОГНОЗУВАННЯ ЗАВЕРШЕНО" + " " * 35 + "║")
    print("╚" + "═" * 78 + "╝\n")


if __name__ == "__main__":
    main()

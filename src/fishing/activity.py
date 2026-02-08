"""
Fish Activity Calculations and Bite Forecast System
===================================================

This module contains the core fish activity calculation algorithms and the
complete bite forecasting system. It uses complex multi-factor models based on:

- Temperature physiology (Van't Hoff rule for cold-blooded animals)
- Barometric pressure effects
- Dissolved oxygen requirements  
- Light/photoperiod patterns
- Wind and aeration
- Lunar phases and circadian rhythms
- Seasonal patterns
- Weather conditions

The system calculates KIAR (Complex Index of Fish Activity) using a 
multiplicative model of all environmental factors. All scientific formulas
and calculations are preserved for accuracy.

MicroPython compatible - uses no numpy dependencies.

Author: Scientific Ichthyology Research System
Date: 2026
"""

import math
from datetime import datetime
from typing import Dict, List, Optional

from ..core.constants import PhysicalConstants
from ..core.calculations import mean, std_dev
from .profiles import FishProfile, FishSpecies, LightType
from .chemistry import WaterChemistry


def log(message: str, level: str = "INFO") -> None:
    """Simple logging function compatible with MicroPython"""
    try:
        print(f"[{level}] FISH: {message}")
    except:
        pass


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


class FishBiteForecastSystem:
    """Професійна система прогнозування клювання риби"""
    
    def __init__(self, species: FishSpecies):
        self.species = species
        self.profile = FishProfile(species)
        self.calc = FishActivityCalculations()
        self.chem = WaterChemistry()
        
        log("=" * 70)
        log(f"СИСТЕМА ПРОГНОЗУВАННЯ КЛЮВАННЯ: {self.profile.name_ua}")
        log(f"Латинська назва: {self.profile.name_lat}")
        log(f"Тип: {self.profile.type}")
        log("=" * 70)
    
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
    
    def save_forecast_to_json(self, kiar_result: Dict, filename: str = 'forecast.json'):
        """Save forecast results to JSON file (MicroPython compatible)"""
        try:
            import ujson as json
        except ImportError:
            import json
        
        output_data = {
            'forecast_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S') if hasattr(datetime, 'now') else 'N/A',
            'forecast': kiar_result
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=4)
            log(f"Прогноз збережено у {filename}")
        except Exception as e:
            log(f"Помилка збереження: {e}", "ERROR")

"""
ПРОФЕСІЙНА СИСТЕМА ПРОГНОЗУВАННЯ ПОГОДИ
========================================

Використовує всі метеорологічні формули та методи з професійного довідника:
- Баричні формули та тенденції
- Психрометричні розрахунки вологості
- Адіабатичні процеси
- Синоптичний аналіз
- Статистичні методи прогнозування
- Індекси нестійкості атмосфери

Автор: Професійна метеорологічна система
Дата: 2026
"""

import json
import logging
import math
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] FORECAST: %(message)s',
    handlers=[
        logging.FileHandler("system.log"),
        logging.StreamHandler()
    ]
)


# ============================================================================
# КОНСТАНТИ ТА ФІЗИЧНІ ПАРАМЕТРИ
# ============================================================================

class PhysicalConstants:
    """Фізичні константи з метеорологічного довідника"""
    
    # Основні константи
    R = 287  # Газова стала повітря, Дж/(кг·К)
    g = 9.81  # Прискорення вільного падіння, м/с²
    cp = 1005  # Питома теплоємність при постійному тиску, Дж/(кг·К)
    cv = 718  # Питома теплоємність при постійному об'ємі, Дж/(кг·К)
    gamma = 1.4  # Показник адіабати
    L = 2.5e6  # Питома теплота пароутворення, Дж/кг
    
    # Психрометричні константи
    A = 0.000662  # Психрометричний коефіцієнт
    
    # Вертикальні градієнти
    GAMMA_DRY = 1.0  # Сухоадіабатичний градієнт, °C/100м
    GAMMA_WET = 0.5  # Вологоадіабатичний градієнт, °C/100м
    GAMMA_NORMAL = 0.6  # Нормальний градієнт, °C/100м
    
    # Стандартні умови
    P0_HPA = 1013.25  # Нормальний атмосферний тиск, гПа
    P0_MMHG = 760  # Нормальний тиск, мм рт.ст.
    T0_CELSIUS = 15  # Стандартна температура, °C
    T0_KELVIN = 273.15  # Абсолютний нуль
    
    # Емпіричні коефіцієнти
    BARIC_STEP_COEF = 8000  # Для розрахунку баричного ступеня
    CONDENSATION_COEF = 122  # Коефіцієнт рівня конденсації, м/°C

    # === НОВІ КОНСТАНТИ (Крок 1) ===
    ELEVATION = 262  # Висота Вінниці над рівнем моря (м)
    EMA_ALPHA = 0.3  # Коефіцієнт згладжування шуму датчиків (0.1 - дуже плавно, 1.0 - без змін)


# ============================================================================
# МЕТЕОРОЛОГІЧНІ РОЗРАХУНКИ
# ============================================================================

class MeteoCalculations:
    """Клас для всіх метеорологічних розрахунків за формулами з довідника"""
    
    @staticmethod
    def adjust_pressure_to_sea_level(p_station: float, t_celsius: float) -> float:
        """
        Приведення тиску до рівня моря (MSLP).
        Критично важливо для правильного прогнозу погоди на висоті > 0м.
        """
        h = PhysicalConstants.ELEVATION
        if h == 0: return p_station
        
        # Середня температура стовпа повітря (Кельвіни) + поправка на градієнт
        t_kelvin = t_celsius + 273.15 + (h * 0.0065 / 2)
        
        # Барометрична формула
        # 0.034163 - це константа, виведена з g * M / R
        p_sea_level = p_station * math.exp((0.034163 * h) / t_kelvin)
        return p_sea_level
        
    
    @staticmethod
    def celsius_to_kelvin(t_celsius: float) -> float:
        """Перетворення Цельсія в Кельвіни"""
        return t_celsius + PhysicalConstants.T0_KELVIN
    
    @staticmethod
    def kelvin_to_celsius(t_kelvin: float) -> float:
        """Перетворення Кельвінів в Цельсії"""
        return t_kelvin - PhysicalConstants.T0_KELVIN
    
    @staticmethod
    def saturation_pressure(t_celsius: float) -> float:
        """
        Розрахунок пружності насичення водяної пари (гПа) за температурою.
        Використовує формулу Магнуса для точних розрахунків.
        
        Формула Магнуса: E = 6.112 × exp((17.67 × T)/(T + 243.5))
        де T - температура в °C
        """
        if t_celsius < -40:
            # Для дуже низьких температур (лід)
            return 0.1
        
        # Формула Магнуса (похідна від Клаузіуса-Клапейрона)
        E = 6.112 * math.exp((17.67 * t_celsius) / (t_celsius + 243.5))
        return E
    
    @staticmethod
    def actual_vapor_pressure(t_celsius: float, humidity_percent: float) -> float:
        """
        Розрахунок фактичної пружності водяної пари.
        
        Формула: e = E × (f/100)
        де E - пружність насичення, f - відносна вологість
        """
        E = MeteoCalculations.saturation_pressure(t_celsius)
        e = E * (humidity_percent / 100.0)
        return e
    
    @staticmethod
    def dew_point(t_celsius: float, humidity_percent: float) -> float:
        """
        Розрахунок точки роси за температурою і вологістю.
        
        Використовує обернену формулу Магнуса:
        τ = (243.5 × ln(e/6.112)) / (17.67 - ln(e/6.112))
        """
        e = MeteoCalculations.actual_vapor_pressure(t_celsius, humidity_percent)
        
        if e <= 0.1:
            return -40.0
        
        # Обернена формула Магнуса
        ln_ratio = math.log(e / 6.112)
        dew_point = (243.5 * ln_ratio) / (17.67 - ln_ratio)
        
        return dew_point
    
    @staticmethod
    def humidity_deficit(t_celsius: float, humidity_percent: float) -> float:
        """
        Розрахунок дефіциту вологості.
        
        Формула: d = E - e = E × (1 - f/100)
        """
        E = MeteoCalculations.saturation_pressure(t_celsius)
        e = MeteoCalculations.actual_vapor_pressure(t_celsius, humidity_percent)
        return E - e
    
    @staticmethod
    def condensation_level(t_celsius: float, humidity_percent: float) -> float:
        """
        Розрахунок висоти рівня конденсації (м).
        
        Формула: Hк = 122 × Δτ
        де Δτ = t - τ (дефіцит точки роси)
        """
        tau = MeteoCalculations.dew_point(t_celsius, humidity_percent)
        delta_tau = t_celsius - tau
        
        Hk = PhysicalConstants.CONDENSATION_COEF * delta_tau
        return max(0, Hk)
    
    @staticmethod
    def baric_step(t_celsius: float) -> float:
        """
        Розрахунок баричного ступеня (м/гПа).
        
        Формула: Hб = 8000 × (1 + 0.004 × t) / 1000
        де t - температура повітря в °C
        
        Показує, на скільки метрів треба піднятися/опуститися,
        щоб тиск змінився на 1 гПа.
        """
        Hb = (PhysicalConstants.BARIC_STEP_COEF * (1 + 0.004 * t_celsius)) / 1000
        return Hb
    
    @staticmethod
    def pressure_tendency_to_height(delta_p: float, t_celsius: float) -> float:
        """
        Перетворення зміни тиску в зміну висоти.
        
        Використовує баричний ступінь:
        Δh = Нб × Δp
        """
        Hb = MeteoCalculations.baric_step(t_celsius)
        delta_h = Hb * delta_p
        return delta_h
    
    @staticmethod
    def air_density(pressure_hpa: float, t_celsius: float) -> float:
        """
        Розрахунок щільності повітря (кг/м³).
        
        Рівняння стану: ρ = p / (R × T)
        де p - тиск в Па, R - газова стала, T - температура в К
        """
        p_pa = pressure_hpa * 100  # Переведення гПа в Па
        T_kelvin = MeteoCalculations.celsius_to_kelvin(t_celsius)
        
        rho = p_pa / (PhysicalConstants.R * T_kelvin)
        return rho
    
    @staticmethod
    def potential_temperature(t_celsius: float, pressure_hpa: float) -> float:
        """
        Розрахунок потенційної температури (K).
        
        Формула: θ = T × (1000/p)^0.286
        де T - температура в К, p - тиск в гПа
        
        Потенційна температура зберігається при адіабатичних процесах.
        """
        T_kelvin = MeteoCalculations.celsius_to_kelvin(t_celsius)
        theta = T_kelvin * math.pow(1000.0 / pressure_hpa, 0.286)
        return theta
    
    @staticmethod
    def stability_index(t_surface: float, humidity: float) -> Dict[str, float]:
        """
        Розрахунок індексів нестійкості з урахуванням вологості.
        Джерело: Адіабатичні градієнти 
        """
        # Визначаємо реальний градієнт (швидкість падіння температури)
        if humidity >= 90:
            gamma = 0.5  # Волога адіабата (повітря повільно остигає)
        elif humidity <= 40:
            gamma = 0.98 # Суха адіабата (повітря швидко остигає)
        else:
            # Плавний перехід між 0.6 та 0.98
            gamma = 0.6 + (0.98 - 0.6) * ((70 - humidity) / 30)

        # Розрахунок температур на висотах (симуляція)
        # 850 гПа ~ 1.5 км, 500 гПа ~ 5.5 км
        t_850_est = t_surface - (gamma * 15)
        t_500_est = t_surface - (gamma * 55)
        
        # Температура частки, що піднімається (завжди по вологій адіабаті для грози)
        t_parcel_500 = t_surface - (0.5 * 55) 
        
        # Індекс Шоуолтера
        SI = t_500_est - t_parcel_500
        
        return {
            'showalter_index': round(SI, 1),
            'lifted_index': round(-SI, 1),
            'parcel_temp_500': round(t_parcel_500, 1)
        }


# ============================================================================
# СИНОПТИЧНИЙ АНАЛІЗ
# ============================================================================

class SynopticAnalysis:
    """Синоптичний аналіз погодних умов"""
    
    @staticmethod
    def pressure_tendency_analysis(pressure_data: List[float]) -> Dict:
        """
        Аналіз баричної тенденції.
        
        Класифікація:
        - Швидко падає: < -3 гПа/3год
        - Падає: -3 до -1 гПа/3год
        - Стабільний: -1 до +1 гПа/3год
        - Зростає: +1 до +3 гПа/3год
        - Швидко зростає: > +3 гПа/3год
        """
        if len(pressure_data) < 4:
            return {'tendency': 'insufficient_data', 'delta': 0, 'trend': 'unknown'}
        
        # Беремо останні 3 години (індекси -3, -2, -1, поточний)
        recent = pressure_data[-4:]
        delta_3h = recent[-1] - recent[0]
        
        # Тренд за останні 6 годин, якщо є дані
        if len(pressure_data) >= 7:
            delta_6h = pressure_data[-1] - pressure_data[-7]
            long_term_trend = 'falling' if delta_6h < -1 else ('rising' if delta_6h > 1 else 'stable')
        else:
            long_term_trend = 'unknown'
        
        # Класифікація тенденції
        if delta_3h < -3:
            tendency = 'rapidly_falling'
            description = 'Швидко падає'
        elif delta_3h < -1:
            tendency = 'falling'
            description = 'Падає'
        elif delta_3h > 3:
            tendency = 'rapidly_rising'
            description = 'Швидко зростає'
        elif delta_3h > 1:
            tendency = 'rising'
            description = 'Зростає'
        else:
            tendency = 'steady'
            description = 'Стабільний'
        
        return {
            'tendency': tendency,
            'description': description,
            'delta_3h': round(delta_3h, 1),
            'delta_per_hour': round(delta_3h / 3, 2),
            'long_term_trend': long_term_trend
        }
    
    @staticmethod
    def front_detection(pressure_tendency: Dict, temp_data: List[float], 
                        hum_data: List[float]) -> Dict:
        """
        Виявлення атмосферних фронтів за зміною метеопараметрів.
        
        Ознаки фронтів:
        - Різкі зміни тиску
        - Зміна температури
        - Зміна вологості
        - Зміна напрямку вітру (не вимірюється в цій системі)
        """
        if len(temp_data) < 4 or len(hum_data) < 4:
            return {'front_type': 'none', 'probability': 0}
        
        # Аналіз змін
        temp_change = temp_data[-1] - temp_data[-4]
        hum_change = hum_data[-1] - hum_data[-4]
        pressure_trend = pressure_tendency['tendency']
        
        # Холодний фронт: тиск зростає, температура падає, вологість спочатку зростає
        if pressure_trend in ['rising', 'rapidly_rising'] and temp_change < -2:
            return {
                'front_type': 'cold_front',
                'probability': min(85, 60 + abs(temp_change) * 5),
                'description': 'Можливий холодний фронт',
                'characteristics': 'Похолодання, можливі зливи'
            }
        
        # Теплий фронт: тиск падає, температура зростає, вологість зростає
        elif pressure_trend in ['falling', 'rapidly_falling'] and temp_change > 2:
            return {
                'front_type': 'warm_front',
                'probability': min(80, 55 + temp_change * 5),
                'description': 'Можливий теплий фронт',
                'characteristics': 'Потепління, обложні опади'
            }
        
        # Оклюзія: складна ситуація з різкими змінами
        elif pressure_trend == 'rapidly_falling' and abs(temp_change) > 3:
            return {
                'front_type': 'occluded_front',
                'probability': 70,
                'description': 'Можлива оклюзія',
                'characteristics': 'Складна погода, опади'
            }
        
        else:
            return {
                'front_type': 'none',
                'probability': 0,
                'description': 'Фронти не виявлені'
            }
    
    @staticmethod
    def classify_air_mass(temp: float, humidity: float, pressure: float) -> Dict:
        """
        Класифікація повітряної маси за її характеристиками.
        
        Типи повітряних мас:
        - Арктична (А): дуже холодна, суха
        - Полярна континентальна (Пк): холодна, суха
        - Полярна морська (Пм): помірно холодна, волога
        - Тропічна континентальна (Тк): тепла, суха
        - Тропічна морська (Тм): тепла, волога
        - Екваторіальна (Е): дуже тепла, дуже волога
        """
        if temp < -15:
            if humidity < 60:
                return {'type': 'Arctic', 'description': 'Арктична', 'stability': 'stable'}
            else:
                return {'type': 'Arctic_modified', 'description': 'Трансформована арктична', 'stability': 'stable'}
        
        elif temp < 5:
            if humidity < 60:
                return {'type': 'Polar_Continental', 'description': 'Полярна континентальна', 'stability': 'stable'}
            else:
                return {'type': 'Polar_Maritime', 'description': 'Полярна морська', 'stability': 'unstable'}
        
        elif temp < 20:
            if humidity < 60:
                return {'type': 'Temperate_Continental', 'description': 'Помірна континентальна', 'stability': 'neutral'}
            else:
                return {'type': 'Temperate_Maritime', 'description': 'Помірна морська', 'stability': 'unstable'}
        
        else:  # temp >= 20
            if humidity < 50:
                return {'type': 'Tropical_Continental', 'description': 'Тропічна континентальна', 'stability': 'very_stable'}
            else:
                return {'type': 'Tropical_Maritime', 'description': 'Тропічна морська', 'stability': 'very_unstable'}



class ZambrettiForecaster:
    """
    Класичний алгоритм прогнозування Zambretti.
    Адаптовано для MSLP (тиску на рівні моря).
    """
    
    @staticmethod
    def get_forecast(pressure_mslp: float, trend_code: str, month: int) -> Dict:
        """
        pressure_mslp: Тиск, приведений до рівня моря (гПа)
        trend_code: 'rising', 'falling', 'steady' (береться з SynopticAnalysis)
        month: місяць (1-12) для визначення сезону
        """
        # Визначаємо сезон (Зима = Жовтень-Березень для півн. півкулі)
        is_winter = month in [10, 11, 12, 1, 2, 3]
        
        forecast_text = "Невизначено"
        
        # 1. ТИСК ПАДАЄ (FALLING)
        if trend_code in ['falling', 'rapidly_falling']:
            if pressure_mslp > 1030: forecast_text = "Ясно, тепліше" if not is_winter else "Сухо, мороз послабне"
            elif pressure_mslp > 1020: forecast_text = "Мінлива хмарність, тепліше"
            elif pressure_mslp > 1010: forecast_text = "Погіршення погоди, вітряно"
            elif pressure_mslp > 1000: forecast_text = "Дощ/Сніг, вітер"
            else: forecast_text = "Шторм, сильний дощ/сніг"
            
        # 2. ТИСК РОСТЕ (RISING)
        elif trend_code in ['rising', 'rapidly_rising']:
            if pressure_mslp > 1030: forecast_text = "Стійка ясна погода"
            elif pressure_mslp > 1020: forecast_text = "Ясно, холодно"
            elif pressure_mslp > 1010: forecast_text = "Покращення погоди"
            elif pressure_mslp > 1000: forecast_text = "Мінлива хмарність, прохолодно"
            else: forecast_text = "Хмарно, можливе покращення"
            
        # 3. ТИСК СТАБІЛЬНИЙ (STEADY)
        else:
            if pressure_mslp > 1020: forecast_text = "Гарна погода, без змін"
            elif pressure_mslp > 1010: forecast_text = "Мінлива хмарність"
            else: forecast_text = "Похмуро, можливі опади"

        return {
            "algorithm": "Zambretti",
            "forecast_text": forecast_text,
            "pressure_context": "High" if pressure_mslp > 1013 else "Low"
        }
        


# ============================================================================
# ПРОГНОЗУВАННЯ ОПАДІВ
# ============================================================================



class PrecipitationForecast:
    """Прогнозування опадів на основі метеорологічних даних"""
    
    @staticmethod
    def calculate_precipitation_probability(
        humidity: float,
        dew_point_deficit: float,
        pressure_tendency: str,
        condensation_level: float,
        stability: str
    ) -> Dict:
        """
        Комплексний розрахунок ймовірності опадів.
        
        Враховує:
        - Вологість повітря
        - Дефіцит точки роси (близькість до насичення)
        - Баричну тенденцію
        - Рівень конденсації
        - Стабільність атмосфери
        """
        # Базова ймовірність від вологості
        if humidity >= 90:
            base_prob = 80
        elif humidity >= 80:
            base_prob = 60
        elif humidity >= 70:
            base_prob = 40
        elif humidity >= 60:
            base_prob = 20
        else:
            base_prob = 5
        
        # Коригування за дефіцитом точки роси
        # Чим менший дефіцит, тим ближче до насичення
        if dew_point_deficit < 1:
            base_prob += 15
        elif dew_point_deficit < 2:
            base_prob += 10
        elif dew_point_deficit < 3:
            base_prob += 5
        
        # Коригування за тиском
        if pressure_tendency in ['rapidly_falling', 'falling']:
            base_prob += 20
        elif pressure_tendency in ['rapidly_rising', 'rising']:
            base_prob -= 15
        
        # Коригування за рівнем конденсації
        # Низький рівень конденсації = більша ймовірність опадів
        if condensation_level < 500:
            base_prob += 15
        elif condensation_level < 1000:
            base_prob += 10
        elif condensation_level < 1500:
            base_prob += 5
        
        # Коригування за стабільністю
        if stability in ['very_unstable', 'unstable']:
            base_prob += 10
            precipitation_type = 'Зливові'
        else:
            precipitation_type = 'Обложні'
        
        # Обмеження 0-100%
        final_prob = max(0, min(100, base_prob))
        
        # Визначення інтенсивності
        if final_prob >= 80:
            intensity = 'Сильні'
        elif final_prob >= 60:
            intensity = 'Помірні'
        elif final_prob >= 40:
            intensity = 'Слабкі'
        else:
            intensity = 'Можливі'
        
        return {
            'probability': round(final_prob, 1),
            'type': precipitation_type,
            'intensity': intensity,
            'description': f'{intensity} {precipitation_type.lower()} опади'
        }
    
    @staticmethod
    def snow_or_rain(temp_celsius: float, humidity: float) -> str:
        """
        Визначення типу опадів: сніг чи дощ.
        
        Правила:
        - Температура < -2°C: сніг
        - Температура -2 до +2°C: мокрий сніг або дощ зі снігом
        - Температура > +2°C: дощ
        """
        if temp_celsius < -2:
            return 'Сніг'
        elif temp_celsius <= 2:
            if humidity > 85:
                return 'Мокрий сніг'
            else:
                return 'Дощ зі снігом'
        else:
            return 'Дощ'


# ============================================================================
# ПРОГНОЗУВАННЯ НЕБЕЗПЕЧНИХ ЯВИЩ
# ============================================================================

class HazardousForecast:
    """Прогнозування небезпечних метеорологічних явищ (Winter-Safe Edition)"""
    
    @staticmethod
    def thunderstorm_probability(
        temp: float,
        humidity: float,
        pressure_tendency: str,
        stability_index: float
    ) -> Dict:
        """
        Прогноз ймовірності грози.
        Використовує індекс нестійкості Шоуолтера (SI).
        """
        # === ВИПРАВЛЕННЯ №1: Температурний запобіжник ===
        # Якщо надворі холодно (нижче +5°C), класична гроза фізично неможлива,
        # навіть якщо індекси показують нестабільність.
        if temp < 5.0:
            return {
                'probability': 0,
                'severity': 'Неможлива',
                'description': 'Гроза неможлива (низька температура)'
            }
        # ================================================

        base_prob = 0
        severity = 'Гроза малоймовірна'
        
        # Базова оцінка за індексом нестійкості
        if stability_index < 0:
            base_prob = 85 + min(15, abs(stability_index) * 5)
            severity = 'Сильна гроза'
        elif stability_index <= 3:
            base_prob = 50 + (3 - stability_index) * 10
            severity = 'Гроза'
        elif stability_index <= 6:
            base_prob = 20 + (6 - stability_index) * 10
            severity = 'Слабка гроза'
        else:
            base_prob = max(0, 20 - (stability_index - 6) * 3)
            
        # Коригування за температурою (грози частіше при високій температурі)
        if temp > 25:
            base_prob += 10
        elif temp > 20:
            base_prob += 5
        
        # Коригування за вологістю
        if humidity > 70:
            base_prob += 5
        
        # Коригування за тиском
        if pressure_tendency in ['rapidly_falling', 'falling']:
            base_prob += 10
        
        final_prob = max(0, min(100, base_prob))
        
        return {
            'probability': round(final_prob, 1),
            'severity': severity,
            'description': f'{severity} з ймовірністю {final_prob:.0f}%'
        }
    
    @staticmethod
    def fog_probability(temp: float, humidity: float, dew_point_deficit: float) -> Dict:
        """
        Прогноз ймовірності туману.
        """
        # === ВИПРАВЛЕННЯ №2: Фізичний фільтр туману ===
        # Туман неможливий, якщо повітря не насичене вологою (дефіцит > 2.5°C).
        # Це прибирає помилкові спрацювання в суху погоду.
        if dew_point_deficit > 2.5:
             return {
                'probability': 0,
                'type': 'none',
                'description': 'Туман неможливий (повітря сухе)'
            }
        # ==============================================

        base_prob = 0
        
        # Основний фактор - дефіцит точки роси
        if dew_point_deficit < 0.5:
            base_prob = 90
        elif dew_point_deficit < 1:
            base_prob = 75
        elif dew_point_deficit < 2:
            base_prob = 50
        elif dew_point_deficit < 3:
            base_prob = 25
        else:
            base_prob = 5
        
        # Коригування за вологістю
        if humidity > 95:
            base_prob += 10
        elif humidity > 90:
            base_prob += 5
        elif humidity < 80:
            base_prob -= 20
        
        # Температурні умови для туману
        if -5 <= temp <= 15:
            base_prob += 5  # Оптимальний діапазон
        
        final_prob = max(0, min(100, base_prob))
        
        # Визначення типу туману (додано крижаний туман)
        if temp < -10:
            fog_type = 'Крижаний туман'
        elif temp < 10:
            fog_type = 'Радіаційний'
        else:
            fog_type = 'Адвективний'
        
        return {
            'probability': round(final_prob, 1),
            'type': fog_type,
            'description': f'{fog_type} туман з ймовірністю {final_prob:.0f}%'
        }
    
    @staticmethod
    def frost_probability(temp: float, humidity: float, time_of_day: int) -> Dict:
        """
        Прогноз ймовірності заморозків.
        """
        # === ВИПРАВЛЕННЯ №3: Розділення Морозу і Заморозку ===
        # Якщо вже мінус - це не ймовірність, це факт.
        if temp <= 0:
            description = "Сильний мороз" if temp < -10 else "Мороз"
            return {
                'probability': 100, 
                'description': description
            }
        # =====================================================

        if temp > 10:
            return {'probability': 0, 'description': 'Заморозки неможливі'}
        
        base_prob = 0
        
        # Базова оцінка за температурою
        if temp < 2:
            base_prob = 60
        elif temp < 5:
            base_prob = 30
        else:
            base_prob = 10
        
        # Коригування за вологістю (висока вологість захищає від заморозків)
        if humidity > 80:
            base_prob -= 10
        elif humidity < 50: # Сухе повітря - більший ризик
            base_prob += 20
        
        # Коригування за часом доби (4-7 ранку - найхолодніший час)
        if 4 <= time_of_day <= 7:
            base_prob += 15
        elif 0 <= time_of_day <= 3 or 8 <= time_of_day <= 9:
            base_prob += 5
        
        final_prob = max(0, min(100, base_prob))
        
        return {
            'probability': round(final_prob, 1),
            'description': f'Ймовірність заморозку {final_prob:.0f}%'
        }



# ============================================================================
# СТАТИСТИЧНЕ ПРОГНОЗУВАННЯ
# ============================================================================

class StatisticalForecast:
    """Статистичні методи прогнозування (Zambretti + Diurnal Cycle + Dynamic Range)"""
    
    @staticmethod
    def diurnal_temperature_model(current_temp: float, hours_ahead: int) -> float:
        """
        Адаптивна синусоїдальна модель.
        Автоматично враховує сезон: влітку сонце гріє сильніше.
        """
        now = datetime.now()
        month = now.month
        
        # Час у десятковому форматі
        hour_now = now.hour + now.minute / 60.0
        target_hour = (hour_now + hours_ahead) % 24
        
        # Автоматичний вибір амплітуди (різниця День-Ніч)
        # Зима: мала амплітуда. Літо: велика.
        if month in [11, 12, 1, 2]: # Зима
            amplitude = 4.0
        elif month in [5, 6, 7, 8]: # Літо
            amplitude = 11.0
        else: # Весна/Осінь
            amplitude = 7.0
            
        # Пік тепла: влітку о 15:00, взимку о 14:00
        peak_hour = 15 if amplitude > 8 else 14
        
        def get_diurnal_factor(h):
            # Період 24 години
            return -math.cos(math.pi * (h - (peak_hour - 10)) / 12) 
            
        factor_now = get_diurnal_factor(hour_now)
        factor_future = get_diurnal_factor(target_hour)
        
        delta_temp = (factor_future - factor_now) * (amplitude / 2)
        
        return current_temp + delta_temp


    @staticmethod
    def temperature_forecast_combined(t_now: float, p_change: float, hours: int) -> Dict:
        """
        Комбінований прогноз: Добовий цикл + Барична тенденція.
        """
        # 1. Добовий хід (Сонце)
        t_diurnal = StatisticalForecast.diurnal_temperature_model(t_now, hours)
        
        # 2. Вплив зміни тиску (Адвекція)
        # Якщо тиск росте -> антициклон -> взимку це сильніше вихолоджування вночі
        baric_correction = 0
        if p_change > 0.5: # Тиск росте
            baric_correction = -0.3 * hours # Стає холодніше
        elif p_change < -0.5: # Тиск падає (хмари)
            baric_correction = 0.2 * hours # Стає тепліше (взимку)
            
        t_final = t_diurnal + baric_correction
        
        # Динамічна похибка
        confidence = 0.8 + abs(p_change) * 0.5
        confidence = max(0.5, min(2.5, confidence))
        
        return {
            'value': round(t_final, 1),
            'min': round(t_final - confidence, 1),
            'max': round(t_final + confidence, 1),
            'confidence': round(confidence, 1)
        }

    @staticmethod
    def linear_extrapolation(data: List[float], hours_ahead: int = 1) -> float:
        """
        Залишаємо для тиску та вологості (вони менше залежать від сонця).
        Для температури використовуйте diurnal_temperature_model!
        """
        if len(data) < 2: return data[-1] if data else 0
        n = min(3, len(data)) # Тренд за останні 3 години
        recent_data = data[-n:]
        X = list(range(n))
        Y = recent_data
        x_mean = sum(X) / n
        y_mean = sum(Y) / n
        numerator = sum((X[i] - x_mean) * (Y[i] - y_mean) for i in range(n))
        denominator = sum((X[i] - x_mean) ** 2 for i in range(n))
        if denominator == 0: return Y[-1]
        b = numerator / denominator
        a = y_mean - b * x_mean
        return a + b * (n - 1 + hours_ahead)

    
    @staticmethod
    def persistence_forecast(current_value: float, inertia: float = 0.95) -> float:
        """Прогноз методом інерції"""
        noise = np.random.normal(0, 0.1)
        return current_value + noise


# ============================================================================
# ОСНОВНА СИСТЕМА ПРОГНОЗУВАННЯ
# ============================================================================

class WeatherForecastSystem:
    """Головна система прогнозування погоди"""
    
    def __init__(self):
        self.meteo_calc = MeteoCalculations()
        self.synoptic = SynopticAnalysis()
        self.precip_forecast = PrecipitationForecast()
        self.hazard_forecast = HazardousForecast()
        self.stat_forecast = StatisticalForecast()
        
        self.weather_history = []
        
        logging.info("=" * 70)
        logging.info("ПРОФЕСІЙНА СИСТЕМА ПРОГНОЗУВАННЯ ПОГОДИ - ІНІЦІАЛІЗОВАНА")
        logging.info("=" * 70)
    
    def load_weather_data(self, filename: str = "weather_log.json") -> bool:
        """Завантаження даних + EMA Фільтрація + MSLP Розрахунок"""
        try:
            with open(filename, 'r') as f:
                raw_data = json.load(f)
            
            # === ЦИФРОВИЙ ФІЛЬТР (EMA) ===
            alpha = PhysicalConstants.EMA_ALPHA
            # Ініціалізація першим значенням
            if raw_data:
                ema_press = raw_data[0]['press'] 
            
            for entry in raw_data:
                # 1. Згладжування тиску (фільтр шуму)
                ema_press = (alpha * entry['press']) + ((1 - alpha) * ema_press)
                entry['press_smooth'] = round(ema_press, 2)
                
                # 2. Розрахунок MSLP (Тиск на рівні моря)
                # Використовуємо згладжений тиск!
                entry['press_mslp'] = round(
                    self.meteo_calc.adjust_pressure_to_sea_level(
                        entry['press_smooth'], entry['temp']
                    ), 1
                )
            
            self.weather_history = raw_data
            logging.info(f"Завантажено та оброблено {len(self.weather_history)} записів")
            return True
        except Exception as e:
            logging.error(f"Помилка завантаження: {e}")
            return False
    
    def get_current_conditions(self) -> Optional[Dict]:
        """Отримання поточних погодних умов"""
        if not self.weather_history:
            return None
        
        current = self.weather_history[-1]
        
        # Метеорологічні розрахунки
        dew_point = self.meteo_calc.dew_point(current['temp'], current['hum'])
        dew_deficit = current['temp'] - dew_point
        vapor_pressure = self.meteo_calc.actual_vapor_pressure(current['temp'], current['hum'])
        sat_pressure = self.meteo_calc.saturation_pressure(current['temp'])
        humidity_deficit = self.meteo_calc.humidity_deficit(current['temp'], current['hum'])
        condensation_level = self.meteo_calc.condensation_level(current['temp'], current['hum'])
        baric_step = self.meteo_calc.baric_step(current['temp'])
        air_density = self.meteo_calc.air_density(current['press'], current['temp'])
        
        return {
            'timestamp': current['ts'],
            'temperature': current['temp'],
            'pressure': current['press'],
            'humidity': current['hum'],
            'dew_point': round(dew_point, 1),
            'dew_point_deficit': round(dew_deficit, 1),
            'vapor_pressure': round(vapor_pressure, 2),
            'saturation_pressure': round(sat_pressure, 2),
            'humidity_deficit': round(humidity_deficit, 2),
            'condensation_level': round(condensation_level, 0),
            'baric_step': round(baric_step, 2),
            'air_density': round(air_density, 3)
        }
    
    def analyze_trends(self) -> Dict:
        """Аналіз трендів погоди"""
        if len(self.weather_history) < 4:
            return {'error': 'Недостатньо даних для аналізу трендів'}
        
        # Витягуємо часові ряди
        pressures = [entry['press'] for entry in self.weather_history]
        temps = [entry['temp'] for entry in self.weather_history]
        humidities = [entry['hum'] for entry in self.weather_history]
        
        # Баричний аналіз
        pressure_tendency = self.synoptic.pressure_tendency_analysis(pressures)
        
        # Виявлення фронтів
        front_info = self.synoptic.front_detection(pressure_tendency, temps, humidities)
        
        # Класифікація повітряної маси
        current = self.weather_history[-1]
        air_mass = self.synoptic.classify_air_mass(
            current['temp'], 
            current['hum'], 
            current['press']
        )
        
        return {
            'pressure_tendency': pressure_tendency,
            'front_detection': front_info,
            'air_mass': air_mass
        }
    
        
    
    def generate_nowcast(self) -> Dict:
        """Генерація Nowcast з використанням MSLP та Zambretti"""
        current = self.get_current_conditions()
        if not current: return {'error': 'No data'}
        
        # Отримуємо останні оброблені дані з історії (де вже є MSLP)
        last_history_entry = self.weather_history[-1]
        
        # Додаємо розрахований MSLP до поточних умов для звіту
        current['press_mslp'] = last_history_entry.get('press_mslp', current['pressure'])
        
        # === АНАЛІЗ ТРЕНДІВ ЗА MSLP (А НЕ ПО СИРОМУ ТИСКУ) ===
        if len(self.weather_history) >= 4:
            p_now = current['press_mslp']
            p_old = self.weather_history[-4].get('press_mslp', self.weather_history[-4]['press'])
            delta_3h = p_now - p_old
        else:
            delta_3h = 0
            
        # Визначаємо тенденцію вручну для Zambretti та розрахунків
        if delta_3h < -1.5: trend_txt = 'falling'
        elif delta_3h > 1.5: trend_txt = 'rising'
        else: trend_txt = 'steady'
        
        # === ПРОГНОЗ ZAMBRETTI ===
        zambretti = ZambrettiForecaster.get_forecast(
            current['press_mslp'], 
            trend_txt, 
            datetime.now().month
        )
        
        # Отримуємо загальні тренди
        trends = self.analyze_trends()
        
        # Перезаписуємо тенденцію тиску на основі MSLP (це точніше для фізики)
        trends['pressure_tendency']['delta_3h'] = round(delta_3h, 1)
        trends['pressure_tendency']['tendency'] = trend_txt

        # Розрахунок стабільності
        stability = self.meteo_calc.stability_index(current['temperature'], current['humidity'])
        
        # === РОЗРАХУНОК ЯВИЩ І НЕБЕЗПЕК ===
        
        # 1. Опади (використовуємо стабільність повітряної маси з аналізу трендів)
        air_stability = trends['air_mass']['stability'] if 'air_mass' in trends else 'neutral'
        
        precip = self.precip_forecast.calculate_precipitation_probability(
            current['humidity'], 
            current['dew_point_deficit'], 
            trend_txt, 
            current['condensation_level'], 
            air_stability
        )
        
        # 2. Гроза (використовуємо індекс Шоуолтера)
        thunder = self.hazard_forecast.thunderstorm_probability(
            current['temperature'], 
            current['humidity'], 
            trend_txt, 
            stability['showalter_index']
        )
        
        # 3. Туман
        fog = self.hazard_forecast.fog_probability(
            current['temperature'], 
            current['humidity'], 
            current['dew_point_deficit']
        )
        
        # 4. Заморозок
        frost = self.hazard_forecast.frost_probability(
            current['temperature'], 
            current['humidity'], 
            datetime.now().hour
        )

        # === ГЕНЕРАЦІЯ РОЗУМНОГО РЕЗЮМЕ ===
        # Передаємо всі дані, включаючи zambretti, для вирішення конфліктів
        summary_text = self._generate_weather_summary(
            current, trends, precip, thunder, fog, frost, zambretti
        )

        # Формування фінального словника
        nowcast = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_conditions': current,
            'trends': trends,
            'zambretti_forecast': zambretti,
            'stability_indices': stability,
            'precipitation': precip,
            'thunderstorm': thunder,
            'fog': fog,
            'frost': frost,
            'weather_summary': summary_text
        }
        return nowcast


    def generate_forecast(self, hours_ahead: int = 3) -> Dict:
        """
        Прогноз на найближчі години.
        Використовує синусоїдальну модель добового ходу для температури
        та лінійну екстраполяцію для інших параметрів.
        """
        if len(self.weather_history) < 6:
            return {'error': 'Недостатньо даних для прогнозу'}
        
        # Отримуємо поточні дані
        curr = self.weather_history[-1]
        
        # Розрахунок зміни тиску (MSLP) для корекції температури
        # Якщо є MSLP в історії (новий код), використовуємо його, інакше звичайний тиск
        if 'press_mslp' in curr:
            p_now = curr['press_mslp']
            # Беремо дані 3 години назад або поточні, якщо історії мало
            p_old = self.weather_history[-4]['press_mslp'] if len(self.weather_history) >= 4 else p_now
        else:
            p_now = curr['press']
            p_old = self.weather_history[-4]['press'] if len(self.weather_history) >= 4 else p_now
            
        p_change = p_now - p_old

        # Дані для екстраполяції тиску та вологості
        press_raw = [x['press'] for x in self.weather_history]
        hum_raw = [x['hum'] for x in self.weather_history]
        
        forecasts = []
        for h in range(1, hours_ahead + 1):
            # 1. Прогноз температури (Нова модель: Сонце + Адвекція)
            t_cast = self.stat_forecast.temperature_forecast_combined(
                curr['temp'], p_change, h
            )
            
            # 2. Екстраполяція тиску та вологості (Лінійна, бо менше залежать від сонця)
            p_next = self.stat_forecast.linear_extrapolation(press_raw, h)
            h_next = self.stat_forecast.linear_extrapolation(hum_raw, h)
            
            # Обмеження вологості (0-100%)
            h_next = max(0, min(100, h_next))
            
            # 3. Додаткові розрахунки для майбутнього стану (для опадів/туману)
            dew_point_fut = self.meteo_calc.dew_point(t_cast['value'], h_next)
            dew_deficit_fut = t_cast['value'] - dew_point_fut
            cond_level_fut = self.meteo_calc.condensation_level(t_cast['value'], h_next)
            
            # Визначаємо тренд тиску для майбутнього
            if p_next < press_raw[-1] - 1: press_trend = 'falling'
            elif p_next > press_raw[-1] + 1: press_trend = 'rising'
            else: press_trend = 'steady'
            
            # Прогноз явищ на майбутнє (використовуємо ті ж методи, що і для nowcast)
            precip_prob = self.precip_forecast.calculate_precipitation_probability(
                h_next, 
                dew_deficit_fut, 
                press_trend, 
                cond_level_fut, 
                'neutral'
            )
            
            fog_prob = self.hazard_forecast.fog_probability(
                t_cast['value'], h_next, dew_deficit_fut
            )

            # Формуємо об'єкт прогнозу
            forecasts.append({
                'hours_ahead': h,
                'timestamp': (datetime.now() + timedelta(hours=h)).strftime('%H:%M'),
                'temperature': t_cast, # Вже містить min/max/confidence з temperature_forecast_combined
                'pressure': {
                    'value': round(p_next, 1), 
                    'trend': press_trend
                },
                'humidity': {
                    'value': round(h_next, 1)
                },
                'dew_point': round(dew_point_fut, 1),
                'precipitation_probability': precip_prob['probability'],
                'fog_probability': fog_prob['probability']
            })
            
        return {
            'forecast_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'forecast_hours': hours_ahead,
            'forecasts': forecasts,
            'confidence': 'High' # Висока довіра завдяки врахуванню добового ходу
        }

    def _generate_weather_summary(self, current: Dict, trends: Dict, 
                                  precipitation: Dict, thunderstorm: Dict,
                                  fog: Dict, frost: Dict, zambretti_forecast: Dict) -> str:
        """Генерація текстового резюме погоди з пріоритетом датчиків"""
        summary_parts = []
        
        # Температура
        temp = current['temperature']
        if temp < -10: summary_parts.append("Сильний мороз")
        elif temp < 0: summary_parts.append("Мороз")
        elif temp < 10: summary_parts.append("Прохолодно")
        elif temp < 20: summary_parts.append("Помірно тепло")
        elif temp < 30: summary_parts.append("Тепло")
        else: summary_parts.append("Спека")
        
        # Тиск
        press_desc = trends['pressure_tendency']['description']
        summary_parts.append(f"тиск {press_desc.lower()}")
        
        # Вологість
        hum = current['humidity']
        if hum > 85: summary_parts.append("дуже волого")
        elif hum > 70: summary_parts.append("волого")
        elif hum < 40: summary_parts.append("суха погода")
        
        # Опади
        if precipitation['probability'] > 70:
            summary_parts.append(f"{precipitation['description'].lower()} ({precipitation['probability']:.0f}%)")
        elif precipitation['probability'] > 40:
            summary_parts.append(f"можливі {precipitation['type'].lower()} опади ({precipitation['probability']:.0f}%)")
        
        # Гроза
        if thunderstorm['probability'] > 50:
            summary_parts.append(f"{thunderstorm['severity'].lower()} ({thunderstorm['probability']:.0f}%)")
        
        # Туман
        if fog['probability'] > 50:
            summary_parts.append(f"{fog['type'].lower()} туман ({fog['probability']:.0f}%)")
        
        # Заморозок
        if frost['probability'] > 50:
            summary_parts.append(f"заморозок ({frost['probability']:.0f}%)")
        
        # Фронти
        if trends['front_detection']['probability'] > 60:
            summary_parts.append(f"{trends['front_detection']['description'].lower()}")
        
        # === ЛОГІКА ВИРІШЕННЯ КОНФЛІКТІВ ===
        # Перевіряємо, чи Zambretti каже "все добре"
        z_text = zambretti_forecast['forecast_text'].lower()
        z_is_optimistic = any(x in z_text for x in ['ясно', 'гарна', 'сонячно', 'без змін', 'покращення'])
        
        # Перевіряємо, чи датчики кричать про негоду
        bad_weather = precipitation['probability'] > 60 or fog['probability'] > 60
        
        # Якщо конфлікт (Zambretti каже сонце, а датчики бачать дощ): віримо датчикам!
        if z_is_optimistic and bad_weather:
            warnings = []
            if precipitation['probability'] > 60: warnings.append(precipitation['description'])
            if fog['probability'] > 60: warnings.append(fog['description'])
            
            warning_str = ", ".join(warnings).capitalize()
            base_summary = ". ".join(summary_parts)
            # Повертаємо попередження замість оптимізму
            return f"Увага! {warning_str}. (Тиск високий, але вологість критична). {base_summary}."
        
        # Якщо конфлікту немає, додаємо прогноз Zambretti на початок
        return f"Zambretti: {zambretti_forecast['forecast_text']}. " + ". ".join(summary_parts) + "."


    
    def print_detailed_report(self, nowcast: Dict, forecast: Dict):
        """Виведення детального звіту"""
        print("\n" + "=" * 80)
        print("ПРОФЕСІЙНИЙ МЕТЕОРОЛОГІЧНИЙ ПРОГНОЗ")
        print("=" * 80)
        
        # Поточні умови
        print("\n📊 ПОТОЧНІ МЕТЕОРОЛОГІЧНІ УМОВИ:")
        print("-" * 80)
        current = nowcast['current_conditions']
        print(f"Час спостереження: {nowcast['timestamp']}")
        print(f"Температура повітря: {current['temperature']:.1f}°C")
        print(f"Атмосферний тиск: {current['pressure']:.1f} гПа")
        print(f"Відносна вологість: {current['humidity']:.1f}%")
        print(f"Точка роси: {current['dew_point']:.1f}°C")
        print(f"Дефіцит точки роси: {current['dew_point_deficit']:.1f}°C")
        print(f"Рівень конденсації: {current['condensation_level']:.0f} м")
        print(f"Баричний ступінь: {current['baric_step']:.2f} м/гПа")
        print(f"Щільність повітря: {current['air_density']:.3f} кг/м³")
        
        # Синоптичний аналіз
        print("\n🌍 СИНОПТИЧНИЙ АНАЛІЗ:")
        print("-" * 80)
        trends = nowcast['trends']
        pt = trends['pressure_tendency']
        print(f"Баричний тренд: {pt['description']} ({pt['delta_3h']:+.1f} гПа за 3 год)")
        print(f"Зміна за годину: {pt['delta_per_hour']:+.2f} гПа/год")
        print(f"Довгостроковий тренд: {pt['long_term_trend']}")
        
        air_mass = trends['air_mass']
        print(f"Повітряна маса: {air_mass['description']} ({air_mass['stability']})")
        
        front = trends['front_detection']
        if front['probability'] > 30:
            print(f"Фронт: {front['description']} (ймовірність {front['probability']:.0f}%)")
            print(f"  Характеристики: {front['characteristics']}")
        
        # Індекси нестійкості
        print("\n⚡ ІНДЕКСИ НЕСТІЙКОСТІ АТМОСФЕРИ:")
        print("-" * 80)
        stability = nowcast['stability_indices']
        print(f"Індекс Шоуолтера (SI): {stability['showalter_index']:.1f}")
        print(f"Lifted Index (LI): {stability['lifted_index']:.1f}")
        
        # Прогноз явищ
        print("\n☔ ПРОГНОЗ ПОГОДНИХ ЯВИЩ (Nowcast):")
        print("-" * 80)
        
        precip = nowcast['precipitation']
        print(f"ОПАДИ: {precip['probability']:.1f}%")
        if precip['probability'] > 10:
            print(f"  Тип: {precip['description']}")
            if 'phase' in precip:
                print(f"  Фаза: {precip['phase']}")
        
        thunder = nowcast['thunderstorm']
        print(f"ГРОЗА: {thunder['probability']:.1f}%")
        if thunder['probability'] > 20:
            print(f"  {thunder['description']}")
        
        fog_now = nowcast['fog']
        print(f"ТУМАН: {fog_now['probability']:.1f}%")
        if fog_now['probability'] > 20:
            print(f"  {fog_now['description']}")
        
        frost_now = nowcast['frost']
        print(f"ЗАМОРОЗОК: {frost_now['probability']:.1f}%")
        if frost_now['probability'] > 20:
            print(f"  {frost_now['description']}")
        
        # Резюме погоди
        print("\n📝 РЕЗЮМЕ:")
        print("-" * 80)
        print(nowcast['weather_summary'])
        
        # Прогноз на години вперед
        if 'forecasts' in forecast:
            print("\n🔮 ПРОГНОЗ НА НАЙБЛИЖЧІ ГОДИНИ:")
            print("-" * 80)
            print(f"Достовірність прогнозу: {forecast['confidence']}")
            print()
            
            for f in forecast['forecasts']:
                print(f"Через {f['hours_ahead']} год ({f['timestamp']}):")
                temp = f['temperature']
                print(f"  Температура: {temp['value']:.1f}°C (діапазон: {temp['min']:.1f}°C...{temp['max']:.1f}°C)")
                print(f"  Тиск: {f['pressure']['value']:.1f} гПа (тренд: {f['pressure']['trend']})")
                print(f"  Вологість: {f['humidity']['value']:.1f}%")
                print(f"  Точка роси: {f['dew_point']:.1f}°C")
                print(f"  Опади: {f['precipitation_probability']:.1f}%")
                print(f"  Туман: {f['fog_probability']:.1f}%")
                print()
        
        print("=" * 80)


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def main():
    """Головна функція для запуску системи прогнозування"""
    
    # Ініціалізація системи
    forecast_system = WeatherForecastSystem()
    
    # Завантаження даних
    if not forecast_system.load_weather_data("weather_log.json"):
        logging.error("Не вдалося завантажити дані. Переконайтеся, що файл weather_log.json існує.")
        logging.info("Спочатку запустіть gen.py для генерації даних.")
        return
    
    # Генерація nowcast (прогноз на зараз)
    logging.info("Генерація прогнозу на поточний момент (Nowcast)...")
    nowcast = forecast_system.generate_nowcast()
    
    # Генерація прогнозу на 3 години
    logging.info("Генерація прогнозу на найближчі 3 години...")
    forecast_3h = forecast_system.generate_forecast(hours_ahead=3)
    
    # Виведення детального звіту
    forecast_system.print_detailed_report(nowcast, forecast_3h)
    
    # Збереження прогнозу у файл
    output_data = {
        'nowcast': nowcast,
        'forecast_3h': forecast_3h
    }
    
    with open('weather_forecast_output.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)
    
    logging.info("Прогноз збережено у файл weather_forecast_output.json")
    
    # Додатково: прогноз у відсотках (summary)
    print("\n" + "=" * 80)
    print("ШВИДКИЙ ПРОГНОЗ У ВІДСОТКАХ")
    print("=" * 80)
    
    current = nowcast['current_conditions']
    print(f"\n🌡️  Температура: {current['temperature']:.1f}°C")
    print(f"🌊 Вологість: {current['humidity']:.0f}%")
    print(f"🔽 Тиск: {current['pressure']:.1f} гПа")
    print()
    print("Ймовірності явищ:")
    print(f"  ☔ Опади: {nowcast['precipitation']['probability']:.0f}%")
    print(f"  ⚡ Гроза: {nowcast['thunderstorm']['probability']:.0f}%")
    print(f"  🌫️  Туман: {nowcast['fog']['probability']:.0f}%")
    print(f"  ❄️  Заморозок: {nowcast['frost']['probability']:.0f}%")
    
    if 'front_detection' in nowcast['trends']:
        front = nowcast['trends']['front_detection']
        if front['probability'] > 30:
            print(f"  🌪️  Атмосферний фронт: {front['probability']:.0f}%")
    
    print("=" * 80)


if __name__ == "__main__":
    main()

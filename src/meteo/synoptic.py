"""
Synoptic Analysis and Statistical Forecasting
==============================================

Professional meteorological analysis and forecasting algorithms:
- SynopticAnalysis: Pressure tendency, front detection, air mass classification
- ZambrettiForecaster: Classic Zambretti forecasting algorithm
- PrecipitationForecast: Precipitation probability and type prediction
- HazardousForecast: Thunderstorm, fog, and frost forecasting
- StatisticalForecast: Statistical methods with diurnal temperature modeling

Compatible with both CPython and MicroPython (no numpy dependency).

Author: Professional Meteorological System
Date: 2026
"""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from ..core.constants import PhysicalConstants
from ..core.calculations import mean


def log(message: str, level: str = "INFO") -> None:
    """Simple logging function for MicroPython compatibility"""
    print(f"[{level}] {message}")


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
        """
        Прогноз методом інерції.
        Note: Removed numpy dependency - simple implementation without random noise.
        """
        # Simple persistence without noise for MicroPython compatibility
        return current_value

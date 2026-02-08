"""
Weather Forecast System Module

Comprehensive weather forecasting system with nowcast and short-term predictions.
Integrates barometric analysis, synoptic methods, and statistical models for
professional-grade meteorological forecasts.

Compatible with both CPython and MicroPython.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

# Import from modular structure
from ..core.constants import PhysicalConstants
from ..core.calculations import mean, std_dev, exponential_smoothing
from .barometric import (
    adjust_pressure_to_sea_level, baric_step, air_density, 
    stability_index, celsius_to_kelvin
)
from .psychrometry import (
    dew_point, actual_vapor_pressure, saturation_pressure, 
    humidity_deficit, condensation_level
)
from .synoptic import (
    SynopticAnalysis, ZambrettiForecaster, PrecipitationForecast, 
    HazardousForecast, StatisticalForecast
)


def log(message, level="INFO"):
    """Simple logging function compatible with CPython and MicroPython"""
    try:
        print(f"[{level}] {message}")
    except:
        pass


class WeatherForecastSystem:
    """Головна система прогнозування погоди"""
    
    def __init__(self):
        self.synoptic = SynopticAnalysis()
        self.precip_forecast = PrecipitationForecast()
        self.hazard_forecast = HazardousForecast()
        self.stat_forecast = StatisticalForecast()
        
        self.weather_history = []
        
        log("=" * 70)
        log("ПРОФЕСІЙНА СИСТЕМА ПРОГНОЗУВАННЯ ПОГОДИ - ІНІЦІАЛІЗОВАНА")
        log("=" * 70)
    
    def load_weather_data(self, filename: str = "weather_log.json") -> bool:
        """Завантаження даних + EMA Фільтрація + MSLP Розрахунок"""
        try:
            with open(filename, 'r') as f:
                # MicroPython and CPython compatible JSON loading
                try:
                    import json
                    raw_data = json.load(f)
                except:
                    import ujson
                    raw_data = ujson.load(f)
            
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
                    adjust_pressure_to_sea_level(
                        entry['press_smooth'], entry['temp']
                    ), 1
                )
            
            self.weather_history = raw_data
            log(f"Завантажено та оброблено {len(self.weather_history)} записів")
            return True
        except Exception as e:
            log(f"Помилка завантаження: {e}", "ERROR")
            return False
    
    def get_current_conditions(self) -> Optional[Dict]:
        """Отримання поточних погодних умов"""
        if not self.weather_history:
            return None
        
        current = self.weather_history[-1]
        
        # Метеорологічні розрахунки
        dew_pt = dew_point(current['temp'], current['hum'])
        dew_deficit = current['temp'] - dew_pt
        vapor_pressure = actual_vapor_pressure(current['temp'], current['hum'])
        sat_pressure = saturation_pressure(current['temp'])
        hum_deficit = humidity_deficit(current['temp'], current['hum'])
        cond_level = condensation_level(current['temp'], current['hum'])
        baric_st = baric_step(current['temp'])
        air_dens = air_density(current['press'], current['temp'])
        
        return {
            'timestamp': current['ts'],
            'temperature': current['temp'],
            'pressure': current['press'],
            'humidity': current['hum'],
            'dew_point': round(dew_pt, 1),
            'dew_point_deficit': round(dew_deficit, 1),
            'vapor_pressure': round(vapor_pressure, 2),
            'saturation_pressure': round(sat_pressure, 2),
            'humidity_deficit': round(hum_deficit, 2),
            'condensation_level': round(cond_level, 0),
            'baric_step': round(baric_st, 2),
            'air_density': round(air_dens, 3)
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
        stability = stability_index(current['temperature'], current['humidity'])
        
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
            dew_point_fut = dew_point(t_cast['value'], h_next)
            dew_deficit_fut = t_cast['value'] - dew_point_fut
            cond_level_fut = condensation_level(t_cast['value'], h_next)
            
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

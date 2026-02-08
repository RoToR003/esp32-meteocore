import requests
import json
from datetime import datetime

def generate_vinnytsia_weather_log():
    # Координати Вінниці
    LAT = 49.243586
    LON = 28.490054
    
    # URL для запиту до Open-Meteo (безкоштовний API, не потребує ключа)
    # Запитуємо температуру, вологість та тиск
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure",
        "timezone": "auto",  # Автоматичне визначення часового поясу України
        "forecast_days": 2   # Беремо із запасом, щоб точно мати 24 години
    }

    try:
        print(f"Отримання даних для міста Вінниця...")
        response = requests.get(url, params=params)
        response.raise_for_status() # Перевірка на помилки
        data = response.json()

        hourly_data = data.get("hourly", {})
        
        # Списки даних від API
        temps = hourly_data.get("temperature_2m", [])
        hums = hourly_data.get("relative_humidity_2m", [])
        pressures = hourly_data.get("surface_pressure", [])
        
        output_log = []

        # Генеруємо список для наступних 24 годин
        # ts: 0..23 (індекс години, як у вашому прикладі)
        for i in range(24):
            # Перевірка, чи достатньо даних
            if i < len(temps):
                entry = {
                    "ts": i,
                    "press": pressures[i], # Тиск у hPa (аналогічно мбар)
                    "temp": temps[i],      # Температура у °C
                    "hum": hums[i]         # Вологість у %
                }
                output_log.append(entry)

        # Ім'я вихідного файлу
        filename = 'weather_log.json'
        
        # Запис у файл
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_log, f, indent=4)
            
        print(f"Успішно! Файл '{filename}' згенеровано з актуальними даними.")
        
        # Для перевірки виведемо перші 3 записи
        print("Перші 3 записи:")
        print(json.dumps(output_log[:3], indent=4))

    except Exception as e:
        print(f"Виникла помилка: {e}")

if __name__ == "__main__":
    generate_vinnytsia_weather_log()

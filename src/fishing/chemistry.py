"""
Water chemistry calculations for fishing forecasts.

This module provides hydrochemical calculations including oxygen saturation,
pH effects, temperature forecasting, and light penetration. All formulas are
MicroPython-compatible and based on scientific research.
"""

import math
from typing import Dict
from ..core.constants import PhysicalConstants


def log(message: str) -> None:
    """Simple logging function for MicroPython compatibility."""
    print(f"[Chemistry] {message}")


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

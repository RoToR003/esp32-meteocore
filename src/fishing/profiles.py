"""
Fish Species Profiles Module
============================

Defines fish species characteristics and behavioral profiles for bite forecasting.
Contains species-specific parameters including:
- Temperature preferences and tolerances
- Pressure sensitivity
- Dissolved oxygen requirements
- Light activity patterns
- Feeding time peaks
- Seasonal patterns

All profiles are based on ichthyological research and are optimized for MicroPython.

Author: Scientific Ichthyology Research System
"""

from enum import Enum
from typing import Dict, List, Optional
from ..core.constants import PhysicalConstants


def log(message, level="INFO"):
    """Simple logging function compatible with MicroPython"""
    try:
        print(f"[{level}] {message}")
    except:
        pass


class FishSpecies(Enum):
    """Fish species enumeration"""
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
    """Light activity type for fish species"""
    DIURNAL = "денний"      # perch, roach
    CREPUSCULAR = "сутінковий"  # pike, bream, carp
    NOCTURNAL = "нічний"    # zander, catfish


class FishProfile:
    """Complete fish species profile with all characteristics"""
    
    def __init__(self, species: FishSpecies):
        self.species = species
        self._load_profile()
    
    def _load_profile(self):
        """Load species characteristics from research data"""
        
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
                'season_peak': 90,  # day of year (end of March)
                'season_peak2': 270,  # autumn feeding
                'season_amplitude': 0.6,
                'spawn_temp': 6.0,
                'spawn_month': 3  # March-April
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
            log(f"Unknown species: {self.species}", "ERROR")
            raise ValueError(f"Unknown species: {self.species}")

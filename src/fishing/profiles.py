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
    
    # LOCAL SPECIES OF SOUTHERN BUG
    SOUTHBUG_PIKE = "Щука (Південний Буг)"  # Pike of Southern Bug
    SOUTHBUG_ZANDER = "Судак (Південний Буг)"  # Zander of Southern Bug
    SOUTHBUG_BREAM = "Лящ (Південний Буг)"  # Bream of Southern Bug
    SOUTHBUG_ROACH = "Плітка (Південний Буг)"  # Roach of Southern Bug
    SOUTHBUG_CHUB = "Головень (Південний Буг)"  # Chub of Southern Bug
    SOUTHBUG_CATFISH = "Сом (Південний Буг)"  # Catfish of Southern Bug


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
            
            # =====================================================================
            # SOUTHERN BUG RIVER SPECIES (VINNYTSIA)
            # =====================================================================
            # Calibrated for Southern Bug (center of Vinnytsia)
            # Data from fishermen observations + UkrNDIVG scientific research
            
            FishSpecies.SOUTHBUG_PIKE: {
                'name_ua': 'Щука (Південний Буг)',
                'name_lat': 'Esox lucius (Bug River)',
                'type': 'хижак',
                
                # TEMPERATURE (calibrated for river pike)
                'T_opt': 16.0,  # Optimum for river pike (15-17°C)
                'T_min': 2.0,
                'T_max': 24.0,
                'sigma_T': 4.5,  # Wide tolerance
                
                # PRESSURE (pike is very sensitive to pressure!)
                'p_opt': 755.0,  # 755 mmHg = 1006.6 hPa at 305m elevation
                'sigma_p': 4.0,  # Narrow tolerance (sensitive to changes)
                'pressure_sensitivity': 0.5,
                
                # OXYGEN (predator - needs a lot of O₂)
                'DO_min': 5.0,  # mg/L
                'DO_opt': 9.0,  # mg/L
                
                # LIGHT (crepuscular predator, but also active during day)
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 1500.0,  # lux (twilight)
                'light_sigma': 1.5,
                'light_critical': 50000,  # above this - hides
                
                # WIND (moderate good, strong bad)
                'wind_opt': 3.0,  # m/s
                
                # SEASONALITY (spring + autumn)
                'season_peak': 120,  # end of April (spring feeding)
                'season_peak2': 280,  # beginning of October (autumn feeding)
                'season_amplitude': 0.4,
                'spawn_temp': 6.0,
                'spawn_month': 3,
                
                # CIRCADIAN RHYTHM (morning + evening)
                'time_peak1': 6.0,  # 6:00 AM
                'time_peak2': 19.0,  # 7:00 PM
                
                # MOON (weak influence)
                'moon_amplitude': 0.15,
                
                # SPECIFICS FOR BUG
                'river_section': 'middle',  # middle flow
                'depth_preference': (1.5, 3.5),  # meters (holes, edges)
                'current_preference': 'slow',  # still water
                'pollution_tolerance': 0.6  # poorly tolerates pollution
            },
            
            FishSpecies.SOUTHBUG_ZANDER: {
                'name_ua': 'Судак (Південний Буг)',
                'name_lat': 'Sander lucioperca (Bug River)',
                'type': 'хижак',
                
                'T_opt': 18.0,  # Optimum 17-19°C
                'T_min': 6.0,
                'T_max': 26.0,
                'sigma_T': 3.5,
                
                'p_opt': 755.0,
                'sigma_p': 5.0,  # Less sensitive to pressure than pike
                'pressure_sensitivity': 0.5,
                
                # CRITICALLY IMPORTANT: zander needs A LOT of oxygen!
                'DO_min': 6.5,  # mg/L (higher than pike!)
                'DO_opt': 10.0,  # mg/L
                
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 500.0,  # lux (darker twilight than pike)
                'light_sigma': 1.2,
                'light_critical': 30000,
                
                'wind_opt': 2.5,
                
                'season_peak': 150,  # May-June (spawning)
                'season_amplitude': 0.35,
                'spawn_temp': 13.5,
                'spawn_month': 5,
                
                'time_peak1': 5.0,  # early dawn
                'time_peak2': 21.0,  # late evening
                
                'moon_amplitude': 0.2,  # slightly more influence than pike
                
                # SPECIFICS
                'river_section': 'middle',
                'depth_preference': (2.0, 4.5),  # deeper places
                'current_preference': 'moderate',  # moderate current
                'pollution_tolerance': 0.4  # very sensitive to pollution!
            },
            
            FishSpecies.SOUTHBUG_BREAM: {
                'name_ua': 'Лящ (Південний Буг)',
                'name_lat': 'Abramis brama (Bug River)',
                'type': 'мирний',
                
                'T_opt': 20.0,  # Heat-loving
                'T_min': 8.0,
                'T_max': 28.0,
                'sigma_T': 5.0,
                
                'p_opt': 755.0,
                'sigma_p': 6.0,  # Tolerant to pressure
                'pressure_sensitivity': 0.8,
                
                'DO_min': 4.0,  # mg/L
                'DO_opt': 7.0,  # mg/L
                
                'light_type': LightType.DIURNAL,  # Diurnal species
                'light_opt': 10000.0,  # lux
                
                'wind_opt': 4.0,  # likes waves
                
                'season_peak': 165,  # June (after spawning)
                'season_amplitude': 0.3,
                'spawn_temp': 14.0,
                'spawn_month': 5,
                
                'time_peak1': 10.0,  # 10:00 AM
                'time_peak2': 16.0,  # 4:00 PM
                
                'moon_amplitude': 0.25,
                
                'river_section': 'middle',
                'depth_preference': (2.5, 4.0),  # deep holes
                'current_preference': 'slow',
                'pollution_tolerance': 0.8  # tolerant to pollution
            },
            
            FishSpecies.SOUTHBUG_ROACH: {
                'name_ua': 'Плітка (Південний Буг)',
                'name_lat': 'Rutilus rutilus (Bug River)',
                'type': 'мирний',
                
                'T_opt': 16.0,  # Moderate temperature preference
                'T_min': 2.0,
                'T_max': 25.0,
                'sigma_T': 5.0,
                
                'p_opt': 752.0,
                'sigma_p': 12.0,
                'pressure_sensitivity': 0.35,
                
                'DO_min': 4.0,  # mg/L
                'DO_opt': 7.0,  # mg/L
                
                'light_type': LightType.DIURNAL,
                'light_opt': 6000.0,
                
                'wind_opt': 4.0,
                
                'season_peak': 90,  # Early spring
                'season_amplitude': 0.4,
                'spawn_temp': 12.0,
                'spawn_month': 4,
                
                'time_peak1': 10.0,
                'time_peak2': None,
                
                'moon_amplitude': 0.30,
                
                'river_section': 'middle',
                'depth_preference': (0.5, 2.5),  # shallower waters
                'current_preference': 'moderate',
                'pollution_tolerance': 0.7
            },
            
            FishSpecies.SOUTHBUG_CHUB: {
                'name_ua': 'Головень (Південний Буг)',
                'name_lat': 'Squalius cephalus (Bug River)',
                'type': 'мирний',
                
                'T_opt': 18.0,
                'T_min': 4.0,
                'T_max': 26.0,
                'sigma_T': 4.5,
                
                'p_opt': 755.0,
                'sigma_p': 10.0,
                'pressure_sensitivity': 0.4,
                
                'DO_min': 6.0,  # mg/L (needs clean water)
                'DO_opt': 9.0,  # mg/L
                
                'light_type': LightType.CREPUSCULAR,
                'light_opt': 2000.0,
                
                'wind_opt': 3.5,
                
                'season_peak': 135,  # May
                'season_amplitude': 0.4,
                'spawn_temp': 15.0,
                'spawn_month': 5,
                
                'time_peak1': 7.0,
                'time_peak2': 18.0,
                
                'moon_amplitude': 0.20,
                
                'river_section': 'middle',
                'depth_preference': (1.0, 3.0),
                'current_preference': 'moderate',  # likes current
                'pollution_tolerance': 0.5  # sensitive to pollution
            },
            
            FishSpecies.SOUTHBUG_CATFISH: {
                'name_ua': 'Сом (Південний Буг)',
                'name_lat': 'Silurus glanis (Bug River)',
                'type': 'хижак',
                
                'T_opt': 23.0,  # Very heat-loving
                'T_min': 10.0,
                'T_max': 30.0,
                'sigma_T': 5.0,
                
                'p_opt': 750.0,
                'sigma_p': 10.0,
                'pressure_sensitivity': 0.5,
                
                'DO_min': 3.0,  # mg/L (can tolerate low oxygen)
                'DO_opt': 6.0,  # mg/L
                
                'light_type': LightType.NOCTURNAL,
                'light_opt': 10.0,
                'light_critical': 100.0,
                
                'wind_opt': 3.0,
                
                'season_peak': 180,  # Summer peak
                'season_amplitude': 0.7,
                'spawn_temp': 20.0,
                'spawn_month': 6,
                
                'time_peak1': 22.0,  # 10:00 PM
                'time_peak2': 4.0,  # 4:00 AM
                
                'moon_amplitude': 0.75,  # strong moon influence
                
                'river_section': 'middle',
                'depth_preference': (2.0, 4.5),  # deep holes
                'current_preference': 'slow',
                'pollution_tolerance': 0.6
            },
        }
        
        if self.species in profiles:
            for key, value in profiles[self.species].items():
                setattr(self, key, value)
        else:
            log(f"Unknown species: {self.species}", "ERROR")
            raise ValueError(f"Unknown species: {self.species}")

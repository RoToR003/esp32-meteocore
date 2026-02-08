"""
Fish Activity Forecasting Demo
==============================

Demonstration of the fish bite prediction module.
Works on both CPython and MicroPython.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.fishing.activity import FishBiteForecastSystem, FishActivityCalculations
from src.fishing.profiles import FishProfile, FishSpecies
from src.core.validators import DataValidator


def demo_fishing_forecast():
    """Demonstrate fish activity forecasting capabilities."""
    print("=" * 70)
    print("ESP32-MeteoCore - Fish Activity Forecasting Demo")
    print("=" * 70)
    print()
    
    # Initialize fish forecast system
    print("Initializing fish bite forecast system...")
    # Using Pike (Щука) as default species
    fish_system = FishBiteForecastSystem(species=FishSpecies.PIKE)
    
    # Example conditions for fishing
    conditions = {
        'temp_celsius': 20.0,           # Air temperature
        'pressure_hpa': 1015.0,         # Atmospheric pressure
        'pressure_change_3h': 2.0,      # Pressure rising (good!)
        'water_temp_celsius': 18.0,     # Water temperature
        'dissolved_O2_mg_per_L': 8.5,   # Good oxygen level
        'illuminance_lux': 5000.0,      # Moderate light (morning)
        'wind_speed_m_s': 3.0,          # Light wind
        'moon_phase': 0.5,              # Half moon
        'time_of_day': 7,               # 7 AM - morning
        'month': 6,                     # June - summer
        'is_raining': False,            # No rain
        'cloud_cover_percent': 40       # Partly cloudy
    }
    
    # Validate conditions
    try:
        validated = DataValidator.validate_conditions(conditions)
        print(f"Conditions validated successfully")
    except Exception as e:
        print(f"Validation warning: {e}")
    
    print()
    print("Environmental Conditions:")
    print("-" * 70)
    print(f"Air Temperature:     {conditions['temp_celsius']}°C")
    print(f"Water Temperature:   {conditions['water_temp_celsius']}°C")
    print(f"Pressure:            {conditions['pressure_hpa']} hPa (change: +{conditions['pressure_change_3h']} hPa)")
    print(f"Dissolved Oxygen:    {conditions['dissolved_O2_mg_per_L']} mg/L")
    print(f"Light Level:         {conditions['illuminance_lux']} lux")
    print(f"Wind Speed:          {conditions['wind_speed_m_s']} m/s")
    print(f"Moon Phase:          {conditions['moon_phase']} (0=new, 1=full)")
    print(f"Time:                {conditions['time_of_day']}:00")
    print(f"Month:               {conditions['month']} (June)")
    print()
    
    # Calculate KIAR (Comprehensive Fish Activity Index)
    print("Calculating Fish Activity Index (KIAR)...")
    print("-" * 70)
    result = fish_system.calculate_KIAR(conditions)
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"KIAR (Fish Activity): {result['KIAR_percent']:.1f}%")
        print(f"Interpretation:       {result['interpretation']}")
        print(f"Recommendation:       {result['recommendation']}")
        print()
        
        print("Individual Coefficients:")
        for key, value in result['coefficients'].items():
            print(f"  {key}: {value:.3f}")
    
    print()
    
    # Test different fish species
    print("Fish Activity by Species:")
    print("-" * 70)
    
    species_to_test = [
        FishSpecies.PIKE,
        FishSpecies.PERCH,
        FishSpecies.CARP,
        FishSpecies.CATFISH
    ]
    
    for species in species_to_test:
        profile_obj = FishProfile(species)
        
        # Calculate temperature coefficient for this species
        calc = FishActivityCalculations()
        K_temp = calc.K_temperature(
            conditions['water_temp_celsius'],
            profile_obj
        )
        
        # Estimate activity (simplified)
        activity = K_temp * result['KIAR_percent']
        
        print(f"{species.value:15s}: {activity:.1f}% activity (optimal temp: {profile_obj.T_opt}°C)")
    
    print()
    
    # Print detailed report
    print("Detailed Forecast Report:")
    print("-" * 70)
    fish_system.print_forecast_report(result)
    
    # Save to file
    fish_system.save_forecast_to_json(result, "/tmp/fishing_forecast.json")
    print("Forecast saved to /tmp/fishing_forecast.json")
    
    print()
    print("=" * 70)
    print("Demo completed!")
    print("=" * 70)
    print()
    print("Tips:")
    print("  - KIAR > 70%: Excellent fishing conditions")
    print("  - KIAR 50-70%: Good fishing conditions")
    print("  - KIAR 30-50%: Moderate fishing conditions")
    print("  - KIAR < 30%: Poor fishing conditions")


if __name__ == "__main__":
    try:
        demo_fishing_forecast()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

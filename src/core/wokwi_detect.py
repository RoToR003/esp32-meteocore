"""
Wokwi Environment Detection
===========================

Detects whether code is running in Wokwi simulator or on real hardware.
Helps adapt behavior for simulation vs physical device.

Author: ESP32-MeteoCore Project
"""


def is_wokwi():
    """
    Check if code is running in Wokwi simulator.
    
    Returns:
        bool: True if Wokwi, False if real hardware
    """
    try:
        import sys
        # Wokwi adds special markers in sys.implementation
        if hasattr(sys, 'implementation'):
            impl_name = sys.implementation.name if hasattr(sys.implementation, 'name') else ''
            # Check for Wokwi-specific markers
            if 'wokwi' in impl_name.lower():
                return True
        
        # Check if wokwi module exists (Wokwi-specific)
        try:
            import wokwi
            return True
        except ImportError:
            pass
        
        # Fallback: check for simulation patterns
        # Wokwi often has specific board IDs or patterns
        return False
        
    except Exception:
        return False


def get_environment():
    """
    Get detailed environment information.
    
    Returns:
        dict: Environment details including platform, board, version
    """
    import sys
    
    env = {
        'platform': 'wokwi' if is_wokwi() else 'hardware',
        'micropython_version': sys.version if hasattr(sys, 'version') else 'unknown',
    }
    
    # Try to detect board type
    try:
        import machine
        # ESP32-S3 specific detection
        if hasattr(machine, 'unique_id'):
            uid = machine.unique_id()
            env['board_id'] = ''.join('{:02x}'.format(b) for b in uid)
        
        # Frequency info
        if hasattr(machine, 'freq'):
            env['cpu_freq'] = machine.freq()
    except Exception:
        pass
    
    return env


def log_environment():
    """
    Log environment details for debugging.
    
    Returns:
        None
    """
    env = get_environment()
    print("=" * 50)
    print("ENVIRONMENT DETECTION")
    print("=" * 50)
    print(f"Platform: {env['platform']}")
    print(f"MicroPython: {env.get('micropython_version', 'N/A')}")
    if 'board_id' in env:
        print(f"Board ID: {env['board_id']}")
    if 'cpu_freq' in env:
        print(f"CPU Frequency: {env['cpu_freq']} Hz")
    print("=" * 50)

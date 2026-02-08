"""
ESP32-S3 Meteo Station - Boot Configuration
============================================

Executed on boot before main.py.
Sets up basic system configuration.

Author: ESP32-MeteoCore Project
"""

import gc

# Enable garbage collection
gc.enable()

print("=" * 50)
print("ESP32-S3 Meteo Station - Boot")
print("=" * 50)

# Print memory info
print(f"Free memory: {gc.mem_free()} bytes")

# Run initial GC
gc.collect()

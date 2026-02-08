"""
Memory Optimization for ESP32-S3 MicroPython
=============================================

Techniques:
- Minimal imports
- Generator functions
- Memory-efficient data structures
- No numpy/pandas/heavy libs

Author: ESP32-MeteoCore Project
"""


def log(message, level="INFO"):
    """Simple logging function for both CPython and MicroPython."""
    try:
        print(f"[{level}] MEM: {message}")
    except:
        pass


def optimize_memory():
    """Apply memory optimizations."""
    try:
        import gc
        
        # Enable and run garbage collection
        gc.enable()
        gc.collect()
        
        log(f"Free memory: {gc.mem_free()} bytes")
        
        # Try to enable emergency exception buffer (MicroPython specific)
        try:
            import micropython
            micropython.alloc_emergency_exception_buf(100)
        except:
            pass
    except Exception as e:
        log(f"Error optimizing memory: {e}", "ERROR")


def get_memory_stats():
    """Get memory statistics."""
    try:
        import gc
        return {
            'free': gc.mem_free(),
            'allocated': gc.mem_alloc(),
            'total': gc.mem_free() + gc.mem_alloc()
        }
    except:
        return {
            'free': 0,
            'allocated': 0,
            'total': 0
        }


class CircularBuffer:
    """Fixed-size circular buffer (no dynamic allocation)."""
    
    def __init__(self, size):
        """
        Initialize circular buffer.
        
        Args:
            size: Maximum buffer size
        """
        self.size = size
        self.buffer = [0.0] * size
        self.index = 0
        self.count = 0
    
    def append(self, value):
        """Add value to buffer."""
        self.buffer[self.index] = value
        self.index = (self.index + 1) % self.size
        self.count = min(self.count + 1, self.size)
    
    def get_last_n(self, n):
        """
        Get last N values.
        
        Args:
            n: Number of values to retrieve
            
        Returns:
            List of last n values
        """
        if n > self.count:
            n = self.count
        
        result = []
        idx = (self.index - 1) % self.size
        
        for _ in range(n):
            result.insert(0, self.buffer[idx])
            idx = (idx - 1) % self.size
        
        return result
    
    def get_all(self):
        """Get all values in chronological order."""
        return self.get_last_n(self.count)
    
    def calculate_delta(self):
        """
        Calculate pressure delta (last - first).
        
        Returns:
            Delta value
        """
        if self.count < 2:
            return 0.0
        
        last = self.buffer[(self.index - 1) % self.size]
        
        # Calculate first element index correctly
        if self.count < self.size:
            # Buffer not full yet, first element is at index 0
            first_idx = 0
        else:
            # Buffer is full, first element is at current index
            first_idx = self.index
        
        first = self.buffer[first_idx]
        
        return last - first
    
    def clear(self):
        """Clear buffer."""
        self.index = 0
        self.count = 0
        self.buffer = [0.0] * self.size

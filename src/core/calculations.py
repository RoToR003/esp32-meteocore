"""
Mathematical calculations for meteorological and fishing predictions.
Numpy-free implementations for MicroPython compatibility.
"""

import math
from typing import List, Optional


def mean(data: List[float]) -> float:
    """
    Calculate arithmetic mean of a list of numbers.
    
    Args:
        data: List of numeric values
        
    Returns:
        Mean value, or 0.0 if list is empty
    """
    if not data:
        return 0.0
    return sum(data) / len(data)


def std_dev(data: List[float]) -> float:
    """
    Calculate standard deviation of a list of numbers.
    
    Args:
        data: List of numeric values
        
    Returns:
        Standard deviation, or 0.0 if list is empty or has single element
    """
    if not data or len(data) < 2:
        return 0.0
    
    m = mean(data)
    variance = sum((x - m) ** 2 for x in data) / len(data)
    return math.sqrt(variance)


def variance(data: List[float]) -> float:
    """
    Calculate variance of a list of numbers.
    
    Args:
        data: List of numeric values
        
    Returns:
        Variance, or 0.0 if list is empty
    """
    if not data:
        return 0.0
    
    m = mean(data)
    return sum((x - m) ** 2 for x in data) / len(data)


def median(data: List[float]) -> float:
    """
    Calculate median of a list of numbers.
    
    Args:
        data: List of numeric values
        
    Returns:
        Median value, or 0.0 if list is empty
    """
    if not data:
        return 0.0
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    
    if n % 2 == 0:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        return sorted_data[n // 2]


def percentile(data: List[float], p: float) -> float:
    """
    Calculate percentile of a list of numbers.
    
    Args:
        data: List of numeric values
        p: Percentile value (0-100)
        
    Returns:
        Percentile value, or 0.0 if list is empty
    """
    if not data:
        return 0.0
    
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (n - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    
    if f == c:
        return sorted_data[int(k)]
    
    d0 = sorted_data[int(f)] * (c - k)
    d1 = sorted_data[int(c)] * (k - f)
    return d0 + d1


def exponential_smoothing(current_value: float, previous_smoothed: float, alpha: float = 0.3) -> float:
    """
    Apply exponential smoothing to reduce sensor noise.
    
    Args:
        current_value: Current sensor reading
        previous_smoothed: Previously smoothed value
        alpha: Smoothing factor (0.0 - very smooth, 1.0 - no smoothing)
        
    Returns:
        Smoothed value
    """
    return alpha * current_value + (1 - alpha) * previous_smoothed


def moving_average(data: List[float], window_size: int) -> List[float]:
    """
    Calculate moving average with specified window size.
    
    Args:
        data: List of numeric values
        window_size: Size of the moving window
        
    Returns:
        List of smoothed values
    """
    if not data or window_size < 1:
        return data
    
    if window_size > len(data):
        window_size = len(data)
    
    result = []
    for i in range(len(data)):
        start = max(0, i - window_size + 1)
        window = data[start:i + 1]
        result.append(mean(window))
    
    return result


def linear_interpolation(x: float, x0: float, y0: float, x1: float, y1: float) -> float:
    """
    Perform linear interpolation between two points.
    
    Args:
        x: X value to interpolate at
        x0, y0: First point coordinates
        x1, y1: Second point coordinates
        
    Returns:
        Interpolated Y value
    """
    if x1 == x0:
        return y0
    
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Normalize a value to 0-1 range.
    
    Args:
        value: Value to normalize
        min_val: Minimum of the range
        max_val: Maximum of the range
        
    Returns:
        Normalized value (0-1)
    """
    if max_val == min_val:
        return 0.5
    
    return (value - min_val) / (max_val - min_val)


def denormalize(normalized_value: float, min_val: float, max_val: float) -> float:
    """
    Denormalize a value from 0-1 range.
    
    Args:
        normalized_value: Normalized value (0-1)
        min_val: Minimum of the target range
        max_val: Maximum of the target range
        
    Returns:
        Denormalized value
    """
    return min_val + normalized_value * (max_val - min_val)


def derivative(data: List[float], dt: float = 1.0) -> List[float]:
    """
    Calculate numerical derivative (rate of change).
    
    Args:
        data: List of values
        dt: Time step between values
        
    Returns:
        List of derivatives
    """
    if not data or len(data) < 2:
        return []
    
    result = []
    for i in range(len(data) - 1):
        result.append((data[i + 1] - data[i]) / dt)
    
    # Append last value to maintain same length
    result.append(result[-1] if result else 0.0)
    
    return result


def integrate(data: List[float], dt: float = 1.0) -> float:
    """
    Calculate numerical integral (sum) using trapezoidal rule.
    
    Args:
        data: List of values
        dt: Time step between values
        
    Returns:
        Integrated value
    """
    if not data or len(data) < 2:
        return 0.0
    
    total = 0.0
    for i in range(len(data) - 1):
        total += (data[i] + data[i + 1]) / 2 * dt
    
    return total

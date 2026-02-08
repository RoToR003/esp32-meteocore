"""
Tests for Core Calculations
===========================

Unit tests for mathematical calculation functions.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.calculations import (
    mean, std_dev, variance, median, percentile,
    exponential_smoothing, moving_average,
    linear_interpolation, clamp, normalize, denormalize
)


class TestCalculations(unittest.TestCase):
    """Test calculation functions."""
    
    def test_mean(self):
        """Test mean calculation."""
        self.assertEqual(mean([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(mean([10, 20, 30]), 20.0)
        self.assertEqual(mean([]), 0.0)
        self.assertEqual(mean([5]), 5.0)
    
    def test_std_dev(self):
        """Test standard deviation calculation."""
        # Test with known values
        data = [2, 4, 4, 4, 5, 5, 7, 9]
        result = std_dev(data)
        self.assertAlmostEqual(result, 2.0, places=1)
        
        # Edge cases
        self.assertEqual(std_dev([]), 0.0)
        self.assertEqual(std_dev([5]), 0.0)
    
    def test_variance(self):
        """Test variance calculation."""
        data = [1, 2, 3, 4, 5]
        var = variance(data)
        self.assertAlmostEqual(var, 2.0, places=1)
    
    def test_median(self):
        """Test median calculation."""
        self.assertEqual(median([1, 2, 3, 4, 5]), 3.0)
        self.assertEqual(median([1, 2, 3, 4]), 2.5)
        self.assertEqual(median([5]), 5.0)
        self.assertEqual(median([]), 0.0)
    
    def test_percentile(self):
        """Test percentile calculation."""
        data = list(range(1, 101))  # 1 to 100
        self.assertAlmostEqual(percentile(data, 50), 50.5, places=1)
        self.assertAlmostEqual(percentile(data, 25), 25.75, places=1)
        self.assertAlmostEqual(percentile(data, 75), 75.25, places=1)
    
    def test_exponential_smoothing(self):
        """Test exponential smoothing."""
        # With alpha=1.0, should return current value
        result = exponential_smoothing(10.0, 5.0, alpha=1.0)
        self.assertEqual(result, 10.0)
        
        # With alpha=0.0, should return previous value
        result = exponential_smoothing(10.0, 5.0, alpha=0.0)
        self.assertEqual(result, 5.0)
        
        # With alpha=0.5, should be average
        result = exponential_smoothing(10.0, 6.0, alpha=0.5)
        self.assertEqual(result, 8.0)
    
    def test_moving_average(self):
        """Test moving average."""
        data = [1, 2, 3, 4, 5]
        result = moving_average(data, 3)
        self.assertEqual(len(result), 5)
        self.assertAlmostEqual(result[-1], 4.0, places=1)  # Average of last 3: (3+4+5)/3
    
    def test_linear_interpolation(self):
        """Test linear interpolation."""
        # Interpolate at midpoint
        result = linear_interpolation(0.5, 0.0, 0.0, 1.0, 10.0)
        self.assertEqual(result, 5.0)
        
        # Interpolate at 0.75
        result = linear_interpolation(0.75, 0.0, 0.0, 1.0, 10.0)
        self.assertEqual(result, 7.5)
    
    def test_clamp(self):
        """Test clamp function."""
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)
    
    def test_normalize(self):
        """Test normalization."""
        result = normalize(5, 0, 10)
        self.assertEqual(result, 0.5)
        
        result = normalize(0, 0, 10)
        self.assertEqual(result, 0.0)
        
        result = normalize(10, 0, 10)
        self.assertEqual(result, 1.0)
    
    def test_denormalize(self):
        """Test denormalization."""
        result = denormalize(0.5, 0, 10)
        self.assertEqual(result, 5.0)
        
        result = denormalize(0.0, 0, 10)
        self.assertEqual(result, 0.0)
        
        result = denormalize(1.0, 0, 10)
        self.assertEqual(result, 10.0)


if __name__ == '__main__':
    unittest.main()

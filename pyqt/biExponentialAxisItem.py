import numpy as np
from pyqtgraph.graphicsItems.AxisItem import AxisItem

class BiExponentialAxisItem(AxisItem):
    """
    Custom axis with linear scaling from 0-100 and logarithmic scaling from 100-10^8.
    
    Major ticks are placed at 0, 100, 10^3, 10^4, 10^5, 10^6, 10^7, 10^8.
    Minor ticks are linearly spaced between 0-100 and logarithmically spaced between decades above 100.
    """
    def __init__(self, orientation, linear_threshold=100.0, **kwargs):
        super().__init__(orientation, **kwargs)
        self.linear_threshold = linear_threshold
        
    def tickValues(self, minVal, maxVal, size):
        """Generate tick values with mixed linear/log scaling"""
        # Scale values to account for SI prefix
        minVal *= self.scale
        maxVal *= self.scale
        
        major_ticks = []
        minor_ticks = []
        
        # Determine visible range
        show_linear_region = minVal < self.linear_threshold
        show_log_region = maxVal > self.linear_threshold
        
        # Add linear region ticks (0 to linear_threshold)
        if show_linear_region:
            # Add major tick at 0
            if minVal <= 0:
                major_ticks.append(0)
            
            # Add major tick at linear_threshold
            if maxVal >= self.linear_threshold:
                major_ticks.append(self.linear_threshold)
            
            # Add minor ticks in linear region (98 divisions)
            linear_divisions = 98
            linear_spacing = self.linear_threshold / (linear_divisions + 1)
            for i in range(1, linear_divisions + 1):
                tick = i * linear_spacing
                if minVal <= tick <= maxVal:
                    minor_ticks.append(tick)
        
        # Add logarithmic region ticks (linear_threshold to 10^8)
        if show_log_region:
            # Add major ticks at powers of 10
            for exp in range(3, 9):  # 10^3 to 10^8
                tick = 10**exp
                if minVal <= tick <= maxVal:
                    major_ticks.append(tick)
            
            # Add minor ticks (8 per decade) in log regions
            start_decade = int(np.ceil(np.log10(max(self.linear_threshold, minVal))))
            end_decade = int(np.floor(np.log10(min(1e8, maxVal))))
            
            for decade in range(start_decade, end_decade + 1):
                base = 10**decade
                # Generate 8 log-spaced ticks within each decade
                for i in range(1, 9):
                    multiplier = 10**(i/8)
                    tick = base * multiplier
                    if minVal <= tick <= maxVal and tick not in major_ticks:
                        minor_ticks.append(tick)
        
        # Convert to format expected by pyqtgraph
        return [
            (None, [t / self.scale for t in major_ticks]),
            (None, [t / self.scale for t in minor_ticks])
        ]
    
    def tickStrings(self, values, scale, spacing):
        """Format tick labels for mixed linear/log scaling"""
        strings = []
        for v in values:
            scaled_val = v * scale
            
            if abs(scaled_val) < 1e-10:
                # Zero case
                strings.append('0')
            elif scaled_val < self.linear_threshold:
                # Linear region - format with appropriate precision
                if scaled_val < 10:
                    strings.append(f"{scaled_val:.1f}")
                else:
                    strings.append(f"{scaled_val:.0f}")
            elif scaled_val == 100:
                strings.append('100')
            elif scaled_val == 1000:
                strings.append('10³')
            elif scaled_val == 10000:
                strings.append('10⁴')
            elif scaled_val == 100000:
                strings.append('10⁵')
            elif scaled_val == 1000000:
                strings.append('10⁶')
            elif scaled_val == 10000000:
                strings.append('10⁷')
            elif scaled_val == 100000000:
                strings.append('10⁸')
            else:
                # Skip intermediate labels in log region to avoid crowding
                strings.append('')
                
        return strings
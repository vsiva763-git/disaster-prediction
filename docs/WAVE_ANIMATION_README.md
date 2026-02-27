# Advanced Wave Animation Dashboard

## Overview
The wave animation dashboard provides real-time, visually stunning visualization of tsunami wave patterns with multiple animation modes. It's designed to display simulated and real-time water level data from three key ocean regions around India.

## Features

### 🌊 Animation Types
1. **Smooth Waves** - Realistic water surface waves with smooth sinusoidal curves
2. **Turbulent** - Chaotic, rough water patterns simulating turbulent conditions
3. **Particle Flow** - Animated particles flowing along wave surfaces
4. **Spectral** - Rainbow gradient effects with multiple frequency overlays

### 📊 Real-time Controls
- **Amplitude Control**: Adjust wave height (1-10 units)
- **Frequency Control**: Change wave oscillation speed (0.5-3.0)
- **Animation Speed**: Control playback speed (0.5-3.0x)
- **Play/Pause**: Toggle animation on/off
- **Reset**: Return animation to initial state

### 📈 Live Monitoring Regions
- **Arabian Sea**: Monitors western coastal waters
- **Bay of Bengal**: Tracks eastern coastal regions
- **Andaman Sea**: Observes Andaman and Nicobar waters

### 📊 Real-time Statistics
Each region displays:
- **Max Height**: Current maximum wave height (meters)
- **Risk Level**: Color-coded risk assessment (LOW/MODERATE/HIGH)
- **Wave Period**: Time between wave peaks (seconds)
- **Speed**: Current wave propagation speed (m/s)

### 📋 Global Statistics Panel
- **Global Max Height**: Highest wave across all regions
- **Average Risk**: Aggregate risk level
- **Monitoring Regions**: Number of active monitoring zones
- **Real-time Status**: Live system status indicator

## How to Access

### Local Development
```bash
# Start the Flask app
python app.py

# Access the wave animation dashboard
http://localhost:5000/waves
```

### From Main Dashboard
- Navigate to the main dashboard (http://localhost:5000)
- Click the **"🌊 Wave Visualization"** button in the header

## Visual Features

### Color Coding
- **Blue (#3498db)**: Arabian Sea waves
- **Green (#2ecc71)**: Bay of Bengal waves
- **Orange (#e67e22)**: Andaman Sea waves

### Risk Levels
- 🟢 **LOW**: Safe conditions
- 🟠 **MODERATE**: Elevated wave activity
- 🔴 **HIGH**: Dangerous conditions

## Technical Details

### Canvas Rendering
- Uses HTML5 Canvas for smooth, performant animations
- GPU-accelerated rendering where available
- 60 FPS target animation frame rate
- Responsive to browser window resizing

### Wave Mathematics
The visualizations use combinations of:
- Sine wave functions: $\sin(x) = $ wave surface
- Multiple frequencies: Complex wave patterns
- Phase shifts: Realistic water movement
- Amplitude modulation: Dynamic height changes

### Animation Modes

#### Smooth Waves Algorithm
```
y = y_center + A * sin(2π * f * x + t * speed) + A/2 * sin(4π * f/2 * x + t * speed * 0.7)
```
Where:
- A = Amplitude (wave height)
- f = Frequency (oscillation rate)
- t = Time (animation progress)

#### Turbulent Waves Algorithm
Multiple overlapping frequencies with random phase variations create turbulent appearance:
```
y = y_center + Σ sin(freq_i * x + t * speed + random)
```

#### Particle Flow Algorithm
Particles follow wave surface with additional vertical jitter:
```
particle_x = (t * speed * 50 + offset) % width
particle_y = wave_surface + sin(t * 2 + index) * 10
```

#### Spectral Algorithm
Uses HSL color space with multiple overlaid waves at different frequencies:
```
hue = (180 + offset * 360) % 360
saturation = 70 + step * 5%
```

## Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 14+)
- Mobile browsers: Responsive design optimized

## Performance Optimizations
- Debounced resize events
- Efficient canvas clearing and redrawing
- Minimal DOM manipulations
- CSS transforms for smooth animations

## Data Integration

### Real Wave Data Sources
The dashboard can integrate with:
- IOC (Indian Ocean Commission) tide stations
- NOAA buoy network
- Real-time water level APIs
- Seismic monitoring systems

### Fallback Simulation
If real-time data is unavailable, the visualization:
1. Generates realistic synthetic wave patterns
2. Maintains historical data consistency
3. Provides educational value for training

## Customization

### Modify Wave Parameters
Edit the `regions` array in the JavaScript:
```javascript
regions = [
    {
        id: 'region_name',
        name: 'Display Name',
        color: '#hexcolor',
        gradient: ['#color1', '#color2', '#color3', '#color4'],
        baseFreq: 0.05,  // Base frequency
        amplitude: 40     // Base amplitude
    }
]
```

### Change Animation Speed
Modify the time step in the animation loop:
```javascript
animationState.time += 0.016; // Default 60 FPS
animationState.time += 0.008; // For 120 FPS (2x faster)
```

## Responsive Design

### Desktop (1200px+)
- 3 wave panels in grid
- Full-size statistics panel
- Optimal readability

### Tablet (768px-1199px)
- 2 wave panels per row
- Adjusted spacing
- Touch-friendly controls

### Mobile (<768px)
- Single column layout
- Smaller wave containers
- Optimized button sizes

## Future Enhancements

### Planned Features
- 3D wave visualization using Three.js
- Real-time earthquake overlay
- Wave prediction algorithms
- Historical data playback
- Export visualization as video
- Live WebSocket data streaming
- Machine learning pattern recognition

### Potential Improvements
- WebGL rendering for better performance
- Advanced particle physics
- Fluid dynamics simulation
- Augmented reality visualization
- Multi-region comparison tools

## API Endpoints

### Wave Data Endpoint
```
GET /wave-data
Response:
{
    "success": true,
    "wave_data": {
        "arabian": { "stations": [...] },
        "bengal": { "stations": [...] },
        "andaman": { "stations": [...] }
    }
}
```

### Animation Dashboard Route
```
GET /waves
Returns: HTML dashboard with embedded visualization
```

## Troubleshooting

### Animations Not Playing
- Check browser console for JavaScript errors
- Ensure hardware acceleration is enabled
- Try different animation mode

### Slow Performance
- Reduce amplitude for smoother rendering
- Check for competing CPU tasks
- Update graphics drivers
- Try a different browser

### Data Not Updating
- Verify API connectivity
- Check network tab in developer tools
- Ensure data sources are online
- Review server logs

## Files

- **wave_animation.html**: Main visualization dashboard
- **app.py**: Flask route handler (`/waves`)
- **index_live.html**: Navigation link integration

## Credits

- Developed for India Tsunami Early Warning System
- Uses HTML5 Canvas for rendering
- Inspired by oceanographic visualization techniques
- Based on real-time seismic and oceanographic data

## License

This visualization component is part of the India Tsunami Early Warning System project.

---

**Last Updated**: January 23, 2026
**Version**: 1.0.0

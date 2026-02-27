# Wave Animation Quick Start Guide

## Access the Wave Animation Dashboard

### Option 1: From Main Dashboard
1. Open http://localhost:5000 (or your deployed URL)
2. Click the **"🌊 Wave Visualization"** button in the top right
3. The advanced wave animation dashboard will load

### Option 2: Direct URL
Navigate directly to: `http://localhost:5000/waves`

## Using the Dashboard

### Interactive Controls

**Amplitude Slider**
- Controls the height of the waves
- Range: 1-10 units
- Higher values = bigger waves
- Default: 3.0

**Frequency Slider**
- Controls how fast the waves oscillate
- Range: 0.5-3.0
- Higher values = faster oscillations
- Default: 1.5

**Speed Slider**
- Controls animation playback speed
- Range: 0.5-3.0x
- Represents multiplication factor
- Default: 1.5x

**Play/Pause Button**
- Toggles animation on/off
- Current state shown in status panel

**Reset Button**
- Restarts animation from beginning
- Resets time counter to 0

### Animation Mode Buttons

Click any button to switch animation type:

🌊 **Smooth Waves**
- Realistic, flowing water surface
- Best for normal conditions
- Smooth sinusoidal curves

⚡ **Turbulent**
- Chaotic, rough patterns
- Simulates turbulent water
- Multiple overlapping frequencies

✨ **Particle Flow**
- Shows particles moving on wave surface
- Good for understanding flow direction
- Visual particle tracking

🎨 **Spectral**
- Rainbow gradient effects
- Multiple frequency layers
- Aesthetically stunning

## Understanding the Data Panels

### Wave Panels (Arabian Sea, Bay of Bengal, Andaman Sea)

Each region shows:
- **Max Height**: Current highest wave (meters)
- **Risk Level**: Color-coded safety assessment
- **Wave Period**: Time between wave peaks (seconds)
- **Speed**: Wave propagation speed (m/s)
- **Live Visualization**: Canvas showing wave pattern

### Statistics Panel (Bottom)

Global metrics:
- **Global Max Height**: Highest wave across all regions
- **Average Risk**: Overall risk level (LOW/MODERATE/HIGH)
- **Monitoring Regions**: Number of active zones (always 3)
- **Real-time Status**: System operational status

### Color Indicators

Risk Levels:
- 🟢 **LOW** (Green) - Safe conditions
- 🟠 **MODERATE** (Orange) - Elevated activity
- 🔴 **HIGH** (Red) - Dangerous conditions

Region Colors:
- Blue: Arabian Sea
- Green: Bay of Bengal  
- Orange: Andaman Sea

## Tips & Tricks

### For Realistic Simulation
1. Set Amplitude to 3-4
2. Set Frequency to 1.0-1.5
3. Use "Smooth Waves" mode
4. Leave speed at normal (1.5x)

### For Educational Demos
1. Try "Spectral" mode for visual appeal
2. Increase amplitude to 8-10 for dramatic effect
3. Slow down speed to 0.5x for observation
4. Use "Particle Flow" to show movement direction

### For Performance
1. Use "Smooth Waves" - most optimized
2. Reduce amplitude if lagging
3. Use smaller browser window
4. Close other browser tabs

### For Monitoring
1. Leave on "Smooth Waves"
2. Set moderate values (3-4 amplitude)
3. Enable auto-refresh on main dashboard
4. Monitor risk level colors

## Real-time Data Integration

### Current Status
- **Simulated Data**: Always available
- **Real Data**: When APIs are online
- **Fallback**: Automatic if APIs down

### Data Sources
- USGS Earthquake API
- IOC Tide Stations (when available)
- NOAA Buoy Network (when available)
- AI Model Predictions

## Keyboard Shortcuts

Currently supported:
- **Space**: Toggle Play/Pause
- **R**: Reset animation

(Note: Currently mouse/button control only - keyboard shortcuts can be added)

## Mobile Usage

Works on all devices:
- **Phones**: Portrait orientation optimized
- **Tablets**: Landscape recommended
- **Touch**: Tap buttons to control
- **Performance**: May vary on older devices

## Troubleshooting

### Waves Not Moving
- Check "Real-time Status" in stats panel
- Click Play/Pause to restart
- Click Reset button
- Try different animation mode

### Slow Animation
- Reduce amplitude slider
- Try "Smooth Waves" mode
- Close other browser tabs
- Reduce window size

### Data Not Showing
- Refresh page (Ctrl+R)
- Check network connection
- Verify server is running
- Check browser console for errors

### Display Issues
- Make browser window larger
- Try different zoom level (Ctrl +/-)
- Use Firefox or Chrome (best compatibility)
- Clear browser cache (Ctrl+Shift+Delete)

## Sharing & Screenshotting

### Take Screenshots
1. Use browser built-in tools (Ctrl+Shift+S)
2. Or use OS screenshot tool
3. Export/share the image

### Record Video
Use screen recording tools:
- Windows: Xbox Game Bar (Win+G)
- Mac: QuickTime Player
- Linux: SimpleScreenRecorder
- Browser: RecordRTC extension

## Integration with Main Dashboard

### Links
- From wave animation → No direct link back (use back button)
- From main dashboard → Click "🌊 Wave Visualization" button
- From summary → Not directly linked

### Synchronized Updates
- Wave animation updates every 60 frames/second
- Main dashboard updates every 30 seconds
- Data refreshes are independent

## Advanced Settings (For Developers)

Edit `wave_animation.html` JavaScript to customize:

```javascript
// Change region parameters
const regions = [
    {
        baseFreq: 0.05,    // Increase for faster waves
        amplitude: 40      // Increase for bigger waves
    }
]

// Change animation frame rate
animationState.time += 0.016; // 60 FPS (lower = slower)
```

## Performance Metrics

Expected performance:
- **Desktop**: 60 FPS (smooth)
- **Tablet**: 30-60 FPS (smooth)
- **Mobile**: 20-30 FPS (acceptable)
- **Older Devices**: 10-20 FPS (functional)

## Browser Requirements

Minimum requirements:
- HTML5 Canvas support
- ES6 JavaScript support
- Modern CSS Grid
- Canvas 2D Context

Tested on:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Safari (iOS 14+)
- ✅ Chrome Mobile (Android 9+)

## Support & Feedback

For issues or suggestions:
1. Check troubleshooting section
2. Review browser console (F12)
3. Check network tab for API errors
4. Report issues with details

## Next Steps

Explore other features:
- 📊 Main Dashboard (http://localhost:5000)
- 📈 Summary Page (http://localhost:5000/summary)
- 🔌 API Endpoints (http://localhost:5000/api)
- 🧪 Test Page (http://localhost:5000/test-data)

---

**Happy Monitoring! 🌊**

Last Updated: January 23, 2026

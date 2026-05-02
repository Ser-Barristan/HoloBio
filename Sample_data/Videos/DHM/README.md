## RBC Phase Video — Tracking Example

**File:** `RBC-Phase_15fps_Tracking`

This video corresponds to a phase reconstruction of red blood cells (RBCs) acquired using a 10× microscope objective. It is intended for testing and demonstrating particle tracking functionality.

### Acquisition Parameters

- **Wavelength:** 0.633 µm  
- **Pixel pitch (X, Y):** 3.75 µm, 3.75 µm  
- **Microscope objective:** 10×  

### Tracking Configuration

- **Filter method:** Gaussian  
- **Color filtering:** Enabled (blob color: 255 — white sample)  
- **Minimum area:** 150  
- **Maximum area:** 500  

### Kalman Filter Parameters

- **P (initial uncertainty):** 100  
- **Q (process noise):** 0.01  
- **R (measurement noise):** 1  

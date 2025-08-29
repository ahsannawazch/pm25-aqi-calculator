
import math

def calculate_pm25_concentration(mass_initial, mass_final, flow_rate, time_start, time_stop):
    """Calculates PM2.5 concentration in µg/m³."""
    if flow_rate <= 0 or time_stop <= time_start:
        return 0
    mass_diff_mg = mass_final - mass_initial
    volume_l = flow_rate * (time_stop - time_start)
    volume_m3 = volume_l / 1000
    concentration_mg_m3 = mass_diff_mg / volume_m3
    concentration_ug_m3 = concentration_mg_m3 * 1000
    return concentration_ug_m3

def get_aqi_breakpoints():
    """Returns the EPA AQI breakpoints for PM2.5."""
    return {
        (0.0, 12.0): (0, 50),
        (12.1, 35.4): (51, 100),
        (35.5, 55.4): (101, 150),
        (55.5, 150.4): (151, 200),
        (150.5, 250.4): (201, 300),
        (250.5, 350.4): (301, 400),
        (350.5, 500.4): (401, 500),
    }

def calculate_aqi(pm25_concentration):
    """Calculates the AQI for a given PM2.5 concentration."""
    breakpoints = get_aqi_breakpoints()
    c = math.trunc(pm25_concentration * 10) / 10  # Truncate to one decimal place
    
    # Debug print to see what concentration we're working with
    print(f"Calculating AQI for concentration: {c} µg/m³")

    for (bp_low, bp_high), (i_low, i_high) in breakpoints.items():
        if bp_low <= c <= bp_high:
            # Linear interpolation formula
            aqi = ((i_high - i_low) / (bp_high - bp_low)) * (c - bp_low) + i_low
            calculated_aqi = round(aqi)
            print(f"AQI calculated: {calculated_aqi} (range: {bp_low}-{bp_high} -> {i_low}-{i_high})")
            return calculated_aqi

    # For concentrations above 500.4, extrapolate beyond the scale
    if c > 500.4:
        print(f"Concentration {c} is above EPA scale maximum (500.4). Returning 500 (Hazardous)")
        return 500
    
    print(f"Concentration {c} is below minimum scale. Returning 0")
    return 0  # For concentrations below 0

def get_aqi_category(aqi):
    """Returns the health category and color for a given AQI value."""
    if 0 <= aqi <= 50:
        return "Good", (0, 1, 0, 1)  # Green
    elif 51 <= aqi <= 100:
        return "Moderate", (1, 1, 0, 1)  # Yellow
    elif 101 <= aqi <= 150:
        return "Unhealthy for Sensitive Groups", (1, 0.5, 0, 1)  # Orange
    elif 151 <= aqi <= 200:
        return "Unhealthy", (1, 0, 0, 1)  # Red
    elif 201 <= aqi <= 300:
        return "Very Unhealthy", (0.5, 0, 0.5, 1)  # Purple
    else:
        return "Hazardous", (0.5, 0, 0.1, 1)  # Maroon



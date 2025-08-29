# print("=== Air Sample Concentration Calculator (PM2.5 AQI) ===")

# # Fixed values
# lpm_avg = 5  # L/min (fixed)

# # Input values
# initial_mass = float(input("Enter Initial Mass (mg): "))
# final_mass = float(input("Enter Final Mass (mg): "))
# initial_time = float(input("Enter Initial Time (minutes): "))
# final_time = float(input("Enter Final Time (minutes): "))

# # Step 1: Mass in µg
# mass_ug = (final_mass - initial_mass) * 1000

# # Step 2: Total Time
# total_time = final_time - initial_time

# # Step 3: Volume (Excel logic uses 16.67 instead of 1000)
# volume_m3 = (lpm_avg * total_time) / 16.67

# # Step 4: Concentration
# concentration = mass_ug / volume_m3 if volume_m3 > 0 else 0

# # Step 5: AQI Calculation (PM2.5 breakpoints)
# breakpoints_pm25 = [
#     (0.0, 12.0, 0, 50),
#     (12.1, 35.4, 51, 100),
#     (35.5, 55.4, 101, 150),
#     (55.5, 150.4, 151, 200),
#     (150.5, 250.4, 201, 300),
#     (250.5, 350.4, 301, 400),
#     (350.5, 500.4, 401, 500),
# ]

# aqi = None
# for c_low, c_high, i_low, i_high in breakpoints_pm25:
#     if c_low <= concentration <= c_high:
#         aqi = ((i_high - i_low) / (c_high - c_low)) * (concentration - c_low) + i_low
#         break

# # Show results
# print("\n=== Results ===")
# print(f"Mass Collected: {mass_ug:.2f} µg")
# print(f"Total Time: {total_time:.2f} min")
# print(f"Volume Sampled: {volume_m3:.2f} m³")
# print(f"Concentration: {concentration:.2f} µg/m³")
# print(f"AQI (PM2.5): {aqi:.2f}" if aqi is not None else "AQI: Out of Range")


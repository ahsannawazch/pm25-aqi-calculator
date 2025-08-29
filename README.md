# PM2.5 AQI Calculator

A comprehensive mobile application for calculating Air Quality Index (AQI) from PM2.5 measurements with professional reporting capabilities.

## Features

- ✅ PM2.5 concentration calculation from sampling data
- ✅ Real-time AQI calculation with EPA standards
- ✅ Professional PDF and HTML report generation
- ✅ Monthly trend charts with color-coded AQI levels
- ✅ Excel data export/import functionality
- ✅ Local data storage with SQLite database
- ✅ Mobile-friendly interface optimized for Android

## Building Android APK

### Method 1: GitHub Actions (Recommended)

1. **Create GitHub Repository**:
   - Go to https://github.com and create a new repository
   - Upload all your project files

2. **Automatic APK Build**:
   - Push your code to the repository
   - GitHub Actions will automatically build the APK
   - Download APK from Actions → Artifacts → `android-apk`

3. **Manual Trigger**:
   - Go to Actions tab in your repository
   - Click "Build Android APK"
   - Click "Run workflow"

### Method 2: Local Build (Advanced)

If you have a Linux environment:

```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip git openjdk-11-jdk
pip install buildozer kivy

# Build APK
buildozer android debug
```

## Installation

1. Download the APK file from GitHub Actions
2. Transfer to your Android device
3. Enable "Install from Unknown Sources" in Android settings
4. Install the APK
5. Launch the app!

## Usage

1. **Input Data**:
   - Flow Rate (L/min)
   - Initial Mass (mg)
   - Final Mass (mg)
   - Start Time (min)
   - Stop Time (min)

2. **Calculate AQI**:
   - Click "Calculate AQI"
   - View results with color-coded health category

3. **Generate Reports**:
   - HTML Report: Interactive charts
   - PDF Report: Professional format with charts

4. **Data Management**:
   - Export data to Excel
   - Import data from Excel
   - Automatic local storage

## AQI Categories

| AQI Range | Category | Color |
|-----------|----------|--------|
| 0-50 | Good | Dark Green |
| 51-100 | Satisfactory | Dark Green |
| 101-150 | Moderate | Yellow |
| 151-200 | Unhealthy for Sensitive Groups | Brown |
| 201-300 | Unhealthy | Red |
| 301-400 | Very Unhealthy | Purple |
| 401-500 | Hazardous | Maroon |

## Technical Details

- **Framework**: Kivy (Python)
- **Database**: SQLite
- **Charts**: Matplotlib
- **Reports**: WeasyPrint (PDF), HTML
- **Data Export**: Excel (openpyxl)
- **Platform**: Android (APK)

## Requirements

- Android 5.0+ (API 21+)
- Storage permissions for reports
- Internet permission for data operations

## Support

For issues or questions:
1. Check GitHub Actions logs for build errors
2. Verify all Python files are included
3. Ensure buildozer.spec is properly configured

## License

This project is open source. Feel free to modify and distribute.
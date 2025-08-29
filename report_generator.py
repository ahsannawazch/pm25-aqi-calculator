import os
from datetime import datetime, timedelta
import random
import weasyprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import seaborn as sns
import base64
from io import BytesIO
import plotly.graph_objects as go
import plotly.io as pio
from database_manager import db_manager

def generate_monthly_data(current_aqi=None):
    """Generate random AQI data for the current month with today's real data."""
    dates = []
    aqi_values = []

    today = datetime.now()

    # Get the first day of the current month
    first_day = today.replace(day=1)

    # Generate dates from the 1st of the month to today
    current_date = first_day
    previous_aqi = None

    while current_date <= today:
        dates.append(current_date.strftime("%m/%d/%Y"))

        if current_date.date() == today.date() and current_aqi is not None:
            # Use the calculated AQI for today if provided
            aqi_values.append(current_aqi)
            previous_aqi = current_aqi
        else:
            # Generate realistic AQI values for all other dates
            if previous_aqi is None:
                # First day of the month - generate baseline
                base_aqi = random.randint(40, 120)
            else:
                # Subsequent days - correlate with previous day (±20 points)
                variation = random.randint(-20, 20)
                base_aqi = previous_aqi + variation

            # Add seasonal variation (higher in winter months)
            month = current_date.month
            seasonal_adjustment = 0
            if month in [11, 12, 1, 2]:  # Winter months - higher AQI
                seasonal_adjustment = random.randint(10, 25)
            elif month in [5, 6, 7, 8]:  # Summer months - lower AQI
                seasonal_adjustment = random.randint(-15, 5)

            base_aqi += seasonal_adjustment

            # Add weekly pattern (slightly higher on weekdays vs weekends)
            weekday = current_date.weekday()
            if weekday < 5:  # Monday-Friday
                base_aqi += random.randint(0, 10)
            else:  # Saturday-Sunday
                base_aqi -= random.randint(0, 8)

            # Ensure AQI stays within reasonable bounds
            base_aqi = max(15, min(250, base_aqi))
            aqi_values.append(base_aqi)
            previous_aqi = base_aqi

        current_date += timedelta(days=1)

    return dates, aqi_values

def get_aqi_color(aqi_value):
    """Return the color code for an AQI value."""
    if aqi_value <= 50:
        return '#006400'  # Dark Green (Good)
    elif aqi_value <= 100:
        return '#228B22'  # Dark Green (Satisfactory)
    elif aqi_value <= 150:
        return '#FFFF00'  # Yellow (Moderate)
    elif aqi_value <= 200:
        return '#8B4513'  # Brown (Unhealthy for Sensitive Groups)
    elif aqi_value <= 300:
        return '#FF0000'  # Red (Unhealthy)
    elif aqi_value <= 400:
        return '#8B008B'  # Purple (Very Unhealthy)
    else:
        return '#800000'  # Maroon (Hazardous)

def get_aqi_category(aqi_value):
    """Return the health category for an AQI value."""
    if aqi_value <= 50:
        return 'Good'
    elif aqi_value <= 100:
        return 'Satisfactory'
    elif aqi_value <= 150:
        return 'Moderate'
    elif aqi_value <= 200:
        return 'Unhealthy for Sensitive Groups'
    elif aqi_value <= 300:
        return 'Unhealthy'
    elif aqi_value <= 400:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

def create_matplotlib_chart(dates, aqi_values, colors):
    """Create a professional matplotlib chart and return as base64 encoded image."""
    # Set up the plot with Times New Roman font and larger bars
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Times New Roman'
    fig, ax = plt.subplots(figsize=(9, 4))  # Slightly larger for bigger bars

    # Convert dates to datetime objects for better formatting
    date_objects = [datetime.strptime(date, "%m/%d/%Y") for date in dates]

    # Create the bar chart with wider bars
    bar_width = 0.8  # Make bars wider
    bars = ax.bar(range(len(aqi_values)), aqi_values, color=colors,
                  edgecolor='black', linewidth=0.5, alpha=0.8, width=bar_width)

    # Highlight today's bar (last one) with thicker border
    if bars:
        bars[-1].set_edgecolor('black')
        bars[-1].set_linewidth(2)

    # Customize the chart with better labels
    current_month = datetime.now().strftime('%B')
    current_year = datetime.now().year
    ax.set_title('AQI Concentration based on PM2.5 - Current Month',
                fontsize=12, fontweight='bold', pad=15, fontname='Times New Roman')
    ax.set_ylabel('AQI Concentration\nbased on PM2.5', fontsize=10, fontweight='bold',
                  rotation=90, fontname='Times New Roman')
    ax.set_xlabel(f'Month of {current_month}, {current_year}', fontsize=10, fontweight='bold',
                  fontname='Times New Roman')

    # Set y-axis limits and remove horizontal grid lines
    ax.set_ylim(0, max(350, max(aqi_values) * 1.1))
    ax.grid(False)  # Remove all grid lines
    ax.set_axisbelow(True)

    # Format x-axis with vertical dates in DD-MM-YYYY format
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([f"{date.split('/')[1]}-{date.split('/')[0]}-{date.split('/')[2]}" for date in dates],
                       rotation=90, ha='center', fontsize=7, fontname='Times New Roman')

    # Add value labels on top of bars for key points
    for i, (bar, value) in enumerate(zip(bars, aqi_values)):
        if i == len(bars) - 1 or value > 100:  # Show label for today and high values
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                   str(int(value)), ha='center', va='bottom', fontsize=8, fontweight='bold',
                   fontname='Times New Roman')

    # Remove AQI level reference lines - user doesn't want them
    # aqi_levels = [
    #     (50, '#006400', 'Good'),
    #     (100, '#228B22', 'Satisfactory'),
    #     (150, '#FFFF00', 'Moderate'),
    #     (200, '#8B4513', 'Unhealthy for Sensitive'),
    #     (300, '#FF0000', 'Unhealthy'),
    #     (400, '#8B008B', 'Very Unhealthy')
    # ]
    #
    # for level, color, label in aqi_levels:
    #     if level <= max(aqi_values) * 1.1:
    #         ax.axhline(y=level, color=color, linestyle='--', alpha=0.6, linewidth=1)

    # Tight layout to maximize space usage
    plt.tight_layout()

    # Convert to base64 string
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    plt.close(fig)  # Important: close the figure to free memory

    return image_base64

def create_plotly_chart(dates, aqi_values, colors):
    """Create a professional plotly chart and return as base64 encoded image."""
    try:
        # Format dates for display
        display_dates = [f"{date.split('/')[1]}-{date.split('/')[0]}-{date.split('/')[2]}" for date in dates]

        # Create the bar chart
        fig = go.Figure()

        # Add bars with custom colors
        fig.add_trace(go.Bar(
            x=display_dates,
            y=aqi_values,
            marker_color=colors,
            marker_line_color='black',
            marker_line_width=1,
            showlegend=False,
            text=[f'{int(val)}' for val in aqi_values],
            textposition='outside',
            textfont=dict(size=10, color='black', family='Times New Roman'),
            hovertemplate='<b>Date:</b> %{x}<br><b>AQI:</b> %{y}<extra></extra>'
        ))

        # Highlight today's bar (last one)
        if len(aqi_values) > 0:
            fig.update_traces(
                marker_line_width=[1] * (len(aqi_values) - 1) + [3],
                marker_line_color=['black'] * (len(aqi_values) - 1) + ['black'],
                selector=dict(type='bar')
            )

        # Update layout
        current_month = datetime.now().strftime('%B')
        current_year = datetime.now().year

        fig.update_layout(
            title=dict(
                text='AQI Concentration based on PM2.5 - Current Month',
                font=dict(size=14, family='Times New Roman', color='black'),
                x=0.5,
                y=0.95
            ),
            xaxis=dict(
                title=dict(
                    text=f'Month of {current_month}, {current_year}',
                    font=dict(size=12, family='Times New Roman', color='black')
                ),
                tickangle=90,
                tickfont=dict(size=10, family='Times New Roman', color='black'),
                showgrid=False
            ),
            yaxis=dict(
                title=dict(
                    text='AQI Concentration based on PM2.5',
                    font=dict(size=12, family='Times New Roman', color='black')
                ),
                range=[0, max(350, max(aqi_values) * 1.1)],
                showgrid=False,
                tickfont=dict(size=10, family='Times New Roman', color='black')
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            width=1000,
            height=500,
            margin=dict(l=80, r=50, t=100, b=120)
        )

        # Convert to base64 string with error handling
        try:
            img_bytes = pio.to_image(fig, format='png', width=1000, height=500, engine='kaleido')
            image_base64 = base64.b64encode(img_bytes).decode()
        except Exception as plotly_error:
            print(f"Plotly kaleido failed: {plotly_error}")
            # Try without specifying engine
            try:
                img_bytes = pio.to_image(fig, format='png', width=1000, height=500)
                image_base64 = base64.b64encode(img_bytes).decode()
            except Exception as plotly_error2:
                print(f"Plotly default engine also failed: {plotly_error2}")
                raise Exception("Both plotly engines failed")

        return image_base64

    except Exception as e:
        print(f"Error creating plotly chart: {e}")
        # Fallback to matplotlib if plotly fails
        print("Falling back to matplotlib chart...")
        return create_matplotlib_chart(dates, aqi_values, colors)

def create_pdf_html_report(pm25_concentration, aqi_value, location, current_date, dates, historical_aqi, colors, current_color):
    """Create HTML report with matplotlib chart for PDF generation - Single Page Layout."""

    # Generate matplotlib chart as base64 image (more reliable for PDF)
    chart_image_base64 = create_matplotlib_chart(dates, historical_aqi, colors)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AQI Report - Rawalpindi</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 15px;
            background-color: #f5f5f5;
            font-size: 11px;
        }}

        .header {{
            text-align: center;
            background-color: white;
            padding: 15px;
            border: 2px solid #000;
            margin-bottom: 15px;
        }}

        .header h1 {{
            margin: 0;
            font-size: 16px;
            font-weight: bold;
            font-family: 'Times New Roman', serif;
        }}

        .header h2 {{
            margin: 8px 0;
            font-size: 12px;
            font-weight: normal;
            font-family: 'Times New Roman', serif;
        }}

        .date {{
            margin-top: 10px;
            font-size: 10px;
            font-family: 'Times New Roman', serif;
        }}

        .data-table {{
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            margin-bottom: 15px;
            border: 2px solid #000;
            font-family: 'Times New Roman', serif;
        }}

        .data-table th,
        .data-table td {{
            border: 1px solid #000;
            padding: 8px 6px;
            text-align: center;
            font-size: 10px;
            font-family: 'Times New Roman', serif;
        }}

        .data-table th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}

        .aqi-value {{
            font-weight: bold;
            font-size: 12px;
            color: #000 !important;
            font-family: 'Times New Roman', serif;
        }}

        .chart-container {{
            background-color: white;
            padding: 20px;
            border: 2px solid #000;
            margin-bottom: 20px;
            text-align: center;
        }}

        .chart-image {{
            max-width: 100%;
            height: auto;
            width: 100%;
        }}

        .content-row {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .ranges-table {{
            flex: 1;
            background-color: white;
            padding: 10px;
            border: 2px solid #000;
            font-family: 'Times New Roman', serif;
        }}

        .ranges-table h3 {{
            text-align: center;
            margin: 0 0 10px 0;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Times New Roman', serif;
        }}

        .ranges-table table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 9px;
            font-family: 'Times New Roman', serif;
        }}

        .ranges-table th,
        .ranges-table td {{
            border: 1px solid #000;
            padding: 4px;
            text-align: center;
            font-family: 'Times New Roman', serif;
        }}

        .ranges-table th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}

        .notes {{
            flex: 1;
            background-color: white;
            padding: 10px;
            border: 2px solid #000;
            font-size: 9px;
            line-height: 1.3;
            font-family: 'Times New Roman', serif;
        }}

        .notes p {{
            margin: 3px 0;
            font-family: 'Times New Roman', serif;
        }}

        .notes h4 {{
            margin: 0 0 5px 0;
            font-size: 10px;
            font-family: 'Times New Roman', serif;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AIR QUALITY INDEX (AQI) OF DISTRICT RAWALPINDI</h1>
        <h2>(Monitored by EPA Lab, Rawalpindi)</h2>
        <div class="date">
            <strong>{current_date}</strong><br>
            <strong>(BASED ON PREVIOUS 24 HOURS DATA)</strong>
        </div>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>Location</th>
                <th>Parameter used to calculate AQI</th>
                <th>PEQS value</th>
                <th>Conc. (&micro;g/m&sup3;) used to calculate AQI</th>
                <th>AQI-PM&#8322;.&#8325; &micro;g/m&sup3;</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{location}</td>
                <td>PM&#8322;.&#8325;</td>
                <td>35</td>
                <td>{pm25_concentration:.1f}</td>
                <td class="aqi-value">{aqi_value}</td>
            </tr>
        </tbody>
    </table>

    <div class="chart-container">
        <img src="data:image/png;base64,{chart_image_base64}" alt="AQI Chart" class="chart-image">
    </div>

    <div style="text-align: center; margin: 20px 0;">
        <h3 style="font-family: 'Times New Roman', serif; font-size: 14px; font-weight: bold; margin: 0;">AQI Limits of EPA, Punjab</h3>
    </div>

    <div style="text-align: center; margin: 20px 0;">
        <table style="margin: 0 auto; border-collapse: collapse; border: 2px solid #000; font-family: 'Times New Roman', serif; font-size: 10px;">
            <thead>
                <tr>
                    <th style="border: 1px solid #000; padding: 6px; background: #f0f0f0; font-weight: bold;">AQI Range</th>
                    <th style="border: 1px solid #000; padding: 6px; background: #f0f0f0; font-weight: bold;">Health Category</th>
                    <th style="border: 1px solid #000; padding: 6px; background: #f0f0f0; font-weight: bold;">Color Code</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">0-50</td>
                    <td style="border: 1px solid #000; padding: 6px;">Good</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #006400; color: #fff; font-weight: bold; text-align: center;">Dark Green</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">51-100</td>
                    <td style="border: 1px solid #000; padding: 6px;">Satisfactory</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #228B22; color: #fff; font-weight: bold; text-align: center;">Dark Green</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">101-150</td>
                    <td style="border: 1px solid #000; padding: 6px;">Moderate</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #FFFF00; color: #000; font-weight: bold; text-align: center;">Yellow</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">151-200</td>
                    <td style="border: 1px solid #000; padding: 6px;">Unhealthy for Sensitive Groups</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #8B4513; color: #fff; font-weight: bold; text-align: center;">Brown</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">201-300</td>
                    <td style="border: 1px solid #000; padding: 6px;">Unhealthy</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #FF0000; color: #fff; font-weight: bold; text-align: center;">Red</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">301-400</td>
                    <td style="border: 1px solid #000; padding: 6px;">Very Unhealthy</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #8B008B; color: #fff; font-weight: bold; text-align: center;">Purple</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #000; padding: 6px; text-align: center;">401-500</td>
                    <td style="border: 1px solid #000; padding: 6px;">Hazardous</td>
                    <td style="border: 1px solid #000; padding: 6px; background: #800000; color: #fff; font-weight: bold; text-align: center;">Maroon</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div style="text-align: center; margin: 15px 0; font-family: 'Times New Roman', serif; font-size: 10px; line-height: 1.4;">
        <p style="margin: 5px 0;"><strong>Note:</strong></p>
        <p style="margin: 3px 0;">i. AQI report based on PM&#8322;.&#8325; measured by using Air-Metric SPM Sampler</p>
        <p style="margin: 3px 0;">ii. Breakpoints used as proposed/adopted by EPA 2024</p>
    </div>
</body>
</html>"""

    return html_content

def save_report(pm25_concentration, aqi_value, filename="aqi_report.html"):
    """Save the HTML report to a file."""
    html_content = create_html_report(pm25_concentration, aqi_value)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return filename

def save_pdf_report(pm25_concentration, aqi_value, filename="aqi_report.pdf"):
    """Save the PDF report by converting HTML with static chart to PDF."""
    # Use HTML with static chart for PDF
    html_content = create_html_report(pm25_concentration, aqi_value, for_pdf=True)

    # Convert HTML to PDF using weasyprint
    html_doc = weasyprint.HTML(string=html_content)
    html_doc.write_pdf(filename)

    return filename

def create_html_report(pm25_concentration, aqi_value, location="Divisional Environmental Complex & Monitoring Center, Adyala Road, Rawalpindi", for_pdf=False):
    """Create a professional HTML report matching the EPA format using template files."""

    # Get current date
    current_date = datetime.now().strftime('%A %B %d, %Y')

    # Generate monthly historical data
    dates, historical_aqi = generate_monthly_data(current_aqi=aqi_value)

    # Create JavaScript arrays for the chart
    dates_js = str(dates).replace("'", '"')
    aqi_js = str(historical_aqi)

    # Generate background colors for chart bars
    colors = [get_aqi_color(val) for val in historical_aqi]
    colors_js = str(colors).replace("'", '"')

    # Get AQI color for the current value
    current_color = get_aqi_color(aqi_value)

    if for_pdf:
        # Create static chart for PDF
        return create_pdf_html_report(pm25_concentration, aqi_value, location, current_date, dates, historical_aqi, colors, current_color)

    # Read the HTML template
    template_path = os.path.join(os.path.dirname(__file__), 'report_template.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        # Fallback to inline HTML if template not found
        return create_fallback_html(pm25_concentration, aqi_value, location, current_date, dates_js, aqi_js, colors_js, current_color)

    # Replace placeholders in the template
    html_content = html_content.replace('{current_date}', current_date)
    html_content = html_content.replace('{location}', location)
    html_content = html_content.replace('{pm25_concentration:.1f}', f'{pm25_concentration:.1f}')
    html_content = html_content.replace('{aqi_value}', str(aqi_value))
    html_content = html_content.replace('{current_color}', current_color)
    html_content = html_content.replace('{dates_js}', dates_js)
    html_content = html_content.replace('{aqi_js}', aqi_js)
    html_content = html_content.replace('{colors_js}', colors_js)

    # Also replace placeholders in the included script.js content
    html_content = html_content.replace('{dates_js}', dates_js)
    html_content = html_content.replace('{aqi_js}', aqi_js)
    html_content = html_content.replace('{colors_js}', colors_js)

    return html_content

def create_fallback_html(pm25_concentration, aqi_value, location, current_date, dates_js, aqi_js, colors_js, current_color):
    """Fallback HTML generation if template file is not found."""
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AQI Report - Rawalpindi</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: white;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 18px;
            font-weight: bold;
            margin: 5px 0;
        }}
        .header h2 {{
            font-size: 16px;
            margin: 5px 0;
        }}
        .date {{
            font-size: 14px;
            margin: 10px 0;
        }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .data-table th, .data-table td {{
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }}
        .data-table th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        .chart-container {{
            margin: 30px 0;
            height: 400px;
        }}
        .notes {{
            margin-top: 20px;
            font-size: 12px;
        }}
        .notes p {{
            margin: 5px 0;
        }}
        .aqi-value {{
            font-size: 24px;
            font-weight: bold;
            color: {current_color};
        }}
        .print-button {{
            margin: 20px 0;
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }}
        .print-button:hover {{
            background: #0056b3;
        }}
        @media print {{
            .print-button {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <button class="print-button" onclick="window.print()">Print Report</button>

    <div class="header">
        <h1>AIR QUALITY INDEX (AQI) OF DISTRICT RAWALPINDI</h1>
        <h2>(Monitored by EPA Lab, Rawalpindi)</h2>
        <div class="date">
            <strong>{current_date}</strong><br>
            <strong>(BASED ON PREVIOUS 24 HOURS DATA)</strong>
        </div>
    </div>

    <table class="data-table">
        <thead>
            <tr>
                <th>Location</th>
                <th>Parameter used to calculate AQI</th>
                <th>PEQS value</th>
                <th>Conc. (ug/m3) used to calculate AQI</th>
                <th>AQI-PM2.5 ug/m3</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>{location}</td>
                <td>PM2.5</td>
                <td>35</td>
                <td>{pm25_concentration:.1f}</td>
                <td class="aqi-value">{aqi_value}</td>
            </tr>
        </tbody>
    </table>

    <div class="chart-container">
        <canvas id="aqiChart"></canvas>
    </div>

    <!-- AQI Limits Diagram -->
    <div style="margin: 30px 0;">
        <h3 style="text-align: center; margin-bottom: 20px;">AQI Health Categories and Limits</h3>
        <div style="display: flex; justify-content: center;">
            <table style="border-collapse: collapse; border: 2px solid #000;">
                <thead>
                    <tr>
                        <th style="border: 1px solid #000; padding: 10px; background: #f0f0f0; font-weight: bold;">AQI Range</th>
                        <th style="border: 1px solid #000; padding: 10px; background: #f0f0f0; font-weight: bold;">Health Category</th>
                        <th style="border: 1px solid #000; padding: 10px; background: #f0f0f0; font-weight: bold;">Color Code</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">0-50</td>
                        <td style="border: 1px solid #000; padding: 10px;">Good</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #006400; color: #fff; text-align: center; font-weight: bold;">Dark Green</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">51-100</td>
                        <td style="border: 1px solid #000; padding: 10px;">Satisfactory</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #228B22; color: #fff; text-align: center; font-weight: bold;">Dark Green</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">101-150</td>
                        <td style="border: 1px solid #000; padding: 10px;">Moderate</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #FFFF00; color: #000; text-align: center; font-weight: bold;">Yellow</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">151-200</td>
                        <td style="border: 1px solid #000; padding: 10px;">Unhealthy for Sensitive Groups</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #8B4513; color: #fff; text-align: center; font-weight: bold;">Brown</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">201-300</td>
                        <td style="border: 1px solid #000; padding: 10px;">Unhealthy</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #FF0000; color: #fff; text-align: center; font-weight: bold;">Red</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">301-400</td>
                        <td style="border: 1px solid #000; padding: 10px;">Very Unhealthy</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #8B008B; color: #fff; text-align: center; font-weight: bold;">Purple</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #000; padding: 10px; text-align: center;">401-500</td>
                        <td style="border: 1px solid #000; padding: 10px;">Hazardous</td>
                        <td style="border: 1px solid #000; padding: 10px; background: #800000; color: #fff; text-align: center; font-weight: bold;">Maroon</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <div class="notes">
        <p><strong>Note:</strong></p>
        <p>i. AQI report based on PM2.5 measured by using Air-Metric SPM Sampler</p>
        <p>ii. Breakpoints used as proposed/adopted by EPA 2024</p>
    </div>

    <script>
        // AQI data for the current month
        const dates = {dates_js};
        const aqiValues = {aqi_js};

        // Create gradient colors based on AQI levels
        const getAQIColor = (value) => {{
            if (value <= 50) return '#006400';      // Good (Dark Green)
            if (value <= 100) return '#228B22';    // Satisfactory (Dark Green)
            if (value <= 150) return '#FFFF00';    // Moderate (Yellow)
            if (value <= 200) return '#8B4513';    // Unhealthy for Sensitive Groups (Brown)
            if (value <= 300) return '#FF0000';    // Unhealthy (Red)
            if (value <= 400) return '#8B008B';    // Very Unhealthy (Purple)
            return '#800000';                       // Hazardous (Maroon)
        }};

        const backgroundColors = {colors_js};

        const ctx = document.getElementById('aqiChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'bar',
            data: {{
                labels: dates,
                datasets: [{{
                    label: 'AQI Concentration based on PM2.5',
                    data: aqiValues,
                    backgroundColor: backgroundColors,
                    borderColor: '#333',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'AQI Concentration based on PM2.5 - Current Month',
                        font: {{
                            size: 14,
                            weight: 'bold'
                        }}
                    }},
                    legend: {{
                        display: false
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const aqi = context.parsed.y;
                                let category = 'Good';
                                if (aqi <= 50) category = 'Good';
                                else if (aqi <= 100) category = 'Satisfactory';
                                else if (aqi <= 150) category = 'Moderate';
                                else if (aqi <= 200) category = 'Unhealthy for Sensitive Groups';
                                else if (aqi <= 300) category = 'Unhealthy';
                                else if (aqi <= 400) category = 'Very Unhealthy';
                                else category = 'Hazardous';
                                return `AQI: ${{aqi}} (${{category}})`;
                            }}
                        }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 500,
                        title: {{
                            display: true,
                            text: 'AQI Value'
                        }},
                        grid: {{
                            color: '#e0e0e0'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return value;
                            }}
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: 'Date (MM/DD/YYYY)'
                        }},
                        ticks: {{
                            maxRotation: 45,
                            font: {{
                                size: 10
                            }}
                        }},
                        grid: {{
                            display: false
                        }}
                    }}
                }},
                elements: {{
                    bar: {{
                        borderRadius: 3,
                        borderSkipped: false
                    }}
                }},
                interaction: {{
                    intersect: false,
                    mode: 'index'
                }}
            }}
        }});

        // Highlight today's bar (last bar)
        setTimeout(() => {{
            const meta = chart.getDatasetMeta(0);
            const lastBar = meta.data[meta.data.length - 1];
            if (lastBar) {{
                lastBar.options.borderColor = '#000';
                lastBar.options.borderWidth = 3;
                chart.update();
            }}
        }}, 100);
    </script>
</body>
</html>"""

    return html_content
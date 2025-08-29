// AQI data for the current month
const dates = {dates_js};
const aqiValues = {aqi_js};

// Create gradient colors based on AQI levels
const getAQIColor = (value) => {
    if (value <= 50) return '#00E400';      // Good (Green)
    if (value <= 100) return '#FFFF00';    // Moderate (Yellow)
    if (value <= 150) return '#FF7E00';    // Unhealthy for Sensitive Groups (Orange)
    if (value <= 200) return '#FF0000';    // Unhealthy (Red)
    if (value <= 300) return '#8F3F97';    // Very Unhealthy (Purple)
    return '#7E0023';                       // Hazardous (Maroon)
};

const backgroundColors = {colors_js};

const ctx = document.getElementById('aqiChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: dates,
        datasets: [{
            label: 'AQI Concentration based on PM2.5',
            data: aqiValues,
            backgroundColor: backgroundColors,
            borderColor: '#333',
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: true,
                text: 'AQI Concentration based on PM2.5 - Current Month',
                font: {
                    size: 14,
                    weight: 'bold'
                }
            },
            legend: {
                display: false
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const aqi = context.parsed.y;
                        let category = 'Good';
                        if (aqi <= 50) category = 'Good';
                        else if (aqi <= 100) category = 'Moderate';
                        else if (aqi <= 150) category = 'Unhealthy for Sensitive Groups';
                        else if (aqi <= 200) category = 'Unhealthy';
                        else if (aqi <= 300) category = 'Very Unhealthy';
                        else category = 'Hazardous';
                        return `AQI: ${aqi} (${category})`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 350,
                title: {
                    display: true,
                    text: 'AQI Value'
                },
                grid: {
                    color: '#e0e0e0'
                },
                ticks: {
                    callback: function(value) {
                        return value;
                    }
                }
            },
            x: {
                title: {
                    display: true,
                    text: 'Date (MM/DD/YYYY)'
                },
                ticks: {
                    maxRotation: 45,
                    font: {
                        size: 10
                    }
                },
                grid: {
                    display: false
                }
            }
        },
        elements: {
            bar: {
                borderRadius: 3,
                borderSkipped: false
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        }
    }
});

// Highlight today's bar (last bar)
setTimeout(() => {
    const meta = chart.getDatasetMeta(0);
    const lastBar = meta.data[meta.data.length - 1];
    if (lastBar) {
        lastBar.options.borderColor = '#000';
        lastBar.options.borderWidth = 3;
        chart.update();
    }
}, 100);
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExcelManager:
    """Manages Excel file operations for AQI data export and import."""
    
    def __init__(self):
        pass
    
    def export_to_excel(self, data: List[Dict], filename: str = None) -> str:
        """Export data to Excel file with two sheets: PM2.5-conc and AQI."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"AQI_Data_Export_{timestamp}.xlsx"
        
        try:
            # Prepare data for PM2.5-conc sheet
            pm25_data = []
            for record in data:
                pm25_data.append({
                    'Date': record['date'].strftime('%Y-%m-%d'),
                    'Initial Mass (mg)': record['initial_mass'],
                    'Final Mass (mg)': record['final_mass'],
                    'Flow Rate (L/min)': record['flow_rate'],
                    'Start Time (min)': record['start_time'],
                    'Stop Time (min)': record['stop_time']
                })
            
            # Prepare data for AQI sheet
            aqi_data = []
            for record in data:
                aqi_data.append({
                    'Date': record['date'].strftime('%Y-%m-%d'),
                    'Concentration (μg/m³)': round(record['concentration'], 1),
                    'AQI Value': record['aqi_value'],
                    'Category': record['category']
                })
            
            # Create DataFrames
            pm25_df = pd.DataFrame(pm25_data)
            aqi_df = pd.DataFrame(aqi_data)
            
            # Write to Excel with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                pm25_df.to_excel(writer, sheet_name='PM2.5-conc', index=False)
                aqi_df.to_excel(writer, sheet_name='AQI', index=False)
                
                # Auto-adjust column widths
                for sheet_name in ['PM2.5-conc', 'AQI']:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Data exported successfully to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            raise
    
    def import_from_excel(self, filename: str) -> Tuple[List[Dict], List[str]]:
        """Import data from Excel file. Returns (data, errors)."""
        data = []
        errors = []
        
        try:
            if not Path(filename).exists():
                errors.append(f"File not found: {filename}")
                return data, errors
            
            # Read both sheets
            try:
                pm25_df = pd.read_excel(filename, sheet_name='PM2.5-conc')
                aqi_df = pd.read_excel(filename, sheet_name='AQI')
            except Exception as e:
                errors.append(f"Error reading Excel sheets: {e}")
                return data, errors
            
            # Validate required columns
            pm25_required = ['Date', 'Initial Mass (mg)', 'Final Mass (mg)', 
                           'Flow Rate (L/min)', 'Start Time (min)', 'Stop Time (min)']
            aqi_required = ['Date', 'Concentration (μg/m³)', 'AQI Value', 'Category']
            
            pm25_missing = [col for col in pm25_required if col not in pm25_df.columns]
            aqi_missing = [col for col in aqi_required if col not in aqi_df.columns]
            
            if pm25_missing:
                errors.append(f"Missing columns in PM2.5-conc sheet: {pm25_missing}")
            if aqi_missing:
                errors.append(f"Missing columns in AQI sheet: {aqi_missing}")
            
            if errors:
                return data, errors
            
            # Merge data by date
            pm25_dict = {}
            for _, row in pm25_df.iterrows():
                try:
                    date_str = str(row['Date'])
                    if pd.isna(row['Date']):
                        continue
                    
                    # Handle different date formats
                    if isinstance(row['Date'], str):
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        date_obj = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
                    
                    pm25_dict[date_obj] = {
                        'initial_mass': float(row['Initial Mass (mg)']),
                        'final_mass': float(row['Final Mass (mg)']),
                        'flow_rate': float(row['Flow Rate (L/min)']),
                        'start_time': float(row['Start Time (min)']),
                        'stop_time': float(row['Stop Time (min)'])
                    }
                except Exception as e:
                    errors.append(f"Error processing PM2.5 row {_}: {e}")
            
            # Process AQI data and merge
            for _, row in aqi_df.iterrows():
                try:
                    date_str = str(row['Date'])
                    if pd.isna(row['Date']):
                        continue
                    
                    # Handle different date formats
                    if isinstance(row['Date'], str):
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    else:
                        date_obj = row['Date'].date() if hasattr(row['Date'], 'date') else row['Date']
                    
                    if date_obj in pm25_dict:
                        record = pm25_dict[date_obj].copy()
                        record.update({
                            'date': date_obj,
                            'concentration': float(row['Concentration (μg/m³)']),
                            'aqi_value': int(row['AQI Value']),
                            'category': str(row['Category'])
                        })
                        data.append(record)
                    else:
                        errors.append(f"No PM2.5 data found for date: {date_obj}")
                        
                except Exception as e:
                    errors.append(f"Error processing AQI row {_}: {e}")
            
            logger.info(f"Imported {len(data)} records from {filename}")
            if errors:
                logger.warning(f"Import completed with {len(errors)} errors")
            
            return data, errors
            
        except Exception as e:
            logger.error(f"Error importing from Excel: {e}")
            errors.append(f"General import error: {e}")
            return data, errors
    
    def validate_data(self, data: List[Dict]) -> List[str]:
        """Validate imported data for consistency."""
        errors = []
        
        for i, record in enumerate(data):
            try:
                # Check required fields
                required_fields = ['date', 'initial_mass', 'final_mass', 'flow_rate', 
                                 'start_time', 'stop_time', 'concentration', 'aqi_value', 'category']
                
                missing_fields = [field for field in required_fields if field not in record]
                if missing_fields:
                    errors.append(f"Record {i+1}: Missing fields {missing_fields}")
                    continue
                
                # Validate data types and ranges
                if record['flow_rate'] <= 0:
                    errors.append(f"Record {i+1}: Flow rate must be positive")
                
                if record['stop_time'] <= record['start_time']:
                    errors.append(f"Record {i+1}: Stop time must be greater than start time")
                
                if record['concentration'] < 0:
                    errors.append(f"Record {i+1}: Concentration cannot be negative")
                
                if not (0 <= record['aqi_value'] <= 500):
                    errors.append(f"Record {i+1}: AQI value must be between 0 and 500")
                
                # Validate AQI category
                valid_categories = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 
                                 'Unhealthy', 'Very Unhealthy', 'Hazardous']
                if record['category'] not in valid_categories:
                    errors.append(f"Record {i+1}: Invalid category '{record['category']}'")
                
            except Exception as e:
                errors.append(f"Record {i+1}: Validation error - {e}")
        
        return errors
    
    def create_template_excel(self, filename: str = "AQI_Data_Template.xlsx") -> str:
        """Create a template Excel file for data import."""
        try:
            # Sample data for template
            pm25_template = pd.DataFrame({
                'Date': ['2025-08-01', '2025-08-02'],
                'Initial Mass (mg)': [100.0, 105.2],
                'Final Mass (mg)': [102.5, 108.1],
                'Flow Rate (L/min)': [16.7, 16.7],
                'Start Time (min)': [0.0, 0.0],
                'Stop Time (min)': [1440.0, 1440.0]
            })
            
            aqi_template = pd.DataFrame({
                'Date': ['2025-08-01', '2025-08-02'],
                'Concentration (μg/m³)': [28.5, 35.2],
                'AQI Value': [83, 98],
                'Category': ['Moderate', 'Moderate']
            })
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                pm25_template.to_excel(writer, sheet_name='PM2.5-conc', index=False)
                aqi_template.to_excel(writer, sheet_name='AQI', index=False)
                
                # Auto-adjust column widths
                for sheet_name in ['PM2.5-conc', 'AQI']:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Template created: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise

# Global instance
excel_manager = ExcelManager()
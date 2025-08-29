import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.filechooser import FileChooserListView
from datetime import datetime, date
import webbrowser
import os
import math

# Import from your modules
from aqi_calculator import calculate_pm25_concentration, calculate_aqi, get_aqi_category
from report_generator import save_report, save_pdf_report
from database_manager import db_manager
from excel_manager import excel_manager

try:
    from plyer import filechooser
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("Plyer not available - file chooser will use Kivy's built-in FileChooser")

class AQIColorBar(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aqi_value = 0
        self.category = "Good"
        self.color = (0, 1, 0, 1)  # Green
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        
    def update_graphics(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(*self.color)
            Rectangle(pos=self.pos, size=self.size)
    
    def update_aqi(self, aqi_value):
        self.aqi_value = aqi_value
        self.category, self.color = get_aqi_category(aqi_value)
        self.update_graphics()

class AQIApp(App):
    def build(self):
        Window.size = (450, 900)
        
        # Create a scrollable main layout
        scroll = ScrollView()
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Title
        title = Label(text='PM2.5 AQI Calculator', font_size=24, size_hint_y=None, height=50)
        main_layout.add_widget(title)
        
        # Input fields
        input_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=250)
        
        # Flow rate
        input_layout.add_widget(Label(text='Flow Rate (L/min):'))
        self.flow_rate_input = TextInput(multiline=False, input_filter='float')
        input_layout.add_widget(self.flow_rate_input)
        
        # Initial filter mass
        input_layout.add_widget(Label(text='Initial Mass (mg):'))
        self.initial_mass_input = TextInput(multiline=False, input_filter='float')
        input_layout.add_widget(self.initial_mass_input)
        
        # Final filter mass
        input_layout.add_widget(Label(text='Final Mass (mg):'))
        self.final_mass_input = TextInput(multiline=False, input_filter='float')
        input_layout.add_widget(self.final_mass_input)
        
        # Start time
        input_layout.add_widget(Label(text='Start Time (min):'))
        self.start_time_input = TextInput(multiline=False, input_filter='float')
        input_layout.add_widget(self.start_time_input)
        
        # Stop time
        input_layout.add_widget(Label(text='Stop Time (min):'))
        self.stop_time_input = TextInput(multiline=False, input_filter='float')
        input_layout.add_widget(self.stop_time_input)
        
        main_layout.add_widget(input_layout)
        
        # Calculate button
        calc_button = Button(text='Calculate AQI', size_hint_y=None, height=50)
        calc_button.bind(on_press=self.calculate_aqi)
        main_layout.add_widget(calc_button)
        
        # Results section
        results_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None, height=200)
        
        # PM2.5 concentration result
        self.pm25_result = Label(text='PM2.5: -- µg/m³', font_size=18)
        results_layout.add_widget(self.pm25_result)
        
        # AQI result
        self.aqi_result = Label(text='AQI: --', font_size=20)
        results_layout.add_widget(self.aqi_result)
        
        # Health category
        self.category_result = Label(text='Category: --', font_size=16)
        results_layout.add_widget(self.category_result)
        
        main_layout.add_widget(results_layout)
        
        # Color bar
        self.color_bar = AQIColorBar(size_hint_y=None, height=50)
        main_layout.add_widget(self.color_bar)
        
        # Generate HTML report button
        html_report_button = Button(text="Generate HTML Report", size_hint_y=None, height=50)
        html_report_button.bind(on_press=self.generate_html_report)
        main_layout.add_widget(html_report_button)

        # Generate PDF report button
        pdf_report_button = Button(text="Generate PDF Report", size_hint_y=None, height=50)
        pdf_report_button.bind(on_press=self.generate_pdf_report)
        main_layout.add_widget(pdf_report_button)

        # Export to Excel button
        excel_export_button = Button(text="Export Data to Excel", size_hint_y=None, height=50)
        excel_export_button.bind(on_press=self.export_to_excel)
        main_layout.add_widget(excel_export_button)

        # Update/Edit Data button
        update_data_button = Button(text="Update/Edit Data", size_hint_y=None, height=50)
        update_data_button.bind(on_press=self.update_data)
        main_layout.add_widget(update_data_button)
        
        # Add main layout to scroll view
        scroll.add_widget(main_layout)
        return scroll
    
    def calculate_aqi(self, instance):
        try:
            # Get input values with better error handling
            flow_rate_text = self.flow_rate_input.text.strip()
            initial_mass_text = self.initial_mass_input.text.strip()
            final_mass_text = self.final_mass_input.text.strip()
            start_time_text = self.start_time_input.text.strip()
            stop_time_text = self.stop_time_input.text.strip()
            
            # Check if any field is empty
            if not all([flow_rate_text, initial_mass_text, final_mass_text, start_time_text, stop_time_text]):
                popup = Popup(title='Error', content=Label(text='Please fill in all fields'), size_hint=(0.8, 0.4))
                popup.open()
                return
            
            # Convert to float
            flow_rate = float(flow_rate_text)
            initial_mass = float(initial_mass_text)
            final_mass = float(final_mass_text)
            start_time = float(start_time_text)
            stop_time = float(stop_time_text)
            
            # Validate inputs
            if flow_rate <= 0:
                popup = Popup(title='Error', content=Label(text='Flow rate must be greater than 0'), size_hint=(0.8, 0.4))
                popup.open()
                return
                
            if stop_time <= start_time:
                popup = Popup(title='Error', content=Label(text='Stop time must be greater than start time'), size_hint=(0.8, 0.4))
                popup.open()
                return
                
            if final_mass < initial_mass:
                popup = Popup(title='Warning', content=Label(text='Final mass is less than initial mass.\nThis may indicate an error in measurement.'), size_hint=(0.8, 0.4))
                popup.open()
            
            # Debug print
            print(f"Inputs - Flow rate: {flow_rate}, Initial mass: {initial_mass}, Final mass: {final_mass}")
            print(f"Times - Start: {start_time}, Stop: {stop_time}")
            
            # Calculate PM2.5 concentration
            pm25_conc = calculate_pm25_concentration(initial_mass, final_mass, flow_rate, start_time, stop_time)
            print(f"PM2.5 concentration: {pm25_conc}")
            
            # Calculate AQI
            aqi_value = calculate_aqi(pm25_conc)
            print(f"AQI value: {aqi_value}")
            
            category, color = get_aqi_category(aqi_value)
            print(f"Category: {category}, Color: {color}")
            
            # Update results
            self.pm25_result.text = f'PM2.5: {pm25_conc:.1f} µg/m³'
            self.aqi_result.text = f'AQI: {aqi_value}'
            self.category_result.text = f'Category: {category}'
            
            # Update color bar
            self.color_bar.update_aqi(aqi_value)
            
            # Store values for report generation
            self.current_pm25 = pm25_conc
            self.current_aqi = aqi_value
            self.current_category = category
            
            # Save to database
            try:
                today = date.today()
                success = db_manager.save_measurement(
                    date_val=today,
                    initial_mass=initial_mass,
                    final_mass=final_mass,
                    flow_rate=flow_rate,
                    start_time=start_time,
                    stop_time=stop_time,
                    concentration=pm25_conc,
                    aqi_value=aqi_value,
                    category=category
                )
                if success:
                    print(f"Data saved to database for {today}")
                else:
                    print("Failed to save data to database")
            except Exception as db_error:
                print(f"Database error: {db_error}")
            
        except ValueError as e:
            print(f"ValueError: {e}")
            popup = Popup(title='Error', content=Label(text='Please enter valid numbers'), size_hint=(0.8, 0.4))
            popup.open()
        except Exception as e:
            print(f"Unexpected error: {e}")
            popup = Popup(title='Error', content=Label(text=f'An error occurred: {str(e)}'), size_hint=(0.8, 0.4))
            popup.open()
    
    def generate_html_report(self, instance):
        if not hasattr(self, 'current_aqi'):
            popup = Popup(title='Error', content=Label(text='Please calculate AQI first'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        try:
            # Generate HTML report
            filename = save_report(self.current_pm25, self.current_aqi)
            
            # Show success popup
            popup = Popup(title='Success', content=Label(text=f'HTML Report generated!\nCheck {filename}'), size_hint=(0.8, 0.4))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Error generating HTML report: {str(e)}'), size_hint=(0.8, 0.4))
            popup.open()

    def generate_pdf_report(self, instance):
        if not hasattr(self, 'current_aqi'):
            popup = Popup(title='Error', content=Label(text='Please calculate AQI first'), size_hint=(0.8, 0.4))
            popup.open()
            return
        
        try:
            # Generate PDF report
            filename = save_pdf_report(self.current_pm25, self.current_aqi)
            
            popup = Popup(title='Success', content=Label(text=f'PDF Report generated!\nCheck {filename}'), size_hint=(0.8, 0.4))
            popup.open()
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Error generating PDF report: {str(e)}'), size_hint=(0.8, 0.4))
            popup.open()

    def export_to_excel(self, instance):
        """Export all stored data to Excel file."""
        try:
            # Get all data from database
            data = db_manager.get_all_data()
            
            if not data:
                popup = Popup(title='No Data', content=Label(text='No data available to export'), size_hint=(0.8, 0.4))
                popup.open()
                return
            
            # Export to Excel
            filename = excel_manager.export_to_excel(data)
            
            popup = Popup(title='Success', content=Label(text=f'Data exported successfully!\nFile: {filename}'), size_hint=(0.8, 0.4))
            popup.open()
            
        except Exception as e:
            popup = Popup(title='Error', content=Label(text=f'Error exporting data: {str(e)}'), size_hint=(0.8, 0.4))
            popup.open()

    def update_data(self, instance):
        """Open file chooser to import/update data from Excel file."""
        if PLYER_AVAILABLE:
            try:
                # Use plyer for better mobile support
                filechooser.open_file(on_selection=self.import_data_callback,
                                    filters=[("Excel files", "*.xlsx"), ("All files", "*")])
            except Exception as e:
                print(f"Plyer filechooser error: {e}")
                self.show_kivy_file_chooser()
        else:
            self.show_kivy_file_chooser()

    def show_kivy_file_chooser(self):
        """Show Kivy's built-in file chooser."""
        content = BoxLayout(orientation='vertical')
        
        filechooser = FileChooserListView()
        filechooser.filters = ['*.xlsx']
        content.add_widget(filechooser)
        
        buttons = BoxLayout(size_hint_y=None, height=50)
        
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        
        buttons.add_widget(select_btn)
        buttons.add_widget(cancel_btn)
        content.add_widget(buttons)
        
        popup = Popup(title='Select Excel File', content=content, size_hint=(0.9, 0.9))
        
        def select_file(btn):
            if filechooser.selection:
                self.import_data_callback(filechooser.selection)
            popup.dismiss()
        
        def cancel_selection(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=select_file)
        cancel_btn.bind(on_press=cancel_selection)
        
        popup.open()

    def import_data_callback(self, selection):
        """Callback for file selection - import data from Excel."""
        if not selection:
            return
        
        filename = selection[0] if isinstance(selection, list) else selection
        
        try:
            # Import data from Excel
            data, errors = excel_manager.import_from_excel(filename)
            
            if errors:
                error_text = "Import completed with errors:\n" + "\n".join(errors[:5])
                if len(errors) > 5:
                    error_text += f"\n... and {len(errors) - 5} more errors"
                
                popup = Popup(title='Import Warnings',
                            content=Label(text=error_text),
                            size_hint=(0.8, 0.6))
                popup.open()
            
            if not data:
                popup = Popup(title='No Data', content=Label(text='No valid data found in file'), size_hint=(0.8, 0.4))
                popup.open()
                return
            
            # Validate data
            validation_errors = excel_manager.validate_data(data)
            if validation_errors:
                error_text = "Data validation errors:\n" + "\n".join(validation_errors[:5])
                if len(validation_errors) > 5:
                    error_text += f"\n... and {len(validation_errors) - 5} more errors"
                
                popup = Popup(title='Validation Errors',
                            content=Label(text=error_text),
                            size_hint=(0.8, 0.6))
                popup.open()
                return
            
            # Save data to database
            success_count = 0
            for record in data:
                success = db_manager.save_measurement(
                    date_val=record['date'],
                    initial_mass=record['initial_mass'],
                    final_mass=record['final_mass'],
                    flow_rate=record['flow_rate'],
                    start_time=record['start_time'],
                    stop_time=record['stop_time'],
                    concentration=record['concentration'],
                    aqi_value=record['aqi_value'],
                    category=record['category']
                )
                if success:
                    success_count += 1
            
            popup = Popup(title='Import Complete',
                        content=Label(text=f'Successfully imported {success_count} records\nfrom {len(data)} total records'),
                        size_hint=(0.8, 0.4))
            popup.open()
            
        except Exception as e:
            popup = Popup(title='Import Error',
                        content=Label(text=f'Error importing data: {str(e)}'),
                        size_hint=(0.8, 0.4))
            popup.open()

if __name__ == '__main__':
    AQIApp().run()
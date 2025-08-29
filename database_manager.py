import sqlite3
import os
from datetime import datetime, date
from typing import List, Tuple, Optional, Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database operations for AQI data storage."""
    
    def __init__(self, db_path: str = "aqi_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create pm25_measurements table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS pm25_measurements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        initial_mass REAL NOT NULL,
                        final_mass REAL NOT NULL,
                        flow_rate REAL NOT NULL,
                        start_time REAL NOT NULL,
                        stop_time REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(date)
                    )
                ''')
                
                # Create aqi_calculations table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS aqi_calculations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        measurement_id INTEGER,
                        date DATE NOT NULL,
                        concentration REAL NOT NULL,
                        aqi_value INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (measurement_id) REFERENCES pm25_measurements (id),
                        UNIQUE(date)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def save_measurement(self, date_val: date, initial_mass: float, final_mass: float, 
                        flow_rate: float, start_time: float, stop_time: float,
                        concentration: float, aqi_value: int, category: str) -> bool:
        """Save measurement data and calculated AQI to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or replace measurement data
                cursor.execute('''
                    INSERT OR REPLACE INTO pm25_measurements 
                    (date, initial_mass, final_mass, flow_rate, start_time, stop_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (date_val, initial_mass, final_mass, flow_rate, start_time, stop_time))
                
                measurement_id = cursor.lastrowid
                
                # Insert or replace AQI calculation
                cursor.execute('''
                    INSERT OR REPLACE INTO aqi_calculations 
                    (measurement_id, date, concentration, aqi_value, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (measurement_id, date_val, concentration, aqi_value, category))
                
                conn.commit()
                logger.info(f"Data saved successfully for date: {date_val}")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error saving measurement: {e}")
            return False
    
    def get_monthly_data(self, year: int, month: int) -> List[Dict]:
        """Get all AQI data for a specific month."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT a.date, a.concentration, a.aqi_value, a.category,
                           m.initial_mass, m.final_mass, m.flow_rate, 
                           m.start_time, m.stop_time
                    FROM aqi_calculations a
                    JOIN pm25_measurements m ON a.measurement_id = m.id
                    WHERE strftime('%Y', a.date) = ? AND strftime('%m', a.date) = ?
                    ORDER BY a.date
                ''', (str(year), f"{month:02d}"))
                
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append({
                        'date': datetime.strptime(row[0], '%Y-%m-%d').date(),
                        'concentration': row[1],
                        'aqi_value': row[2],
                        'category': row[3],
                        'initial_mass': row[4],
                        'final_mass': row[5],
                        'flow_rate': row[6],
                        'start_time': row[7],
                        'stop_time': row[8]
                    })
                
                logger.info(f"Retrieved {len(data)} records for {year}-{month:02d}")
                return data
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving monthly data: {e}")
            return []
    
    def get_current_month_data(self) -> List[Dict]:
        """Get AQI data for the current month."""
        now = datetime.now()
        return self.get_monthly_data(now.year, now.month)
    
    def update_aqi_value(self, date_val: date, new_aqi: int, new_category: str) -> bool:
        """Update AQI value for a specific date."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE aqi_calculations 
                    SET aqi_value = ?, category = ?
                    WHERE date = ?
                ''', (new_aqi, new_category, date_val))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Updated AQI for {date_val}: {new_aqi} ({new_category})")
                    return True
                else:
                    logger.warning(f"No record found for date: {date_val}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Error updating AQI value: {e}")
            return False
    
    def delete_record(self, date_val: date) -> bool:
        """Delete records for a specific date."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get measurement_id first
                cursor.execute('SELECT id FROM pm25_measurements WHERE date = ?', (date_val,))
                result = cursor.fetchone()
                
                if result:
                    measurement_id = result[0]
                    
                    # Delete from both tables
                    cursor.execute('DELETE FROM aqi_calculations WHERE measurement_id = ?', (measurement_id,))
                    cursor.execute('DELETE FROM pm25_measurements WHERE id = ?', (measurement_id,))
                    
                    conn.commit()
                    logger.info(f"Deleted records for date: {date_val}")
                    return True
                else:
                    logger.warning(f"No record found for date: {date_val}")
                    return False
                    
        except sqlite3.Error as e:
            logger.error(f"Error deleting record: {e}")
            return False
    
    def get_all_data(self) -> List[Dict]:
        """Get all stored data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT a.date, a.concentration, a.aqi_value, a.category,
                           m.initial_mass, m.final_mass, m.flow_rate, 
                           m.start_time, m.stop_time
                    FROM aqi_calculations a
                    JOIN pm25_measurements m ON a.measurement_id = m.id
                    ORDER BY a.date DESC
                ''')
                
                rows = cursor.fetchall()
                
                data = []
                for row in rows:
                    data.append({
                        'date': datetime.strptime(row[0], '%Y-%m-%d').date(),
                        'concentration': row[1],
                        'aqi_value': row[2],
                        'category': row[3],
                        'initial_mass': row[4],
                        'final_mass': row[5],
                        'flow_rate': row[6],
                        'start_time': row[7],
                        'stop_time': row[8]
                    })
                
                logger.info(f"Retrieved {len(data)} total records")
                return data
                
        except sqlite3.Error as e:
            logger.error(f"Error retrieving all data: {e}")
            return []
    
    def clear_all_data(self) -> bool:
        """Clear all data from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM aqi_calculations')
                cursor.execute('DELETE FROM pm25_measurements')
                
                conn.commit()
                logger.info("All data cleared from database")
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Error clearing data: {e}")
            return False
    
    def close(self):
        """Close database connection (for cleanup if needed)."""
        # SQLite connections are automatically closed when using context manager
        pass

# Singleton instance for global use
db_manager = DatabaseManager()
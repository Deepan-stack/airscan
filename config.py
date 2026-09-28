import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'aerolux-super-secret-key-2026-luxury-aviation')
    
    # MySQL Database Configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'airline_db')
    
    # Force SQLite if MySQL is not available or explicitly chosen
    USE_SQLITE = os.environ.get('USE_SQLITE', 'auto').lower() # 'true', 'false', or 'auto'
    SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'airline.db')

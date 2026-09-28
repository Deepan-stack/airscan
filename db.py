import sqlite3
import socket
import re
from datetime import datetime
from config import Config

# Check if mysql.connector is available
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception

class Database:
    _connection_mode = None # 'mysql' or 'sqlite'

    @classmethod
    def determine_mode(cls):
        if cls._connection_mode:
            return cls._connection_mode

        if Config.USE_SQLITE == 'true':
            cls._connection_mode = 'sqlite'
            return 'sqlite'

        if MYSQL_AVAILABLE and Config.USE_SQLITE in ('auto', 'false'):
            # Ultra-fast socket check to see if port 3306 is actually open
            try:
                with socket.create_connection((Config.MYSQL_HOST, Config.MYSQL_PORT), timeout=0.4):
                    pass
            except (socket.timeout, ConnectionRefusedError, OSError):
                cls._connection_mode = 'sqlite'
                print(f"[DB] MySQL server not reachable at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}. Using SQLite.")
                return 'sqlite'

            try:
                conn = mysql.connector.connect(
                    host=Config.MYSQL_HOST,
                    port=Config.MYSQL_PORT,
                    user=Config.MYSQL_USER,
                    password=Config.MYSQL_PASSWORD,
                    connection_timeout=1
                )
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB} CHARACTER SET utf8mb4;")
                conn.database = Config.MYSQL_DB
                conn.close()
                cls._connection_mode = 'mysql'
                print(f"[DB] Successfully connected to MySQL at {Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}")
                return 'mysql'
            except Exception as e:
                print(f"[DB] MySQL connection skipped/failed ({e}). Falling back to SQLite.")
                cls._connection_mode = 'sqlite'
                return 'sqlite'
        else:
            cls._connection_mode = 'sqlite'
            return 'sqlite'

    @classmethod
    def get_connection(cls):
        mode = cls.determine_mode()
        if mode == 'mysql':
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                autocommit=False
            )
            return conn, 'mysql'
        else:
            conn = sqlite3.connect(Config.SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys for SQLite
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn, 'sqlite'

    @classmethod
    def get_db_info(cls):
        mode = cls.determine_mode()
        if mode == 'mysql':
            return {
                'type': 'MySQL',
                'host': f"{Config.MYSQL_HOST}:{Config.MYSQL_PORT}",
                'database': Config.MYSQL_DB
            }
        else:
            return {
                'type': 'SQLite',
                'host': 'Local File',
                'database': Config.SQLITE_PATH
            }

    @classmethod
    def execute_query(cls, query, params=(), fetch_one=False):
        """
        Executes a SELECT query and returns list of dictionaries (or single dict).
        Handles parameter placeholder normalization (%s for MySQL, ? for SQLite).
        """
        conn, mode = cls.get_connection()
        try:
            if mode == 'sqlite':
                # Convert %s to ? for SQLite
                sql = query.replace('%s', '?')
                cursor = conn.cursor()
                cursor.execute(sql, params)
                if fetch_one:
                    row = cursor.fetchone()
                    return dict(row) if row else None
                else:
                    rows = cursor.fetchall()
                    return [dict(r) for r in rows]
            else:
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, params)
                if fetch_one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
        finally:
            conn.close()

    @classmethod
    def execute_commit(cls, query, params=()):
        """
        Executes an INSERT, UPDATE, DELETE query, commits, and returns lastrowid.
        """
        conn, mode = cls.get_connection()
        try:
            if mode == 'sqlite':
                sql = query.replace('%s', '?')
                cursor = conn.cursor()
                cursor.execute(sql, params)
                last_id = cursor.lastrowid
                conn.commit()
                return last_id
            else:
                cursor = conn.cursor()
                cursor.execute(query, params)
                last_id = cursor.lastrowid
                conn.commit()
                return last_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    @classmethod
    def init_db(cls):
        """Initializes tables using the appropriate schema."""
        mode = cls.determine_mode()
        conn, _ = cls.get_connection()
        try:
            if mode == 'sqlite':
                with open('schema_sqlite.sql', 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
                conn.commit()
            else:
                cursor = conn.cursor()
                with open('schema_mysql.sql', 'r', encoding='utf-8') as f:
                    statements = f.read().split(';')
                for stmt in statements:
                    cleaned = stmt.strip()
                    if cleaned and not cleaned.lower().startswith(('create database', 'use ')):
                        cursor.execute(cleaned)
                conn.commit()
            print(f"[DB] Initialized schema successfully in {mode.upper()} mode.")
        finally:
            conn.close()

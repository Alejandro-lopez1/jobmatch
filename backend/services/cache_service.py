import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from backend.config import DATA_DIR

DB_PATH = DATA_DIR / "jobmatch.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cv_cache (
            cv_id TEXT PRIMARY KEY,
            file_hash TEXT,
            parsed_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_cache (
            job_id TEXT PRIMARY KEY,
            source TEXT,
            query TEXT,
            location TEXT,
            job_data TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            location TEXT,
            results_count INTEGER,
            best_match_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_job_cache_query ON job_cache(query, location)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_search_history_created ON search_history(created_at)
    """)

    conn.commit()
    conn.close()


def cache_cv(cv_id: str, file_hash: str, cv_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO cv_cache (cv_id, file_hash, parsed_data, created_at)
        VALUES (?, ?, ?, ?)
    """, (cv_id, file_hash, json.dumps(cv_data, default=str), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_cached_cv(file_hash: str) -> Optional[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT parsed_data FROM cv_cache WHERE file_hash = ?", (file_hash,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row['parsed_data'])
    return None


def cache_job(job_id: str, source: str, query: str, location: str, job_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO job_cache (job_id, source, query, location, job_data, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (job_id, source, query, location, json.dumps(job_data, default=str), datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_cached_jobs(query: str, location: str, max_age_hours: int = 24) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    since = (datetime.now() - timedelta(hours=max_age_hours)).isoformat()
    cursor.execute("""
        SELECT job_data FROM job_cache
        WHERE query = ? AND location = ? AND scraped_at > ?
        ORDER BY scraped_at DESC
    """, (query, location, since))
    rows = cursor.fetchall()
    conn.close()
    return [json.loads(row['job_data']) for row in rows]


def add_search_history(query: str, location: str, results_count: int, best_match_score: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO search_history (query, location, results_count, best_match_score, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (query, location, results_count, best_match_score, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def get_search_history(limit: int = 20) -> List[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT query, location, results_count, best_match_score, created_at
        FROM search_history
        ORDER BY created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_old_cache(max_age_days: int = 30):
    conn = get_connection()
    cursor = conn.cursor()
    since = (datetime.now() - timedelta(days=max_age_days)).isoformat()
    cursor.execute("DELETE FROM job_cache WHERE scraped_at < ?", (since,))
    cursor.execute("DELETE FROM cv_cache WHERE created_at < ?", (since,))
    conn.commit()
    conn.close()


# Initialize on import
init_db()
import os
import sqlite3
import pandas as pd
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def clean(val):
    """numpy types ko plain Python types mein convert karo."""
    import numpy as np
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_,)):
        return bool(val)
    return val


def get_connection():
    if DATABASE_URL:
        import psycopg2
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    else:
        return sqlite3.connect("loan_predictions.db", check_same_thread=False)


def is_postgres():
    return bool(DATABASE_URL)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    if is_postgres():
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id              SERIAL PRIMARY KEY,
                applicant_name  TEXT,
                age             INTEGER,
                gender          TEXT,
                marital_status  TEXT,
                education       TEXT,
                dependents      INTEGER,
                employment      TEXT,
                annual_income   BIGINT,
                monthly_expense BIGINT,
                work_exp        INTEGER,
                job_stability   TEXT,
                loan_amount     BIGINT,
                loan_tenure     INTEGER,
                loan_purpose    TEXT,
                interest_rate   REAL,
                collateral      TEXT,
                credit_score    INTEGER,
                existing_loans  INTEGER,
                missed_payments INTEGER,
                debt_to_income  REAL,
                savings         BIGINT,
                investments     BIGINT,
                property_owned  TEXT,
                residence_type  TEXT,
                area_type       TEXT,
                insurance       TEXT,
                credit_history  TEXT,
                emi             REAL,
                approve_prob    REAL,
                reject_prob     REAL,
                prediction      TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                applicant_name  TEXT,
                age             INTEGER,
                gender          TEXT,
                marital_status  TEXT,
                education       TEXT,
                dependents      INTEGER,
                employment      TEXT,
                annual_income   INTEGER,
                monthly_expense INTEGER,
                work_exp        INTEGER,
                job_stability   TEXT,
                loan_amount     INTEGER,
                loan_tenure     INTEGER,
                loan_purpose    TEXT,
                interest_rate   REAL,
                collateral      TEXT,
                credit_score    INTEGER,
                existing_loans  INTEGER,
                missed_payments INTEGER,
                debt_to_income  REAL,
                savings         INTEGER,
                investments     INTEGER,
                property_owned  TEXT,
                residence_type  TEXT,
                area_type       TEXT,
                insurance       TEXT,
                credit_history  TEXT,
                emi             REAL,
                approve_prob    REAL,
                reject_prob     REAL,
                prediction      TEXT,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    cur.close()
    conn.close()


def save_prediction(data: dict):
    """Prediction save karo — numpy types automatically convert honge."""

    # ── Saare values clean karo ──────────────────────────────────────
    d = {k: clean(v) for k, v in data.items()}

    conn = get_connection()
    cur = conn.cursor()

    if is_postgres():
        cur.execute("""
            INSERT INTO predictions (
                applicant_name, age, gender, marital_status, education,
                dependents, employment, annual_income, monthly_expense,
                work_exp, job_stability, loan_amount, loan_tenure,
                loan_purpose, interest_rate, collateral, credit_score,
                existing_loans, missed_payments, debt_to_income,
                savings, investments, property_owned, residence_type,
                area_type, insurance, credit_history,
                emi, approve_prob, reject_prob, prediction
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
            )
        """, (
            d["applicant_name"], d["age"], d["gender"],
            d["marital_status"], d["education"], d["dependents"],
            d["employment"], d["annual_income"], d["monthly_expense"],
            d["work_exp"], d["job_stability"], d["loan_amount"],
            d["loan_tenure"], d["loan_purpose"], d["interest_rate"],
            d["collateral"], d["credit_score"], d["existing_loans"],
            d["missed_payments"], d["debt_to_income"], d["savings"],
            d["investments"], d["property_owned"], d["residence_type"],
            d["area_type"], d["insurance"], d["credit_history"],
            d["emi"], d["approve_prob"], d["reject_prob"],
            d["prediction"]
        ))
    else:
        cur.execute("""
            INSERT INTO predictions (
                applicant_name, age, gender, marital_status, education,
                dependents, employment, annual_income, monthly_expense,
                work_exp, job_stability, loan_amount, loan_tenure,
                loan_purpose, interest_rate, collateral, credit_score,
                existing_loans, missed_payments, debt_to_income,
                savings, investments, property_owned, residence_type,
                area_type, insurance, credit_history,
                emi, approve_prob, reject_prob, prediction
            ) VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        """, (
            d["applicant_name"], d["age"], d["gender"],
            d["marital_status"], d["education"], d["dependents"],
            d["employment"], d["annual_income"], d["monthly_expense"],
            d["work_exp"], d["job_stability"], d["loan_amount"],
            d["loan_tenure"], d["loan_purpose"], d["interest_rate"],
            d["collateral"], d["credit_score"], d["existing_loans"],
            d["missed_payments"], d["debt_to_income"], d["savings"],
            d["investments"], d["property_owned"], d["residence_type"],
            d["area_type"], d["insurance"], d["credit_history"],
            d["emi"], d["approve_prob"], d["reject_prob"],
            d["prediction"]
        ))

    conn.commit()
    cur.close()
    conn.close()


def get_all_predictions() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY created_at DESC", conn
    )
    conn.close()
    return df


def get_stats() -> dict:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM predictions")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 'Approved'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM predictions WHERE prediction = 'Rejected'")
    rejected = cur.fetchone()[0]

    cur.execute("SELECT AVG(approve_prob) FROM predictions")
    avg_prob = cur.fetchone()[0] or 0.0

    cur.execute("SELECT AVG(credit_score) FROM predictions")
    avg_credit = cur.fetchone()[0] or 0.0

    cur.execute("SELECT AVG(loan_amount) FROM predictions")
    avg_loan = cur.fetchone()[0] or 0.0

    cur.close()
    conn.close()

    return {
        "total":      total,
        "approved":   approved,
        "rejected":   rejected,
        "avg_prob":   round(avg_prob, 1),
        "avg_credit": round(avg_credit, 1),
        "avg_loan":   round(avg_loan, 0),
    }
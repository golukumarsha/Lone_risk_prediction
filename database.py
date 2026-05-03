import os
import sqlite3
import pandas as pd
from datetime import datetime

# ── Auto-detect: PostgreSQL (Render pe) ya SQLite (local) ─────────────────────
DATABASE_URL = os.environ.get("DATABASE_URL", "")


def get_connection():
    """PostgreSQL ya SQLite connection return karta hai."""
    if DATABASE_URL:
        import psycopg2
        # Render ka DATABASE_URL "postgres://" se start hota hai, psycopg2 ko "postgresql://" chahiye
        url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    else:
        return sqlite3.connect("loan_predictions.db", check_same_thread=False)


def is_postgres():
    return bool(DATABASE_URL)


def init_db():
    """Table create karo agar exist nahi karti."""
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
    """Ek prediction record database mein save karo."""
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
            data["applicant_name"], data["age"], data["gender"],
            data["marital_status"], data["education"], data["dependents"],
            data["employment"], data["annual_income"], data["monthly_expense"],
            data["work_exp"], data["job_stability"], data["loan_amount"],
            data["loan_tenure"], data["loan_purpose"], data["interest_rate"],
            data["collateral"], data["credit_score"], data["existing_loans"],
            data["missed_payments"], data["debt_to_income"], data["savings"],
            data["investments"], data["property_owned"], data["residence_type"],
            data["area_type"], data["insurance"], data["credit_history"],
            data["emi"], data["approve_prob"], data["reject_prob"],
            data["prediction"]
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
            data["applicant_name"], data["age"], data["gender"],
            data["marital_status"], data["education"], data["dependents"],
            data["employment"], data["annual_income"], data["monthly_expense"],
            data["work_exp"], data["job_stability"], data["loan_amount"],
            data["loan_tenure"], data["loan_purpose"], data["interest_rate"],
            data["collateral"], data["credit_score"], data["existing_loans"],
            data["missed_payments"], data["debt_to_income"], data["savings"],
            data["investments"], data["property_owned"], data["residence_type"],
            data["area_type"], data["insurance"], data["credit_history"],
            data["emi"], data["approve_prob"], data["reject_prob"],
            data["prediction"]
        ))

    conn.commit()
    cur.close()
    conn.close()


def get_all_predictions() -> pd.DataFrame:
    """Saari predictions fetch karo DataFrame mein."""
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM predictions ORDER BY created_at DESC",
        conn
    )
    conn.close()
    return df


def get_stats() -> dict:
    """Dashboard ke liye summary stats."""
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
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "avg_prob": round(avg_prob, 1),
        "avg_credit": round(avg_credit, 1),
        "avg_loan": round(avg_loan, 0),
    }

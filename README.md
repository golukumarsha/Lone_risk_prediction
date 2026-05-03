# 🏦 Loan Approval Predictor

> **AI-powered loan eligibility checker** — KNN Machine Learning model + PostgreSQL database + Streamlit UI, deployed on Render.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

---

## 📸 App Preview

| 🔍 Predict Page | 📊 Dashboard | 📋 All Records |
|---|---|---|
| Form bharein, result instant milega | Live charts & analytics | Filter, search, CSV download |

---

## ✨ Features

- 🤖 **KNN Classifier** — 31 features, K=7, binary classification (Approved / Rejected)
- 📊 **Analytics Dashboard** — Real-time charts (trend, loan purpose, credit score)
- 🗄️ **PostgreSQL** — Render pe permanent data storage
- 💾 **SQLite Fallback** — Local testing ke liye automatically switch hota hai
- 📋 **All Records Page** — Filter by result, search by name, CSV export
- 💡 **Smart Tips** — Rejection ke baad improvement suggestions

---

## 📁 Project Structure

```
loan-approval-predictor/
│
├── app.py                            # Main Streamlit application (3 pages)
├── database.py                       # PostgreSQL + SQLite connection & queries
├── requirements.txt                  # Python dependencies
├── render.yaml                       # Render auto-deploy configuration
├── best_model_lone_prediction.pkl    # Trained KNN ML model
└── README.md                         # Yahi file hai 😊
```

---

## ⚙️ Local Machine Pe Chalana (Testing)

### Step 1 — Repository Clone Karo

```bash
git clone https://github.com/YOUR_USERNAME/loan-approval-predictor.git
cd loan-approval-predictor
```

### Step 2 — Virtual Environment Banao

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Dependencies Install Karo

```bash
pip install -r requirements.txt
```

### Step 4 — App Run Karo

```bash
streamlit run app.py
```

> ✅ Browser mein `http://localhost:8501` khulega
> 💾 Local mode mein **SQLite** automatically use hoga — koi setup nahi chahiye!

---

## 🚀 Render Pe Deploy Karna (Production)

### 🔷 Step 1 — GitHub Pe Code Upload Karo

```bash
git init
git add .
git commit -m "first commit: loan predictor app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/loan-approval-predictor.git
git push -u origin main
```

> ⚠️ `.pkl` file bhi push karni hai — model ke bina app kaam nahi karega!

---

### 🔷 Step 2 — Render.com Account Banao

1. [https://render.com](https://render.com) pe jaao
2. **"Get Started for Free"** click karo
3. GitHub se sign up karo (same account jahan code hai)

---

### 🔷 Step 3 — PostgreSQL Database Banao

1. Render Dashboard mein **"New +"** click karo
2. **"PostgreSQL"** select karo
3. Ye settings bharo:

   | Field | Value |
   |---|---|
   | Name | `loan-db` |
   | Database | `loan_predictions` |
   | User | (auto fill hoga) |
   | Region | Singapore (closest to India) |
   | Plan | **Free** |

4. **"Create Database"** click karo
5. Database ban jaane ke baad **"Internal Database URL"** copy karo — yeh baad mein chahiye

---

### 🔷 Step 4 — Web Service Banao

1. Render Dashboard mein **"New +"** click karo
2. **"Web Service"** select karo
3. **"Connect a repository"** — apna GitHub repo select karo
4. Ye settings bharo:

   | Field | Value |
   |---|---|
   | Name | `loan-approval-predictor` |
   | Region | Singapore |
   | Branch | `main` |
   | Runtime | **Python 3** |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true` |
   | Plan | **Free** |

---

### 🔷 Step 5 — Environment Variable Add Karo

1. Web Service ke **"Environment"** tab mein jaao
2. **"Add Environment Variable"** click karo
3. Ye add karo:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | (Step 3 mein copy ki hui Internal Database URL) |

---

### 🔷 Step 6 — Deploy!

1. **"Create Web Service"** click karo
2. Render automatically:
   - Code install karega
   - Dependencies setup karega
   - PostgreSQL connect karega
   - App live kar dega ✅

3. 2-3 minute baad aapko URL milega:
   ```
   https://loan-approval-predictor.onrender.com
   ```

---

## 🗄️ Database Schema

`predictions` table automatically create hoti hai — manually kuch nahi karna.

| Column | Type | Description |
|---|---|---|
| `id` | SERIAL | Auto-increment primary key |
| `applicant_name` | TEXT | Applicant ka naam |
| `age` | INTEGER | Umar |
| `gender` | TEXT | Male / Female |
| `annual_income` | BIGINT | Salana aay (₹) |
| `loan_amount` | BIGINT | Maange gaye loan ki rakam |
| `credit_score` | INTEGER | Credit score (300–900) |
| `approve_prob` | REAL | Approval probability (%) |
| `prediction` | TEXT | **Approved** ya **Rejected** |
| `created_at` | TIMESTAMP | Record save hone ka time |
| *(+22 more columns)* | | Saare 31 features stored hain |

---

## 📦 Dependencies

```
streamlit==1.35.0        # Web UI framework
scikit-learn==1.6.1      # ML model (KNN)
joblib==1.4.2            # Model load karne ke liye
numpy==1.26.4            # Numerical computations
pandas==2.2.2            # Data handling & DataFrames
psycopg2-binary==2.9.9   # PostgreSQL connection
```

---

## 🔄 Database: Local vs Production

| Feature | Local (SQLite) | Render (PostgreSQL) |
|---|---|---|
| Setup | Zero setup | DATABASE_URL env var |
| File | `loan_predictions.db` | Render cloud database |
| Data persist | Haan, file mein | Haan, permanently |
| Auto-detect | ✅ Automatic | ✅ Automatic |
| Reset on redeploy | Nahi | **Nahi** ✅ |

> 💡 Code automatically detect karta hai — `DATABASE_URL` environment variable set hai to PostgreSQL, nahi to SQLite use hoga.

---

## ❓ Common Problems & Solutions

**❌ Model load nahi ho raha?**
```
Make sure best_model_lone_prediction.pkl same folder mein hai
aur GitHub pe push kiya hua hai.
```

**❌ Database connect nahi ho raha?**
```
Render ke Environment tab mein DATABASE_URL check karo.
"Internal URL" use karo, "External URL" nahi.
```

**❌ App start nahi ho raha Render pe?**
```
Start Command exactly yeh hona chahiye:
streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
```

**❌ Free plan pe app slow hai?**
```
Render free plan mein app 15 min inactivity ke baad sleep hoti hai.
Pehli request pe 30-60 sec lag sakte hain — normal hai.
```

---

## 👨‍💻 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit + Custom CSS |
| **ML Model** | Scikit-learn KNN Classifier |
| **Database** | PostgreSQL (Render) / SQLite (Local) |
| **Deployment** | Render.com |
| **Language** | Python 3.10+ |

---

## 📄 License

This project is for educational purposes.

---

<p align="center">
  🏦 Built with ❤️ using Streamlit, scikit-learn & PostgreSQL
</p>
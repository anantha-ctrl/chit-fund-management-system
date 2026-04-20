# SmartChit & Loan Management Suite 🏆

A high-performance, enterprise-grade Django ecosystem designed for unified financial management. This platform integrates **Chit Fund Operations** and **Loan Portfolio Management** into a single, high-density executive cockpit, allowing regional firms to monitor liquidity, member cycles, and asset recovery with precision.

## 🚀 Key Features

### 🏢 Regional Branch & Operations Nexus
- **Multi-Branch Isolation:** Centralized administration with localized branch data isolation for scaling across multiple districts.
- **Unified Executive Cockpit:** A high-performance dashboard that aggregates performance metrics from both Chit and Loan divisions into a single source of truth.

### 💰 Unified Loan Management System (LMS)
- **End-to-End Loan Lifecycle:** Seamless application workflow, multi-stage admin approval queue, and automated disbursement tracking.
- **Dynamic EMI Scheduling:** Intelligent EMI generation with automated due-date projections and interest rate calculations.
- **Asset Recovery Tracking:** Dedicated overdue monitoring and follow-up engines to minimize portfolio risk.

### 💼 Field Collection & Mobile Gamification
- **Dual-Stream POS:** Lightweight Field Collection interface engineered for on-the-spot capture of both Chit installments and Loan EMIs.
- **Daily Performance Pulse:** Visual collector dashboards featuring live progress bars tracking daily & monthly recovery rates against dynamic targets.
- **EOD Cash Handover Protocol:** Secure End-Of-Day workflow allowing staff to lock 'Expected Branch Deposits' and push verification alerts to Super Admins.

### 📱 CRM & Multi-Channel Interaction
- **Digital Receipt Nexus:** Instantly fires properly formatted WhatsApp receipts (`wa.me` links) directly from the field collection screen for all transaction types.
- **Client Engagement Engine:** Unified callback tracker for field staff to log member promises across both Chit and Loan portfolios.

### 📊 Advanced Analytics & E-Ledger
- **Unified Branch Matrix:** Comparative performance analytics showing revenue contributions from Chit and Loan streams per regional hub.
- **Digital Portfolio Passbook:** Real-time personal ledger for members tracking combined financial health, paid installments, and upcoming commitments.
- **Print-Ready Audit Suite:** High-fidelity, A4 output for official statements, branch performance matrixes, and transaction trail audits.

### 🔒 Security & Compliance
- **KYC Digital Vault:** Encrypted document storage interface for member verification with strict Admin-only validation protocols.
- **OTP-Based Recovery:** Hardened zero-touch password reset workflow utilizing robust Gmail SMTP/OTP channels.
- **Audit Logging:** Live monitoring of all system events (Login, Payments, Approvals, Auctions) via a seamless real-time telemetry console.

## 🛠️ Technology Stack
- **Backend Core:** Python 3.14+ & Django 5.x/6.x
- **Data Persistence:** MySQL / MariaDB (Optimized via PyMySQL)
- **Frontend Architecture:** Vanilla Framework, Bootstrap 5.3, Bi-Icons (Glassmorphism & High-Density UI Standard)
- **Visual Intelligence:** Chart.js (Stacked Analytics & Performance Pulse)
- **Push Telemetry:** Django Messages Framework + Internal Notification DB Engine

## 📥 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Chit_Fund_Management
   ```

2. **Setup Virtual Environment:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configure Database (XAMPP):**
   - Ensure **MySQL** is running in your XAMPP Control Panel.
   - Create the target local database: `CREATE DATABASE chit_fund_db;`
   - Update `core/settings.py` with your database credentials.

4. **Initialize System State:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py create_admin.py  # Create/Reset default admin (admin/admin123)
   ```

5. **Launch Environment:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```
   Access the unified dashboard via [http://127.0.0.1:8000](http://127.0.0.1:8000).

---
_Developed with peak architectural design by CloudHawk_

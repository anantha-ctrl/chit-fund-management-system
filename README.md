# Chit Fund Management System (SmartChit) 🏆

A high-performance, enterprise-grade Django application designed for regional Chit Fund firms to manage members, cycles, auctions, and financial reporting with precision and localized branch support.

## 🚀 Key Features

### 🏢 Regional Branch Management

- **Multi-Branch Support:** Centralized administration with localized branch data isolation.
- **Role-Based Access (RBAC):** Distinct specialized dashboards for **Super Admins**, **Branch Managers**, and **Customers**.

### 📊 Executive Financial Reporting

- **Print-Locked Sheet System:** High-density, single-page A4 output for receipts and performance reports.
- **Branch Analytics:** Real-time comparative analytics (Bar Charts) of collection efficiency across physical locations.
- **Predictive Customer Engine:** Smart "Upcoming Dues" projection that calculates future commitments even before billing cycles begin.

### 🔨 Auction & Settlement Suite

- **Auction Hub:** Track bids, winners, and dividend distributions.
- **Guarantor Management:** Modal-based identity verification (Aadhaar/PAN) for legally binding auction settlements.
- **Transaction Ledger:** Automated physical receipt generation with unique tracking IDs.

### 🔒 Security & Compliance

- **KYC Vault:** Secure document storage for member ID proofs and verification status.
- **CSRF Protection:** Hardened session validation for secure regional dashboard access.
- **OTP-Based Recovery:** Secure password reset workflow via Gmail SMTP integration.

## 🛠️ Technology Stack

- **Backend:** Python 3.12+ & Django 6.0.3
- **Database:** MySQL / MariaDB (Optimized for XAMPP environments)
- **Frontend:** Vanilla CSS, Bootstrap 5.3, Bi-Icons
- **Charting:** Chart.js (Interactive Analytics)
- **Email:** Gmail SMTP integration for OTP & Notifications

## 📥 Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd Chit_Fund_Management
   ```

2. **Setup Virtual Environment:**

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   ```

3. **Configure Database:**
   - Ensure MySQL/MariaDB is running (e.g., via XAMPP).
   - Create a database: `CREATE DATABASE chit_fund_db;`
   - Update `core/settings.py` with your database credentials.

4. **Initialize System:**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Run Development Server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## 📜 Branch Management Strategy

The system uses a localized data model where every **Member** and **Chit Group** is linked to a specific **Branch**. This allows for regional performance tracking and localized report generation, essential for scaling across multiple districts.

---

_Designed and developed by CloudHawk_

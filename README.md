🏭 Warehouse Productivity System
📘 Overview

The Warehouse Productivity System is a web-based application built with Django that helps track, manage, and analyze productivity within a warehouse environment.
It allows administrators to record and monitor employee performance or task entries while providing warehouse staff with an organized view of their work progress.

⚙️ Core Features
🧑‍💼 Role-Based Access

Admin Users (Superusers)

Can create, edit, and manage all productivity entries.

Have access to administrative dashboards and reporting tools.

Can use inline AJAX editing to quickly update records without reloading pages.

Regular Users (Warehouse Staff)

Can log in to view their personal entries and productivity statistics.

Restricted from creating or editing global data unless granted permissions.

📊 Dashboard

Provides a real-time summary of warehouse productivity data.

Displays key performance metrics, recent entries, and user activity.

Includes navigation that highlights the active page dynamically.

📦 Productivity Entry Management

Entry List View: Shows all recorded productivity entries.

Add Entry (Admin-only): Allows admins to add new warehouse activity logs.

Update Entry: Supports inline field updates via AJAX for quick adjustments.

Validation & Security: Only specific fields (like title, notes, status) can be modified, protecting data integrity.

🔒 Access Control

Uses Django’s built-in authentication system (login_required, is_superuser, and user_passes_test) to secure sensitive views.

Navigation items (like “Add Entry”) are conditionally displayed only for admins.

Ensures all data modifications occur through authorized POST requests.

🧰 Technology Stack
Layer	Technology
Backend	Django (Python)
Frontend	Django Templates, HTML5, CSS, JavaScript (AJAX)
Database	SQLite or PostgreSQL (Django ORM)
Auth & Security	Django Authentication System
Deployment	Compatible with any WSGI server (Gunicorn, Nginx, etc.)

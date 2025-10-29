Warehouse Productivity Django project

Instructions:
1. Unzip and go to the project root.
2. Create a virtualenv, install Django (tested on Django 4.x).
   pip install Django
3. Run migrations:
   python manage.py migrate
4. Create superuser:
   python manage.py createsuperuser
5. Start server:
   python manage.py runserver

Notes:
- Custom User model is productivity.User with a 'role' field and 'sections' M2M.
- Roles: Admin, Manager, Lead, Employee.
- Leads must be assigned to sections to add entries for them.
- ProductivityEntry has unique constraint to avoid duplicates.

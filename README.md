# ByteBites - Gamified Campus Food Ordering Website

A Django starter project structure for the ByteBites campus quest/order platform.

## Stack
- Django
- HTML templates
- CSS
- Vanilla JavaScript
- SQLite for development
- QR code generation can be added using a Python QR package later

## Core Flow
Login/Signup -> Welcome Hub -> Vendor -> Category -> Products -> Cart -> QR Ticket

## Roles
- Student/User: browse vendors, order food, view tickets
- Employee: access Ticket Center
- Admin: access Admin Dashboard

## Pages
1. Auth Gateway
2. Login
3. Signup
4. Welcome To ByteBites
5. Royal Kitchen
6. Mario
7. Campus Kitchen
8. Tasty Time
9. Admin Panel
10. Ticket Center

## Run
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

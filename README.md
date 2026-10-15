# Close-Match Secure Flask Agency Project

This project is a close-match inspired digital agency website built with Flask.
It is designed to resemble the interface flow of premium agency websites while using original placeholder assets and editable content.

## Features
- Responsive homepage with hero, services, team, packages, testimonials, FAQs, blogs, and CTA
- Secure admin login via `/admin-login`
- Protected admin dashboard `/admin`
- Protected CSV export `/admin/export`
- Contact form saved to SQLite (`database.db`)
- No public admin button on the website

## Default admin login
- Email: `babulsinghbhumi@gmail.com`
- Password: `Babul@123`

## Run locally
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Important before going live
- Change `SECRET_KEY`
- Change `ADMIN_EMAIL` and `ADMIN_PASSWORD_HASH` using environment variables
- Set `debug=False`
- Enable HTTPS and set `SESSION_COOKIE_SECURE=True`

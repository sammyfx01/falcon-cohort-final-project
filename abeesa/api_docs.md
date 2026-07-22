# API Documentation

Base URL (local development): `http://127.0.0.1:8000`

All endpoints return JSON. Endpoints requiring authentication use Django's
session authentication — log in via the site (`/accounts/login/`) in the same
browser session, or use DRF's browsable API login link.

---

## Menu Items

### List all menu items
# Sellpilot Instagram OAuth Backend

Production-style FastAPI backend for Instagram OAuth with MongoDB persistence and HTTP-only cookie authentication.

## Architecture

```text
app/
  config/          Environment settings
  database/        MongoDB connection and indexes
  routers/         Thin HTTP controllers
  services/        Business logic and OAuth orchestration
  repositories/   MongoDB persistence layer
  models/         Internal DB models
  schemas/        API response schemas
  middleware/     Auth dependencies
  utils/          Logging and security helpers
  exceptions/     Custom exception types
```

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your Instagram app values. For local MongoDB, this is enough:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=sellpilot
FRONTEND_URL=http://localhost:8080
FRONTEND_REDIRECT_PATH=/dashboard
```

Generate a strong cookie secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Run

```bash
uvicorn app.main:app --reload
```

Alternative:

```bash
python run.py
```

The API runs at:

```text
http://127.0.0.1:8000
```

## Endpoints

- `GET /api/health`
- `GET /api/auth/login`
- `GET /api/auth/callback`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `GET /api/users/me`
- `POST /api/shop/products`
- `GET /api/shop/products`

## OAuth Flow

1. React redirects the browser to `GET /api/auth/login`.
2. Backend sets a short-lived OAuth state cookie and redirects to Instagram.
3. Instagram redirects to `REDIRECT_URI`.
4. Backend validates state and exchanges the code for a short-lived token.
5. Backend exchanges the short-lived token for a long-lived token via `https://graph.instagram.com/access_token`.
6. Backend stores the Instagram token server-side in MongoDB.
7. Backend sets a signed HTTP-only cookie containing only the internal MongoDB user id.
8. Backend redirects to `FRONTEND_URL` + `FRONTEND_REDIRECT_PATH`.

## React Integration

Start login:

```ts
window.location.href = "http://127.0.0.1:8000/api/auth/login";
```

Read auth state:

```ts
const response = await fetch("http://127.0.0.1:8000/api/auth/me", {
  credentials: "include",
});

const auth = await response.json();
```

Logout:

```ts
await fetch("http://127.0.0.1:8000/api/auth/logout", {
  method: "POST",
  credentials: "include",
});
```

Register shop products:

```ts
await fetch("https://your-ngrok-domain.ngrok-free.dev/api/shop/products", {
  method: "POST",
  credentials: "include",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    shop: {
      name: "Beauty Shop Casa",
    },
    products: [
      {
        name: "Serum Vitamin C",
        price: 149,
        description: "Brightening serum for dark spots",
        available: true,
      },
    ],
    delivery: "Casablanca 25 MAD, other cities 35 MAD, delivery in 24-72h",
  }),
});
```

Read shop products:

```ts
const response = await fetch("https://your-ngrok-domain.ngrok-free.dev/api/shop/products", {
  credentials: "include",
});

const shopProducts = await response.json();
```

## Cookie Notes

Cookies are configured with:

- `httponly=True`
- `secure=COOKIE_SECURE`
- `samesite=COOKIE_SAMESITE`

For plain HTTP local development where the frontend calls `http://localhost:8000`,
browsers will not store `secure=True` cookies. Use local HTTPS or temporarily set:

```env
COOKIE_SECURE=false
```

Do not use `COOKIE_SECURE=false` in production.

When Instagram redirects to an HTTPS ngrok API and the frontend runs on
`http://localhost:8080`, the dashboard must call the ngrok API URL with
`credentials: "include"` and cookies should use:

```env
COOKIE_SECURE=true
COOKIE_SAMESITE=none
```

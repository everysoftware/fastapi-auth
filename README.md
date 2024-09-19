# FastAPI Authorization Server

Authorization server with Google, Yandex & Telegram SSO, RBAC, user management, etc. 🔥

## Features

Main features:

- Secure **authorization** with JWT+RSA+Refresh Tokens
- Extendable **single sign-on** via Google, Yandex & Telegram
- **Confirmation of actions** via Email & Telegram
- Extendable **role-based access control** (supports user & superuser)
- Powerful **user** management

## Installation

1. Clone the repository:

```bash
git clone https://github.com/everysoftware/fastapi-auth
```

2. Generate RSA keys:

```bash
openssl genrsa -out certs/private.pem 2048
openssl rsa -in certs/private.pem -pubout -out certs/public.pem
```

3. Create a `.env` file. Use the `.env.example` as a reference.
4. Run the application:

```bash
make up
```

**Made with love by Ivan Stasevich ❤️**

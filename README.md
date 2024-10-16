# Breeze Auth

Authorization server with OAuth2, permissions, user management, etc.

## Features

- Secure **JWT authorization**
- Scalable Google, Telegram and Yandex **single sign-on**
- **One-time code** confirmation (Email & Telegram)
- Extendable **permission system**
- Powerful **user management**: CRUD, search, roles, etc.
- **Admin panel** with authorization and CRUD operations
- **Grafana dashboard** with metrics, tracing & logging

## Installation

1. Install [observability preset](https://github.com/everysoftware/fastapi-obs)
2. Clone the repository:

    ```bash
    git clone https://github.com/everysoftware/fastapi-auth
    ```

3. Generate RSA keys:

    ```bash
    openssl genrsa -out certs/private.pem 2048
    openssl rsa -in certs/private.pem -pubout -out certs/public.pem
    ```

4. Create a `.env` file. Use the `.env.example` as a reference.
5. Run the application:

    ```bash
    make up
    ```

## Screenshots

### Swagger UI

![Swagger Auth](assets/swagger_auth.png)
![Swagger OAuth](assets/swagger_oauth.png)

### Consents

![Google](assets/google_consent.png)
![Telegram](assets/telegram_consent.png)
![Yandex](assets/yandex_consent.png)

### Admin Panel

![Admin Panel](assets/admin_panel.png)

### Dashboards

![Metrics](assets/dashboard_metrics.png)
![Logs](assets/dashboards_logs.png)

**Made with ❤️**

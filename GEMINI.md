# SIGILO Project - GEMINI.md

## 1. Project Overview

SIGILO (SIstema de Gestão de Informações e Links Operacionais) is a secure information and URL sharing tool for the Tribunal de Justiça de Minas Gerais (TJMG). It allows users to create encrypted, expiring messages and shortened URLs, addressing the security risks of using unsecured communication channels.

## 2. Technologies

- **Backend:** Python 3, Flask
- **Database:** Redis for persistence of messages and links.
- **Authentication:** Keycloak (OAuth2)
- **Deployment:** Docker, Docker Compose, Helm for Kubernetes.

## 3. Project Structure

The project follows a layered architecture pattern (Controllers, Services, Repositories) to ensure separation of concerns.

-   `app/routes/`: Controller layer. Handles HTTP requests and calls the appropriate services.
-   `app/services/`: Service layer. Contains the core business logic (e.g., expiration rules, cryptography orchestration). It depends on repository interfaces, not concrete implementations.
-   `app/repositories/`: Repository layer. Abstracted data access layer. This is the only part of the app that knows how data is stored (currently Redis).
    -   `app/repositories/interfaces/`: Defines the contracts (Abstract Base Classes) for the repositories.
-   `app/dependencies.py`: A factory module responsible for dependency injection, deciding which concrete repository to use and injecting it into the services.
-   `app/templates/`: View layer, containing Jinja2 templates.
-   `Dockerfile`, `docker-compose.yml`, `helm/`: Files for containerization and deployment.

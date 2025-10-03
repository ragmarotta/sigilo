# SIGILO Project - GEMINI.md

## 1. Project Overview

SIGILO (SIstema de Gestão de Informações e Links Operacionais) is a secure information and URL sharing tool for the Tribunal de Justiça de Minas Gerais (TJMG). It allows users to create encrypted, expiring messages and shortened URLs, addressing the security risks of using unsecured communication channels.

## 2. Technologies

- **Backend:** Python 3, Flask
- **Database:** Redis for persistence of messages and links.
- **Authentication:** Keycloak (OAuth2)
- **Deployment:** Docker, Docker Compose, Helm for Kubernetes.

## 3. Core Features

- **Secure Messaging:** Create encrypted messages with configurable expiration (time and access count).
- **URL Shortener:** Create short URLs with optional expiration.
- **Secure Access:** Messages are accessed via a unique URL and token.
- **Email Notifications:** Send access details via a configurable email service.
- **Role-Based Access:** Differentiated permissions for administrators and users.
- **Audit Logging:** Configurable logging for all critical operations.

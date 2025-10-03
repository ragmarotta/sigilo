# Diagrama de Arquitetura (Componentes)

Este diagrama mostra os principais componentes da aplicação e como eles interagem entre si.

```mermaid
graph TD
    subgraph "Usuário"
        Browser[<i class="material-icons">web</i> Navegador Web]
    end

    subgraph "Infraestrutura SIGILO (Kubernetes/Docker)"
        App[<i class="material-icons">layers</i> Aplicação Flask SIGILO]
        Redis[<i class="material-icons">storage</i> Redis]
    end

    subgraph "Serviços Externos"
        Keycloak[<i class="material-icons">security</i> Keycloak]
        SMTPServer[<i class="material-icons">email</i> Servidor SMTP]
    end

    Browser -- HTTPS --> App
    App -- OIDC --> Keycloak
    App -- Lê/Escreve --> Redis
    App -- Envia E-mail --> SMTPServer
```

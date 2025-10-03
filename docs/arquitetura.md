# Diagrama de Arquitetura (Componentes)

Este diagrama mostra os principais componentes da aplicação e como eles interagem entre si, destacando a nova arquitetura em camadas.

```mermaid
graph TD
    subgraph "Usuário"
        Browser[<i class="material-icons">web</i> Navegador Web]
    end

    subgraph "Infraestrutura SIGILO (Kubernetes/Docker)"
        subgraph "Aplicação Flask SIGILO"
            direction LR
            Routes[Routes<br>(Controllers)]
            Services[Services<br>(Lógica de Negócio)]
            Repositories[Repositories<br>(Acesso a Dados)]
            
            Routes --> Services
            Services --> Repositories
        end
        Redis[<i class="material-icons">storage</i> Redis]
        Repositories -- Lê/Escreve --> Redis
    end

    subgraph "Serviços Externos"
        Keycloak[<i class="material-icons">security</i> Keycloak]
        SMTPServer[<i class="material-icons">email</i> Servidor SMTP]
    end

    Browser -- HTTPS --> Routes
    Services -- OIDC --> Keycloak
    Services -- Envia E-mail --> SMTPServer
```
# Diagrama de Fluxo (Criação e Acesso de Mensagem)

Este diagrama de sequência foi atualizado para mostrar a interação entre as novas camadas da arquitetura (Serviço e Repositório).

### Criação da Mensagem

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Route as Rota
    participant Service as Serviço
    participant Repository as Repositório
    participant Redis

    User->>Route: POST /create/message
    Route->>Service: create_message(dados)
    Service->>Repository: save(dados_criptografados)
    Repository->>Redis: HSET, EXPIRE
    Redis-->>Repository: OK
    Repository-->>Service: OK
    Service-->>Route: token
    Route-->>User: Exibe página com link
```

### Acesso à Mensagem

```mermaid
sequenceDiagram
    participant User as Usuário
    participant Route as Rota
    participant Service as Serviço
    participant Repository as Repositório
    participant Redis

    User->>Route: GET /message/<token>
    Route->>Service: find_and_process_message(token)
    Service->>Repository: find_by_id(token)
    Repository->>Redis: HGETALL
    Redis-->>Repository: dados_da_mensagem
    Repository-->>Service: dados_da_mensagem
    Service->>Repository: increment_visits(token)
    Repository->>Redis: HINCRBY
    alt Mensagem válida
        Service-->>Route: conteúdo_descriptografado
        Route-->>User: Exibe página com mensagem
    else Mensagem expirada
        Service->>Repository: delete(token)
        Repository->>Redis: DEL
        Service-->>Route: erro
        Route-->>User: Exibe página de erro
    end
```
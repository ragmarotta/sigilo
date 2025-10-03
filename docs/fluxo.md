# Diagrama de Fluxo (Criação e Acesso de Mensagem)

Este diagrama de sequência descreve o fluxo de interações para o caso de uso principal: um usuário criando e outro acessando uma mensagem segura.

### Criação da Mensagem

```mermaid
sequenceDiagram
    participant UserA as Usuário A
    participant Browser as Navegador
    participant SIGILO as App SIGILO
    participant Redis

    UserA->>Browser: Preenche formulário da mensagem
    Browser->>SIGILO: POST /create/message
    SIGILO->>Redis: Gera token, criptografa e salva mensagem (HSET)
    SIGILO->>Redis: Define tempo de expiração (EXPIRE)
    Redis-->>SIGILO: Confirmação
    SIGILO-->>Browser: Retorna página com link de acesso
    Browser-->>UserA: Exibe link seguro
```

### Acesso à Mensagem

```mermaid
sequenceDiagram
    participant UserB as Usuário B
    participant Browser as Navegador
    participant SIGILO as App SIGILO
    participant Redis

    UserB->>Browser: Acessa URL com token
    Browser->>SIGILO: GET /message/&lt;token&gt;
    SIGILO->>Redis: Incrementa visitas (HINCRBY) e busca dados
    Redis-->>SIGILO: Retorna dados da mensagem
    alt Mensagem válida
        SIGILO->>SIGILO: Descriptografa conteúdo
        SIGILO-->>Browser: Renderiza página com a mensagem
        Browser-->>UserB: Exibe mensagem
        SIGILO->>Redis: Se limite de visitas foi atingido, apaga a chave (DEL)
    else Mensagem inválida ou expirada
        SIGILO-->>Browser: Renderiza página de erro
        Browser-->>UserB: Exibe erro
    end
```

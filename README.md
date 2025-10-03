# SIGILO: SIstema de Gestão de Informações e Links Operacionais

O SIGILO é uma aplicação web segura desenvolvida para o Tribunal de Justiça de Minas Gerais (TJMG) para permitir o compartilhamento de informações sensíveis (textos, chaves, mensagens) e o encurtamento de URLs de forma controlada e auditável.

O sistema aborda a necessidade de uma ferramenta interna segura, evitando o uso de canais não oficiais como e-mails pessoais, chats e aplicativos de mensagens, que podem comprometer a segurança da informação.

## Funcionalidades Principais

- **Mensagens Seguras:** Crie mensagens criptografadas que se autodestroem após um tempo definido ou um número de acessos.
- **Encurtador de URLs:** Crie links curtos para URLs longas, com opção de expiração.
- **Autenticação Centralizada:** Integração com Keycloak (via OIDC) para controle de acesso, com um modo "mock" para facilitar o desenvolvimento local.
- **Painel de Administração:** Uma área restrita para administradores visualizarem e revogarem mensagens e links ativos.
- **Log de Auditoria:** Todos os eventos importantes (logins, criação, acessos, revogações) são registrados em formato JSON estruturado para fácil análise e monitoramento.
- **Notificação por E-mail:** Envio automático de links seguros para destinatários de e-mail.

## Tecnologias Utilizadas

- **Backend:** Python 3, Flask, Flask-Mail
- **Frontend:** Materialize CSS, JavaScript
- **Banco de Dados:** Redis
- **Autenticação:** Keycloak (OpenID Connect)
- **Deploy:** Docker, Docker Compose, Helm, Kubernetes

## Arquitetura e Diagramas

A aplicação segue um padrão de arquitetura em camadas (Controllers, Services, Repositories) para garantir a separação de responsabilidades, alta coesão e baixo acoplamento entre os componentes.

- **Controllers (Rotas):** Responsáveis por receber as requisições HTTP e orquestrar as ações.
- **Services (Serviços):** Contêm a lógica de negócio da aplicação (ex: regras de expiração, criptografia).
- **Repositories (Repositórios):** Camada de abstração de dados. É a única parte do sistema que sabe como e onde os dados são persistidos (atualmente, no Redis).

Este design, que utiliza **Injeção de Dependência** e **Interfaces**, torna a aplicação extremamente flexível. Para trocar o Redis por outro banco de dados no futuro, basta criar uma nova implementação do repositório e atualizar a fábrica de dependências, sem a necessidade de alterar os serviços ou as rotas.

Para detalhes visuais, consulte os diagramas na pasta `docs`:

- **[Diagrama de Arquitetura](./docs/arquitetura.md):** Visão geral dos componentes e suas interações.
- **[Diagrama de Classes](./docs/classes.md):** Desenho simplificado ilustrando o padrão de Inversão de Dependência.
- **[Diagrama de Fluxo](./docs/fluxo.md):** Diagrama de sequência para o caso de uso de criação e acesso de mensagens.

## Funcionamento da Expiração

A expiração de itens no SIGILO é gerenciada diretamente pelo Redis, garantindo alta performance e eficiência. Existem dois mecanismos principais:

### 1. Expiração por Tempo (Para Mensagens e URLs)

- **Como funciona:** Ao criar um item com um prazo de validade (ex: "1 Hora"), a aplicação utiliza o comando `EXPIRE` do Redis.
- **Mecanismo:** Este comando funciona como um "timer" que instrui o Redis a **apagar automaticamente** o item após o tempo especificado. A aplicação não precisa verificar a data a cada acesso; se o item expirou, o Redis simplesmente informa que ele não existe mais.

### 2. Expiração por Número de Acessos (Apenas para Mensagens)

- **Como funciona:** Ao criar uma mensagem com um "Nº Máximo de Acessos", a aplicação armazena um contador.
- **Mecanismo:** A cada acesso, o contador é incrementado de forma atômica (usando o comando `HINCRBY`). Quando o contador atinge o limite definido, a aplicação **deleta explicitamente** a mensagem, garantindo que ela seja lida apenas o número de vezes especificado.

## Executando Localmente (com Docker)

Siga os passos abaixo para executar a aplicação em seu ambiente de desenvolvimento.

### Pré-requisitos

- Docker
- Docker Compose

### 1. Clone o Repositório

```bash
git clone <url-do-repositorio>
cd sigilo
```

### 2. Configure o Ambiente

O sistema é configurado via variáveis de ambiente. Para desenvolvimento, você pode usar um arquivo `.env`.

1.  Copie o arquivo de exemplo:
    ```bash
    cp .env.example .env
    ```

2.  Edite o arquivo `.env` e configure as variáveis. Para um teste rápido e local, as seguintes configurações são suficientes:

    - **Desativar Keycloak (Recomendado para teste local):**
      ```
      KEYCLOAK_ENABLED=False
      ```
      Isso ativará a tela de login falso, permitindo que você teste a aplicação sem precisar de uma instância do Keycloak.

    - **Gerar uma Chave de Criptografia:**
      A `FERNET_KEY` é usada para criptografar as mensagens. Gere uma nova chave e cole no arquivo `.env`.
      ```bash
      python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
      ```
      Substitua o valor de `FERNET_KEY` pela chave gerada.

### 3. Suba os Contêineres

Com o Docker em execução, execute o comando abaixo na raiz do projeto:

```bash
docker-compose up --build
```

Isso irá construir a imagem da aplicação, baixar a imagem do Redis e iniciar os dois contêineres.

### 4. Acesse a Aplicação

A aplicação estará disponível em [http://localhost:5000](http://localhost:5000).

Como o Keycloak foi desativado, ao clicar em "Login", você será direcionado para uma página de login falso, onde poderá escolher entrar como um usuário comum ou como administrador.

## Implantação em Kubernetes (com Helm)

O projeto inclui um Helm chart para facilitar a implantação em um ambiente Kubernetes.

### Pré-requisitos

- Cluster Kubernetes acessível.
- `kubectl` configurado para acessar o cluster.
- Helm 3 instalado.

### 1. Configure o Ambiente de Produção

Crie um arquivo `.env` com as configurações de **produção**. As variáveis mais importantes são:

- `KEYCLOAK_ENABLED=True`
- `KEYCLOAK_SERVER_URL`, `KEYCLOAK_REALM_NAME`, `KEYCLOAK_CLIENT_ID`, `KEYCLOAK_CLIENT_SECRET_KEY` com os valores reais do seu Keycloak.
- `FERNET_KEY` com uma chave estática e segura.
- `MAIL_SERVER`, `MAIL_PORT`, etc., com os dados do seu servidor de e-mail.

### 2. Crie o Secret no Kubernetes

É uma boa prática armazenar as variáveis de ambiente em um `Secret` do Kubernetes, em vez de passá-las diretamente.

```bash
kubectl create secret generic sigilo-env --from-env-file=.env
```

O nome `sigilo-env` corresponde ao valor `existingSecret` no arquivo `values.yaml`.

### 3. Configure a Imagem Docker

Antes de instalar, você precisa construir e enviar a imagem da aplicação para um registro de contêineres (Docker Hub, Harbor, GCR, etc.).

Edite o arquivo `helm/sigilo/values.yaml` e ajuste o repositório da imagem:

```yaml
image:
  repository: seu-registro/sigilo
```

### 4. Instale o Helm Chart

Navegue até a raiz do projeto e execute o comando de instalação do Helm. Você pode definir a tag da imagem durante a instalação.

```bash
helm install sigilo ./helm/sigilo --set image.tag=<tag-da-sua-imagem>
```

Exemplo:
```bash
helm install sigilo ./helm/sigilo --set image.tag=1.0.0
```

Isso irá criar o `Deployment` e o `Service` no seu cluster Kubernetes. A aplicação buscará as variáveis de ambiente do `Secret` `sigilo-env` que você criou.
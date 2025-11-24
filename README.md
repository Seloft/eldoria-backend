# Eldoria Backend

<div aling="center">

![ELdora logo]()

**Backend de uma API FastAPI para gerenciamento de um servidor Minecraft com suporte a mods, integração com Modrinth e controle via RCON.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)

</div>

---

## Indice

- [Caracteristicas](#-caracteristicas)
- [Requisitos](#-requisitos)


## Caracteristicas

- **Gerenciamento de Mods**: Instalar, remover e listar mods
- **Integração Modrinth**: Buscar e baixar mods do Modrinth com resolução automática de dependências
- **Controle do Servidor**: Iniciar, parar e reiniciar servidor Minecraft via Docker
- **RCON**: Enviar comandos para o servidor Minecraft
- **WebSocket**: Stream em tempo real dos logs do servidor
- **Configuração**: Gerenciar configurações do servidor
- **Backup**: Backup automático de mods antes de instalações
- **Segurança**: Middleware de CORS e validação de origem

## Requisitos

- **Python**: 3.10 ou superior
- **Docker Desktop**: 20.10+ (com Docker Compose v2)
- **Git**: Para controle de versão

## Instalação

### Opção 1: Ambiente Local (Desenvolvimento)


```bash
# 1. Clone o repositório
git clone <repository-url>
cd eldoria-backend

# 2. Crie um ambiente virtal

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 5. Execute a aplicação
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Configuração

Copie o arquivo `.env.example` para `.env` e ajuste as seguintes variáveis:

```env

ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
MINECRAFT_RCON_PASSWORD=sua_senha_rcon
MODRINTH_AUTHORIZATION=seu_token_modrinth

```

## Execução

### Comandos Docker

```bash
# Build da imagem
docker build -t eldoria-backend .

# Executar container
docker run -d \
  --name eldoria-backend \
  -p 8000:8000 \
  -v minecraft_data:/minecraft \
  -e MINECRAFT_RCON_PASSWORD=sua_senha \
  -e MODRINTH_AUTHORIZATION=seu_token \
  eldoria-backend
```

### Comandos de Desenvolvimento

```bash
# Executar com hot-reload
uvicorn app.main:app --reload

# Executar testes
pytest

# Executar testes com coverage
pytest --cov=app --cov-report=html

```

### Acessando a Aplicação

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs

---

## Estrutura do Projeto

```
eldoria-backend/
├── main.py                          # Entrada da aplicação
├── requirements.txt                 # Dependências
├── dockerfile                       # Configuração Docker
├── config/                          # Arquivos de configuração
│   ├── installed_mods.json         # Mods instalados
│   ├── ready_to_install.json       # Mods prontos para instalar
│   └── sent_commands.json          # Histórico de comandos
├── controllers/                     # Rotas e controllers
│   ├── modrinth/                   # Endpoints Modrinth
│   ├── mods/                       # Endpoints de mods
│   ├── mc_server/                  # Endpoints do servidor
│   └── files/                      # Endpoints de arquivos
└── services/                        # Lógica de negócio
    ├── modrinth/                   # Integração Modrinth
    ├── mods/                       # Serviços de mods
    ├── mc_server/                  # Serviços do servidor
    ├── files/                      # Serviços de arquivos
    └── docker_s/                   # Integração Docker
```

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com coverage
pytest --cov=app --cov-report=html

# Executar testes específicos
pytest tests/api/
pytest tests/services/

# Executar com verbose
pytest -v

# Executar testes em paralelo
pytest -n auto
```

### Estrutura de Testes

```
tests/
├── api/              # Testes de endpoints
├── services/         # Testes de serviços
├── repositories/     # Testes de repositórios
├── conftest.py       # Fixtures compartilhadas
└── __init__.py
```

---

# Endipoints até agora...

### Modrinth

- GET /modrinth/search/fabric - Buscar mods Fabric
- GET /modrinth/mod/{project_id} - Obter detalhes do mod

### Mods

- POST /mods/install-ready-mods - Instalar mods prontos
- POST /mods/add-new-mod - Adicionar novo mod

### Servidor Minecraft

- GET /mc-server/status - Status do servidor
- POST /mc-server/start - Iniciar servidor
- POST /mc-server/stop - Parar servidor
- POST /mc-server/restart - Reiniciar servidor
- POST /mc-server/command - Enviar comando RCON
- GET /mc-server/mods - Listar mods instalados
- WebSocket /mc-server/logs - Stream de logs

### Arquivos

- GET /files/server-config - Configuração do servidor
- GET /files/players-data - Dados de jogadores (banidos, ops, whitelist)
- GET /files/mods/download-all - Baixar todos os mods

---

# Segurança

- CORS: Apenas localhost e redes internas (172.x, 192.168.x)
- Validação de origem: Rejeita acessos externos
- RCON Password: Variável de ambiente para segurança

# Contribuindo

### Workflow de Desenvolvimento

1. Crie uma branch a partir de `develop`:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. Faça suas alterações seguindo os padrões do projeto

3. Execute os testes:
   ```bash
   pytest
   ```

4. Commit suas mudanças:
   ```bash
   git commit -m "feat: adiciona nova funcionalidade"
   ```

5. Push para o repositório:
   ```bash
   git push origin feature/nova-funcionalidade
   ```

6. Abra um Pull Request para `develop`

### Padrões de Código

- **Estilo**: PEP 8 (verificado com Ruff)
- **Type Hints**: Obrigatório em funções públicas
- **Docstrings**: Google Style
- **Commits**: Conventional Commits

### Conventional Commits

```
feat: nova funcionalidade
fix: correção de bug
docs: alteração em documentação
style: formatação de código
refactor: refatoração
test: adição/alteração de testes
chore: tarefas de manutenção
```

---

## Equipe 

| Nome            | Função                  | GitHub                                                   |
| --------------- | ----------------------- | -------------------------------------------------------- |
| Marcos Gabriel  | Desenvolvedor FullStack | [@marcosgabriel-mm](https://github.com/marcosgabriel-mm) |
| Pedro Henrique  | Desenvolvedor Backend   | [@ph3523](https://github.com/ph3523)                     |

---

## Contato 

Para dúvidas ou sugestões, abra uma issue no repositório.
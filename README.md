# Sistema de Checklist de Não Conformidades (NC)

Sistema web desenvolvido em Python com Flask para gerenciamento de checklists de não conformidades, com **notificações em tempo real via WebSocket** e sistema completo de autenticação de usuários.

## 📋 Funcionalidades

- ✅ **Sistema de autenticação de usuários** (login/registro)
- ✅ **Perfis de usuário** com nome, email e função
- ✅ Criação de múltiplos checklists
- ✅ Gerenciamento completo de itens de verificação
- ✅ **Cálculo automático de % de aderência**
- ✅ Classificação de NCs (Leve, Moderada, Grave)
- ✅ **Atribuição de responsáveis** para cada NC
- ✅ **Notificações em tempo real via WebSocket**
- ✅ **Acompanhamento de NCs** por usuário
- ✅ **Atualização de status de NCs** (Pendente, Em Andamento, Resolvida)
- ✅ Controle de prazos de resolução
- ✅ Dashboard com estatísticas
- ✅ Interface responsiva com Bootstrap

## 🔔 Sistema de Notificações (WebSocket)

O sistema utiliza **WebSocket (Socket.IO)** para enviar notificações em tempo real quando:

- Uma NC é **atribuída** a um usuário
- O **responsável de uma NC é alterado**
- Uma NC é **atualizada**
- O **status de uma NC muda**

As notificações aparecem instantaneamente sem necessidade de recarregar a página, com:
- Toast de notificação no canto superior direito
- Contador de notificações não lidas no menu
- Som de alerta (opcional)
- Lista completa de notificações com filtro de lidas/não lidas

## 🔧 Campos do Checklist

Cada item do checklist possui:
- **Seção**: Categoria do item
- **Item de Verificação**: Descrição do que verificar
- **Critério de Conformidade**: Critério para avaliar
- **Resultado**: Conforme, Não Conforme ou N/A
- **Observação**: Notas adicionais
- **Responsável pela Correção**: Usuário responsável (seletor de usuários)
- **Classificação da NC**: L (Leve), M (Moderada), G (Grave)
- **Ação Corretiva**: O que deve ser feito
- **Prazo de Resolução**: Dias para resolver
- **Status da NC**: Pendente, Em Andamento, Resolvida

## 👥 Sistema de Usuários

- **Cadastro de usuários** com nome, email, função e senha
- **Login seguro** com hash de senhas
- **Perfis de usuário** com informações profissionais
- **Atribuição de responsabilidades** para NCs
- **Página "Minhas NCs"** para cada usuário acompanhar suas não conformidades

## 🚀 Instalação

1. **Clone ou navegue até o diretório do projeto**

2. **Crie um ambiente virtual** (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # No macOS/Linux
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**:
```bash
python app.py
```

5. **Acesse no navegador**:
```
http://localhost:5000
```

6. **Primeiro acesso**:
   - Clique em "Criar nova conta"
   - Preencha seus dados (nome, email, função, senha)
   - Faça login com suas credenciais

## 📊 Cálculo de Aderência

A aderência é calculada automaticamente como:
```
Aderência (%) = (Itens Conformes / Total de Itens) × 100
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: Usuario
- id (PK)
- nome
- email (unique)
- senha_hash
- funcao
- ativo
- data_criacao

### Tabela: Checklist
- id (PK)
- nome
- descricao
- criador_id (FK → Usuario)
- data_criacao

### Tabela: ItemChecklist
- id (PK)
- checklist_id (FK → Checklist)
- secao
- item_verificacao
- criterio_conformidade
- resultado
- observacao
- responsavel_id (FK → Usuario)
- classificacao_nc
- acao_corretiva
- prazo_resolucao_dias
- status_nc
- data_criacao
- data_resolucao

### Tabela: Notificacao
- id (PK)
- usuario_id (FK → Usuario)
- item_id (FK → ItemChecklist)
- tipo (nova_nc, nc_atualizada, prazo_proximo)
- titulo
- mensagem
- lida
- data_criacao

## 📱 Interface

- **Página de Login/Registro**: Autenticação segura de usuários
- **Dashboard**: Visualização de todos os checklists com % de aderência
- **Detalhes do Checklist**: Lista completa de itens com estatísticas
- **Minhas NCs**: Página pessoal com NCs atribuídas ao usuário
- **Notificações**: Central de notificações em tempo real
- **Formulários**: Criação e edição intuitivas
- **Modais**: Visualização rápida de detalhes dos itens
- **Notificações Toast**: Alertas em tempo real na tela

## 🎨 Tecnologias Utilizadas

- **Backend**: Python 3 + Flask
- **Autenticação**: Flask-Login com hash de senhas
- **WebSocket**: Flask-SocketIO para notificações em tempo real
- **Template Engine**: Jinja2
- **Banco de Dados**: SQLite3
- **ORM**: SQLAlchemy
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Real-time**: Socket.IO (JavaScript)
- **Responsividade**: Mobile-first design

## 🚀 Fluxo de Uso

1. **Usuário se cadastra** no sistema (nome, email, função, senha)
2. **Faz login** com credenciais
3. **Cria um checklist** com nome e descrição
4. **Adiciona itens** ao checklist com todos os campos
5. Ao marcar um item como **"Não Conforme"**:
   - Seleciona um **responsável** da lista de usuários
   - Define **classificação** (Leve, Moderada, Grave)
   - Define **ação corretiva** e **prazo**
6. O **responsável recebe notificação instantânea** via WebSocket
7. Responsável acessa **"Minhas NCs"** para ver suas atribuições
8. Responsável **atualiza o status** (Pendente → Em Andamento → Resolvida)
9. O **criador do checklist é notificado** sobre as atualizações
10. Sistema calcula **% de aderência** automaticamente

## 📝 Notas

- O banco de dados é criado automaticamente na primeira execução
- Todos os dados são armazenados localmente em SQLite
- A aplicação roda em modo debug por padrão (ideal para desenvolvimento)

## 🔒 Segurança

Para produção, lembre-se de:
- Alterar a `SECRET_KEY` no arquivo `app.py`
- Desativar o modo debug
- Configurar um servidor WSGI (Gunicorn, uWSGI)
- Usar HTTPS

## 📄 Licença

Este projeto é livre para uso educacional e comercial.

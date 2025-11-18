# 📁 Estrutura de Arquivos Estáticos

Esta pasta contém todos os arquivos CSS e JavaScript do sistema, organizados de forma modular.

## 📂 Estrutura de Pastas

```
static/
├── css/           # Arquivos de estilos CSS
│   ├── base.css                    # Estilos globais do sistema
│   ├── login.css                   # Estilos da página de login
│   ├── ver_checklist.css          # Estilos para visualização de checklist
│   └── preencher_checklist.css    # Estilos para preenchimento de checklist
│
└── js/            # Arquivos JavaScript
    ├── notificacoes.js            # Sistema de notificações em tempo real
    ├── ver_checklist.js           # Scripts para visualização de checklist
    └── preencher_checklist.js     # Scripts para preenchimento de checklist
```

## 🎨 Arquivos CSS

### `base.css`
Estilos globais aplicados em todo o sistema:
- Variáveis CSS de cores
- Estilos de cards e badges
- Classes utilitárias (stat-card, notification-badge, etc.)
- Estilos da navbar e footer

### `login.css`
Estilos específicos da página de login:
- Gradiente de fundo
- Card de login centralizado
- Botões personalizados

### `ver_checklist.css`
Estilos para a página de visualização de checklist:
- Prevenção de piscar dos modais
- Transições suaves

### `preencher_checklist.css`
Estilos para a página de preenchimento de checklist:
- Ajustes de bordas
- Espaçamentos específicos

## 🔧 Arquivos JavaScript

### `notificacoes.js`
Sistema de notificações em tempo real via WebSocket:
- Conexão com Socket.IO
- Atualização do contador de notificações
- Exibição de toast notifications
- Som de notificação (opcional)

**Funções principais:**
- `atualizarContadorNotificacoes()` - Atualiza o badge de notificações
- `mostrarToastNotificacao(notificacao)` - Exibe toast na tela
- `playNotificationSound()` - Reproduz som de notificação

### `ver_checklist.js`
Scripts para visualização de checklist:
- Prevenção de múltiplas aberturas de modal
- Limpeza de backdrops residuais
- Gerenciamento de estado dos modais

**Funções principais:**
- `limparBackdrops()` - Remove backdrops fantasma dos modais

### `preencher_checklist.js`
Scripts para preenchimento de checklist:
- Toggle de campos de NC (Não Conformidade)
- Validação dinâmica de formulários
- Gerenciamento de campos obrigatórios

**Funções principais:**
- `toggleNC(itemId)` - Mostra/oculta campos de NC baseado no resultado

## 🔗 Como Usar nos Templates

### Incluindo CSS
```html
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/nome_arquivo.css') }}">
{% endblock %}
```

### Incluindo JavaScript
```html
{% block extra_js %}
<script src="{{ url_for('static', filename='js/nome_arquivo.js') }}"></script>
{% endblock %}
```

## 📝 Boas Práticas

1. **Modularidade**: Cada arquivo tem uma responsabilidade específica
2. **Nomenclatura**: Nomes descritivos e consistentes
3. **Comentários**: Todo arquivo tem comentário explicativo no topo
4. **Organização**: CSS e JS separados por funcionalidade
5. **Performance**: Arquivos carregados apenas quando necessários

## 🎯 Benefícios desta Estrutura

✅ **Manutenibilidade**: Fácil localizar e editar estilos/scripts específicos  
✅ **Performance**: Navegador pode cachear arquivos estáticos  
✅ **Organização**: Separação clara de responsabilidades  
✅ **Escalabilidade**: Simples adicionar novos módulos  
✅ **Debugging**: Mais fácil identificar origem de bugs  
✅ **Reutilização**: Estilos/scripts podem ser compartilhados entre páginas

## 🚀 Próximos Passos (Opcional)

- [ ] Minificar arquivos CSS/JS para produção
- [ ] Adicionar versionamento nos arquivos (cache busting)
- [ ] Implementar SASS/LESS para CSS mais avançado
- [ ] Criar arquivo de constantes JavaScript compartilhadas
- [ ] Adicionar linting automático (ESLint, StyleLint)

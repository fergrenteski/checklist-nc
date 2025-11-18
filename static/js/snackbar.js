// Sistema de Snackbar/Toast Notifications

class SnackbarManager {
    constructor() {
        this.container = null;
        this.init();
    }

    init() {
        // Criar container se não existir
        this.container = document.getElementById('snackbar-container');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.id = 'snackbar-container';
            this.container.className = 'snackbar-container';
            document.body.appendChild(this.container);
        }
    }

    show(message, type = 'info', duration = 3000, title = null) {
        const snackbar = this.createSnackbar(message, type, title);
        this.container.appendChild(snackbar);

        // Auto-remover após duração
        if (duration > 0) {
            setTimeout(() => {
                this.hide(snackbar);
            }, duration);
        }

        return snackbar;
    }

    createSnackbar(message, type, title) {
        const snackbar = document.createElement('div');
        snackbar.className = `snackbar ${type}`;

        // Ícone baseado no tipo
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-x-circle-fill',
            danger: 'bi-x-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };

        // Títulos padrão
        const defaultTitles = {
            success: 'Sucesso!',
            error: 'Erro',
            danger: 'Erro',
            warning: 'Atenção',
            info: 'Informação'
        };

        const icon = icons[type] || icons.info;
        const displayTitle = title || defaultTitles[type] || 'Notificação';

        snackbar.innerHTML = `
            <i class="bi ${icon} snackbar-icon"></i>
            <div class="snackbar-content">
                <div class="snackbar-title">${displayTitle}</div>
                <p class="snackbar-message">${message}</p>
            </div>
            <button class="snackbar-close" aria-label="Fechar">
                <i class="bi bi-x"></i>
            </button>
            <div class="snackbar-progress"></div>
        `;

        // Botão de fechar
        const closeBtn = snackbar.querySelector('.snackbar-close');
        closeBtn.addEventListener('click', () => {
            this.hide(snackbar);
        });

        return snackbar;
    }

    hide(snackbar) {
        snackbar.classList.add('hiding');
        setTimeout(() => {
            if (snackbar.parentNode) {
                snackbar.parentNode.removeChild(snackbar);
            }
        }, 300);
    }

    // Métodos de conveniência
    success(message, title = null, duration = 3000) {
        return this.show(message, 'success', duration, title);
    }

    error(message, title = null, duration = 4000) {
        return this.show(message, 'error', duration, title);
    }

    warning(message, title = null, duration = 3500) {
        return this.show(message, 'warning', duration, title);
    }

    info(message, title = null, duration = 3000) {
        return this.show(message, 'info', duration, title);
    }
}

// Instância global
const snackbar = new SnackbarManager();

// Função auxiliar global para compatibilidade
window.showSnackbar = function(message, type = 'info', title = null, duration = 3000) {
    return snackbar.show(message, type, duration, title);
};

// Função auxiliar para converter flash messages em snackbar
document.addEventListener('DOMContentLoaded', function() {
    // Prevenir execução múltipla
    if (window._snackbarInitialized) return;
    window._snackbarInitialized = true;

    // Converter alerts bootstrap em snackbars (apenas uma vez)
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    const processedMessages = new Set();
    
    alerts.forEach(alert => {
        // Pegar apenas o texto, sem o botão de fechar
        const closeButton = alert.querySelector('.btn-close');
        if (closeButton) closeButton.remove();
        
        const message = alert.textContent.trim();
        
        // Evitar duplicatas
        if (processedMessages.has(message)) {
            alert.remove();
            return;
        }
        processedMessages.add(message);
        
        let type = 'info';
        if (alert.classList.contains('alert-success')) {
            type = 'success';
        } else if (alert.classList.contains('alert-danger')) {
            type = 'danger';
        } else if (alert.classList.contains('alert-warning')) {
            type = 'warning';
        }
        
        // Mostrar snackbar
        snackbar.show(message, type);
        
        // Remover alert original
        alert.remove();
    });
});

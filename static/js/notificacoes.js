/* Notificações JS - Sistema de notificações em tempo real */

// Conectar ao WebSocket
const socket = io();

socket.on('connect', function() {
    console.log('Conectado ao servidor de notificações');
});

socket.on('nova_notificacao', function(data) {
    console.log('Nova notificação recebida:', data);
    
    // Atualizar contador de notificações
    atualizarContadorNotificacoes();
    
    // Mostrar toast de notificação
    mostrarToastNotificacao(data);
    
    // Tocar som (opcional)
    playNotificationSound();
});

function atualizarContadorNotificacoes() {
    fetch('/api/notificacoes/count')
        .then(response => response.json())
        .then(data => {
            const badge = document.getElementById('notification-count');
            const link = document.getElementById('notificacoes-link');
            
            if (data.count > 0) {
                if (!badge) {
                    const newBadge = document.createElement('span');
                    newBadge.className = 'notification-badge';
                    newBadge.id = 'notification-count';
                    newBadge.textContent = data.count;
                    link.appendChild(newBadge);
                } else {
                    badge.textContent = data.count;
                }
            } else if (badge) {
                badge.remove();
            }
        })
        .catch(error => console.error('Erro ao atualizar contador:', error));
}

function mostrarToastNotificacao(notificacao) {
    const toastContainer = document.getElementById('toast-container');
    
    const toastHtml = `
        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-primary text-white">
                <i class="bi bi-bell-fill me-2"></i>
                <strong class="me-auto">${notificacao.titulo}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${notificacao.mensagem}
            </div>
        </div>
    `;
    
    toastContainer.innerHTML = toastHtml;
    
    const toastElement = toastContainer.querySelector('.toast');
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastContainer.innerHTML = '';
    });
}

function playNotificationSound() {
    // Som de notificação (opcional - pode usar um arquivo de áudio)
    const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBze+7O2iVhsMP5r');
    audio.volume = 0.3;
    audio.play().catch(e => console.log('Erro ao tocar som:', e));
}

// Atualizar contador ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    atualizarContadorNotificacoes();
});

/* Ver Checklist JS - Scripts para visualização de checklist */

// Prevenir múltiplas aberturas de modal e piscar
document.addEventListener('DOMContentLoaded', function() {
    // Limpar qualquer backdrop residual
    function limparBackdrops() {
        const backdrops = document.querySelectorAll('.modal-backdrop');
        for (const backdrop of backdrops) {
            backdrop.remove();
        }
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    }
    
    limparBackdrops();
    
    // Configurar cada modal
    const modais = document.querySelectorAll('.modal');
    for (const modal of modais) {
        // Prevenir abertura se já houver modal aberto
        modal.addEventListener('show.bs.modal', function (e) {
            const modalAberto = document.querySelector('.modal.show');
            if (modalAberto && modalAberto !== modal) {
                e.preventDefault();
                e.stopPropagation();
                return false;
            }
        });
        
        // Limpar ao fechar
        modal.addEventListener('hidden.bs.modal', function () {
            limparBackdrops();
        });
        
        // Garantir que o modal não fique preso
        modal.addEventListener('hide.bs.modal', function() {
            setTimeout(limparBackdrops, 300);
        });
    }
    
    // Adicionar evento de clique nos botões de visualizar
    const botoesVisualizar = document.querySelectorAll('[data-bs-toggle="modal"]');
    for (const botao of botoesVisualizar) {
        botao.addEventListener('click', function(e) {
            // Limpar antes de abrir novo modal
            limparBackdrops();
        });
    }
});

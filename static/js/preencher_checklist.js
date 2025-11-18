/* Preencher Checklist JS - Scripts para preenchimento de checklist */

function toggleNC(itemId) {
    const resultado = document.getElementById('resultado_' + itemId).value;
    const ncFields = document.getElementById('nc_fields_' + itemId);
    
    if (resultado === 'Não Conforme') {
        ncFields.style.display = 'block';
        
        // Tornar campos obrigatórios
        const classificacao = ncFields.querySelector('select[name$="_classificacao"]');
        const responsavel = ncFields.querySelector('select[name$="_responsavel"]');
        const acao = ncFields.querySelector('textarea[name$="_acao"]');
        
        if (classificacao) classificacao.required = true;
        if (responsavel) responsavel.required = true;
        if (acao) acao.required = true;
    } else {
        ncFields.style.display = 'none';
        
        // Remover obrigatoriedade
        const classificacao = ncFields.querySelector('select[name$="_classificacao"]');
        const responsavel = ncFields.querySelector('select[name$="_responsavel"]');
        const acao = ncFields.querySelector('textarea[name$="_acao"]');
        
        if (classificacao) classificacao.required = false;
        if (responsavel) responsavel.required = false;
        if (acao) acao.required = false;
    }
}

// Inicializar ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // A inicialização será feita no template com os IDs específicos
    const resultadoSelects = document.querySelectorAll('[id^="resultado_"]');
    for (const select of resultadoSelects) {
        const itemId = select.id.replace('resultado_', '');
        toggleNC(itemId);
    }
});

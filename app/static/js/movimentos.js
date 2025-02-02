async function editarMovimento(id) {
    try {
        const response = await fetch(`/movimento/${id}`);
        const movimento = await response.json();
        
        // Preencher modal de edição
        const form = document.getElementById('formEditarMovimento');
        form.querySelector('[name="cliente"]').value = movimento.cliente;
        form.querySelector('[name="tipo_servico"]').value = movimento.tipo_servico;
        form.querySelector('[name="valor"]').value = movimento.valor;
        form.querySelector('[name="descricao"]').value = movimento.descricao;
        form.querySelector('[name="forma_pagamento"]').value = movimento.forma_pagamento;
        form.dataset.movimentoId = id;
        
        // Mostrar modal
        const modalEditar = new bootstrap.Modal(document.getElementById('modalEditarMovimento'));
        modalEditar.show();
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: 'Erro ao carregar dados do movimento'
        });
    }
}

async function salvarEdicao(event) {
    event.preventDefault();
    const form = event.target;
    const id = form.dataset.movimentoId;
    const formData = new FormData(form);
    
    try {
        const response = await fetch(`/movimento/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(Object.fromEntries(formData))
        });

        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Sucesso',
                text: 'Movimento atualizado com sucesso!',
                showConfirmButton: false,
                timer: 1500
            }).then(() => {
                window.location.reload();
            });
        } else {
            throw new Error('Erro ao atualizar movimento');
        }
    } catch (error) {
        Swal.fire({
            icon: 'error',
            title: 'Erro',
            text: error.message
        });
    }
} 
import sys
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

def verificar_dependencias():
    try:
        import xlsxwriter
        print("Todas as dependências estão instaladas.")
        return True
    except ImportError:
        print("Erro: Módulo xlsxwriter não encontrado.")
        print("Por favor, execute: pip install xlsxwriter")
        return False

def criar_template_excel():
    if not verificar_dependencias():
        return
    
    try:
        # Criar um Excel writer
        writer = pd.ExcelWriter('Controle_Transportadora.xlsx', engine='xlsxwriter')
        workbook = writer.book

        # Formatos
        formato_moeda = workbook.add_format({'num_format': 'R$ #,##0.00'})
        formato_data = workbook.add_format({'num_format': 'dd/mm/yyyy'})
        formato_km = workbook.add_format({'num_format': '#,##0.0'})
        formato_header = workbook.add_format({
            'bold': True,
            'bg_color': '#2c3e50',
            'font_color': 'white',
            'border': 1
        })

        # 1. Aba Movimentos (ajustada - removido controle de KM)
        df_movimentos = pd.DataFrame(columns=[
            'Data',
            'Dia da Semana',
            'Veículo',
            'Cliente',
            'Tipo Serviço',
            'Qtd Volumes',
            'Qtd Locais',
            'Valor Base',
            'Valor Adicional',
            'Valor Total',
            'Forma Pagamento',
            'Data Pagamento',
            'Status'
        ])
        
        # Adicionar algumas linhas de exemplo
        df_movimentos.loc[0] = [
            datetime.now(),
            'Segunda',
            'ABC-1234',
            'Cliente Exemplo',
            'Coleta',
            1,
            2,
            30.00,
            10.00,
            40.00,
            'PIX',
            datetime.now(),
            'Pago'
        ]

        # 2. Nova Aba - Controle Diário
        df_controle_diario = pd.DataFrame(columns=[
            'Data',
            'Veículo',
            'KM Inicial',
            'KM Final',
            'KM Total',
            'Qtd Entregas',
            'Qtd Coletas',
            'Combustível Litros',
            'Valor Combustível',
            'Outras Despesas',
            'Observações'
        ])
        
        # Exemplo de linha para controle diário
        df_controle_diario.loc[0] = [
            datetime.now(),
            'ABC-1234',
            1000,
            1150,
            150,
            5,
            3,
            20.5,
            200.00,
            0.00,
            ''
        ]

        # 3. Aba Despesas (ajustada)
        df_despesas = pd.DataFrame(columns=[
            'Data',
            'Veículo',
            'Tipo Despesa',
            'Descrição',
            'Valor',
            'Forma Pagamento',
            'Observação'
        ])

        # 4. Aba Veículos
        df_veiculos = pd.DataFrame(columns=[
            'Placa',
            'Modelo',
            'Ano',
            'Capacidade Tanque',
            'KM Inicial Mês',
            'KM Atual',
            'Consumo Médio',
            'Data Última Revisão',
            'KM Última Revisão',
            'Próxima Revisão KM',
            'Status'
        ])

        # 5. Aba Clientes
        df_clientes = pd.DataFrame(columns=[
            'Código',
            'Nome/Razão Social',
            'CNPJ/CPF',
            'Endereço',
            'Telefone',
            'Contato',
            'Condição Pagamento',
            'Limite Crédito',
            'Saldo Devedor'
        ])

        # 6. Aba Configurações
        df_config = pd.DataFrame({
            'Parâmetro': [
                'Valor Base Coleta',
                'Valor Adicional por Local',
                'Valor Mínimo Frete',
                'Limite Diário KM',
                'Alerta Revisão (KM)',
                'Limite Crédito Padrão'
            ],
            'Valor': [30.00, 10.00, 30.00, 200, 10000, 1000.00]
        })

        # Salvar cada DataFrame em uma aba
        df_movimentos.to_excel(writer, sheet_name='Movimentos', index=False)
        df_controle_diario.to_excel(writer, sheet_name='Controle Diário', index=False)
        df_despesas.to_excel(writer, sheet_name='Despesas', index=False)
        df_veiculos.to_excel(writer, sheet_name='Veículos', index=False)
        df_clientes.to_excel(writer, sheet_name='Clientes', index=False)
        df_config.to_excel(writer, sheet_name='Configurações', index=False)

        # Aplicar formatos e ajustes nas abas
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            
            # Aplicar formato de cabeçalho em todas as abas
            if sheet_name == 'Movimentos':
                for col_num, value in enumerate(df_movimentos.columns.values):
                    worksheet.write(0, col_num, value, formato_header)
                    
                worksheet.set_column('A:A', 12, formato_data)  # Data
                worksheet.set_column('H:J', 12, formato_moeda)  # Valores
                worksheet.set_column('L:L', 12, formato_data)  # Data Pagamento
                
                # Fórmulas para Valor Total
                for row in range(2, 1002):
                    worksheet.write_formula(
                        f'J{row}',
                        f'=H{row}+I{row}',
                        formato_moeda
                    )
                
                # Validações
                worksheet.data_validation('K2:K1000', {
                    'validate': 'list',
                    'source': ['PIX', 'Dinheiro', 'A Prazo']
                })
                worksheet.data_validation('M2:M1000', {
                    'validate': 'list',
                    'source': ['Pago', 'Pendente']
                })

            elif sheet_name == 'Controle Diário':
                for col_num, value in enumerate(df_controle_diario.columns.values):
                    worksheet.write(0, col_num, value, formato_header)
                
                worksheet.set_column('A:A', 12, formato_data)  # Data
                worksheet.set_column('C:E', 10, formato_km)    # KMs
                worksheet.set_column('H:J', 12, formato_moeda) # Valores
                
                # Fórmulas para cálculos automáticos
                for row in range(2, 1002):
                    # Cálculo do KM Total
                    worksheet.write_formula(
                        f'E{row}',
                        f'=IF(AND(C{row}>0,D{row}>0),D{row}-C{row},"")',
                        formato_km
                    )
                
                # Validações para KMs
                worksheet.data_validation(f'C2:D1000', {
                    'validate': 'integer',
                    'criteria': 'between',
                    'minimum': 0,
                    'maximum': 999999
                })

            elif sheet_name == 'Despesas':
                for col_num, value in enumerate(df_despesas.columns.values):
                    worksheet.write(0, col_num, value, formato_header)
                worksheet.set_column('E:E', 12, formato_moeda)  # Valor

            elif sheet_name == 'Veículos':
                for col_num, value in enumerate(df_veiculos.columns.values):
                    worksheet.write(0, col_num, value, formato_header)
                worksheet.set_column('E:F', 12, formato_km)     # KMs

            elif sheet_name == 'Clientes':
                for col_num, value in enumerate(df_clientes.columns.values):
                    worksheet.write(0, col_num, value, formato_header)
                worksheet.set_column('H:I', 12, formato_moeda)  # Valores

            # Ajustar largura das colunas
            for idx in range(15):  # Número aproximado de colunas
                worksheet.set_column(idx, idx, 15)

        # Salvar o arquivo
        writer.close()
        print(f"Template criado com sucesso! Arquivo: Controle_Transportadora.xlsx")
        
    except Exception as e:
        print(f"Erro ao criar o template: {str(e)}")
        return False

if __name__ == "__main__":
    criar_template_excel() 
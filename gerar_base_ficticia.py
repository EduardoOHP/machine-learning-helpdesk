import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Garante reproducao dos mesmos dados aleatorios
np.random.seed(42)

# Lista de unidades (clientes) fictícias
clientes = ["Matriz - São Paulo", "Filial - Campinas", "Centro de Distribuição - Jundiaí", "Escritório - Rio de Janeiro"]

# Categorias comuns de Helpdesk
categorias = ["Infraestrutura / Rede", "Hardware / Impressoras", "Sistemas / ERP", "Acessos / Senhas", "Suporte Geral"]

# Padrões de problemas e suas respectivas resoluções reais simuladas
templates_chamados = [
    {
        "cat": "Hardware / Impressoras",
        "desc": ["A impressora do financeiro não puxa o papel e está piscando luz vermelha.", "Papel atolado na bandeja traseira da impressora principal.", "Impressora offline para todos os micros do andar."],
        "servico": ["Removido atolamento de papel e realizado teste de impressão.", "Reiniciado o spooler de impressão e reconfigurado IP da impressora.", "Substituído toner e limpos os roletes de tração."]
    },
    {
        "cat": "Acessos / Senhas",
        "desc": ["Esqueci minha senha de acesso ao sistema e estou bloqueado.", "Preciso de redefinição de senha da rede corporativa.", "Usuário novo sem permissão de acesso à pasta compartilhada do RH."],
        "servico": ["Senha temporária gerada e enviada por canal seguro ao colaborador.", "Conta desbloqueada no Active Directory e redefinida a senha padrão.", "Liberada permissão de acesso à pasta solicitada via ACL."]
    },
    {
        "cat": "Infraestrutura / Rede",
        "desc": ["A internet caiu na mesa da recepção e o Teams desconectou.", "Cabo de rede danificado após movimentação de mesa.", "Wi-Fi corporativo não conecta com o notebook novo."],
        "servico": ["Substituído cabo de rede RJ45 e testado link na tomada da parede.", "Reconfigurado o perfil de rede sem fio no notebook do colaborador.", "Porta do switch local reativada após travamento."]
    },
    {
        "cat": "Sistemas / ERP",
        "desc": ["Erro ao emitir nota fiscal no sistema ERP.", "Tela travada ao tentar gerar o relatório de fechamento de caixa.", "O sistema fecha sozinho quando clico em salvar."],
        "servico": ["Limpo o cache do navegador e reiniciada a sessão do usuário no sistema.", "Finalizada sessão travada no banco de dados e revalidado o cadastro.", "Atualizado o cliente do ERP para a versão mais recente."]
    }
]

# Gerar 1.500 chamados fictícios
dados = []
data_inicio_base = datetime(2025, 1, 1)

for i in range(1, 1501):
    ticket_id = 10000 + i
    cliente = np.random.choice(clientes, p=[0.4, 0.3, 0.2, 0.1]) # Matriz tem mais chamados
    
    # Escolhe um template de problema aleatório
    template = np.random.choice(templates_chamados)
    categoria = template["cat"]
    descricao = np.random.choice(template["desc"])
    servico = np.random.choice(template["servico"])
    
    # Datas aleatórias em 2025/2026
    dias_aleatorios = np.random.randint(0, 400)
    horas_aleatorias = np.random.randint(1, 8)
    dt_criacao = data_inicio_base + timedelta(days=dias_aleatorios, hours=np.random.randint(8, 18))
    dt_fim = dt_criacao + timedelta(hours=horas_aleatorias, minutes=np.random.randint(15, 59))
    
    dados.append({
        "Ticket": ticket_id,
        "Cliente": cliente,
        "Tipo de Ticket": "Incidente",
        "Contato": "Usuário Fictício",
        "Técnico": "Analista de TI",
        "Situação": "Finalizado",
        "Categoria": categoria,
        "Data de criação": dt_criacao.strftime("%d/%m/%Y %H:%M"),
        "Data de finalização": dt_fim.strftime("%d/%m/%Y %H:%M"),
        "Descrição": f"Unidade com problema: {descricao}",
        "Serviço realizado": servico
    })

df_ficticio = pd.DataFrame(dados)

# Salva em arquivo Excel
df_ficticio.to_excel("chamados_ficticio.xlsx", index=False)
print("Arquivo 'chamados_ficticio.xlsx' gerado com sucesso!")
import streamlit as st
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Configuração inicial da página
st.set_page_config(
    page_title="IA Helpdesk - Análise de Chamados",
    page_icon="🤖",
    layout="wide"
)

# Baixa a lista de stopwords em português na primeira execução
@st.cache_resource
def carregar_stopwords():
    nltk.download('stopwords', quiet=True)
    palavras_irrelevantes = stopwords.words('portuguese')
    palavras_extras = ['bom', 'dia', 'boa', 'tarde', 'noite', 'olá', 'ola', 'favor', 'gentileza', 'preciso', 'ajuda', 'chamado', 'verificar', 'unidade']
    palavras_irrelevantes.extend(palavras_extras)
    return palavras_irrelevantes

STOPWORDS_PT = carregar_stopwords()

# Função de limpeza de texto (NLP)
def limpar_texto(texto):
    if pd.isna(texto):
        return ""
    texto = str(texto).lower()
    texto = re.sub(r'http\S+', '', texto) # Remove links
    texto = re.sub(r'\d+', '', texto) # Remove números
    texto = re.sub(r'[^\w\s]', ' ', texto) # Remove pontuação
    texto = re.sub(r'\s+', ' ', texto).strip() # Remove espaços extras
    return texto

# Função para carregar e tratar a base
@st.cache_data
def processar_base(arquivo):
    if arquivo.name.endswith('.csv'):
        try:
            df = pd.read_csv(arquivo, sep=None, engine='python')
        except Exception:
            df = pd.read_csv(arquivo, sep=';')
    else:
        df = pd.read_excel(arquivo)

    # Identifica o nome exato da coluna de Ticket (pode variar maiúscula/minúscula)
    coluna_ticket_encontrada = None
    for col in df.columns:
        if col.strip().lower() in ['ticket', 'código', 'codigo', 'id']:
            coluna_ticket_encontrada = col
            break
            
    if coluna_ticket_encontrada and coluna_ticket_encontrada != 'Ticket':
        df = df.rename(columns={coluna_ticket_encontrada: 'Ticket'})

    # Garante que as colunas essenciais existam
    colunas_necessarias = ['Cliente', 'Situação', 'Descrição', 'Serviço realizado', 'Ticket']
    for col in colunas_necessarias:
        if col not in df.columns:
            st.error(f"A coluna obrigatória '{col}' não foi encontrada no arquivo exportado!")
            st.stop()

    # Anonimização básica por segurança
    for col_sensivel in ['Contato', 'Técnico']:
        if col_sensivel in df.columns:
            df = df.drop(columns=[col_sensivel])

    # Filtra apenas chamados finalizados/fechados
    df = df[df['Situação'].astype(str).str.lower().str.contains('finalizado|fechado|concluído|concluido', na=False)].copy()

    # Calcula tempo de resolução se as colunas de data existirem
    if 'Data de criação' in df.columns and 'Data de finalização' in df.columns:
        df['dt_criacao'] = pd.to_datetime(df['Data de criação'], dayfirst=True, errors='coerce')
        df['dt_fim'] = pd.to_datetime(df['Data de finalização'], dayfirst=True, errors='coerce')
        df['horas_resolucao'] = (df['dt_fim'] - df['dt_criacao']).dt.total_seconds() / 3600
        df['horas_resolucao'] = df['horas_resolucao'].apply(lambda x: x if (pd.notna(x) and 0 <= x <= 720) else np.nan)

    # Prepara o texto para a IA
    texto_base = df['Descrição'].fillna('')
    if 'Categoria' in df.columns:
        texto_base = df['Categoria'].fillna('') + " " + texto_base
        
    df['texto_limpo'] = texto_base.apply(limpar_texto)
    df = df[df['texto_limpo'].str.len() > 3]
    
    return df

# Função de Machine Learning (TF-IDF + K-Means)
def executar_kmeans(df_unidade, n_clusters):
    vetorizador = TfidfVectorizer(
        max_features=1500,
        stop_words=STOPWORDS_PT,
        ngram_range=(1, 2)
    )
    
    X = vetorizador.fit_transform(df_unidade['texto_limpo'])
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df_unidade['cluster'] = kmeans.fit_predict(X)
    
    termos = vetorizador.get_feature_names_out()
    centroides_ordenados = kmeans.cluster_centers_.argsort()[:, ::-1]
    
    resultados = []
    for i in range(n_clusters):
        grupo = df_unidade[df_unidade['cluster'] == i]
        qtd = len(grupo)
        if qtd == 0:
            continue
            
        palavras_chave = [termos[ind] for ind in centroides_ordenados[i, :4]]
        tema = " / ".join(palavras_chave).upper()
        
        top_resolucoes = grupo['Serviço realizado'].dropna().value_counts().head(3)
        
        # Pega a descrição e o ticket do primeiro exemplo representativo do grupo
        exemplo_chamado = grupo['Descrição'].dropna().iloc[0] if len(grupo) > 0 else ""
        exemplo_ticket = grupo['Ticket'].dropna().iloc[0] if len(grupo) > 0 else "N/A"
        
        resultados.append({
            'id': i,
            'tema': tema,
            'quantidade': qtd,
            'percentual': (qtd / len(df_unidade)) * 100,
            'resolucoes': top_resolucoes,
            'exemplo': exemplo_chamado,
            'ticket': exemplo_ticket
        })
        
    resultados = sorted(resultados, key=lambda x: x['quantidade'], reverse=True)
    return resultados

# ================= INTERFACE STREAMLIT =================

st.title("🤖 IA Helpdesk: Diagnóstico e Resoluções por Unidade")
st.markdown("Sistema baseado em **Processamento de Linguagem Natural (TF-IDF)** e **Clusterização Não Supervisionada (K-Means)**.")

st.sidebar.header("1. Base de Dados")
arquivo_upado = st.sidebar.file_uploader("Carregue a exportação do seu portal de chamados (.csv ou .xlsx)", type=['csv', 'xlsx'])

if arquivo_upado is not None:
    with st.spinner("Processando a base..."):
        df = processar_base(arquivo_upado)

    st.sidebar.header("2. Filtros de Análise")
    
    contagem_clientes = df['Cliente'].value_counts()
    lista_clientes = contagem_clientes.index.tolist()
    
    cliente_selecionado = st.sidebar.selectbox(
        "Selecione a Unidade (Cliente):",
        options=lista_clientes,
        format_func=lambda x: f"{x} ({contagem_clientes[x]} chamados)"
    )

    num_clusters = st.sidebar.slider(
        "Quantidade de grupos de problemas (K-Means):",
        min_value=2,
        max_value=12,
        value=5
    )

    df_unidade = df[df['Cliente'] == cliente_selecionado].copy()

    st.subheader(f"📊 Panorama da Unidade: {cliente_selecionado}")
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Chamados Finalizados na Unidade", f"{len(df_unidade):,}".replace(",", "."))
    
    if 'horas_resolucao' in df_unidade.columns and df_unidade['horas_resolucao'].notna().any():
        media_horas = df_unidade['horas_resolucao'].mean()
        col2.metric("Tempo Médio de Resolução", f"{media_horas:.1f} horas")
    else:
        col2.metric("Tempo Médio de Resolução", "N/A")
        
    if 'Categoria' in df_unidade.columns:
        cat_principal = df_unidade['Categoria'].mode()[0] if not df_unidade['Categoria'].mode().empty else "N/A"
        col3.metric("Categoria Mais Frequente", str(cat_principal))

    st.divider()

    if len(df_unidade) < num_clusters:
        st.warning(f"Esta unidade possui apenas {len(df_unidade)} chamados finalizados. Diminua o número de grupos na barra lateral.")
    else:
        with st.spinner("A IA está agrupando os problemas..."):
            clusters_encontrados = executar_kmeans(df_unidade, num_clusters)

        st.subheader(f"🧠 Top {len(clusters_encontrados)} Problemas Descobertos pela IA")
        
        for idx, item in enumerate(clusters_encontrados, 1):
            with st.expander(f"#{idx} | Tema: {item['tema']} — {item['quantidade']} chamados ({item['percentual']:.1f}%)", expanded=(idx <= 3)):
                c1, c2 = st.columns([1, 1.5])
                
                with c1:
                    st.markdown(f"**🏷️ Exemplo Referência (Ticket #{item['ticket']}):**")
                    st.info(f"\"{item['exemplo'][:300]}...\"" if len(str(item['exemplo'])) > 300 else f"\"{item['exemplo']}\"")
                
                with c2:
                    st.markdown("**✅ Resoluções mais aplicadas (Serviço realizado):**")
                    if item['resolucoes'].empty:
                        st.write("Nenhuma descrição de serviço registrado.")
                    else:
                        for servico, freq in item['resolucoes'].items():
                            st.success(f"**({freq}x aplicada):** {servico}")

else:
    st.info("👈 Faça o upload do arquivo no menu lateral para iniciar.")
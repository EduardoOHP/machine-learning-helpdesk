=========================================================================
PROJETO DE INTELIGÊNCIA ARTIFICIAL: DIAGNÓSTICO E RESOLUÇÕES DE HELPDESK 
=========================================================================

1. DESCRIÇÃO DO PROJETO
--------------------------------------------------------------------------------
Este projeto aplica técnicas de Inteligência Artificial, Processamento de 
Linguagem Natural (PLN) e Machine Learning Não Supervisionado para analisar 
históricos de chamados de suporte técnico (Helpdesk).

O sistema permite filtrar os atendimentos por unidade/cliente, identificar 
automaticamente os problemas mais recorrentes (ofensores) por meio de 
agrupamento semântico e sugerir as resoluções mais aplicadas pelos técnicos, 
mantendo a rastreabilidade através do número do ticket original.


2. ARQUITETURA E TECNOLOGIAS UTILIZADAS
--------------------------------------------------------------------------------
- Linguagem: Python 3.x
- Interface Web: Streamlit
- Manipulação de Dados: Pandas e NumPy
- Processamento de Linguagem Natural (PLN): NLTK (Stopwords) e Regex
- Machine Learning: Scikit-Learn (TF-IDF Vectorizer + K-Means Clustering)
- Leitura/Escrita de Planilhas: OpenPyXL


3. COMO FUNCIONA O PIPELINE DE INTELIGÊNCIA ARTIFICIAL
--------------------------------------------------------------------------------
Passo 1 - Pré-processamento e Anonimização (LGPD):
  O sistema filtra apenas chamados finalizados, remove dados sensíveis 
  (como nomes de contatos e técnicos), limpa pontuações, números, links e 
  elimina palavras irrelevantes (stopwords e saudações comuns).

Passo 2 - Vetorização de Texto (TF-IDF com N-Grams):
  As descrições dos chamados e suas categorias são transformadas em vetores 
  numéricos ponderados (TF-IDF), considerando palavras isoladas e pares de 
  palavras (bigramas, ex: "não imprime") para capturar o contexto do erro.

Passo 3 - Clusterização Não Supervisionada (K-Means):
  Como os usuários relatam o mesmo problema de maneiras diferentes, o algoritmo 
  K-Means agrupa os chamados por similaridade matemática sem a necessidade de 
  rotulagem prévia.

Passo 4 - Extração de Conhecimento e Recomendação:
  O sistema analisa os centróides de cada grupo para extrair as palavras-chave 
  que definem o tema do problema, ordena os grupos por volume de ocorrência, 
  exibe um ticket real de referência e lista as soluções mais frequentes.


4. ESTRUTURA DE ARQUIVOS
--------------------------------------------------------------------------------
- app.py                          : Código principal da aplicação web e modelo IA.
- gerar_base_ficticia.py          : Script gerador de dados simulados para testes.
- chamados_ficticio.xlsx          : Base de dados fictícia gerada para apresentação.
- README.txt                      : Documentação geral do projeto.


5. INSTALAÇÃO E EXECUÇÃO
--------------------------------------------------------------------------------
Pré-requisito: Ter o Python 3 instalado no sistema.

Passo 1: Instale as bibliotecas necessárias executando no terminal:
  pip install streamlit pandas scikit-learn openpyxl nltk

Passo 2: Gere a base de dados fictícia para demonstração (opcional):
  python gerar_base_ficticia.py

Passo 3: Inicie a aplicação web:
  python -m streamlit run app.py

Passo 4: No navegador que abrir automaticamente, faça o upload do arquivo 
(.csv ou .xlsx) no menu lateral esquerdo, selecione a unidade desejada e 
ajuste o número de clusters (grupos de problemas) no controle deslizante.


6. CONFORMIDADE COM A LGPD (SEGURANÇA DA INFORMAÇÃO)
--------------------------------------------------------------------------------
Para fins acadêmicos e de demonstração pública, o projeto conta com rotina 
automática de descarte de colunas pessoais e acompanha um gerador de massa 
de dados fictícia que replica fielmente a estrutura de exportação do sistema 
sem expor informações reais de clientes ou colaboradores.
================================================================================
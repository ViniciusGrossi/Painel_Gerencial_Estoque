import pandas as pd
import streamlit as st
import plotly.express as px

# Leitura do arquivo CSV e limpeza dos dados
df = pd.read_csv(
    'C:/Users/ALMOX-3/Documents/Projeto_Estoque/Painel Gerencial/database/MOVIMENTOS 08-24.csv', 
    sep=';', 
    encoding='latin1'
)

def data_clean(df):
    df = df.rename(columns={
        'DescriÃ§Ã£o do Material': 'Descrição do Material', 
        'CÃ³digo do Material': 'Codigo do Material',
        'Unidade de NegÃ³cio': 'Unidade de Negócio',
        'Tipo de OperaÃ§Ã£o': 'Tipo de Operação',
        'Empresa': 'Código Empresa',
        'Nome Completo': 'Nome Empresa',
        'Qtd': 'Quantidade'  # Supondo que "Qtd" é a coluna que representa a quantidade
    })
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Codigo do Material'] = df['Codigo do Material'].astype(str)
    df.drop(columns=['Movimento'], errors='ignore', inplace=True)
    
    # Remover itens que contenham 'INATIVADO' ou 'INATIVO'
    df = df[~df['Descrição do Material'].str.contains('INATIVADO|INATIVO|PRESTACAO DE SERVICOS PJ|PRESTACAO DE SERVICOS CONTABEIS|CADASTRO', case=False, na=False)]
    
    # Filtrar por Tipo de Operação
    df = df[df['Tipo de Operação'].isin(['1556A', '2556A'])]
    
    # Converter a coluna 'Quantidade' para numérico
    df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
    
    return df

# Limpeza dos dados
df_limpo = data_clean(df)

# Converter a coluna para string para evitar erros de tipo
df_limpo['Descrição do Material'] = df_limpo['Descrição do Material'].astype(str)

# Adicionar colunas para Mês e Ano
df_limpo['Ano'] = df_limpo['Data'].dt.year
df_limpo['Mês'] = df_limpo['Data'].dt.month

# Interface no Streamlit
st.title("Visualização de Movimentação de Itens por Período")

# Mostrar os 20 itens que mais apareceram
st.sidebar.header("Top 20 Itens Mais Movimentados")
top_20_itens = df_limpo.groupby('Descrição do Material')['Quantidade'].sum().nlargest(20).reset_index()
top_20_itens.columns = ['Descrição do Material', 'Quantidade']
st.sidebar.table(top_20_itens)

# Escolher entre visualização mensal ou anual
visualizacao = st.selectbox("Escolha a visualização:", ["Por Mês", "Por Ano"])

# Filtro opcional para Unidade de Negócio
filtrar_unidade = st.checkbox("Deseja filtrar por Unidade de Negócio?")
if filtrar_unidade:
    unidade_selecionada = st.radio("Selecione a Unidade de Negócio:", [1, 2])

# Filtrar anos e meses disponíveis
anos = sorted(df_limpo['Ano'].dropna().unique())
meses = sorted(df_limpo['Mês'].dropna().unique())

# Campo de seleção para um item específico
# Remover valores nulos antes de exibir a lista
itens_disponiveis = sorted(df_limpo['Descrição do Material'].dropna().unique())
item_selecionado = st.selectbox("Selecione um item:", itens_disponiveis)

if visualizacao == "Por Mês":
    anos_selecionados = st.multiselect("Selecione os anos:", anos, default=anos)
    meses_selecionados = st.multiselect("Selecione os meses:", meses, default=meses)
    df_filtrado = df_limpo[
        (df_limpo['Ano'].isin(anos_selecionados)) & 
        (df_limpo['Mês'].isin(meses_selecionados)) & 
        (df_limpo['Descrição do Material'] == item_selecionado)
    ]
    
    # Aplicar filtro de Unidade de Negócio, se selecionado
    if filtrar_unidade:
        df_filtrado = df_filtrado[df_filtrado['Unidade de Negócio'] == unidade_selecionada]
    
    agrupado = df_filtrado.groupby(['Ano', 'Mês'])['Quantidade'].sum().reset_index()
    soma_total = agrupado['Quantidade'].sum()
    fig = px.line(agrupado, x='Mês', y='Quantidade', line_group='Ano', color='Ano',
                  title=f'Soma da Quantidade de {item_selecionado} por Mês',
                  labels={'Mês': 'Mês', 'Quantidade': 'Soma da Quantidade'})
else:
    anos_selecionados = st.multiselect("Selecione os anos:", anos, default=anos)
    df_filtrado = df_limpo[
        (df_limpo['Ano'].isin(anos_selecionados)) & 
        (df_limpo['Descrição do Material'] == item_selecionado)
    ]
    
    # Aplicar filtro de Unidade de Negócio, se selecionado
    if filtrar_unidade:
        df_filtrado = df_filtrado[df_filtrado['Unidade de Negócio'] == unidade_selecionada]
    
    agrupado = df_filtrado.groupby(['Ano'])['Quantidade'].sum().reset_index()
    soma_total = agrupado['Quantidade'].sum()
    fig = px.line(agrupado, x='Ano', y='Quantidade', 
                  title=f'Soma da Quantidade de {item_selecionado} por Ano',
                  labels={'Ano': 'Ano', 'Quantidade': 'Soma da Quantidade'})

# Exibir métrica da soma total
st.metric(label="Quantidade Total Selecionada", value=soma_total)

# Exibir gráfico
st.plotly_chart(fig)

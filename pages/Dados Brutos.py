import streamlit as st
import requests
import pandas as pd
import time
import io  # Adicione esta importação no topo do seu arquivo

@st.cache_data
def converte_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)  # Retorna ao início do stream
    return output.getvalue()


def mensagem_sucesso():
    sucesso = st.success("Arquivo baixado com sucesso!", icon="✅")
    time.sleep(5)
    sucesso.empty()

st.title('DADOS BRUTOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

with st.expander('Colunas'):
    colunas_selecionadas = st.multiselect('Selecione as colunas', list(dados.columns))
    if colunas_selecionadas:
        dados = dados[colunas_selecionadas]

st.sidebar.title('Filtros')

if 'Produto' in dados.columns:
    with st.sidebar.expander('Nome do produto'):
        produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique())
        if produtos:
            dados = dados[dados['Produto'].isin(produtos)]

if 'Categoria do Produto' in dados.columns:
    with st.sidebar.expander('Categoria do produto'):
        categoria = st.multiselect('Selecione as categorias', dados['Categoria do Produto'].unique())
        if categoria:
            dados = dados[dados['Categoria do Produto'].isin(categoria)]

if 'Preço' in dados.columns:
    with st.sidebar.expander('Preço do produto'):
        preco_min, preco_max = st.slider('Selecione o preço', 0, 5000, (0, 5000))
        if preco_min or preco_max:
            dados = dados[(dados['Preço'] >= preco_min) & (dados['Preço'] <= preco_max)]

if 'Frete' in dados.columns:
    with st.sidebar.expander('Frete da venda'):
        frete_min, frete_max = st.slider('Frete', 0, 250, (0,250))
        if frete_min or frete_max:
            dados = dados[(dados['Frete']>=frete_min) & (dados['Frete']<=frete_max)]

if 'Data da Compra' in dados.columns:
    with st.sidebar.expander('Data da compra'):
        data_compra_min, data_compra_max = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
        
        # Converte as datas selecionadas para datetime64[ns]
        data_compra_min = pd.to_datetime(data_compra_min)
        data_compra_max = pd.to_datetime(data_compra_max)

        # Realiza a filtragem usando os valores convertidos
        if data_compra_min or data_compra_max:
            dados = dados[(dados['Data da Compra'] >= data_compra_min) & (dados['Data da Compra'] <= data_compra_max)]

if 'Vendedor' in dados.columns:
    with st.sidebar.expander('Vendedor'):
        vendedores = st.multiselect('Selecione os vendedores', dados['Vendedor'].unique())
        if vendedores:  # Aplica o filtro apenas se algo for selecionado
            dados = dados[dados['Vendedor'].isin(vendedores)]

if 'Local da compra' in dados.columns:
    with st.sidebar.expander('Local da compra'):
        local_compra = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique())
        if local_compra:
            dados = dados[dados['Local da compra'].isin(local_compra)]

if 'Avaliação da compra' in dados.columns:
    with st.sidebar.expander('Avaliação da compra'):
        avaliacao_min, avaliacao_max = st.slider('Selecione a avaliação da compra', 1, 5, value=(1,5))
        if avaliacao_min or avaliacao_max:
            dados = dados[(dados['Avaliação da compra'] >= avaliacao_min) & (dados['Avaliação da compra'] <= avaliacao_max)]

if 'Tipo de pagamento' in dados.columns:
    with st.sidebar.expander('Tipo de pagamento'):
        tipo_pagamento = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique())
        if tipo_pagamento:
            dados = dados[dados['Tipo de pagamento'].isin(tipo_pagamento)]

if 'Quantidade de parcelas' in dados.columns:
    with st.sidebar.expander('Quantidade de parcelas'):
        qtd_parcelas_min, qdt_parcelas_max = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))
        if qtd_parcelas_min or qdt_parcelas_max:
            dados = dados[(dados['Quantidade de parcelas'] >= qtd_parcelas_min) & (dados['Quantidade de parcelas'] <= qdt_parcelas_max)]

st.dataframe(dados)

st.markdown(f'A tabela possui :blue[{dados.shape[0]}] linhas e :blue[{dados.shape[1]}] colunas')

st.markdown("Escreva um nome para o arquivo")
col1, col2 = st.columns(2)
with col1:
    nome_arquivo = st.text_input("teste", label_visibility='collapsed', value='dados')
    nome_arquivo += '.xlsx'

with col2:
    st.download_button(
        label="Fazer o download da tabela em Excel",
        data=converte_excel(dados),
        file_name=nome_arquivo,
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        on_click=mensagem_sucesso
    )

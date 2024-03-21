import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from tools import formata_numero

# CONFIGURANDO O DASHBOARD

st.set_page_config(layout='wide')

# SETANDO O TÍTULO DA APLICAÇÃO DO STREAMLIT
st.title("DASHBOARD DE VENDAS :shopping_trolley:")

# OBTENDO DADOS VIA API
url = 'https://labdados.com/produtos'
regioes = ['Brasil', 'Centro-Oeste','Nordeste','Norte','Sudeste','Sul']

# Inserindo uma barra lateral
st.sidebar.title("Filtros")
regiao = st.sidebar.selectbox('Região', regioes)
if regiao == 'Brasil':
    regiao = ''

todos_anos = st.sidebar.checkbox('Dados de todo o período', value=True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023)

query_string = {
    'regiao':regiao.lower(),
    'ano':ano
}

response = requests.get(url, params=query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

# TABELAS

# Tabelas de Receita
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index= True).sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)

# Tabelas de Quantidade de Vendas

vendas_estados = pd.DataFrame(dados.groupby('Local da compra')['Preço'].count())
vendas_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra','lat', 'lon']].merge(vendas_estados, left_on = 'Local da compra', right_index = True).sort_values('Preço', ascending = False)

vendas_mensal = pd.DataFrame(dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'ME'))['Preço'].count()).reset_index()
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

vendas_categorias = pd.DataFrame(dados.groupby('Categoria do Produto')['Preço'].count().sort_values(ascending = False))


# Tabelas Vendedores

vendedores = pd.DataFrame(dados.groupby("Vendedor")['Preço'].agg(['sum','count']))

# GRÁFICOS

# Gráficos de Receita

fig_mapa_receita = px.scatter_geo(receita_estados, lat = 'lat', lon= 'lon', scope= 'south america',
                                  size='Preço', template='seaborn', hover_name='Local da compra',
                                  hover_data= {'lat':False, 'lon':False},
                                  title='Receita por estado')

fig_receita_mensal = px.line(receita_mensal, x='Mês', y='Preço', markers=True, range_y=(0, receita_mensal.max()),
                             color="Ano", line_dash='Ano', title='Receita Mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y='Preço',
                             text_auto=True,
                             title='Top estados (Receita)')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categorias,
                                text_auto=True,
                                title='Receita por Categoria')
fig_receita_categorias.update_layout(yaxis_title='Receita')

fig_mapa_vendas = px.scatter_geo(vendas_estados, 
                     lat = 'lat', 
                     lon= 'lon', 
                     scope = 'south america', 
                     #fitbounds = 'locations', 
                     template='seaborn', 
                     size = 'Preço', 
                     hover_name ='Local da compra', 
                     hover_data = {'lat':False,'lon':False},
                     title = 'Vendas por estado',
                     )

fig_vendas_mensal = px.line(vendas_mensal, 
              x = 'Mes',
              y='Preço',
              markers = True, 
              range_y = (0,vendas_mensal.max()), 
              color = 'Ano', 
              line_dash = 'Ano',
              title = 'Quantidade de vendas mensal')

fig_vendas_mensal.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x ='Local da compra',
                             y = 'Preço',
                             text_auto = True,
                             title = 'Top 5 estados'
)

fig_vendas_estados.update_layout(yaxis_title='Quantidade de vendas')

fig_vendas_categorias = px.bar(vendas_categorias, 
                                text_auto = True,
                                title = 'Vendas por categoria')
fig_vendas_categorias.update_layout(showlegend=False, yaxis_title='Quantidade de vendas')

# VISUALIZAÇÃO NO STREAMLIT

# ABAS

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:
    # COLUNAS
    col1, col2 = st.columns(2)
    # MÉTRICAS
    with col1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)

    with col2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'))
        st.plotly_chart(fig_mapa_vendas, use_container_width = True)
        st.plotly_chart(fig_vendas_estados, use_container_width = True)

    with coluna2:
        st.metric('Quantidade de vendas', formata_numero(dados.shape[0]))
        st.plotly_chart(fig_vendas_mensal, use_container_width = True)
        st.plotly_chart(fig_vendas_categorias, use_container_width = True)

with aba3:
    qtde_vendedores = st.number_input("Quantidade de Vendedores", 2, 10, 5)
    # COLUNAS
    col1, col2 = st.columns(2)
    # MÉTRICAS
    with col1:
        st.metric("Receita", formata_numero(dados['Preço'].sum(), 'R$'))
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores),
                                        x='sum', 
                                        y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtde_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtde_vendedores} vendedores (Receita)')
        st.plotly_chart(fig_receita_vendedores)

    with col2:
        st.metric("Quantidade de Vendas", formata_numero(dados.shape[0]))
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtde_vendedores),
                                        x='count', 
                                        y=vendedores[['count']].sort_values('count', ascending=False).head(qtde_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtde_vendedores} vendedores (Quantidade de Vendas)')
        st.plotly_chart(fig_vendas_vendedores)


















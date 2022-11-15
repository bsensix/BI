#!/usr/bin/env python
# coding: utf-8

# ##  Bibliotecas:

# In[1]:


import pandas as pd 
import numpy as np 
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import date
import base64
import openpyxl


# ##  Barra Lateral: 

# In[2]:


#Barra Lateral
barra_lateral = st.sidebar.empty()
image = Image.open('Logo-Escuro.png')
st.sidebar.image(image)
                     
tipo_analise = st.sidebar.selectbox("📊 Tipo de Ánalise:", ['Página Principal','Curvas Fenológicas', 'Falhas de Plantio', 'Fertilidade do Solo', 'Produtividade'])

if tipo_analise == 'Página Principal':
    st.sidebar.markdown("- [FieldScan](https://fieldscan.sensix.com.br/login_user/)")
    st.sidebar.markdown("- [Site](https://sensix.ag/)")
    st.sidebar.markdown("- [Blog](https://blog.sensix.ag/)")
    st.sidebar.markdown("- [Linkedin](https://br.linkedin.com/company/sensixag)")
    
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
    background-image: url("https://diarural.com.br/wp-content/uploads/2021/10/agricultor2.jpg");
    background-size: cover;
    }

    [data-testid="stHeader"] {
    background: rgba(0,0,0,0);
    }

    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)
    image2 = Image.open('titulo.png')
    st.image(image2)
    
    st.markdown('')
               
    image3 = Image.open('fluxo.png')
     
    st.image(image3)  
    
       
if tipo_analise == 'Curvas Fenológicas':
    #Barra Lateral
    barra_lateral = st.sidebar.empty()
    st.title('Índices de Vegetação 🛰️')

    # Upload Arquivo csv 
    uploaded_files = st.sidebar.file_uploader("- Upload dos Dados ⬇️")
  
    tabela = pd.read_excel(uploaded_files)   
    tabela = tabela.rename_axis('ID').reset_index()
    
    #Coluna Data0
    tabela['Data0'] = tabela['Data']

    #Coluna Data1
    tabela['Data1'] = tabela['Data']
    tabela['Data1'] = tabela['Data1'].apply(lambda x: str(x)[6:10]).astype('int')
    tabela['Data1'] = tabela['Data1'].astype(str)
    tabela['Data1'] = '01/01/' + tabela['Data1'] 

    #Coluna Data 2
    tabela['Data0'] = pd.to_datetime(tabela['Data0'],dayfirst=True)
    tabela['Data1'] = pd.to_datetime(tabela['Data1'])

    #Nº Dias 
    tabela['N Dias'] = tabela['Data0'] - tabela['Data1']
    tabela['N Dias'] = tabela['N Dias'].astype('timedelta64[D]')
    tabela['N Dias'].astype(int)
    
    #Calculo Curva Fenologica Padrão
    tabela['NDRE'] = 0.562 + (0.00976 * tabela['N Dias']) - (0.0000899 * tabela['N Dias']**2) + (0.000000178* tabela['N Dias']**3)
    tabela['NDVI'] = 0.615 + (0.0124 * tabela['N Dias'])  -  (0.00011 * tabela['N Dias']**2) + (0.000000215* tabela['N Dias']**3)
    
    #Comparação Índices FS
    tabela['P_NDRE'] = (tabela['Índice Médio NDRE']/tabela['NDRE'])*100
    tabela['P_NDVI'] = (tabela['Índice Médio NDVI']/tabela['NDVI'])*100
    tabela.head()

    tabela_sem_nuvens = tabela.query('P_NDRE > 70 & P_NDVI > 70')
    tabela_com_nuvens = tabela.query('P_NDRE <= 70 & P_NDVI <= 70')
    
    col1, col2, col3 = st.columns(3)
    
    #Selecionar Fazenda
    filtro_fazenda = col1.selectbox('🚜 Selecione a Fazenda:',(tabela_sem_nuvens['Fazenda']))
    tabela_fazenda = tabela_sem_nuvens['Fazenda'] == filtro_fazenda
    tabela_fazenda = tabela_sem_nuvens[tabela_fazenda]

    #Selecionar Talhão 
    filtro_talhao = col2.selectbox('🔲 Selecione o Talhão:',(tabela_fazenda['Talhão']))
    tabela_talhao = tabela_fazenda['Talhão'] == filtro_talhao
    tabela_talhao = tabela_fazenda[tabela_talhao]

    number =  col3.number_input('📶 Grau da Regressão Polinomial:')

    col1, col2 = st.columns(2)

    # N° imagens Satelite
    n_imagens= tabela_talhao.nunique()
    n_planet = n_imagens["ID"]
    col1.metric(label="📷 N° de Imagens:", value= n_planet)

    #Média de imagens 
    def numOfDays(date1, date2):
         return (date2-date1).days
     
    date1 = tabela_talhao['Data'].iloc[0]
    date1 = date1.split("/")
    dia_date1=int(date1[0])
    mes_date1=int(date1[1])
    ano_date1=int(date1[2])
    date1=date(ano_date1,mes_date1,dia_date1)

    date2 = tabela_talhao['Data'].iloc[-1]
    date2 = date2.split("/")
    dia_date2=int(date2[0])
    mes_date2=int(date2[1])
    ano_date2=int(date2[2])
    date2=date(ano_date2,mes_date2,dia_date2)

    n_dias=numOfDays(date1, date2)
    media_imagens = int(n_dias/n_planet)
    col2.metric(label= "ℹ️ Resolução Temporal: ", value = media_imagens, delta = "dias",delta_color="off")

    #Gráfico NDVI
    st.markdown('### Curva Fenológica NDVI')
    fig = px.scatter(tabela_talhao, x='Data', y='Índice Médio NDVI', opacity=0.7)
    fig.update_xaxes(title = 'Data')
    fig.update_yaxes(title = 'Índice Médio NDVI')
    #Modelo Regressão
    modelo = np.poly1d(np.polyfit(tabela_talhao['ID'], tabela_talhao['Índice Médio NDVI'],number))
    y5 = modelo(tabela_talhao['ID'])
    fig.add_traces(go.Scatter(x=tabela_talhao['Data'], y=y5, name="Regressão Polinomial"))
 
    st.plotly_chart(fig)
    
    #Gráfico NDRE
    st.markdown('### Curva Fenológica NDRE')
    fig = px.scatter(tabela_talhao, x='Data', y='Índice Médio NDRE', opacity=0.7)
    fig.update_xaxes(title = 'Data')
    fig.update_yaxes(title = 'Índice Médio NDRE')
    #Modelo Regressão
    modelo = np.poly1d(np.polyfit(tabela_talhao['ID'], tabela_talhao['Índice Médio NDRE'],number))
    y5 = modelo(tabela_talhao['ID'])
    fig.add_traces(go.Scatter(x=tabela_talhao['Data'], y=y5, name="Regressão Polinomial"))

    st.plotly_chart(fig)  

    #Tabela com os Dados 
    st.title('Links Mapas:')
    df = tabela_talhao[['Data','Link','Índice Médio NDRE','Índice Médio NDVI']]
    st.dataframe(df)
    
if tipo_analise == 'Falhas de Plantio':
    #Barra Lateral
    barra_lateral = st.sidebar.empty()
    # Upload Arquivo csv 
    uploaded_files = st.sidebar.file_uploader("- Upload dos Dados ⬇️")
    tabela = pd.read_excel(uploaded_files)
    st.title('Relatório de Falhas de Plantio 🌿')

    tab1, tab2 = st.tabs([" 📈 Dados Gerais", " 🚜 Dados Fazenda e Talhão"])

    with tab1:

        col1, col2, col3, col4, col5 = st.columns(5)
        #Métricas Gerais
      
        area_total_planilha = round(tabela['Área'].sum(),2)
        col1.metric(label="Área Total :", value= area_total_planilha)

        total_falhas_planilha = tabela['Total de falhas [km]'].sum()
        col2.metric(label="Total Falhas [Km] :", value= total_falhas_planilha)

        media_km_ha = round((total_falhas_planilha / area_total_planilha),4)
        col3.metric(label="Falhas [Km/ha] :", value= media_km_ha)

        fazenda = tabela['Fazenda'].drop_duplicates()
        n_fazendas = fazenda.count()
        col4.metric(label='Nº Fazendas:', value= n_fazendas)

        n_mapas = tabela['Cliente'].count()
        col5.metric(label='Nº Mapas:', value= n_mapas)
        
        col1, col2 = st.columns(2)
    
        agrupados = tabela.groupby('Fazenda').sum()
        agrupados = agrupados.reset_index()
    
        
        total_min = agrupados['Total de falhas [km]'].min()
        total_max = agrupados['Total de falhas [km]'].max()
    
        faz_min = agrupados.loc[agrupados['Total de falhas [km]'] == total_min]
        faz_max = agrupados.loc[agrupados['Total de falhas [km]'] == total_max]
    
        
        col1.subheader('🔽 Menor Nº de Falhas:')
        col1.markdown(faz_min['Fazenda'].to_string())   
        col2.subheader('🔼 Maior Nº de Falhas:')
        col2.markdown(faz_max['Fazenda'].to_string())
    
        st.title('% Falhas por Fazenda')
    
        fig = go.Figure()
        fig.add_trace(go.Bar(
        x=tabela['Fazenda'],
        y=tabela['Falhas 0,5m a 1m [%]'],
        name='Falhas 0,5m a 1m [%]',
        marker_color='green'
        ))
        fig.add_trace(go.Bar(
        x=tabela['Fazenda'],
        y=tabela['Falhas 1m a 1,5m [%]'],
        name='Falhas 1m a 1,5m [%]',
        marker_color='yellow'
        ))
        fig.add_trace(go.Bar(
        x=tabela['Fazenda'],
        y=tabela['Falhas 1,5m a 2,5m [%]'],
        name='Falhas 1,5m a 2,5m [%]',
        marker_color='orange'
        ))
        fig.add_trace(go.Bar(
        x=tabela['Fazenda'],
        y=tabela['Falhas maiores que 2,5m [%]'],
        name='Falhas Maiores que 2,5m [%]',
        marker_color='red'
        ))
           
        st.plotly_chart(fig)  
    
        #Tabela com os Dados 
        st.markdown('**Mapeamentos** ') 
        df = tabela[['Fazenda','Talhão','Link']]
        st.dataframe(df)
    
    
    with tab2:
        #Selecionar Fazenda
        filtro_fazenda = st.selectbox('Selecione a Fazenda:',(tabela['Fazenda']))
        tabela_fazenda = tabela['Fazenda'] == filtro_fazenda
        tabela_fazenda = tabela[tabela_fazenda]
    
        col1, col2, col3, col4, col5 = st.columns(5)
        area_fazenda = round(tabela_fazenda['Área'].sum(),2)
        col1.metric(label="Área Fazenda :", value= area_fazenda)

        total_km_05a1_fazenda = round(tabela_fazenda['Falhas 0,5m a 1m [km]'].sum(),2)
        col2.metric(label="0,5m a 1m [km]:", value= total_km_05a1_fazenda, delta = "Falhas",delta_color="inverse")

        total_km_1a15_fazenda = round(tabela_fazenda['Falhas 1m a 1,5m [km]'].sum(),2)
        col3.metric(label="1m a 1,5m [km]:", value= total_km_1a15_fazenda, delta = "Falhas",delta_color="inverse")

        total_km_15a25_fazenda = round(tabela_fazenda['Falhas 1,5m a 2,5m [km]'].sum(),2)
        col4.metric(label="1,5m a 2,5m [km]:", value= total_km_15a25_fazenda, delta = "Falhas",delta_color="inverse")

        total_km_25_fazenda = round(tabela_fazenda['Falhas maiores que 2,5m [km]'].sum(),2)
        col5.metric(label="> que 2,5m [km]:", value= total_km_25_fazenda, delta = "Falhas",delta_color="inverse")
    
        st.markdown('**Falhas por Talhões em Km**')
    
        fig = go.Figure()
        fig.add_trace(go.Bar(
        x=tabela_fazenda['Talhão'],
        y=tabela_fazenda['Falhas 0,5m a 1m [km]'],
        name='Falhas 0,5m a 1m [km]',
        marker_color='green'
        ))
        fig.add_trace(go.Bar(
        x=tabela_fazenda['Talhão'],
        y=tabela_fazenda['Falhas 1m a 1,5m [km]'],
        name='Falhas 1m a 1,5m [km]',
        marker_color='yellow'
        ))
        fig.add_trace(go.Bar(
        x=tabela_fazenda['Talhão'],
        y=tabela_fazenda['Falhas 1,5m a 2,5m [km]'],
        name='Falhas 1,5m a 2,5m [km]',
        marker_color='orange'
        ))
        fig.add_trace(go.Bar(
        x=tabela_fazenda['Talhão'],
        y=tabela_fazenda['Falhas maiores que 2,5m [km]'],
        name='Falhas Maiores que 2,5m [km]',
        marker_color='red'
        ))
           
        st.plotly_chart(fig)
        
if tipo_analise == 'Fertilidade do Solo':     
    barra_lateral = st.sidebar.empty()
    st.title('Estatística Ánalise do Solo 🌱')
    # Upload Arquivo csv 
    uploaded_files1 = st.sidebar.file_uploader("Upload Planilha 1️⃣:")

    uploaded_files2 = st.sidebar.file_uploader("Upload Planilha 2️⃣:")

    uploaded_files3 = st.sidebar.file_uploader("Upload Planilha 3️⃣:")

    tabela1 = pd.read_excel(uploaded_files1)   

    tabela2 = pd.read_excel(uploaded_files2)   

    tabela3 = pd.read_excel(uploaded_files3)   
    
    col1, col2, col3 = st.columns(3)

    #Talhão 1 
    col1.subheader('Talhão 1️⃣')
    filtro_talhao1 = col1.selectbox('Selecione Nutriente 1:',(tabela1.columns[1:50]))
    tabela_met1 = tabela1[filtro_talhao1] 
    tabela_met1 = pd.DataFrame(tabela_met1)
    tabela_met1 = tabela_met1.iloc[1:]
    tabela_met1 = tabela_met1[filtro_talhao1].astype(float)

    #Talhão 2 
    col2.subheader('Talhão 2️⃣')
    filtro_talhao2 = col2.selectbox('Selecione Nutriente 2:',(tabela2.columns[1:50]))
    tabela_met2 = tabela2[filtro_talhao2] 
    tabela_met2 = pd.DataFrame(tabela_met2)
    tabela_met2 = tabela_met2.iloc[1:]
    tabela_met2 = tabela_met2[filtro_talhao2].astype(float)

    #Talhão 3
    col3.subheader('Talhão 3️⃣')
    filtro_talhao3 = col3.selectbox('Selecione Nutriente 3:',(tabela3.columns[1:50]))
    tabela_met3 = tabela3[filtro_talhao3] 
    tabela_met3 = pd.DataFrame(tabela_met3)
    tabela_met3 = tabela_met3.iloc[1:]
    tabela_met3 = tabela_met3[filtro_talhao3].astype(float)


    #Métricas 1

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    min = tabela_met1.min()
    col1.metric(label="Mín:", value= min)
    max = tabela_met1.max()
    col2.metric(label="Máx:", value= max)
    med = round(tabela_met1.mean(),2)
    col1.metric(label="Média:", value= med)
    var = round(tabela_met1.var(),2)
    col2.metric(label="Variância:", value= var)

    min2 = tabela_met2.min()
    col3.metric(label="Mín:", value= min2)
    max2 = tabela_met2.max()
    col4.metric(label="Máx:", value= max2)
    med2 = round(tabela_met2.mean(),2)
    col3.metric(label="Média:", value= med2)
    var2 = round(tabela_met2.var(),2)
    col4.metric(label="Variância:", value= var2)


    min3 = tabela_met3.min()
    col5.metric(label="Mín:", value= min3)
    max3 = tabela_met3.max()
    col6.metric(label="Máx:", value= max3)
    med3 = round(tabela_met3.mean(),2)
    col5.metric(label="Média:", value= med3)
    var3 = round(tabela_met3.var(),2)
    col6.metric(label="Variância:", value= var3)

    st.title('Valores da Amostragem 📉')

    col1, col2, col3 = st.columns(3)

    df1 = tabela_met1
    df2 = tabela_met2
    df3 = tabela_met3

    col1.dataframe(df1)
    col2.dataframe(df2)
    col3.dataframe(df3)
    
    


# In[ ]:





# In[ ]:





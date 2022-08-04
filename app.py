import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
# from streamlit.state.session_state import SessionState
import streamlit as st
st.set_page_config(page_title='Ergotec', page_icon=None, layout='wide', initial_sidebar_state='auto', menu_items=None)
from forex_python.converter import CurrencyRates


def load_data():
    # Tasa de Cambio
    c = CurrencyRates()
    rates = c.get_rates('USD')
    tasa_cambio = rates['EUR']

    # Archivo
    cols = ['MARCA', 'Nº Producto Sistema', 'Nº referencia cruzada', 'Descripción',
            'Cantidad', 'PL / FOB UNITARIO', 'Grupo_Producto']
    return (
        pd.read_excel('./data/Ventas.xlsx')[cols]
        .rename(columns={'PL / FOB UNITARIO':'PL'})), tasa_cambio


def percent(num,percent):
    num = num * (100 - percent) / 100
    return num

def merge(df, tasa_de_cambio, emp=None):
    df = df.copy()
    if emp:
        empresas = emp
    else:
        empresas = {
            'DVO':      { 'factor': 160, 'flete': 25, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'Milani':   { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'MIDJ':     { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'Arper':    { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'OMP':      { 'factor': 320, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'Mohawk':   { 'factor': 285, 'flete': 15, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': 1              },
            'Viccaribe':{ 'factor': 130, 'flete': 45, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'Sunon':    { 'factor': 400, 'flete': 114,'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': 1              },
            'Marte':    { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'Castel':   { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'Confisa':  { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
            'EUN':      { 'factor': 160, 'flete': 30, 'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio }}
    df_emp = pd.DataFrame.from_dict(empresas).T

    df = pd.merge(df,df_emp, left_on='MARCA',right_index=True)

    df['FOB'] = df['PL'] * df['Cantidad'] * ((100-df['descuento_marca'])/100) * df['tasa_de_cambio']
    df['FOB+Flete'] = df['FOB'] * (100 + df['flete'])/100
    df['CIF'] = df['FOB+Flete'] + (df['FOB+Flete'] * 0.28)
    df['CT'] = df['CIF'] * (100 + df['gravamen'] + df['aduanas'])/100
    df['PV'] = df['CT'] * df['factor']/100
    return df

def group(df):

    g = df.groupby(by=['MARCA','Grupo_Producto']).sum().reset_index()
    g = g[['MARCA','Grupo_Producto','Cantidad','FOB','Cargo Maritimo','Costo Total','PV','Ganancias']].sort_values(by=['Ganancias'], ascending=False)
    g = pd.io.formats.style.Styler(g,precision=0,thousands=',')

def sidebar(df, last_discount):
    st.sidebar.title('Variables')

    descuento = st.sidebar.slider('Descuento',0,last_discount,0)

    factores = st.sidebar.expander('Factores')
    DVO_factor = factores.slider('DVO',100,450,160)
    Milani_factor = factores.slider('Milani',100,450,160)
    MIDJ_factor = factores.slider('MIDJ',100,450,160)
    Arper_factor = factores.slider('Arper',100,450,160)
    OMP_factor = factores.slider('OMP',100,450,320)
    Mohawk_factor = factores.slider('Mohawk',100,450,285)
    Viccaribe_factor = factores.slider('Viccaribe',100,450,130)
    Sunon_factor = factores.slider('Sunon',100,450,400)
    Marte_factor = factores.slider('Marte',100,450,160)
    Kastel_factor = factores.slider('Kastel',100,450,160)
    Confisa_factor = factores.slider('Confisa',100,450,160)
    EUN_factor = factores.slider('EUN',100,450,160)

    fletes = st.sidebar.expander('Flete')
    DVO_flete = fletes.slider('DVO',0,100,25)
    Milani_flete = fletes.slider('Milani',0,100,30)
    MIDJ_flete = fletes.slider('MIDJ',0,100,30)
    Arper_flete = fletes.slider('Arper',0,100,30)
    OMP_flete = fletes.slider('OMP',0,100,30)
    Mohawk_flete = fletes.slider('Mohawk',0,100,15)
    Viccaribe_flete = fletes.slider('Viccaribe',0,100,45)
    Sunon_flete = fletes.slider('Sunon',0,150,114)
    Marte_flete = fletes.slider('Marte',0,100,30)
    Kastel_flete = fletes.slider('Kastel',0,100,30)
    Confisa_flete = fletes.slider('Confisa',0,100,30)
    EUN_flete = fletes.slider('EUN',0,100,30)

    empresas = {
        'DVO':      { 'factor': DVO_factor,      'flete': DVO_flete,      'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'Milani':   { 'factor': Milani_factor,   'flete': Milani_flete,   'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'MIDJ':     { 'factor': MIDJ_factor,     'flete': MIDJ_flete,     'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'Arper':    { 'factor': Arper_factor,    'flete': Arper_flete,    'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'OMP':      { 'factor': OMP_factor,      'flete': OMP_flete,      'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'Mohawk':   { 'factor': Mohawk_factor,   'flete': Mohawk_flete,   'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': 1              },
        'Viccaribe':{ 'factor': Viccaribe_factor,'flete': Viccaribe_flete,'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'Sunon':    { 'factor': Sunon_factor,    'flete': Sunon_flete,    'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': 1              },
        'Marte':    { 'factor': Marte_factor,    'flete': Marte_flete,    'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'Castel':   { 'factor': Kastel_factor,   'flete': Kastel_flete,   'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'Confisa':  { 'factor': Confisa_factor,  'flete': Confisa_flete,  'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio },
        'EUN':      { 'factor': EUN_factor,      'flete': EUN_flete,      'descuento_marca': 55, 'gravamen': 20, 'aduanas': 3, 'tasa_de_cambio': tasa_de_cambio }}

    return empresas, descuento

def treemap(df):
    df = df.copy()
    df['Demas'] = df['CT'] - df['FOB']

    df['Ganancias'] = np.where(df['Ganancias']>=0,df['Ganancias'],0)
    # st.write(df)
    df = pd.melt(df, id_vars=['MARCA','Grupo_Producto'], value_vars=['FOB','Demas','Ganancias'],
        var_name='Tipo', value_name='Valor')
    df['Valor'] = df['Valor'].astype(int)
    df = df.groupby(by=['MARCA','Grupo_Producto','Tipo']).sum().reset_index()

    df['Proceso'] = np.where(df['Tipo']=='Ganancias','Ganancias','Costo')
    fig = px.treemap(df, path=['Proceso','Tipo','MARCA','Grupo_Producto'], values='Valor', color='MARCA', hover_name='Valor',)
    fig.update_traces(root_color="lightgrey")
    fig.update_layout(margin = dict(t=50, l=25, r=25, b=25), width=800, title='Distribucion del Dinero')
    return fig

def graph(data, descuento=10):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=data['descuentos'], y=data['CT'], name="CT", fill=None, marker_color='blue',),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=data['descuentos'], y=data['PV'], name="PV", fill='tonexty', marker_color='crimson'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=data['descuentos'], y=data['roi'], name="Retorno de Inversion", marker_color='gold'),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(x=[descuento,descuento],y=[0,max(data['PV'])], name='Descuento', 
            mode='lines', line=dict(dash='dash'),marker_color='black', showlegend=False,),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=[descuento], y=[data['PV'][descuento]], mode='markers+text', 
            text=[f"{int(data['PV'][descuento]):,}"],
            textposition='bottom left',
            marker_color='crimson',
            showlegend=False
            ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=[descuento], y=[data['roi'][descuento]], mode='markers+text', 
            text=[f'{round(data["roi"][descuento])}%'],
            textposition='top right',
            marker_color='gold',
            showlegend=False
            ),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        # title_text=f"Precio y Retorno por Descuento\nGanancias: {int(data['ganancias'][descuento]):,}",
        width=500,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.90
    ))
    # fig.add_hline(y=end)


    # Set x-axis title
    fig.update_xaxes(title_text="Descuento", ticks='inside', showgrid=False, ticksuffix='%', zeroline=False)

    # Set y-axes titles
    fig.update_yaxes(
        title_text="<b>Ventas</b> USD$", 
        ticks='inside',secondary_y=False, 
        showgrid=False, zeroline=False, 
        title_font=dict(color='crimson'), 
        range=[max(data['CT']),max(data['PV'])])
    fig.update_yaxes(
        title_text="<b>Retorno</b> de Inversion", 
        ticks='inside', 
        ticksuffix='%',
        secondary_y=True, 
        showgrid=False, 
        title_font=dict(color='gold'), 
        zeroline=False,
        range=[0,max(data['roi'])])

    return fig

def discount(df):
    df = df.copy()
    sums = df[['PV','CT']].sum()
    start = sums[0]
    end = sums[1]

    descuentos = []
    PVs = []
    ganancias = []
    roi = []
    CTs = []

    for i in range(100):
        y = percent(start, i)
        g = y-end
        roi.append((g*100/end))
        descuentos.append(i)
        PVs.append(y)
        ganancias.append(g)
        CTs.append(end)
        if y < end:
            break

    return {'descuentos': descuentos, 'roi': roi,'PV': PVs, 'ganancias':ganancias,'CT':CTs}

def make_tables(df, descuento):
    df = df.copy().groupby(by=['MARCA','Grupo_Producto'])['FOB','CT','PV'].sum()
    df['PV'] = df['PV'] * ((100-descuento)/100)
    df['Ganancias'] = df['PV'] - df['CT']
    df = df.reset_index()
    summary = df.copy().groupby('MARCA')['CT','PV','Ganancias'].sum().sort_values(by=['Ganancias'], ascending=False)
    summary.loc['Total'] = summary.sum(numeric_only=True)
    summary = pd.io.formats.style.Styler(summary,precision=0,thousands=',')
    return summary, df

# st.markdown('<style></style>', unsafe_allow_html=True)
df, tasa_de_cambio = load_data()
initial_merge = merge(df, tasa_de_cambio)
if __name__ == '__main__':
    # col2.write(initial_merge)
    # col1.write(discount(initial_merge))
    data_to_discount = discount(initial_merge)
    last_discount = data_to_discount['descuentos'][-1]
    
    emp, descuento = sidebar(df, last_discount)
    t = "<div>Hello there my <span style='color: red; font-size: 20px;'>name <span class='bold'>yo</span> </span> is <span class='highlight red'>Fanilo <span class='bold'>Name</span></span></div>"

    # st.markdown(t, unsafe_allow_html=True)

    df = merge(df, tasa_de_cambio, emp)
    discounted_dict = discount(df)
    # st.write(discounted_dict)
    col1, col2 = st.columns([3,2])
    col1.plotly_chart(graph(discounted_dict, descuento=descuento))
    col2.markdown("## Ganancias")
    col2.markdown(f"#### <span style='color:crimson'>{round(discounted_dict['PV'][descuento]):,}</span> - <span style='color:blue'>{round(discounted_dict['CT'][descuento]):,}</span>",
        unsafe_allow_html=True)
    col2.markdown(f"#### <span style='color:green'>{round(discounted_dict['ganancias'][descuento]):,}</span> | <span style='color:gold'>{round(discounted_dict['roi'][descuento])}%</span>",
        unsafe_allow_html=True)


    summary, desagregado = make_tables(df, descuento)
    col2.write(summary)
    st.plotly_chart(treemap(desagregado))
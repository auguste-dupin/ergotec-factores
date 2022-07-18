import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
# from streamlit.state.session_state import SessionState
import streamlit as st
st.set_page_config(page_title='Ergotec', page_icon=None, layout='wide', initial_sidebar_state='auto', menu_items=None)

def load_data():
    cols = ['MARCA', 'Nº Producto Sistema', 'Nº referencia cruzada', 'Descripción',
            'Cantidad', 'PL / FOB UNITARIO', 'Grupo_Producto']
    return (
        pd.read_excel('./data/Ventas.xlsx')[cols]
        .rename(columns={'PL / FOB UNITARIO':'FOB'}))


def percent(num,percent):
    num = num * (100 - percent) / 100
    return num

def merge(df,emp=None):
    df = df.copy()
    if emp:
        empresas = emp
    else:
        empresas = {
            'DVO':      { 'factor': 160, 'cargo': 45 },
            'Milani':   { 'factor': 160, 'cargo': 45 },
            'MIDJ':     { 'factor': 160, 'cargo': 45 },
            'Arper':    { 'factor': 160, 'cargo': 45 },
            'OMP':      { 'factor': 320, 'cargo': 45 },
            'Mohawk':   { 'factor': 285, 'cargo': 43 },
            'Viccaribe':{ 'factor': 130, 'cargo': 61 },
            'Sunon':    { 'factor': 400, 'cargo': 66 },
            'Marte':    { 'factor': 160, 'cargo': 60 },
            'Castel':   { 'factor': 160, 'cargo': 45 },
            'Confisa':  { 'factor': 160, 'cargo': 66 },
            'EUN':      { 'factor': 160, 'cargo': 30 }}
    df_emp = pd.DataFrame.from_dict(empresas).T

    df = pd.merge(df,df_emp, left_on='MARCA',right_index=True)

    df['PV'] = df['FOB'] * (df['factor'] + df['cargo'])/100
    df['Cargo Maritimo'] = df['FOB'] * df['cargo']/100
    df['Costo Total'] = df['FOB'] + df['Cargo Maritimo']
    df['Ganancias'] = df['PV'] - df['Costo Total']
    

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

    cargos = st.sidebar.expander('Cargos Maritimos')
    DVO_cargo = cargos.slider('DVO',0,100,45)
    Milani_cargo = cargos.slider('Milani',0,100,45)
    MIDJ_cargo = cargos.slider('MIDJ',0,100,45)
    Arper_cargo = cargos.slider('Arper',0,100,45)
    OMP_cargo = cargos.slider('OMP',0,100,45)
    Mohawk_cargo = cargos.slider('Mohawk',0,100,43)
    Viccaribe_cargo = cargos.slider('Viccaribe',0,100,61)
    Sunon_cargo = cargos.slider('Sunon',0,100,66)
    Marte_cargo = cargos.slider('Marte',0,100,60)
    Kastel_cargo = cargos.slider('Kastel',0,100,45)
    Confisa_cargo = cargos.slider('Confisa',0,100,66)
    EUN_cargo = cargos.slider('EUN',0,100,30)

    empresas = {
        'DVO':      { 'factor':DVO_factor ,     'cargo': DVO_cargo },
        'Milani':   { 'factor':Milani_factor ,  'cargo': Milani_cargo },
        'MIDJ':     { 'factor':MIDJ_factor ,    'cargo': MIDJ_cargo },
        'Arper':    { 'factor':Arper_factor ,   'cargo': Arper_cargo },
        'OMP':      { 'factor':OMP_factor ,     'cargo': OMP_cargo },
        'Mohawk':   { 'factor':Mohawk_factor ,  'cargo': Mohawk_cargo },
        'Viccaribe':{ 'factor':Viccaribe_factor,'cargo': Viccaribe_cargo},
        'Sunon':    { 'factor':Sunon_factor ,   'cargo': Sunon_cargo },
        'Marte':    { 'factor':Marte_factor ,   'cargo': Marte_cargo},
        'Kastel':   { 'factor':Kastel_factor ,  'cargo': Kastel_cargo },
        'Confisa':  { 'factor':Confisa_factor , 'cargo': Confisa_cargo },
        'EUN':      { 'factor':EUN_factor ,     'cargo': EUN_cargo }}

    return empresas, descuento

def treemap(df):
    df = df.copy()    

    df = pd.melt(df, id_vars=['MARCA','Grupo_Producto'], value_vars=['FOB','Cargo Maritimo','Ganancias'],
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
        go.Scatter(x=data['descuentos'], y=data['gastos'], name="Gastos", fill=None, marker_color='blue'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=data['descuentos'], y=data['ventas'], name="Ganancias", fill='tonexty', marker_color='crimson'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=[descuento], y=[data['gastos'][descuento]], mode='markers+text', 
            text=[f"{int(data['gastos'][descuento]):,}"],
            textposition='bottom right',
            marker_color='blue',
            showlegend=False
            ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=data['descuentos'], y=data['roi'], name="Retorno de Inversion", marker_color='gold'),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(x=[descuento,descuento],y=[0,max(data['ventas'])], name='Descuento', mode='lines', line=dict(dash='dash'),marker_color='black',),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=[descuento], y=[data['ventas'][descuento]], mode='markers+text', 
            text=[f"{int(data['ventas'][descuento]):,}"],
            textposition='top right',
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
        width=600
    )
    # fig.add_hline(y=end)


    # Set x-axis title
    fig.update_xaxes(title_text="Descuento", ticks='inside', showgrid=False, ticksuffix='%')

    # Set y-axes titles
    fig.update_yaxes(title_text="<b>Ventas</b> USD$", ticks='inside',secondary_y=False, showgrid=False, rangemode='tozero')
    fig.update_yaxes(title_text="<b>Retorno</b> de Inveriosn", ticks='inside', ticksuffix='%',secondary_y=True, showgrid=False, title_font=dict(color='gold'))

    return fig

def discount(df):
    df = df.copy()
    sums = df[['PV','Costo Total','Ganancias']].sum()
    start = sums[0]
    end = sums[1]

    descuentos = []
    roi = []
    ventas = []
    ganancias = []
    gastos = []
    for i in range(100):
        y = percent(start, i)
        g = y-end
        roi.append((g*100/end))
        descuentos.append(i)
        ventas.append(y)
        ganancias.append(g)
        gastos.append(end)
        if y < end:
            break
    return {'descuentos': descuentos,'roi': roi,'ventas': ventas, 'ganancias':ganancias,'gastos':gastos}

def make_tables(df, descuento):
    df = df.copy().groupby(by=['MARCA','Grupo_Producto'])['FOB','Cargo Maritimo','Costo Total','PV'].sum()
    df['PV'] = df['PV'] * ((100-descuento)/100)
    df['Ganancias'] = df['PV'] - df['Costo Total']
    df = df.reset_index()
    summary = df.copy().groupby('MARCA')['Costo Total','PV','Ganancias'].sum()
    summary.loc['Total'] = summary.sum(numeric_only=True)
    summary = pd.io.formats.style.Styler(summary,precision=0,thousands=',')
    return summary, df


df = load_data()
initial_merge = merge(df)
if __name__ == '__main__':
    data_to_discount = discount(initial_merge)
    last_discount = data_to_discount['descuentos'][-1]
    
    emp, descuento = sidebar(df, last_discount)

    df = merge(df,emp)
    discounted_dict = discount(df)
    # st.write(discounted_dict)
    col1, col2 = st.columns([3,1])
    col1.plotly_chart(graph(discounted_dict, descuento=descuento))
    col2.title(f"Ganancias: {round(discounted_dict['ganancias'][descuento]):,}")
    summary, desagregado = make_tables(df, descuento)
    col2.write(summary)
    st.plotly_chart(treemap(desagregado))
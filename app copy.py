import pandas as pd
import plotly.graph_objects as go
# from streamlit.state.session_state import SessionState
import streamlit as st
st.set_page_config(page_title='Finanzas Ergotec', page_icon=None, layout='wide', initial_sidebar_state='auto', menu_items=None)


##### Variables
unidad = 'k USD'
width = 500
height = 280

class Modelo:
    def __init__(self, gastos=85, beneficio=150, ratio=73):
        self.GASTOS = gastos
        self.BENEFICIOS = beneficio
        self.RATIO = ratio
        self.venta_minima = self.GASTOS + self.BENEFICIOS
        self.get_ventas()
        self.get_GPs()
        self.make_df()
        self.gp = 100-self.RATIO
        self.venta = int((self.BENEFICIOS + self.GASTOS)*10000/(self.gp))/100
        self.P = int(self.BENEFICIOS*10000/self.venta)/100
        self.get_reduction_values()

    def update_gastos(self, gasto):
        self.GASTOS = gasto

    def update_beneficios(self, beneficio):
        self.BENEFICIOS = beneficio

    def update_ratio(self, ratio):
        self.RATIO = ratio

    def get_reduction_values(self):
        # Beneficios
        ben = int((self.venta_reduction(self.gp, self.BENEFICIOS*0.99, self.GASTOS)-self.venta)*100)/100
        gp = int((self.venta_reduction(self.gp+1, self.BENEFICIOS, self.GASTOS)-self.venta)*100)/100
        gas = int((self.venta_reduction(self.gp, self.BENEFICIOS, self.GASTOS*0.99)-self.venta)*100)/100

        self.reduction_values = [gp,ben,gas,0]

    def venta_reduction(self, gp, beneficio, gasto):
        return (beneficio+gasto)*100/gp


    def get_gross_profit(self, venta, beneficios, gastos):
        gp = int((beneficios + gastos)*10000/venta)/100
        return [gp, 100-gp]

    def get_GPs(self):
        gps = []
        ratios = []
        for venta in self.ventas:
            gp, r = self.get_gross_profit(venta, self.BENEFICIOS, self.GASTOS)
            gps.append(gp)
            ratios.append(r)
        self.gps = gps
        self.ratios = ratios

    def get_ventas(self, n=20):
        ventas = []
        venta_temp = self.venta_minima
        for i in range(n):
            ventas.append(venta_temp)
            venta_temp += 50
        self.ventas = ventas

    def make_df(self):
        df = pd.DataFrame()
        df['Gross_Profit'] = self.gps
        df['Ratio_Costo/Venta'] = self.ratios
        df['Venta'] = self.ventas
        self.df = df

def plot_curvas(modelo, st):
    fig = go.Figure()

    # Gross Profit
    fig.add_trace(
        go.Scatter(
            x=modelo.ventas,
            y=modelo.gps,
            name='Gross Profit',
            mode='lines',
            line=dict(width=3)
        )
    )

    # Ratio
    fig.add_trace(
        go.Scatter(
            x=modelo.ventas,
            y=modelo.ratios,
            name='Ratio Costo/Venta',
            mode='lines',
            line=dict(width=3)
        )
    )

    # Lineas
    # Linea Horizontal Upper
    fig.add_trace(
        go.Scatter(
            x=[v.venta_minima,v.venta],
            y=[v.RATIO,v.RATIO],
            name='linea horizontal up',
            mode='lines',
            showlegend=False,
            line=dict(
                color='#333',
                width=1,
                dash='dash'
            )
        )
    )


    # Linea Vertical
    fig.add_trace(
        go.Scatter(
            x=[v.venta,v.venta,v.venta],
            y=[0,v.gp,v.RATIO],
            name='linea vertical',
            mode='lines',
            showlegend=False,
            line=dict(
                color='#333',
                width=1,
                dash='dash'
            )
        )
    )

    # Marker
    fig.add_trace(
        go.Scatter(
            x=[v.venta],
            y=[v.gp],
            name='Punto de encuentro',
            text=f'GP: {v.gp}%, Ventas: {v.venta}',
            textposition='top left',
            hoverinfo='text',
            mode='markers',
            marker_symbol='x',
            marker=dict(size=10)
        )
    )

    fig.update_layout(
        xaxis_title=f"Ventas ({unidad})",
        yaxis_title="%",
        margin=dict(t=0,l=0,b=10,r=0),
        width=width+100,
        height=height,
        # legend_title="Legend Title",
        # font=dict(
        #     family="Courier New, monospace",
        #     size=18,
        #     color="RebeccaPurple"
        # )
    )

    st.plotly_chart(fig)

def plot_reduccion(modelo, st):
    fig = go.Figure()

    # Reduccion
    fig.add_trace(
        go.Bar(
            x=v.reduction_values,
            y=['Ratio','Beneficios','Gasto','Normal'],
            text=v.reduction_values,
            textposition='auto',
            name='Reduccion',
            orientation='h',
            marker_color='lightgreen'
        )
    )

    # Linea Vertical
    fig.add_trace(
        go.Scatter(
            x=[-10,-10],
            y=['Normal','Ratio'],
            name='linea vertical',
            mode='lines',
            showlegend=False,
            line=dict(
                color='#333',
                width=1,
                dash='dash'
            )
        )
    )

    fig.update_layout(
        barmode='stack',
        xaxis_title=f"Reduccion en Ventas ({unidad})",
        # yaxis_title=f"Reduccion en Ventas ({unidad})",
        # yaxis=dict(side='right'),
        width=250,
        height=height,
        margin=dict(t=0,l=0,b=0,r=0),
        plot_bgcolor='rgb(255,255,255)',
        # width=width+30,
        # height=height-40,
        # margin=dict(t=0,l=45,b=10,r=0),
        showlegend=False)

    # fig.update_yaxes(position=1)
    # fig.update_yaxes(side:'right')
    st.plotly_chart(fig)


st.session_state.gasto = 85
if __name__ == '__main__':

    ##### Sidebar
    st.sidebar.title('Variables')
    beneficio = st.sidebar.slider(f'Beneficios ({unidad})',0,250,150)
    ratio = st.sidebar.slider('Ratio Costo/Venta (%)',0,100,73)

    costos_general = st.sidebar.radio(f'Costo Indirecto ({unidad})', ['Agregado', 'Desagregado'])
    if costos_general == 'Agregado':
        gastos = st.sidebar.slider('Costo Indirecto Agregado',0,150,st.session_state.gasto)
        st.session_state.gasto = gastos
    else:
        comision = st.sidebar.slider('Comision',0,35,int(st.session_state.gasto*0.29))
        inst_sup = st.sidebar.slider('Instalacion y Supervision',0,25,int(st.session_state.gasto*0.23))
        instalacion = st.sidebar.slider('Instalacion',0,15,int(st.session_state.gasto*0.15))
        almacen = st.sidebar.slider('Almacen',0,15,int(st.session_state.gasto*0.12))
        transporte = st.sidebar.slider('Transporte',0,5,int(st.session_state.gasto*0.04))
        materiales = st.sidebar.slider('Materiales',0,5,int(st.session_state.gasto*0.04))
        error = st.sidebar.slider('Error en Ordenes',0,6,int(st.session_state.gasto*0.05))
        otros_gastos = st.sidebar.slider('Otros',0,15,int(st.session_state.gasto*0.12))
        gastos = (
            comision + inst_sup + instalacion +
            almacen + transporte + materiales +
            error + otros_gastos
        )
        st.session_state.gasto = gastos
        st.sidebar.markdown(f'Gastos totales: {gastos}')

    st.session_state.gasto = gastos
    # st.write(st.session_state.gasto)


    v = Modelo(gastos, beneficio, ratio)

    ##### Main Page
    col1, col2, col3, col4 = st.columns((2,1,1,1))
    col1.title('Finanzas')

    col2.metric('Gross Profit (%)',v.gp)
    col3.metric(f'Ventas Mensuales ({unidad})',v.venta)
    col4.metric(f'Ventas Anuales ({unidad})',(int(v.venta*1200))/100)
    col1, col2 = st.columns((2,3))
    col2.markdown(f"""
    Para alcanzar los beneficios de **{beneficio} {unidad}**
    se necesita vender **{v.venta} {unidad}** mensual. 
    Con ese ratio el GP es **{v.gp}%**
    """)

    # st.markdown('### Graficas')
    col1, col2 = st.columns((3,1))

    col1.markdown("**Curva de GP y Ratio C/V con Ventas**")
    plot_curvas(v, col1)
    col2.markdown('**Reduccion Marginal (-1%)**')
    plot_reduccion(v, col2)

    # col1.markdown(f"""
    # Para alcanzar los beneficios de **{beneficio} {unidad}**
    # se necesita vender **{v.venta} {unidad}** mensual\n
    # Con ese ratio el GP es **{v.gp}%**
    # """)
    st.markdown("""
    Dependiendo del **Punto de encuentro** en el GP, las variables pueden reducir las ventas de distintas maneras.
    Mientras menos inclinada se encuentra la curva en el **Punto de encuentro**, mas sensible son las ventas a una reduccion del GP.
    """)
    # plot_reduccion(v, col1)

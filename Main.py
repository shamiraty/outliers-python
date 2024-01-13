import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import norm

st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")

# load Style css
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

theme_plotly = None

#sidebar
html_code = '''
<iframe src="https://free.timeanddate.com/clock/i95di01a/n71/szw160/szh160/hocfff/hbw6/cf100/hgr0/hcw2/hcd88/fan2/fas20/fdi70/mqc000/mqs3/mql13/mqw4/mqd94/mhc000/mhs3/mhl13/mhw4/mhd94/mmc000/mml5/mmw1/mmd94/hwm2/hhs2/hhb18/hms2/hml80/hmb18/hmr7/hscf09/hss1/hsl90/hsr5" frameborder="0" width="160" height="160"></iframe>

'''
st.sidebar.markdown(html_code, unsafe_allow_html=True)
# load dataset
dataset = pd.read_excel("data.xlsx")

outliers = []

#parameters
mean = np.mean(dataset.Demand)
std_dev = np.std(dataset.Demand)
z_score = (dataset.Demand - mean) / std_dev
probability = norm.cdf(z_score)

#add more columns to dataset
dataset['Z score'] = z_score
dataset['PDF'] = probability

#show table
with st.expander("DISTRIBUTION TABLE"):
    showData = st.multiselect('Filter: ', dataset.columns,default=["Product","Demand","Z score","PDF"])
    st.dataframe(dataset[showData], use_container_width=True)

#detect outlier
def detect_outliers(data):
    threshold = 3
    mean = np.mean(data)
    std = np.std(data)

    for i in data:
        z_score = (i - mean) / std
        if np.abs(z_score) > threshold:
            outliers.append(i)
    return outliers
outlier_pt = detect_outliers(dataset.Demand)
st.info(f"**Outliers:** {outlier_pt}")



div1,div2=st.columns(2)

try:
 with div1:
  st.subheader(f"**NORMAL CURVE X~N**({round(mean, 2)},{round(std_dev, 2)})")
  # Create a normal distribution curve
  x_values = np.linspace(mean - 4 * std_dev, mean + 4 * std_dev, 1000)
  y_values = norm.pdf(x_values, mean, std_dev)

  # Create trace for normal distribution curve
  trace_curve = go.Scatter(x=x_values, y=y_values, mode='lines', name='Normal Distribution Curve')

  # Add threshold lines at ±3 standard deviations
  trace_threshold_neg = go.Scatter(x=[mean - 3 * std_dev, mean - 3 * std_dev], y=[0, max(y_values)], mode='lines', name='-3 SD Threshold', line=dict(color='red', dash='dash'))
  trace_threshold_pos = go.Scatter(x=[mean + 3 * std_dev, mean + 3 * std_dev], y=[0, max(y_values)], mode='lines', name='+3 SD Threshold', line=dict(color='red', dash='dash'))

  # Highlight the outliers
  outliers = np.abs(z_score) > 3
  trace_outliers = go.Scatter(x=np.array(dataset.Demand)[outliers], y=norm.pdf(np.array(dataset.Demand)[outliers], mean, std_dev),
                           mode='markers', name='Outliers', marker=dict(color='red'))

  # Show only threshold values on the X-axis
  layout = go.Layout(xaxis=dict(tickvals=[mean - 3 * std_dev, mean, mean + 3 * std_dev],
                              ticktext=['-3 SD Threshold', 'Mean', '+3 SD Threshold']),
                   yaxis=dict(title='Probability Density'),
                   title='',
                   legend=dict(x=0.7, y=1))

  # Create figure
  fig = go.Figure(data=[trace_curve, trace_threshold_neg, trace_threshold_pos, trace_outliers], layout=layout)

  # Display the plot using Streamlit
  st.plotly_chart(fig,use_container_width=True)
except:
    st.warning("Error")



with div2:
 try:

    demand_quartiles = dataset.Demand.quantile([0.25, 0.5, 0.75])
    demand_min = dataset.Demand.min()
    demand_max = dataset.Demand.max()

    quartiles_table = pd.DataFrame({
        'Quartiles': ['First Quartile (Q1)', 'Second Quartile (Q2)', 'Third Quartile (Q3)', 'Min', 'Max'],
        'Value': [demand_quartiles[0.25], demand_quartiles[0.5], demand_quartiles[0.75], demand_min,
                  demand_max]
    })

    fig = px.box(dataset.Demand, y=dataset.Demand, title='', points='all')
    fig.update_layout(
        xaxis=dict(showgrid=True),  # Adding grids on x-axis
        yaxis=dict(showgrid=True),  # Adding grids on y-axis
        showlegend=True,  # Show legend

    )
    st.subheader(f"**BOX PLOT**(max:{round(demand_max, 2)}, min: {round(demand_min, 2)})")
    c1, c2 = st.columns(2)
    st.table(quartiles_table)
    st.plotly_chart(fig, use_container_width=True)
 except:
    st.info("Error")
import streamlit as st
import pandas as pd
import data_generator
import analytics
import visualizations

# Page Configuration
st.set_page_config(
    page_title="Painel de Learning Analytics - PRODITEC",
    page_icon="🎓",
    layout="wide"
)

# Title and Introduction
st.title("🎓 Painel de Learning Analytics")
st.markdown("""
Este painel oferece uma visão geral do desempenho e engajamento dos cursistas nas turmas do PRODITEC.
Utilize o menu lateral para filtrar por turma e explorar os dados.
""")

# Sidebar for Filters
st.sidebar.header("Filtros")
selected_class = st.sidebar.selectbox("Selecione a Turma", ["Todas", "Turma A", "Turma B"])

# Load Data
@st.cache_data
def load_data():
    return data_generator.get_all_data()

df = load_data()

# Filter Data
if selected_class != "Todas":
    df_filtered = df[df['Turma'] == selected_class].copy()
else:
    df_filtered = df.copy()

# Calculate Metrics
df_filtered = analytics.calculate_average(df_filtered)
at_risk_students = analytics.identify_at_risk(df_filtered)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Alunos", len(df_filtered))
with col2:
    st.metric("Média Geral da Turma", f"{df_filtered['Média Geral'].mean():.2f}")
with col3:
    st.metric("Alunos em Risco (< 6.0)", len(at_risk_students), delta_color="inverse")
with col4:
    st.metric("Taxa de Engajamento (Média Acessos)", int(df_filtered['Acessos'].mean()))

st.divider()

# Visualizations Section
st.subheader("📊 Visão Geral do Desempenho")

tab1, tab2, tab3 = st.tabs(["Distribuição de Notas", "Desempenho por Módulo", "Engajamento vs. Notas"])

with tab1:
    st.plotly_chart(visualizations.plot_grade_distribution(df_filtered), use_container_width=True)

with tab2:
    st.plotly_chart(visualizations.plot_module_performance(df_filtered), use_container_width=True)

with tab3:
    # Perform clustering for this visualization to show groups
    df_clustered = analytics.perform_clustering(df_filtered)
    st.plotly_chart(visualizations.plot_engagement_vs_performance(df_clustered), use_container_width=True)

st.divider()

# Machine Learning Section
st.subheader("🤖 Análise de Grupos (Clustering)")
st.markdown("""
Utilizando algoritmos de Machine Learning (K-Means), identificamos grupos de alunos com comportamentos semelhantes
baseados em suas notas e engajamento.
""")

# Ensure clustering is done (if not already for the tab above)
if 'Cluster' not in df_filtered.columns:
    df_filtered = analytics.perform_clustering(df_filtered)

col_ml1, col_ml2 = st.columns([2, 1])

with col_ml1:
    st.plotly_chart(visualizations.plot_cluster_profiles(df_filtered), use_container_width=True)

with col_ml2:
    st.markdown("### Detalhes dos Grupos")
    cluster_counts = df_filtered['Cluster'].value_counts().sort_index()
    for cluster_id, count in cluster_counts.items():
        avg_grade = df_filtered[df_filtered['Cluster'] == cluster_id]['Média Geral'].mean()
        st.info(f"**Grupo {cluster_id}**: {count} alunos - Média Geral: {avg_grade:.1f}")

st.divider()

# Detailed Data View
st.subheader("📋 Lista de Alunos")
st.dataframe(
    df_filtered.style.highlight_between(left=0, right=5.9, subset=['Média Geral'], color='#ffcdd2'),
    use_container_width=True
)

# Download Button
csv = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Baixar Dados em CSV",
    data=csv,
    file_name='dados_learning_analytics.csv',
    mime='text/csv',
)

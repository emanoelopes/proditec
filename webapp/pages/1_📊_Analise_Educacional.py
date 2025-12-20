import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Análise Educacional", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    # Use absolute path or relative to main app
    # Assuming running from root or webapp
    # Try to find the file
    possible_paths = [
        '/home/emanoel/proditec/processed_data.csv',
        'processed_data.csv',
        '../processed_data.csv'
    ]
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            # Ensure numeric
            if 'Media_Final' in df.columns:
                 df['Media_Final'] = pd.to_numeric(df['Media_Final'], errors='coerce')
            return df
    return None

def main():
    st.title("📊 Painel Analítico Educacional")
    st.markdown("Monitoramento de desempenho, frequência e status dos discentes.")

    df = load_data()

    if df is None:
        st.error("Dados não encontrados. Execute o script de consolidação primeiro (eda_analysis.py).")
        return

    # Sidebar Filters
    st.sidebar.header("Filtros")
    
    cities = sorted(df['Cidade'].astype(str).unique())
    selected_cities = st.sidebar.multiselect("Cidade", cities)

    states = sorted(df['Estado'].astype(str).unique())
    selected_states = st.sidebar.multiselect("Estado", states)

    cargos = sorted(df['Cargo'].astype(str).unique())
    selected_cargos = st.sidebar.multiselect("Cargo", cargos)

    # Apply filters
    filtered_df = df.copy()
    if selected_cities:
        filtered_df = filtered_df[filtered_df['Cidade'].isin(selected_cities)]
    if selected_states:
        filtered_df = filtered_df[filtered_df['Estado'].isin(selected_states)]
    if selected_cargos:
        filtered_df = filtered_df[filtered_df['Cargo'].isin(selected_cargos)]

    # --- KPIs ---
    total_students = len(filtered_df)
    avg_grade = filtered_df['Media_Final'].mean()
    
    # Calculate Approval Rate (Assuming 'Status Final' contains 'Aprovado')
    # Or calculate based on Grade >= 7
    if 'Status Final' in filtered_df.columns:
        approved = filtered_df[filtered_df['Status Final'].astype(str).str.contains('Aprovado', case=False, na=False)]
        approval_rate = (len(approved) / total_students * 100) if total_students > 0 else 0
    else:
        # Fallback calculation
        approved = filtered_df[filtered_df['Media_Final'] >= 7.0]
        approval_rate = (len(approved) / total_students * 100) if total_students > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Alunos", total_students)
    col2.metric("Média Geral", f"{avg_grade:.2f}")
    col3.metric("Taxa de Aprovação", f"{approval_rate:.1f}%")
    
    # Data Quality Warning
    missing_grades = filtered_df['Media_Final'].isna().sum()
    if missing_grades > 0:
        col4.warning(f"{missing_grades} alunos sem nota final")

    st.markdown("---")

    # --- Charts ---
    
    # 1. Performance by Municipality (Bar Chart) - REQUESTED
    st.subheader("Desempenho por Município")
    
    # Group by City
    city_stats = filtered_df.groupby('Cidade').agg({
        'Media_Final': 'mean',
        'Nome': 'count'
    }).reset_index().sort_values('Media_Final', ascending=False)
    
    # Filter out Cities with very few students to avoid noise? Or showing all.
    # User asked for "Performance", let's show top 20 if too many
    
    fig_city = px.bar(
        city_stats.head(20), # Limit to top 20 for readability if many
        x='Cidade', 
        y='Media_Final',
        color='Media_Final',
        title='Média Final por Município (Top 20)',
        hover_data=['Nome'],
        labels={'Media_Final': 'Média das Notas', 'Nome': 'Qtd Alunos'},
        text_auto='.2f',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_city, use_container_width=True)

    col_chart1, col_chart2 = st.columns(2)

    # 2. Grade Distribution (Histogram)
    with col_chart1:
        st.subheader("Distribuição das Notas")
        fig_hist = px.histogram(
            filtered_df, 
            x='Media_Final', 
            nbins=20, 
            title='Histograma de Notas Finais',
            color_discrete_sequence=['#3366cc']
        )
        fig_hist.add_vline(x=7.0, line_dash="dash", line_color="red", annotation_text="Meta (7.0)")
        st.plotly_chart(fig_hist, use_container_width=True)

    # 3. Status Breakdown
    with col_chart2:
        st.subheader("Status Final")
        if 'Status Final' in filtered_df.columns:
            status_counts = filtered_df['Status Final'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_pie = px.pie(
                status_counts, 
                values='Count', 
                names='Status', 
                title='Distribuição de Status',
                hole=0.4
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Coluna 'Status Final' não encontrada para gráfico de pizza.")

    # --- Data Table ---
    st.subheader("Dados Detalhados")
    cols_to_show = ['Nome', 'Cidade', 'Estado', 'Cargo', 'Media_Final', 'Status Final', 'Status_Frequencia']
    # Filter existing columns
    cols_to_show = [c for c in cols_to_show if c in filtered_df.columns]
    
    st.dataframe(
        filtered_df[cols_to_show].sort_values('Media_Final', ascending=False),
        use_container_width=True
    )

if __name__ == "__main__":
    main()

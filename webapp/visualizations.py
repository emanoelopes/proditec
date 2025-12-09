import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_grade_distribution(df):
    """
    Plots a histogram of the average grades.
    """
    fig = px.histogram(
        df, 
        x="Média Geral", 
        nbins=10, 
        title="Distribuição das Médias Gerais",
        color_discrete_sequence=['#636EFA'],
        labels={"Média Geral": "Média Final", "count": "Número de Alunos"}
    )
    fig.update_layout(bargap=0.1)
    return fig

def plot_engagement_vs_performance(df):
    """
    Scatter plot of Engagement (Logins) vs. Performance (Average Grade).
    """
    # Use 'Cluster' for color if available
    color_col = 'Cluster' if 'Cluster' in df.columns else None
    
    fig = px.scatter(
        df, 
        x="Acessos", 
        y="Média Geral", 
        color=color_col,
        size="Postagens no Fórum",
        hover_data=["Nome"],
        title="Engajamento vs. Desempenho",
        labels={"Acessos": "Número de Acessos", "Média Geral": "Média Final"},
        color_continuous_scale=px.colors.sequential.Viridis
    )
    return fig

def plot_module_performance(df):
    """
    Box plot comparing performance across different modules.
    """
    module_cols = [col for col in df.columns if "Módulo" in col]
    
    # Melt dataframe for boxplot
    df_melted = df.melt(id_vars=["Nome"], value_vars=module_cols, var_name="Módulo", value_name="Nota")
    
    fig = px.box(
        df_melted, 
        x="Módulo", 
        y="Nota", 
        title="Desempenho por Módulo",
        color="Módulo"
    )
    return fig

def plot_cluster_profiles(df):
    """
    Radar chart or parallel coordinates to show cluster profiles.
    For simplicity, we'll use a grouped bar chart of averages per cluster.
    """
    if 'Cluster' not in df.columns:
        return None
        
    cluster_avg = df.groupby('Cluster')[['Média Geral', 'Acessos', 'Postagens no Fórum']].mean().reset_index()
    
    # Normalize for better visualization if needed, but raw values are okay for bar chart
    # We might need to scale them to fit on same chart, or just show separate charts.
    # Let's do a normalized parallel coordinates plot which is cool for clusters.
    
    fig = px.parallel_coordinates(
        df, 
        color="Cluster", 
        dimensions=['Média Geral', 'Acessos', 'Postagens no Fórum'],
        title="Perfis dos Clusters de Alunos",
        color_continuous_scale=px.colors.diverging.Tealrose,
    )
    return fig

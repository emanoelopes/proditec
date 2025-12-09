import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def calculate_average(df):
    """
    Calculates the average grade for each student across all modules.
    """
    module_cols = [col for col in df.columns if "Módulo" in col]
    df['Média Geral'] = df[module_cols].mean(axis=1).round(1)
    return df

def identify_at_risk(df, threshold=6.0):
    """
    Identifies students with an average grade below the threshold.
    """
    if 'Média Geral' not in df.columns:
        df = calculate_average(df)
    return df[df['Média Geral'] < threshold]

def perform_clustering(df, n_clusters=3):
    """
    Performs K-Means clustering on students based on grades and engagement.
    """
    # Select features for clustering
    features = ['Média Geral', 'Acessos', 'Postagens no Fórum']
    
    # Ensure average is calculated
    if 'Média Geral' not in df.columns:
        df = calculate_average(df)
        
    X = df[features].copy()
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['Cluster'] = kmeans.fit_predict(X_scaled)
    
    # Map clusters to meaningful names based on centroids (simplified heuristic)
    # We can analyze the cluster centers to name them, but for now we'll just return the cluster ID
    # In a real app, we would analyze the centers to label "High Performers", etc.
    
    return df

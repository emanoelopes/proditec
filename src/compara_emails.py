import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
from typing import List, Dict, Tuple
import io
import os

class ComparadorEmails:
    """
    Classe para comparar emails de participantes do Google Meet com listas de convidados.
    """
    
    def __init__(self):
        self.participantes_df = None
        self.convidados_df = None
        self.grupos_tematicos_df = None
        self.emails_nao_convidados = None
        
    def carregar_planilha_participantes(self, arquivo, formato='csv'):
        """
        Carrega planilha com participantes do Google Meet.
        
        Args:
            arquivo: Caminho do arquivo ou objeto de upload
            formato: 'csv', 'excel', 'txt'
        """
        try:
            if formato == 'csv':
                self.participantes_df = pd.read_csv(arquivo)
            elif formato == 'excel':
                self.participantes_df = pd.read_excel(arquivo)
            elif formato == 'txt':
                # Para ata de texto do Google Meet
                with open(arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                self.participantes_df = self._extrair_participantes_do_texto(conteudo)
            
            st.success(f"✅ Planilha de participantes carregada: {len(self.participantes_df)} registros")
            return True
        except Exception as e:
            st.error(f"❌ Erro ao carregar planilha de participantes: {str(e)}")
            return False
    
    def carregar_planilha_convidados(self, arquivo, formato='csv'):
        """
        Carrega planilha com lista de convidados.
        
        Args:
            arquivo: Caminho do arquivo ou objeto de upload
            formato: 'csv', 'excel'
        """
        try:
            if formato == 'csv':
                self.convidados_df = pd.read_csv(arquivo)
            elif formato == 'excel':
                self.convidados_df = pd.read_excel(arquivo)
            
            st.success(f"✅ Planilha de convidados carregada: {len(self.convidados_df)} registros")
            return True
        except Exception as e:
            st.error(f"❌ Erro ao carregar planilha de convidados: {str(e)}")
            return False
    
    def carregar_grupos_tematicos(self, arquivo, formato='csv'):
        """
        Carrega planilha com grupos temáticos.
        
        Args:
            arquivo: Caminho do arquivo ou objeto de upload
            formato: 'csv', 'excel'
        """
        try:
            if formato == 'csv':
                self.grupos_tematicos_df = pd.read_csv(arquivo)
            elif formato == 'excel':
                self.grupos_tematicos_df = pd.read_excel(arquivo)
            
            st.success(f"✅ Planilha de grupos temáticos carregada: {len(self.grupos_tematicos_df)} registros")
            return True
        except Exception as e:
            st.error(f"❌ Erro ao carregar planilha de grupos temáticos: {str(e)}")
            return False
    
    def _extrair_participantes_do_texto(self, texto: str) -> pd.DataFrame:
        """
        Extrai participantes de uma ata de texto do Google Meet.
        
        Args:
            texto: Conteúdo da ata em texto
            
        Returns:
            DataFrame com participantes extraídos
        """
        # Regex para encontrar emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, texto)
        
        # Regex para encontrar nomes (linhas que não contêm @)
        linhas = texto.split('\n')
        nomes = []
        
        for linha in linhas:
            linha = linha.strip()
            if linha and '@' not in linha and len(linha) > 2:
                # Remove caracteres especiais e números no início
                nome_limpo = re.sub(r'^[\d\s\-\.]+', '', linha)
                if nome_limpo and len(nome_limpo) > 2:
                    nomes.append(nome_limpo)
        
        # Criar DataFrame
        dados = []
        for i, email in enumerate(emails):
            nome = nomes[i] if i < len(nomes) else f"Participante {i+1}"
            dados.append({
                'nome': nome,
                'email': email,
                'origem': 'Google Meet'
            })
        
        return pd.DataFrame(dados)
    
    def extrair_emails_participantes(self, coluna_email='email', coluna_nome='nome'):
        """
        Extrai e padroniza emails dos participantes.
        
        Args:
            coluna_email: Nome da coluna com emails
            coluna_nome: Nome da coluna com nomes
        """
        if self.participantes_df is None:
            st.error("❌ Planilha de participantes não carregada")
            return False
        
        try:
            # Padronizar emails
            self.participantes_df[coluna_email] = self.participantes_df[coluna_email].str.lower().str.strip()
            
            # Remover duplicatas
            self.participantes_df = self.participantes_df.drop_duplicates(subset=[coluna_email])
            
            st.success(f"✅ Emails dos participantes extraídos: {len(self.participantes_df)} únicos")
            return True
        except Exception as e:
            st.error(f"❌ Erro ao extrair emails: {str(e)}")
            return False
    
    def comparar_participantes_convidados(self, coluna_email_convidados='email'):
        """
        Compara participantes com lista de convidados.
        
        Args:
            coluna_email_convidados: Nome da coluna com emails dos convidados
        """
        if self.participantes_df is None or self.convidados_df is None:
            st.error("❌ Planilhas necessárias não carregadas")
            return False
        
        try:
            # Padronizar emails dos convidados
            self.convidados_df[coluna_email_convidados] = self.convidados_df[coluna_email_convidados].str.lower().str.strip()
            
            # Encontrar participantes não convidados
            emails_participantes = set(self.participantes_df['email'])
            emails_convidados = set(self.convidados_df[coluna_email_convidados])
            
            emails_nao_convidados = emails_participantes - emails_convidados
            
            # Criar DataFrame com participantes não convidados
            self.emails_nao_convidados = self.participantes_df[
                self.participantes_df['email'].isin(emails_nao_convidados)
            ].copy()
            
            st.success(f"✅ Comparação concluída: {len(self.emails_nao_convidados)} participantes não convidados")
            return True
        except Exception as e:
            st.error(f"❌ Erro na comparação: {str(e)}")
            return False
    
    def obter_estatisticas(self) -> Dict:
        """
        Retorna estatísticas da análise.
        
        Returns:
            Dicionário com estatísticas
        """
        if self.participantes_df is None:
            return {}
        
        total_participantes = len(self.participantes_df)
        nao_convidados = len(self.emails_nao_convidados) if self.emails_nao_convidados is not None else 0
        convidados = total_participantes - nao_convidados
        
        return {
            'total_participantes': total_participantes,
            'convidados': convidados,
            'nao_convidados': nao_convidados,
            'percentual_nao_convidados': (nao_convidados / total_participantes * 100) if total_participantes > 0 else 0
        }
    
    def gerar_grafico_participacao(self):
        """
        Gera gráfico de pizza com distribuição de participantes.
        """
        stats = self.obter_estatisticas()
        
        if not stats:
            return None
        
        fig = px.pie(
            values=[stats['convidados'], stats['nao_convidados']],
            names=['Convidados', 'Não Convidados'],
            title='Distribuição de Participantes',
            color_discrete_map={'Convidados': '#2E8B57', 'Não Convidados': '#DC143C'}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        return fig
    
    def gerar_grafico_recorrencia(self):
        """
        Gera gráfico de barras com recorrência de domínios de email.
        """
        if self.emails_nao_convidados is None or len(self.emails_nao_convidados) == 0:
            return None
        
        # Extrair domínios
        dominios = self.emails_nao_convidados['email'].str.extract(r'@(.+)')[0]
        contagem_dominios = dominios.value_counts().head(10)
        
        fig = px.bar(
            x=contagem_dominios.index,
            y=contagem_dominios.values,
            title='Top 10 Domínios de Email (Não Convidados)',
            labels={'x': 'Domínio', 'y': 'Quantidade'}
        )
        
        fig.update_layout(xaxis_tickangle=-45)
        return fig


def main():
    """
    Função principal da aplicação Streamlit.
    """
    st.set_page_config(
        page_title="Comparador de Emails - Google Meet",
        page_icon="📧",
        layout="wide"
    )
    
    st.title("📧 Comparador de Emails - Google Meet")
    st.markdown("---")
    
    # Inicializar comparador
    if 'comparador' not in st.session_state:
        st.session_state.comparador = ComparadorEmails()
    
    comparador = st.session_state.comparador
    

    # Sidebar Navigation
    st.sidebar.title("Navegação")
    modo = st.sidebar.radio(
        "Selecione o Modo:", 
        ["Visão Geral", "Comparador de Emails", "Análise de Notas Avamec", "Comparação Planilhas vs Avamec"], 
        key="nav_mode"
    )
    
    if modo == "Visão Geral":
        render_overview()
    elif modo == "Comparador de Emails":
        render_email_comparator(comparador)
    elif modo == "Análise de Notas Avamec":
        render_grade_analysis()
    else:  # Comparação Planilhas vs Avamec
        render_comparison_dashboard()

def render_overview():
    st.header("📊 Visão Geral - PRODITEC")
    
    # Path to consolidated file
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'grades_consolidados.csv')
    
    if not os.path.exists(csv_path):
        st.error(f"Arquivo de dados não encontrado em: {csv_path}")
        st.info("Execute o script de consolidação primeiro.")
        return
    
    try:
        # Load data
        df = pd.read_csv(csv_path, header=0)
        
        # Find group column
        group_col = None
        for col in df.columns:
            if df[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
                group_col = col
                break
        
        if not group_col:
            st.error("Não foi possível identificar a coluna de grupos.")
            return
        
        # Extract Turma info
        df['Turma'] = df[group_col].astype(str).str.extract(r'(Turma [AB] - Grupo \d+)', expand=False)
        
        # Filter valid groups
        df_valid = df[df['Turma'].notna()]
        
        # Calculate metrics
        total_grupos = df_valid['Turma'].nunique()
        total_cursistas = len(df_valid)
        
        # Find Sala columns
        sala_cols = [c for c in df.columns if 'Sala' in c and c != 'Sala']
        
        # Count groups with missing grades
        grupos_com_falta = set()
        for grupo in df_valid['Turma'].unique():
            df_grupo = df_valid[df_valid['Turma'] == grupo]
            
            # Check if any student in this group has missing grades
            for _, row in df_grupo.iterrows():
                for sala in sala_cols:
                    valor = str(row[sala]).strip()
                    # Only empty cells, not zeros
                    if valor in ['', 'nan', 'NaN'] or pd.isna(row[sala]):
                        grupos_com_falta.add(grupo)
                        break
                if grupo in grupos_com_falta:
                    break
        
        qtd_grupos_com_falta = len(grupos_com_falta)
        
        # Display metrics
        st.markdown("### 📈 Métricas Gerais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total de Grupos",
                value=total_grupos,
                help="Número total de grupos (Turma A e B)"
            )
        
        with col2:
            st.metric(
                label="Total de Cursistas",
                value=total_cursistas,
                help="Número total de cursistas em todos os grupos"
            )
        
        with col3:
            st.metric(
                label="Grupos com Notas Faltantes",
                value=qtd_grupos_com_falta,
                delta=f"-{total_grupos - qtd_grupos_com_falta} completos",
                delta_color="inverse",
                help="Grupos que possuem pelo menos uma atividade sem nota lançada"
            )
        
        # Detailed breakdown
        st.markdown("---")
        st.markdown("### 📋 Detalhamento por Grupo")
        
        # Create summary table
        grupo_data = []
        for grupo in sorted(df_valid['Turma'].unique()):
            df_grupo = df_valid[df_valid['Turma'] == grupo]
            qtd_alunos = len(df_grupo)
            
            # Count missing grades
            total_missing = 0
            for _, row in df_grupo.iterrows():
                for sala in sala_cols:
                    valor = str(row[sala]).strip()
                    if valor in ['', 'nan', 'NaN'] or pd.isna(row[sala]):
                        total_missing += 1
            
            status = "✅ Completo" if total_missing == 0 else f"⚠️ {total_missing} notas faltando"
            
            grupo_data.append({
                'Grupo': grupo,
                'Cursistas': qtd_alunos,
                'Notas Faltantes': total_missing,
                'Status': status
            })
        
        grupo_df = pd.DataFrame(grupo_data)
        st.dataframe(grupo_df, use_container_width=True, hide_index=True)
        
        # Chart: Groups with missing grades
        st.markdown("---")
        st.markdown("### 📊 Distribuição de Notas Faltantes por Grupo")
        
        fig_data = grupo_df[grupo_df['Notas Faltantes'] > 0].sort_values('Notas Faltantes', ascending=False)
        if not fig_data.empty:
            st.bar_chart(fig_data.set_index('Grupo')['Notas Faltantes'])
        else:
            st.success("🎉 Todos os grupos estão com as notas completas!")
        
    except Exception as e:
        st.error(f"Erro ao processar dados: {e}")
        import traceback
        st.code(traceback.format_exc())

def render_email_comparator(comparador):
    # Sidebar para upload de arquivos
    st.sidebar.header("📁 Upload de Arquivos")
    
    # Upload da ata de participantes
    st.sidebar.subheader("1. Ata de Participantes")
    arquivo_participantes = st.sidebar.file_uploader(
        "Selecione a ata do Google Meet",
        type=['csv', 'xlsx', 'txt'],
        key="participantes"
    )
    
    if arquivo_participantes:
        formato_participantes = 'txt' if arquivo_participantes.name.endswith('.txt') else 'csv'
        if st.sidebar.button("Carregar Participantes"):
            comparador.carregar_planilha_participantes(arquivo_participantes, formato_participantes)
    
    # Upload da lista de convidados
    st.sidebar.subheader("2. Lista de Convidados")
    arquivo_convidados = st.sidebar.file_uploader(
        "Selecione a planilha de convidados",
        type=['csv', 'xlsx'],
        key="convidados"
    )
    
    if arquivo_convidados:
        formato_convidados = 'csv' if arquivo_convidados.name.endswith('.csv') else 'excel'
        if st.sidebar.button("Carregar Convidados"):
            comparador.carregar_planilha_convidados(arquivo_convidados, formato_convidados)
    
    # Upload dos grupos temáticos
    st.sidebar.subheader("3. Grupos Temáticos (Opcional)")
    arquivo_grupos = st.sidebar.file_uploader(
        "Selecione a planilha de grupos temáticos",
        type=['csv', 'xlsx'],
        key="grupos"
    )
    
    if arquivo_grupos:
        formato_grupos = 'csv' if arquivo_grupos.name.endswith('.csv') else 'excel'
        if st.sidebar.button("Carregar Grupos"):
            comparador.carregar_grupos_tematicos(arquivo_grupos, formato_grupos)
    
    # Conteúdo principal
    st.header("📧 Comparador de Emails")
    
    if comparador.participantes_df is not None and comparador.convidados_df is not None:
        
        # Botão para executar comparação
        if st.button("🔍 Executar Comparação", type="primary"):
            with st.spinner("Processando dados..."):
                comparador.extrair_emails_participantes()
                comparador.comparar_participantes_convidados()
        
        # Exibir estatísticas
        if comparador.emails_nao_convidados is not None:
            stats = comparador.obter_estatisticas()
            
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Participantes", stats['total_participantes'])
            
            with col2:
                st.metric("Convidados", stats['convidados'])
            
            with col3:
                st.metric("Não Convidados", stats['nao_convidados'])
            
            with col4:
                st.metric("% Não Convidados", f"{stats['percentual_nao_convidados']:.1f}%")
            
            st.markdown("---")
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pizza = comparador.gerar_grafico_participacao()
                if fig_pizza:
                    st.plotly_chart(fig_pizza, use_container_width=True)
            
            with col2:
                fig_barras = comparador.gerar_grafico_recorrencia()
                if fig_barras:
                    st.plotly_chart(fig_barras, use_container_width=True)
            
            # Tabela de participantes não convidados
            st.subheader("👥 Participantes Não Convidados")
            
            if len(comparador.emails_nao_convidados) > 0:
                st.dataframe(
                    comparador.emails_nao_convidados[['nome', 'email']],
                    use_container_width=True,
                    hide_index=True
                )
                
                # Botão para download
                csv = comparador.emails_nao_convidados.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"participantes_nao_convidados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.success("🎉 Todos os participantes estavam na lista de convidados!")
        
        # Visualizar dados carregados
        st.subheader("📊 Dados Carregados")
        
        tab1, tab2, tab3 = st.tabs(["Participantes", "Convidados", "Grupos Temáticos"])
        
        with tab1:
            if comparador.participantes_df is not None:
                st.dataframe(comparador.participantes_df.head(), use_container_width=True)
        
        with tab2:
            if comparador.convidados_df is not None:
                st.dataframe(comparador.convidados_df.head(), use_container_width=True)
        
        with tab3:
            if comparador.grupos_tematicos_df is not None:
                st.dataframe(comparador.grupos_tematicos_df.head(), use_container_width=True)
            else:
                st.info("Nenhum arquivo de grupos temáticos carregado")
    
    else:
        st.info("👆 Faça upload dos arquivos necessários na barra lateral para começar a análise.")
        
        # Instruções
        st.markdown("### 📋 Como usar:")
        st.markdown("""
        1. **Ata de Participantes**: Faça upload da ata do Google Meet (CSV, Excel ou TXT)
        2. **Lista de Convidados**: Faça upload da planilha com emails dos convidados
        3. **Grupos Temáticos** (opcional): Faça upload da planilha com grupos temáticos
        4. Clique em "Executar Comparação" para analisar os dados
        """)

def render_grade_analysis():
    st.header("📊 Análise de Notas Avamec")
    
    # Path to consolidated file
    # We navigate up from src/ to data/
    # script is in src/, so .. is base
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, 'data', 'grades_consolidados.csv')
    
    if not os.path.exists(csv_path):
        st.error(f"Arquivo de dados não encontrado em: {csv_path}")
        st.info("Execute o script de consolidação primeiro.")
        return

    try:
        # Load Data with first row as header (where Sala 1, Sala 2, etc. are defined)
        df = pd.read_csv(csv_path, header=0)
        
        # The CSV has technical column names in row 0 and human-readable in row 1
        # Since we used header=0, we get the technical names like "Sala 1", "Sala 2"
        
        # Clean columns if needed?
        # The column 'Turma B - Grupo 01' in the *first* row might not be capturing properly if we skip it.
        # But wait, the group info is in the DATA rows too? 
        # Step 702 output: Row 5 ends with "...Reprovado,Turma B - Grupo 01,https://..."
        # So there is a column for Group. We need to find its name.
        # Let's load with header=1 and see if we can identify the group column.
        # It seems the last columns are 'Source_Sheet_Title'.
        
        # Debug: show column structure
        # st.write("Columns:", df.columns.tolist())
        
        # Find the column that contains "Turma A" or "Turma B" in its VALUES (not column name)
        group_col = None
        for col in df.columns:
            if df[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
                group_col = col
                break
        
        if group_col:
            st.sidebar.subheader("Filtros")
            
            # Extract Turma from the values in group_col (e.g., "Turma B - Grupo 01" -> "Turma B")
            df['Turma'] = df[group_col].astype(str).str.extract(r'(Turma [AB])', expand=False)
            
            # Filter 1: Select Turma
            turmas = sorted([t for t in df['Turma'].dropna().unique() if t != 'nan'])
            
            if len(turmas) == 0:
                st.error("Nenhuma turma encontrada nos dados.")
                st.write("Debug - Valores únicos na coluna:", df[group_col].unique()[:10])
                return
            
            selected_turma = st.sidebar.selectbox("1. Selecione a Turma:", turmas, key="select_turma")
            
            # Filter data by Turma
            df_turma = df[df['Turma'] == selected_turma]
            
            # Filter 2: Select Student Name
            # Find the column with student names
            name_col = next((c for c in df.columns if 'Nome' in c and 'Completo' in c), None)
            if name_col:
                students = sorted([s for s in df_turma[name_col].dropna().unique() if str(s) != 'nan' and s])
                selected_student = st.sidebar.selectbox("2. Selecione o Cursista:", ["Todos"] + list(students), key="select_student")
                
                if selected_student != "Todos":
                    filtered_df = df_turma[df_turma[name_col] == selected_student]
                else:
                    filtered_df = df_turma
            else:
                filtered_df = df_turma
                st.warning("Coluna de nomes não encontrada.")
            
            # Build display text
            if name_col and selected_student != "Todos":
                display_text = f"{selected_turma} - {selected_student}"
            else:
                display_text = selected_turma
            
            st.markdown(f"### Visualizando: {display_text}")
            st.metric("Total de Alunos", len(filtered_df))
            
            # Show names and grades
            # Filter columns to only show Name and potential grade columns (Sala X)
            # Find columns that look like "Sala" or "Ambientação"
            cols_to_show = [c for c in df.columns if 'Nome' in c or 'Sala' in c or 'Ambientação' in c]
            
            if not cols_to_show:
                cols_to_show = df.columns
            
            st.dataframe(filtered_df[cols_to_show], use_container_width=True)
            
            # Additional Analysis: Grading Status
            st.subheader("📊 Status de Lançamento de Notas")
            st.markdown("*Mostra quantos alunos têm notas lançadas em cada atividade/sala. **Nota:** Zero é considerado nota válida.*")
            
            # Calculate how many non-null/non-zero values in Sala columns
            sala_cols = [c for c in cols_to_show if 'Sala' in c]
            
            # Debug
            st.write(f"**Debug:** Encontradas {len(sala_cols)} colunas de Sala para análise")
            
            if len(sala_cols) == 0:
                st.warning("Nenhuma coluna de 'Sala' foi encontrada nos dados. Verifique a estrutura do arquivo.")
            else:
                status_data = []
                for col in sala_cols:
                    # Count filled cells (including zeros)
                    # Only empty/null cells are considered missing
                    valid_count = filtered_df[col].apply(
                        lambda x: 0 if (pd.isna(x) or str(x).strip() in ['', 'nan', 'NaN']) else 1
                    ).sum()
                    status_data.append({'Atividade': col, 'Notas Lançadas': valid_count, 'Total Alunos': len(filtered_df)})
                    
                status_df = pd.DataFrame(status_data)
                if not status_df.empty:
                    st.bar_chart(status_df.set_index('Atividade')['Notas Lançadas'])
                    
                    # Also show as table for clarity
                    st.dataframe(status_df, use_container_width=True)
                else:
                    st.info("Nenhum dado de status disponível.")
            
        else:
            st.warning("Não foi possível identificar a coluna de Turma/Grupo.")
            st.dataframe(df.head())

    except Exception as e:
        st.error(f"Erro ao ler arquivo de dados: {e}")

def render_comparison_dashboard():
    """Renderiza dashboard de comparação entre Planilhas e Avamec"""
    st.header("📊 Comparação: Planilhas vs Avamec")
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    grades_file = os.path.join(base_dir, 'data', 'grades_consolidados.csv')
    
    # Tentar arquivo completo primeiro, depois o parcial
    avamec_file = os.path.join(base_dir, 'data', 'avamec_completo.json')
    if not os.path.exists(avamec_file):
        avamec_file = os.path.join(base_dir, 'data', 'avamec_status_situacao.json')
    
    # Verificar arquivos
    if not os.path.exists(grades_file):
        st.error(f"❌ Arquivo não encontrado: {grades_file}")
        st.info("Execute: python3 src/core/consolidate_grades.py")
        return
    
    if not os.path.exists(avamec_file):
        st.warning(f"⚠️ Dados do Avamec não encontrados: {avamec_file}")
        st.info("Execute: python3 scripts/scrape_avamec_completo.py")
        st.info("Mostrando apenas dados das planilhas...")
        avamec_data = {}
    else:
        # Carregar dados do Avamec
        with open(avamec_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            avamec_data = {a['nome'].strip().upper(): a for a in data.get('alunos', [])}
    
    # Carregar dados das planilhas
    df_grades = pd.read_csv(grades_file, header=0)
    
    # Colunas
    name_col = df_grades.columns[1]
    status_col = 'Extra_Col_61'
    
    # Encontrar coluna de grupo
    group_col = None
    for col in df_grades.columns:
        if df_grades[col].astype(str).str.contains('Turma [AB]', regex=True, na=False).any():
            group_col = col
            break
    
    if not group_col:
        st.error("Coluna de grupo não encontrada!")
        return
    
    # Extrair turma e grupo
    df_grades['Turma_Grupo'] = df_grades[group_col].astype(str).str.extract(r'(Turma [AB] - Grupo \d+)', expand=False)
    df_grades['Turma'] = df_grades['Turma_Grupo'].str.extract(r'(Turma [AB])', expand=False)
    df_grades['Grupo'] = df_grades['Turma_Grupo'].str.extract(r'(Grupo \d+)', expand=False)
    
    # FILTROS NO SIDEBAR
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros")
    
    # Filtro de Turma
    turmas_disponiveis = ['Todas'] + sorted([t for t in df_grades['Turma'].unique() if pd.notna(t)])
    selected_turma = st.sidebar.selectbox("Selecione a Turma:", turmas_disponiveis, key="comp_turma")
    
    # Filtrar por turma
    if selected_turma != 'Todas':
        df_filtered = df_grades[df_grades['Turma'] == selected_turma].copy()
    else:
        df_filtered = df_grades.copy()
    
    # Filtro de Grupo
    grupos_disponiveis = ['Todos'] + sorted([g for g in df_filtered['Grupo'].unique() if pd.notna(g)])
    selected_grupo = st.sidebar.selectbox("Selecione o Grupo:", grupos_disponiveis, key="comp_grupo")
    
    # Filtrar por grupo
    if selected_grupo != 'Todos':
        df_filtered = df_filtered[df_filtered['Grupo'] == selected_grupo].copy()
    
    # Criar dados comparativos
    comparison_data = []
    for _, row in df_filtered.iterrows():
        nome = str(row[name_col]).strip()
        nome_upper = nome.upper()
        status_planilha = str(row[status_col]).strip() if status_col in df_filtered.columns else 'N/A'
        grupo = str(row['Turma_Grupo'])
        
        # Buscar no Avamec
        avamec_info = avamec_data.get(nome_upper, {})
        situacao_avamec = avamec_info.get('situacao_parcial', '—')
        
        # Determinar status da nota
        if situacao_avamec == '—':
            status_nota = '⏳ Aguardando'
        else:
            try:
                nota = float(situacao_avamec)
                status_nota = '✅ Lançada' if nota > 0 else '⚠️ Zero'
            except:
                status_nota = '❓ Verificar'
        
        comparison_data.append({
            'Nome': nome,
            'Grupo': grupo,
            'Status_Planilha': status_planilha,
            'Situacao_Avamec': situacao_avamec,
            'Status_Nota': status_nota
        })
    
    df_comp = pd.DataFrame(comparison_data)
    
    # MÉTRICAS
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(df_comp)
    com_avamec = len([x for x in df_comp['Situacao_Avamec'] if x != '—'])
    aguardando = len([x for x in df_comp['Status_Nota'] if 'Aguardando' in x])
    
    # Calcular divergências
    divergencias = 0
    for _, row in df_comp.iterrows():
        if row['Situacao_Avamec'] != '—':
            try:
                nota = float(row['Situacao_Avamec'])
                status_avamec = 'Aprovado' if nota >= 7 else 'Reprovado'
                if row['Status_Planilha'].upper() != status_avamec.upper():
                    divergencias += 1
            except:
                pass
    
    with col1:
        st.metric("Total de Cursistas", total)
    with col2:
        st.metric("Com Dados Avamec", com_avamec)
    with col3:
        st.metric("🔴 Divergências", divergencias)
    with col4:
        st.metric("⏳ Aguardando", aguardando)
    
    st.markdown("---")
    
    # VISUALIZAÇÕES
    if com_avamec > 0:
        # Gráfico de Comparação de Status
        st.subheader("📊 Comparação de Status")
        
        # Preparar dados para gráfico
        status_counts = {
            'Aprovado (Planilhas)': len(df_comp[df_comp['Status_Planilha'].str.upper() == 'APROVADO']),
            'Reprovado (Planilhas)': len(df_comp[df_comp['Status_Planilha'].str.upper() == 'REPROVADO']),
        }
        
        # Contar status Avamec
        aprovado_avamec = 0
        reprovado_avamec = 0
        for _, row in df_comp.iterrows():
            if row['Situacao_Avamec'] != '—':
                try:
                    nota = float(row['Situacao_Avamec'])
                    if nota >= 7:
                        aprovado_avamec += 1
                    else:
                        reprovado_avamec += 1
                except:
                    pass
        
        status_counts['Aprovado (Avamec)'] = aprovado_avamec
        status_counts['Reprovado (Avamec)'] = reprovado_avamec
        
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[
            go.Bar(name='Planilhas', x=['Aprovado', 'Reprovado'], 
                   y=[status_counts['Aprovado (Planilhas)'], status_counts['Reprovado (Planilhas)']],
                   marker_color='lightblue'),
            go.Bar(name='Avamec', x=['Aprovado', 'Reprovado'], 
                   y=[status_counts['Aprovado (Avamec)'], status_counts['Reprovado (Avamec)']],
                   marker_color='orange')
        ])
        
        fig.update_layout(barmode='group', title='Status: Planilhas vs Avamec',
                         xaxis_title='Status', yaxis_title='Quantidade')
        st.plotly_chart(fig, use_container_width=True)
        
        # Distribuição de Notas Avamec
        st.subheader("📈 Distribuição de Notas (Avamec)")
        
        notas_avamec = []
        for _, row in df_comp.iterrows():
            if row['Situacao_Avamec'] != '—':
                try:
                    notas_avamec.append(float(row['Situacao_Avamec']))
                except:
                    pass
        
        if notas_avamec:
            fig_hist = go.Figure(data=[go.Histogram(x=notas_avamec, nbinsx=11, marker_color='green')])
            fig_hist.update_layout(title='Distribuição de Notas do Avamec',
                                  xaxis_title='Nota', yaxis_title='Quantidade')
            st.plotly_chart(fig_hist, use_container_width=True)
    
    # DIVERGÊNCIAS
    if divergencias > 0:
        st.subheader(f"⚠️ Divergências Encontradas ({divergencias})")
        
        divergent_students = []
        for _, row in df_comp.iterrows():
            if row['Situacao_Avamec'] != '—':
                try:
                    nota = float(row['Situacao_Avamec'])
                    status_avamec = 'Aprovado' if nota >= 7 else 'Reprovado'
                    if row['Status_Planilha'].upper() != status_avamec.upper():
                        divergent_students.append({
                            'Nome': row['Nome'],
                            'Grupo': row['Grupo'],
                            'Planilhas': row['Status_Planilha'],
                            'Avamec': f"{row['Situacao_Avamec']} ({status_avamec})"
                        })
                except:
                    pass
        
        df_div = pd.DataFrame(divergent_students)
        st.dataframe(df_div, use_container_width=True)
    
    # TABELA COMPLETA
    st.subheader("📋 Tabela Detalhada")
    
    # Renomear colunas para exibição
    df_display = df_comp.copy()
    df_display.columns = ['Nome', 'Grupo', 'Status Final (Planilhas)', 'Situação Parcial (Avamec)', 'Status da Nota']
    
    st.dataframe(df_display, use_container_width=True, height=400)
    
    # Opção de download
    csv = df_display.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Baixar Comparação (CSV)",
        data=csv,
        file_name=f"comparacao_{selected_turma}_{selected_grupo}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

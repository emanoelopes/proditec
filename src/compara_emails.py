import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import re
from typing import List, Dict, Tuple
import io

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


if __name__ == "__main__":
    main()

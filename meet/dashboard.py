"""
Dashboard Streamlit para monitoramento em tempo real das salas temáticas.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
from typing import Optional

from config import (
    SPREADSHEET_ID, DASHBOARD_REFRESH_INTERVAL, NUM_GRUPOS, TURMAS,
    OLLAMA_BASE_URL, OLLAMA_MODEL, DEFAULT_WORKSHEET_NAME
)
from google_integration import GoogleIntegration
from monitor import MonitorSalas
from agente_ia import AgenteIA


# Configuração da página
st.set_page_config(
    page_title="Monitor de Salas Temáticas - Google Meet",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização de sessão
if 'google_integration' not in st.session_state:
    st.session_state.google_integration = None
if 'monitor' not in st.session_state:
    st.session_state.monitor = None
if 'agente_ia' not in st.session_state:
    st.session_state.agente_ia = None
if 'dados_carregados' not in st.session_state:
    st.session_state.dados_carregados = False
if 'ultima_atualizacao' not in st.session_state:
    st.session_state.ultima_atualizacao = None
if 'meeting_ativo' not in st.session_state:
    st.session_state.meeting_ativo = None


def inicializar_servicos():
    """Inicializa serviços do Google e agente IA."""
    if st.session_state.google_integration is None:
        try:
            with st.spinner("Conectando com Google APIs..."):
                st.session_state.google_integration = GoogleIntegration()
                st.session_state.agente_ia = AgenteIA(
                    base_url=OLLAMA_BASE_URL,
                    model=OLLAMA_MODEL
                )
            st.success("✅ Conectado com sucesso!")
        except FileNotFoundError as e:
            st.error(f"❌ {str(e)}")
            st.info("💡 Dica: Baixe o arquivo credentials.json do Google Cloud Console e coloque no diretório meet/")
            st.stop()
        except Exception as e:
            error_msg = str(e)
            if 'insufficient authentication scopes' in error_msg.lower() or 'scope' in error_msg.lower():
                st.error("❌ Erro de autenticação: Permissões insuficientes")
                st.warning("""
                **Solução:**
                1. Delete o arquivo `token.json` no diretório meet/
                2. Clique novamente em "Conectar Google APIs"
                3. Autorize todos os scopes solicitados no navegador
                """)
                if st.button("🗑️ Deletar token.json e reautenticar"):
                    import os
                    token_path = os.path.join(os.path.dirname(__file__), 'token.json')
                    if os.path.exists(token_path):
                        os.remove(token_path)
                        st.session_state.google_integration = None
                        st.rerun()
            else:
                st.error(f"❌ Erro ao conectar: {error_msg}")
            st.stop()


def carregar_dados_planilha(spreadsheet_id: str, worksheet_name: Optional[str] = None):
    """Carrega dados da planilha Google Sheets."""
    try:
        with st.spinner("Carregando dados da planilha..."):
            df = st.session_state.google_integration.ler_planilha_por_id(
                spreadsheet_id, worksheet_name
            )
            
            if df.empty:
                st.error("Planilha vazia ou não encontrada.")
                return False
            
            # Cria monitor
            st.session_state.monitor = MonitorSalas(df)
            st.session_state.dados_carregados = True
            st.session_state.ultima_atualizacao = datetime.now()
            
            st.success(f"✅ Dados carregados: {len(df)} registros")
            return True
            
    except Exception as e:
        error_msg = str(e)
        st.error(f"❌ Erro ao carregar planilha: {error_msg}")
        
        # Detecta erro de scope insuficiente
        if 'insufficient authentication scopes' in error_msg.lower() or 'ACCESS_TOKEN_SCOPE_INSUFFICIENT' in error_msg:
            st.warning("""
            **Erro de Permissões:**
            
            O token de autenticação não tem permissões suficientes para acessar o Google Sheets.
            
            **Solução:**
            1. Delete o arquivo `token.json` no diretório meet/
            2. Clique em "Conectar Google APIs" novamente
            3. Autorize TODOS os scopes solicitados no navegador
            
            Você pode deletar o token executando no terminal:
            ```bash
            rm /home/emanoel/progpy/avamec/meet/token.json
            ```
            """)
            if st.button("🔄 Tentar reconectar (delete token.json primeiro)"):
                import os
                token_path = os.path.join(os.path.dirname(__file__), 'token.json')
                if os.path.exists(token_path):
                    os.remove(token_path)
                    st.session_state.google_integration = None
                    st.rerun()
        
        return False


def obter_meeting_code():
    """Obtém o código do meeting ativo."""
    meeting_info = st.session_state.get('meeting_ativo')
    if not meeting_info:
        return None
    return meeting_info.get('meet_link') or meeting_info.get('meeting_code')


def exibir_metricas_gerais(turma: Optional[str] = None):
    """Exibe métricas gerais do monitoramento."""
    if not st.session_state.monitor:
        st.warning("⚠️ Monitor não inicializado. Carregue os dados da planilha primeiro.")
        return
    
    # Garante que o status foi calculado
    if not st.session_state.monitor.status_salas:
        st.session_state.monitor.calcular_status(turma=turma)
    
    estatisticas = st.session_state.monitor.obter_estatisticas_gerais(turma=turma)
    
    # Debug: mostra informações se estiver tudo zerado
    if estatisticas['total_esperado'] == 0:
        total_participantes_esperados = len(st.session_state.monitor.participantes_esperados)
        st.warning(
            f"⚠️ **Atenção:** Total esperado está zerado.\n\n"
            f"- Participantes esperados no monitor: {total_participantes_esperados}\n"
            f"- Turma filtrada: {turma if turma else 'Todas'}\n"
            f"- Status salas calculadas: {len(st.session_state.monitor.status_salas)}\n\n"
            f"**Possíveis causas:**\n"
            f"1. Filtro de turma não corresponde aos dados\n"
            f"2. Dados da planilha não foram processados corretamente\n"
            f"3. Colunas da planilha não foram mapeadas corretamente"
        )
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Esperado",
            estatisticas['total_esperado']
        )
    
    with col2:
        st.metric(
            "Total Presente",
            estatisticas['total_presente'],
            delta=f"{estatisticas['percentual_presente']:.1f}%" if estatisticas['total_esperado'] > 0 else "0%"
        )
    
    with col3:
        st.metric(
            "Total Ausente",
            estatisticas['total_ausente'],
            delta=f"{estatisticas['percentual_ausente']:.1f}%" if estatisticas['total_esperado'] > 0 else "0%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            "Em Sala Errada",
            estatisticas['total_errados'],
            delta_color="inverse"
        )
    
    with col5:
        if st.session_state.ultima_atualizacao:
            tempo_decorrido = (datetime.now() - st.session_state.ultima_atualizacao).total_seconds()
            st.metric(
                "Última Atualização",
                f"{int(tempo_decorrido)}s atrás"
            )
        else:
            st.metric("Última Atualização", "N/A")


def exibir_status_por_sala(turma: Optional[str] = None):
    """Exibe status detalhado de cada sala."""
    if not st.session_state.monitor:
        return
    
    status_salas = st.session_state.monitor.calcular_status(turma=turma)
    
    # Filtra salas da turma selecionada
    salas_filtradas = [
        (t, g) for t, g in status_salas.keys()
        if turma is None or t == turma
    ]
    salas_filtradas.sort()
    
    # Cria grid de cards
    num_cols = 5
    for i in range(0, len(salas_filtradas), num_cols):
        cols = st.columns(num_cols)
        for j, (t, g) in enumerate(salas_filtradas[i:i+num_cols]):
            if j < len(cols):
                status = status_salas[(t, g)]
                with cols[j]:
                    exibir_card_sala(status)


def exibir_card_sala(status):
    """Exibe card de uma sala."""
    # Determina cor baseada no status
    if status.total_ausente == 0 and len(status.participantes_errados) == 0:
        cor = "🟢"
        cor_bg = "#d4edda"
    elif status.total_ausente > 0 or len(status.participantes_errados) > 0:
        cor = "🟡"
        cor_bg = "#fff3cd"
    else:
        cor = "🔴"
        cor_bg = "#f8d7da"
    
    st.markdown(
        f"""
        <div style="
            background-color: {cor_bg};
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
        ">
            <h3>{cor} Grupo {status.grupo} - Turma {status.turma}</h3>
            <p><strong>Esperado:</strong> {status.total_esperado}</p>
            <p><strong>Presente:</strong> {status.total_presente}</p>
            <p><strong>Ausente:</strong> {status.total_ausente}</p>
            <p><strong>Errados:</strong> {len(status.participantes_errados)}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Expander com detalhes
    with st.expander(f"Detalhes - Turma {status.turma}, Grupo {status.grupo}"):
        if status.participantes_ausentes:
            st.write("**Ausentes:**")
            df_ausentes = pd.DataFrame([
                {'Nome': p.nome, 'Email': p.email, 'Telefone': p.telefone or 'N/A'}
                for p in status.participantes_ausentes
            ])
            st.dataframe(df_ausentes, use_container_width=True, hide_index=True)
        
        if status.participantes_errados:
            st.write("**Em Sala Errada:**")
            df_errados = pd.DataFrame([
                {
                    'Nome': p.nome,
                    'Email': p.email,
                    'Turma Esperada': p.turma,
                    'Grupo Esperado': p.grupo_esperado if p.grupo_esperado > 0 else 'N/A',
                    'Grupo Atual': p.grupo_atual or 'N/A'
                }
                for p in status.participantes_errados
            ])
            st.dataframe(df_errados, use_container_width=True, hide_index=True)
        
        if status.participantes_presentes:
            st.write("**Presentes Corretamente:**")
            st.write(f"{len(status.participantes_presentes)} participantes")


def exibir_graficos(turma: Optional[str] = None):
    """Exibe gráficos de visualização."""
    if not st.session_state.monitor:
        return
    
    status_salas = st.session_state.monitor.calcular_status(turma=turma)
    
    # Prepara dados para gráficos
    dados_grafico = []
    for (t, g), status in status_salas.items():
        if turma is None or t == turma:
            dados_grafico.append({
                'Turma': t,
                'Grupo': g,
                'Presente': status.total_presente,
                'Ausente': status.total_ausente,
                'Errados': len(status.participantes_errados),
                'Esperado': status.total_esperado
            })
    
    if not dados_grafico:
        return
    
    df_grafico = pd.DataFrame(dados_grafico)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de barras - Presença por grupo
        fig = px.bar(
            df_grafico,
            x='Grupo',
            y=['Presente', 'Ausente'],
            title='Presença por Grupo',
            labels={'value': 'Quantidade', 'variable': 'Status'},
            color_discrete_map={'Presente': '#28a745', 'Ausente': '#dc3545'}
        )
        fig.update_layout(barmode='stack')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de pizza - Distribuição geral
        estatisticas = st.session_state.monitor.obter_estatisticas_gerais(turma=turma)
        fig = px.pie(
            values=[
                estatisticas['total_presente'],
                estatisticas['total_ausente']
            ],
            names=['Presente', 'Ausente'],
            title='Distribuição Geral',
            color_discrete_map={'Presente': '#28a745', 'Ausente': '#dc3545'}
        )
        st.plotly_chart(fig, use_container_width=True)


def exibir_recomendacoes_ia(turma: Optional[str] = None):
    """Exibe recomendações do agente de IA."""
    if not st.session_state.monitor or not st.session_state.agente_ia:
        return
    
    with st.spinner("Analisando com IA..."):
        try:
            analise = st.session_state.agente_ia.analisar_discrepancias(
                st.session_state.monitor, turma=turma
            )
            
            st.subheader("🤖 Análise e Recomendações da IA")
            
            # Resumo
            st.info(f"**Resumo:** {analise.get('resumo', 'N/A')}")
            
            # Problemas principais
            if analise.get('problemas_principais'):
                st.write("**Problemas Principais:**")
                for problema in analise['problemas_principais']:
                    st.write(f"- {problema}")
            
            # Recomendações
            if analise.get('recomendacoes'):
                st.write("**Recomendações:**")
                for rec in analise['recomendacoes']:
                    st.write(f"- {rec}")
            
            # Ações sugeridas
            if analise.get('acoes_sugeridas'):
                st.write("**Ações Sugeridas:**")
                for i, acao in enumerate(analise['acoes_sugeridas'], 1):
                    st.write(f"{i}. {acao}")
            
            # Prioridade
            prioridade = analise.get('prioridade', 'media')
            cor_prioridade = {
                'alta': '🔴',
                'media': '🟡',
                'baixa': '🟢'
            }.get(prioridade, '⚪')
            st.write(f"**Prioridade:** {cor_prioridade} {prioridade.upper()}")
            
        except Exception as e:
            st.error(f"Erro ao obter análise da IA: {str(e)}")


def main():
    """Função principal do dashboard."""
    st.title("📊 Monitor de Salas Temáticas - Google Meet")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Inicialização de serviços
        if st.button("🔌 Conectar Google APIs"):
            inicializar_servicos()
        
        if st.session_state.google_integration:
            st.success("✅ Conectado")
            
            # Configuração da planilha
            st.subheader("📋 Planilha Google Sheets")
            spreadsheet_id = st.text_input(
                "ID da Planilha",
                value=SPREADSHEET_ID,
                help="ID da planilha Google Sheets (encontrado na URL)"
            )
            worksheet_name = st.text_input(
                "Nome da Aba",
                value=DEFAULT_WORKSHEET_NAME,
                help=f"Nome da aba da planilha (padrão: {DEFAULT_WORKSHEET_NAME})"
            )
            
            if st.button("📥 Carregar Dados"):
                if spreadsheet_id:
                    # Usa a aba especificada ou o padrão
                    worksheet = worksheet_name.strip() if worksheet_name.strip() else DEFAULT_WORKSHEET_NAME
                    carregar_dados_planilha(spreadsheet_id, worksheet)
                else:
                    st.error("Por favor, informe o ID da planilha")
        
        # Configuração do Google Meet
        st.subheader("📹 Google Meet")
        meeting_source = st.radio(
            "Fonte do Meeting",
            ["Auto (Calendar)", "Link Manual"],
            help="Auto: busca meeting ativo no Calendar | Manual: informe o link do meeting",
            key="meeting_source"
        )
        
        meeting_info = None
        if meeting_source == "Auto (Calendar)":
            if st.button("🔍 Buscar Meeting Ativo"):
                try:
                    with st.spinner("Buscando meeting ativo no Calendar..."):
                        meeting_info = st.session_state.google_integration.obter_meeting_ativo()
                        if meeting_info:
                            st.session_state.meeting_ativo = meeting_info
                            st.success(f"✅ Meeting encontrado: {meeting_info['title']}")
                            st.info(f"🔗 Link: {meeting_info['meet_link']}")
                        else:
                            st.warning("⚠️ Nenhum meeting ativo encontrado no Calendar")
                            st.info("💡 Dica: Verifique se há um evento do Google Meet acontecendo agora no seu Calendar")
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Erro: {error_msg}")
                    
                    # Detecta erro de API não habilitada
                    if 'não está habilitada' in error_msg or 'has not been used' in error_msg or 'is disabled' in error_msg:
                        st.warning("""
                        **⚠️ Google Calendar API não habilitada**
                        
                        Para habilitar a API:
                        1. Acesse o [Google Cloud Console](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
                        2. Selecione o projeto: **133165406108**
                        3. Clique em **"HABILITAR"**
                        4. Aguarde alguns minutos para a propagação
                        5. Tente novamente
                        
                        Ou use a opção **"Link Manual"** para informar o link do meeting diretamente.
                        """)
        else:
            meet_link = st.text_input(
                "Link do Google Meet",
                help="Cole o link completo do meeting (ex: https://meet.google.com/abc-defg-hij)",
                key="meet_link_input"
            )
            if meet_link and st.button("🔗 Conectar ao Meeting"):
                try:
                    with st.spinner("Conectando ao meeting..."):
                        meeting_info = st.session_state.google_integration.obter_meeting_por_link(meet_link)
                        if meeting_info:
                            st.session_state.meeting_ativo = meeting_info
                            st.success(f"✅ Conectado ao meeting: {meeting_info['meeting_code']}")
                            st.info(f"🔗 Link: {meeting_info['meet_link']}")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
        
        # Mostra informações do meeting ativo
        if st.session_state.get('meeting_ativo'):
            meeting_ativo = st.session_state.meeting_ativo
            st.success(f"📹 Meeting Ativo: {meeting_ativo.get('title', meeting_ativo.get('meeting_code', 'N/A'))}")
            if st.button("❌ Desconectar Meeting"):
                st.session_state.meeting_ativo = None
                st.rerun()
        
        # Filtro por turma
        st.subheader("🔍 Filtros")
        turma_selecionada = st.selectbox(
            "Turma",
            options=[None, 'A', 'B'],
            format_func=lambda x: "Todas" if x is None else f"Turma {x}"
        )
        
        # Controles do Meeting
        st.subheader("🎮 Controles do Meeting")
        
        meeting_code = obter_meeting_code()
        if not meeting_code:
            st.info("ℹ️ Configure um meeting primeiro para usar os controles")
        else:
            # Controle de Gravação
            st.write("**📹 Gravação**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("▶️ Iniciar Gravação", type="primary"):
                    try:
                        with st.spinner("Iniciando gravação..."):
                            resultado = st.session_state.google_integration.iniciar_gravacao(meeting_code)
                            if resultado:
                                st.success("✅ Gravação iniciada!")
                            else:
                                st.warning("⚠️ Não foi possível iniciar a gravação")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            with col2:
                if st.button("⏹️ Parar Gravação"):
                    try:
                        with st.spinner("Parando gravação..."):
                            resultado = st.session_state.google_integration.parar_gravacao(meeting_code)
                            if resultado:
                                st.success("✅ Gravação parada!")
                            else:
                                st.warning("⚠️ Não foi possível parar a gravação")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            
            # Status da Gravação
            if st.button("🔍 Verificar Status da Gravação"):
                try:
                    status = st.session_state.google_integration.obter_status_gravacao(meeting_code)
                    if status.get('gravando'):
                        st.success(f"🔴 Gravando: {status.get('status', 'ativo')}")
                    else:
                        st.info(f"⚪ Não está gravando: {status.get('status', 'inativo')}")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
            
            st.markdown("---")
            
            # Configuração de Breakout Rooms
            st.write("**🏫 Salas Temáticas (Breakout Rooms)**")
            
            st.info("ℹ️ **Importante:** O número de salas já está configurado no Google Calendar e não será alterado para evitar perda de atribuição dos cursistas.")
            
            duracao_minutos = st.number_input(
                "Duração (minutos)",
                min_value=5,
                max_value=120,
                value=60,
                help="Duração das salas temáticas em minutos (padrão: 60)"
            )
            
            if st.button("⚙️ Configurar Duração das Salas"):
                try:
                    with st.spinner("Configurando duração das salas temáticas..."):
                        resultado = st.session_state.google_integration.configurar_duracao_breakout_rooms(
                            meeting_code, duracao_minutos
                        )
                        if resultado:
                            st.success(f"✅ Duração configurada: {duracao_minutos} minutos")
                            st.info("ℹ️ Número de salas permanece inalterado (configurado no Calendar)")
                        else:
                            st.warning("⚠️ Não foi possível configurar a duração")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
            
            if st.button("🚀 Iniciar Salas Temáticas", type="primary"):
                try:
                    with st.spinner("Iniciando salas temáticas..."):
                        resultado = st.session_state.google_integration.iniciar_breakout_rooms(meeting_code)
                        if resultado:
                            st.success("✅ Salas temáticas iniciadas!")
                        else:
                            st.warning("⚠️ Não foi possível iniciar as salas")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
            
            st.markdown("---")
            
            # Listar Participantes da Sala Principal
            st.write("**👥 Participantes da Sala Principal**")
            if st.button("📋 Listar Participantes"):
                try:
                    with st.spinner("Buscando participantes da sala principal..."):
                        participantes = st.session_state.google_integration.listar_participantes_sala_principal(meeting_code)
                        
                        if participantes:
                            st.success(f"✅ {len(participantes)} participantes encontrados")
                            
                            # Cria DataFrame
                            df_participantes = pd.DataFrame(participantes)
                            
                            # Exibe tabela
                            st.dataframe(
                                df_participantes[['nome', 'email', 'tipo']],
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Download CSV
                            csv = df_participantes.to_csv(index=False)
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv,
                                file_name=f"participantes_sala_principal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                            
                            # Lista apenas emails
                            emails = [p['email'] for p in participantes if p.get('email')]
                            if emails:
                                st.write("**📧 Emails dos Participantes:**")
                                emails_texto = "\n".join(emails)
                                st.text_area("Emails (um por linha)", emails_texto, height=200)
                                
                                st.download_button(
                                    label="📥 Download Emails (TXT)",
                                    data=emails_texto,
                                    file_name=f"emails_participantes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                        else:
                            st.warning("⚠️ Nenhum participante encontrado ou API não disponível")
                            st.info("💡 A API do Google Meet pode ter limitações. Verifique se você tem permissões adequadas.")
                            
                except Exception as e:
                    st.error(f"❌ Erro ao listar participantes: {str(e)}")
                    st.info("💡 Isso pode ser normal - a API pode ter limitações ou requerer permissões especiais do Google Workspace.")
        
        # Atualização automática
        st.subheader("🔄 Atualização")
        auto_refresh = st.checkbox("Atualização Automática", value=False)
        if auto_refresh:
            st.info(f"Atualizando a cada {DASHBOARD_REFRESH_INTERVAL}s")
            time.sleep(DASHBOARD_REFRESH_INTERVAL)
            st.rerun()
    
    # Conteúdo principal
    if not st.session_state.dados_carregados:
        st.info("👆 Configure a conexão e carregue os dados na barra lateral para começar.")
        st.markdown("""
        ### 📋 Como usar:
        1. Clique em "Conectar Google APIs" na barra lateral
        2. Informe o ID da planilha Google Sheets
        3. Clique em "Carregar Dados"
        4. O dashboard será atualizado automaticamente
        """)
        return
    
    # Métricas gerais
    st.subheader("📈 Métricas Gerais")
    exibir_metricas_gerais(turma=turma_selecionada)
    
    st.markdown("---")
    
    # Gráficos
    st.subheader("📊 Visualizações")
    exibir_graficos(turma=turma_selecionada)
    
    st.markdown("---")
    
    # Status por sala
    st.subheader("🏫 Status por Sala")
    exibir_status_por_sala(turma=turma_selecionada)
    
    st.markdown("---")
    
    # Lista de problemas
    st.subheader("⚠️ Participantes com Problemas")
    problemas = st.session_state.monitor.obter_problemas(turma=turma_selecionada)
    
    if problemas:
        df_problemas = pd.DataFrame([
            {
                'Nome': p.nome,
                'Email': p.email,
                'Turma': p.turma,
                'Grupo Esperado': p.grupo_esperado,
                'Grupo Atual': p.grupo_atual or 'N/A',
                'Status': 'Ausente' if not p.presente else 'Sala Errada',
                'Telefone': p.telefone or 'N/A'
            }
            for p in problemas
        ])
        st.dataframe(df_problemas, use_container_width=True, hide_index=True)
        
        # Download CSV
        csv = df_problemas.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"problemas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.success("🎉 Nenhum problema detectado! Todos os participantes estão nas salas corretas.")
    
    st.markdown("---")
    
    # Recomendações da IA
    if st.session_state.agente_ia:
        exibir_recomendacoes_ia(turma=turma_selecionada)


if __name__ == "__main__":
    main()


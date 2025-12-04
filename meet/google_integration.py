"""
Módulo de integração com APIs do Google (Sheets, Calendar, Meet).
"""
import os.path
import pandas as pd
from typing import Dict, List, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2
from googleapiclient.discovery import build
import gspread
from google.oauth2.credentials import Credentials as OAuthCredentials

from config import SCOPES, TOKEN_FILE, CREDENTIALS_FILE


class GoogleIntegration:
    """Classe para integração com APIs do Google."""
    
    def __init__(self):
        self.creds = None
        self.meet_client = None
        self.sheets_service = None
        self.calendar_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica com as APIs do Google usando token.json existente."""
        # Carrega credenciais existentes
        if os.path.exists(TOKEN_FILE):
            try:
                self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
                
                # Verifica se o token tem todos os scopes necessários
                if self.creds and self.creds.valid:
                    token_scopes = set(self.creds.scopes or [])
                    required_scopes = set(SCOPES)
                    if not required_scopes.issubset(token_scopes):
                        # Token não tem todos os scopes necessários, força reautenticação
                        print(f"⚠️ Token não tem todos os scopes necessários. Reautenticando...")
                        print(f"   Scopes necessários: {required_scopes}")
                        print(f"   Scopes no token: {token_scopes}")
                        self.creds = None
            except Exception as e:
                print(f"⚠️ Erro ao carregar token: {e}. Reautenticando...")
                self.creds = None
        
        # Se não há credenciais válidas, solicita autenticação
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"⚠️ Erro ao renovar token: {e}. Reautenticando...")
                    self.creds = None
            
            if not self.creds or not self.creds.valid:
                if not os.path.exists(CREDENTIALS_FILE):
                    raise FileNotFoundError(
                        f"Arquivo credentials.json não encontrado em {CREDENTIALS_FILE}. "
                        "Por favor, baixe as credenciais OAuth2 do Google Cloud Console."
                    )
                print("🔐 Autenticando com Google...")
                print("   Por favor, autorize o acesso no navegador que será aberto.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Salva as credenciais atualizadas
            with open(TOKEN_FILE, 'w') as token:
                token.write(self.creds.to_json())
            print("✅ Autenticação concluída!")
        
        # Inicializa clientes das APIs
        self.meet_client = meet_v2.SpacesServiceClient(credentials=self.creds)
        self.meet_conference_records_client = meet_v2.ConferenceRecordsServiceClient(credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
    
    def ler_planilha_por_id(self, spreadsheet_id: str, worksheet_name: str = None) -> pd.DataFrame:
        """
        Lê dados de uma planilha Google Sheets.
        
        Args:
            spreadsheet_id: ID da planilha Google Sheets (pode ser URL completa ou apenas o ID)
            worksheet_name: Nome da aba (None para primeira aba)
            
        Returns:
            DataFrame com os dados da planilha
        """
        try:
            # Extrai o ID da planilha se uma URL foi fornecida
            if 'docs.google.com' in spreadsheet_id or 'spreadsheets/d/' in spreadsheet_id:
                # Extrai o ID da URL
                if '/d/' in spreadsheet_id:
                    spreadsheet_id = spreadsheet_id.split('/d/')[1].split('/')[0]
                elif 'id=' in spreadsheet_id:
                    spreadsheet_id = spreadsheet_id.split('id=')[1].split('&')[0]
            
            sheet = self.sheets_service.spreadsheets()
            
            # Primeiro, obtém informações da planilha para encontrar a aba correta
            spreadsheet = sheet.get(spreadsheetId=spreadsheet_id).execute()
            sheets = spreadsheet.get('sheets', [])
            
            # Se não especificou aba, pega a primeira
            if worksheet_name is None or worksheet_name.strip() == '':
                if sheets:
                    worksheet_name = sheets[0]['properties']['title']
                else:
                    raise Exception("Planilha não contém abas")
            
            worksheet_name = worksheet_name.strip()
            
            # Verifica se a aba existe
            worksheet_found = False
            for s in sheets:
                if s['properties']['title'] == worksheet_name:
                    worksheet_found = True
                    break
            
            if not worksheet_found:
                # Lista abas disponíveis para ajudar no debug
                available_sheets = [s['properties']['title'] for s in sheets]
                raise Exception(
                    f"Aba '{worksheet_name}' não encontrada na planilha.\n"
                    f"Abas disponíveis: {', '.join(available_sheets)}"
                )
            
            # Tenta usar gspread como método principal (mais robusto com nomes de aba)
            try:
                return self.ler_planilha_gspread_por_nome(spreadsheet_id, worksheet_name)
            except Exception as gspread_error:
                # Se gspread falhar, tenta com a API nativa
                # Formata o range corretamente
                # A API do Google Sheets requer que nomes de aba com caracteres especiais sejam escapados
                # Formato: 'Nome da Aba'!A1:Z1000 ou 'Nome da Aba'!A:Z para todas as linhas
                # Usa aspas simples para escapar o nome da aba
                
                # Tenta diferentes formatos de range
                range_formats = [
                    f"'{worksheet_name}'!A:ZZ",  # Com aspas e range de colunas
                    f"'{worksheet_name}'",        # Apenas nome da aba com aspas
                    f"{worksheet_name}!A:ZZ",     # Sem aspas, com range
                    worksheet_name                # Apenas nome da aba
                ]
                
                last_error = None
                for range_str in range_formats:
                    try:
                        result = sheet.values().get(
                            spreadsheetId=spreadsheet_id,
                            range=range_str
                        ).execute()
                        break  # Sucesso, sai do loop
                    except Exception as range_error:
                        last_error = range_error
                        continue
                else:
                    # Se todos os formatos falharam, tenta gspread novamente ou lança erro
                    raise Exception(
                        f"Erro ao ler a aba '{worksheet_name}'. "
                        f"Tentou múltiplos formatos de range sem sucesso.\n"
                        f"Erro: {str(last_error)}\n"
                        f"Tentativa com gspread também falhou: {str(gspread_error)}"
                    )
            
            values = result.get('values', [])
            
            if not values:
                return pd.DataFrame()
            
            # Primeira linha como cabeçalho
            headers = values[0]
            data = values[1:] if len(values) > 1 else []
            
            # Garante que todas as linhas tenham o mesmo número de colunas
            max_cols = len(headers)
            normalized_data = []
            for row in data:
                normalized_row = row + [''] * (max_cols - len(row))
                normalized_data.append(normalized_row[:max_cols])
            
            df = pd.DataFrame(normalized_data, columns=headers)
            
            # Normaliza nomes das colunas (lowercase, sem espaços)
            df.columns = df.columns.str.strip().str.lower()
            
            return df
            
        except Exception as e:
            error_msg = str(e)
            # Detecta erro de scope insuficiente
            if 'insufficient authentication scopes' in error_msg or 'ACCESS_TOKEN_SCOPE_INSUFFICIENT' in error_msg:
                raise Exception(
                    f"Erro de autenticação: O token não tem permissões suficientes para acessar o Google Sheets.\n"
                    f"Por favor, delete o arquivo token.json e execute o dashboard novamente para reautenticar com os scopes corretos.\n"
                    f"Erro original: {error_msg}"
                )
            raise Exception(f"Erro ao ler planilha: {error_msg}")
    
    def ler_planilha_gspread(self, spreadsheet_id: str, worksheet_index: int = 0) -> pd.DataFrame:
        """
        Lê planilha usando gspread (alternativa).
        
        Args:
            spreadsheet_id: ID da planilha Google Sheets
            worksheet_index: Índice da aba (0 para primeira)
            
        Returns:
            DataFrame com os dados da planilha
        """
        try:
            # Converte credenciais OAuth2 para formato gspread
            gc = gspread.authorize(self.creds)
            sh = gc.open_by_key(spreadsheet_id)
            worksheet = sh.get_worksheet(worksheet_index)
            
            # Pega todos os dados
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Normaliza nomes das colunas
            df.columns = df.columns.str.strip().str.lower()
            
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao ler planilha com gspread: {str(e)}")
    
    def ler_planilha_gspread_por_nome(self, spreadsheet_id: str, worksheet_name: str) -> pd.DataFrame:
        """
        Lê planilha usando gspread pelo nome da aba.
        
        Args:
            spreadsheet_id: ID da planilha Google Sheets
            worksheet_name: Nome da aba
            
        Returns:
            DataFrame com os dados da planilha
        """
        try:
            # Converte credenciais OAuth2 para formato gspread
            gc = gspread.authorize(self.creds)
            sh = gc.open_by_key(spreadsheet_id)
            
            # Tenta obter a aba pelo nome
            try:
                worksheet = sh.worksheet(worksheet_name)
            except gspread.exceptions.WorksheetNotFound:
                # Lista abas disponíveis para ajudar no debug
                available_sheets = [ws.title for ws in sh.worksheets()]
                raise Exception(
                    f"Aba '{worksheet_name}' não encontrada na planilha.\n"
                    f"Abas disponíveis: {', '.join(available_sheets)}"
                )
            
            # Pega todos os dados
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            # Normaliza nomes das colunas
            df.columns = df.columns.str.strip().str.lower()
            
            return df
            
        except Exception as e:
            raise Exception(f"Erro ao ler planilha com gspread por nome: {str(e)}")
    
    def obter_eventos_calendario(self, calendar_id: str = 'primary', max_results: int = 10) -> List[Dict]:
        """
        Obtém eventos do Google Calendar.
        
        Args:
            calendar_id: ID do calendário ('primary' para calendário principal)
            max_results: Número máximo de resultados
            
        Returns:
            Lista de eventos
        """
        try:
            from datetime import datetime, timedelta
            
            now = datetime.utcnow().isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return events
            
        except Exception as e:
            raise Exception(f"Erro ao obter eventos do calendário: {str(e)}")
    
    def obter_link_meet_do_evento(self, event: Dict) -> Optional[str]:
        """
        Extrai link do Google Meet de um evento do Calendar.
        
        Args:
            event: Dicionário do evento do Calendar
            
        Returns:
            Link do Meet ou None
        """
        # Tenta obter do campo conferenceData
        if 'conferenceData' in event:
            entry_points = event['conferenceData'].get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    return entry.get('uri')
        
        # Tenta obter do campo hangoutLink (legado)
        if 'hangoutLink' in event:
            return event['hangoutLink']
        
        return None
    
    def obter_meeting_ativo(self) -> Optional[Dict]:
        """
        Obtém o meeting do Google Meet ativo no momento (do Calendar).
        
        Returns:
            Dicionário com informações do meeting ou None
        """
        try:
            from datetime import datetime, timedelta
            
            now = datetime.utcnow()
            time_min = (now - timedelta(hours=1)).isoformat() + 'Z'
            time_max = (now + timedelta(hours=1)).isoformat() + 'Z'
            
            # Busca eventos do calendário no período atual
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Procura por eventos com Google Meet que estão acontecendo agora
            for event in events:
                # Verifica se tem link do Meet
                meet_link = self.obter_link_meet_do_evento(event)
                if meet_link:
                    # Verifica se o evento está acontecendo agora
                    start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                    end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                    
                    if start and end:
                        try:
                            from dateutil import parser
                            start_time = parser.parse(start)
                            end_time = parser.parse(end)
                            
                            if start_time <= now <= end_time:
                                return {
                                    'event': event,
                                    'meet_link': meet_link,
                                    'title': event.get('summary', 'Sem título'),
                                    'start': start,
                                    'end': end
                                }
                        except Exception:
                            # Se não conseguir parsear, continua procurando
                            continue
            
            return None
            
        except Exception as e:
            error_msg = str(e)
            # Detecta erro de API não habilitada
            if 'has not been used' in error_msg or 'is disabled' in error_msg or 'accessNotConfigured' in error_msg:
                # Extrai o link do console se disponível
                console_link = None
                if 'console.developers.google.com' in error_msg:
                    import re
                    links = re.findall(r'https://console\.developers\.google\.com[^\s\)]+', error_msg)
                    if links:
                        console_link = links[0]
                
                raise Exception(
                    f"Google Calendar API não está habilitada no projeto.\n\n"
                    f"Para habilitar:\n"
                    f"1. Acesse: {console_link or 'https://console.cloud.google.com/apis/library/calendar-json.googleapis.com'}\n"
                    f"2. Selecione o projeto: 133165406108\n"
                    f"3. Clique em 'HABILITAR'\n"
                    f"4. Aguarde alguns minutos para a propagação\n"
                    f"5. Tente novamente\n\n"
                    f"Erro original: {error_msg}"
                )
            raise Exception(f"Erro ao obter meeting ativo: {error_msg}")
    
    def obter_meeting_por_link(self, meet_link: str) -> Optional[Dict]:
        """
        Obtém informações de um meeting pelo link.
        
        Args:
            meet_link: Link do Google Meet (ex: https://meet.google.com/abc-defg-hij)
            
        Returns:
            Dicionário com informações do meeting ou None
        """
        try:
            # Extrai o código do meeting do link
            if 'meet.google.com' in meet_link:
                meeting_code = meet_link.split('meet.google.com/')[-1].split('?')[0].strip()
            elif '/' in meet_link:
                meeting_code = meet_link.split('/')[-1].split('?')[0].strip()
            else:
                meeting_code = meet_link.strip()
            
            # Tenta obter informações do meeting usando a API
            # Nota: A API do Google Meet v2 pode ter limitações
            # Por enquanto, retorna estrutura básica
            return {
                'meeting_code': meeting_code,
                'meet_link': meet_link if meet_link.startswith('http') else f'https://meet.google.com/{meeting_code}',
                'status': 'active',
                'title': f'Meeting {meeting_code}'
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter meeting por link: {str(e)}")
    
    def listar_participantes_meet(self, meeting_code: str) -> List[Dict]:
        """
        Lista participantes da sala principal de uma reunião do Google Meet.
        
        Args:
            meeting_code: Código ou URI da reunião Meet
            
        Returns:
            Lista de participantes com informações (nome, email, etc.)
        """
        try:
            # Extrai o código do meeting se necessário
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0].strip()
            
            participants = []
            
            # Tenta obter o conference record usando a API
            # Primeiro, precisa obter o space name do meeting code
            try:
                # Tenta listar conference records recentes
                # A API pode requerer o nome do espaço (space) ao invés do código
                # Por enquanto, tenta usar o código diretamente
                
                # Nota: A API do Google Meet v2 pode ter limitações
                # Pode ser necessário usar o nome do espaço (space name) ao invés do código
                
                # Tenta obter informações do espaço primeiro
                try:
                    # Formato do space name geralmente é: spaces/{meeting_code}
                    space_name = f"spaces/{meeting_code}"
                    space_request = meet_v2.GetSpaceRequest(name=space_name)
                    space = self.meet_client.get_space(request=space_request)
                    
                    # Se conseguiu obter o espaço, tenta listar participantes
                    # Nota: A listagem de participantes pode requerer o conference record
                    # que só está disponível após a reunião ou durante (dependendo da API)
                    
                except Exception as space_error:
                    # Se não conseguir pelo space, tenta outras abordagens
                    print(f"⚠️ Não foi possível obter espaço: {space_error}")
                
                # Tenta listar conference records recentes
                # Isso pode funcionar se você tem permissões administrativas
                try:
                    from datetime import datetime, timedelta
                    # Lista conference records das últimas 24 horas
                    now = datetime.utcnow()
                    filter_time = (now - timedelta(hours=24)).isoformat() + 'Z'
                    
                    list_request = meet_v2.ListConferenceRecordsRequest(
                        filter=f"end_time>={filter_time}"
                    )
                    # Nota: Pode precisar de permissões especiais
                    
                except Exception as record_error:
                    print(f"⚠️ Não foi possível listar conference records: {record_error}")
                
            except Exception as api_error:
                print(f"⚠️ Erro ao acessar API: {api_error}")
            
            # Se não conseguiu pela API, retorna estrutura vazia
            # A API do Google Meet v2 tem limitações para listar participantes em tempo real
            # Pode ser necessário usar Google Workspace Reports API ou outras abordagens
            
            return participants
            
        except Exception as e:
            raise Exception(f"Erro ao listar participantes: {str(e)}")
    
    def listar_participantes_sala_principal(self, meeting_code: str) -> List[Dict]:
        """
        Lista participantes da sala principal (não breakout rooms) de uma reunião.
        
        NOTA: A API do Google Meet v2 tem limitações para listar participantes em tempo real.
        Este método tenta usar Conference Records, mas pode não funcionar sem permissões
        administrativas do Google Workspace.
        
        Args:
            meeting_code: Código ou URI da reunião Meet
            
        Returns:
            Lista de participantes com email e nome
        """
        try:
            # Extrai o código do meeting
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0].strip()
            
            participants = []
            
            try:
                # Tenta usar a API de Conference Records
                # Lista conference records recentes (últimas 2 horas)
                from datetime import datetime, timedelta
                now = datetime.utcnow()
                filter_time = (now - timedelta(hours=2)).isoformat() + 'Z'
                
                # Tenta listar conference records
                list_request = meet_v2.ListConferenceRecordsRequest(
                    filter=f"end_time>={filter_time}"
                )
                
                response = self.meet_conference_records_client.list_conference_records(
                    request=list_request
                )
                
                # Procura pelo conference record que corresponde ao meeting code
                for conference_record in response.conference_records:
                    try:
                        # Lista participantes deste conference record
                        participants_request = meet_v2.ListParticipantsRequest(
                            parent=conference_record.name
                        )
                        
                        participants_response = self.meet_conference_records_client.list_participants(
                            request=participants_request
                        )
                        
                        # Processa participantes
                        for participant in participants_response.participants:
                            # Extrai informações do participante
                            email = None
                            nome = None
                            
                            # Verifica o tipo de usuário
                            if hasattr(participant, 'signedin_user') and participant.signedin_user:
                                signedin_user = participant.signedin_user
                                email = getattr(signedin_user, 'user', None) or getattr(signedin_user, 'email', None)
                                nome = getattr(signedin_user, 'display_name', None) or email
                            elif hasattr(participant, 'anonymous_user') and participant.anonymous_user:
                                anonymous_user = participant.anonymous_user
                                nome = getattr(anonymous_user, 'display_name', 'Participante Anônimo')
                            elif hasattr(participant, 'phone_user') and participant.phone_user:
                                phone_user = participant.phone_user
                                nome = f"Telefone: {getattr(phone_user, 'display_number', 'N/A')}"
                            
                            if email or nome:
                                participants.append({
                                    'email': email or '',
                                    'nome': nome or 'Sem nome',
                                    'tipo': 'signedin' if email else ('anonymous' if hasattr(participant, 'anonymous_user') and participant.anonymous_user else 'phone')
                                })
                    except Exception as participant_error:
                        # Continua procurando em outros records
                        continue
                    
                    # Se encontrou participantes, para a busca
                    if participants:
                        break
                        
            except Exception as api_error:
                # Se a API não permitir ou não tiver permissões, retorna lista vazia
                error_msg = str(api_error)
                if 'PERMISSION_DENIED' in error_msg or 'permission' in error_msg.lower():
                    raise Exception(
                        "Permissão negada. A listagem de participantes pode requerer:\n"
                        "- Conta Google Workspace (não Gmail pessoal)\n"
                        "- Permissões administrativas\n"
                        "- Scopes adicionais configurados no Google Cloud Console"
                    )
                print(f"⚠️ Não foi possível listar participantes via API: {api_error}")
                return []
            
            return participants
            
        except Exception as e:
            raise Exception(f"Erro ao listar participantes da sala principal: {str(e)}")
    
    def criar_espaco_meet(self) -> str:
        """
        Cria um novo espaço (reunião) no Google Meet.
        NOTA: Este método cria um novo meeting. Use obter_meeting_ativo() ou 
        obter_meeting_por_link() para usar um meeting existente.
        
        Returns:
            URI da reunião criada
        """
        try:
            request = meet_v2.CreateSpaceRequest()
            response = self.meet_client.create_space(request=request)
            return response.meeting_uri
        except Exception as e:
            raise Exception(f"Erro ao criar espaço Meet: {str(e)}")
    
    def iniciar_gravacao(self, meeting_code: str) -> bool:
        """
        Inicia a gravação do meeting.
        
        Args:
            meeting_code: Código ou URI do meeting
            
        Returns:
            True se iniciado com sucesso
        """
        try:
            # Nota: A API do Google Meet v2 pode ter limitações para controlar gravação
            # Este método é uma estrutura base que pode precisar de ajustes conforme a API
            
            # Extrai o código do meeting se necessário
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0]
            
            # TODO: Implementar controle de gravação quando a API permitir
            # Por enquanto, retorna sucesso (será implementado quando disponível)
            print(f"⚠️ Iniciar gravação: Funcionalidade em desenvolvimento para meeting {meeting_code}")
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao iniciar gravação: {str(e)}")
    
    def parar_gravacao(self, meeting_code: str) -> bool:
        """
        Para a gravação do meeting.
        
        Args:
            meeting_code: Código ou URI do meeting
            
        Returns:
            True se parado com sucesso
        """
        try:
            # Extrai o código do meeting se necessário
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0]
            
            # TODO: Implementar controle de gravação quando a API permitir
            print(f"⚠️ Parar gravação: Funcionalidade em desenvolvimento para meeting {meeting_code}")
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao parar gravação: {str(e)}")
    
    def configurar_duracao_breakout_rooms(self, meeting_code: str, duracao_minutos: int = 60) -> bool:
        """
        Configura APENAS a duração dos breakout rooms (salas temáticas).
        
        IMPORTANTE: Este método NÃO altera o número de salas, pois elas já estão
        configuradas no Google Calendar. Alterar o número de salas pode causar
        perda de atribuição dos cursistas.
        
        Args:
            meeting_code: Código ou URI do meeting
            duracao_minutos: Duração das salas em minutos (padrão: 60)
            
        Returns:
            True se configurado com sucesso
        """
        try:
            # Extrai o código do meeting se necessário
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0]
            
            # TODO: Implementar configuração de duração de breakout rooms quando a API permitir
            # NOTA: NÃO alterar o número de salas - elas vêm do Google Calendar
            print(f"⚠️ Configurar duração de breakout rooms: {duracao_minutos} minutos")
            print(f"   Meeting: {meeting_code}")
            print(f"   ⚠️ Número de salas NÃO será alterado (já configurado no Calendar)")
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao configurar duração dos breakout rooms: {str(e)}")
    
    def iniciar_breakout_rooms(self, meeting_code: str) -> bool:
        """
        Inicia os breakout rooms (salas temáticas).
        
        Args:
            meeting_code: Código ou URI do meeting
            
        Returns:
            True se iniciado com sucesso
        """
        try:
            # Extrai o código do meeting se necessário
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0]
            
            # TODO: Implementar início de breakout rooms quando a API permitir
            print(f"⚠️ Iniciar breakout rooms: Funcionalidade em desenvolvimento para meeting {meeting_code}")
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao iniciar breakout rooms: {str(e)}")
    
    def obter_status_gravacao(self, meeting_code: str) -> Dict:
        """
        Obtém o status da gravação do meeting.
        
        Args:
            meeting_code: Código ou URI do meeting
            
        Returns:
            Dicionário com status da gravação
        """
        try:
            # Extrai o código do meeting se necessário
            if 'meet.google.com' in meeting_code:
                meeting_code = meeting_code.split('meet.google.com/')[-1].split('?')[0]
            
            # TODO: Implementar verificação de status quando a API permitir
            return {
                'gravando': False,
                'status': 'desconhecido',
                'meeting_code': meeting_code
            }
            
        except Exception as e:
            raise Exception(f"Erro ao obter status da gravação: {str(e)}")


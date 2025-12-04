"""
Módulo de monitoramento de participantes nas salas temáticas.
"""
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from config import NUM_GRUPOS, TURMAS


@dataclass
class ParticipanteStatus:
    """Status de um participante."""
    email: str
    nome: str
    turma: str
    grupo_esperado: int
    grupo_atual: Optional[int] = None
    presente: bool = False
    em_sala_errada: bool = False
    telefone: Optional[str] = None


@dataclass
class StatusSala:
    """Status de uma sala temática."""
    grupo: int
    turma: str
    total_esperado: int
    total_presente: int
    total_ausente: int
    participantes_presentes: List[ParticipanteStatus]
    participantes_ausentes: List[ParticipanteStatus]
    participantes_errados: List[ParticipanteStatus]  # Estão na sala mas não deveriam


class MonitorSalas:
    """Monitor de participantes nas salas temáticas."""
    
    def __init__(self, dados_planilha: pd.DataFrame):
        """
        Inicializa o monitor com dados da planilha.
        
        Args:
            dados_planilha: DataFrame com colunas: turma, grupo, nome, email, telefone
        """
        self.dados_planilha = dados_planilha
        self.participantes_esperados = self._processar_dados_planilha()
        self.participantes_reais: Dict[str, Dict] = {}  # {email: {grupo, turma, ...}}
        self.status_salas: Dict[Tuple[str, int], StatusSala] = {}
    
    def _processar_dados_planilha(self) -> Dict[str, ParticipanteStatus]:
        """
        Processa dados da planilha e cria dicionário de participantes esperados.
        
        Returns:
            Dicionário {email: ParticipanteStatus}
        """
        participantes = {}
        
        # Mapeamento de possíveis nomes de colunas para nomes padrão
        mapeamento_colunas = {
            'turma': [
                'indique abaixo o melhor período para realização das atividades síncronas',
                'turma',
                'período',
                'periodo'
            ],
            'grupo': [
                'grupo'
            ],
            'nome': [
                'nome completo',
                'nome',
                'nome completo (sem abreviação)'
            ],
            'email': [
                'escreva o e-mail',
                'e-mail',
                'email',
                'g-mail',
                'gmail',
                'escreva o e-mail (g-mail) o qual você irá acessar as aulas síncronas pelo google meet'
            ],
            'telefone': [
                'número do telefone',
                'telefone',
                'whatsapp',
                'número do telefone com ddd (whatsapp)',
                'ddd',
                'celular'
            ]
        }
        
        # Normaliza colunas (lowercase, remove espaços extras)
        colunas_originais = self.dados_planilha.columns
        colunas_normalizadas = {col: str(col).lower().strip() for col in colunas_originais}
        
        # Encontra colunas relevantes usando o mapeamento
        def encontrar_coluna(tipo: str) -> Optional[str]:
            """Encontra a coluna correspondente ao tipo usando o mapeamento."""
            for col_original, col_normalizada in colunas_normalizadas.items():
                for padrao in mapeamento_colunas[tipo]:
                    if padrao in col_normalizada:
                        return col_original
            return None
        
        turma_col = encontrar_coluna('turma')
        grupo_col = encontrar_coluna('grupo')
        nome_col = encontrar_coluna('nome')
        email_col = encontrar_coluna('email')
        telefone_col = encontrar_coluna('telefone')
        
        # Valida colunas obrigatórias
        if not email_col:
            raise ValueError(
                "Coluna de email não encontrada. "
                "Procure por colunas contendo: 'email', 'e-mail', 'g-mail'"
            )
        if not nome_col:
            raise ValueError(
                "Coluna de nome não encontrada. "
                "Procure por colunas contendo: 'nome completo', 'nome'"
            )
        if not turma_col:
            raise ValueError(
                "Coluna de turma não encontrada. "
                "Procure por colunas contendo: 'período', 'turma', 'atividades síncronas'"
            )
        if not grupo_col:
            raise ValueError(
                "Coluna de grupo não encontrada. "
                "Procure por colunas contendo: 'grupo'"
            )
        
        # Processa cada linha
        for idx, row in self.dados_planilha.iterrows():
            try:
                # Extrai email
                email = str(row[email_col]).strip().lower()
                if '@' not in email or email == 'nan' or email == '':
                    continue
                
                # Extrai nome
                nome = str(row[nome_col]).strip() if pd.notna(row[nome_col]) else email
                if nome == 'nan' or nome == '':
                    nome = email
                
                # Extrai turma (pode ser texto, precisa extrair A ou B)
                turma_str = str(row[turma_col]).strip().upper() if pd.notna(row[turma_col]) else ''
                # Tenta encontrar A ou B no texto (procura por padrões comuns)
                turma = None
                # Primeiro, procura por "TURMA A" ou "TURMA B"
                for t in TURMAS:
                    if f'TURMA {t}' in turma_str or f' {t} ' in turma_str or turma_str.startswith(t) or turma_str.endswith(t):
                        turma = t
                        break
                # Se não encontrou, procura apenas pela letra
                if turma is None:
                    for t in TURMAS:
                        if t in turma_str:
                            turma = t
                            break
                # Se ainda não encontrou, tenta pegar o primeiro caractere se for A ou B
                if turma is None and turma_str:
                    primeiro_char = turma_str[0]
                    if primeiro_char in TURMAS:
                        turma = primeiro_char
                
                if turma not in TURMAS:
                    continue
                
                # Extrai grupo
                grupo_val = row[grupo_col]
                if pd.isna(grupo_val):
                    continue
                try:
                    grupo = int(float(grupo_val))  # Converte para int (float primeiro para lidar com "1.0")
                except (ValueError, TypeError):
                    continue
                
                if grupo < 1 or grupo > NUM_GRUPOS:
                    continue
                
                # Extrai telefone (opcional)
                telefone = None
                if telefone_col and pd.notna(row.get(telefone_col, None)):
                    telefone = str(row[telefone_col]).strip()
                    if telefone == 'nan' or telefone == '':
                        telefone = None
                
                # Cria participante
                participantes[email] = ParticipanteStatus(
                    email=email,
                    nome=nome,
                    turma=turma,
                    grupo_esperado=grupo,
                    telefone=telefone
                )
                
            except Exception as e:
                # Ignora linhas com erro, mas loga para debug
                print(f"⚠️ Erro ao processar linha {idx}: {e}")
                continue
        
        return participantes
    
    def atualizar_participantes_reais(self, participantes_por_grupo: Dict[int, List[Dict]], participantes_por_turma_grupo: Dict[Tuple[str, int], List[Dict]] = None):
        """
        Atualiza lista de participantes reais por grupo.
        
        Args:
            participantes_por_grupo: Dict {grupo: [{'email': str, 'nome': str, ...}, ...]}
                Método legado - apenas grupo (sem considerar turma)
            participantes_por_turma_grupo: Dict {(turma, grupo): [{'email': str, 'nome': str, ...}, ...]}
                Método preferido - considera turma E grupo
        """
        self.participantes_reais = {}
        
        # Se fornecido participantes por (turma, grupo), usa esse método
        if participantes_por_turma_grupo:
            for (turma, grupo), participantes in participantes_por_turma_grupo.items():
                for participante in participantes:
                    email = participante.get('email', '').strip().lower()
                    if '@' not in email:
                        continue
                    
                    self.participantes_reais[email] = {
                        'grupo': grupo,
                        'turma': turma,
                        'nome': participante.get('nome', email),
                        'email': email
                    }
        else:
            # Método legado - apenas grupo (sem turma)
            # Tenta inferir turma dos participantes esperados se disponível
            for grupo, participantes in participantes_por_grupo.items():
                for participante in participantes:
                    email = participante.get('email', '').strip().lower()
                    if '@' not in email:
                        continue
                    
                    # Tenta encontrar a turma do participante esperado
                    turma = None
                    if email in self.participantes_esperados:
                        turma = self.participantes_esperados[email].turma
                    
                    self.participantes_reais[email] = {
                        'grupo': grupo,
                        'turma': turma,
                        'nome': participante.get('nome', email),
                        'email': email
                    }
    
    def calcular_status(self, turma: Optional[str] = None) -> Dict[Tuple[str, int], StatusSala]:
        """
        Calcula status de todas as salas.
        
        Args:
            turma: Filtrar por turma específica (None para todas)
            
        Returns:
            Dicionário {(turma, grupo): StatusSala}
        """
        self.status_salas = {}
        
        # Filtra participantes por turma se especificado
        participantes_filtrados = {
            email: p for email, p in self.participantes_esperados.items()
            if turma is None or p.turma == turma
        }
        
        # Agrupa participantes esperados por (turma, grupo)
        esperados_por_sala: Dict[Tuple[str, int], List[ParticipanteStatus]] = {}
        for participante in participantes_filtrados.values():
            key = (participante.turma, participante.grupo_esperado)
            if key not in esperados_por_sala:
                esperados_por_sala[key] = []
            esperados_por_sala[key].append(participante)
        
        # Processa cada sala
        for (turma_sala, grupo), participantes_esperados_sala in esperados_por_sala.items():
            presentes = []
            ausentes = []
            errados = []
            
            # Verifica quais participantes esperados estão presentes
            for participante in participantes_esperados_sala:
                if participante.email in self.participantes_reais:
                    participante_real = self.participantes_reais[participante.email]
                    grupo_real = participante_real['grupo']
                    turma_real = participante_real.get('turma')
                    
                    participante.presente = True
                    participante.grupo_atual = grupo_real
                    
                    # Verifica se está no grupo E turma corretos
                    grupo_correto = grupo_real == participante.grupo_esperado
                    turma_correta = (turma_real is None) or (turma_real == participante.turma)
                    
                    if grupo_correto and turma_correta:
                        presentes.append(participante)
                    else:
                        participante.em_sala_errada = True
                        errados.append(participante)
                else:
                    ausentes.append(participante)
            
            # Verifica participantes que estão na sala mas não deveriam estar
            # (participantes não esperados ou de outra turma)
            for email, participante_real in self.participantes_reais.items():
                grupo_real = participante_real['grupo']
                turma_real = participante_real.get('turma')
                
                # Verifica se está no grupo E turma corretos
                if grupo_real == grupo:
                    # Verifica se este participante deveria estar aqui
                    if email not in participantes_filtrados:
                        # Participante não esperado nesta sala
                        participante_errado = ParticipanteStatus(
                            email=email,
                            nome=participante_real.get('nome', email),
                            turma=turma_real or '?',
                            grupo_esperado=-1,  # Não esperado
                            grupo_atual=grupo_real,
                            presente=True,
                            em_sala_errada=True
                        )
                        errados.append(participante_errado)
                    else:
                        # Verifica se está na turma correta
                        participante_esperado = participantes_filtrados[email]
                        if participante_esperado.turma != turma_sala:
                            # Participante está na sala correta do grupo, mas da turma errada
                            # Marca como erro - cada turma tem seus próprios grupos
                            participante_esperado.em_sala_errada = True
                            if participante_esperado not in errados:
                                errados.append(participante_esperado)
            
            # Cria status da sala
            status = StatusSala(
                grupo=grupo,
                turma=turma_sala,
                total_esperado=len(participantes_esperados_sala),
                total_presente=len(presentes),
                total_ausente=len(ausentes),
                participantes_presentes=presentes,
                participantes_ausentes=ausentes,
                participantes_errados=errados
            )
            
            self.status_salas[(turma_sala, grupo)] = status
        
        return self.status_salas
    
    def obter_estatisticas_gerais(self, turma: Optional[str] = None) -> Dict:
        """
        Obtém estatísticas gerais do monitoramento.
        
        Args:
            turma: Filtrar por turma específica (None para todas)
            
        Returns:
            Dicionário com estatísticas
        """
        if not self.status_salas:
            self.calcular_status(turma=turma)
        
        total_esperado = 0
        total_presente = 0
        total_ausente = 0
        total_errados = 0
        
        for status in self.status_salas.values():
            if turma is None or status.turma == turma:
                total_esperado += status.total_esperado
                total_presente += status.total_presente
                total_ausente += status.total_ausente
                total_errados += len(status.participantes_errados)
        
        percentual_presente = (total_presente / total_esperado * 100) if total_esperado > 0 else 0
        percentual_ausente = (total_ausente / total_esperado * 100) if total_esperado > 0 else 0
        
        return {
            'total_esperado': total_esperado,
            'total_presente': total_presente,
            'total_ausente': total_ausente,
            'total_errados': total_errados,
            'percentual_presente': percentual_presente,
            'percentual_ausente': percentual_ausente,
            'timestamp': datetime.now().isoformat()
        }
    
    def obter_problemas(self, turma: Optional[str] = None) -> List[ParticipanteStatus]:
        """
        Obtém lista de todos os participantes com problemas.
        
        Args:
            turma: Filtrar por turma específica (None para todas)
            
        Returns:
            Lista de participantes com problemas (ausentes ou em sala errada)
        """
        problemas = []
        
        for status in self.status_salas.values():
            if turma is None or status.turma == turma:
                problemas.extend(status.participantes_ausentes)
                problemas.extend(status.participantes_errados)
        
        return problemas


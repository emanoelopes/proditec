"""
Agente de IA usando Ollama para análise inteligente de discrepâncias.
"""
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime

from config import OLLAMA_BASE_URL, OLLAMA_MODEL
from monitor import MonitorSalas, ParticipanteStatus, StatusSala


class AgenteIA:
    """Agente de IA para análise de dados de participação."""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        """
        Inicializa o agente de IA.
        
        Args:
            base_url: URL base do Ollama (padrão: http://localhost:11434)
            model: Nome do modelo a ser usado (padrão: llama3)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.api_url = f"{self.base_url}/api/generate"
    
    def _chamar_ollama(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Chama a API do Ollama.
        
        Args:
            prompt: Prompt do usuário
            system_prompt: Prompt do sistema (opcional)
            
        Returns:
            Resposta do modelo
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erro ao chamar Ollama: {str(e)}")
    
    def analisar_discrepancias(self, monitor: MonitorSalas, turma: Optional[str] = None) -> Dict:
        """
        Analisa discrepâncias e gera recomendações.
        
        Args:
            monitor: Instância do MonitorSalas
            turma: Filtrar por turma específica (None para todas)
            
        Returns:
            Dicionário com análise e recomendações
        """
        estatisticas = monitor.obter_estatisticas_gerais(turma=turma)
        problemas = monitor.obter_problemas(turma=turma)
        status_salas = monitor.calcular_status(turma=turma)
        
        # Prepara dados para análise
        dados_analise = {
            'estatisticas': estatisticas,
            'total_problemas': len(problemas),
            'problemas_por_tipo': {
                'ausentes': len([p for p in problemas if not p.presente]),
                'em_sala_errada': len([p for p in problemas if p.em_sala_errada])
            },
            'salas_com_problemas': [
                {
                    'turma': status.turma,
                    'grupo': status.grupo,
                    'total_ausente': status.total_ausente,
                    'total_errados': len(status.participantes_errados)
                }
                for status in status_salas.values()
                if status.total_ausente > 0 or len(status.participantes_errados) > 0
            ]
        }
        
        # Cria prompt para análise
        prompt = self._criar_prompt_analise(dados_analise, problemas)
        
        system_prompt = """Você é um assistente especializado em análise de dados de participação em encontros síncronos.
        Sua função é analisar discrepâncias entre participantes esperados e participantes reais,
        identificar problemas e sugerir ações corretivas para o técnico de TI.
        
        Responda sempre em formato JSON com a seguinte estrutura:
        {
            "resumo": "Resumo breve da situação",
            "problemas_principais": ["lista", "de", "problemas"],
            "recomendacoes": ["lista", "de", "recomendações"],
            "prioridade": "alta|media|baixa",
            "acoes_sugeridas": ["ação 1", "ação 2"]
        }"""
        
        try:
            resposta = self._chamar_ollama(prompt, system_prompt)
            
            # Tenta extrair JSON da resposta
            json_str = self._extrair_json_da_resposta(resposta)
            analise = json.loads(json_str)
            
            analise['timestamp'] = datetime.now().isoformat()
            analise['dados_originais'] = dados_analise
            
            return analise
            
        except Exception as e:
            # Em caso de erro, retorna análise básica
            return {
                'resumo': f"Análise automática não disponível: {str(e)}",
                'problemas_principais': [
                    f"{len([p for p in problemas if not p.presente])} participantes ausentes",
                    f"{len([p for p in problemas if p.em_sala_errada])} participantes em sala errada"
                ],
                'recomendacoes': [
                    "Verificar conexão dos participantes ausentes",
                    "Verificar se participantes estão nas salas corretas"
                ],
                'prioridade': 'media',
                'acoes_sugeridas': [
                    "Contatar participantes ausentes",
                    "Verificar atribuição de salas"
                ],
                'timestamp': datetime.now().isoformat(),
                'dados_originais': dados_analise
            }
    
    def _criar_prompt_analise(self, dados: Dict, problemas: List[ParticipanteStatus]) -> str:
        """Cria prompt estruturado para análise."""
        prompt = f"""Analise os seguintes dados de participação em encontros síncronos:

ESTATÍSTICAS:
- Total esperado: {dados['estatisticas']['total_esperado']}
- Total presente: {dados['estatisticas']['total_presente']}
- Total ausente: {dados['estatisticas']['total_ausente']}
- Total em sala errada: {dados['problemas_por_tipo']['em_sala_errada']}
- Percentual de presença: {dados['estatisticas']['percentual_presente']:.1f}%

PROBLEMAS DETECTADOS:
Total de problemas: {dados['total_problemas']}

SALAS COM PROBLEMAS:
{json.dumps(dados['salas_com_problemas'], indent=2, ensure_ascii=False)}

PARTICIPANTES COM PROBLEMAS (primeiros 10):
{self._formatar_problemas_para_prompt(problemas[:10])}

Analise essa situação e forneça:
1. Um resumo claro da situação
2. Lista dos problemas principais identificados
3. Recomendações práticas para o técnico de TI
4. Prioridade (alta/média/baixa)
5. Ações sugeridas em ordem de prioridade

Responda APENAS em formato JSON válido, sem texto adicional antes ou depois."""
        
        return prompt
    
    def _formatar_problemas_para_prompt(self, problemas: List[ParticipanteStatus]) -> str:
        """Formata lista de problemas para o prompt."""
        if not problemas:
            return "Nenhum problema detectado."
        
        linhas = []
        for p in problemas:
            tipo = "AUSENTE" if not p.presente else f"EM SALA ERRADA (esperado: {p.grupo_esperado}, atual: {p.grupo_atual})"
            linhas.append(f"- {p.nome} ({p.email}) - Turma {p.turma}, Grupo {p.grupo_esperado} - {tipo}")
        
        return "\n".join(linhas)
    
    def _extrair_json_da_resposta(self, resposta: str) -> str:
        """Extrai JSON da resposta do modelo."""
        # Tenta encontrar JSON na resposta
        resposta = resposta.strip()
        
        # Se começa com {, assume que é JSON direto
        if resposta.startswith('{'):
            # Encontra o último }
            ultimo_brace = resposta.rfind('}')
            if ultimo_brace > 0:
                return resposta[:ultimo_brace + 1]
        
        # Tenta encontrar JSON entre ```json e ```
        if '```json' in resposta:
            inicio = resposta.find('```json') + 7
            fim = resposta.find('```', inicio)
            if fim > inicio:
                return resposta[inicio:fim].strip()
        
        # Tenta encontrar JSON entre ``` e ```
        if '```' in resposta:
            partes = resposta.split('```')
            for parte in partes:
                parte = parte.strip()
                if parte.startswith('{') and parte.endswith('}'):
                    return parte
        
        # Se não encontrou, retorna resposta completa (pode causar erro, mas é melhor que nada)
        return resposta
    
    def gerar_alerta(self, problema: ParticipanteStatus) -> str:
        """
        Gera mensagem de alerta para um participante com problema.
        
        Args:
            problema: ParticipanteStatus com problema
            
        Returns:
            Mensagem de alerta formatada
        """
        if not problema.presente:
            mensagem = f"ALERTA: {problema.nome} ({problema.email}) está AUSENTE da sala {problema.grupo_esperado} (Turma {problema.turma})"
        elif problema.em_sala_errada:
            mensagem = f"ALERTA: {problema.nome} ({problema.email}) está na SALA ERRADA. Esperado: Grupo {problema.grupo_esperado} (Turma {problema.turma}), Atual: Grupo {problema.grupo_atual}"
        else:
            mensagem = f"INFO: {problema.nome} está presente corretamente"
        
        return mensagem


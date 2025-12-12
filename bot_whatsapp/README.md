# 🤖 WhatsApp Mass Messenger Bot

Este é um bot simples para envio de mensagens em massa via WhatsApp Web, utilizando Python e Selenium. Ele lê uma lista de contatos de um arquivo CSV e envia uma mensagem personalizada para cada um.

## 📋 Pré-requisitos

*   **Python 3.8+** instalado.
*   **Google Chrome** instalado.
*   Uma conta ativa no **WhatsApp**.

## 🚀 Instalação

1.  Acesse a pasta do projeto:
    ```bash
    cd /home/emanoel/proditec/bot_whatsapp
    ```

2.  Crie e ative um ambiente virtual (recomendado):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

## 📝 Preparação

### 1. Lista de Contatos (.csv)
Crie um arquivo CSV (ex: `contatos.csv`) com, no mínimo, uma coluna para o telefone. Você pode incluir uma coluna de nome para personalização.

**Formato esperado:**
```csv
phone,name
5511999999999,João Silva
5521988888888,Maria Oliveira
```
*   **phone:** Deve conter o código do país (55 para Brasil) + DDD + Número. Evite espaços ou traços, embora o bot tente enviar mesmo assim.
*   **name:** (Opcional) Usado para substituir `{name}` na mensagem.

### 2. Mensagem
Você pode definir a mensagem diretamente no comando ou usar um arquivo de texto.

*   **Arquivo de texto (Recomendado):** Crie um arquivo `mensagem.txt` com o conteúdo. Quebras de linha e links funcionam normalmente.
    ```text
    Olá {name},
    
    Tudo bem? Segue o link: https://exemplo.com
    ```
*   **Linha de comando:** Texto simples passado via terminal.

## ▶️ Como Usar

Com o ambiente virtual ativado (`source .venv/bin/activate`), execute:

### Usando mensagem de um arquivo (Recomendado):
```bash
python main.py --csv contatos.csv --message-file mensagem.txt
```

### Usando mensagem direto no comando:
```bash
python main.py --csv contatos.csv --message "Olá {name}, isso é um teste!"
```

### Opções Adicionais:
*   `--phone-col`: Nome da coluna de telefone no CSV (padrão: `phone`).
*   `--name-col`: Nome da coluna de nome no CSV (padrão: `name`).
*   `--batch-size`: Quantidade de mensagens enviadas antes de uma pausa longa (padrão: 50).
*   `--batch-pause`: Tempo de pausa em segundos entre os lotes (padrão: 60).

### Exemplo de Envio Seguro (Lotes):
Para enviar para 300 pessoas em 2 lotes de 150, com uma pausa de 10 minutos (600 segundos) entre eles:
```bash
python main.py --csv contatos.csv --message-file mensagem.txt --batch-size 150 --batch-pause 600
```

## ⚠️ Avisos Importantes

1.  **Risco de Bloqueio:** O WhatsApp pode banir números que enviam muitas mensagens rapidamente para pessoas que não têm o contato salvo. Use com moderação.
2.  **QR Code:** Ao iniciar, o navegador abrirá e você precisará escanear o QR Code do WhatsApp Web.
3.  **Atualização de Lista:** O script gera um relatório de envio e **remove** do arquivo CSV original os contatos que receberam a mensagem com sucesso. Isso permite parar e continuar o envio depois sem duplicar. **Faça um backup da sua lista antes!**

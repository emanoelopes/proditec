import pyautogui
import os
from dotenv import load_dotenv
from buscar_imagem import clica_na_imagem
from time import sleep
from presencialidade import acessar_site

load_dotenv()

SENHA_AVAMEC = os.getenv('AVAMEC_PASSWORD')
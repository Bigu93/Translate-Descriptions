import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("O_SECRET")
ALLOWED_IPs = os.getenv("IPs")
VALID_API_KEY = os.getenv("API_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
ROUTES_WITHOUT_API_KEY = ["/", "/product-data"]
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
CLIENT_USERNAME = os.getenv("IDOSELL_CLIENT_USERNAME")
CLIENT_SECRET = os.getenv("IDOSELL_CLIENT_SECRET")
BASE_URL = os.getenv("IDOSELL_BASE_URL")
TRANSLATE_PRODUCT_NAME = """Act like a language translator. I will give you product name and desired lang for translating. Keep the word seqeuence in place. Don't add any special signs like commas, hyphens or similar to the response. I will give you some examples in Polish. In given examples, the "Suzy", "Carrie", "KK174215", "LL274A177", "MR870-49" are special names. If the sentence has special name, keep it at the end of sentence, but if it's from Big Star company or different, put it before the last one. Examples in Polish:
###
Klapki Z Kokardą I Ozdobnym Misiem Fuksja Suzy, Damskie Lakierowane Sandały Na Słupku Maciejka Czarne Carrie,Męskie Buty Trekkingowe Big Star KK174215 Czarne, Damskie Tenisówki Na Platformie Big Star LL274A177 Białe, Lakierowane Botki Na Obcasie S.Barski MR870-49 Jasnoszare
###
Return just the translated text in JSON following format:{"Czech":"Sample text"}"""

TRANSLATE_PRODUCT_DESC = """Act like a language translator. I will give you product descriptions for translating. Important thing is to remove all HTML tags. You will get langs list for all translations. Return just the translated text in following JSON format: {"Sample lang":"Sample text","Sample lang":"Sample text",}"""

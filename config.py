import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("O_SECRET")
OPENAI_MODEL = os.getenv("MODEL")

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

CLIENT_USERNAME = os.getenv("IDOSELL_CLIENT_USERNAME")
CLIENT_SECRET = os.getenv("IDOSELL_CLIENT_SECRET")
BASE_URL = os.getenv("IDOSELL_BASE_URL")
API_VERSION = os.getenv("API_VERSION")

VIES_WSDL = os.getenv("VIES")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")

PROMPT_PRODUCT_NAME = """You are a language translator. Translate the provided product name into the specified languages, maintaining the word sequence as originally presented. Follow these instructions carefully:\n1. Do not introduce any special characters (e.g., commas, hyphens) into the translated text.\n2. If the product name contains a special name (e.g., \"Suzy\", \"Carrie\", \"KK174215\", \"LL274A177\", \"MR870-49\"), place it at the end of the sentence.\n3. If the product is associated with the Big Star brand or a similar brand, position the special name before the last term.\n4. Provide the translations in a JSON object format, with each key being the target language and the corresponding value being the translated text.\n\nInput Examples in Polish for translation:\n\"[Klapki Z Kokardą I Ozdobnym Misiem Fuksja Suzy] Langs:[\"Czech\"]\",\n\"[Damskie Lakierowane Sandały Na Słupku Maciejka Czarne Carrie] Langs:[\"English\", \"Czech\", \"Slovak\"]\",\n\"[Męskie Buty Trekkingowe Big Star KK174215 Czarne] Langs:[\"Slovak\"]\",\n\"[Damskie Tenisówki Na Platformie Big Star LL274A177 Białe] Langs:[\"Romanian\", \"Czech\"]\",\n\"[Lakierowane Botki Na Obcasie S.Barski MR870-49 Jasnoszare] Langs:[\"Italian\", \"Czech\"]\"\n\nTranslate the text provided by the user into the specified languages and format the response as a JSON object, where the key is the name of the target language (e.g., \"Czech\") and the value is the translated text. Do not include any additional commentary or formatting in your response.\n\nExample Output:\n{\n  \"German\": \"Translated text in German\",\n  \"Bulgarian\": \"Translated text in Bulgarian\"\n}\nReplace \"German\" and \"Bulgarian\" with the actual target language names and the translated text accordingly."""

PROMPT_PRODUCT_DESC = """You are a language translator. Translate the provided product description into the specified languages while preserving all HTML tags. Follow these instructions carefully:\n1. Preserve all HTML tags exactly as they are.\n2. Translate only the text content within the HTML tags into the target languages.\n3. Completely omit any content related to the size chart (including instructions to refer to it and the size chart itself).\n4. Provide the translations in a JSON object format, with each key being the target language and the corresponding value being the translated text.\n5. Do not add any punctuation such as commas or semicolons at the end of the JSON object.\n\nExample Output:\n{\n  \"German\": \"Translated text in German\",\n  \"Bulgarian\": \"Translated text in Bulgarian\"\n}\nReplace \"German\" and \"Bulgarian\" with the actual target language names and the translated text accordingly."""

PROMPT_META_TITLE = """You are a language translator and SEO expert. Your task is to create a concise, engaging meta title in specified languages from a detailed Polish product name and category. The meta title should capture the essence of the product and entice potential customers. Follow these instructions carefully:\n1. Translate the main elements of the Polish product name and category name into the specified languages, ensuring accuracy and natural language use.\n2. Identify the most compelling features, benefits, and unique selling points of the product from the translated name.\n3. Craft a concise, engaging meta title that incorporates the translated category name as a primary keyword. The meta title should not exceed 60 characters to ensure it is fully displayed in search engine results.\n4. Review the meta title for SEO optimization, making sure it includes relevant keywords naturally and is appealing to both search engines and potential customers.\n\nExpected Output Format:\n{\n  \"Language1\": \"MetaTitle1\",\n  \"Language2\": \"MetaTitle2\"\n}\nReplace \"Language1\", \"Language2\", etc., with the actual languages identified from user input. Replace \"MetaTitle1\", \"MetaTitle2\", etc., with the actual created content."""

PROMPT_META_DESC = """You are a language translator and SEO expert. Your task is to create a concise, engaging meta description in specified languages from a detailed Polish product description and category. The meta description should capture the essence of the product, be optimized for search engines, and attract potential customers. Follow these instructions carefully:\n1. Translate the main elements of the Polish product description and category name into the specified languages, ensuring accuracy and natural language use.\n2. Identify the most compelling features, benefits, and unique selling points of the product based on the translated description.\n3. Ignore all information about size charts and selection advice.\n4. Craft a concise, engaging meta description that incorporates the translated category name as a part of the main sentence of the description. The meta description should not exceed 140 characters to ensure it is fully displayed in search engine results.\n5. Ensure the meta description is appealing and informative, effectively summarizing the product’s appeal to entice potential customers. Avoid using any technical jargon or abbreviations that the average customer might not understand.\n6. Review the meta description for SEO optimization, making sure it includes relevant keywords naturally and reads well to both search engines and potential customers.\n\nExpected Output Format:\n{\n  \"Language1\": \"MetaDescription1\",\n  \"Language2\": \"MetaDescription2\"\n}\nReplace \"Language1\", \"Language2\", etc., with the actual languages identified from user input. Replace \"MetaDescription1\", \"MetaDescription2\", etc., with the actual created content."""

PROMPT_KEYWORDS = """You are a language translator and SEO expert. Your task is to generate a translated list of 6 relevant keywords for specified languages from a Polish product description and category. The keywords should summarize the primary features and attributes of the product. Follow these instructions carefully:\n1. Carefully read the provided Polish description and category name to identify key aspects and characteristics of the product, excluding any sections that discuss size charts or sizing instructions.\n2. Translate the main body of the description (ignoring sizes and selection advice) into the specified languages, and from that translation, extract 6 keywords for each language that reflect the most important elements such as material and composition, design and style features, and functionality and comfort considerations.\n3. Ensure the category name is translated and included as a primary keyword.\n4. Present the keywords for each language in a JSON format, ensuring they are concise and to the point.\n\nExpected Output Format:\n{\n  \"Language1\": \"keyword1 keyword2 keyword3 keyword4 keyword5 keyword6\",\n  \"Language2\": \"keyword1 keyword2 keyword3 keyword4 keyword5 keyword6\"\n}\nReplace \"keyword1\", \"keyword2\", etc., with the actual keywords identified from the description. Replace \"Language1\", \"Language2\", etc., with the actual languages identified from user input."""

PROMPT_GENERATE = """Na podstawie przesłanego zdjęcia lub kilku zdjęć, wygeneruj opis produktu dla sklepu internetowego. Skup się tylko na produkcie, nie opisuj dodatkowych akcesoriów, które ma modelka. Poniżej kilka przykładowych opisów:###
Opis 1: 
Półbuty damskie marki Vinceza to połączenie elegancji i wygody. Wykonane ze skóry naturalnej, zapewniają trwałość i komfort noszenia. Słupkowy obcas zapewnia stabilność podczas chodzenia. Sznurowanie pozwala na idealne dopasowanie do stopy. Te półbuty są doskonałym wyborem na wiele okazji, dodając Twojej stylizacji wyrafinowanego charakteru.
Opis 2:
Damskie trampki marki Big Star. Wykonane z wysokiej jakości materiału tekstylnego. Cholewka sięgająca za kostkę dodaje stabilności, co jest szczególnie ważne podczas długich spacerów czy aktywności na świeżym powietrzu. W tych modnych trampkach będziesz czuć się swobodnie i stylowo jednocześnie!
Opis 3:
Sandały płaskie damskie od marki Big Star to wyjątkowe połączenie stylu i wygody. Wykonane z wysokiej jakości eko skóry, są nie tylko trwałe, ale także przyjazne dla środowiska. Przeplatające się paseczki dodają subtelnego uroku i sprawiają, że prezentują się niezwykle stylowo. Doskonale sprawdzą się w letnich stylizacjach, dodając im lekkości i swobodnego charakteru. Idealne zarówno na spacer po plaży, jak i na relaksujące spacery po mieście.
Opis 4:
Kapcie damskie osadzone na grubej podeszwie zapewniają stabilność i wygodę podczas poruszania się po domu. Miękkie futerko sprawia, że stopy są otulone. Te kapcie są nie tylko praktyczne, ale także stylowe, doskonale komponując się z domowymi strojami. Idealne na wieczorne leniuchowanie lub przytulny wieczór przy kominku.
###
Zwróć tylko opis, nic więcej.
"""

PROMPT_REPHRASE = """
Na podstawie podanego opisu przeformułuj go. Pozostaw znaczniki HTML bez zmian. Nie zmieniaj ani nie modyfikuj części którego zawierają treść o wyborze rozmiaru na podstawie tabeli rozmiarów i samej tabeli rozmiarów. Nie zmieniaj pierwotnego znaczenia/przeznaczenia tekstu.

{additional_instructions}

Zwróć tylko opis, nic więcej.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("O_SECRET")

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

CLIENT_USERNAME = os.getenv("IDOSELL_CLIENT_USERNAME")
CLIENT_SECRET = os.getenv("IDOSELL_CLIENT_SECRET")
BASE_URL = os.getenv("IDOSELL_BASE_URL")

VIES_WSDL = os.getenv("VIES")

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")

PROMPT_PRODUCT_NAME = """Translate the following product name into the specified languages, maintaining the word sequence as originally presented. Do not introduce any special characters (e.g., commas, hyphens) into the translated text. If a sentence contains a special name (e.g., "Suzy", "Carrie", "KK174215", "LL274A177", "MR870-49"), it should be placed at the end of the sentence. However, if the product is associated with the Big Star brand or similar, position the special name before the last term. Below are input examples in Polish for translation:
###
"[Klapki Z Kokardą I Ozdobnym Misiem Fuksja Suzy] Lang:["Czech"]", 
"[Damskie Lakierowane Sandały Na Słupku Maciejka Czarne Carrie] Lang:["English", "Czech", "Slovak"]",
"[Męskie Buty Trekkingowe Big Star KK174215 Czarne]" Lang:["Slovak"], 
"[Damskie Tenisówki Na Platformie Big Star LL274A177 Białe] Lang:["Romanian", "Czech"]", 
"[Lakierowane Botki Na Obcasie S.Barski MR870-49 Jasnoszare] Lang:["Italian", "Czech"]"
###
Translate text provided by the user into the specified languages and format the response as a JSON object, where the key is the name of the target language (e.g., "Czech") and the value is the translated text. Do not include any additional commentary or formatting in your response. Below is an example output:
{"Czech":"Sample text"}"""

PROMPT_PRODUCT_DESC = """As a language translator, translate the provided product description into the specified languages. Prioritize leaving all HTML tags as it is and do not translate them. You will be given a list of target languages for which translations are needed. Present the translated texts in a JSON object format, adhering to the following guidelines:
1.  Ensure all HTML tags are leave as it be.
2. Translate the cleaned text into each of the specified languages.
3. Format the response as a JSON object, with each key being the target language (as provided in the list) and the corresponding value being the translated text in that language. Do not include any extra punctuation, such as commas or semicolons, at the end of the JSON object.
4. Ignore and remove information about checking size with size chart and size chart itself.
Expected Output Format:
{
  "Language 1": "Translated text for Language 1",
  "Language 2": "Translated text for Language 2"
}
Please replace "Language 1" and "Language 2" with the actual names of the target languages and "Translated text for Language 1" and "Translated text for Language 2" with your translations."""

PROMPT_META_TITLE = """Given a detailed product name and category in Polish that outlines key features, benefits, and unique selling points of the product, create a concise, engaging meta title in specified languages that captures the essence of the product and entices potential customers. The title should be optimized for search engines, being succinct yet descriptive, and should contain max 60 characters to ensure it is fully displayed in search engine results. The category name should be included in the translated meta title as a primary keyword, emphasizing the product's most distinctive attributes. The goal is to make the meta title appealing and informative, drawing potential customers' attention in search engine results.
Instructions:
1. Translate the main elements of the Polish product name and category name into specified languages, ensuring accuracy and natural language use.
2. From the translated name, identify the most compelling features, benefits, and unique selling points of the product.
3. Craft a concise, engaging meta title that incorporates the translated category name as a primary keyword. The meta title should not exceed 60 characters to ensure it is fully displayed in search engine results.
4. Review the meta title for SEO optimization, making sure it includes relevant keywords naturally and is appealing to both search engines and potential customers.
Expected Output Format:
{
"Language1": "MetaTitle1",
"Language2": "MetaTitle2",
}
Replace "Language1", "Language2", etc., with the actual languages identified from user input.
Replace "MetaTitle1", "MetaTitle2", etc., with the actual created content."""
PROMPT_META_DESC = """Given a detailed product description and category in Polish that outlines key features, benefits, and unique selling points of the product, create a concise, engaging meta description in specified languages that captures the essence of the product. The description should be optimized for search engines and designed to attract potential customers. It should contain max 140 characters. The category name should be included in the translated meta description as a part of main sentence. Focus on highlighting the product's most distinctive attributes, ensuring the meta description is appealing and informative.
Instructions:
1. Translate the main elements of the Polish product description and category name into specified languages, ensuring accuracy and natural language use.
2. Identify the most compelling features, benefits, and unique selling points of the product based on the translated description.
3. Ignore all information about size charts and selection advice!
4. Craft a concise, engaging meta description that incorporates the translated category name as a part of main sentence of description. The meta description should not exceed 140 characters to ensure it is fully displayed in search engine results.
5. Ensure the meta description is appealing and informative, effectively summarizing the product’s appeal to entice potential customers. Avoid using any technical jargon or abbreviations that the average customer might not understand.
6. Review the meta description for SEO optimization, making sure it includes relevant keywords naturally and reads well to both search engines and potential customers.
Expected Output Format:
{
"Language1": "MetaDescription1",
"Language2": "MetaDescription2",
}
Replace "Language1", "Language2", etc., with the actual languages identified from user input.
Replace "MetaDescription1", "MetaDescription2", etc., with the actual the created content. """
PROMPT_KEYWORDS = """Given a product description and category in polish language that includes various details about the item, generate a translated list of 6 relevant keywords for specified language list that summarize the primary features and attributes of the product. The category name should be translated and included as a primary keyword. Exclude any reference to size charts or specific sizing instructions, focusing instead on the material, design, and functional aspects of the product described.
Instructions:
1. Carefully read the provided Polish description and category name to identify key aspects and characteristics of the product, excluding any sections that discuss size charts or sizing instructions.
2. Translate the main body of the description (ignoring sizes and selection advice!) into specified languages, and from that translation, extract 6 keywords for each language that reflect the most important elements such as material and composition, design and style features, and functionality and comfort considerations.
3. Present the keywords for each language in a JSON format, ensuring they are concise and to the point.
Expected Output Format:
{
"Language1": "keyword1 keyword2 keyword3 keyword4 keyword5 keyword6",
"Language2": "keyword1 keyword2 keyword3 keyword4 keyword5 keyword6",
}
Replace "keyword1", "keyword2", etc., with the actual keywords identified from the description. Replace "Language1", "Language2", etc., with the actual languages identified from user input."""

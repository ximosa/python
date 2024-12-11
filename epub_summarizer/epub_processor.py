from ebooklib import epub
from transformers import pipeline
import nltk
import re
import torch

def limpiar_texto(texto):
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\[.*?\]', '', texto)
    return texto.strip()

def procesar_epub(ruta_epub, ruta_salida):
    # Configurar dispositivo
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Cargar el libro
    libro = epub.read_epub(ruta_epub)
    contenido = []

    # Extraer contenido
    for item in libro.get_items():
        if isinstance(item, epub.EpubHtml):
            contenido.append(item.get_content().decode('utf-8'))

    # Procesar y limpiar el texto
    texto_completo = ' '.join(contenido)
    texto_limpio = limpiar_texto(texto_completo)

    # Dividir el texto en chunks más pequeños
    chunks = [texto_limpio[i:i+1000] for i in range(0, len(texto_limpio), 1000)]

    # Generar resumen
    resumidor = pipeline("summarization", model="facebook/bart-large-cnn", device=device)
    resumenes = []

    for chunk in chunks[:5]:  # Procesar los primeros 5 chunks para un resumen general
        if len(chunk) > 100:  # Asegurar que el chunk tiene suficiente contenido
            resumen = resumidor(chunk, max_length=150, min_length=50)
            resumenes.append(resumen[0]['summary_text'])

    # Guardar resultado
    resumen_final = ' '.join(resumenes)
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(resumen_final)

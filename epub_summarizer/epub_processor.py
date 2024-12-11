from ebooklib import epub
from transformers import pipeline
import nltk
import re
import torch
from bs4 import BeautifulSoup

def limpiar_texto(texto):
    # Eliminar HTML
    soup = BeautifulSoup(texto, 'html.parser')
    texto = soup.get_text()
    # Limpiar espacios y caracteres especiales
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\[.*?\]', '', texto)
    return texto.strip()

def procesar_epub(ruta_epub, ruta_salida):
    print("Iniciando procesamiento...")
    
    # Cargar el libro
    libro = epub.read_epub(ruta_epub)
    contenido = []
    
    print("Extrayendo contenido...")
    for item in libro.get_items():
        if isinstance(item, epub.EpubHtml):
            contenido.append(item.get_content().decode('utf-8'))

    # Procesar texto
    texto_completo = ' '.join(contenido)
    texto_limpio = limpiar_texto(texto_completo)
    
    print("Generando resumen...")
    resumidor = pipeline(
        "summarization",
        model="facebook/bart-large-cnn",
        device="cpu"
    )
    
    # Ajuste dinámico del tamaño del resumen
    longitud_chunk = 1024
    chunks = [texto_limpio[i:i+longitud_chunk] 
             for i in range(0, len(texto_limpio), longitud_chunk)]
    
    resumenes = []
    for i, chunk in enumerate(chunks[:3]):
        print(f"Procesando chunk {i+1}...")
        if len(chunk) > 100:
            max_length = min(500, len(chunk) // 2)
            min_length = max(30, max_length // 4)
            resumen = resumidor(chunk, max_length=max_length, min_length=min_length)
            resumenes.append(resumen[0]['summary_text'])
    
    # Guardar resultado
    resumen_final = ' '.join(resumenes)
    print("Guardando resultado...")
    with open(ruta_salida, 'w', encoding='utf-8') as f:
        f.write(resumen_final)
    
    print("¡Procesamiento completado!")

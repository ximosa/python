import moviepy.config as conf
conf.IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

from PIL import Image
Image.ANTIALIAS = Image.Resampling.LANCZOS

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_credentials.json"

from google.cloud import texttospeech
from moviepy.editor import AudioFileClip, TextClip, VideoFileClip, CompositeVideoClip, concatenate_videoclips
import glob
import random

def crear_video(texto, carpeta_videos, nombre_salida="video_final.mp4", duracion_clip=15):
    print(f"Nombre del archivo de salida: {nombre_salida}")  # Línea de debug
    print("1. Iniciando proceso...")
    
    # Dar formato al texto
    texto = texto.replace('?', '?\n')
    texto = texto.replace('!', '!\n')
    
    print("2. Generando audio...")
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=texto)

    voice = texttospeech.VoiceSelectionParams(
        language_code="es-ES",
        name="es-ES-Standard-A",
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=0.9,
        pitch=0
    )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    with open("audio_temp.mp3", "wb") as out:
        out.write(response.audio_content)

    print("3. Cargando audio...")
    audio = AudioFileClip("audio_temp.mp3")
    duracion_total = audio.duration

    print("4. Buscando videos...")
    videos = glob.glob(os.path.join(carpeta_videos, "*.mp4"))
    if not videos:
        raise Exception("No se encontraron videos MP4 en la carpeta")
    print(f"   Encontrados {len(videos)} videos")

    # Dividir el texto en frases y calcular tiempos
    frases = [f.strip() for f in texto.split('.') if f.strip()]
    tiempo_por_frase = duracion_total / len(frases)
    print(f"   Tiempo promedio por frase: {tiempo_por_frase:.2f} segundos")

    clips = []
    tiempo_actual = 0

    print("5. Procesando videos...")
    while tiempo_actual < duracion_total:
        video_path = random.choice(videos)
        print(f"   Procesando video: {os.path.basename(video_path)}")
        
        video_clip = VideoFileClip(video_path)
        duracion = min(duracion_clip, duracion_total - tiempo_actual)
        
        # Verificar duración del video
        if video_clip.duration < duracion:
            duracion = video_clip.duration
            video_clip = video_clip.subclip(0, duracion)
        else:
            start = random.uniform(0, video_clip.duration - duracion)
            video_clip = video_clip.subclip(start, start + duracion)
        
        # Redimensionar video
        w, h = video_clip.size
        new_h = int(h * 1280 / w)
        video_clip = video_clip.resize((1280, new_h))
        
        # Obtener frase actual según el tiempo
        indice_frase = int(tiempo_actual / tiempo_por_frase)
        frase_actual = frases[min(indice_frase, len(frases)-1)]
        print(f"   Subtítulo actual: {frase_actual[:50]}...")
        
        # Crear subtítulos
        texto_clip = TextClip(frase_actual,
                            fontsize=30,
                            color='white',
                            bg_color='rgba(0,0,0,0.5)',
                            size=(1200, None),
                            method='caption',
                            align='center',
                            font='Arial')
        
        texto_clip = texto_clip.set_duration(duracion)
        texto_clip = texto_clip.set_position(('center', 0.8), relative=True)

        # Combinar video y texto
        clip_compuesto = CompositeVideoClip([video_clip, texto_clip])
        clips.append(clip_compuesto)

        tiempo_actual += duracion
        video_clip.close()
        print(f"   Progreso: {(tiempo_actual/duracion_total)*100:.1f}%")

    print("6. Uniendo clips...")
    video_final = concatenate_videoclips(clips)
    video_final = video_final.set_audio(audio)

    print("7. Guardando video final...")
    video_final.write_videofile(nombre_salida,
                              fps=30,
                              codec='libx264',
                              audio_codec='aac',
                              threads=4)

    print("8. Limpiando...")
    os.remove("audio_temp.mp3")
    
    print("¡Video completado!")

# Ejemplo de uso
texto_prueba = """Respirar, ese acto que realizamos millones de veces a lo largo de nuestra vida, es mucho más que un simple intercambio de gases."""

crear_video(
    texto=texto_prueba,
    carpeta_videos="./imagenes",
    nombre_salida="Sistema respiratorio.mp4",
    duracion_clip=15
)

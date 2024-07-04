"""
Video Editor

Questo script fornisce funzionalità per l'editing di video, inclusi il montaggio audio,
l'estrazione di intervalli specifici e l'ottenimento della lunghezza del video.

Il script utilizza la libreria moviepy per la manipolazione dei video e implementa
un sistema di logging per registrare le operazioni e gli errori.

Funzionalità principali:
- Montaggio di un nuovo audio su un video esistente
- Estrazione di intervalli specifici da un video
- Ottenimento della lunghezza totale di un video

Utilizzo:
    python video_editor.py [-h] (-a VIDEO_INPUT AUDIO_INPUT | -e VIDEO_INPUT INTERVALS | -l VIDEO_INPUT)

Esempi:
    python video_editor.py -a input_video.mp4 new_audio.mp3
    python video_editor.py -e input_video.mp4 "1:30-2:45,3:15-4:00"
    python video_editor.py -l input_video.mp4

Note:
    Tutte le operazioni e gli errori vengono registrati nel file 'log.txt'.
"""

import argparse
import os
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Configurazione del logging
logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_time(time_str):
    """
    Converte una stringa di tempo in secondi.

    Accetta formati MM:SS o HH:MM:SS.

    :param time_str: Stringa rappresentante il tempo
    :type time_str: str
    :return: Tempo in secondi
    :rtype: int
    :raises ValueError: Se il formato del tempo non è valido
    """
    try:
        parts = time_str.split(':')
        if len(parts) == 2:
            minutes, seconds = map(int, parts)
        elif len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            minutes += hours * 60
        else:
            raise ValueError("Formato tempo non valido. Usa MM:SS o HH:MM:SS")
        return minutes * 60 + seconds
    except ValueError as e:
        logging.error(f"Errore nel parsing del tempo: {str(e)}")
        raise

def parse_intervals(intervals_str):
    """
    Analizza una stringa di intervalli e la converte in una lista di tuple (inizio, fine).

    Accetta intervalli nel formato "1:30-2:45,3:15-4:00" o "1:30,2:45,3:15,4:00".

    :param intervals_str: Stringa rappresentante gli intervalli
    :type intervals_str: str
    :return: Lista di tuple (inizio, fine) in secondi
    :rtype: list of tuple
    :raises ValueError: Se il formato degli intervalli non è valido
    """
    try:
        intervals = []
        for interval in intervals_str.split(','):
            if '-' in interval:
                start, end = map(parse_time, interval.split('-'))
            else:
                start = parse_time(interval)
                end = start + 60  # Se non è specificato un intervallo, prendi 60 secondi
            intervals.append((start, end))
        return intervals
    except Exception as e:
        logging.error(f"Errore nel parsing degli intervalli: {str(e)}")
        raise

def montaggio_audio(video_input, audio_input):
    """
    Sostituisce l'audio di un video con un nuovo file audio.

    :param video_input: Percorso del file video di input
    :type video_input: str
    :param audio_input: Percorso del file audio di input
    :type audio_input: str
    :raises Exception: Se si verifica un errore durante il montaggio audio
    """
    try:
        video = VideoFileClip(video_input)
        audio = VideoFileClip(audio_input).audio

        if audio.duration > video.duration:
            audio = audio.subclip(0, video.duration)

        final_video = video.set_audio(audio)
        output_filename = os.path.splitext(os.path.basename(video_input))[0] + '_montato.mp4'
        final_video.write_videofile(output_filename)

        video.close()
        audio.close()
        logging.info(f"Montaggio audio completato: {output_filename}")
    except Exception as e:
        logging.error(f"Errore durante il montaggio audio: {str(e)}")
        raise

def estrai_intervalli(video_input, intervals):
    """
    Estrae intervalli specifici da un video e li concatena in un nuovo video.

    :param video_input: Percorso del file video di input
    :type video_input: str
    :param intervals: Lista di tuple (inizio, fine) rappresentanti gli intervalli da estrarre
    :type intervals: list of tuple
    :raises Exception: Se si verifica un errore durante l'estrazione degli intervalli
    """
    try:
        video = VideoFileClip(video_input)
        clips = []
        for start, end in intervals:
            clip = video.subclip(start, end)
            clips.append(clip)
        
        final_video = concatenate_videoclips(clips)

        output_filename = os.path.splitext(os.path.basename(video_input))[0] + '_estratto.mp4'
        final_video.write_videofile(output_filename)

        video.close()
        for clip in clips:
            clip.close()
        logging.info(f"Estrazione intervalli completata: {output_filename}")
    except Exception as e:
        logging.error(f"Errore durante l'estrazione degli intervalli: {str(e)}")
        raise

def get_video_length(video_input):
    """
    Ottiene la lunghezza di un video in minuti e secondi.

    :param video_input: Percorso del file video di input
    :type video_input: str
    :return: Tuple contenente minuti e secondi
    :rtype: tuple
    :raises Exception: Se si verifica un errore nell'ottenere la lunghezza del video
    """
    try:
        video = VideoFileClip(video_input)
        duration = video.duration
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        video.close()
        logging.info(f"Lunghezza video ottenuta: {minutes} minuti e {seconds} secondi")
        return minutes, seconds
    except Exception as e:
        logging.error(f"Errore nell'ottenere la lunghezza del video: {str(e)}")
        raise

def main():
    """
    Funzione principale che gestisce l'interfaccia a riga di comando e esegue le operazioni richieste.

    Utilizza argparse per analizzare gli argomenti della riga di comando e chiamare le funzioni appropriate.
    Gestisce anche le eccezioni e registra gli errori nel file di log.
    """
    parser = argparse.ArgumentParser(description='Elabora video: monta audio, estrai intervalli o ottieni lunghezza.')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-a', '--audio', nargs=2, metavar=('VIDEO_INPUT', 'AUDIO_INPUT'),
                       help='Monta un audio su un video. Richiede il path del video e il path dell\'audio.')
    group.add_argument('-e', '--extract', nargs=2, metavar=('VIDEO_INPUT', 'INTERVALS'),
                       help='Estrai intervalli da un video. Richiede il path del video e gli intervalli '
                            'nel formato "1:35-3:00,4:20-12:24,..." o "1:35,3:00,4:20,..."')
    group.add_argument('-l', '--length', metavar='VIDEO_INPUT',
                       help='Ottieni la lunghezza del video. Richiede il path del video.')

    args = parser.parse_args()

    try:
        if args.audio:
            logging.info(f"Avvio montaggio audio: {args.audio[0]}, {args.audio[1]}")
            montaggio_audio(args.audio[0], args.audio[1])
        elif args.extract:
            logging.info(f"Avvio estrazione intervalli: {args.extract[0]}, {args.extract[1]}")
            intervals = parse_intervals(args.extract[1])
            estrai_intervalli(args.extract[0], intervals)
        elif args.length:
            logging.info(f"Richiesta lunghezza video: {args.length}")
            minutes, seconds = get_video_length(args.length)
            print(f"La lunghezza del video è {minutes} minuti e {seconds} secondi.")
        logging.info("Operazione completata con successo")
    except Exception as e:
        logging.error(f"Si è verificato un errore durante l'esecuzione: {str(e)}")
        print(f"Si è verificato un errore. Controlla il file log.txt per i dettagli.")

if __name__ == "__main__":
    main()
import argparse
import os
import logging
from moviepy.editor import VideoFileClip, concatenate_videoclips

# Configurazione del logging
logging.basicConfig(filename='log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def parse_time(time_str):
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
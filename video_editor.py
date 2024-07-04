import argparse
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

def parse_time(time_str):
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes, seconds = map(int, parts)
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        minutes += hours * 60
    else:
        raise ValueError("Formato tempo non valido. Usa MM:SS o HH:MM:SS")
    return minutes * 60 + seconds

def parse_intervals(intervals_str):
    intervals = []
    for interval in intervals_str.split(','):
        if '-' in interval:
            start, end = map(parse_time, interval.split('-'))
        else:
            start = parse_time(interval)
            end = start + 60  # Se non è specificato un intervallo, prendi 60 secondi
        intervals.append((start, end))
    return intervals

def montaggio_audio(video_input, audio_input):
    video = VideoFileClip(video_input)
    audio = VideoFileClip(audio_input).audio

    if audio.duration > video.duration:
        audio = audio.subclip(0, video.duration)

    final_video = video.set_audio(audio)
    output_filename = os.path.splitext(os.path.basename(video_input))[0] + '_montato.mp4'
    final_video.write_videofile(output_filename)

    video.close()
    audio.close()

def estrai_intervalli(video_input, intervals):
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

def get_video_length(video_input):
    video = VideoFileClip(video_input)
    duration = video.duration
    minutes = int(duration // 60)
    seconds = int(duration % 60)
    video.close()
    return minutes, seconds

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

    if args.audio:
        montaggio_audio(args.audio[0], args.audio[1])
    elif args.extract:
        intervals = parse_intervals(args.extract[1])
        estrai_intervalli(args.extract[0], intervals)
    elif args.length:
        minutes, seconds = get_video_length(args.length)
        print(f"La lunghezza del video è {minutes} minuti e {seconds} secondi.")

if __name__ == "__main__":
    main()
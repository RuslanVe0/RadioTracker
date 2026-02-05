import time
import threading
import os
import RadioTracker
import utils.utils
import uuid

class constructor():
    """
        The purpose of this class is to store 4-unique data:
        current_song : the name of the current played song.
        current_artist: the name of the current played artist.
        
        start_time : the start time of the song.
        finished : whether the implementation has finished.
    """
    
    current_song: str = ""
    current_artist: str = ""
    
    start_time: str = utils.utils.get_current_time()
    finished: bool = False

def write_song(sample: bytes, _constructor: constructor):
    """
    The purpose of this method is to write locally the downloaded data from the given source (server destination).
    The data that is written is audio sample, not the full song. It is written in the 'audiosamples/' directory.
    After completion, the file is being converted to MP3, unlike the full audio song where the file remains ACC as
    a type.
    
    <h2>Required arguments:</h2>
        sample (bytes) - audio sample.
        _constructor (constructor) - data container for storing the current played song and the current artist. It is required
        in order the file to be saved succesfully under the current played song and the current artist.
    
    Returns:
        None.
    """
    path: str = f"audiosamples/{_constructor.current_artist.strip()}_{_constructor.current_song.strip()}_sample.acc"
    with open(path, "wb") as file:
        file.write(sample)
    file.close()
    utils.utils.convert_file_to_mp3(path)
    print("[+] Downloading completed!")
    
@utils.utils.threaded
def sample_audio(tracker: RadioTracker, _constructor) -> None:
    sample: bytes = tracker.audio_sample(_constructor)
    if not sample:
        return
    write_song(sample, _constructor)

@utils.utils.threaded
def full_audio(tracker: RadioTracker, _constructor) -> None:
    _constructor.finished = False
    tracker.music_stream(_constructor, open(f"music_downloader/{_constructor.current_artist}_{_constructor.current_song}_full_audio.acc", "wb"), f"music_downloader/{_constructor.current_artist}_{_constructor.current_song}_full_audio.acc", "RADIO_ENERGY")


def banner():
    print("""⠀⠀⠀⠀
                            ⢀⣴⠶⣶⡄⠀⠀⠀⠀
                        ⢀⣴⣧⠀⠸⣿⣀⣸⡇⠀⢨⡦⣄
                        ⠘⣿⣿⣄⠀⠈⠛⠉⠀⣠⣾⡿⠋
                        ⠀⠀⠈⠛⠿⠶⣶⡶⠿⠟⠉

  /$$$$$$   /$$$$$$  /$$$$$$$  /$$$$$$$$ /$$   /$$ /$$$$$$$  /$$$$$$$$
 /$$__  $$ /$$__  $$| $$__  $$|__  $$__/| $$  | $$| $$__  $$| $$_____/
| $$  \\__/| $$  \\ $$| $$  \\ $$   | $$   | $$  | $$| $$  \\s $$| $$      
| $$      | $$$$$$$$| $$$$$$$/   | $$   | $$  | $$| $$$$$$$/| $$$$$   
| $$      | $$__  $$| $$____/    | $$   | $$  | $$| $$__  $$| $$__/   
| $$    $$| $$  | $$| $$         | $$   | $$  | $$| $$  \\ $$| $$      
|  $$$$$$/| $$  | $$| $$         | $$   |  $$$$$$/| $$  | $$| $$$$$$$$
 \\______/ |__/  |__/|__/         |__/    \\______/ |__/  |__/|________/
                                                                      
                         Matthew 13:16:
    "But blessed are your eyes because they see, and your ears because they hear".                                       
                                                                      
""")

def capture(source: str = "radioenergy", download_music: bool = False):
    if source not in ["radioenergy"]:
        raise ValueError("Source has one of these (radioenergy,)")
    banner()
    recorded: list[list] = []
    radiotracker: RadioTracker = RadioTracker.RadioTracker(type_of = f"?radio={source}")
    _constructor: constructor = constructor()
    radiotracker.capture()
    _constructor.current_song = radiotracker.constructor.json_data["current_song"]
    _constructor.current_artist = radiotracker.constructor.json_data["current_artist"]
    print(f"Current artist: {_constructor.current_artist}\r\x0ACurrent song: ♪ {_constructor.current_song} ♪\r\x0AStart time: {_constructor.start_time}\r\x0ASource: {source}\r\x0A")
    recorded.append([_constructor.current_song, _constructor.current_artist, _constructor.start_time])
    if not download_music and download_music != "no_download":
        threading.Thread(target = sample_audio, args = (radiotracker, _constructor)).start()
        print("[*] Downloading sample...")
    elif download_music and download_music != "no_download":
        threading.Thread(target = full_audio, args = (radiotracker, _constructor)).start()
        print("[*] Downloading full audio...")
    try:        
        while True:
            radiotracker.capture()
            data: dict = radiotracker.constructor.json_data
            if data["current_artist"] != _constructor.current_artist and data["current_song"] != _constructor.current_song:
                os.system("cls"); banner()
                recorded.append([_constructor.current_song, _constructor.current_artist, _constructor.start_time])
                _constructor.current_song = data["current_song"]
                _constructor.current_artist = data["current_artist"]
                _constructor.start_time = utils.utils.get_current_time()
                print(f"Current artist: {_constructor.current_artist}\r\x0ACurrent song: ♪ {_constructor.current_song} ♪\r\x0AStart time: {_constructor.start_time}\r\x0ASource: {source}\r\x0A")
                if not download_music:
                    sample_audio(radiotracker, _constructor)
                    print("[*] Downloading sample...")
                else:
                    full_audio(radiotracker, _constructor)
                    print("[*] Downloading full audio...")
            if len(recorded) >= 1:
                with open("recorded.txt", "a", encoding = "utf-8", errors = "ignore") as file:
                    for current_song, current_artist, start_time in recorded:
                        file.write(f"Current song: {current_song}\nCurrent artist: {current_artist}\nStart time: {start_time}\nLocation: {f'audiosamples/{current_artist}_{current_song}_sample.acc'}\n\n")                    
                    file.close()
                    recorded = []
            time.sleep(20)
            
    except KeyboardInterrupt:
        _constructor.current_artist = ""
        _constructor.current_song = ""
        del _constructor
        exit("Exitting...")
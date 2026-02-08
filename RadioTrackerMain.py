import time
import threading
import os
import RadioTracker
import utils.utils
import uuid
import database_controller
import terminal as _terminal


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
    
    terminal: bool = False
    running: bool = True
    
_constructor: constructor = constructor()

def write_song(sample: bytes, _constructor: constructor, verbosity: bool):
    Controller: database_controller.Controller = database_controller.Controller()
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
    Controller.modify("song_location", path.replace(".acc", ".mp3"), _constructor.current_song)
    utils.utils.convert_file_to_mp3(path)
    if verbosity:
        print("[+] Downloading completed!")
    
@utils.utils.threaded
def sample_audio(tracker: RadioTracker, _constructor, verbosity: bool) -> None:
    sample: bytes = tracker.audio_sample(_constructor)
    if not sample:
        return
    write_song(sample, _constructor, verbosity)

@utils.utils.threaded
def full_audio(tracker: RadioTracker, _constructor, verbosity: bool) -> None:
    Controller: database_controller.Controller = database_controller.Controller()
    _constructor.finished = False
    location: str = f"music_downloader/{_constructor.current_artist}_{_constructor.current_song}_full_audio.acc"
    if verbosity:
        print("[+] Data uploaded in DB, modified time.")
    Controller.modify("song_location", location, _constructor.current_song)
    tracker.music_stream(_constructor, open(location, "wb"), f"music_downloader/{_constructor.current_artist}_{_constructor.current_song}_full_audio.acc", "RADIO_ENERGY", verbosity)

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

def db_controller(_constructor: constructor, source: str):
    Controller: database_controller.Controller = database_controller.Controller()
    if Controller.find("song", _constructor.current_song):
        Controller.modify("last_played", utils.utils.get_current_time(), _constructor.current_song)
    else:
        Controller.add_artist_song_new(_constructor.current_song, _constructor.current_artist, utils.utils.get_current_time(), utils.utils.get_current_time(),
        "/", source)

@utils.utils.threaded
def update_all():
    # updates per 5-seconds.
    db_controller: database_controller.Controller = database_controller.Controller()
    while True:
        if not _constructor.running:
            return
        for elements in db_controller.fetch_all():
            location, _time = elements[5], elements[8]
            total_time = utils.utils.calculate_length(utils.utils.read_file(location).length, 0.192)
            db_controller.modify("time", total_time, elements[1])
        time.sleep(5)
    

def capture(source: str = "radioenergy", download_music: bool = False, verbosity: bool = False, terminal: bool = False):
    if source not in ["radioenergy"]:
        raise ValueError("Source has one of these (radioenergy,)")
    banner()
    recorded: list[list] = []
    radiotracker: RadioTracker = RadioTracker.RadioTracker(type_of = f"?radio={source}")
    if terminal:
        _constructor.terminal = True
        threading.Thread(target = _terminal.terminal_init, args = (_constructor,), kwargs = None).start()
    radiotracker.capture()
    _constructor.current_song = radiotracker.constructor.json_data["current_song"]
    _constructor.current_artist = radiotracker.constructor.json_data["current_artist"]
    if not terminal:
        print(f"Current artist: {_constructor.current_artist}\r\x0ACurrent song: ♪ {_constructor.current_song} ♪\r\x0AStart time: {_constructor.start_time}\r\x0ASource: {source}\r\x0A")
    recorded.append([_constructor.current_song, _constructor.current_artist, _constructor.start_time])
    db_controller(_constructor, source)
    if not download_music and download_music != "no_download":
        threading.Thread(target = sample_audio, args = (radiotracker, _constructor, verbosity)).start()
        if verbosity:
            print("[*] Downloading sample...")
    elif download_music and download_music != "no_download":
        threading.Thread(target = full_audio, args = (radiotracker, _constructor, verbosity)).start()
        if verbosity:
            print("[*] Downloading full audio...")
    update_all()
    try:        
        while True:
            radiotracker.capture()
            data: dict = radiotracker.constructor.json_data
            if data["current_artist"] != _constructor.current_artist and data["current_song"] != _constructor.current_song:
                if not _constructor.terminal:
                    os.system("cls"); banner()
                recorded.append([_constructor.current_song, _constructor.current_artist, _constructor.start_time])
                _constructor.current_song = data["current_song"]
                _constructor.current_artist = data["current_artist"]
                _constructor.start_time = utils.utils.get_current_time()
                db_controller(_constructor, source)
                if not _constructor.terminal:
                    print(f"Current artist: {_constructor.current_artist}\r\x0ACurrent song: ♪ {_constructor.current_song} ♪\r\x0AStart time: {_constructor.start_time}\r\x0ASource: {source}\r\x0A")
                if not download_music:
                    sample_audio(radiotracker, _constructor, verbosity)
                    if not _constructor.terminal:
                        print("[*] Downloading sample...")
                else:
                    full_audio(radiotracker, _constructor, verbosity)
                    if not terminal:
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
        _constructor.running = False
        exit("Exitting...")
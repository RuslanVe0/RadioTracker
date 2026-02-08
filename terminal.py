import vlc
import os
import database_controller
import utils.utils
import time


class constructor():

    song_is_playing: bool = False
    player_module: vlc.MediaPlayer = None
    has_finished: bool = False
    

global_constr = constructor()


def current_artist(constructor, args):
    print(f"Current artist: {constructor.current_artist}")
    
def current_song(constructor, args):
    print(f"Current song: {constructor.current_song}")
    
def output_all(constructor, args):
    print(f"\r\x0ACurrent artist: {constructor.current_artist}\r\x0ACurrent song: {constructor.current_song}\r\x0ATime started: {constructor.start_time}\r\x0A")
    
    
def fetch_all(constructor, args):
    DBController: database_controller.Controller = database_controller.Controller()
    records: list = DBController.fetch_all()
    commands_compl: dict = {"sorted": False}
    if args:
        for elements in args.split(","):
            if elements.split("(")[0] in commands_compl:
                if len(elements.split("(")) > 1:
                    commands_compl[elements.split("(")[0]] = elements.split("(")[1].split(")")[0] == "True"
                else:
                    print("Incomplete command.")
            else:
                print(f"Unrecognized command. {elements.split("(")[0]}?")
    if commands_compl["sorted"]:
        records.sort(key = lambda x: x[1])
    header = (
        f"| {'ID':^4} | {'SONG':^20} | {'ARTIST':^20} | "
        f"{'DATE ADDED':^24} | {'LAST PLAYED':^23} | "
        f"{'LOCATION':^30} | {'SOURCE':^30} |"
        f"{'MINIHASH':^20} | {'TIME':^10} |"
    )
    separator = "-" * len(header)

    table = header + "\n" + separator
    for elements in records:
        index, song, artist, date_added, last_time_played, location, source, minihash, time = elements
        location = DBController.findr("mini_hash", minihash)[0][5]
        if not os.path.exists(location):
            print("Song not found.")
        else:
            table += (
            f"\n| {index:^4} | {song[:20]:<20} | {artist[:20]:<20} | "
            f"{date_added:^12} | {last_time_played:^15} | "
            f"{location[:27]+"...":<30} | {source[:11]:<30} |"
            f"{minihash:^20} | {time:^10} |"
        )

    print(table, end = "\n\n\n")
    
def clear_screen(constructor, args):
    os.system("cls")
    
def delete_all(constructor, args):
    DBController: database_controller = database_controller.Controller()
    DBController.delete_all()
    print("Successfully deleted all records.")


@utils.utils.threaded
def play_song(constructor, args):
    if global_constr.song_is_playing:
        print("Another song is currently playing.")
        return
    DBController: database_controller = database_controller.Controller()
    seconds: int = 0
    data = None
    if not args:
        print("No song has been specified.")
        return
    if "," in args:
        if len(args.split(",")) < 2:
            print("The format must be - song,seconds.")
            return
        try:
            seconds = int(args.split(",")[1])
        except ValueError:
            print("Expected an integer.")
        song = args.split(",")[0]
    else:
        song = args
    data = DBController.findr("mini_hash", song)
    if not data:
        print("Song not found.")
        return
    player = vlc.MediaPlayer(f"{os.getcwd() + "\\" + data[0][5]}")
    global_constr.player_module = player
    global_constr.song_is_playing = True
    event = player.event_manager()
    event.event_attach(
        vlc.EventType.MediaPlayerEndReached,
        on_stop
    )
    player.play()
    if seconds:
        counter: int = 0
        while counter < seconds:
            counter += 1
            time.sleep(1)
        stop_song(None, "")
        return

def on_stop(event):
    global_constr.song_is_playing = False
    global_constr.player_module.stop()
    global_constr.player_module = None

    
def stop_song(constructor, args):
    if global_constr.song_is_playing:
        global_constr.song_is_playing = None
        global_constr.player_module.stop()
    else:
        print("No song is currently played.")

def find_requested_minihash(constructor, args):
    DBController: database_controller.Controller = database_controller.Controller()
    if not args:
        print("No arguments specified. Mini_hash is required.")
        return
    mini_hash = args
    data = DBController.findr("mini_hash", mini_hash)
    if not data:
        print("No data has been found.")
        return
    data = data[0]
    total_time = utils.utils.calculate_length(utils.utils.read_file(data[5]).length, 0.192)
    datac: str = f"[{data[0]}]\r\x0AArtist: {data[1]}\r\x0ASong: {data[2]}\r\x0ADate added: {data[3]}\r\x0ALast-played: {data[4]}\r\x0A\r\x0ALocation: {data[5]}\r\x0ATime: {total_time}\r\x0A"
    print(datac)

@utils.utils.threaded
def count_time(seconds: int, mini_hash: str, song: str, artist: str, full: list) -> None:
    global_constr.has_finished = False
    counter: int = 0
    play_song(constructor, mini_hash)
    while counter != seconds:
        print(f"{artist} - {song}\r\x0AMore information: \r\x0A\
Date added: {full[3]}\r\x0ALast played: {full[4]}\r\x0ALocation: {full[5]}\r\x0AMini-hash: {mini_hash}\r\x0A\r\x0ACompleted: {(counter/seconds)*100}%/{100}% [{counter}/{seconds}]\r\x0A")
        counter += 1
        time.sleep(1)
        os.system("cls")
    if global_constr.song_is_playing:
        stop_song(None, "")
    global_constr.has_finished = True

def play_all(constructor, args):
    DBController: database_controller.Controller = database_controller.Controller()
    seconds: int = 5
    if args:
        try:
            seconds = int(args)
        except ValueError:
            print("Expected an integer.")
    global_constr.has_finished = False
    for elements in DBController.fetch_all():
        mini_hash = elements[7]
        count_time(seconds, mini_hash, elements[1], elements[2], elements)
        while not global_constr.has_finished:
            pass
    

commands: dict = {"current_artist": {"method": current_artist, "description": "Outputs the current played artist."}, 
                  "curr_artist": {"method": current_artist,
                                "description": "Outputs the current played artist."},
                  "current_song": {"method": current_song,
                                "description": "Outputs the current played song."}, "curr_song": {"method": current_song,
                                                                                                  "description": "Outputs the current played song."}, 
                "output_all": {"method": output_all, "description": "Outputs all elements."},
                "fetch_all": {"method": fetch_all, "description": "Fetches all records and outputs them, from the database."},
                "clear": {"method": clear_screen, "description": "Clears the screen."},
                "delete_all": {"method": delete_all, "description": "Deletes all records."},
                "play": {"method": play_song, "description": "Play a given downloaded song."},
                "stop": {"method": stop_song, "description": "Stop the song that is playing."},
                "find": {"method": find_requested_minihash, "description": "Outputs all information regarding the specified song. (Only mini_hash is accepted)."},
                "playall": {"method": play_all, "description": "Plays all songs sequentially, each song is partitioned per 5-seconds. You have control over time."}}



class Terminal(object):
    
    
    
    def __init__(self, constructor):
        self.constructor = constructor
    
    def __repr__(self):
        return f"<Terminal constructor={self.constructor}>"
    
    def init(self):
        try:
            while True:
                args = None
                command = input("#> ").strip()
                if command == "help" or command == "?":
                    tables: str = "\n\n"
                    count: int = 0
                    for elements in commands:
                        if count != 4:
                            tables += elements + " | "
                        else:
                            tables += elements + " |\n"
                            count = 0
                        count += 1
                    tables += "\n\n"
                    for elements in commands:
                        tables += f" * {elements} - " + commands[elements]["description"] + "\n"
                    print(tables)
                    continue
                elif "=" in command:
                    if len(command.split("=")) > 1:
                        command, args = command.split("=")
                    else:
                        print("Incomplete command.")
                elif command not in commands:
                    print("Command not found.")
                    continue
                commands[command]["method"].__call__(self.constructor, args)
                
        except EOFError:
            print("[-] Keyboard interrupt. Exitting.")
    
    
def terminal_init(constructor):
    terminal: Terminal = Terminal(constructor)
    terminal.init()
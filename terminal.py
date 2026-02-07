import vlc
import os
import database_controller
import utils.utils
import mutagen.mp3

class constructor():

    song_is_playing: bool = False
    player_module: vlc.MediaPlayer = None
    

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
        total_time = utils.utils.calculate_length(os.path.getsize(location), 0.192)
        table += (
            f"\n| {index:^4} | {song[:20]:<20} | {artist[:20]:<20} | "
            f"{date_added:^12} | {last_time_played:^15} | "
            f"{location[:27]+"...":<30} | {source[:11]:<30} |"
            f"{minihash:^20} | {total_time:^10} |"
        )

    print(table, end = "\n\n\n")
    
def clear_screen(constructor, args):
    os.system("cls")
    
def delete_all(constructor, args):
    DBController: database_controller = database_controller.Controller()
    DBController.delete_all()
    print("Successfully deleted all records.")

@utils.utils.threaded

@utils.utils.threaded
def play_song(constructor, args):
    if global_constr.song_is_playing:
        print("Another song is currently playing.")
        return
    DBController: database_controller = database_controller.Controller()
    if not args:
        print("No song has been specified.")
        return
    data = DBController.findr("mini_hash", args)
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
    

def on_stop(event):
    global_constr.song_is_play = False
    global_constr.player_module.stop()
    global_constr.player_module = None

    
def stop_song(constructor, args):
    if global_constr.song_is_playing:
        global_constr.song_is_playing = None
        global_constr.player_module.stop()
    else:
        print("No song is currently played.")
    

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
                "stop": {"method": stop_song, "description": "Stop the song that is playing."}}



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
                    print("\n\n".join(("  * " + elements + f"\n   - {commands[elements]["description"]}") for elements in commands))
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
import argparse
import RadioTrackerMain

class startProgram(object):
    
    
    def __init__(self):
        self.argparse = argparse.ArgumentParser(prog = "RadioTracker", usage = "This program is meant to view the current played song from a given radio source.")
        
    def add_arguments(self):
        self.argparse.add_argument("-m", "--music-downloader", required = False, default = False, help = "E.g --music-downloader", action = "store_true")
        self.argparse.add_argument("-s", "--source", required = False, default = "radioenergy", help = "E.g --source=radioenergy")
        self.argparse.add_argument("-n", "--no-download", required = False, default = False, help = "E.g --no-download (it is automatically flagged.)", action = "store_true")
        self.argparse.add_argument("-v", "--verbosity", required = False, default = False, help = "E.g --verbosity", action = "store_true")
        self.argparse.add_argument("-t", "--terminal", required = False, default = False, help = "E.g --terminal (it is automatically flagged.)", action = "store_true")

    def parse_args(self):
        return self.argparse.parse_args()

class Controller(object):
    
    
    def __init__(self):
        
        self.sp_argpa: startProgram = startProgram()
        self.sp_argpa.add_arguments()
    
    
    def finalize(self):
        parse_args = self.sp_argpa.parse_args()
        RadioTrackerMain.capture(parse_args.source, parse_args.music_downloader if not parse_args.no_download else "no_download", parse_args.verbosity, parse_args.terminal)

if __name__ == "__main__":
    Controller().finalize()
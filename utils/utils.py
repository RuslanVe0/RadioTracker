import datetime
import threading
import copy
import subprocess
import os


def get_current_time() -> str:
    dt_data: dict = {
        "months": {0: "Jan", 1: "Feb", 2: "Mar", 3: "Apr", 4: "May", 5: "Jun", 6: "Jul", 7: "Aug", 8: "Sep", 9: "Oct", 10: "Nov", 11: "Dec"},
        "week": {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    }
    dt_object: datetime = datetime.datetime.now()
    year, month, day, weekday, hour, minute, second = dt_object.year, dt_object.month,\
    dt_object.day, dt_object.weekday(), dt_object.hour, dt_object.minute, dt_object.second
    
    if day < 10:
        day = f"0{day}"
    
    if hour < 10:
        hour = f"0{hour}"
    
    if minute < 10:
        minute = f"0{minute}"
        
    if second < 10:
        second = f"0{second}"
    
    return f"{year} {dt_data["months"][month]} {day} {dt_data["week"][weekday]} {hour}:{minute}:{second}"

def threaded(function):
    
    def wrapper(*args, **kwargs):
        
        threading.Thread(target = function, args = args, kwargs = kwargs).start()
        
    return wrapper    


def convert_file_to_mp3(path: str) -> None:
    subprocess.run(["ffmpeg/ffmpeg.exe", "-y", "-i", path, path.replace(".acc", ".mp3")], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL, check = True)
    os.remove(path)
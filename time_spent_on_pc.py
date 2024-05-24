import time
import datetime
import json
import os
import pygame
import psutil
import pygetwindow as gw
from pynput import keyboard, mouse

# Fichier pour enregistrer les données d'activité
ACTIVITY_FILE = "activity_log.json"
INACTIVITY_THRESHOLD = 5  # secondes avant de considérer l'utilisateur comme inactif
WATCHED_PROCESSES = ["chrome.exe", "firefox.exe", "msedge.exe"]  # Navigateurs web

# Variable globale pour suivre le temps de démarrage et d'arrêt du programme
start_time = None
end_time = None

def load_activity_log():
    if os.path.exists(ACTIVITY_FILE):
        with open(ACTIVITY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_activity_log(activity_log):
    with open(ACTIVITY_FILE, "w") as f:
        json.dump(activity_log, f)

def get_current_day():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def log_activity(activity_log):
    current_day = get_current_day()
    if current_day not in activity_log:
        activity_log[current_day] = []

    activity_log[current_day].append({"start": datetime.datetime.now().isoformat()})

def end_activity(activity_log):
    current_day = get_current_day()
    if current_day in activity_log and activity_log[current_day]:
        last_activity = activity_log[current_day][-1]
        if "end" not in last_activity:
            end_time = time.time()
            start_time = datetime.datetime.fromisoformat(last_activity["start"])
            duration = (end_time - start_time.timestamp())

            if duration > INACTIVITY_THRESHOLD:
                adjusted_duration = duration - INACTIVITY_THRESHOLD
            else:
                adjusted_duration = 0

            last_activity["end"] = (start_time + datetime.timedelta(seconds=adjusted_duration)).isoformat()

def calculate_daily_usage(activity_log):
    usage_summary = {}
    for day, activities in activity_log.items():
        total_seconds = 0
        for activity in activities:
            start_time = datetime.datetime.fromisoformat(activity["start"])
            end_time = datetime.datetime.fromisoformat(activity.get("end", datetime.datetime.now().isoformat()))
            total_seconds += (end_time - start_time).total_seconds()
        usage_summary[day] = total_seconds / 3600  # Convert seconds to hours
    return usage_summary

def is_watched_process_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in WATCHED_PROCESSES:
            return True
    return False

def is_youtube_active():
    try:
        window = gw.getActiveWindow()
        return window and "YouTube" in window.title
    except:
        return False

pygame.init()
pygame.display.set_caption("Time Spent On PC")
clock = pygame.time.Clock()
screen_width, screen_height = 800, 160
screen = pygame.display.set_mode((screen_width, screen_height))
font_lilitaone_50 = pygame.font.Font("fonts/LilitaOne-Regular.ttf", 50)

def draw_text(texte, font, couleur, x, y):
    img = font.render(texte, True, couleur)
    text_width, text_height = font.size(texte)
    screen.blit(img, (x - text_width // 2, y - text_height // 2))

activity_log = load_activity_log()
last_activity_time = time.time()
activity_active = False

def on_activity():
    global last_activity_time, activity_active
    last_activity_time = time.time()
    if not activity_active:
        log_activity(activity_log)
        activity_active = True

keyboard_listener = keyboard.Listener(on_press=lambda _: on_activity())
mouse_listener = mouse.Listener(on_move=lambda *args: on_activity(), on_click=lambda *args: on_activity())

keyboard_listener.start()
mouse_listener.start()

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if time.time() - last_activity_time > INACTIVITY_THRESHOLD:
        if activity_active and not is_watched_process_running() and not is_youtube_active():
            end_activity(activity_log)
            activity_active = False
    else:
        if not activity_active:
            log_activity(activity_log)
            activity_active = True

    clock.tick(60)

    screen.fill((0, 0, 0))

    save_activity_log(activity_log)
    usage_summary = calculate_daily_usage(activity_log)
    
    for day, hours in usage_summary.items():
        hours_int = int(hours)
        minutes = (hours % 1) * 60
        minutes_int = int(minutes)
        seconds = (minutes % 1) * 60
        seconds_int = int(seconds)
        draw_text(f"{day}: {hours_int} h {minutes_int:02d} min {seconds_int:02d} sec", font_lilitaone_50, (255, 255, 255), 400, 80)

    pygame.display.update()

keyboard_listener.stop()
mouse_listener.stop()
pygame.quit()
save_activity_log(activity_log)

import time
import datetime
import json
import os
import pygame
import psutil
import pygetwindow as gw
from pynput import keyboard, mouse

stockage_file = "activity_log.json"
inactive_time = 5  # durée avant de considérer l'utilisateur comme inactif
naviguateurs = ["chrome.exe", "firefox.exe", "msedge.exe", "opera.exe", "operagx", "vivaldi.exe", "brave.exe"]
months = ["Jan", "Fev", "Mar", "Avr", "Mai", "Juin", "Jui", "Août", "Sept", "Oct", "Nov", "Dec"]
start_time = None

def load_logs():
    if os.path.exists(stockage_file) and os.path.getsize(stockage_file) > 0:
        try:
            with open(stockage_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Erreur de décodage JSON. Le fichier est corrompu. Dommage mdr")
    return {}

def save_logs(activity_log):
    with open(stockage_file, "w") as f:
        json.dump(activity_log, f, indent=4)

def get_date():
    jour_abrev = {
        "Monday": "Lun",
        "Tuesday": "Mar",
        "Wednesday": "Mer",
        "Thursday": "Jeu",
        "Friday": "Ven",
        "Saturday": "Sam",
        "Sunday": "Dim"
    }
    nom_jour = datetime.datetime.now().strftime("%A")
    return f"{jour_abrev[nom_jour]} {datetime.datetime.now().strftime('%d ')}" + months[datetime.datetime.now().month - 1]

def activity_logs(activity_log):
    global start_time
    current_day = get_date()
    if current_day not in activity_log:
        activity_log[current_day] = []
    if not start_time:
        start_time = datetime.datetime.now().isoformat()
        activity_log[current_day].append({"start": start_time})

def end_activity(activity_log):
    global start_time
    current_day = get_date()
    if start_time and current_day in activity_log and activity_log[current_day]:
        last_activity = activity_log[current_day][-1]
        if "end" not in last_activity:
            end_time = datetime.datetime.now().isoformat()
            start_time_dt = datetime.datetime.fromisoformat(last_activity["start"])
            end_time_dt = datetime.datetime.fromisoformat(end_time)
            duration = (end_time_dt - start_time_dt).total_seconds()

            if duration > inactive_time:
                adjusted_duration = duration - inactive_time
            else:
                adjusted_duration = 0
            last_activity["end"] = (start_time_dt + datetime.timedelta(seconds=adjusted_duration)).isoformat()
            start_time = None

def track_time(activity_log):
    usage_summary = {}
    for day, activities in activity_log.items():
        total_seconds = 0
        for activity in activities:
            start_time = datetime.datetime.fromisoformat(activity["start"])
            end_time = datetime.datetime.fromisoformat(activity["end"]) if "end" in activity else datetime.datetime.now()
            total_seconds += (end_time - start_time).total_seconds()
        usage_summary[day] = total_seconds / 3600  # Convert seconds to hours
    return usage_summary

def is_in_browser():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in naviguateurs:
            return True
    return False

def is_watching_videos():
    try:
        window = gw.getActiveWindow()
        return window and ("YouTube" in window.title or "Netflix" in window.title)
    except:
        return False

def clean_up_sessions(activity_log):
    """Ensure any open sessions from previous runs are closed."""
    for day, activities in activity_log.items():
        for activity in activities:
            if "end" not in activity:
                end_time = datetime.datetime.now().isoformat()
                start_time_dt = datetime.datetime.fromisoformat(activity["start"])
                end_time_dt = datetime.datetime.fromisoformat(end_time)
                duree = (end_time_dt - start_time_dt).total_seconds()

                if duree > inactive_time:
                    delta_temps = duree - inactive_time
                else:
                    delta_temps = 0

                activity["end"] = (start_time_dt + datetime.timedelta(seconds=delta_temps)).isoformat()

activity_log = load_logs()
clean_up_sessions(activity_log)
save_logs(activity_log)
last_active = time.time()
active = False

def on_activity():
    global last_active, active
    last_active = time.time()
    if not active:
        activity_logs(activity_log)
        active = True

keyboard_listener = keyboard.Listener(on_press=lambda _: on_activity())
mouse_listener = mouse.Listener(on_move=lambda *args: on_activity(), on_click=lambda *args: on_activity())
keyboard_listener.start()
mouse_listener.start()

#Now it's Pygame turn (to create a visual interface hehe :) ) --------------------------------------------------------------------------------------------------------

pygame.init()
pygame.display.set_caption("Time Spent On PC")
clock = pygame.time.Clock()
screen_width, screen_height = 760, 160
screen = pygame.display.set_mode((screen_width, screen_height))
font_lilitaone_50 = pygame.font.Font("fonts/LilitaOne-Regular.ttf", 50)
font_lilitaone_30 = pygame.font.Font("fonts/LilitaOne-Regular.ttf", 30)

def draw_text(texte, font, couleur, x, y):
    img = font.render(texte, True, couleur)
    text_width, text_height = font.size(texte)
    screen.blit(img, (x - text_width // 2, y - text_height // 2))

class Bouton():

    def __init__(self, x, y, width, height, color, color_text):
        self.rect = pygame.draw.rect(screen, color, (x, y, width, height))
        self.clicked = False
        self.color = color
        self.x, self.y = x, y
        self.width, self.height = width, height
        self.color_text = color_text

    def draw(self):
        reset_click = False
        mouse_cos = pygame.mouse.get_pos()
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        if self.rect.collidepoint(mouse_cos):
            if pygame.mouse.get_pressed()[0] == 1:
                self.clicked = True
            if pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                reset_click = True
                self.clicked = False
        return reset_click

clr_white = (255,255,255)
clr_black = (0,0,0)
clr_background = (149,212,175)
clr_text = (255,255,255)

bouton_black = Bouton(screen_width - 40, 10, 30, 30, (0,0,0), clr_white)
bouton_red = Bouton(screen_width - 40, 45, 30, 30, (202, 60, 102), clr_white)
bouton_green = Bouton(screen_width - 40, 80, 30, 30, (149,212,175), clr_white)
bouton_yellow = Bouton(screen_width - 40, 115, 30, 30, (235,212,169), clr_black)
bouton_white = Bouton(screen_width - 75, 10, 30, 30, (243,243,243), clr_black)
bouton_brown = Bouton(screen_width - 75, 45, 30, 30, (182, 115, 50), clr_white)
bouton_blue = Bouton(screen_width - 75, 80, 30, 30, (87, 132, 186), clr_white)
bouton_pink = Bouton(screen_width - 75, 115, 30, 30, (255, 122, 209), clr_white)
boutons = [bouton_black, bouton_green, bouton_yellow, bouton_white, bouton_red, bouton_brown, bouton_blue, bouton_pink]

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if time.time() - last_active > inactive_time:
        if active and not (is_in_browser() and is_watching_videos()):
            end_activity(activity_log)
            active = False
    else:
        if not active:
            activity_logs(activity_log)
            active = True

    clock.tick(60)
    screen.fill(clr_background)
    pygame.draw.rect(screen, (100,100,100), (screen_width - 80, 5, 75, 145))
    draw_text("Temps passé sur le PC:", font_lilitaone_30, clr_text, 150, 20)

    for bouton in boutons:
        if bouton.draw():
            clr_background = bouton.color
            clr_text = bouton.color_text

    save_logs(activity_log)
    summary = track_time(activity_log)

    paragraphe = 80
    for day, hours in summary.items():
        hours_int = int(hours)
        minutes = int((hours % 1) * 60)
        seconds = int(((hours * 3600) % 60))
        draw_text(f"{day}: {hours_int}h {minutes:02d}min {seconds:02d}sec", font_lilitaone_50, clr_text, screen_width // 2 - 30, paragraphe)
        paragraphe += 50

    pygame.display.update()

keyboard_listener.stop()
mouse_listener.stop()
pygame.quit()
save_logs(activity_log)
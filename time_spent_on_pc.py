from settings import *



def load_logs():
    if os.path.exists(STOCKAGE_FILE) and os.path.getsize(STOCKAGE_FILE) > 0:
        try:
            with open(STOCKAGE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Erreur de décodage JSON. Le fichier est corrompu.")
    return {}

def save_logs_and_data(activity_log):
    with open(STOCKAGE_FILE, "w") as f:
        json.dump(activity_log, f, indent=4)
    pickle_out = open('data/data_main', 'wb')
    data[0] = clr_background
    data[1] = clr_text
    pickle.dump(data, pickle_out)
    pickle_out.close()

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
    return f"{jour_abrev[nom_jour]} {datetime.datetime.now().strftime('%d ')}" + MONTHS[datetime.datetime.now().month - 1]

def activity_logs(activity_log):
    global START_TIME
    current_day = get_date()
    if current_day not in activity_log:
        activity_log[current_day] = []
    if not START_TIME:
        START_TIME = datetime.datetime.now().isoformat()
        activity_log[current_day].append({"start": START_TIME})

def end_activity(activity_log):
    global START_TIME
    current_day = get_date()
    if START_TIME and current_day in activity_log and activity_log[current_day]:
        last_activity = activity_log[current_day][-1]
        if "end" not in last_activity:
            end_time = datetime.datetime.now().isoformat()
            start_time_dt = datetime.datetime.fromisoformat(last_activity["start"])
            end_time_dt = datetime.datetime.fromisoformat(end_time)
            duration = (end_time_dt - start_time_dt).total_seconds()

            if duration > INACTIVE_TIME:
                adjusted_duration = duration - INACTIVE_TIME
            else:
                adjusted_duration = 0
            last_activity["end"] = (start_time_dt + datetime.timedelta(seconds=adjusted_duration)).isoformat()
            START_TIME = None

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

def is_watching_videos():
    try:
        window = gw.getActiveWindow()
        return window and ("YouTube" in window.title or "Netflix" in window.title)
    except:
        return False

def clean_up_sessions(activity_log):
    """Ensure any open sessions from previous runs are closed."""
    for _, activities in activity_log.items():
        for activity in activities:
            if "end" not in activity:
                end_time = datetime.datetime.now().isoformat()
                start_time_dt = datetime.datetime.fromisoformat(activity["start"])
                end_time_dt = datetime.datetime.fromisoformat(end_time)
                duree = (end_time_dt - start_time_dt).total_seconds()

                if duree > INACTIVE_TIME:
                    delta_temps = duree - INACTIVE_TIME
                else:
                    delta_temps = 0

                activity["end"] = (start_time_dt + datetime.timedelta(seconds=delta_temps)).isoformat()

activity_log = load_logs()
clean_up_sessions(activity_log)
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

def draw_text(texte, font, couleur, x, y):
    img = font.render(texte, True, couleur)
    text_width, text_height = font.size(texte)
    SCREEN.blit(img, (x - text_width // 2, y - text_height // 2))

class Bouton():

    def __init__(self, x, y, width, height, type, color, color_text, image):

        self.clicked = False
        self.type = type
        if self.type == "colored":
            self.rect = pygame.draw.rect(SCREEN, color, (x, y, width, height))
            self.x, self.y = x, y
            self.width, self.height = width, height
            self.color = color
            self.color_text = color_text
        elif self.type == "image":
            self.image = pygame.transform.scale(image, (width, height))
            self.rect = self.image.get_rect()
            self.rect.x = x
            self.rect.y = y

    def draw(self):
        reset_click = False
        mouse_cos = pygame.mouse.get_pos()
        if self.type == "colored":
            pygame.draw.rect(SCREEN, self.color, (self.x, self.y, self.width, self.height))
        elif self.type == "image":
            SCREEN.blit(self.image, self.rect)
        if self.rect.collidepoint(mouse_cos):
            if pygame.mouse.get_pressed()[0] == 1:
                self.clicked = True
            if pygame.mouse.get_pressed()[0] == 0 and self.clicked == True:
                reset_click = True
                self.clicked = False
        return reset_click


pickle_in = open(f'data/data_main', 'rb')
data = pickle.load(pickle_in)
clr_background = data[0]
clr_text = data[1]

bouton_black = Bouton(SCREEN_WIDTH - 40, 10, 30, 30, "colored", (0,0,0), CLR_WHITE, None)
bouton_red = Bouton(SCREEN_WIDTH - 40, 45, 30, 30, "colored", (202, 60, 102), CLR_WHITE, None)
bouton_green = Bouton(SCREEN_WIDTH - 40, 80, 30, 30, "colored", (149,212,175), CLR_WHITE, None)
bouton_yellow = Bouton(SCREEN_WIDTH - 40, 115, 30, 30, "colored", (235,212,169), CLR_BLACK, None)
bouton_white = Bouton(SCREEN_WIDTH - 75, 10, 30, 30, "colored", (243,243,243), CLR_BLACK, None)
bouton_brown = Bouton(SCREEN_WIDTH - 75, 45, 30, 30, "colored", (182, 115, 50), CLR_WHITE, None)
bouton_blue = Bouton(SCREEN_WIDTH - 75, 80, 30, 30, "colored", (87, 132, 186), CLR_WHITE, None)
bouton_pink = Bouton(SCREEN_WIDTH - 75, 115, 30, 30, "colored", (255, 122, 209), CLR_WHITE, None)

img_fleche = pygame.image.load("sprites/img_fleche.webp")
img_fleche_flip = pygame.transform.flip(img_fleche, True, False)
bouton_colors = Bouton(SCREEN_WIDTH - 27, 15, 23, 31, "image", None, None, img_fleche_flip)
bouton_colors_bis = Bouton(SCREEN_WIDTH - 107, 15, 23, 31, "image", None, None, img_fleche_flip)
boutons_colored = [bouton_black, bouton_green, bouton_yellow, bouton_white, bouton_red, bouton_brown, bouton_blue, bouton_pink]
menu_colors = False
current_day = get_date()



run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if time.time() - last_active > INACTIVE_TIME:
        if active and not  is_watching_videos():
            end_activity(activity_log)
            active = False
    else:
        if not active:
            activity_logs(activity_log)
            active = True

    CLOCK.tick(60)
    SCREEN.fill(clr_background)
    draw_text("Temps passé sur le PC:", FONT_LILITAONE_50, clr_text, SCREEN_WIDTH // 2 - 30, 55)
    draw_text("© TraZe 2024", FONT_LILITAONE_10, clr_text, SCREEN_WIDTH - 30, SCREEN_HEIGHT - 5)

    if not menu_colors:
        if bouton_colors.draw():
            menu_colors = True

    if menu_colors:
        pygame.draw.rect(SCREEN, (100,100,100), (SCREEN_WIDTH - 80, 5, 75, 145))
        for bouton in boutons_colored:
            if bouton.draw():
                clr_background = bouton.color
                clr_text = bouton.color_text
        if bouton_colors_bis.draw():
            menu_colors = False

    summary = track_time(activity_log)
    for day, hours in summary.items():
        if day == current_day:
            hours_int = int(hours)
            minutes = int((hours % 1) * 60)
            seconds = int(((hours * 3600) % 60))
            draw_text(f"{day}: {hours_int}h {minutes:02d}min {seconds:02d}sec", FONT_LILITAONE_30, clr_text, SCREEN_WIDTH // 2 - 30, 105)

    pygame.display.update()

keyboard_listener.stop()
mouse_listener.stop()
save_logs_and_data(activity_log)
pygame.quit()

# Just some functions to make the program minimize in the taskbar when closed -----------------------------------------------------



def create_image():
    # Créer une image carrée noire
    image = Image.new('RGB', (64, 64), "black")
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (16, 16, 48, 48),
        fill="white")
    return image

def on_exit(icon, item):
    icon.stop()
    python = sys.executable
    threading.Thread(target=lambda: os.execv(python, [python] + sys.argv)).start()

def setup(icon):
    icon.visible = True

icon = pystray.Icon("test")
icon.icon = create_image()
icon.title = "Time Spent on PC"
icon.menu = pystray.Menu(
    item("Développer", on_exit),
    item('Quitter', on_exit)
)

thread = threading.Thread(target=lambda: None)
thread.daemon = True
thread.start()

# Lancer l'icône dans la barre des tâches
icon.run(setup)


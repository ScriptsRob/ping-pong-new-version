from pygame import *
import socket
import json
from threading import Thread
import pygame_widgets
import sys



# ---ПУГАМЕ НАЛАШТУВАННЯ ---
volume = 0.4
mixer.init()
trail = []
MAX_TRAIL = 30
WIDTH, HEIGHT = 800, 600
trail_surface = Surface((WIDTH, HEIGHT), SRCALPHA)
init()

screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Hellfire ping-pong")


# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080))  # ---- Підключення до сервера

            buffer = ""
            game_state = {}

            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over

    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data

            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)

                if packet.strip():
                    game_state = json.loads(packet)

        except:
            game_state["winner"] = -1
            break


# --- ШРИФТИ ---
font_win = font.SysFont("Segoe UI", 30, 'bold')
font_main = font.SysFont("Segoe UI", 30, "bold")

# --- ЗОБРАЖЕННЯ ---
bar1_image = image.load('assets/images/bar1.png')
bar1_image = transform.scale(bar1_image, (30, 120))
bar2_image = image.load('assets/images/bar2.png')
bar2_image = transform.scale(bar2_image, (30, 120))

bg = image.load(r'D:\Logika_projects\PygameProjects\ping-pong\assets\images\background.png')
bg = transform.scale(bg, (WIDTH, HEIGHT))

ball = image.load('assets/images/ball.png')
ball = transform.scale(ball, (25, 25))

# --- ЗВУКИ ---
padel_hit_sound = mixer.Sound("assets/sounds/padel.mp3")
wall_hit_sound = mixer.Sound("assets/sounds/wall.mp3")
bg_music = mixer.music.load("assets/sounds/BG.mp3")
mixer.music.set_volume(0.2)

# --- ГРА ---
game_over = False
winner = None
you_winner = None

my_id, game_state, buffer, client = connect_to_server()

Thread(target=receive, daemon=True).start()

mixer.music.play(-1)

while True:

    screen.blit(bg, (0, 0))

    for e in event.get():
        if e.type == QUIT:
            exit()

    # --- ВІДЛІК ---
    
    if "countdown" in game_state and game_state["countdown"] > 0:
        countdown_text = font.Font(None, 72).render(
            str(game_state["countdown"]),
            True,
            (0, 0, 0)
        )

        screen.blit(
            countdown_text,
            (WIDTH // 2 - 15, HEIGHT // 2 - 30)
        )
        display.update()
        continue  # Не малюємо гру до завершення відліку

    # --- ПЕРЕМОГА ---
    if "winner" in game_state and game_state["winner"] is not None:

        if you_winner is None:  # Встановлюємо тільки один раз

            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False

        if you_winner:
            text = "Ти переміг!"
        else:
            text = "Пощастить наступним разом!"

        win_text = font_win.render(
            text,
            True,
            (255, 215, 0)
        )

        text_rect = win_text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2)
        )

        screen.blit(win_text, text_rect)

        text = font_win.render(
            'К - рестарт',
            True,
            (255, 215, 0)
        )

        text_rect = text.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 120)
        )

        screen.blit(text, text_rect)

        display.update()
        continue  # Блокує гру після перемоги

    # --- ОСНОВНА ГРА ---
    if game_state:

        screen.blit(bar2_image,(20, game_state['paddles']['0'], 20, 100))

        screen.blit(bar1_image,(WIDTH - 40, game_state['paddles']['1'], 20, 100))

        screen.blit(ball,(game_state['ball']['x'], game_state['ball']['y']))

        score_text = font_main.render(
            f"{game_state['scores'][0]} : {game_state['scores'][1]}",
            True,
            (255, 255, 255)
        )

        screen.blit(
            score_text,
            (WIDTH // 2 - 25, 20)
        )

        if game_state['sound_event']:

            if game_state['sound_event'] == 'wall_hit':
               wall_hit_sound.play()

            if game_state['sound_event'] == 'platform_hit':
                # звук відбиття м'ячика від платформи
                padel_hit_sound.play()

    else:

        wating_text = font_main.render(
            "Очікування гравців . . .",
            True,
            (0, 0, 0),
            (255,255,255)
            
        )

        screen.blit(
            wating_text,
            (WIDTH // 2 - 120 , 275)
        )

    display.update()
    clock.tick(60)

    keys = key.get_pressed()

    if keys[K_w]:
        client.send(b"UP")

    if keys[K_s]:
        client.send(b"DOWN")
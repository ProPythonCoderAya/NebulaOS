import os
import sys
import json
import pygame
import bcrypt
import _core.Disk as Disk
pygame.init()


# Functions
def check_user_exists(user):
    with open(Disk.disk_name + "/usr.ur") as file:
        user_data = json.load(file)
    validate_user_data(user_data)
    if user not in user_data["users"].keys():
        exit(1)


def run(filepath, *args):
    cmd = [
        f"\"{sys.executable}\"", f"\"{filepath}\"", *map(str, args)
    ]
    os.system(" ".join(cmd))


def validate_user_data(user_data):
    check_if_dict(user_data)


def check_password(stored_hash, password):
    # Compare the entered password with the stored hash
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))


def check_if_dict(obj: object, error: str = "Expected dict, not $OBJ"):
    if not isinstance(obj, dict):
        complete_error_message = ""
        i = 0
        while i < len(error):
            char = error[i]
            if char == "$":
                if error[i+1:i+4] == "OBJ":
                    complete_error_message += obj.__class__.__name__
                    i += 4
                    continue
                else:
                    complete_error_message += "$"
            else:
                complete_error_message += char
            i += 1

        exit(complete_error_message)


# Main screen called 'WIN'
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NebulaOS Restart - Login")

# Other
ms = int

# Fonts
font_big = pygame.font.SysFont("Arial", 48)
font_small = pygame.font.SysFont("Arial", 24)

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (230, 230, 230)
BLACK = (0, 0, 0)

# Other
clock = pygame.time.Clock()

def login():
    # Check if remember me is set
    name = ""
    with open(Disk.disk_name + "/settings.st") as settings:
        data = json.load(settings)
        if not isinstance(data, dict):
            raise TypeError("Settings file may be corrupted")
        if "remember_me" in data.keys():
            name = data["remember_me"]
    # Text
    username = name
    password = ""
    typing = "p" if name else "u"

    # Time
    start_time = pygame.time.get_ticks()
    clock = pygame.time.Clock()
    fps = 60
    blink_speed: ms = 1000

    # Main loop
    active = True
    while active:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                active = False
            if event.type == pygame.KEYDOWN:
                if typing == "u":
                    if event.key == pygame.K_BACKSPACE:  # User presses Backspace
                        username = username[:-1]  # Remove last character
                    elif event.key == pygame.K_RETURN:
                        username = "Ayaan"  # Just makes it easier for testing the desktop, so Chat, don't comment ANYTHING about this.
                        if len(username) > 0:
                            typing = "p"
                    elif event.unicode and 32 <= ord(event.unicode) <= 0xffff:
                        username += event.unicode  # Add typed character
                else:
                    if event.key == pygame.K_BACKSPACE:  # User presses Backspace
                        if not password:
                            typing = "u"
                        else:
                            password = password[:-1]  # Remove last character
                    elif event.key == pygame.K_RETURN:
                        password = "Voyages*1985"  # Just makes it easier for testing the desktop, so Chat, don't comment ANYTHING about this.
                        if len(password) > 0:
                            active = False
                    elif event.unicode and 32 <= ord(event.unicode) <= 0xffff:
                        password += event.unicode  # Add typed character

        # Fill the screen
        WIN.fill("black")

        # Draw in the UI
        x, y = (WIDTH - 350) / 2, (HEIGHT - 200) / 2  # Lots and lots of math
        pygame.draw.rect(WIN, (255, 255, 255), (x, y, 350, 200), border_radius=25)
        x += 20  # Lots and lots of math
        y += (200 - 125) / 2  # Lots and lots of math
        pygame.draw.rect(WIN, (230, 230, 230), (x, y, 75, 125), border_radius=10)
        pygame.draw.circle(WIN, (0, 0, 0), (x + 75 / 2, y + 125 / 2 - 20), 15)  # Lots and lots of math
        pygame.draw.rect(WIN, (0, 0, 0), (x + 17.5, y + 50, 40, 50), border_top_left_radius=500,
                         border_top_right_radius=500, border_bottom_left_radius=15,
                         border_bottom_right_radius=15)  # Lots and lots of math
        x, y = (WIDTH - 350) / 2 + 115, (HEIGHT - 200 + 200 - 125) / 2 + 10  # Lots and lots of math
        pygame.draw.rect(WIN, (230, 230, 230), (x, y, 150, 30), border_radius=10)
        pygame.draw.rect(WIN, (230, 230, 230), (x, y + 50, 150, 30), border_radius=10)

        # Draw the typed text
        username_rect = font_small.render(username, True, (0, 0, 0))
        WIN.blit(username_rect, (x + 5, y))

        password_dots = "•" * len(password)
        password_rect = font_small.render(password_dots, True, (0, 0, 0))
        WIN.blit(password_rect, (x + 5, y + 50))

        # Draw the caret for username or password based on typing
        if typing == "u":
            width = username_rect.get_width()
            caret_y = y
        else:
            width = password_rect.get_width()
            caret_y = y + 50

        difference = ((pygame.time.get_ticks() - start_time) // (blink_speed / 2)) * (blink_speed / 2)
        if difference % blink_speed == (blink_speed / 2):
            pygame.draw.rect(WIN, (200, 200, 200), (x + width + 5, caret_y + 3, 3, 24))

        # Update the screen
        pygame.display.flip()

    return username, password


def main() -> None:
    username, password = login()
    check_user_exists(username)
    data = json.load(Disk.disk_name + "/usr.ur")
    hashed_password = data["users"][username]["password"]
    if check_password(hashed_password, password):
        pygame.quit()
        run("main.py", username, json.dumps(data["users"][username]))
    else:
        exit(1)

if __name__ == "__main__":
    main()

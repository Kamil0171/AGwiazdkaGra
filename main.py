# Autor: Kamil Amarasekara

import os
import sys
import pygame
import random

# Minimalne i maksymalne rozmiary okna (w pikselach)
MIN_SCREEN_SIZE = (800, 600)
MAX_SCREEN_SIZE = (1920, 1080)


# Funkcja do uzyskania ścieżki do zasobów, kompatybilna z PyInstallerem
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller tymczasowy folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Ustawienia planszy (stała wirtualna rozdzielczość)
GRID_SIZE = 20  # Liczba komórek w jednym wierszu/kolumnie
CELL_SIZE = 40  # Rozmiar pojedynczej komórki (w pikselach)
HEADER_HEIGHT = 60  # Wysokość nagłówka (obszar górny)
VIRTUAL_WIDTH = GRID_SIZE * CELL_SIZE
VIRTUAL_HEIGHT = GRID_SIZE * CELL_SIZE + HEADER_HEIGHT
VIRTUAL_SIZE = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

# Początkowy rozmiar okna – ustawiony na wirtualną rozdzielczość
SCREEN_SIZE = VIRTUAL_SIZE

# Definicje kolorów
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 128)
GRAY = (200, 200, 200)

# Domyślne punkty startowy i końcowy
DEFAULT_START = (19, 0)
DEFAULT_END = (0, 19)

# Inicjalizacja Pygame i utworzenie okna resizable
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
pygame.display.set_caption("A* Gra")  # Po wyjściu z menu tytuł to tylko "A* Gra"

# Ładowanie obrazków przy użyciu funkcji resource_path
try:
    start_img = pygame.image.load(resource_path("start.jpg"))
    end_img = pygame.image.load(resource_path("koniec.jpg"))
    ludzik_img = pygame.image.load(resource_path("ludzik.jpg"))
    button_play = pygame.image.load(resource_path("graj.png"))
    button_exit_orig = pygame.image.load(resource_path("wyjdz.png"))
    button_check = pygame.image.load(resource_path("check.jpg"))
    button_restart = pygame.image.load(resource_path("restart.jpg"))
    background_img = pygame.image.load(resource_path("tlo.jpg"))
except Exception as e:
    print("Błąd ładowania obrazków:", e)
    sys.exit()

# Skalowanie obrazków do wirtualnych rozmiarów
start_img = pygame.transform.scale(start_img, (CELL_SIZE, CELL_SIZE))
end_img = pygame.transform.scale(end_img, (CELL_SIZE, CELL_SIZE))
ludzik_img = pygame.transform.scale(ludzik_img, (CELL_SIZE, CELL_SIZE))
button_play = pygame.transform.scale(button_play, (200, 200))
button_check = pygame.transform.smoothscale(button_check, (50, 50))
button_restart = pygame.transform.smoothscale(button_restart, (50, 50))
background_img = pygame.transform.smoothscale(background_img, VIRTUAL_SIZE)

# Przyciski Exit:
button_exit_menu = pygame.transform.scale(button_exit_orig, (200, 200))
button_exit_game = pygame.transform.smoothscale(button_exit_orig, (50, 50))


# Klasa Node – reprezentacja pojedynczej komórki dla algorytmu A*
class Node:
    def __init__(self, position, parent=None):
        self.position = position  # krotka (wiersz, kolumna)
        self.parent = parent  # referencja do rodzica
        self.g = 0  # koszt dojścia od startu do tego węzła
        self.h = 0  # heurystyka (odległość do celu)
        self.f = 0  # suma g + h


def euclidean_distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


def calculate_all_f_values(grid, end):
    nodes_dict = {}
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 5:
                continue
            node = Node((row, col))
            node.h = euclidean_distance((row, col), end)
            node.f = node.g + node.h
            nodes_dict[(row, col)] = node
    return nodes_dict, grid


def astar_algorithm(grid, start, end, nodes_dict, console_grid):
    open_list = []
    closed_set = set()
    if start not in nodes_dict or end not in nodes_dict:
        return None
    start_node = nodes_dict[start]
    open_list.append(start_node)
    while open_list:
        open_list.sort(key=lambda node: node.f)
        current_node = open_list.pop(0)
        closed_set.add(current_node.position)
        if current_node.position == end:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            path.reverse()
            return path
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Tylko ruchy w górę, dół, lewo, prawo
            neighbor_pos = (current_node.position[0] + dx, current_node.position[1] + dy)
            if 0 <= neighbor_pos[0] < GRID_SIZE and 0 <= neighbor_pos[1] < GRID_SIZE:
                if grid[neighbor_pos[0]][neighbor_pos[1]] == 5 or neighbor_pos in closed_set:
                    continue
                neighbor_node = nodes_dict.get(neighbor_pos)
                if neighbor_node is None:
                    continue
                new_g = current_node.g + 1
                if neighbor_node.g == 0 or new_g < neighbor_node.g:
                    neighbor_node.g = new_g
                    neighbor_node.h = euclidean_distance(neighbor_pos, end)
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    neighbor_node.parent = current_node
                    if neighbor_node not in open_list:
                        open_list.append(neighbor_node)
    return None


def generate_random_grid(obstacle_chance=0.3):
    grid = []
    for row in range(GRID_SIZE):
        row_data = []
        for col in range(GRID_SIZE):
            if (row, col) == DEFAULT_START or (row, col) == DEFAULT_END:
                row_data.append(0)
            else:
                row_data.append(5 if random.random() < obstacle_chance else 0)
        grid.append(row_data)
    return grid


def draw_grid(target_surface, grid, start, end, user_path, optimal_path, user_correct, reveal_optimal=False):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + HEADER_HEIGHT, CELL_SIZE, CELL_SIZE)
            color = BLACK if grid[row][col] == 5 else WHITE
            if user_correct and user_path and (row, col) in user_path:
                color = GREEN
            elif reveal_optimal and optimal_path and (row, col) in optimal_path:
                color = RED
            elif user_path and (row, col) in user_path:
                color = DARK_BLUE
            pygame.draw.rect(target_surface, color, cell_rect)
            pygame.draw.rect(target_surface, GRAY, cell_rect, 1)
    if start:
        target_surface.blit(start_img, (start[1] * CELL_SIZE, start[0] * CELL_SIZE + HEADER_HEIGHT))
    if end:
        target_surface.blit(end_img, (end[1] * CELL_SIZE, end[0] * CELL_SIZE + HEADER_HEIGHT))


def draw_text(target_surface, text, position, font_size=20, color=BLACK):
    font = pygame.font.SysFont("comicsans", font_size, bold=True)
    label = font.render(text, True, color)
    target_surface.blit(label, position)


def is_valid_position(start, end):
    return abs(start[0] - end[0]) >= 3 or abs(start[1] - end[1]) >= 3


def animate_ludzik(path, reveal_optimal):
    for pos in path:
        draw_grid(game_surface, current_grid, current_start, current_end, user_path, optimal_path, user_correct,
                  reveal_optimal)
        ludzik_x = pos[1] * CELL_SIZE
        ludzik_y = pos[0] * CELL_SIZE + HEADER_HEIGHT
        game_surface.blit(ludzik_img, (ludzik_x, ludzik_y))
        scaled = pygame.transform.scale(game_surface, SCREEN_SIZE)
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        pygame.time.delay(300)


def main_menu():
    global SCREEN_SIZE
    menu_surface = pygame.Surface(VIRTUAL_SIZE)
    pygame.display.set_caption("A* Gra - Menu")
    button_play_rect = button_play.get_rect(center=(VIRTUAL_WIDTH // 3, VIRTUAL_HEIGHT // 2))
    button_exit_rect = button_exit_menu.get_rect(center=(2 * VIRTUAL_WIDTH // 3, VIRTUAL_HEIGHT // 2))
    font_title = pygame.font.SysFont("comicsans", 50, bold=True)
    font_menu = pygame.font.SysFont("comicsans", 30, bold=True)
    title_text = font_title.render("A* Gra - Menu", True, WHITE)
    title_rect = title_text.get_rect(center=(VIRTUAL_WIDTH // 2, 100))
    menu_text = font_menu.render("", True, WHITE)
    menu_rect = menu_text.get_rect(center=(VIRTUAL_WIDTH // 2, 200))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                new_width = max(MIN_SCREEN_SIZE[0], min(int(event.size[0]), MAX_SCREEN_SIZE[0]))
                new_height = max(MIN_SCREEN_SIZE[1], min(int(event.size[1]), MAX_SCREEN_SIZE[1]))
                SCREEN_SIZE = (new_width, new_height)
        menu_surface.blit(background_img, (0, 0))
        menu_surface.blit(title_text, title_rect)
        menu_surface.blit(menu_text, menu_rect)
        menu_surface.blit(button_play, button_play.get_rect(center=(VIRTUAL_WIDTH // 3, VIRTUAL_HEIGHT // 2)))
        menu_surface.blit(button_exit_menu, button_exit_rect)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                virtual_mx = mx * VIRTUAL_WIDTH / SCREEN_SIZE[0]
                virtual_my = my * VIRTUAL_HEIGHT / SCREEN_SIZE[1]
                if button_play.get_rect(center=(VIRTUAL_WIDTH // 3, VIRTUAL_HEIGHT // 2)).collidepoint(
                        (virtual_mx, virtual_my)):
                    return
                elif button_exit_menu.get_rect(center=(2 * VIRTUAL_WIDTH // 3, VIRTUAL_HEIGHT // 2)).collidepoint(
                        (virtual_mx, virtual_my)):
                    pygame.quit()
                    sys.exit()
        scaled = pygame.transform.scale(menu_surface, SCREEN_SIZE)
        screen.blit(scaled, (0, 0))
        pygame.display.flip()


# Globalne zmienne do przechowywania stanu gry
current_grid = None
current_start = None
current_end = None
user_path = []
optimal_path = None
user_correct = False


def main():
    global current_grid, current_start, current_end, user_path, optimal_path, user_correct, SCREEN_SIZE, screen, game_surface
    main_menu()  # Uruchom menu
    pygame.display.set_caption("A* Gra")
    current_grid = generate_random_grid()
    current_start = None
    current_end = None
    user_path = []
    optimal_path = None
    user_correct = False
    reveal_optimal = False
    remaining_steps = 0
    show_error_message = False
    message = "Wybierz punkt startowy"
    button_check_rect = button_check.get_rect(topleft=(10, 10))
    button_restart_rect = button_restart.get_rect(topleft=(button_check.get_rect().right + 10, 10))
    button_exit_top_rect = button_exit_game.get_rect(topright=(VIRTUAL_WIDTH - 10, 10))
    selecting_start = True
    selecting_end = False
    path_checked = False  # Zmienna do zapamiętania, czy ścieżka została już sprawdzona

    # Utwórz wirtualną powierzchnię gry o stałym rozmiarze VIRTUAL_SIZE
    game_surface = pygame.Surface(VIRTUAL_SIZE)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE:
                new_width = max(MIN_SCREEN_SIZE[0], min(int(event.size[0]), MAX_SCREEN_SIZE[0]))
                new_height = max(MIN_SCREEN_SIZE[1], min(int(event.size[1]), MAX_SCREEN_SIZE[1]))
                SCREEN_SIZE = (new_width, new_height)
                screen = pygame.display.set_mode(SCREEN_SIZE, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                virtual_mx = mx * VIRTUAL_WIDTH / SCREEN_SIZE[0]
                virtual_my = my * VIRTUAL_HEIGHT / SCREEN_SIZE[1]
                if button_exit_top_rect.collidepoint((virtual_mx, virtual_my)):
                    pygame.quit()
                    sys.exit()
                if button_restart_rect.collidepoint((virtual_mx, virtual_my)):
                    current_grid = generate_random_grid()
                    current_start = None
                    current_end = None
                    user_path = []
                    optimal_path = None
                    user_correct = False
                    reveal_optimal = False
                    remaining_steps = 0
                    show_error_message = False
                    message = "Wybierz punkt startowy"
                    selecting_start = True
                    selecting_end = False
                    path_checked = False
                    continue
                if button_check_rect.collidepoint((virtual_mx, virtual_my)):
                    if optimal_path:
                        if user_path and current_end and user_path[-1] == current_end and user_path == optimal_path:
                            user_correct = True
                            message = "Znaleziono ścieżkę!"
                            animate_ludzik(optimal_path, False)
                        else:
                            message = "Niepoprawna ścieżka!"
                            reveal_optimal = True
                            animate_ludzik(optimal_path, True)
                        path_checked = True
                    continue
                if virtual_my < HEADER_HEIGHT:
                    continue
                row = int((virtual_my - HEADER_HEIGHT) // CELL_SIZE)
                col = int(virtual_mx // CELL_SIZE)
                if row < 0 or row >= GRID_SIZE or col < 0 or col >= GRID_SIZE:
                    continue
                if current_grid[row][col] == 5:
                    continue
                if selecting_start:
                    current_start = (row, col)
                    user_path = [current_start]
                    selecting_start = False
                    selecting_end = True
                    message = "Wybierz punkt końcowy"
                elif selecting_end:
                    current_end = (row, col)
                    if not is_valid_position(current_start, current_end):
                        show_error_message = True
                        message = "Punkty muszą być oddalone o co najmniej 3 komórki"
                    else:
                        show_error_message = False
                        selecting_end = False
                        nodes_dict, console_grid = calculate_all_f_values(current_grid, current_end)
                        optimal_path = astar_algorithm(current_grid, current_start, current_end, nodes_dict,
                                                       console_grid)
                        if optimal_path:
                            remaining_steps = len(optimal_path) - 1
                            message = ""
                        else:
                            message = "Nie można wyznaczyć ścieżki!"
                else:
                    # Zapobiegamy poruszaniu się na skos - sprawdzamy, czy nowy krok jest sąsiadujący (góra, dół, prawo, lewo)
                    if remaining_steps > 0 and (row, col) not in user_path:
                        last = user_path[-1]
                        if (abs(row - last[0]) == 1 and col == last[1]) or (abs(col - last[1]) == 1 and row == last[0]):
                            user_path.append((row, col))
                            remaining_steps -= 1
                        # Jeśli krok nie jest sąsiadujący, kliknięcie jest ignorowane.
        # Automatyczne sprawdzenie ścieżki tylko gdy jest idealna
        if not selecting_start and not selecting_end and remaining_steps == 0 and optimal_path is not None and not path_checked:
            if user_path == optimal_path:
                user_correct = True
                message = "Znaleziono ścieżkę!"
                animate_ludzik(optimal_path, False)
                path_checked = True
            # Jeśli ścieżka nie jest optymalna, użytkownik musi kliknąć przycisk "Sprawdź"

        game_surface.fill(WHITE)
        draw_grid(game_surface, current_grid, current_start, current_end, user_path, optimal_path, user_correct,
                  reveal_optimal)
        game_surface.blit(button_check, button_check.get_rect(topleft=(10, 10)))
        game_surface.blit(button_restart, button_restart.get_rect(topleft=(button_check.get_rect().right + 10, 10)))
        game_surface.blit(button_exit_game, button_exit_top_rect)
        header_text = f"Pozostało {remaining_steps} kroków" if optimal_path is not None else message
        font = pygame.font.SysFont("comicsans", 20, bold=True)
        label = font.render(header_text, True, BLACK)
        label_width, label_height = label.get_size()
        text_position = ((VIRTUAL_WIDTH - label_width) // 2, (HEADER_HEIGHT - label_height) // 2)
        game_surface.blit(label, text_position)
        scaled_surface = pygame.transform.scale(game_surface, SCREEN_SIZE)
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()


if __name__ == "__main__":
    main()

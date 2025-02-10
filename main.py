import pygame
import sys
import numpy as np

GRID_SIZE = 20
CELL_SIZE = 40
HEADER_HEIGHT = 60
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE + HEADER_HEIGHT
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

WHITE     = (255, 255, 255)
BLACK     = (0, 0, 0)
RED       = (255, 0, 0)
GREEN     = (0, 255, 0)
DARK_BLUE = (0, 0, 128)
GRAY      = (200, 200, 200)

DEFAULT_START = (19, 0)
DEFAULT_END   = (0, 19)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("A* Gra")

try:
    start_img    = pygame.image.load("start.jpg")
    end_img      = pygame.image.load("koniec.jpg")
    ludzik_img   = pygame.image.load("ludzik.jpg")
    button_play  = pygame.image.load("graj.jpg")
    button_exit  = pygame.image.load("wyjdz.jpg")
    button_check = pygame.image.load("check.jpg")
except Exception as e:
    print("Błąd ładowania obrazków:", e)
    sys.exit()

start_img    = pygame.transform.scale(start_img, (CELL_SIZE, CELL_SIZE))
end_img      = pygame.transform.scale(end_img, (CELL_SIZE, CELL_SIZE))
ludzik_img   = pygame.transform.scale(ludzik_img, (CELL_SIZE, CELL_SIZE))
button_play  = pygame.transform.scale(button_play, (200, 200))
button_exit  = pygame.transform.scale(button_exit, (200, 200))
button_check = pygame.transform.smoothscale(button_check, (50, 50))

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

def euclidean_distance(pos1, pos2):
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

def calculate_all_f_values(grid, end):
    nodes_dict = {}
    console_grid = np.copy(grid)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 5:
                continue
            node = Node((row, col))
            node.h = euclidean_distance((row, col), end)
            node.f = node.g + node.h
            nodes_dict[(row, col)] = node
    return nodes_dict, console_grid

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
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
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
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if (row, col) == DEFAULT_START or (row, col) == DEFAULT_END:
                continue
            if np.random.rand() < obstacle_chance:
                grid[row][col] = 5
    return grid

def draw_grid(grid, start, end, user_path, optimal_path, user_correct, reveal_optimal=False):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE + HEADER_HEIGHT, CELL_SIZE, CELL_SIZE)
            if grid[row][col] == 5:
                color = BLACK
            else:
                color = WHITE
            if user_correct and user_path and (row, col) in user_path:
                color = GREEN
            elif reveal_optimal and optimal_path and (row, col) in optimal_path:
                color = RED
            elif user_path and (row, col) in user_path:
                color = DARK_BLUE
            pygame.draw.rect(screen, color, cell_rect)
            pygame.draw.rect(screen, GRAY, cell_rect, 1)
    if start:
        screen.blit(start_img, (start[1] * CELL_SIZE, start[0] * CELL_SIZE + HEADER_HEIGHT))
    if end:
        screen.blit(end_img, (end[1] * CELL_SIZE, end[0] * CELL_SIZE + HEADER_HEIGHT))

def draw_text(text, position, font_size=20, color=BLACK):
    font = pygame.font.SysFont("comicsans", font_size, bold=True)
    label = font.render(text, True, color)
    screen.blit(label, position)

def is_valid_position(start, end):
    return abs(start[0] - end[0]) >= 3 or abs(start[1] - end[1]) >= 3

def animate_ludzik(path, reveal_optimal):
    for pos in path:
        draw_grid(current_grid, current_start, current_end, user_path, optimal_path, user_correct, reveal_optimal)
        ludzik_x = pos[1] * CELL_SIZE
        ludzik_y = pos[0] * CELL_SIZE + HEADER_HEIGHT
        screen.blit(ludzik_img, (ludzik_x, ludzik_y))
        pygame.display.flip()
        pygame.time.delay(300)

def main_menu():
    menu_screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("A* Gra - Menu")
    button_play_rect = button_play.get_rect(center=(SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
    button_exit_rect = button_exit.get_rect(center=(2 * SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2))
    font_title = pygame.font.SysFont("comicsans", 50, bold=True)
    font_menu = pygame.font.SysFont("comicsans", 30, bold=True)
    title_text = font_title.render("A* Gra", True, BLACK)
    menu_text = font_menu.render("Menu", True, BLACK)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
    menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
    while True:
        menu_screen.fill(WHITE)
        menu_screen.blit(title_text, title_rect)
        menu_screen.blit(menu_text, menu_rect)
        menu_screen.blit(button_play, button_play_rect)
        menu_screen.blit(button_exit, button_exit_rect)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_play_rect.collidepoint(event.pos):
                    return
                elif button_exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
        pygame.display.flip()

current_grid = None
current_start = None
current_end = None
user_path = []
optimal_path = None
user_correct = False

def main():
    global current_grid, current_start, current_end, user_path, optimal_path, user_correct
    main_menu()
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
    selecting_start = True
    selecting_end = False
    while True:
        screen.fill(WHITE)
        draw_grid(current_grid, current_start, current_end, user_path, optimal_path, user_correct, reveal_optimal)
        screen.blit(button_check, button_check_rect)
        if optimal_path is not None:
            header_text = f"Pozostało {remaining_steps} kroków"
        else:
            header_text = message
        font = pygame.font.SysFont("comicsans", 20, bold=True)
        label = font.render(header_text, True, BLACK)
        label_width, label_height = label.get_size()
        text_position = ((SCREEN_WIDTH - label_width) // 2, (HEADER_HEIGHT - label_height) // 2)
        screen.blit(label, text_position)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if button_check_rect.collidepoint(event.pos):
                    if optimal_path:
                        if user_path and current_end and user_path[-1] == current_end and user_path == optimal_path:
                            user_correct = True
                            message = "Znaleziono ścieżkę!"
                        else:
                            message = "Niepoprawna ścieżka!"
                            reveal_optimal = True
                            animate_ludzik(optimal_path, reveal_optimal)
                    continue
                if my < HEADER_HEIGHT:
                    continue
                row = (my - HEADER_HEIGHT) // CELL_SIZE
                col = mx // CELL_SIZE
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
                        optimal_path = astar_algorithm(current_grid, current_start, current_end, nodes_dict, console_grid)
                        if optimal_path:
                            remaining_steps = len(optimal_path) - 1
                            message = ""
                        else:
                            message = "Brak ścieżki optymalnej!"
                else:
                    if remaining_steps > 0 and (row, col) not in user_path:
                        user_path.append((row, col))
                        remaining_steps -= 1

if __name__ == "__main__":
    main()

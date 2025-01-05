import numpy as np
import pygame
import sys

GRID_SIZE = 20
CELL_SIZE = 40
SCREEN_SIZE = GRID_SIZE * CELL_SIZE

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_BLUE = (0, 0, 128)
GRAY = (200, 200, 200)

START = (19, 0)
END = (0, 19)

pygame.init()
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))

start_img = pygame.image.load("start.jpg")
end_img = pygame.image.load("koniec.jpg")
ludzik_img = pygame.image.load("ludzik.jpg")
button_play = pygame.image.load("graj.jpg")
button_exit = pygame.image.load("wyjdz.jpg")

start_img = pygame.transform.scale(start_img, (CELL_SIZE, CELL_SIZE))
end_img = pygame.transform.scale(end_img, (CELL_SIZE, CELL_SIZE))
ludzik_img = pygame.transform.scale(ludzik_img, (CELL_SIZE, CELL_SIZE))
button_play = pygame.transform.scale(button_play, (200, 100))
button_exit = pygame.transform.scale(button_exit, (200, 100))


class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0


def euclidean_distance(node1, node2):
    return ((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2) ** 0.5


def calculate_all_f_values(grid):
    nodes_dict = {}
    end_node = Node(END)

    console_grid = np.copy(grid)

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if grid[row][col] == 5:
                continue
            node = Node((row, col))
            node.h = euclidean_distance((row, col), END)
            node.f = node.g + node.h
            nodes_dict[(row, col)] = node

    return nodes_dict, console_grid


def astar_algorithm(grid, start, end, nodes_dict, console_grid):
    open_list = []
    closed_list = set()
    start_node = nodes_dict[start]
    open_list.append(start_node)

    while open_list:
        open_list.sort(key=lambda node: node.f)
        current_node = open_list.pop(0)
        closed_list.add(current_node.position)

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
                if grid[neighbor_pos] == 5 or neighbor_pos in closed_list:
                    continue
                neighbor_node = nodes_dict[neighbor_pos]
                new_g = current_node.g + 1

                if neighbor_node.g == 0 or new_g < neighbor_node.g:
                    neighbor_node.g = new_g
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    neighbor_node.parent = current_node
                    if neighbor_node not in open_list:
                        open_list.append(neighbor_node)

    return None


def generate_random_grid(obstacle_chance=0.3):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if (row, col) != START and (row, col) != END:
                if np.random.rand() < obstacle_chance:
                    grid[row, col] = 5
    return grid


def draw_grid(grid, start=None, end=None):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = WHITE
            if grid[row][col] == 5:
                color = BLACK
            pygame.draw.rect(screen, color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, GRAY, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    if start != (19, 0):
        screen.blit(start_img, (start[1] * CELL_SIZE, start[0] * CELL_SIZE))
    if end != (0, 19):  # Ensures the end point is only drawn after selection
        screen.blit(end_img, (end[1] * CELL_SIZE, end[0] * CELL_SIZE))


def animate_path(path):
    for pos in path[1:-1]:
        screen.fill(WHITE)
        draw_grid(grid, START, END)
        screen.blit(ludzik_img, (pos[1] * CELL_SIZE, pos[0] * CELL_SIZE))
        pygame.display.flip()
        pygame.time.delay(300)

    screen.fill(WHITE)
    draw_grid(grid, START, END)
    for previous_pos in path[1:-1]:
        pygame.draw.rect(screen, GREEN, (previous_pos[1] * CELL_SIZE, previous_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    pygame.display.flip()


def main_menu():
    menu_screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
    pygame.display.set_caption("A* gra")

    button_play_rect = button_play.get_rect(center=(SCREEN_SIZE // 3, SCREEN_SIZE // 2))
    button_exit_rect = button_exit.get_rect(center=(2 * SCREEN_SIZE // 3, SCREEN_SIZE // 2))

    font_title = pygame.font.SysFont("comicsans", 50, bold=True)
    font_menu = pygame.font.SysFont("comicsans", 30, bold=True)

    title_text = font_title.render("", True, BLACK)
    menu_text = font_menu.render("Menu", True, BLACK)

    play_text = font_menu.render("Graj", True, BLACK)
    exit_text = font_menu.render("Wyjdz", True, BLACK)

    title_rect = title_text.get_rect(center=(SCREEN_SIZE // 2, 100))
    menu_rect = menu_text.get_rect(center=(SCREEN_SIZE // 2, 200))

    play_text_rect = play_text.get_rect(center=(SCREEN_SIZE // 3, SCREEN_SIZE // 2 + 60))
    exit_text_rect = exit_text.get_rect(center=(2 * SCREEN_SIZE // 3, SCREEN_SIZE // 2 + 60))

    while True:
        menu_screen.fill(WHITE)
        menu_screen.blit(title_text, title_rect)
        menu_screen.blit(menu_text, menu_rect)
        menu_screen.blit(button_play, button_play_rect)
        menu_screen.blit(button_exit, button_exit_rect)

        menu_screen.blit(play_text, play_text_rect)
        menu_screen.blit(exit_text, exit_text_rect)

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


def main():
    main_menu()

    global grid, nodes_dict, START, END
    grid = generate_random_grid()
    nodes_dict, console_grid = calculate_all_f_values(grid)

    selecting_start = True
    selecting_end = False

    while True:
        screen.fill(WHITE)
        draw_grid(grid, START, END)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = event.pos[1] // CELL_SIZE, event.pos[0] // CELL_SIZE
                if grid[row][col] != 5:
                    if selecting_start:
                        START = (row, col)
                        selecting_start = False
                        selecting_end = True
                    elif selecting_end:
                        END = (row, col)
                        selecting_end = False

        if not selecting_start and not selecting_end:
            nodes_dict, console_grid = calculate_all_f_values(grid)
            path = astar_algorithm(grid, START, END, nodes_dict, console_grid)
            if path:
                animate_path(path)
            else:
                print("\nNie znaleziono ścieżki")
            break

        pygame.display.flip()


if __name__ == "__main__":
    main()

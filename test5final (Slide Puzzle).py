import pygame
import sys
import random
import heapq

# Dimensions de la fenêtre
screen_width = 600
screen_height = 600

# Initialisation de Pygame
pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Puzzle Slide Game")
font = pygame.font.Font(None, 50)

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Choix de la taille de la grille
print("Choisissez la taille du puzzle :")
print("1. 8-puzzle (3x3)")
print("2. 15-puzzle (4x4)")
choice = input("Entrez votre choix (1 ou 2) : ")
grid_size = 3 if choice == '1' else 4

# Entrer la valeur de k
k = int(input("Entrez la valeur de k (nombre de déplacements avant un échange) : "))

# Calcul des dimensions des cases
tile_width = screen_width // grid_size
tile_height = screen_height // grid_size

# Fonction pour générer la grille
def generate_grid():
    tiles = list(range(1, grid_size * grid_size)) + [0]
    random.shuffle(tiles)
    return [tiles[i * grid_size:(i + 1) * grid_size] for i in range(grid_size)]

grid = generate_grid()

# Fonction pour dessiner la grille
def draw_grid(grid):
    for row in range(grid_size):
        for col in range(grid_size):
            tile_value = grid[row][col]
            x = col * tile_width
            y = row * tile_height
            if tile_value != 0:
                pygame.draw.rect(screen, GRAY, (x, y, tile_width, tile_height))
                text = font.render(str(tile_value), True, BLACK)
                text_rect = text.get_rect(center=(x + tile_width // 2, y + tile_height // 2))
                screen.blit(text, text_rect)
            pygame.draw.rect(screen, BLACK, (x, y, tile_width, tile_height), 2)

def find_empty_tile(grid):
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] == 0:
                return row, col

def swap_tiles(grid, pos1, pos2):
    if 0 <= pos1[0] < grid_size and 0 <= pos1[1] < grid_size and 0 <= pos2[0] < grid_size and 0 <= pos2[1] < grid_size:
        grid[pos1[0]][pos1[1]], grid[pos2[0]][pos2[1]] = grid[pos2[0]][pos2[1]], grid[pos1[0]][pos1[1]]

def check_win(grid):
    correct_order = list(range(1, grid_size * grid_size)) + [0]
    flattened_grid = sum(grid, [])
    return flattened_grid == correct_order

def manhattan_distance(state, goal):
    distance = 0
    for r in range(grid_size):
        for c in range(grid_size):
            value = state[r][c]
            if value == 0:
                continue
            goal_row, goal_col = divmod(goal.index(value), grid_size)
            distance += abs(r - goal_row) + abs(c - goal_col)
    return distance

def a_star_solver(initial_state):
    goal_state = list(range(1, grid_size * grid_size)) + [0]
    goal_state = [goal_state[i:i + grid_size] for i in range(0, len(goal_state), grid_size)]

    initial_state_flat = sum(initial_state, [])
    goal_state_flat = sum(goal_state, [])
    start_node = (initial_state, 0, manhattan_distance(initial_state, goal_state_flat), None)

    open_list = []
    heapq.heappush(open_list, start_node)

    closed_list = set()
    came_from = {}

    while open_list:
        current_state, g_cost, h_cost, parent = heapq.heappop(open_list)
        if current_state == goal_state:
            path = []
            while current_state is not None:
                path.append(current_state)
                current_state = came_from.get(tuple(map(tuple, current_state)))
            path.reverse()
            return path

        closed_list.add(tuple(map(tuple, current_state)))
        empty_row, empty_col = find_empty_tile(current_state)

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            new_row, new_col = empty_row + dx, empty_col + dy
            if 0 <= new_row < grid_size and 0 <= new_col < grid_size:
                new_state = [row[:] for row in current_state]
                swap_tiles(new_state, (empty_row, empty_col), (new_row, new_col))
                if tuple(map(tuple, new_state)) not in closed_list:
                    g_cost_new = g_cost + 1
                    h_cost_new = manhattan_distance(new_state, goal_state_flat)
                    heapq.heappush(open_list, (new_state, g_cost_new, h_cost_new, current_state))
                    came_from[tuple(map(tuple, new_state))] = current_state

    return []

running = True
move_count = 0
swap_mode = False
selected_tiles = []

while running:
    screen.fill(WHITE)
    draw_grid(grid)

    solver_button_rect = pygame.Rect(10, 10, 100, 50)
    pygame.draw.rect(screen, BLACK, solver_button_rect)
    solver_text = font.render("Solve", True, WHITE)
    screen.blit(solver_text, (solver_button_rect.centerx - solver_text.get_width() // 2, solver_button_rect.centery - solver_text.get_height() // 2))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if solver_button_rect.collidepoint(event.pos):
                print("Démarrage de la résolution...")
                solution_path = a_star_solver(grid)
                if solution_path:
                    for state in solution_path:
                        grid = state
                        screen.fill(WHITE)
                        draw_grid(grid)
                        pygame.display.flip()
                        pygame.time.wait(300)
                else:
                    print("Pas de solution trouvée.")

        elif event.type == pygame.KEYDOWN and not swap_mode:
            empty_row, empty_col = find_empty_tile(grid)
            moved = False
            if event.key == pygame.K_UP and empty_row < grid_size - 1:
                swap_tiles(grid, (empty_row, empty_col), (empty_row + 1, empty_col))
                moved = True
            elif event.key == pygame.K_DOWN and empty_row > 0:
                swap_tiles(grid, (empty_row, empty_col), (empty_row - 1, empty_col))
                moved = True
            elif event.key == pygame.K_LEFT and empty_col < grid_size - 1:
                swap_tiles(grid, (empty_row, empty_col), (empty_row, empty_col + 1))
                moved = True
            elif event.key == pygame.K_RIGHT and empty_col > 0:
                swap_tiles(grid, (empty_row, empty_col), (empty_row, empty_col - 1))
                moved = True

            if moved:
                move_count += 1
                if move_count >= k:
                    swap_mode = True
                    print("Mode permutation activé.")

        elif event.type == pygame.MOUSEBUTTONDOWN and swap_mode:
            x, y = event.pos
            col = x // tile_width
            row = y // tile_height
            selected_tiles.append((row, col))
            if len(selected_tiles) == 2:
                swap_tiles(grid, selected_tiles[0], selected_tiles[1])
                selected_tiles = []
                swap_mode = False
                move_count = 0
                print("Permutation effectuée.")

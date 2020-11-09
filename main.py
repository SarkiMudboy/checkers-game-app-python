import pygame
import os

pygame.font.init()
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (186, 85, 211)
TEAL = (0, 128, 128)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WIDTH, HEIGHT = (550, 800)
PLAY_WIDTH, PLAY_HEIGHT = (350, 550)
block_size = 50
top_left_x = 100
top_left_y = 100
PIECES = []
MOD_LIST = []
n = 0
BG = pygame.transform.scale(pygame.image.load(os.path.join('background.png')), (WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')
player_1 = None
player_2 = None
game_started = False


class Piece:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 21
        self.draw(surface=win)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def click(self, position_x, position_y):
        if (self.x - block_size/2) <= position_x <= (self.x + block_size/2) and (self.y - block_size/2) <= position_y <= (self.y + block_size/2):
            return self.x - block_size/2, self.y - block_size/2
        else:
            return False

    def type(self):
        return self.color


def highlight(p1, p2, color):
    mat_list = matrix_list()
    for index, item in enumerate(mat_list):
        for inner_index, c in enumerate(item):
            if top_left_x + inner_index*block_size <= p1 <= (top_left_x + inner_index*block_size) + block_size and top_left_y + index*block_size <= p2 <= (top_left_y + index*block_size) + block_size:
                pygame.draw.rect(win, color, (top_left_x + inner_index*block_size, top_left_y + index*block_size, block_size, block_size), 4)


def get_pos(x, y, isPiece):
    dist_x = abs(x - (WIDTH / 2 - PLAY_WIDTH / 2))
    dist_y = abs(y - (HEIGHT / 2 - PLAY_HEIGHT / 2))
    if isPiece:
        column = int(dist_x / block_size)
    else:
        column = round(dist_x / block_size)
    row = round(dist_y / block_size)
    return row, column


def check_error_indexing(test_value):
    test_list = [i for i in range(50, 1000, 100)]
    if test_value in test_list:
        return True
    else:
        return False


def is_winning_move(pos1, pos2, pos3, pos4, error_check):
    global PIECES, MOD_LIST
    winning_move = False
    if error_check:
        p1 = pos1 + 1
    else:
        p1 = pos1
    instances = [p1 + 2 == pos3, p1 - 2 == pos3, pos2 + 2 == pos4, pos2 - 2 == pos4]
    piece_position = [(p1 + 1, pos2 + 1), (p1 - 1, pos2 - 1), (p1 + 1, pos2 - 1), (p1 - 1, pos2 + 1)]
    if instances[0] or instances[1] and instances[2] or instances[3]:
        for p in PIECES:
            g = get_pos(p.x, p.y, True)
            if g in piece_position:
                PIECES.remove(p)
                MOD_LIST[g[0]][g[1]] = 1
                winning_move = True
        return winning_move
    else:
        return False


def is_valid_move(init_pos, final_pos):

    error = False

    if check_error_indexing(init_pos[1]):
        error = True

    valid_distance = False
    r1, c1 = get_pos(init_pos[0], init_pos[1], False)
    r2, c2 = get_pos(final_pos[0], final_pos[1], False)
    won = is_winning_move(r1, c1, r2, c2, error)

    if won:
        return won
    else:
        instances = [r1 + 1 == r2, r1 - 1 == r2, c1 + 1 == c2, c1 - 1 == c2]
        if error:
            if (r1+1) + 1 == r2 or (r1+1) - 1 == r2 and c1 + 1 == c2 or c1 - 1 == c2:
                valid_distance = True
        else:
            if instances[0] or instances[1] and instances[2] or instances[3]:
                valid_distance = True
        if game_started:
            value = MOD_LIST[r2][c2]
        else:
            value = matrix_list()[r2][c2]
        if valid_distance:
            if value == 1:
                return valid_distance
            else:
                return not valid_distance
        else:
            return False


def check_play(piece, x, y, pos_x, pos_y):
    global n, MOD_LIST
    if n == 0:
        mat_list = arrange_piece()
        n += 1
    else:
        mat_list = MOD_LIST
    r2, c2 = get_pos(pos_x, pos_y, False)
    r1, c1 = get_pos(x, y, False)
    if check_error_indexing(y):
        mat_list[r1 + 1][c1] = 1
    else:
        mat_list[r1][c1] = 1
    mat_list[r2][c2] = piece
    MOD_LIST = mat_list
    return MOD_LIST


def matrix_list():
    col = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    mat_list = []
    for i in col:
        if i == 0:
            inner_list = [x % 2 for x in range(i, 7)]
        else:
            inner_list = [x % 2 for x in range(i, 8)]
        mat_list.append(inner_list)
    return mat_list


def re_arrange_piece(data):
    global PIECES
    mat_list = data
    pieces = []
    for i, l in enumerate(mat_list):
        for p, n in enumerate(l):
            if n == 'piece1':
                x, y = ((top_left_x + p * block_size) + block_size / 2, (top_left_y + i * block_size) + block_size / 2)
                piece = Piece(x, y, TEAL)
                pieces.append(piece)
            elif n == 'piece2':
                x, y = ((top_left_x + p * block_size) + block_size / 2, (top_left_y + i * block_size) + block_size / 2)
                piece = Piece(x, y, PURPLE)
                pieces.append(piece)
    PIECES = pieces
    return mat_list


def arrange_piece():
    mat_list = matrix_list()
    for i, l in enumerate(mat_list):
        if i in [0, 1, 2, 3]:
            for p, n in enumerate(l):
                if n == 1:
                    mat_list[i][p] = 'piece1'
                else:
                    pass
        elif i in [7, 8, 9, 10]:
            for p, n in enumerate(l):
                if n == 1:
                    mat_list[i][p] = 'piece2'
                else:
                    pass
    return mat_list


def handle_click(event):
    global game_started
    clicked = False
    if event.type == pygame.MOUSEBUTTONDOWN:
        pos = event.pos
        for p in set(PIECES):
            if p.click(pos[0], pos[1]):
                position = p.click(pos[0], pos[1])
                clicked = True
                if p.type() == PURPLE:
                    piece = 'piece2'
                else:
                    piece = 'piece1'
    while clicked:
        for event in pygame.event.get():
            highlight(pos[0], pos[1], BLACK)
            if event.type == pygame.MOUSEBUTTONDOWN:
                new_pos = event.pos
                if is_valid_move(position, new_pos):
                    data = check_play(piece, position[0], position[1], new_pos[0], new_pos[1])
                    re_arrange_piece(data)
                    pygame.display.update()
                    game_started = True
                    clicked = False
                else:
                    clicked = False
            else:
                continue


def draw_board():
    mat_list = matrix_list()
    for i, l in enumerate(mat_list):
        for p, n in enumerate(l):
            if n == 1:
                mat_list[i][p] = WHITE
            else:
                mat_list[i][p] = BLACK

    for index, item in enumerate(mat_list):
        for inner_index, color in enumerate(item):
            pygame.draw.rect(win, color, (top_left_x + inner_index*block_size, top_left_y + index*block_size, block_size, block_size))

    pygame.draw.rect(win, RED, (top_left_x, top_left_y, PLAY_WIDTH, PLAY_HEIGHT), 2)


def redraw_window(surface):
    global game_started
    surface.blit(BG, (0, 0))
    draw_board()
    if not game_started:
        re_arrange_piece(arrange_piece())
    else:
        re_arrange_piece(MOD_LIST)
    pygame.display.update()


def main():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEMOTION:
                posx = event.pos[0]
                posy = event.pos[1]
                highlight(posx, posy, GREEN)
            handle_click(event)
        pygame.display.update()
        redraw_window(win)


main()

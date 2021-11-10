import pygame
import os
import math

os.environ["SDL_VIDEO_CENTERED"] = "1"

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('monospace', 40, 3)
font2 = pygame.font.SysFont('comicsans', 19)
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
player_id = 0
win_data = [0, 0]
is_multiple = False
multiple_asset = []
multiple_stash = {'knocked pieces': [],
                  'winning slots': [],
                  'init_pos': (),
                  'drift': (),
                  'instant_drift': (),
                  'instant-pos': ()}
BG = pygame.transform.scale(pygame.image.load(os.path.join('background.jpg')), (WIDTH, HEIGHT))
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')
game_started = False
checkmate = [False, None]


class Player:
    def __init__(self, id_num, score, piece):
        self.id = id_num
        self.score = score
        self.piece = piece
        self.floating = False
        self.piece_is_king = False


class Piece:
    def __init__(self, x, y, color, piece_type, is_king=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 21
        self.is_king = is_king
        self.piece_type = piece_type
        self.draw(surface=win)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def click(self, position_x, position_y):
        if (self.x - block_size / 2) <= position_x <= (self.x + block_size / 2) and (self.y - block_size / 2) <= position_y <= (self.y + block_size / 2):
            return self.x - block_size / 2, self.y - block_size / 2
        else:
            return False

    def type(self):
        return self.color


def reset_asset(player):
    global multiple_asset, multiple_stash
    player.floating = False
    multiple_asset = []
    multiple_stash = {'knocked pieces': [],
                      'winning slots': [],
                      'init_pos': (),
                      'drift': (),
                      'instant_drift': (),
                      'instant-pos': ()}


def reset_global_var():
    global game_started, win_data, checkmate, player_id, n
    game_started = False
    win_data = [0, 0]
    checkmate = [False, None]
    player_id = 0
    n = 0


def highlight(p1, p2, color):
    mat_list = matrix_list()
    for index, item in enumerate(mat_list):
        for inner_index, c in enumerate(item):
            if top_left_x + inner_index * block_size <= p1 <= (
                    top_left_x + inner_index * block_size) + block_size and top_left_y + index * block_size <= p2 <= (
                    top_left_y + index * block_size) + block_size:
                pygame.draw.rect(win, color, (
                top_left_x + inner_index * block_size, top_left_y + index * block_size, block_size, block_size), 4)


def get_pos(x, y):
    ORIGIN = (top_left_x - 2, top_left_y - 2)
    dist_x = x - ORIGIN[0]
    dist_y = y - ORIGIN[1]
    column = int(dist_x / block_size)
    row = int(dist_y / block_size)
    return row, column


def check_checkmate():
    global checkmate
    piece_1 = []
    piece_2 = []

    winner = ['Player 2', 'Player 1']

    for p in PIECES:
        if p.piece_type == 'piece1' or p.piece_type == 'piece1k':
            piece_1.append(p)
        else:
            piece_2.append(p)

    check_loser = (len(piece_1), len(piece_2))
    if 0 in check_loser:
        checkmate[1] = f'{winner[check_loser.index(0)]} wins!'
        checkmate[0] = True


def is_winning_move(pos1, pos2, pos3, pos4, diagonal, player):
    global PIECES, MOD_LIST
    winning_move = False
    init_piece_type = None
    piece_position = ((pos1 + pos3) / 2, (pos2 + pos4) / 2)

    for p in PIECES:
        if get_pos(p.x, p.y) == (pos1, pos2):
            init_piece_type = p.type()

    if diagonal == 2:
        for p in PIECES:
            g = get_pos(p.x, p.y)
            if abs(pos1 - g[0]) == 1 and p.type() != init_piece_type and g == piece_position:
                MOD_LIST[g[0]][g[1]] = 1
                winning_move = True
        return winning_move
    else:
        return False


def is_valid_move(init_pos, final_pos, player):
    r1, c1 = get_pos(init_pos[0], init_pos[1])
    r2, c2 = get_pos(final_pos[0], final_pos[1])
    pp = [r1 - r2, c1 - c2]
    if pp[1] != 0:
        dist = pp[0] / pp[1]
    diagonal = abs(pp[0])

    valid_distance = abs(int(math.atan(dist) * 57.296)) == 45 and diagonal in (1, 2)

    if valid_distance:
        won = is_winning_move(r1, c1, r2, c2, diagonal, player)
        if won:
            player.score += 1
            win_data[player.id] = player.score
            return won
        elif (player.id == 0 and pp[0] < 0 or player_id == 1 and pp[0] > 0) and diagonal == 1:
            if game_started:
                value = MOD_LIST[r2][c2]
            else:
                value = matrix_list()[r2][c2]
            if value == 1:
                return valid_distance
            else:
                return not valid_distance
    else:
        return False


def check_play(player, pos1, pos2):
    global n, MOD_LIST
    if n == 0:
        mat_list = arrange_piece()
        n += 1
    else:
        mat_list = MOD_LIST
    r2, c2 = get_pos(pos2[0], pos2[1])
    r1, c1 = get_pos(pos1[0], pos1[1])

    mat_list[r1][c1] = 1
    if (r2, c2) in [(0, i) for i in range(0, 7)] or (r2, c2) in [(0, i) for i in range(10, 7)]:
        mat_list[r2][c2] = player.piece[2]
    else:
        mat_list[r2][c2] = player.piece[1]

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

    def crowning(p):
        p.is_king = True
        return p

    def create_piece(n):
        values = {'piece1': TEAL,
                  'piece2': PURPLE,
                  'piece1k': TEAL,
                  'piece2k': PURPLE}
        x, y = ((top_left_x + p * block_size) + block_size / 2, (top_left_y + i * block_size) + block_size / 2)
        piece = Piece(x, y, values[n], n)
        return piece

    for i, l in enumerate(mat_list):
        for p, n in enumerate(l):
            if n == 'piece1k' or n == 'piece2k':
                pieces.append(crowning(create_piece(n)))
            elif n == 'piece1' or n == 'piece2':
                pieces.append(create_piece(n))

    PIECES = pieces
    check_checkmate()
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


def handle_click(pos1, player, multiple_play):
    global game_started, MOD_LIST, multiple_asset, is_multiple, multiple_stash
    clicked = False

    for p in set(PIECES):
        if p.click(pos1[0], pos1[1]) and p.type() == player.piece[0]:
            player.piece_position = p.click(pos1[0], pos1[1])
            player.p = p
            if p.is_king:
                is_multiple = True
                multiple_play = True

    if multiple_play:
        x, y = get_pos(player.piece_position[0], player.piece_position[1])
        MOD_LIST[x][y] = 1
        multiple_asset = player
        multiple_stash['init_pos'] = (x, y)
        multiple_stash['drift'] = pos1
        redraw_window(win)
    else:
        clicked = True

    while clicked:
        for event in pygame.event.get():
            highlight(pos1[0], pos1[1], BLACK)
            if event.type == pygame.MOUSEBUTTONDOWN:
                new_pos = event.pos
                if is_valid_move(player.piece_position, new_pos, player):
                    data = check_play(player, player.piece_position, new_pos)
                    re_arrange_piece(data)
                    pygame.display.update()
                    flipPlayer(player)
                    game_started = True
                    clicked = False
                else:
                    clicked = False
            else:
                continue


def handle_multiple(ip, asset):
    global multiple_asset, multiple_stash
    r, c = get_pos(asset.piece_position[0], asset.piece_position[1])
    peasants = []
    data = None

    def check_possible_moves(player_asset):
        pr_temp = []
        rects1 = [(r + 2, c + 2), (r - 2, c + 2), (r + 2, c - 2), (r - 2, c - 2)]
        rects2 = [(r + 1, c + 1), (r - 1, c + 1), (r + 1, c - 1), (r - 1, c - 1)]

        filtered_rect1 = list(filter(lambda x: x[0] < 11 and x[1] < 7, rects1))
        filtered_rect2 = list(filter(lambda x: x[0] < 11 and x[1] < 7, rects2))

        if player_asset.floating:
            rects = list(zip(filtered_rect1, filtered_rect2))
        else:
            rects = list(zip(rects1, rects2))

        for i in rects:
            if MOD_LIST[i[0][0]][i[0][1]] == 1 and MOD_LIST[i[1][0]][i[1][1]] != player_asset.piece[1] and \
                    MOD_LIST[i[1][0]][i[1][1]] != 1:
                highlight((top_left_x + i[0][1] * block_size) + 2, (top_left_y + i[0][0] * block_size) + 2, RED)
                pr_temp.append(
                    pygame.Rect((top_left_x + i[0][1] * block_size) + 2, (top_left_y + i[0][0] * block_size) + 2,
                                block_size, block_size))

        return pr_temp

    def drift_direction(var_row, var_column):
        drift = None
        dr = []

        def retrieve(direction, pos1, pos2):
            if direction == 'down-right':
                return pos1 + 1, pos2 + 1
            elif direction == 'down-left':
                return pos1 + 1, pos2 - 1
            elif direction == 'top-right':
                return pos1 - 1, pos2 + 1
            elif direction == 'top-left':
                return pos1 - 1, pos2 - 1

        if multiple_stash['drift'][0] < ip[0] and multiple_stash['drift'][1] < ip[1]:
            drift = var_row + 1, var_column + 1
            dr = 'down-right'
        elif multiple_stash['drift'][0] > ip[0] and multiple_stash['drift'][1] < ip[1]:
            drift = var_row + 1, var_column - 1
            dr = 'down-left'
        elif multiple_stash['drift'][0] < ip[0] and multiple_stash['drift'][1] > ip[1]:
            drift = var_row - 1, var_column + 1
            dr = 'top-right'
        elif multiple_stash['drift'][0] > ip[0] and multiple_stash['drift'][1] > ip[1]:
            drift = var_row - 1, var_column - 1
            dr = 'top-left'

        multiple_stash['drift'] = ip
        if drift:
            multiple_stash['instant_drift'] = dr
            return drift
        else:
            return retrieve(multiple_stash['instant_drift'], var_row, var_column)

    def slope(pos1, pos2):
        slopes = []

        for row, i in enumerate(MOD_LIST):
            for column, element in enumerate(i):
                if (pos2 - column) != 0 and (pos1 - row) != 0:
                    angle = (45, 135)
                    delta = abs(int(math.atan2(pos2 - column, pos1 - row) / math.pi * 180)) in angle
                    if delta:
                        slopes.append(
                            pygame.Rect((top_left_x + column * block_size) + 2, (top_left_y + row * block_size) + 2,
                                        block_size, block_size))

        return slopes

    if asset.p.is_king:

        multiple_stash['winning slots'] = slope(r, c)
        multiple_stash['winning slots'].append(
            pygame.Rect((top_left_x + c * block_size) + 2, (top_left_y + r * block_size) + 2, block_size, block_size))

        for rect in multiple_stash['winning slots']:
            for p in PIECES:
                if rect.collidepoint(p.x, p.y) and p.type() != asset.p.type():
                    rows, columns = get_pos(p.x, p.y)
                    drift_index = drift_direction(rows, columns)
                    if drift_index and drift_index[1] != 7:
                        data = drift_index
                    if data and MOD_LIST[data[0]][data[1]] == 1:
                        peasants_rect = (pygame.Rect((top_left_x + data[1] * block_size) + 2,
                                                     (top_left_y + data[0] * block_size) + 2, block_size, block_size))
                        peasants.append((p, peasants_rect))
                        highlight((top_left_x + data[1] * block_size) + 2, (top_left_y + data[0] * block_size) + 2, RED)

        if peasants:
            for item in peasants:
                if item[1].collidepoint(ip[0], ip[1]):
                    p1, p2 = get_pos(item[0].x, item[0].y)
                    MOD_LIST[p1][p2] = 1
                    multiple_stash['knocked pieces'].append((item[0], (p1, p2)))
                    x, y = get_pos(item[1].left, item[1].top)
                    multiple_stash['instant-pos'] = x, y

            inst = multiple_stash['instant-pos']
            if inst and inst != (r, c):
                squares = slope(r, c)
                for square in squares:
                    if square.collidepoint(ip[0], ip[1]):
                        multiple_asset.piece_position = (square.left, square.top)

    else:
        possible_rects = check_possible_moves(asset)

        if possible_rects:
            multiple_stash['winning slots'] = possible_rects
            for rct in possible_rects:
                if rct.collidepoint(ip[0], ip[1]):
                    r1, c1 = get_pos(ip[0], ip[1])
                    piece_position = int((r + r1) / 2), int((c + c1) / 2)
                    for p in PIECES:
                        if piece_position == get_pos(p.x, p.y):
                            MOD_LIST[piece_position[0]][piece_position[1]] = 1
                            multiple_stash['knocked pieces'].append((p, piece_position))
                            asset.score += 1
                            win_data[asset.id] = asset.score
                    multiple_asset.floating = True
                    multiple_asset.piece_position = (rct.left, rct.top)

    asset.p.x = ip[0]
    asset.p.y = ip[1]
    asset.p.draw(win)
    pygame.display.update()


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
            pygame.draw.rect(win, color, (
            top_left_x + inner_index * block_size, top_left_y + index * block_size, block_size, block_size))

    pygame.draw.rect(win, RED, (top_left_x, top_left_y, PLAY_WIDTH, PLAY_HEIGHT), 2)


def redraw_window(surface):
    global game_started
    label = font.render('Checkers', 1, GREEN)
    score0 = font2.render(f'player1: {win_data[0]}', 1, WHITE)
    score1 = font2.render(f'player2: {win_data[1]}', 1, WHITE)
    player1_label = font2.render('player 1', 1, TEAL)
    player2_label = font2.render('player 2', 1, PURPLE)
    surface.blit(BG, (0, 0))
    surface.blit(label, (WIDTH / 2 - label.get_width() / 2, 20))
    draw_board()
    if not game_started:
        re_arrange_piece(arrange_piece())
    else:
        re_arrange_piece(MOD_LIST)
    surface.blit(player1_label, (15, 150))
    surface.blit(player2_label, (15, 550))
    pygame.draw.circle(surface, PURPLE, (31, 40), 17)
    pygame.draw.circle(surface, TEAL, (519, 40), 17)
    surface.blit(score0, (10, 60))
    surface.blit(score1, (WIDTH - (score1.get_width() + 10), 60))
    player_label = [player1_label.get_width(), player1_label.get_height(), player2_label.get_width(),
                    player2_label.get_height()]
    if player_id == 0:
        pygame.draw.rect(surface, RED, (10, 145, player_label[0] + 10, player_label[1] + 10), 2)
    else:
        pygame.draw.rect(surface, RED, (10, 545, player_label[2] + 10, player_label[3] + 10), 2)

    if checkmate[0]:
        checkmate_label = font.render(checkmate[1], 1, RED)
        surface.blit(checkmate_label,
                     (WIDTH / 2 - checkmate_label.get_width() / 2, HEIGHT / 2 - checkmate_label.get_height() / 2))
        pygame.display.update()
        pygame.time.delay(3000)
        reset_global_var()

    pygame.display.update()


def flipPlayer(current_player):
    global player_id
    player_id = (current_player.id + 1) % 2


def main():
    global is_multiple, MOD_LIST
    run = True
    locked_in = False
    clock = pygame.time.Clock()
    player_1 = Player(0, 0, (TEAL, 'piece1', 'piece1k'))
    player_2 = Player(1, 0, (PURPLE, 'piece2', 'piece2k'))

    while run:
        clock.tick(60)

        if player_id == 0:
            player = player_1
        else:
            player = player_2

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEMOTION:
                if locked_in:
                    inst_pos = pygame.mouse.get_pos()
                    handle_multiple(inst_pos, multiple_asset)
                else:
                    posx = pygame.mouse.get_pos()[0]
                    posy = pygame.mouse.get_pos()[1]
                    highlight(posx, posy, GREEN)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    is_multiple = True
                if event.key == pygame.K_q:
                    max_score = max(win_data[0], win_data[1])
                    winner = win_data.index(max_score) + 1
                    win_label = font.render(f'Player{winner} won!', 1, RED)
                    win.blit(win_label,
                             (WIDTH / 2 - win_label.get_width() / 2, HEIGHT / 2 - win_label.get_height() / 2))
                    pygame.display.update()
                    pygame.time.delay(3000)
                    reset_global_var()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                handle_click(pos, player, is_multiple)
                if is_multiple:
                    locked_in = True
            if event.type == pygame.MOUSEBUTTONUP:
                test_point = event.pos
                x, y = get_pos(test_point[0], test_point[1])
                if is_multiple:
                    for rct in multiple_stash['winning slots']:
                        if rct.collidepoint(test_point):
                            MOD_LIST[x][y] = multiple_asset.piece[1]
                            flipPlayer(player)
                    if MOD_LIST[x][y] == 1:
                        for piece in multiple_stash['knocked pieces']:
                            row, column = piece[1][0], piece[1][1]
                            MOD_LIST[row][column] = piece[0].piece_type
                            player.score -= 1
                            win_data[player.id] = player.score
                        init_x, init_y = multiple_stash['init_pos'][0], multiple_stash['init_pos'][1]
                        MOD_LIST[init_x][init_y] = player.piece[1]
                        flipPlayer(player)
                    reset_asset(player)
                    is_multiple = False
                    locked_in = False
        pygame.display.update()
        redraw_window(win)


def main_menu():
    run = True
    clock = pygame.time.Clock()

    while run:

        clock.tick(60)
        win.fill((0, 0, 0))
        menu_label = font.render('Lets Play Checkers', 1, GREEN)
        win.blit(menu_label, (WIDTH / 2 - menu_label.get_width() / 2, HEIGHT / 2 - menu_label.get_height() / 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main()


main_menu()

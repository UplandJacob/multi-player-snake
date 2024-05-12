import pygame
import random
import sys
import time
import numpy as np
import threading

pygame.init()

WIDTH, HEIGHT = 750, 750
BACKGROUND_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
TEXT_COLOR = (255, 255, 255)
SNAKE_SIZE = 15
START_POSITION = [WIDTH / 2, HEIGHT / 2]
BOARD_POSITION = [0, 40]
TOP_BAR_COLOR = (100, 100, 100)
FPS = 10

PLAYER_CONTROLS = [ # up, down, left, right
    [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
    [pygame.K_w, pygame.K_s , pygame.K_a, pygame.K_d]
]
PLAYER_COLORS = [(0, 255, 0), (255, 255, 0)]

FOOD_COLORS = [
    ["normal", (255, 0, 0)],
    ["speed", (0, 0, 255)]
]




def generate_positions(width, height, num_points):
    # Calculate the number of points along each axis
    num_points_x = int(np.sqrt(num_points * width / height))
    num_points_y = int(num_points / num_points_x)

    # Generate evenly spaced points along each axis
    x_positions = np.linspace(width/(num_points_x*2), width, num_points_x, endpoint=False)
    y_positions = np.linspace(height/(num_points_y*2), height, num_points_y, endpoint=False)

    # Create a grid of points
    xx, yy = np.meshgrid(x_positions, y_positions)
    points = np.vstack([xx.ravel(), yy.ravel()]).T

    return points.tolist()


class Board:
    def __init__(self, width=750, height=750, num_of_players=1, start_x=0, start_y=0, player_controls=[[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]]):
        self.snakes = []
        self.score = 0
        self.foods = []
        self.timers = []
        self.late_food_gen = False
        self.players = []
        self.current_fps = FPS
        self.width = width
        self.height = height
        for player in range(num_of_players):
            self.players.append({
                "player": player,
                "controls": player_controls[player],
                "can_move": True,
                "move": None,
                "score": 0
            })

    def loop(self):
        alive = True
        while alive:
            screen.fill(BACKGROUND_COLOR)
            self.update_timers()
            self.process_events()

            for snk in self.snakes:
                snk.move()
                snk.draw()
            self.update_foods()
            self.draw_foods()

            pygame.draw.rect(screen, TOP_BAR_COLOR, pygame.Rect(0, 0, WIDTH, BOARD_POSITION[1]))  # top bar
            font = pygame.font.Font(None, 36)
            text = font.render("Score: "+str(self.score), True, TEXT_COLOR)
            text_rect = text.get_rect(center = (60, 20))
            screen.blit(text, text_rect)

            pygame.display.update()
            if self.is_game_over():
                print('game over')
                alive = False
            pygame.time.Clock().tick(self.current_fps)
            for p in self.players:
                p['can_move'] = True

    def is_game_over(self):
        over = []
        for snki in range(len(self.snakes)): # for each snake on board
            for snk2i in range(len(self.snakes)): # check if it is colliding with another snake
                if snki != snk2i and self.snakes[snki].position[0] in self.snakes[snk2i].position:
                    over.append(snk2i) # snake that got ran into loses
                    print('into another snake')
            if self.snakes[snki].position[0] in self.snakes[snki].position[1:]: over.append(snki);  print('into itself') # if is is colliding with itself
            if self.snakes[snki].position[0][0] not in range(0, WIDTH, SNAKE_SIZE) or \
               self.snakes[snki].position[0][1] not in range(0, HEIGHT, SNAKE_SIZE):
                over.append(snki)
                print('wall')
        return over

    def start_screen(self):
        font = pygame.font.Font(None, 36)
        text = font.render("Press any key to start", True, TEXT_COLOR)
        text_rect = text.get_rect(center = (WIDTH / 2, HEIGHT / 2))
        if self.score:
            txt = font.render("Score: "+str(self.score), True, TEXT_COLOR)
            txt_rect = txt.get_rect(center = (WIDTH / 2, HEIGHT / 2 - 40))
        
        self.snakes = []
        positions = generate_positions(self.width/SNAKE_SIZE, self.height/SNAKE_SIZE, len(self.players))
        print(positions)
        for player in range(len(self.players)):
            self.snakes.append(Snake([int(positions[player][0])*SNAKE_SIZE, int(positions[player][1])*SNAKE_SIZE]))
        waiting = True
        while waiting:
            screen.fill(BACKGROUND_COLOR)
            screen.blit(text, text_rect)
            if self.score: screen.blit(txt, txt_rect)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    offset = [0, 0]
                    for pi in range(len(self.players)):
                        if event.key in self.players[pi]['controls']:
                            if event.key == self.players[pi]['controls'][0]:
                                offset = [0, -SNAKE_SIZE]
                                self.snakes[pi].speed = offset
                            elif event.key == self.players[pi]['controls'][1]:
                                offset = [0, SNAKE_SIZE]
                                self.snakes[pi].speed = offset
                            elif event.key == self.players[pi]['controls'][2]:
                                offset = [-SNAKE_SIZE, 0]
                                self.snakes[pi].speed = offset
                            elif event.key == self.players[pi]['controls'][3]:
                                offset = [SNAKE_SIZE, 0]
                                self.snakes[pi].speed = offset
                    print(offset)
                    if offset != [0, 0]:
                        for pi in range(len(self.players)):
                            self.snakes[pi].position.append([self.snakes[pi].position[0][0]+offset[0], self.snakes[pi].position[0][1]+offset[1]])
                            self.snakes[pi].speed = offset
                        waiting = False
        # bofore gal=me start
        self.foods = [self.get_new_food_location()]
        self.score = 0
        self.late_food_gen = False
        self.timers = []
        # start
        self.loop()
        # on game over
        self.current_FPS = FPS
        self.foods = []
        self.start_screen()

    def get_new_food_location(self):
        location = []; occupied_squares = [];
        for snake in self.snakes:
            for position in snake.position:
                occupied_squares.append(position)

        if len(occupied_squares) + len(self.foods) >= WIDTH/20 * HEIGHT/20 / 2:
            self.late_food_gen = True
        
        if not self.late_food_gen:
            location = [random.randrange(0, WIDTH, SNAKE_SIZE), random.randrange(0, HEIGHT, SNAKE_SIZE)]
            print(location)
            bad = False
            if location in occupied_squares: bad == True; print("food can't be at", location)
            # for position in snake.position:
            #     if position == location:
            #         print("food can't be at", location)
            #         bad = True
            #         break
            if location in self.foods: bad == True; print("food can't be at", location)
            # for position in self.foods:
            #     if position == location:
            #         print("food can't be at", location)
            #         bad = True
            #         break

            if bad:
                location = self.get_new_food_location()
        else: 
            self.foods.sort(); open_squares = []; 

            for x in range(0, WIDTH, 20): 
                for y in range(0, HEIGHT, 20):
                    good = True
                    if not [x, y] in occupied_squares:
                        open_squares.append([x, y])
                    # for pos in snake.position:
                    #     if pos[0] == x or pos[1] != y:
                    #         good = False
                    # for food in self.foods:
                    #     if food[0] == x or food[1] != y:
                    #         good = False
                    # if good:
                    #     print("good", [x, y])
                    #     open_squares.append([x, y])
            # print("open_squares", open_squares)
            rand_num = random.randint(0, len(open_squares) - 1)
            location = open_squares[rand_num]
        
        modifiers = []
        if random.randint(0, 100) <= 50:
            modifiers.append("speed")
        location.append(modifiers)
        print(location)
        return location

    def update_foods(self):
        for snake in self.snakes:
            for food in self.foods:
                if snake.position[0] == [food[0], food[1]]:
                    self.foods.remove(food)
                    self.score += 1
                    print("score: "+str(self.score))
                    ############ Food effects ############
                    if "speed" in food[2]:
                        self.current_FPS = FPS*2 # speed: 2x multiplier
                        self.set_timer('speed', 10) # 10 seconds

                    self.foods.append(self.get_new_food_location())
                    # foods.append(self.get_new_food_location())
                    snake.position.append(snake.last_position)

    def draw_foods(self):
        for food in self.foods:
            color = FOOD_COLOR
            if "speed" in food[2]:
                color = self.get_food_color("speed")
            pygame.draw.rect(screen, color, pygame.Rect(food[0]+BOARD_POSITION[0], food[1]+BOARD_POSITION[1], SNAKE_SIZE, SNAKE_SIZE))

    def get_food_color(self, mod):
        for i in FOOD_COLORS:
            if mod in i: return i[1]

    def set_timer(self, name, seconds): self.timers.append([name, time.time(), seconds])

    def update_timers(self):
        for timer in self.timers: 
            if "speed" in timer[0] and timer[1] + timer[2] <= time.time(): 
                self.timers.remove(timer); self.current_FPS = FPS # end speed
        else:
            self.current_FPS = FPS*2

    
    def process_events(self):
        # possible cached move from last tick
        for pi in range(len(self.players)):
            move = self.players[pi]['move']
            if move:
                if   move.key == self.players[pi]['controls'][0]:
                    self.snakes[pi].speed = [0, -SNAKE_SIZE]; # up
                elif move.key == self.players[pi]['controls'][1]:
                    self.snakes[pi].speed = [0, SNAKE_SIZE];  # down
                elif move.key == self.players[pi]['controls'][2]:
                    self.snakes[pi].speed = [-SNAKE_SIZE, 0]; # left
                elif move.key == self.players[pi]['controls'][3]:
                    self.snakes[pi].speed = [SNAKE_SIZE, 0];  # right
                self.players[pi]['can_move'] = True
                self.players[pi]['move'] = None
        
        # other events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                for pi in range(len(self.players)):
                    if self.players[pi]['can_move']: 
                        if   event.key == self.players[pi]['controls'][0] and self.snakes[pi].speed != [0, SNAKE_SIZE]:
                            self.snakes[pi].speed = [0, -SNAKE_SIZE]; self.players[pi]['can_move'] = False # up
                        elif event.key == self.players[pi]['controls'][1] and self.snakes[pi].speed != [0, -SNAKE_SIZE]:
                            self.snakes[pi].speed = [0, SNAKE_SIZE];  self.players[pi]['can_move'] = False # down
                        elif event.key == self.players[pi]['controls'][2] and self.snakes[pi].speed != [SNAKE_SIZE, 0]:
                            self.snakes[pi].speed = [-SNAKE_SIZE, 0]; self.players[pi]['can_move'] = False # left
                        elif event.key == self.players[pi]['controls'][3] and self.snakes[pi].speed != [-SNAKE_SIZE, 0]:
                            self.snakes[pi].speed = [SNAKE_SIZE, 0];  self.players[pi]['can_move'] = False # right
                    else:
                        self.players[pi]['move'] = event



class Snake:
    def __init__(self, start_position=START_POSITION):
        self.position = [start_position]
        self.speed = [0, 0]
        self.last_position = []

    def move(self):
        tail = self.position[-1]
        self.position = [[self.position[0][0] + self.speed[0], self.position[0][1] + self.speed[1]]] + self.position[:-1]
        self.last_position = self.position[len(self.position) - 1]
        return tail
    
    def draw(self):
        for position in self.position:
            pygame.draw.rect(screen, SNAKE_COLOR, pygame.Rect(position[0]+BOARD_POSITION[0], position[1]+BOARD_POSITION[1], SNAKE_SIZE, SNAKE_SIZE))
    
    

screen = pygame.display.set_mode((WIDTH+BOARD_POSITION[0], HEIGHT+BOARD_POSITION[1]))
#start_screen(snake)
#foods = [get_new_food_location(snake)]
BOARDS = []
BOARDS.append(Board(WIDTH, HEIGHT, 2, 0, 0, PLAYER_CONTROLS))
for board in BOARDS:
        #threading.Thread(target=board.start_screen).start()
        board.start_screen()
# while True:
#     screen.fill(BACKGROUND_COLOR)
#     for board in BOARDS:
#         #threading.Thread(target=board.loop).start()
#         board.loop()



# while True:
#     screen.fill(BACKGROUND_COLOR)
#     update_timers()
#     process_events(snake)

#     tail = snake.move()
#     snake.draw()
#     update_foods(snake)
#     draw_foods()

#     pygame.draw.rect(screen, TOP_BAR_COLOR, pygame.Rect(0, 0, WIDTH, BOARD_POSITION[1]))  # top bar
#     font = pygame.font.Font(None, 36)
#     text = font.render("Score: "+str(score), True, TEXT_COLOR)
#     text_rect = text.get_rect(center = (60, 20))
#     screen.blit(text, text_rect)

#     pygame.display.update()
#     if is_game_over(snake):
#         print('game over')
#         snake = Snake()
#         start_screen(snake, score=score)
#         score = 0
#         current_FPS = FPS
#         late_food_gen = False
#         timers = []
#         foods = [get_new_food_location(snake)]
#     pygame.time.Clock().tick(current_FPS)
#     can_move = True

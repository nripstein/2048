import random
import colr
import statistics
from prettytable import PrettyTable
from pynput import keyboard
from pynput.keyboard import Key
from copy import copy
import gui

import time


import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# gui.assemble_image(64, (200, 200))


class Game:
    def __init__(self, track_primes: bool = False) -> None:
        self.track_primes: bool = track_primes
        self.prime_tracker: int = 1

        self.score: int = 0
        self.board: Board = Board()
        self.num_moves: int = 0
        self.highest_tile: int = 0

    def return_prime(self):
        if not self.track_primes:
            return False
        else:
            return self.prime_tracker

    def setup_board(self) -> None:
        # this fn should be called in __init__

        # pick which squares to use
        x1, y1 = random.randint(0, 3), random.randint(0, 3)
        # this thing with the loop prevents duplicates of the same square
        x2, y2 = x1, y1
        while x2 == x1 and y2 == y1:
            x2, y2 = random.randint(0, 3), random.randint(0, 3)

        # 90% chance of a tile being 2
        # weird that this makes a list and I need to take the first element from it. can clean up later
        tile1_value = random.choices([2, 4], weights=(0.9, 0.1))[0]
        tile2_value = random.choices([2, 4], weights=(0.9, 0.1))[0]
        # print(f"tile1 = {tile1_value}, tile2 = {tile2_value}")
        self.board.add_tile(tile1_value, x1, y1)
        self.board.add_tile(tile2_value, x2, y2)

    def add_new_tile(self) -> None:
        tile_value = random.choices([2, 4], weights=(0.9, 0.1))[0]

        x, y = random.randint(0, 3), random.randint(0, 3)
        square_coord = [x, y]
        while self.board[square_coord] != 0:
            x, y = random.randint(0, 3), random.randint(0, 3)
            square_coord = [x, y]
        self.board.add_tile(tile_value, x, y)

    def print_board(self):
        print(f"--------------------SCORE: {self.score}--------------------")
        self.board.print(highest=len(str(self.highest_tile)))

    def left(self):
        return self.move(1)

    def right(self):
        return self.move(0)

    def up(self):
        return self.move(2)

    def down(self):
        return self.move(3)

    def move(self, direction: int) -> bool:
        """returns whether it was successful"""
        # 0 = right, 1 = left, 2 = up, 3 = down

        square_coord_list = []
        if direction in (1, 2):  # left or up
            # generate list of squares from left to right one row at a time, starting from top
            for row_num in range(len(self.board.board)):
                # print(row_num)
                for i in range(4):
                    # print(3 - i)
                    # print(f"({i}, {row_num})")
                    square_coord_list.append((i, row_num))
        elif direction in (0, 3):    # right or down
            for row_num in range(len(self.board.board)):
                # print(row_num)
                for i in range(4):
                    # print(3 - i)
                    # print(f"({i}, {row_num})")
                    square_coord_list.append((3 - i, 3 - row_num))

        # removes empty tiles
        tiles_to_move = []
        for square in square_coord_list:
            if self.board.value_of_position(square[0], square[1]) != 0:
                tiles_to_move.append(square)

        not_moving_list = set()
        for tile in tiles_to_move:
            #print(f"---tile is {tile}--")
            temp_board_obj = Board(self.board.board[:])
            #temp_board_obj.print()
            traverse = self.traverse_list(tile, direction, temp_board_obj)
            # print(f"traverse of {tile}= {traverse}")
            if not traverse[0]:
                # print(f"{tile} not moving")
                not_moving_list.add(tile)  # should make this a set off the bat for efficiency instaed of converting it
            else:
                #print(f"{tile} moving to {traverse[0][-1]}")
                #print(f"{tile}'s traverse = {traverse}")
                xf, yf = traverse[0][-1]
                add_to_score = self.board.move_tile(tile, (xf, yf), traverse[-1])
                self.score += add_to_score
                if add_to_score > self.highest_tile:
                    self.highest_tile = add_to_score

        illegal_move = False
        if set(not_moving_list) == set(tiles_to_move):
            print("ILLEGAL MOVE!")
            return False

        if not illegal_move:
            self.add_new_tile()

            # prime stuff. disabled by default because it would slow things down on large simulations
            if self.track_primes:
                prime_direction_dict = {
                    0: 2,  # right
                    1: 3,  # left
                    2: 5,  # up
                    3: 7  # down
                }
                self.prime_tracker *= prime_direction_dict[direction]
        self.print_board()

        self.num_moves += 1
        return True

    def traverse_list(self, square: tuple, direction: int, board=None) -> list:
        if board is None:
            board = self.board
        # makes ordered list of squares to traverse for a given square
        # 0 = right, 1 = left, 2 = up, 3 = down
        # square is a tuple of form (x, y)
        output_list: list = []
        final_capture: bool = False
        x, y = square
        square_value: int = board.value_of_position(x, y)

        # print(f"starting square x = ({x}, {y})")
        next_square: list = [x, y]
        if direction == 0:  # right
            while next_square[0] < 3:
                next_square[0] += 1
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])
                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}")
                        output_list.append(next_square[:])
                        final_capture: bool = True
                    break
        elif direction == 1: # left. this and others could be condensed into 1 loop for all of them if I switch next square [0 to 1] and += 1 to -1 in the right places
            while next_square[0] > 0:
                #print(f"next square before = {next_square} ---- ---- ---- ----")
                next_square[0] -= 1
                #print(f"next square = {next_square} ---- ---- ---- ----")
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])

                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}. traverse = {output_list}")
                        output_list.append(next_square[:])
                        final_capture: bool = True

                    break
        elif direction == 2: # up. this and others could be condensed into 1 loop for all of them if I switch next square [0 to 1] and += 1 to -1 in the right places
            while next_square[1] > 0:
                next_square[1] -= 1
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])
                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}")
                        output_list.append(next_square[:])
                        final_capture: bool = True
                    break
        elif direction == 3:  # down
            while next_square[1] < 3:
                next_square[1] += 1
                if self.empty_square(next_square):
                    #print(f"next_square = {next_square}")
                    output_list.append(next_square[:])
                else:
                    #print(f"{next_square} isn't empty")
                    if board.value_of_position(next_square[0], next_square[1]) == square_value:
                        # print(f"we gon eat on {next_square}")
                        output_list.append(next_square[:])
                        final_capture: bool = True
                    break
        if output_list:
            output: list = [output_list, final_capture]
        else:
            output: list = [[], final_capture]
        # print(f"output = {output}")
        return output

    def empty_square(self, square: tuple) -> bool:
        """returns true if empty, false if not"""
        x, y = square
        # print(f"in empty sq, will return {self.board.value_of_position(x, y) == 0}")
        return self.board.value_of_position(x, y) == 0


class Board:
    def __init__(self, initial_board=None):
        if initial_board is None:
            self.board: list = [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ]
        else:
            self.board: list = initial_board

    def add_tile(self, tile_value: int, x_coord: int, y_coord: int):
        self.board[y_coord][x_coord] = tile_value

    def value_of_position(self, x_coord: int, y_coord: int) -> int:
        return self.board[y_coord][x_coord]

    # this fn untested! it's important tho
    def move_tile(self, square1: tuple, square2: tuple, eat: bool = False) -> int:
        """returns how much score to add"""
        x1, y1 = square1
        x2, y2 = square2
        tile_value = self.value_of_position(x1, y1)
        # remove from old location
        self.board[y1][x1] = 0
        # place in new location no eat
        if not eat:
            self.board[y2][x2] = tile_value
        else:
            self.board[y2][x2] = tile_value * 2
            return tile_value * 2
        return 0

    def print(self, highest=2):
        tile_colours = {
            2048: "EDC22E",
            1024: "#EDC23F",
            512: "#EDC850",
            256: "#EDCC61",
            128: "#EDCF72",
            64: "#F65E3B",
            32: "#F67C5F",
            16: "#F59563",
            8: "#F2B179",
            4: "#EDE0C8",
            2: "#EEE4DA",
            0: "#CCC0B3"
        }

        # print("in if not un")
        #print(f"highest = {highest}")
        highest2 = copy(highest)
        #print(f"highest2 = {highest2}, highest = {highest}")
        for row in self.board:
            #print(f"higest2 = {highest2}")
            for tile in row:

                # FFFFFF is white, 000000 is black
                print(colr.color(f"{tile}\t".expandtabs(highest2 + 2), back=tile_colours[tile], fore="000000"), end=" ")
                # print(colr.color("32", back=tile_colours[32], fore="FFFFFF"))
            print("")
        # self.print_table()

    def print_table(self):  # not currently used
        my_table = PrettyTable()
        my_table.header = False
        for i in range(4):
            my_table.add_row(self.board[i])

        print(my_table)

    def __getitem__(self, coordinate: tuple) -> int:
        x, y = coordinate
        return self.board[y][x]

    def __setitem__(self, coordinate: tuple, value: int):
        x, y = coordinate
        self.board[y][x] = value



#global latest_key
# latest_key = "NONE"

def keyboard_input():

    def on_key_release(key):

        if key == Key.right:
            print("Right key clicked")
            # global latest_key
            # latest_key = "Right"
        elif key == Key.left:
            print("Left key clicked")
        elif key == Key.up:
            print("Up key clicked")
        elif key == Key.down:
            print("Down key clicked")
        elif key == Key.esc:
            exit()

    with keyboard.Listener(on_release=on_key_release) as listener:
        listener.join()


# keyboard_input()

def run_game(arrow_input=False, track_primes=False):
    running_game = Game(track_primes)
    print(f"on any move, enter 'p' to return prime tracker")
    running_game.setup_board()
    running_game.print_board()

    while True:
        #running_game.print_board()
        if not arrow_input:
            move = input("direction (w, a, s, d): ")
            # 0 = right, 1 = left, 2 = up, 3 = down

            if move == "s":
                running_game.down()
            elif move == "w":
                running_game.up()
            elif move == "a":
                running_game.left()
            elif move == "d":
                running_game.right()

            elif move == "p":
                print(running_game.return_prime())
        else:
            keyboard_input()





run_game(track_primes=True)
#db2 = Down2(print_moves=False)
#db2.run()

# db1 = DownBot(print_moves=True)
# db1.run()

# m1 = ManyRuns(Down2, 50, print_moves=True)
# m1.run()

# from opeinAI
import tkinter as tk



# class GameGUI:
#     def __init__(self, game):
#         self.game = game
#         self.root = tk.Tk()
#         self.frame = tk.Frame(self.root)
#         self.frame.pack()
#
#         self.score_label = tk.Label(self.frame, text=f"Score: {self.game.score}")
#         self.score_label.pack()
#
#         self.board_frame = tk.Frame(self.frame)
#         self.board_frame.pack()
#
#         self.tile_labels = []
#         for row in range(4):
#             row_frame = tk.Frame(self.board_frame)
#             row_frame.pack()
#             self.tile_labels.append([])
#             for col in range(4):
#                 label = tk.Label(row_frame, text=self.game.board[row, col], width=5, height=2)
#                 label.pack(side=tk.LEFT)
#                 self.tile_labels[row].append(label)
#
#         self.button_frame = tk.Frame(self.frame)
#         self.button_frame.pack()
#         self.left_button = tk.Button(self.button_frame, text="Left", command=self.move_left)
#         self.left_button.pack(side=tk.LEFT)
#         self.up_button = tk.Button(self.button_frame, text="Up", command=self.move_up)
#         self.up_button.pack(side=tk.LEFT)
#         self.right_button = tk.Button(self.button_frame, text="Right", command=self.move_right)
#         self.right_button.pack(side=tk.LEFT)
#         self.down_button = tk.Button(self.button_frame, text="Down", command=self.move_down)
#         self.down_button.pack(side=tk.LEFT)
#
#     def move_left(self):
#         if self.game.left():
#             self.update_display()
#
#     def move_up(self):
#         if self.game.up():
#             self.update_display()
#
#     def move_right(self):
#         if self.game.right():
#             self.update_display()
#
#     def move_down(self):
#         if self.game.down():
#             self.update_display()
#
#     def update_display(self):
#         for row in range(4):
#             for col in range(4):
#                 self.tile_labels[row][col].config(text=self.game.board[row, col])
#         self.score_label.config(text=f"Score: {self.game.score}")
#
#     def run(self):
#         self.root.mainloop()


# class GameGUI:
#     def __init__(self):
#         self.game = game
#         self.root = tk.Tk()
#         self.frame = tk.Frame(self.root)
#         self.frame.pack()
#         self.score_label = tk.Label(self.frame, text=f"Score: {self.game.score}")
#         self.score_label.pack()
#
#         self.board_frame = tk.Frame(self.frame)
#         self.board_frame.pack()
#
#         self.tile_labels = []
#         for row in range(4):
#             row_frame = tk.Frame(self.board_frame)
#             row_frame.pack()
#             self.tile_labels.append([])
#             for col in range(4):
#                 label = tk.Label(row_frame, text=self.game.board[row, col], width=5, height=2)
#                 label.pack(side=tk.LEFT)
#                 self.tile_labels[row].append(label)
#
#         self.button_frame = tk.Frame(self.frame)
#         self.button_frame.pack()
#         self.left_button = tk.Button(self.button_frame, text="Left", command=self.move_left)
#         self.left_button.pack(side=tk.LEFT)
#         self.up_button = tk.Button(self.button_frame, text="Up", command=self.move_up)
#         self.up_button.pack(side=tk.LEFT)
#         self.right_button = tk.Button(self.button_frame, text="Right", command=self.move_right)
#         self.right_button.pack(side=tk.LEFT)
#         self.down_button = tk.Button(self.button_frame, text="Down", command=self.move_down)
#         self.down_button.pack(side=tk.LEFT)
#
#         self.root.bind("<Left>", self.move_left)
#         self.root.bind("<Up>", self.move_up)
#         self.root.bind("<Right>", self.move_right)
#         self.root.bind("<Down>", self.move_down)
#
#
#     def move_left(self, event=None):
#         if self.game.left():
#             self.update_display()
#
#
#     def move_up(self, event=None):
#         if self.game.up():
#             self.update_display()
#
#
#     def move_right(self, event=None):
#         if self.game.right():
#             self.update_display()
#
#
#     def move_down(self, event=None):
#         if self.game.down():
#             self.update_display()
#
#
#     def update_display(self):
#         for row in range(4):
#             for col in range(4):
#                 self.tile_labels[row][col].config(text=self.game.board[row, col])
#         self.score_label.config(text=f"Score: {self.game.score}")


# def run(self


# game = Game()
# game.setup_board()
# gui = GameGUI(game)
# gui.run()






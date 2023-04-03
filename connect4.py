#!/usr/bin/env python3

"""
The original Connect 4.
"""

from typing import Callable
from common import (
	DRAW,
	GAME_NOT_OVER,
	Board,
	Column,
	Player,
	clear_screen,
	cpu_player_easy,
	cpu_player_hard,
	cpu_player_medium,
	create_board,
	end_of_game,
	execute_player_turn,
	print_board,
)

NUM_ROWS = 6
NUM_COLS = 7
NUM_PLAYERS = 2
K = 4


def print_rules():
	"""
	Prints the rules of the game.

	:return: None
	"""
	print("================= Rules =================")
	print("Connect 4 is a two-player game where the")
	print("objective is to get four of your pieces")
	print("in a row either horizontally, vertically")
	print("or diagonally. The game is played on a")
	print("6x7 grid. The first player to get four")
	print("pieces in a row wins the game. If the")
	print("grid is filled and no player has won,")
	print("the game is a draw.")
	print("=========================================")


def local_2_player_game():
	"""
	Runs a local 2 player game of Connect 4.

	:return: None
	"""
	board = create_board(NUM_ROWS, NUM_COLS)
	player: Player = 1
	state = GAME_NOT_OVER
	previous_player = None
	previous_column = None
	while state == GAME_NOT_OVER:
		clear_screen()
		print_board(K, NUM_PLAYERS, board)
		if previous_column:
			print(
				f"Player {previous_player} dropped a piece into column {previous_column}"
			)
		previous_column = execute_player_turn(K, NUM_PLAYERS, board, player)
		previous_player = player
		state = end_of_game(K, board)
		player = player % NUM_PLAYERS + 1
	clear_screen()
	print_board(K, NUM_PLAYERS, board)
	print(f"Player {previous_player} dropped a piece into column {previous_column}")
	print("Draw" if state == DRAW else f"Player {state} wins!")

def get_cpu_difficulty() -> Callable[[int, int, Board, Player], Column]:
	clear_screen()
	print("============= CPU Difficulty ============")
	print("1. Easy")
	print("2. Medium")
	print("3. Hard")
	print("=========================================")
	while True:
		match input().strip():
			case "1":
				return cpu_player_easy
			case "2":
				return cpu_player_medium
			case "3":
				return cpu_player_hard
			case _:
				print("Invalid selection")


def game_against_cpu():
	"""
	Runs a game of Connect 4 against the computer.

	:return: None
	"""

	cpu_player = get_cpu_difficulty()
	board = create_board(NUM_ROWS, NUM_COLS)
	player: Player = 1
	state = GAME_NOT_OVER
	previous_human_column = None
	previous_cpu_column = None

	def print_previous_turns():
		print(f"Player 1 dropped a piece into column {previous_human_column}")
		print(f"Player 2 dropped a piece into column {previous_cpu_column}")

	while state == GAME_NOT_OVER:
		clear_screen()
		print_board(K, NUM_PLAYERS, board)
		if previous_cpu_column:
			print_previous_turns()
		if player == 1:
			previous_human_column = execute_player_turn(K, NUM_PLAYERS, board, player)
		else:
			previous_cpu_column = cpu_player(K, NUM_PLAYERS, board, player)
		state = end_of_game(K, board)
		player = player % NUM_PLAYERS + 1
	clear_screen()
	print_board(K, NUM_PLAYERS, board)
	print_previous_turns()
	print("Draw" if state == DRAW else f"Player {state} wins!")


def main():
	"""
	Defines the main application loop.
	User chooses a type of game to play or to exit.

	:return: None
	"""
	while True:
		clear_screen()
		print("=============== Main Menu ===============")
		print("Welcome to Connect 4!")
		print("1. View Rules")
		print("2. Play a local 2 player game")
		print("3. Play a game against the computer")
		print("4. Exit")
		print("=========================================")
		while True:
			match input().strip():
				case "1":
					print_rules()
					break
				case "2":
					local_2_player_game()
					break
				case "3":
					game_against_cpu()
					break
				case "4":
					return
				case _:
					print("Invalid selection")
		input("Hit any key to return to the menu.")

if __name__ == "__main__":
	main()

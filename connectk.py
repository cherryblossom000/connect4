#!/usr/bin/env python3

"""
Connect K.
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


def print_rules():
	"""
	Prints the rules of the game.

	:return: None
	"""
	print("================= Rules =================")
	print("Connect K is a two-player game where the")
	print("objective is to get K of your pieces")
	print("in a row either horizontally, vertically")
	print("or diagonally. The first player to get K")
	print("pieces in a row wins the game. If the")
	print("grid is filled and no player has won,")
	print("the game is a draw.")
	print("=========================================")


def ask_for_positive_int(prompt: str) -> int:
	"""
	Asks the user for an integer input and keeps asking until the user supplies
	a valid positive integer.

	:param prompt: The message to prompt the user with.
	:return: The positive integer the user inputted (int).
	"""
	while True:
		input_str = input(prompt)
		try:
			integer = int(input_str)
		except ValueError:
			print(f"Invalid integer {input_str}")
			continue
		if integer <= 0:
			print(f"{integer} must be > 0")
		else:
			return integer


def get_player_turn_function(
	number: int,
) -> Callable[[int, int, Board, Player], Column]:
	"""
	Gets the function used to execute a player's turn.

	:param number: The player number (starting at 1).
	:return: A function that can be called like
	`play_turn(k, num_players, board, player)` that plays the turn for the
	particular player, dropping a piece into `board`, and returns the column
	that the piece was dropped in.
	"""
	clear_screen()
	print(f"=============== Player {number} ===============")
	print("1. Human")
	print("2. CPU - Easy")
	print("3. CPU - Medium")
	print("4. CPU - Hard")
	print("=========================================")
	while True:
		match input().strip():
			case "1":
				return execute_player_turn
			case "2":
				return cpu_player_easy
			case "3":
				return cpu_player_medium
			case "4":
				return cpu_player_hard
			case _:
				print("Invalid selection")


def play_game():
	"""
	Plays a game of Connect K.

	:return: None
	"""
	clear_screen()
	num_rows = ask_for_positive_int("Number of rows: ")
	num_cols = ask_for_positive_int("Number of columns: ")

	k = ask_for_positive_int("Number of tokens in a row to required to win (K): ")
	while k > max(num_rows, num_cols):
		print("It is impossible to win with this number of tokens")
		k = ask_for_positive_int("Number of tokens in a row to required to win (K): ")

	num_players = ask_for_positive_int("Number of players: ")
	while (num_rows * num_cols) // num_players < k:
		print(
			"It is impossible (for at least the last player) to win with this number of players"
		)
		num_players = ask_for_positive_int("Number of players: ")

	players = [get_player_turn_function(i + 1) for i in range(num_players)]

	board = create_board(num_rows, num_cols)
	player = 1
	state = GAME_NOT_OVER
	previous_turns: list[tuple[Player, Column]] = []

	def print_board_and_previous_turns():
		clear_screen()
		print_board(k, num_players, board)
		for previous_player, previous_column in previous_turns:
			print(
				f"Player {previous_player} dropped a piece into column {previous_column}"
			)

	while state == GAME_NOT_OVER:
		print_board_and_previous_turns()
		play_turn = players[player - 1]
		column = play_turn(k, num_players, board, player)
		if play_turn is execute_player_turn:
			previous_turns = [(player, column)]
		else:
			previous_turns.append((player, column))
		state = end_of_game(k, board)
		player = player % num_players + 1
	print_board_and_previous_turns()
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
		print("Welcome to Connect K!")
		print("1. View Rules")
		print("2. Play a game")
		print("3. Exit")
		print("=========================================")
		while True:
			match input().strip():
				case "1":
					print_rules()
					break
				case "2":
					play_game()
					break
				case "3":
					return
				case _:
					print("Invalid selection")
		input("Hit any key to return to the menu.")


if __name__ == "__main__":
	main()

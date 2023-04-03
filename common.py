"""
Common functions for connect4.py and connectk.py.
"""

from math import log10
import random
import os

from collections.abc import Generator, Iterable
from typing import Literal, Optional, Union

# region Constants and Types

GameNotOver = Literal[0]
GAME_NOT_OVER: GameNotOver = 0

Draw = Literal[-1]
DRAW: Draw = -1

Player = int
Cell = int
Board = list[list[Cell]]
Column = int
"""
Columns start at 1.
"""

Position = tuple[int, int]
"""
A tuple of (row, column) indicating the position of a cell in a game board.
The row and column start at for convenience.
"""

State = Union[Player, Draw, GameNotOver]
"""
The game state. Either `GAME_NOT_OVER` (0), `DRAW` (3), or the player who has
won.
"""

# endregion

# region Utilities


def clear_screen():
	"""
	Clears the terminal for Windows and Linux/MacOS.

	:return: None
	"""
	os.system("cls" if os.name == "nt" else "clear")


def validate_input(
	prompt: str,
	valid_inputs: list[str],
	invalid_msg: str = "Invalid input, please try again.",
) -> str:
	"""
	Repeatedly ask user for input until they enter an input
	within a set valid of options.

	:param prompt: The prompt to display to the user, string.
	:param valid_inputs: The range of values to accept, list
	:return: The user's input, string.
	"""
	user_input = input(prompt)
	while user_input not in valid_inputs:
		print(invalid_msg)
		user_input = input(prompt)

	return user_input


# endregion

# region Board


def create_board(num_rows: int, num_cols: int) -> Board:
	"""
	Returns a 2D list of `num_rows` rows and `num_cols` columns to represent
	the game board. Default cell value is 0.

	:return: A 2D list of `num_rows`×`num_cols` dimensions.
	"""
	return [[0] * num_cols for _ in range(num_rows)]


def print_board(k: int, num_players: int, board: Board):
	"""
	Prints the game board to the console.

				:param k: Number of tokens in a row
	:param board: The game board, 2D list of 6x7 dimensions.
	:return: None
	"""
	num_columns = len(board[0])
	column_width = int(log10(max(num_columns, num_players))) + 1
	horizontal_line = (" " + "-" * (column_width + 2)) * num_columns
	total_width = num_columns * (column_width + 3) + 1
	connect_k = f" Connect {k} "
	connect_k_len = len(connect_k)
	num_equals_left = (total_width - connect_k_len) // 2
	print(
		"=" * num_equals_left
		+ connect_k
		+ "=" * (total_width - num_equals_left - connect_k_len)
	)
	print("Players are represented by a number (e.g. player 1 is ‘1’ on the board)")
	print()
	# Column numbers at top
	print("  ", end="")
	print(*(f"{i + 1:{column_width}}" for i in range(num_columns)), sep="   ")
	print(horizontal_line)
	for row in board:
		# Print each row
		print("| ", end="")
		print(
			*(f"{cell:{column_width}}" if cell else " " * column_width for cell in row),
			sep=" | ",
			end="",
		)
		print(" |")
		print(horizontal_line)
	print("=" * total_width)


def get_free_columns(board: Board) -> list[Column]:
	"""
	Gets the columns that a piece can be placed in. The columns start at 1.
	"""
	# We only need to check if the top row has an empty cell (cell == 0) in
	# order to determine whether a column is full or not.
	return [
		# Add 1 as indexes start at 0 in Python, whereas our columns start at 1
		i + 1
		# i is the index of the column, and cell is the cell in the top row
		for i, cell in enumerate(board[0])
		# Only include columns that have an empty cell in the top row
		if cell == 0
	]


def pieces_in_a_row(
	board: Board,
) -> Generator[tuple[Player, list[Position]], None, None]:
	"""
	Gets the positions and players of the pieces in a row on a game board. Only
	returns pieces that are 2 or more in a row.

	:param board: The game board.
	:return: A generator that generates tuples. Each tuple represents a line of
	pieces in a row. The first element of the tuple is the player who the piece
	is for. The second element of the tuple is a list of positions, which
	represent the location of the pieces. Note that these positions start at 0
	(so the top left position is (0, 0)).

	>>> list(pieces_in_a_row([[1, 1]]))
	[(1, [(0, 0), (0, 1)])]
	>>> list(pieces_in_a_row([[1], [1]]))
	[(1, [(0, 0), (1, 0)])]
	>>> list(pieces_in_a_row([
	...	[0, 0, 0, 0, 0],
	...	[1, 1, 1, 0, 0],
	...	[2, 2, 1, 0, 0],
	...	[1, 2, 1, 0, 0],
	... ]))
	[(1, [(1, 0), (1, 1), (1, 2)]), (2, [(2, 0), (2, 1)]), (2, [(2, 1), (3, 1)]), (1, [(1, 2), (2, 2), (3, 2)]), (1, [(1, 1), (2, 2)]), (2, [(2, 0), (3, 1)])]
	>>> list(pieces_in_a_row([
	...	[0, 0, 0, 1],
	...	[0, 0, 1, 0],
	...	[0, 1, 0, 0],
	...	[1, 0, 0, 0],
	... ]))
	[(1, [(3, 0), (2, 1), (1, 2), (0, 3)])]
	>>> list(pieces_in_a_row([
	...	[0, 0, 0, 1],
	...	[0, 0, 1, 0],
	...	[0, 1, 0, 0],
	...	[0, 0, 0, 0],
	... ]))
	[(1, [(2, 1), (1, 2), (0, 3)])]
	>>> list(pieces_in_a_row([
	...	[0, 0, 0, 0],
	...	[0, 0, 0, 0],
	...	[1, 0, 0, 0],
	...	[2, 1, 0, 0],
	... ]))
	[(1, [(2, 0), (3, 1)])]
	>>> list(pieces_in_a_row([
	...	[0, 0, 1, 0],
	...	[0, 1, 0, 0],
	...	[1, 0, 0, 0],
	...	[0, 0, 0, 0],
	... ]))
	[(1, [(2, 0), (1, 1), (0, 2)])]
	"""
	num_rows = len(board)
	num_cols = len(board[0])

	def pieces_in_a_row_from_cells(
		cells: Iterable[tuple[Position, Cell]],
	) -> Generator[tuple[Player, list[Position]], None, None]:
		"""
		Yields the info about consecutive cells in `cells`.

		:param cells: An iterable of tuples. The tuple's first element is the
		position of the cell, and the second element is the value of the cell
		itself.
		Simply, an iterable is a thing you can use in a for loop. They aren't
		exactly the same as a list, but you can think of them like lists.
		`range` returns an iterable, for example.
		"""
		current_player = 0
		positions: list[Position] = []
		for position, cell in cells:
			if cell == current_player:
				positions.append(position)
			else:
				if len(positions) > 1 and current_player != 0:
					# why does pyright not narrow current_player down to 1 | 2
					# it should know it can't be 0...
					yield current_player, positions
				current_player = cell
				positions = [position]
		if len(positions) > 1 and current_player != 0:
			yield current_player, positions

	# A list[list[tuple[Position, Cell]]]. Like a board, but instead of a 2x2
	# list of cells, it's a 2x2 list of tuples, where each tuple has the cell's
	# position as well as it's value.
	# This is useful because we want to return the cells' positions from this
	# function (which is used for cpu_player_hard).
	board_with_positions = [
		# Create a list and return...
		[
			# Return the position and the cell
			((i, j), cell)
			# for every cell (j is the column index)
			for j, cell in enumerate(row)
		]  # and store the results in a list
		# ...for every row. i is the row index and row is the actual row
		for i, row in enumerate(board)
	]  # and store the results in a list

	# Horizontal: →
	for row in board_with_positions:
		yield from pieces_in_a_row_from_cells(row)

	# Vertical: ↓
	for column_index in range(num_cols):
		yield from pieces_in_a_row_from_cells(
			# This is all the cells at column column_index
			row[column_index]
			for row in board_with_positions
		)

	# Diagonal: ↘︎
	# If we had a simple 4x5 board like this:
	# 1 2 3 4 -
	# - 1 2 3 4
	# - - 1 2 3
	# - - - 1 2
	# this first for loop starts at the top left cell and goes diagonally
	# downwards following the 1s. Then it does the cells labelled 2, then 3,
	# etc.
	# The range only goes up to num_cols - 1 because we don't need to check
	# the top right corner (we don't care about single pieces by itself).
	for starting_column in range(num_cols - 1):
		yield from pieces_in_a_row_from_cells(
			# starting_column is the column we started at. Each time we go down,
			# we have to go right 1, which is why we add j.
			row[starting_column + offset]
			for offset, row in enumerate(
				# num_cols - starting_column is how many cells we can go right
				# (including the first cell)
				# We only need to go down as many times as we can go right
				board_with_positions[: num_cols - starting_column]
			)
		)
	# Now this second for loop checks these ones:
	# - - - - -
	# 1 - - - -
	# 2 1 - - -
	# - 2 1 - -
	# We've already checked the top left corner, and we also don't need to check
	# the bottom left corner either, so the range is [1, num_rows - 1)
	for starting_row in range(1, num_rows - 1):
		yield from pieces_in_a_row_from_cells(
			# offset starts at 0 and increases each time we go down
			row[offset]
			for offset, row in enumerate(
				# Because we always start in the first column, num_cols is how
				# many times we can go right. We start at starting_row and only go
				# down as many times as we can go right.
				board_with_positions[starting_row : starting_row + num_cols]
			)
		)

	# Diagonal: ↗︎
	# - - - 1 2
	# - - 1 2 3
	# - 1 2 3 4
	# 1 2 3 4 -
	for starting_column in range(num_cols - 1):
		yield from pieces_in_a_row_from_cells(
			row[starting_column + offset]
			for offset, row in enumerate(
				# Again, num_cols - starting_column is how many times we can go
				# right, but this time we're starting from the bottom of the
				# board and going up
				board_with_positions[
					# start at the end
					-1:
					# only get (num_cols - starting_column) many cells
					# fmt: off
					-(num_cols - starting_column) - 1 :
					# this is the step size, so we're going backwards
					-1
				]
			)
		)
	# - 1 2 - -
	# 1 2 - - -
	# 2 - - - -
	# - - - - -
	for starting_row in range(1, num_rows - 1):
		# num_cols: how many times we can go up and therefore how many
		# times we can go up
		last_index = starting_row - num_cols
		yield from pieces_in_a_row_from_cells(
			row[offset]
			for offset, row in enumerate(
				board_with_positions[
					# If last_index is negative, we should include all the rows
					# to the start (including the first row). To do that in
					# Python we need None here
					starting_row : (None if last_index < 0 else last_index) : -1
				]
			)
		)


def end_of_game(k: int, board: Board) -> State:
	"""
	Checks if the game has ended with a winner
	or a draw.

	:param board: The game board.
	:return: 0 if game is not over, -1 if draw, otherwise the player who won.
	>>> end_of_game(4, [
	...	[1, 2, 1, 2],
	...	[2, 1, 2, 1],
	...	[1, 2, 1, 2],
	...	[1, 1, 1, 2],
	... ])
	-1
	>>> end_of_game(4, [[1, 1, 1, 0]])
	0
	>>> end_of_game(4, [[1, 1, 1, 1]])
	1
	>>> end_of_game(4, [[1, 1, 1, 0, 2, 2, 2, 2]])
	2
	>>> end_of_game(4, [[0], [1], [1], [1]])
	0
	>>> end_of_game(4, [[1], [1], [1], [1]])
	1
	>>> end_of_game(4, [[1], [1], [1], [0], [2], [2], [2], [2]])
	2
	>>> end_of_game(4, [
	...	[0, 0, 0, 0],
	...	[0, 1, 0, 0],
	...	[0, 0, 1, 0],
	...	[0, 0, 0, 1]
	... ])
	0
	>>> end_of_game(4, [
	...	[1, 0, 0, 0],
	...	[0, 1, 0, 0],
	...	[0, 0, 1, 0],
	...	[0, 0, 0, 1],
	... ])
	1
	>>> end_of_game(4, [
	...	[0, 1, 0, 0, 0],
	...	[0, 0, 1, 0, 0],
	...	[0, 0, 0, 1, 0],
	...	[0, 0, 0, 0, 1],
	... ])
	1
	>>> end_of_game(4, [
	...	[1, 0, 0, 0, 0, 0],
	...	[0, 2, 0, 0, 0, 0],
	...	[0, 0, 1, 0, 0, 0],
	...	[0, 0, 0, 1, 0, 0],
	...	[0, 0, 0, 0, 1, 0],
	...	[0, 0, 0, 0, 0, 1],
	... ])
	1
	>>> end_of_game(4, [
	...	[0, 0, 0, 0],
	...	[0, 0, 1, 0],
	...	[0, 1, 0, 0],
	...	[1, 0, 0, 0],
	... ])
	0
	>>> end_of_game(4, [
	...	[0, 0, 0, 1],
	...	[0, 0, 1, 0],
	...	[0, 1, 0, 0],
	...	[1, 0, 0, 0],
	... ])
	1
	>>> end_of_game(4, [
	...	[0, 0, 0, 0, 1],
	...	[0, 0, 0, 1, 0],
	...	[0, 0, 1, 0, 0],
	...	[0, 1, 0, 0, 1],
	... ])
	1
	>>> end_of_game(4, [
	...	[0, 0, 0, 0, 0, 1],
	...	[0, 0, 0, 0, 1, 0],
	...	[0, 0, 0, 1, 0, 0],
	...	[0, 0, 1, 0, 0, 0],
	...	[0, 2, 0, 0, 0, 0],
	...	[1, 0, 0, 0, 0, 0],
	... ])
	1
	"""
	for player, cells in pieces_in_a_row(board):
		if len(cells) >= k:
			return player
	return (
		# If any of the cells are empty (0), the game isn't over: return 0
		GAME_NOT_OVER
		if 0 in board[0]
		else
		# Otherwise it's a draw: return 3
		DRAW
	)


def drop_piece(board: Board, player: Player, column: Column) -> bool:
	"""
	Drops a piece into the game board in the given column.
	Please note that this function expects the column index
	to start at 1.

	:param board: The game board.
	:param player: The player dropping the piece, int.
	:param column: The index of column to drop the piece into, int.
	:return: True if piece was successfully dropped, False if not.
	"""
	index = column - 1
	# Search for an available row, starting from the bottom (hence the reversed)
	for row in reversed(board):
		if row[index] == 0:
			row[index] = player
			return True
	return False


def copy_and_drop_piece(board: Board, player: Player, column: Column) -> Board:
	"""
	Copies the board, drops a piece into the copied board, and returns the
	copied board.
	"""
	new_board = [row.copy() for row in board]
	drop_piece(new_board, player, column)
	return new_board


# endregion

# region Players


def execute_player_turn(_: int, __: int, board: Board, player: Player) -> Column:
	"""
	Prompts user for a legal move given the current game board
	and executes the move.

	:return: Column that the piece was dropped into, int.
	"""
	# Explicitly specifying the parameter names for clarity
	column_str = validate_input(
		prompt=f"Player {player}, please enter the column you would like to drop your piece into: ",
		# Convert ints into strings for validate_input
		valid_inputs=[str(column) for column in get_free_columns(board)],
		invalid_msg="That column is full, please try again.",
	)
	column = int(column_str)
	assert drop_piece(board, player, column)
	return column


def cpu_player_easy(_: int, __: int, board: Board, player: Player) -> Column:
	"""
	Executes a move for the CPU on easy difficulty. This function
	plays a randomly selected column.

	:param board: The game board, 2D list of 6x7 dimensions.
	:param player: The player whose turn it is, integer value of 1 or 2.
	:return: Column that the piece was dropped into, int.
	"""
	chosen_column = random.choice(get_free_columns(board))
	assert drop_piece(board, player, chosen_column)
	return chosen_column


def win_or_block_column(
	k: int,
	num_players: int,
	board: Board,
	free_columns: list[Column],
	player: Player,
) -> Optional[Column]:
	"""
	Attempts to find a column that will win the game or block the opponent from
	winning the game.

	:param board: The game board.
	:param player: The player whose turn it is, integer value of 1 or 2.
	:return: The column that should be played (int), or None if the current
	player in this turn and the opponent cannot win in their next turn.

	>>> win_or_block_column(4, 2, [
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [1, 0, 1, 1, 1, 0, 0],
	... ], [1, 2, 3, 4, 5 ,6 ,7], 2)
	2
	"""
	# Win if possible
	for column in free_columns:
		if end_of_game(k, copy_and_drop_piece(board, player, column)) == player:
			return column
	# Otherwise try to block any opponents from winning, prioritising the
	# opponents who are about to play next
	for i in range(num_players - 1):
		opponent = (player + i) % num_players + 1
		for column in free_columns:
			if end_of_game(k, copy_and_drop_piece(board, opponent, column)) == opponent:
				return column


def cpu_player_medium(k: int, num_players: int, board: Board, player: Player) -> Column:
	"""
	Executes a move for the CPU on medium difficulty.
	It first checks for an immediate win and plays that move if possible.
	If no immediate win is possible, it checks for an immediate win
	for the opponent and blocks that move. If neither of these are
	possible, it plays a random move.

	:param board: The game board.
	:param player: The player whose turn it is, integer value of 1 or 2.
	:return: Column that the piece was dropped into, int.
	"""
	free_columns = get_free_columns(board)
	chosen_column = win_or_block_column(
		k, num_players, board, free_columns, player
	) or random.choice(free_columns)
	assert drop_piece(board, player, chosen_column)
	return chosen_column


# region Hard CPU Player


def can_win_from_pieces(k: int, board: Board, positions: list[Position]) -> bool:
	"""
	Determines whether a line of pieces can all be part of (the same)
	4-in-a-row. In other words, determines whether a line of pieces is a threat.

	:param board: The game board.
	:param positions: A list of positions of the cells to check.
	:return: Whether the pieces can be part of a 4 in a row (bool).

	>>> can_win_from_pieces(4, [
	...	 [0, 0, 0, 0, 0, 0, 0],
	...	 [0, 0, 0, 0, 0, 0, 0],
	...	 [0, 0, 0, 1, 1, 0, 0],
	...	 [0, 0, 2, 2, 2, 0, 0],
	...	 [0, 0, 1, 2, 1, 0, 0],
	...	 [2, 1, 1, 2, 1, 0, 0],
	... ], [(3, 2), (4, 3)])
	True
	>>> can_win_from_pieces(4, [
	...	 [0, 0, 0, 0, 0, 0, 0],
	...	 [0, 0, 0, 0, 0, 0, 0],
	...	 [0, 0, 0, 1, 1, 0, 0],
	...	 [0, 0, 2, 2, 2, 0, 0],
	...	 [0, 0, 1, 2, 1, 0, 0],
	...	 [2, 1, 1, 2, 1, 0, 0],
	... ], [(4, 3), (3, 4)])
	True
	>>> can_win_from_pieces(4, [
	...	 [0, 0, 0, 0, 0, 0, 0],
	...	 [0, 0, 0, 0, 0, 0, 0],
	...	 [0, 0, 0, 1, 1, 0, 0],
	...	 [0, 0, 2, 2, 2, 0, 0],
	...	 [0, 0, 1, 2, 1, 0, 0],
	...	 [2, 1, 1, 2, 1, 0, 0],
	... ], [(3, 3), (4, 3), (5, 3)])
	False
	"""
	num_rows = len(board)
	num_cols = len(board[0])

	def count_free_cells(row: int, col: int, row_diff: int, col_diff: int) -> int:
		count = 0
		while True:
			row += row_diff
			col += col_diff
			if 0 <= row < num_rows and 0 <= col < num_cols and board[row][col] == 0:
				count += 1
			else:
				break
		return count

	fst_pos = positions[0]
	snd_pos = positions[1]
	lst_pos = positions[-1]
	row_diff = snd_pos[0] - fst_pos[0]
	col_diff = snd_pos[1] - fst_pos[1]
	return (
		# Starting from the last position and going forwards
		count_free_cells(lst_pos[0], lst_pos[1], row_diff, col_diff) +
		# Starting from the first position and going backwards
		count_free_cells(fst_pos[0], fst_pos[1], -row_diff, -col_diff)
		# Is the total number of available cells in front and behind enough to
		# win?
		>= k - len(positions)
	)


def can_win_now(k: int, board: Board, player: Player) -> bool:
	"""
	Determines whether the current player can win in their current turn.

	:param board: The game board.
	:param player: The current player.
	:return: Whether `player` can win in their turn right now.
	"""
	for column in get_free_columns(board):
		if end_of_game(k, copy_and_drop_piece(board, player, column)) == player:
			return True
	return False


def column_score(
	k: int, num_players: int, board: Board, player: Player, column: Column
) -> tuple[bool, list[list[int]]]:
	"""
	This doesn't really compute a 'score'. It returns something that can be
	sorted, and all the columns' 'score' are sorted in descending order that
	should mean the columns are sorted from the best to the worst move.

	This function returns a tuple. The first element is a boolean. If the
	opponent can win in the next move after `player` places a piece in `column`,
	this boolean is `False`, otherwise it's `True`. This prevents us from
	letting the opponent immediately afterwards, and this works because
	`True` > `False`.

	The second element is a list.

	Each element of this list is a 2-element list: the first element of this list
	represents the player and the second element represents the opponents.

	In a standard game of Connect 4 with 2 players, this list will look something
	like `[[a, b], [c, d]]`, where
	- `a` is the number of 3-in-a-rows that `player` would have if they played
	  `column` next
	- `b` is the number of 3-in-a-rows that any opponent would have if it was
	  their turn and they played `column` next.
	  This number will be higher if the player would block the opponent from
	  making a 3-in-a-row by placing a piece in `column`.
	- `c` is the number of 2-in-a-rows that `player` would have if they played
	  `column` next
	- `d` is always 0 as this code ignores the 2-in-a-rows that the player could
	  block any opponent from forming. Doing this improved the cpu_player_hard's
	  win rate.
	These only include the x-in-a-rows that can form 4 in a row. For example,
	- - - - - - -
	- - - - - - -
	- - - - - - -
	- - - - - - -
	- - - - - - -
	1 1 2 - - - -
	the two 1s at the bottom wouldn't count as it's blocked by the 2.

	Python sorts lists by comparing the lists' first elements, then their second
	elements if the first ones are the same, etc. This means that the CPU would
	prioritise moves that give the player the most number of 3-in-a-rows, then
	moves that block the opponent from getting 3 in a row the most, then moves
	that give the player the most number of 2-in-a-rows, etc.

	:param board: The game board.
	:param player: The current player.
	:param column: The column that `player` is putting their piece into.
	:return: See above description.

	>>> column_score(4, 2, [
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 1, 0, 0, 0],
	... ], 1, 4)
	(True, [[0, 0], [1, 0]])
	>>> column_score(4, 2, [
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 1, 0, 0, 0],
	... [0, 0, 2, 2, 2, 0, 0],
	... [0, 0, 1, 2, 1, 0, 0],
	... [2, 1, 1, 2, 1, 0, 0],
	... ], 1, 5)
	(True, [[0, 1], [1, 0]])
	>>> column_score(4, 2, [
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 2, 1, 1, 0, 0],
	... [0, 0, 1, 2, 1, 0, 0],
	... [0, 2, 2, 1, 2, 0, 0],
	... [1, 2, 2, 2, 1, 1, 0],
	... ], 2, 2)
	(False, [])
	"""
	# Count of x-in-a-rows for each player, where x is
	# k - 1, k - 2, ..., 2
	counts = [[0, 0] for _ in range(k - 2)]

	new_board = copy_and_drop_piece(board, player, column)
	for row_player, cells in pieces_in_a_row(new_board):
		if row_player == player and can_win_from_pieces(k, board, cells):
			counts[k - len(cells) - 1][0] += 1

	for opponent in range(1, num_players + 1):
		if opponent == player:
			continue
		board_with_players_play = copy_and_drop_piece(board, player, column)
		if can_win_now(k, board_with_players_play, opponent):
			return False, []

		board_with_opponents_play = copy_and_drop_piece(board, opponent, column)
		for row_player, cells in pieces_in_a_row(board_with_opponents_play):
			if row_player == opponent and can_win_from_pieces(
				k, board_with_opponents_play, cells
			):
				# If the opponent only has 1 piece, don't try blocking them from
				# getting 2 in a row
				if len(cells) != 2:
					counts[k - len(cells) - 1][1] += 1

	return True, counts


def cpu_player_hard(k: int, num_players: int, board: Board, player: Player) -> Column:
	"""
	Executes a move for the CPU on hard difficulty.
	This function creates a copy of the board to simulate moves.

	It first checks for an immediate win and plays that move if possible.
	If no immediate win is possible, it checks for an immediate win
	for the opponent and blocks that move.

	If it can't block the opponent from an immediate win, it tries to play a
	move that results in the most 3-in-a-rows. If there's a tie, it then picks
	the move that blocks the opponent from getting 3 in a row. If there's
	another tie, it does the same thing but for 2-in-a-rows, except that it
	doesn't try blocking the opponent from forming 2 pieces in a row (so it
	ignores the opponent's pieces that are by themselves). If there's another
	tie, it picks columns closer to the center. The CPU will also avoid picking
	a column that would mean the opponent can win immediately in their next
	move.

	:param board: The game board, 2D list of 6x7 dimensions.
	:param player: The player whose turn it is, integer value of 1 or 2.
	:return: Column that the piece was dropped into, int.

	>>> cpu_player_hard(4, 2, [
	... [0, 0, 0],
	... [0, 0, 0],
	... [0, 0, 0],
	... ], 1)
	2
	>>> cpu_player_hard(4, 2, [
	... [0, 0, 0],
	... [0, 2, 0],
	... [1, 2, 0],
	... ], 1)
	2
	>>> cpu_player_hard(4, 2, [
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 0, 0, 0, 0],
	... [0, 0, 0, 1, 1, 0, 0],
	... [0, 0, 0, 1, 2, 0, 0],
	... [0, 0, 0, 1, 2, 0, 0],
	... ], 1)
	4
	"""
	num_cols = len(board[0])
	free_columns = get_free_columns(board)

	chosen_column = win_or_block_column(
		k, num_players, board, free_columns, player
	) or max(
		free_columns,
		key=lambda column: (
			column_score(k, num_players, board, player, column),
			# If there's a tie, pick the column closer to the middle
			# (num_cols + 1) / 2 is the middle column, so
			# abs((num_cols + 1) / 2 - column) is the distance to the center.
			# Because we want this number to be bigger for columns closer to the
			# center, we do num_cols - distance_from_the_center
			num_cols - abs((num_cols + 1) / 2 - column),
		),
	)
	assert drop_piece(board, player, chosen_column)
	return chosen_column


# endregion

# endregion

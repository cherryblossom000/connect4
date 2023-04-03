#!/usr/bin/env python3

"""
Utilities for testing (mainly `cpu_player_hard`).
"""

# pylint: disable=import-outside-toplevel

from argparse import ArgumentParser, Namespace
from pathlib import Path
import sys

from collections.abc import Sequence
from typing import Any, Callable

from common import (
	DRAW,
	GAME_NOT_OVER,
	Board,
	Column,
	Player,
	State,
	clear_screen,
	cpu_player_medium,
	cpu_player_hard,
	create_board,
	drop_piece,
	end_of_game,
	print_board,
)
from connect4 import K, NUM_COLS, NUM_PLAYERS, NUM_ROWS


def test():
	import doctest
	import common

	doctest.testmod(common, verbose=True)


def hard_vs_medium() -> State:
	board = create_board(NUM_ROWS, NUM_COLS)
	player = 1
	state = GAME_NOT_OVER
	while state == GAME_NOT_OVER:
		(cpu_player_medium if player == 1 else cpu_player_hard)(
			K, NUM_PLAYERS, board, player
		)
		state = end_of_game(K, board)
		player = player % NUM_PLAYERS + 1
	return state


def run_hard_cpu(num_games: int, progress: bool) -> dict[State, int]:
	from tqdm import tqdm

	result = {1: 0, 2: 0, DRAW: 0}
	if progress:
		for i in (progress_bar := tqdm(range(num_games))):
			result[hard_vs_medium()] += 1
			progress_bar.set_description(f"{result[2] / (i + 1):3.2%}")
	else:
		for i in range(num_games):
			result[hard_vs_medium()] += 1
	return result


def test_hard_cpu(num_games: int, progress: bool):
	result = run_hard_cpu(num_games, progress)
	print(f"{result[2] / num_games:3.2%}")
	print(f"  Wins: {result[2]}")
	print(f"Losses: {result[1]}")
	print(f" Draws: {result[DRAW]}")


def _run(num_games: int, _: int) -> int:
	return run_hard_cpu(num_games, False)[2]


def plot(num_games: int, count: int, out: str):
	from collections import Counter
	from functools import partial
	from statistics import mean
	from matplotlib import pyplot as plt, ticker
	from tqdm.contrib.concurrent import process_map

	data = process_map(partial(_run, num_games), range(count))
	# fmt: off
	# data = [99, 97, 95, 98, 97, 98, 97, 99, 96, 94, 96, 98, 95, 97, 98, 97, 98, 98, 99, 98, 94, 97, 96, 99, 97, 96, 98, 96, 93, 93, 93, 100, 96, 96, 99, 94, 96, 93, 95, 98, 98, 96, 93, 97, 94, 94, 98, 98, 100, 95, 95, 93, 97, 97, 95, 95, 93, 96, 99, 96, 97, 96, 96, 95, 90, 93, 94, 96, 97, 92, 94, 95, 100, 97, 98, 95, 91, 98, 97, 96, 97, 98, 96, 99, 98, 93, 99, 98, 97, 93, 98, 97, 93, 96, 93, 94, 92, 95, 95, 100]
	print(data)
	print(f"Average: {mean(data)} wins")
	counter = Counter(data)

	fig, ax = plt.subplots()
	ax.bar(*zip(*sorted(counter.items())), width=1)
	ax.set_xlabel("Number of wins")
	ax.set_xticks(list(counter.keys()))
	ax.set_ylabel("Frequency")
	ax.yaxis.set_major_locator(ticker.MultipleLocator(5))
	ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))
	fig.savefig(out)


def benchmark():
	from statistics import mean, stdev
	import timeit

	print("Playing 100 hard vs medium games 10 times:")
	result = timeit.repeat(hard_vs_medium, number=100, repeat=10)
	print(f"{mean(result):.3f} s ± {stdev(result):.3f} s")
	print(f"{min(result):.3f} s … {max(result):.3f} s")


def watch_game(play_turn: Callable[[Board, Player], Column]):
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
		input("Hit any key to play the next move")
		previous_column = play_turn(board, player)
		previous_player = player
		state = end_of_game(K, board)
		player = player % NUM_PLAYERS + 1
	clear_screen()
	print_board(K, NUM_PLAYERS, board)
	print(f"Player {previous_player} dropped a piece into column {previous_column}")
	assert state != GAME_NOT_OVER
	print("Draw" if state == DRAW else f"Player {state} wins!")
	input("Press any key to restart")


def watch_cpu_hard_vs_medium():
	while True:
		watch_game(
			# https://github.com/PyCQA/pylint/pull/8498
			# TODO: remove directive in pylint 2.17.2
			# pylint: disable-next=unnecessary-lambda
			lambda board, player: (
				cpu_player_medium if player == 1 else cpu_player_hard
			)(K, NUM_PLAYERS, board, player)
		)
		input("Press any key to restart")


def save_hard_cpu_losses(out_dir: Path):
	import json
	import os

	try:
		os.mkdir(out_dir)
	except FileExistsError:
		pass

	num_losses = 0
	for i in range(100):
		board = create_board(NUM_ROWS, NUM_COLS)
		player = 1
		state = GAME_NOT_OVER
		plays: list[Column] = []
		while state == GAME_NOT_OVER:
			plays.append(
				(cpu_player_medium if player == 1 else cpu_player_hard)(
					K, NUM_PLAYERS, board, player
				)
			)
			state = end_of_game(K, board)
			player = player % NUM_PLAYERS + 1
		if state == 1:
			num_losses += 1
			with open(out_dir / f"{i}.json", "w", encoding="utf8") as file:
				json.dump(plays, file)

	print(f"{num_losses} losses")


def load_and_watch_game(path: str):
	import json

	with open(path, "r", encoding="utf8") as file:
		columns = iter(json.load(file))

		def play_turn(board: Board, player: Player) -> Column:
			column = next(columns)
			assert drop_piece(board, player, column)
			return column

		watch_game(play_turn)


if __name__ == "__main__":
	parser = ArgumentParser(description=__doc__)
	subparsers = parser.add_subparsers()

	def add_subcmd(
		name: str,
		# pylint: disable-next=redefined-outer-name
		func: Callable[[Namespace], None],
		add_args: Callable[[ArgumentParser], Any] = lambda _: None,
		*,
		aliases: Sequence[str],
		# pylint: disable-next=redefined-builtin
		help: str,
	):
		subparser = subparsers.add_parser(name, aliases=aliases, help=help)
		add_args(subparser)
		subparser.set_defaults(func=func)

	add_subcmd("test", lambda _: test(), aliases=["t"], help="run the doctests")

	# Hard CPU
	def num_games_arg(subparser: ArgumentParser):
		subparser.add_argument(
			"number-of-games",
			type=int,
			nargs="?",
			default=100,
			help="the number of games to simulate (default: 100)",
		)

	add_subcmd(
		"test-hard-cpu",
		lambda args: test_hard_cpu(getattr(args, "number-of-games"), not args.quiet),
		lambda subparser: [
			num_games_arg(subparser),
			subparser.add_argument(
				"-q",
				"--quiet",
				action="store_true",
				help="suppress all output except the final result",
			),
		],
		aliases=["h"],
		help="test the hard CPU’s win rate against the medium CPU",
	)
	add_subcmd(
		"plot",
		lambda args: plot(
			getattr(args, "number-of-games"), args.count, args.output_file
		),
		lambda subparser: [
			num_games_arg(subparser),
			subparser.add_argument(
				"-n",
				"--count",
				type=int,
				default=100,
				help="the number of times to run the games (default: 100)",
			),
			subparser.add_argument(
				"-o",
				"--output-file",
				default="chart.png",
				help="the file for the chart (default: chart.png)",
			),
		],
		aliases=["p"],
		help="plays the hard CPU against the medium CPU for <number-of-games> games <count> times, and plots a chart of how many times the hard CPU player won",
	)
	add_subcmd(
		"bench",
		lambda _: benchmark(),
		aliases=["b"],
		help="benchmark running 100 games of the hard CPU vs the medium CPU",
	)

	# Debug Hard CPU
	add_subcmd(
		"watch-hard-game",
		lambda _: watch_cpu_hard_vs_medium(),
		help="watch the hard CPU player play against the medium CPU player",
		aliases=["w"],
	)
	add_subcmd(
		"save-hard-cpu-losses",
		lambda args: save_hard_cpu_losses(getattr(args, "out-dir")),
		lambda subparser: subparser.add_argument(
			"out-dir",
			type=Path,
			default=Path("losses"),
			help="the output directory",
		),
		aliases=["s"],
		help="run 100 games of the hard CPU against the medium CPU and save the games where the hard CPU lost (see also: `watch-game`)",
	)
	add_subcmd(
		"watch-game",
		lambda args: load_and_watch_game(args.file),
		lambda subparser: subparser.add_argument(
			"file", type=Path, help="the game file"
		),
		help="load and watch a game from a file (see also: `save-hard-cpu-losses`)",
		aliases=["l"],
	)

	args = parser.parse_args()
	func = getattr(args, "func", None)
	if func:
		# pylint: disable-next=not-callable
		func(args)
	else:
		parser.print_help()
		sys.exit(1)

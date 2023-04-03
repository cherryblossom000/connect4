# Connect 4

```sh
python3 connect4.py
python3 connectk.py
```

`connect4.py` is a simple 2-player Connect 4 game (local 2v2 or against one of 3
CPU difficulties). `connectk.py` allows you to customise the number of rows and
columns in the board, the number of tokens to win (k), and the number of player
in the game.

`util.py` is random stuff that helped me to improve `cpu_player_hard`. Run
`python3 util.py` for more details.

The external deps in `requirements.txt` is only used for `util.py`.

## `cpu_player_hard` Strategy

- Try to make an immediate win if possible, else
- Block the opponent from making an immediate win, else
- Plays the ‘best’ column according to these criteria (ordered by descending
  priority):
  - Don’t make a move that allows the opponent to win on their next turn
  - Form as many 3-in-a-rows as possible
  - Block the opponent from making 3-in-a-rows
  - Form as many 2-in-a-rows as possible
  - Pick the column closest to the center of the board

This is generalised for Connect K as well: it tries to form as many
`k-1`-in-a-rows as possible, then blocks the opponents from making
`k-1`-in-a-rows, then tries to form as many `k-2`-in-a-rows as possible etc.

Note how the CPU does *not* try to block the opponent from making 2-in-a-rows.
An older version of this code did do that, but it would do this (opponent is
`X`, CPU hard player is playing second and is `O`):

```none
- - - - - - -
- - - - - - -
- - - - - - -
- - - - - - -
- - - - - - -
X O - - - - -
```

instead of

```none
- - - - - - -
- - - - - - -
- - - - - - -
- - - - - - -
- - - - - - -
X - - O - - -
```

which is not ideal.

### Performance (for Connect 4)

These results are not very reliable as `cpu_player_medium` chooses a random
column most of the time.

100 games 100 times:

```none
❯ ./util.py plot
Average: 96.1 wins
```

![Bar chart showing frequency against number of wins. The chart roughly follows
a normal distribution with a slight negative skew. The least number of wins was
90 (which occurred once), and the greatest number of wins was 100 (which
occurred 4 times). The most frequent number of wins was 98, with 18
occurrences.](chart.png)

It takes around 5.2 seconds to run 100 games:

```none
❯ ./util.py bench
Playing 100 hard vs medium games 10 times:
5.221 s ± 0.419 s
4.509 s … 5.791 s
```

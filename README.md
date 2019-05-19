# Nine-Board-Tic-Tac-Toe-AI-Agent

## Introduction
An agent to play the game of Nine-Board Tic-Tac-Toe.
This game is played on a 3 x 3 array of 3 x 3 Tic-Tac-Toe boards. The first move is made by placing an X in a randomly chosen cell of a randomly chosen board. After that, the two players take turns placing an O or X alternately into an empty cell of the board corresponding to the cell of the previous move. (For example, if the previous move was into the upper right corner of a board, the next move must be made into the upper right board.)

The game is won by getting three-in-a row either horizontally, vertically or diagonally in one of the nine boards. If a player is unable to make their move (because the relevant board is already full) the game ends in a draw.

## Getting Started
Clone this repo then type
```
cd src
make all
```
```
./servt -x -o
```
You should then see something like this:
```
 . . . | . . . | . . .
 . . . | . . . | . . .
 . . . | . . . | . . .
 ------+-------+------
 . . . | . . . | . . .
 . . . | . . . | . . .
 . . . | . . x | . . .
 ------+-------+------
 . . . | . . . | . . .
 . . . | . . . | . . .
 . . . | . . . | . . .

next move for O ?  
```
You can now play Nine-Board Tic-Tac-Toe against yourself, by typing a number for each move. 
The cells in each board are numbered 1, 2, 3, 4, 5, 6, 7, 8, 9 as follows:
```
+-----+
|1 2 3|
|4 5 6|
|7 8 9|
+-----+
```
To play against a computer player, you need to open another terminal window (and cd to the src directory).

Type this into the first window:

`./servt -p 12345 -x`
This tells the server to use port 12345 for communication, and that the moves for X will be chosen by you, the human, typing at the keyboard. (If port 12345 is busy, choose another 5-digit number.)
You should then type this into the second window (using the same port number):

`./randt -p 12345`
The program randt simply chooses each move randomly among the available legal moves.
The Prolog program random.pl behaves in exactly the same way. You can play against it by typing this into the second window:

`prolog 12345 < agent.wrap`
You can play against a slightly more sophisticated player by typing this into the second window:
`./lookt -p 12345`
(If you are using a Mac, type ./lookt.mac instead of ./lookt)
To play two computer programs against each other, you may need to open three windows. For example, to play agent against lookt using port 54321, type as follows:
```
window 1:	./servt -p 54321
window 2:	./agent -p 54321
window 3:	./lookt -p 54321
```
(Whichever program connects first will play X; the other program will play O.)
Alternatively, you can launch all three programs from a single window by typing
```
./servt -p 54321 &
./agent -p 54321 &
./lookt -p 54321
```
or, using a shell script:
```
./playc.sh lookt 54321
```
To play the prolog program agent.pl against lookt using port 23232, you can type
```
./servt -p 23232 &
prolog 23232 < agent.wrap &
./lookt -p 23232
```
or, using a shell script:
```
./playpl.sh lookt 23232
```
(If you are using a Mac, edit playpl.sh and replace "prolog" with "swipl")
The strength of lookt can be adjusted by specifying a maximum search depth (default value is 9; reasonable range is 1 to 18), e.g.
```
./lookt -p 12345 -d 6
```
or
```
./playc.sh "lookt -d 16" 54321
```
To play the python program agent.py against lookt using port 55555, you can type
```
./servt -p 23232 &
python3 agent.py -p 23232
./lookt -p 23232
```
or, using a shell script:
```
./playpy.sh lookt 23232
```

## How it works
Communication between the server and the player(s) is illustrated in this brief example:
```
Player X		Server		Player O
      ←	init
                  init	→
      ←	start(x)
              start(o)	→
      second_move(6,1)	→
      ←	7
      ←	third_move(6,1,7)	
                      9	→		
          next_move(9)	→
      ←	6
      ←	next_move(6)	
                      5	→		
          last_move(5)	→
      ←	win(triple)	
          loss(triple)	→
      ←	end
                    end	→
```
Language Options
The agent is available in many languages.
Prolog:
```
prolog (port) < agent.wrap
```
C:
```
./agent -p (port)
```
Python
```
python3 agent.py -p (port)
```

#!/usr/bin/python3
"""
  COMP9414 Assignment 3:  Nine-Board Tic-Tac-Toe
  Team name: WhateverWeLike
  Team member:
    - Kuan-Chun Hwang - SID: z5175539
    - Zhounan Wang    - SID: z5179018

  This program can be run by:
    python3 agent.py -p <port number>
  
  Design and data structure:
  When the above line is called, it attempts to connect to the port specified and waits
  for instruction from the server. After recieving instruction from the server, we use 
  regular expression to process the message from server and call the relevant function related 
  to that message.

  We also used a custom data structure called Point to store each point such that they all have a 
  board number and the position they are on that board. This was created to make computation and
  information passing easy. 

  During initialisation, we set a board using a 10x10 matrix with the 0th index not being 
  used. This design choice was made because the server sends instructions from 1 to 9 and 
  not 0 to 8 so we chose to follow the same scheme instead of doing our own translation, 
  even though this causes some more wasted space. In init, we initialise the 9 smaller boards
  each store in an array of length 10. We then set the agent to the player the server instructed
  as to be. We also precompute all possible score for a small board during initialisation for
  time efficiency after.

  When recieving a move from opponent, the program first put that move onto the board inside 
  the agent's memory. We then explore all possible moves based on the opponent's move. For example,
  when the opponent place in cell 1 of a small board, in our next move, we can only choose an 
  available space inside board 1 of the whole game board. After getting all available moves, 
  we start our alpha beta pruning tree search. 

  Algorithm:
  Our agent uses alpha beta pruning to identify the best possible move in the current scenario.
  At each step, our heuristic function evaluate all the smaller board's score and then we sum
  everything to get the score of the whole game board. In the small board score calculation,
  we give a board a very large score if we win the board, which is also the game, or a 
  very small score if we lost the board. Then for the cases where we have an edge, we give it
  a higher score based on how much advantage we have. Vice versa, we do the opposite for boards
  where we have an disadvantage. We also give bonuses to those score such that if the position 
  held was the center, we give it a higher multiplicative bonus and if it was in the corder, we
  give it a smaller multiplicative bonus. We compute advantage and disadvantage by counting how
  many X's and O's are on each row, column and diagonal of the board.

  Also, at each depth of recursion, if we can win the game we give it a super large score multiplied 
  by maxdepth - current depth. This will make the agent priortise the shorter paths to win and avoid
  shorter paths to lose. We also give a positive score if there is no available move such that our 
  agent will also try to go for draws instead. This decision was made to prioritise not losing instead
  of always wanting to win. Also, when we calculate the whole game board score, we also store the 
  score of this board. This should save up some computation time such that we don't need to keep repetitively
  looking at boards we have already computed before. Finally, at last from alpha beta pruning, we 
  get the move with the best score. In the cases where there are multiple best moves, we randomly
  select one.

  We also do increasing in recursion depth as the game goes. Initially, when the game just started,
  there are too many paths to explore so it is very easy to time out. However, as the game goes on,
  we can start increasing the depth limit since there are less path now. This also increase the 
  strength of the agent since it can see further into the future now. We increase depth after 9 moves
  and then after that we increase by 1 every 3 moves. If we reach more then 17 moves, we increase
  by 2 every time. These depth variation values were found based on trial and error testing.
"""
import sys
import argparse
import socket
import re
import time
import random
import datetime
import itertools
import copy

MAX_MOVE = 81
MAX_DEPTH = 6

class Point:
  def __init__(self, board_num, pos):
    self.board_num = board_num
    self.pos = pos

class Agent:
  def __init__(self):
    # Initiate a tic tac toe board where each list represent a board. There are
    # 9 boards in total
    self.board = [['.' for _ in range(10)] for _ in range(10)]
    self.player, self.m = None, None
    self.move = [-1]*MAX_MOVE
    self.result, self.cause = None, None
    self.scores = []
    self.max_depth = MAX_DEPTH
    self.center = set([5])
    self.corners = set([1, 3, 7, 9])
    self.seen_large = dict()
    self.seen_small = dict()
    self.step_count = 0

  def precompute_small(self):
    board = [[]]
    for comb in itertools.product(['x', 'o', '.'], repeat=9):
      mini_board = ['.']
      mini_board.extend(list(comb))
      self.seen_small[str(mini_board)] = self.calculate_heuristic_score(mini_board)

  def calculate_heuristic_score(self, mini_board):
    """Calculate the heuristic function's value
    score = Number of row/column/diagonal opponent can win -  Number of row/column/diagonal player can win 
    """
    if str(mini_board) in self.seen_small:
      return self.seen_small[str(mini_board)]
    score = 0
    # row score
    score += self.calculate_score(1, 2, 3, mini_board)
    score += self.calculate_score(4, 5, 6, mini_board)
    score += self.calculate_score(7, 8, 9, mini_board)
    # column score
    score += self.calculate_score(1, 4, 7, mini_board)
    score += self.calculate_score(2, 5, 8, mini_board)
    score += self.calculate_score(3, 6, 9, mini_board)
    # diagonal score
    score += self.calculate_score(1, 5, 9, mini_board)
    score += self.calculate_score(3, 5, 7, mini_board)
    self.seen_small[str(mini_board)] = score
    return score

  def calculate_score(self, idx1, idx2, idx3, mini_board):
    a, b, c = mini_board[idx1], mini_board[idx2], mini_board[idx3]
    player_win, player_lose, bonus = 0, 0, 1
    player = self.player
    if a == player:
      player_win += 1
    elif a != '.':
      player_lose += 1
    if b == player:
      player_win += 1
    elif b != '.':
      player_lose += 1
    if c == player:
      player_win += 1
    elif c != '.':
      player_lose += 1

    if b != '.' and b in self.center:
      bonus *= 5
    if a != '.' and a in self.corners:
      bonus *= 2
    if c != '.' and c in self.corners:
      bonus *= 2

    # Check who has the advantage and return a relative score
    if player_lose == 3:
      return -1000*bonus
    elif player_win == 3:
      return 10000*bonus
    elif player_win == 0 and player_lose == 2:
      return -30*bonus
    elif player_win == 2 and player_lose == 0:
      return 30*bonus
    elif player_win == 0 and player_lose == 1:
      return -1*bonus
    elif player_win == 1 and player_lose == 0:
      return 1*bonus
    return 0  # No one has an advantage in other cases so return a neutral value

  def get_available_moves(self, prev_move):
    mini_board = self.board[prev_move]
    available_moves = []
    for i in range(1, len(mini_board)):
      if mini_board[i] == '.':
        available_moves.append(Point(prev_move, i))
    return available_moves # if available_moves, then the game ends in a draw

  def make_move(self, point , player):
    self.board[point.board_num][point.pos] = player
    return point.pos  # return the new pre_move

  def make_best_move(self, prev_move):
    available_moves = self.get_available_moves(prev_move)
    best_moves, best_move_score = [], -float('inf')
    opponent = 'o' if self.player == 'x' else 'x'
    for point in available_moves:
      prev_move = self.make_move(point, self.player)
      move_score = self.alpha_beta(1, opponent, -float('inf'), float('inf'), prev_move)
      self.board[point.board_num][point.pos] = '.'
      if move_score > best_move_score:
        best_moves, best_move_score = [point.pos], move_score
      elif move_score == best_move_score:
        best_moves.append(point.pos)
    return random.choice(best_moves)

  def alpha_beta(self, depth, player, alpha, beta, prev_move):
    available_moves = self.get_available_moves(prev_move)
    opponent = 'o' if self.player == 'x' else 'x'
    # terminate early if we already found a winning move. Give winning move with 
    # a short depth more score
    if self.someone_won(self.player):
      return 1000000*(self.max_depth+1 - depth)
    else:
      if self.someone_won(opponent):
        return -100000*(self.max_depth+1 - depth)
    if not available_moves:
      return 1000
    # Call heursitic to evaluate the score straight away when max depth reached.
    if depth == self.max_depth:
      if str(self.board) not in self.seen_large:
        score = 0
        for i in range(1, len(self.board)):
          score += self.calculate_heuristic_score(self.board[i])
        self.seen_large[str(self.board)] = score
      else:
        score = self.seen_large[str(self.board)]
      return score

    if player == self.player:
      for point in available_moves:
        prev_move = self.make_move(point, player)
        new_score = self.alpha_beta(depth+1, opponent, alpha, beta, prev_move)
        alpha = max(alpha, new_score)
        # Reset board
        self.board[point.board_num][point.pos] = '.'
        if alpha >= beta:
          return alpha
      return alpha
    else:
      for point in available_moves:
        prev_move = self.make_move(point, player)
        new_score = self.alpha_beta(depth+1, self.player, alpha, beta, prev_move)
        beta = min(beta, new_score)
        # Reset board
        self.board[point.board_num][point.pos] = '.'
        if beta <= alpha:
          return beta
      return beta

  def someone_won(self, player):
    return any([self.someone_won_single(i, player) for i in range(len(self.board))])

  def someone_won_single(self, board_num, player):
    mini_board = self.board[board_num]
    return True if ((mini_board[1] == mini_board[2] == mini_board[3]) and mini_board[1] == player) or \
                   ((mini_board[4] == mini_board[5] == mini_board[6]) and mini_board[4] == player) or \
                   ((mini_board[7] == mini_board[8] == mini_board[9]) and mini_board[7] == player) or \
                   ((mini_board[1] == mini_board[4] == mini_board[7]) and mini_board[1] == player) or \
                   ((mini_board[2] == mini_board[5] == mini_board[8]) and mini_board[2] == player) or \
                   ((mini_board[3] == mini_board[6] == mini_board[9]) and mini_board[3] == player) or \
                   ((mini_board[1] == mini_board[5] == mini_board[9]) and mini_board[1] == player) or \
                   ((mini_board[3] == mini_board[5] == mini_board[7]) and mini_board[3] == player) else False

  def init(self):
    """On init, we reset everything? 
    not sure if we need to set random seed like agent.c
    """
    random.seed(datetime.datetime.now().second)
    self.player, self.m = None, None
    self.move = [-1]*MAX_MOVE
    self.result, self.cause = None, None
    return None
  
  def reset_board(self):
    self.board = [['.' for _ in range(10)] for _ in range(10)]

  def print_board_row(self, a, b, c, i, j, k):
    result = ''
    result += ' {} {} {} |'.format(self.board[a][i], self.board[a][j], self.board[a][k])
    result += ' {} {} {} |'.format(self.board[b][i], self.board[b][j], self.board[b][k])
    result += ' {} {} {} |\n'.format(self.board[c][i], self.board[c][j], self.board[c][k])
    return result

  def print_board(self):
    result = ''
    result += self.print_board_row(1, 2, 3, 1, 2, 3)
    result += self.print_board_row(1, 2, 3, 4, 5, 6)
    result += self.print_board_row(1, 2, 3, 7, 8, 9)
    result += ' ------+-------+-------\n'
    result += self.print_board_row(4, 5, 6, 1, 2, 3)
    result += self.print_board_row(4, 5, 6, 4, 5, 6)
    result += self.print_board_row(4, 5, 6, 7, 8, 9)
    result += ' ------+-------+-------\n'
    result += self.print_board_row(7, 8, 9, 1, 2, 3)
    result += self.print_board_row(7, 8, 9, 4, 5, 6)
    result += self.print_board_row(7, 8, 9, 7, 8, 9)
    return result

  def start(self, player):
    self.reset_board()
    self.m = 0
    self.move[self.m] = 0
    self.player = player
    self.precompute_small()
    return None

  def second_move(self, board_num, prev_move):
    self.move[0], self.move[1] = board_num, prev_move
    opponent = 'o' if self.player == 'x' else 'x'
    self.board[board_num][prev_move] = opponent
    self.m = 2

    this_move = self.make_best_move(prev_move)

    self.move[self.m] = this_move
    self.board[prev_move][this_move] = self.player
    return this_move


  def third_move(self, board_num, first_move, prev_move):
    self.move[0], self.move[1], self.move[2] = board_num, first_move, prev_move
    opponent = 'o' if self.player == 'x' else 'x'
    self.board[board_num][first_move] = self.player
    self.board[first_move][prev_move] = opponent
    self.m = 3
    self.step_count += 1

    this_move = self.make_best_move(prev_move)

    self.move[self.m] = this_move
    self.board[self.move[self.m-1]][this_move] = self.player
    return this_move

  def next_move(self, prev_move):
    self.m+=1
    self.move[self.m] = prev_move
    opponent = 'o' if self.player == 'x' else 'x'
    self.board[self.move[self.m-1]][self.move[self.m]] = opponent
    self.m+=1
    self.step_count+=1
    # depth variaiton
    if self.step_count>8:
      if not self.step_count%3 and self.step_count < 16:
        self.max_depth += 1
      elif not self.step_count%2 and self.step_count >= 17 and self.max_depth < 14:
        self.max_depth += 1

    this_move = self.make_best_move(prev_move)

    self.move[self.m] = this_move
    self.board[self.move[self.m-1]][this_move] = self.player
    return this_move

  def last_move(self, prev_move):
    self.m+=1
    self.move[self.m] = prev_move
    self.board[self.move[self.m-1]][self.move[self.m]] = 'o' if self.player == 'x' else 'x'

  def win(self, cause):
    self.result = 'WIN'
    self.cause = cause
    # print('>'*50, self.result)

  def loss(self, cause):
    self.result = 'LOSS'
    self.cause = cause
    # print('>'*50, self.result)

  def draw(self, cause):
    self.result = 'DRAW'
    self.cause = cause
    # print('>'*50, self.result)

  def end(self):
    sys.exit()

  def process_data(self, data):
    if re.match('init', data):
      self.init()
    elif re.match('start\((.+)\)', data):
      player = re.search('start\((.+)\)', data).group(1)
      self.start(player)
    elif re.match('second_move\(\d+,\d+\)', data):
      args = re.search('second_move\((\d+),(\d+)\)', data)
      board_num, prev_move = int(args.group(1)), int(args.group(2))
      return self.second_move(board_num, prev_move)
    elif re.match('third_move\(\d+,\d+,\d+\)', data):
      args = re.search('third_move\((\d+),(\d+),(\d+)\)', data)
      board_num, first_move, prev_move = int(args.group(1)), int(args.group(2)), int(args.group(3))
      return self.third_move(board_num, first_move, prev_move)
    elif re.match('next_move\(\d+\)', data):
      prev_move = int(re.search('next_move\((\d+)\)', data).group(1))
      return self.next_move(prev_move)
    elif re.match('last_move\(\d+\)', data):
      last_move = int(re.search('last_move\((\d+)\)', data).group(1))
      return self.last_move(last_move)
    elif re.match('win\(.*\)', data):
      cause = re.search('win\((.+)\)', data)
      self.win(cause)
    elif re.match('loss\(.*\)', data):
      cause = re.search('win\((.+)\)', data)
      self.loss(cause)
    elif re.match('draw\(.*\)', data):
      cause = re.search('win\((.+)\)', data)
      self.draw(cause)
    elif re.match('end', data):
      self.end()


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", type=int, help="Usage: python agent.py -p <port>")
  args = parser.parse_args()
  if not args.p:
    sys.exit("Usage: python agent.py -p <port>")
  port = args.p

  agent = Agent()
  
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  client.connect(("localhost", port))

  while True:
    data = client.recv(1024).decode().rstrip()
    if not data:
      break
    commands = data.split('\n')
    for command in commands:
      response = agent.process_data(command)
      if response is not None:
        client.send('{}\n'.format(str(response)).encode())

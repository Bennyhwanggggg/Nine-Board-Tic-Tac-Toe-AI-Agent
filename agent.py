#!/usr/bin/python3

import sys
import argparse
import socket
import re
import time
import random
import datetime
import heapq
import logging
import copy
from uuid import uuid4

MAX_MOVE = 81
MAX_DEPTH = 6

LOG_FORMAT = "%(levelname)s:\n%(message)s"
logging.basicConfig(format=LOG_FORMAT)
logger = logging.getLogger(__name__)
# Change the level to logging.DEBUG or logging.INFO for more messages on console. logging.ERROR or logging.WARNING to hide
logger.setLevel(level=logging.ERROR)

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
    # self.precompute_small()

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
      return self.seen_small[str(mini_board)], self.seen_small
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
    return score, self.seen_small

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
      move_score, self.seen_large = self.alpha_beta(1, opponent, -float('inf'), float('inf'), prev_move)
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
      return 1000000*(self.max_depth+1 - depth), self.seen_large
    else:
      if self.someone_won(opponent):
        return -100000*(self.max_depth+1 - depth), self.seen_large
    if not available_moves:
      return 0, self.seen_large
    # Call heursitic to evaluate the score straight away when max depth reached.
    if depth == self.max_depth:
      # _, best_move_score = self.make_move_mct(prev_move)
      # return best_move_score
      if str(self.board) not in self.seen_large:
        score = 0
        for i in range(1, len(self.board)):
          result, self.seen_small = self.calculate_heuristic_score(self.board[i])
          score += result
        self.seen_large[str(self.board)] = score
      else:
        score = self.seen_large[str(self.board)]
      return score, self.seen_large

    if player == self.player:
      for point in available_moves:
        prev_move = self.make_move(point, player)
        new_score, self.seen_large = self.alpha_beta(depth+1, opponent, alpha, beta, prev_move)
        alpha = max(alpha, new_score)
        # Reset board
        self.board[point.board_num][point.pos] = '.'
        if alpha >= beta:
          return alpha, self.seen_large
      return alpha, self.seen_large
    else:
      for point in available_moves:
        prev_move = self.make_move(point, player)
        new_score, self.seen_large = self.alpha_beta(depth+1, self.player, alpha, beta, prev_move)
        beta = min(beta, new_score)
        # Reset board
        self.board[point.board_num][point.pos] = '.'
        if beta <= alpha:
          return beta, self.seen_large
      return beta, self.seen_large

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
    logger.info('Agent initalised')
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

  def print_board_row_mct(self, board, a, b, c, i, j, k):
    result = ''
    result += ' {} {} {} |'.format(board[a][i], board[a][j], board[a][k])
    result += ' {} {} {} |'.format(board[b][i], board[b][j], board[b][k])
    result += ' {} {} {} |\n'.format(board[c][i], board[c][j], board[c][k])
    return result

  def print_board_mct(self, board):
    result = ''
    result += self.print_board_row_mct(board, 1, 2, 3, 1, 2, 3)
    result += self.print_board_row_mct(board, 1, 2, 3, 4, 5, 6)
    result += self.print_board_row_mct(board, 1, 2, 3, 7, 8, 9)
    result += ' ------+-------+-------\n'
    result += self.print_board_row_mct(board, 4, 5, 6, 1, 2, 3)
    result += self.print_board_row_mct(board, 4, 5, 6, 4, 5, 6)
    result += self.print_board_row_mct(board, 4, 5, 6, 7, 8, 9)
    result += ' ------+-------+-------\n'
    result += self.print_board_row_mct(board, 7, 8, 9, 1, 2, 3)
    result += self.print_board_row_mct(board, 7, 8, 9, 4, 5, 6)
    result += self.print_board_row_mct(board, 7, 8, 9, 7, 8, 9)
    return result

  def start(self, player):
    self.reset_board()
    self.m = 0
    self.move[self.m] = 0
    self.player = player
    logger.info('Agent is starting. Player is: {}'.format(self.player))
    return None

  def second_move(self, board_num, prev_move):
    self.move[0], self.move[1] = board_num, prev_move
    opponent = 'o' if self.player == 'x' else 'x'
    self.board[board_num][prev_move] = opponent
    self.m = 2
    logger.info('Agent starting second move, board looks like:')
    logger.info(self.print_board())

    this_move = self.make_best_move(prev_move)
    # this_move = self.make_move_mct(prev_move)

    self.move[self.m] = this_move
    self.board[prev_move][this_move] = self.player
    logger.info('Agent ran second move with the best move being: {}\nThe board now looks like:'.format(this_move))
    logger.info(self.print_board())
    return this_move


  def third_move(self, board_num, first_move, prev_move):
    self.move[0], self.move[1], self.move[2] = board_num, first_move, prev_move
    opponent = 'o' if self.player == 'x' else 'x'
    self.board[board_num][first_move] = self.player
    self.board[first_move][prev_move] = opponent
    self.m = 3
    logger.info('Agent starting third move, board looks like:')
    logger.info(self.print_board())

    this_move = self.make_best_move(prev_move)
    # this_move = self.make_move_mct(prev_move)

    self.move[self.m] = this_move
    self.board[self.move[self.m-1]][this_move] = self.player
    logger.info('Agent ran third move with the best move being: {}\nThe board now looks like:'.format(this_move))
    logger.info(self.print_board())
    return this_move

  def next_move(self, prev_move):
    self.m+=1
    self.move[self.m] = prev_move
    opponent = 'o' if self.player == 'x' else 'x'
    self.board[self.move[self.m-1]][self.move[self.m]] = opponent
    self.m+=1
    self.step_count+=1
    if self.step_count>7 and self.max_depth < 17:
      if not self.step_count%4:
        self.max_depth += 1
    logger.info('Agent starting next move, board looks like:')
    logger.info(self.print_board())

    this_move = self.make_best_move(prev_move)
    # this_move = self.make_move_mct(prev_move)

    self.move[self.m] = this_move
    self.board[self.move[self.m-1]][this_move] = self.player
    logger.info('Agent ran next move with the best move being: {}\nThe board now looks like:'.format(this_move))
    logger.info(self.print_board())
    return this_move

  def last_move(self, prev_move):
    self.m+=1
    self.move[self.m] = prev_move
    self.board[self.move[self.m-1]][self.move[self.m]] = 'o' if self.player == 'x' else 'x'
    logger.info('Agent ran last move and the board now looks like:')
    logger.info(self.print_board())

  def win(self, cause):
    self.result = 'WIN'
    self.cause = cause
    print('>'*50, self.result)

  def loss(self, cause):
    self.result = 'LOSS'
    self.cause = cause
    print('>'*50, self.result)

  def draw(self, cause):
    self.result = 'DRAW'
    self.cause = cause
    print('>'*50, self.result)

  def end(self):
    logger.info('Agent closing.')
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
      # print('Recieved from server:', command)
      response = agent.process_data(command)
      if response is not None:
        # print('Sending to server:', response)
        client.send('{}\n'.format(str(response)).encode())
      else:
        # print('The previous command: {} -- required no response'.format(command))
        continue


    
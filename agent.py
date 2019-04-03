#!/usr/bin/python3

import sys
import argparse
import socket
import re
import time
import random
import datetime

MAX_MOVE = 81

class Agent:
  def __init__(self):
    # Initiate a tic tac toe board where each list represent a board. There are
    # 9 boards in total
    self.board = [['.' for _ in range(10)] for _ in range(10)]
    self.player, self.m = None, None
    self.move = [-1]*MAX_MOVE
    self.result, self.cause = None, None

  def init(self):
    """On init, we reset everything? 
    not sure if we need to set random seed like agent.c
    """
    random.seed(datetime.datetime.now().second)
    self.player, self.m = None, None
    self.move = [-1]*MAX_MOVE
    self.result, self.cause = None, None
    print('Agent initalised')
    return None
    

  def reset_board(self):
    self.board = [['.' for _ in range(10)] for _ in range(10)]

  def print_board_row(self, a, b, c, i, j, k):
    print(' {} {} {} '.format(self.board[a][i], self.board[a][j], self.board[a][k]), end='|')
    print(' {} {} {} '.format(self.board[b][i], self.board[b][j], self.board[b][k]), end='|')
    print(' {} {} {} '.format(self.board[c][i], self.board[c][j], self.board[c][k]), end='|\n')

  def print_board(self):
    self.print_board_row(1, 2, 3, 1, 2, 3)
    self.print_board_row(1, 2, 3, 4, 5, 6)
    self.print_board_row(1, 2, 3, 7, 8, 9)
    print(' ------+-------+-------')
    self.print_board_row(4, 5, 6, 1, 2, 3)
    self.print_board_row(4, 5, 6, 4, 5, 6)
    self.print_board_row(4, 5, 6, 7, 8, 9)
    print(' ------+-------+-------')
    self.print_board_row(7, 8, 9, 1, 2, 3)
    self.print_board_row(7, 8, 9, 4, 5, 6)
    self.print_board_row(7, 8, 9, 7, 8, 9)

  def start(self, player):
    self.reset_board()
    self.m = 0
    self.move[self.m] = 0
    self.player = player
    print('Agent is starting. Player is:', self.player)
    return None

  def second_move(self, board_num, prev_move):
    self.move[0], self.move[1] = board_num, prev_move
    self.board[board_num][prev_move] = 'o' if self.player == 'x' else 'x'
    self.m = 2
    this_move = random.randint(1, 9)
    while self.board[prev_move][this_move] != '.':
      this_move = random.randint(1, 9)
    self.move[self.m] = this_move
    self.board[prev_move][this_move] = self.player
    print('Agent ran second move and the board now looks like:')
    self.print_board()
    return this_move


  def third_move(self, board_num, first_move, prev_move):
    self.move[0], self.move[1], self.move[2] = board_num, first_move, prev_move
    self.board[board_num][first_move] = 'x' if self.player == 'x' else 'o'
    self.board[first_move][prev_move] = 'o' if self.player == 'x' else 'x'
    self.m = 3
    this_move = random.randint(1, 9)
    while self.board[prev_move][this_move] != '.':
      this_move = random.randint(1, 9)
    self.move[self.m] = this_move
    self.board[self.move[self.m-1]][this_move] = self.player
    print('Agent ran third move and the board now looks like:')
    self.print_board()
    return this_move

  def next_move(self, prev_move):
    self.m+=1
    self.move[self.m] = prev_move
    self.board[self.move[self.m-1]][self.move[self.m]] = 'o' if self.player == 'x' else 'x'
    self.m+=1
    this_move = random.randint(1, 9)
    while self.board[prev_move][this_move] != '.':
      this_move = random.randint(1, 9)
    self.move[self.m] = this_move
    self.board[self.move[self.m-1]][this_move] = self.player
    print('Agent ran next move and the board now looks like:')
    self.print_board()
    return this_move

  def last_move(self, prev_move):
    self.m+=1
    self.move[self.m] = prev_move
    self.board[self.move[self.m-1]][self.move[self.m]] = 'o' if self.player == 'x' else 'x'
    print('Agent ran last move and the board now looks like:')
    self.print_board()

  def win(self, cause):
    self.result = 'WIN'
    self.cause = cause

  def loss(self, cause):
    self.result = 'LOSS'
    self.cause = cause

  def draw(self, cause):
    self.result = 'DRAW'
    self.cause = cause

  def end(self):
    print('Agent closing.')
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
      print('Recieved from server:', command)
      response = agent.process_data(command)
      time.sleep(0.1)
      if response:
        print('Sending to server:', response)
        client.send('{}\n'.format(str(response)).encode())
      else:
        print('The previous command required no response')


    
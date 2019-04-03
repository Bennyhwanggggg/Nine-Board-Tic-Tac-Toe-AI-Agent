#!/usr/bin/python3

import sys
import argparse
import socket
import re
import time

class Agent:
  def __init__(self):
    # Initiate a tic tac toe board where each list represent a board. There are
    # 9 boards in total
    self.board = [['.' for _ in range(10)] for _ in range(10)]

  def init(self):
    """On init, we reset everything.
    """
    self.reset_board()
    return

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
    pass

  def second_move(self, board_num, prev_move):
    pass

  def third_move(self, board_num, first_move, prev_move):
    pass

  def next_move(self, prev_move):
    pass

  def last_move(self, prev_move):
    pass

  def win(self):
    pass

  def loss(self):
    pass

  def draw(self):
    pass

  def end(self):
    pass

  def process_data(self, data):
    if re.match('init.', data):
      self.init()
    elif re.match('start(.+).', data):
      player = re.search('start(.+).', data).group(1)
      self.start(player)
    elif re.match('second_move(\d+,\d+).'):
      args = re.search('second_move(\d+,\d+).', data)
      board_num, prev_move = args.group(1), args.group(2)
      self.second_move(board_num, prev_move)
    elif re.match('third_move(\d+,\d+,\d+).'):
      args = re.search('third_move(\d+,\d+,\d+).', data)
      board_num, first_move, prev_move = args.group(1), args.group(2), args.group(3)
      self.third_move(board_num, first_move, prev_move)
    elif re.match('next_move(\d+).'):
      prev_move = re.search('next_move(\d+).', data).group(1)
      self.next_move(prev_move)
    elif re.match('last_move(\d+).'):
      last_move = re.search('last_move(\d+).').group(1)
    elif re.match('win(.*)'):
      self.win()
    elif re.match('loss(.*)'):
      self.loss()
    elif re.match('draw(.*)'):
      self.draw()
    elif re.match('end'):
      self.end()



if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", type=int, help="Usage: python agent.py -p <port>")
  args = parser.parse_args()
  if not args.p:
    sys.exit("Usage: python agent.py -p <port>")
  port = args.p

  agent = Agent()
  agent.print_board()
  sys.exit()
  
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  client.connect(("localhost", port))

  while True:
    data = client.recv(1024).decode('utf-8')
    if not data:
      break
    print(data)
    agent.process_data(data)
    time.sleep(0.1)


    
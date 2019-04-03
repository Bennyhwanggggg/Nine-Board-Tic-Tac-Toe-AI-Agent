#!/usr/bin/python3

import sys
import argparse
import socket
import re
import time

class Agent:
  def __init__(self):
    self.board = []  # TODO: make this tic tac toe board?
    self.action_map = {
      'init': self.init,
      'start': self.start,
      'second_move': self.second_move,
      'third_move': self.third_move,
      'last_move': self.last_move,
      'win': self.win,
      'loss': self.loss,
      'draw': self.draw,
      'end': self.end
    }

  def init(self):
    pass

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


    
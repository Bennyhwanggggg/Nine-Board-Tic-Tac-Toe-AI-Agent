#!/usr/bin/python3

import argparse
import sockets

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("-p", default=12345, help="Port number of the server to connect to")


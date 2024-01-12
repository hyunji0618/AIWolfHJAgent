import warnings
from argparse import ArgumentParser

from aiwolf import AbstractPlayer, TcpipClient

from hyunji_agent import HyunjiPlayer
from analyzer import Analyzer
from random import randint
from read_log import read_log

if __name__ == "__main__":
    agent: AbstractPlayer = HyunjiPlayer('KimAgent')
    parser: ArgumentParser = ArgumentParser(add_help=False)
    parser.add_argument("-p", type=int, action="store", dest="port", required=True)
    parser.add_argument("-h", type=str, action="store", dest="hostname", required=True)
    parser.add_argument("-r", type=str, action="store", dest="role", default="none")
    parser.add_argument("-n", type=str, action="store", dest="name", required=True)
    input_args = parser.parse_args()

    TcpipClient(agent, input_args.name, input_args.hostname, input_args.port, input_args.role).connect()

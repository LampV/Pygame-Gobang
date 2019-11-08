# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/07
# pygame Cheese 小游戏
# ---------------------------------------

from CheeseAgent import CheeseDQN
from CheeseEnv import CheeseENV
import pygame
from sys import exit
from pygame.locals import *

if __name__ == '__main__':
    cheese_border_size = 15
    env = CheeseENV(border_count=cheese_border_size, line_margin=40)
    agent = CheeseDQN(cheese_border_size * cheese_border_size, cheese_border_size * cheese_border_size)
    while True:  # 这是维持游戏循环进行的循环
        state = env.reset()  # 每局游戏开始之前重置环境
        while True:  # 这是每一局游戏内部接受落子的循环
            action = None
            if env.get_color() == 1:  # 黑棋，则由人输入
                for event in pygame.event.get():  # 这是pygame接受输入的循环，直到退出或者落子为止
                    # 点击叉时退出
                    if event.type == QUIT:
                        exit()
                    # 按下Esc时退出
                    if event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            exit()
                    # 如果按下鼠标，检查落子，判断游戏是否结束
                    if event.type == MOUSEBUTTONDOWN:
                        x, y = event.pos
                        # 将点击位置转换为棋盘上的点
                        row, col = env.point_convert(x, y)
                        action = (row, col)
                        if action == (-1, -1) or env.has_piece(action):
                            action = None
                        break
            else:  # 白棋，则由agent输入
                action = agent.get_action(state)
                action = (action // cheese_border_size, action % cheese_border_size)

            if action:
                next_state, reward, done, _ = env.step(action)
                if done:
                    break
                state = next_state

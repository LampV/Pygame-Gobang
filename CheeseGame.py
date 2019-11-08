# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/07
# pygame Cheese 小游戏
# ---------------------------------------
import argparse

from CheeseAgent import CheeseDQN
from CheeseEnv import CheeseENV
import pygame
from sys import exit
from pygame.locals import *


def human_action(env):
    """获取人类落子动作"""
    while True:
        _action = None
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
                _action = (row, col)
                if _action == (-1, -1) or env.has_piece(_action):
                    _action = None
                break
        if _action:
            return _action


def ai_vs_ai():
    cheese_border_size = 15
    env = CheeseENV(enable_pygame=False, border_count=cheese_border_size, line_margin=40)
    black_agent = CheeseDQN(cheese_border_size * cheese_border_size, cheese_border_size * cheese_border_size, 'blackAgent')
    white_agent = CheeseDQN(cheese_border_size * cheese_border_size, cheese_border_size * cheese_border_size, 'whiteAgent')
    while True:  # 这是维持游戏循环进行的循环
        print('new game', flush=True)
        state = env.reset()  # 每局游戏开始之前重置环境
        step = 0
        while True:  # 这是每一局游戏内部接受落子的循环
            if env.get_color() == 1:  # 黑棋，则由人输入
                action = black_agent.get_action(state)
                action = (action // cheese_border_size, action % cheese_border_size)
            else:  # 白棋，则由agent输入
                action = white_agent.get_action(state)
                action = (action // cheese_border_size, action % cheese_border_size)

            if not action:  # 若是无效action，跳过
                raise TypeError("不应该出现无效action!")
            # 模型训练及保存
            step += 1
            next_state, reward, done, _ = env.step(action)
            action = action[0] * cheese_border_size + action[1]
            if done:
                print(f'''{'black' if env.get_color() ==1 else 'white'} player win!''', flush=True)
                print('game end, save model.')
                black_agent.save()
                white_agent.save()
                break
            black_agent.train(state, next_state, action, reward)  # 黑棋的原则是reward最大化，黑棋赢的时候reward是1，输的时候reward是-1
            white_agent.train(state, next_state, action, -reward)  # 白棋刚好相反
            state = next_state
            if step % 20 == 0:
                print('save model per 20 steps.')
                black_agent.save()
                white_agent.save()


def human_vs_ai():
    cheese_border_size = 15
    env = CheeseENV(border_count=cheese_border_size, line_margin=40)
    white_agent = CheeseDQN(cheese_border_size * cheese_border_size, cheese_border_size * cheese_border_size, 'whiteAgent')
    while True:  # 这是维持游戏循环进行的循环
        print('new game', flush=True)
        state = env.reset()  # 每局游戏开始之前重置环境
        step = 0
        while True:  # 这是每一局游戏内部接受落子的循环
            if env.get_color() == 1:  # 黑棋，则由人输入
                action = human_action(env)
            else:  # 白棋，则由agent输入
                action = white_agent.get_action(state)
                action = (action // cheese_border_size, action % cheese_border_size)

            if not action:  # 若是无效action，跳过
                raise TypeError("不应该出现无效action")
            # 模型训练及保存
            step += 1
            next_state, reward, done, _ = env.step(action)
            action = action[0] * cheese_border_size + action[1]
            if done:
                break
            white_agent.train(state, next_state, action, -reward)  # 白棋刚好相反
            state = next_state
            if step % 20 == 0:
                print('save model per 20 steps.')
                white_agent.save()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Game Mode')
    parser.add_argument('--mode',
                        type=str,
                        default='human_ai',
                        help='Set game mode, Default: human vs ai')
    args = parser.parse_args()
    mode = args.mode
    if mode == 'human_ai':
        print('Start human vs ai', flush=True)
        human_vs_ai()
    if mode == 'ai_ai':
        print('Start ai vs ai', flush=True)
        ai_vs_ai()

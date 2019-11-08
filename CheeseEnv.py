# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/07
# pygame Cheese 小游戏
# ---------------------------------------
import threading
from typing import List, Tuple
import pygame
from sys import exit
from pygame.locals import *
import operator
from CheeseAgent import CheeseDQN
import queue


class CheeseENV:
    def __init__(self, enable_pygame=True, **kwargs):
        self.black, self.white = 1, -1
        self.border_count = kwargs['border_count']  # 棋盘有多少棋子
        self.line_margin = kwargs['line_margin']  # 两条线之间的距离
        self.border_size = self.line_margin * (self.border_count + 1)  # 计算棋盘需要的尺寸
        screen_width, screen_height = self.border_size, self.border_size  # 屏幕尺寸
        self.enable_pygame = enable_pygame
        if self.enable_pygame:
            pygame.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
            self.font = pygame.font.SysFont("arial", 32)
        self.cheese_board = [[0] * self.border_count for _ in range(self.border_count)]
        self.piece_color = self.black

    def reset(self):
        """重置pygame的screen"""
        self.cheese_board = [[0] * self.border_count for _ in range(self.border_count)]
        self.piece_color = self.black
        if not self.enable_pygame:
            return
        background_color, line_color = (200, 200, 200), (100, 100, 100)
        screen = self.screen
        border_count, line_margin = self.border_count, self.line_margin
        screen.fill(background_color)
        border_size = self.border_size
        for row in range(border_count):
            pygame.draw.line(screen, line_color, (0, (row + 1) * line_margin), (border_size, (row + 1) * line_margin))
        for col in range(border_count):
            pygame.draw.line(screen, line_color, ((col + 1) * line_margin, 0), ((col + 1) * line_margin, border_size))
        pygame.display.update()

    def point_convert(self, px: int, py: int, point_thres: float = 0.375):
        line_margin = self.line_margin
        line_thres = line_margin * point_thres
        for row in range(self.border_count):
            for col in range(self.border_count):
                if (row + 1) * line_margin - line_thres < py < (row + 1) * line_margin + line_thres and \
                        (col + 1) * line_margin - line_thres < px < (col + 1) * line_margin + line_thres: \
                        return row, col
        return -1, -1

    def has_piece(self, _pos) -> bool:
        """
        判断给定位置是否有棋子
        :param _pos: 给定棋子位置
        :return: 是否有棋子
        """
        row, col = _pos
        return self.cheese_board[row][col] != 0

    def _piece_down(self, row: int, col: int, c: int in [1, -1]):
        """
        落下一枚棋子，如果开启pygame则绘制
        :param row: 棋子所在的行
        :param col: 棋子所在的列
        :param c: 棋子颜色
        """
        assert (c in [self.black, self.white])  # 确保color合法
        piece_color = (0, 0, 0) if c == self.black else (255, 255, 255)
        line_margin = self.line_margin
        self.cheese_board[row][col] = c
        # 在pygame绘制
        if self.enable_pygame:
            pygame.draw.circle(self.screen, piece_color, ((col + 1) * line_margin, (row + 1) * line_margin), 17)
            pygame.display.update()

    def _judge(self) -> int in [1, -1, 0]:
        """
        判断胜负情况
        :return: 当前胜利者 {1: 黑棋, -1: 白棋, 0: 暂时无人胜利}
        """
        black, white = self.black, self.white
        border_count = self.border_count
        border_res = 4  # 因为是五子棋，判断是否有五子连环的时候在距离边界为4的位置就可以停止了
        black_five, white_five = [black for _ in range(5)], [white for _ in range(5)]
        cheeses = self.cheese_board
        # 纵向判断是否有五子连环
        for row in range(border_count - border_res):
            for column in range(border_count):
                five_pieces = [cheeses[row + i][column] for i in range(5)]  # 纵向五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('|')
                    return black
                if operator.eq(five_pieces, white_five):  # 白胜
                    return white
        # 横向判断是否有五子连环
        for row in range(border_count):
            for column in range(border_count - border_res):
                five_pieces = [cheeses[row][column + j] for j in range(5)]  # 横向五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('-')
                    return black
                if operator.eq(five_pieces, white_five):  # 白胜
                    return white
        # 向右下斜向判断是否有五子连环
        for row in range(border_count - border_res):
            for column in range(border_count - border_res):
                five_pieces = [cheeses[row + i][column + i] for i in range(5)]  # 右斜五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('\\')
                    return black
                if operator.eq(five_pieces, white_five):  # 白胜
                    return white
        # 向左下斜向判断是否有五子连环
        for row in range(border_res, border_count):
            for column in range(border_count - border_res):
                five_pieces = [cheeses[row - i][column + i] for i in range(5)]  # 左斜五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('/')
                    return black
                if operator.eq(five_pieces, white_five):  # 白胜
                    return white
        # 若棋盘满了，黑胜
        if sum([cheese_board_row.count(0) for cheese_board_row in cheeses]) == 0:
            return black
        return 0

    def _settle(self, winner):
        """
        处理当前结果
        :param winner: 胜利方
        :return:
        """
        piece_color = (0, 0, 0) if winner == self.black else (255, 255, 255)  # 指定棋子颜色
        content_color = (0, 0, 0) if winner == self.white else (255, 255, 255)  # 指定 打印语句颜色
        content = 'Black Player Win!' if winner == self.black else 'White Player Win!'
        # 填充颜色并打印语句
        screen, font = self.screen, self.font
        screen.fill(piece_color)
        screen.blit(font.render(content, True, content_color), (200, 200))
        pygame.display.update()
        # 清空事件，等待时间输入激活下一阶段
        pygame.event.clear()
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:
                    break
                if event.type == KEYDOWN:
                    break
                if event.type == QUIT:
                    exit()
            else:
                continue
            break

    def step(self, _action):
        """
        执行一步动作（落子），返回环境状态
        :param _action: （x, y)构成的落子位置信息
        :return:
        """
        piece_x, piece_y = _action
        # 落子之后切换当前颜色，返回四元组信息
        self._piece_down(piece_x, piece_y, self.piece_color)
        result = self._judge()
        if result != 0 and self.enable_pygame:
            self._settle(self.piece_color)
        self.piece_color = -self.piece_color
        return self.cheese_board, -result, result != 0, 'exta info'

    def get_obs(self):
        return self.cheese_board

    def run(self):
        """cheese game 的主程序，正常模式下运行"""
        while True:  # 这是维持游戏循环进行的循环
            self.reset()  # 每局游戏开始之前重置环境
            while True:  # 这是每一局游戏内部接受落子的循环
                action = None
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
                        row, col = self.point_convert(x, y, point_thres=0.375)
                        action = (row, col)
                        if action == (-1, -1) or self.has_piece(action):
                            action = None
                        break
                if action:
                    next_state, reward, done, _ = self.step(action)
                    if done:
                        break


if __name__ == '__main__':
    env = CheeseENV(border_count=15, line_margin=40)
    while True:  # 这是维持游戏循环进行的循环
        env.reset()  # 每局游戏开始之前重置环境
        while True:  # 这是每一局游戏内部接受落子的循环
            action = None
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
            if action:
                next_state, reward, done, _ = env.step(action)
                if done:
                    break

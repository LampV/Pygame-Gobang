# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/07
# pygame Cheese 环境
# ---------------------------------------
import operator
from typing import List

import pygame
from sys import exit
from pygame.locals import *

black = 1
white = -1
blank = 0


def game_end(cheeses: List[List[int]]) -> int in [1, -1, 0]:
    """
    判断胜负情况
    :return: 当前胜利者 {1: 黑棋, -1: 白棋, 0: 暂时无人胜利}
    """
    # 遍历所有点
    board_count = len(cheeses)
    border_res = 4  # 因为是五子棋，判断是否有五子连环的时候在距离边界为4的位置就可以停止了
    black_five, white_five = [black for _ in range(5)], [white for _ in range(5)]
    # 纵向判断是否有五子连环
    for row in range(board_count - border_res):
        for column in range(board_count):
            five_pieces = [cheeses[row + i][column] for i in range(5)]  # 纵向五子
            if operator.eq(five_pieces, black_five):  # 黑胜
                return black
            if operator.eq(five_pieces, white_five):  # 白胜
                return white
    # 横向判断是否有五子连环
    for row in range(board_count):
        for column in range(board_count - border_res):
            five_pieces = [cheeses[row][column + j] for j in range(5)]  # 横向五子
            if operator.eq(five_pieces, black_five):  # 黑胜
                return black
            if operator.eq(five_pieces, white_five):  # 白胜
                return white
    # 向右下斜向判断是否有五子连环
    for row in range(board_count - border_res):
        for column in range(board_count - border_res):
            five_pieces = [cheeses[row + i][column + i] for i in range(5)]  # 右斜五子
            if operator.eq(five_pieces, black_five):  # 黑胜
                return black
            if operator.eq(five_pieces, white_five):  # 白胜
                return white
    # 向左下斜向判断是否有五子连环
    for row in range(border_res, board_count):
        for column in range(board_count - border_res):
            five_pieces = [cheeses[row - i][column + i] for i in range(5)]  # 左斜五子
            if operator.eq(five_pieces, black_five):  # 黑胜
                return black
            if operator.eq(five_pieces, white_five):  # 白胜
                return white
    # 若棋盘满了，黑胜
    if sum([cheese_board_row.count(0) for cheese_board_row in cheeses]) == 0:
        return black
    return 0


class CheeseENV:
    def __init__(self, enable_pygame=True, **kwargs):
        self.enable_pygame = enable_pygame
        self.board_count = kwargs['board_count'] if 'board_count' in kwargs else 15  # 棋盘有多少棋子
        self.line_margin = kwargs['line_margin'] if 'line_margin' in kwargs else 40  # 两条线之间的距离
        self.ignore_wait = True if 'ignore_wait' in kwargs else False
        self.board_size = self.line_margin * (self.board_count + 1)  # 计算棋盘需要的尺寸

        if self.enable_pygame:
            pygame.init()
            screen_width, screen_height = self.board_size, self.board_size  # 屏幕尺寸
            self.screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
            self.font = pygame.font.SysFont("arial", 32)
        # 设置棋盘和棋子颜色
        self.cheese_board = [[0] * self.board_count for _ in range(self.board_count)]
        self.piece_color = black

    def reset(self):
        """重置环境：将棋盘置为空，将棋子颜色置为黑色，重新绘制screen（如果需要）"""
        # 重置棋盘
        self.cheese_board = [[0] * self.board_count for _ in range(self.board_count)]
        # 重置棋子颜色
        self.piece_color = black
        if not self.enable_pygame:
            return self.get_obs()
        # 如果开启了pygame，重新绘制screen
        background_color, line_color = (200, 200, 200), (100, 100, 100)
        screen = self.screen
        border_count, line_margin = self.board_count, self.line_margin
        screen.fill(background_color)
        board_size = self.board_size
        for row in range(border_count):
            pygame.draw.line(screen, line_color, (0, (row + 1) * line_margin), (board_size, (row + 1) * line_margin))
        for col in range(border_count):
            pygame.draw.line(screen, line_color, ((col + 1) * line_margin, 0), ((col + 1) * line_margin, board_size))
        pygame.display.update()
        return self.get_obs()

    def point_convert(self, px: int, py: int, point_thres: float = 0.375):
        """
        将鼠标点击点的坐标转换为在棋盘交汇点的坐标
        :param px: 鼠标点击的x
        :param py: 鼠标点击的y
        :param point_thres: 允许的噪声容限
        :return: 在棋盘的行列值
        """
        line_margin = self.line_margin
        line_thres = line_margin * point_thres
        for row in range(self.board_count):
            for col in range(self.board_count):
                if (row + 1) * line_margin - line_thres < py < (row + 1) * line_margin + line_thres and \
                        (col + 1) * line_margin - line_thres < px < (col + 1) * line_margin + line_thres:
                    return row, col
        # 如果找不到，返回-1, -1
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
        assert (c in [black, white])  # 确保color合法
        piece_color = (0, 0, 0) if c == black else (255, 255, 255)
        line_margin = self.line_margin
        self.cheese_board[row][col] = c  # 覆盖写入颜色
        # 在pygame绘制
        if self.enable_pygame:
            pygame.draw.circle(self.screen, piece_color, ((col + 1) * line_margin, (row + 1) * line_margin), 17)
            pygame.display.update()

    def _pygame_settle(self, winner):
        """
        处理当前结果（对于pygame而言）
        :param winner: 胜利方
        :return:
        """
        piece_color = (0, 0, 0) if winner == black else (255, 255, 255)  # 指定棋子颜色
        content_color = (0, 0, 0) if winner == white else (255, 255, 255)  # 指定 打印语句颜色
        content = 'Black Player Win!' if winner == black else 'White Player Win!'
        # 填充颜色并打印语句
        screen, font = self.screen, self.font
        screen.fill(piece_color)
        screen.blit(font.render(content, True, content_color), (200, 200))
        pygame.display.update()
        # 清空事件，等待时间输入激活下一阶段
        if not self.ignore_wait:
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
        # 落子
        self._piece_down(piece_x, piece_y, self.piece_color)
        # 判断游戏是否结束
        result = game_end(self.cheese_board)
        # 如果游戏结束且开启pygame，绘制结果
        if result != 0 and self.enable_pygame:
            self._pygame_settle(self.piece_color)
        # 翻转棋子颜色
        self.piece_color = -self.piece_color
        # 返回四元组信息
        return self.cheese_board, -result, result != 0, 'exta info'

    def get_color(self):
        """返回当前落子的颜色"""
        return self.piece_color

    def get_obs(self):
        """
        获取observation
        :return: 棋盘
        """
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
    env = CheeseENV()
    env.run()

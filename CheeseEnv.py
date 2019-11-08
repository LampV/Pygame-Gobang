# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/07
# pygame Cheese 小游戏
# ---------------------------------------
from typing import List
import pygame
from sys import exit
from pygame.locals import *
import operator


class CheeseENV:

    def __init__(self):
        self.black, self.white = 1, -1
        self.border_count = 15  # 棋盘有多少棋子
        self.line_margin = 40  # 两条线之间的距离
        self.border_size = self.line_margin * (self.border_count + 1)  # 计算棋盘需要的尺寸
        screen_width, screen_height = self.border_size, self.border_size  # 屏幕尺寸
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height), 0, 32)
        self.font = pygame.font.SysFont("arial", 32)

    def reset(self):
        """重置pygame的screen"""
        background_color, line_color = (200, 200, 200), (100, 100, 100)
        screen = self.screen
        border_count, line_margin = self.border_count, self.line_margin
        screen.fill(background_color)
        border_size = self.border_size
        for raw in range(border_count):
            pygame.draw.line(screen, line_color, (0, line_margin + raw * line_margin), (border_size, line_margin + raw * line_margin))
        for col in range(border_count):
            pygame.draw.line(screen, line_color, (40 + col * line_margin, 0), (line_margin + col * line_margin, border_size))
        pygame.display.update()

    def piece_down(self, px: int, py: int, c: int in [1, -1], cheeses) -> bool:
        """
        对于鼠标点击的屏幕位置(px, py)(相对于pygame程序的位置)，寻找其落在哪个棋子范围内
        对于找到的这个落子点，若无子，则落子
        :param cheeses: 棋盘的引用
        :param c: 点击者执棋的颜色
        :param px: 鼠标点击点的x值
        :param py: 鼠标点击点的y值
        :return: 落子是否成功（这个点是否在棋盘范围内）
        """
        assert (c in [1, -1])  # 确保color合法
        piece_color = (0, 0, 0) if c == 1 else (255, 255, 255)
        line_margin = self.line_margin
        line_thres = line_margin * 0.375
        for row in range(self.border_count):
            for col in range(self.border_count):
                if cheeses[row][col] == 0 and \
                    (row + 1) * line_margin - line_thres < py < (row + 1) * line_margin + line_thres and \
                    (col + 1) * line_margin - line_thres < px < (col + 1) * line_margin + line_thres: \
                        # 找到落子点， 在数组上落子
                    cheeses[row][col] = c
                    # 在pygame绘制
                    pygame.draw.circle(self.screen, piece_color, ((col + 1) * line_margin, (row + 1) * line_margin), 17)
                    return True
        return False

    def judge(self, cheeses: List[List[int]]) -> int in [1, -1, 0]:
        """
        判断胜负情况
        :param cheeses: 棋盘的引用
        :return: 当前胜利者 {1: 黑棋, -1: 白棋, 0: 暂时无人胜利}
        """
        black, white = self.black, self.white
        border_count = self.border_count
        border_res = 4  # 因为是五子棋，判断是否有五子连环的时候在距离边界为4的位置就可以停止了
        black_five, white_five = [black for _ in range(5)], [white for _ in range(5)]
        # 纵向判断是否有五子连环
        for row in range(border_count - border_res):
            for column in range(border_count):
                five_pieces = [cheeses[row + i][column] for i in range(5)]  # 纵向五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('|')
                    return 1
                if operator.eq(five_pieces, white_five):  # 白胜
                    return -1
        # 横向判断是否有五子连环
        for row in range(border_count):
            for column in range(border_count - border_res):
                five_pieces = [cheeses[row][column + j] for j in range(5)]  # 横向五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('-')
                    return 1
                if operator.eq(five_pieces, white_five):  # 白胜
                    return -1
        # 向右下斜向判断是否有五子连环
        for row in range(border_count - border_res):
            for column in range(border_count - border_res):
                five_pieces = [cheeses[row + i][column + i] for i in range(5)]  # 右斜五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('\\')
                    return 1
                if operator.eq(five_pieces, white_five):  # 白胜
                    return -1
        # 向左下斜向判断是否有五子连环
        for row in range(border_res, border_count):
            for column in range(border_count - border_res):
                five_pieces = [cheeses[row - i][column + i] for i in range(5)]  # 左斜五子
                if operator.eq(five_pieces, black_five):  # 黑胜
                    print('/')
                    return 1
                if operator.eq(five_pieces, white_five):  # 白胜
                    return -1
        # 若棋盘满了，黑胜
        if sum([cheese_board_row.count(0) for cheese_board_row in cheeses]) == 0:
            return 1
        return 0

    def settle(self, winner):
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

    def run(self):
        """cheese game 的主程序"""

        # open_ai = False  # 是否开启AI对战
        while True:
            #   绘制棋盘
            self.reset()
            #   初始化数组与标志
            cheese_board = [[0] * 15 for _ in range(15)]
            flag = 1
            while True:
                for event in pygame.event.get():
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
                        if self.piece_down(x, y, flag, cheese_board):
                            flag = -flag
                        pygame.display.update()
                        result = self.judge(cheese_board)
                        if result != 0:
                            self.settle(result)
                            break
                        # a, b = cheese_ai()
                        # my_event = pygame.event.Event(MOUSEBUTTONDOWN, {'pos': (40 + a * 40, 40 + b * 40), 'Botton': 1})
                        # pygame.event.post(my_event)
                else:
                    continue
                break


if __name__ == '__main__':
    env = CheeseENV()
    env.run()

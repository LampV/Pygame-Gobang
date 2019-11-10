# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/07
# pygame 静态得分表算法计算棋局分数
# ---------------------------------------

from typing import List
from CheeseEnv import black, white

# 棋型的评估分数
shape_score = [(50, (0, 1, 1, 0, 0)),
               (50, (0, 0, 1, 1, 0)),
               (200, (1, 1, 0, 1, 0)),
               (500, (0, 0, 1, 1, 1)),
               (500, (1, 1, 1, 0, 0)),
               (5000, (0, 1, 1, 1, 0)),
               (5000, (0, 1, 0, 1, 1, 0)),
               (5000, (0, 1, 1, 0, 1, 0)),
               (5000, (1, 1, 1, 0, 1)),
               (5000, (1, 1, 0, 1, 1)),
               (5000, (1, 0, 1, 1, 1)),
               (5000, (1, 1, 1, 1, 0)),
               (5000, (0, 1, 1, 1, 1)),
               (50000, (0, 1, 1, 1, 1, 0)),
               (99999999, (1, 1, 1, 1, 1)),
               (-50, (0, -1, -1, 0, 0)),
               (-50, (0, 0, -1, -1, 0)),
               (-200, (-1, -1, 0, -1, 0)),
               (-500, (0, 0, -1, -1, -1)),
               (-500, (-1, -1, -1, 0, 0)),
               (-5000, (0, -1, -1, -1, 0)),
               (-5000, (0, -1, 0, -1, -1, 0)),
               (-5000, (0, -1, -1, 0, -1, 0)),
               (-5000, (-1, -1, -1, 0, -1)),
               (-5000, (-1, -1, 0, -1, -1)),
               (-5000, (-1, 0, -1, -1, -1)),
               (-5000, (-1, -1, -1, -1, 0)),
               (-5000, (0, -1, -1, -1, -1)),
               (-50000, (0, -1, -1, -1, -1, 0)),
               (-99999999, (-1, -1, -1, -1, -1))
               ]


def cal_score(m, n, x_decrict, y_derice, enemy_list, my_list, score_all_arr):
    """
    对于指定坐标、方向，计算总得分
    :param m: 坐标x值
    :param n: 坐标y值
    :param x_decrict: x方向增量（即x轴方向）
    :param y_derice: y方向增量（即y轴方向）
    :param enemy_list: 对手列表
    :param my_list:     自己列表
    :param score_all_arr: 得分序列
    :return: 总得分
    """
    add_score = 0  # 加分项
    # 在一个方向上， 只取最大的得分项
    max_score_shape = (0, [])

    # 如果此方向上，该点已经有得分形状，不重复计算
    for item in score_all_arr:
        for pt in item[1]:
            if m == pt[0] and n == pt[1] and x_decrict == item[2][0] and y_derice == item[2][1]:
                return 0

    # 在落子点 左右方向上循环查找得分形状
    for offset in range(-5, 1):
        # offset = -2
        pos = []
        for i in range(0, 6):
            if (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in enemy_list:
                pos.append(2)
            elif (m + (i + offset) * x_decrict, n + (i + offset) * y_derice) in my_list:
                pos.append(1)
            else:
                pos.append(0)
        tmp_shap5 = (pos[0], pos[1], pos[2], pos[3], pos[4])
        tmp_shap6 = (pos[0], pos[1], pos[2], pos[3], pos[4], pos[5])

        for (score, shape) in shape_score:
            if tmp_shap5 == shape or tmp_shap6 == shape:
                if tmp_shap5 == (1, 1, 1, 1, 1):
                    pass
                if score > max_score_shape[0]:
                    max_score_shape = (score, [(m + (0 + offset) * x_decrict, n + (0 + offset) * y_derice),
                                               (m + (1 + offset) * x_decrict, n + (1 + offset) * y_derice),
                                               (m + (2 + offset) * x_decrict, n + (2 + offset) * y_derice),
                                               (m + (3 + offset) * x_decrict, n + (3 + offset) * y_derice),
                                               (m + (4 + offset) * x_decrict, n + (4 + offset) * y_derice)], (x_decrict, y_derice))

    # 计算两个形状相交， 如两个3活 相交， 得分增加 一个子的除外
    if max_score_shape[1]:
        for item in score_all_arr:
            for pt1 in item[1]:
                for pt2 in max_score_shape[1]:
                    if pt1 == pt2 and max_score_shape[0] > 10 and item[0] > 10:
                        add_score += item[0] + max_score_shape[0]

        score_all_arr.append(max_score_shape)

    return add_score + max_score_shape[0]


class StaticEval:
    def __init__(self, ratio=1):
        self.ratio = ratio  # 进攻的系数   大于1 进攻型，  小于1 防守型

    # 评估函数
    def evaluation(self, piece_color, cheeses: List[List[int]]):
        board_count = len(cheeses)
        black_list = [(row, col) for row in range(board_count) for col in range(board_count) if cheeses[row][col] == black]
        white_list = [(row, col) for row in range(board_count) for col in range(board_count) if cheeses[row][col] == white]

        # 算自己的得分
        score_all_arr = []  # 得分形状的位置 用于计算如果有相交 得分翻倍
        black_score = 0
        for pt in black_list:
            m = pt[0]
            n = pt[1]
            black_score += cal_score(m, n, 0, 1, white_list, black_list, score_all_arr)
            black_score += cal_score(m, n, 1, 0, white_list, black_list, score_all_arr)
            black_score += cal_score(m, n, 1, 1, white_list, black_list, score_all_arr)
            black_score += cal_score(m, n, -1, 1, white_list, black_list, score_all_arr)

        #  算敌人的得分， 并减去
        score_all_arr_white = []
        white_score = 0
        for pt in white_list:
            m = pt[0]
            n = pt[1]
            white_score += cal_score(m, n, 0, 1, black_list, white_list, score_all_arr_white)
            white_score += cal_score(m, n, 1, 0, black_list, white_list, score_all_arr_white)
            white_score += cal_score(m, n, 1, 1, black_list, white_list, score_all_arr_white)
            white_score += cal_score(m, n, -1, 1, black_list, white_list, score_all_arr_white)
        
        if piece_color == black:
            return black_score - white_score * self.ratio
        else:
            return white_score - black_score * self.ratio

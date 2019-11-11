# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/11
# 基于Alpha-Beta剪枝树的博弈算法
# ---------------------------------------
import copy
from typing import List
from CheeseEnv import game_end, black, white
# from DRLAgent import DDPG
from StaticEval import StaticEval


class AlphaBeta:
    def __init__(self, max_depth=2, evaluator='static'):
        if evaluator == 'static':
            self.evaluator = StaticEval(ratio=1)
        # elif evaluator == 'drl':
        #     self.evaluator = DDPG(board_size * board_size, 1, 'evalAgent')

        self.max_depth = max_depth
        self.next_point = [0, 0]  # AI下一步最应该下的位置
        self.cheese_board = []
        # 搜索深度   只能是单数。  如果是负数， 评估函数评估的的是自己多少步之后的自己得分的最大值，并不意味着是最好的棋， 评估函数的问题

    def get_action(self, cur_state: List[List[int]]):
        self.cheese_board = copy.deepcopy(cur_state)
        self.negamax(white, self.max_depth, -99999999, 99999999)
        return self.next_point

    def negamax(self, piece_color: int, depth, alpha, beta):
        """
        极大极小值算法： 基于黑棋评估全局分数
        记录当前能确保的极小分数alpha和可能的最大分数beta
        通过迭代算法计算depth步后能够达到最理想分数的走法
        因为对手希望最小化分数，即取负值之后的最大化分数，所以可以使用负值极大来统一Max和Min算法
        自己的alpha对于对手而言，就是-beta（反而言之，对手的最坏情况就是自己可能的最好情况）
        1. alpha是之前被记录的最小的分数，意味着自己能确保的最低分
        2. 如果这一步的value比alpha大，则我们应该选择这个value作为新的alpha
        3 但是，如果value比beta还大，我们反而可以剪掉这一条枝，理由是：
          -beta其实就是对手的alpha，即"可以确保的最坏情况"。
          如果有一个枝的分数比beta还大，意味着-value会比-beta还小
          既然对手可以确保得到-beta的分数，那么对手就不会给你机会走出这一步棋
          所以分数比beta还高的情况是"对手不会允许发生"的，不发生就不用考虑
        4 但是，depth已经是0了，就不用这么做了，因为depth=0不考虑下一步，直接返回局势评估即可。
        :param piece_color:   棋子颜色
        :param depth:   需要考虑到多少步之后
        :param alpha:   已知可以确保的最低得分
        :param beta:    已知自己可能拿到的最高得分
        :return:
        """
        # 如果当前的状态有一方已经胜利，或者已经到达迭代深度，则返回局势计算得分
        if game_end(self.cheese_board) != 0 or depth == 0:
            return self.evaluator.evaluation(piece_color, self.cheese_board)

        blank_list = self.ordered_blank_list()  # 有哪些位置可以走

        # 遍历每一个候选步，这里的next_step指的是下一步落子的坐标
        for next_step in blank_list:
            row, col = next_step
            # 如果要评估的位置没有相邻的子，则不去评估，减少计算
            if not self.has_neightnor(next_step):
                continue
            # 记录这一步
            self.cheese_board[row][col] = piece_color

            # 反向计算递归计算value
            # 黑棋的最大值alpha取负数之后就是白棋的最小值beta
            value = -self.negamax(-piece_color, depth - 1, -beta, -alpha)
            # 递归计算之后，将这个位置清空
            self.cheese_board[row][col] = 0

            # 更新下限
            if value > alpha:
                if depth == self.max_depth:
                    self.next_point = next_step
                # alpha + beta剪枝点
                if value >= beta:
                    return beta
                alpha = value

        return alpha

    def ordered_blank_list(self):
        """
        返回排序过后的可以落子的点，加速剪枝
        :return: 排序过后的可以落子的点列表
        """
        board_count = len(self.cheese_board)
        blank_list = [(row, col) for row in range(board_count) for col in range(board_count) if self.cheese_board[row][col] == 0]
        return blank_list

    def has_neightnor(self, point):
        """
        判断一个点附近有没有棋子
        :param point: 这个点的坐标
        """
        row, col = point
        cheeses = self.cheese_board
        board_count = len(cheeses)
        if any(cheeses[r][c] != 0 for r in range(max(0, row - 1), min(row + 2, board_count)) for c in range(max(0, col - 1), min(col + 2, board_count))):
            return True
        return False

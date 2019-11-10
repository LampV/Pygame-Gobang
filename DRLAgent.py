# !/usr/bin/env python
# coding=utf-8
# --------------------------------------
# Copyright: Jiawei Wu
# 2019/11/08
# 通过强化学习评估棋局得分的agent
# ---------------------------------------
import os

import numpy as np
import keras


class DQN:
    """使用DQN的强化学习智能体"""

    def __init__(self, input_size, output_size, modelname='agent'):
        """通过Keras创建模型，中间层1024个节点，ReLU激活，输出softmax，交叉熵损失函数"""
        self.epsilon, self.epsilon_decay, self.epsilon_min = 1.0, 0.999, 0.1
        self.input_size, self.output_size = input_size, output_size

        if os.path.exists(f'./train/model-{modelname}.h5'):
            model = keras.models.load_model(f"./train/model-{modelname}.h5")
        else:
            model = keras.Sequential()
            model.add(keras.layers.Dense(1024, input_shape=(input_size,), activation='relu'))
            model.add(keras.layers.Dense(output_size, activation='softmax'))
        model.compile(optimizer=keras.optimizers.Adam(0.001),
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        self.model = model
        self.modelname = modelname

    def get_action(self, board_state):
        """根据当前state进行预测，state含义是棋盘状态，是一个二维数组"""
        board_size = len(board_state)
        state = np.reshape(board_state, [1, self.input_size])  # 化为列向量
        model = self.model
        # 直到网络产生了正确的落子为止
        while True:
            # 按照epsilon为概率，随机选取动作或者按价值最大值选取动作
            if np.random.rand(1) < self.epsilon:
                action = np.random.randint(self.output_size)
            else:
                action = np.argmax(model.predict(state)[0])
            # 获得动作以后要看是否与之前的棋子重复
            if board_state[action // board_size][action % board_size] != 0:
                # 若重复，说明这个动作不应该被选取，让神经网络学习
                target_f = model.predict(state)
                target_f[0][action] = -10
                model.fit(state, target_f, epochs=1, verbose=0)
                continue
            else:
                return action

    def train(self, board_state, board_next_state, action, reward):
        """
        对模型进行训练
        :param board_state: 棋盘的状态（AI落子前）
        :param board_next_state: 棋盘的下一状态（AI落子后）
        :param action: AI选择的落子动作
        :param reward: 游戏奖励
        """
        model = self.model
        state = np.reshape(board_state, [1, self.input_size])  # 化为列向量
        next_state = np.reshape(board_next_state, [1, self.input_size])  # 化为列向量
        target = (reward + 0.95 * np.amax(model.predict(next_state)[0]))
        target_f = model.predict(state)
        target_f[0][action] = target
        model.fit(state, target_f, epochs=1, verbose=0)

    def save(self):
        if not os.path.exists('train'):
            os.mkdir('train')
        self.model.save(f'./train/model-{self.modelname}.h5')


if __name__ == '__main__':
    agent = DQN(225, 225)
    agent.save()

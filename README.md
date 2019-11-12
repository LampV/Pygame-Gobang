Pygame-GoBang  
---
五子棋游戏的Pygame实现
> 注意Mac更新了Mojave之后无法运行Pygame，请在conda环境下执行命令
#### 游戏主程序`CheeseGame`
代码基于pygamepython3.7  
因为使用了f_string，请确保python版本>=3.6  
~~可以通过conda创建合适的环境~~  
```bash
# conda env create -f enviornment.yaml
```
只需要安装了pygame就可以运行
运行方式是  
```bash
# conda activate gobang
python3 CheeseGame --mode=MODE
``` 
其中*MODE* 可以被指定为 'ai_ai' 和 'human_ai'， 分别表示ai自己训练和人机对战。  
默认MODE为'human_ai'  
#### 游戏环境`CheeseEnv`  
创建`env`的方式是  
```python
# from CheeseEnv import CheeseENV
env = CheeseENV()
```
游戏环境通过二维数组维护，可以通过设置`enable_pygame=True` 的方式开启Pygame绘制 
运行方式： 
```python
python3 Cheese.py
```
`env` 还接受 `**kwargs`输入，参数和意义如下：  
- `border_count`：设置棋盘一行（列）最多能放多少枚棋子  
- `line_margin`：设置绘制棋盘时，两条线之间的距离  
- `ignore_wait`：一局游戏结束后会等待有效键盘或鼠标输入，使用`ignore_wait`可以略过这一步  
#### 博弈算法`AlphaBeta`  
使用AlphaBeta剪枝树计算落子位置  
> AlphaBeta算法的基本原理如下：  
使用深度优先搜索遍历，按照设定的depth看多步棋，选择最终棋局最适合自己的一步。  
棋局分数是对特定颜色棋子（如黑棋）而言的，因此黑棋要分数最大化，白棋要分数最小化。  
当白棋考虑棋局时，对分数取负值，可以统一最大化和最小化的算法。  
通过alpha剪枝，可以将对自己不利的情况直接剪去，减少计算。  
通过beta剪枝，可以将对对手不利的情况剪去（因为对手也是理智的，不会允许情况发生），减少计算。  

在AlphaBeta算法中，当depth不为0的时候，应该迭代计算。  
AlphaBeta算法的核心在于，黑棋的"可确保最低分"alpha取负值之后就是白棋的"可能最坏情况"；反之亦然。  
所以可以使用如下代码实现迭代：   
`value = -self.negamax(-piece_color, depth - 1, -beta, -alpha)`  
当depth为0的时候，应该直接返回棋局得分。  
计算棋局得分可以有很多种方法，其中传统实现是给定静态得分表计算，可行的另一种做法是通过神经网络来实现。  
通过创建AlphaBeta的AI时指定参数 `evaluator` 可以修改评估器。目前已经实现的评估器有：  
- 'static': 静态得分表计算
- 'ddpg': (未完成)强化学习计算

~~#### CheeseAgent~~ 
> 已失效 
```python
# from CheeseAgent import CheeseDQN
agent = CheeseDQN(input_size=225, output_size=225, model_name='whiteAgent')
```
其中`inpt_size`和`output_size`指定了神经网络的输入和输出维度  
`model_name`指定了模型的名称，并向`./train/model-{model_name}.h5`读取模型 
> 注意因为是直接读取模型，所以当目录下有对应文件的时候，`input_size`和`output_size`会失效  ~~
  

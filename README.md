DRL-GoBang  
---
五子棋游戏的强化学习实现 
> 注意Mac更新了Mojave之后无法运行Pygame，请在conda环境下执行命令
#### CheeseGame
代码基于pygame、tensorflow和python3.7  
因为使用了f_string，请确保python版本>=3.6  
tensorflow2.0中舍弃了default_graph，建议使用tensorflow==1.13.1   
可以通过conda创建合适的环境  
```bash
conda env create -f enviornment.yaml
```
运行方式是  
```bash
# conda activate gobang
python3 CheeseGame --mode=MODE
``` 
其中*MODE* 可以被指定为 'ai_ai' 和 'human_ai'， 分别表示ai自己训练和人机对战。  
默认MODE为'human_ai'  
#### CheeseEnv  
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
#### CheeseAgent
创建`agent`的方式是  
```python
# from CheeseAgent import CheeseDQN
agent = CheeseDQN(input_size=225, output_size=225, model_name='whiteAgent')
```
其中`inpt_size`和`output_size`指定了神经网络的输入和输出维度  
`model_name`指定了模型的名称，并向`./train/model-{model_name}.h5`读取模型 
> 注意因为是直接读取模型，所以当目录下有对应文件的时候，`input_size`和`output_size`会失效  
  

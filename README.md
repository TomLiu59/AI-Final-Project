**[Iterative Alternating Neural Attention in tensorflow](https://arxiv.org/abs/1606.02245)**
  
AI-Final-Project是依據以上論文實現，以GRU雙向RNN進行文章與問句之字詞預測估算，並對CBTest数据集進行問答模式進行測試

**Requirements:**

* Python 3.5.x
* TensorFlow 1.10.0
* Numpy 1.15.0
* Matplotlib 2.2.2

**Use Method:**
  
執行主程式，可得到預測答案:
```
python main.py
```
  
TensorBoard 模型圖示，開啟windows powershell，將路徑切換至log資料夾: 
```
tensorboard --logdir='./20190111182231/'
```
**Test（CBTest）:**
  
  http://www.thespermwhale.com/jaseweston/babi/CBTest.tgz

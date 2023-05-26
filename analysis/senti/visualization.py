# 绘制情绪分布饼图
# senti_list为excel中的情绪参数列表
import random
import matplotlib.pyplot as plt
from pylab import mpl

# 设置显示中文字体
mpl.rcParams["font.sans-serif"] = ["SimHei"]


def drawpic(senti_list):
    p = 0
    n = 0
    ordinary = 0
    flag = 0

    for mood in senti_list:
        if mood == -100:
            flag += 1
        elif mood < 0:
            n += 1
        elif mood == 0:
            ordinary += 1
    else:
        p += 1

    # 绘制饼状图

    labels = ['积极', '消极', '中性', '空数据']

    # 绘图显示的标签
    values = [p, n, ordinary, flag]

    colors = ['gold', 'lemonchiffon', 'khaki', 'k']
    explode = [0, 0, 0, 0]
    # 旋转角度
    plt.title("情感占比图", fontsize=20)
    # 标题
    plt.pie(values, labels=labels, explode=explode, colors=colors, startangle=180, shadow=True, autopct='%1.1f%%')
    plt.axis('equal')
    # plt.show()
    plt.savefig('./export/pics/senti.png', dpi=500, bbox_inches='tight')

    return "./export/pics/senti.png"

if __name__ == '__main__':
    senti_list = [random.randint(0, 150) for _ in range(100)]

    drawpic(senti_list)

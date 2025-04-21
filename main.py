import matplotlib.pyplot as plt
import numpy as np
from tkinter import *
import messagebox
from sympy.abc import *
from sympy import *
from sympy.utilities.lambdify import lambdify
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class FunctionPlotter:
    def __init__(self, master):
        self.master = master
        master.title("函数图像生成器")

        # 创建文本框和说明标签
        function_label = Label(master, text="输入函数(e.g. x**2)：y=")
        function_label.grid(row=0, column=0, columnspan=2)

        self.function_entry = Entry(master, width=30)
        self.function_entry.insert(END, "")
        self.function_entry.grid(row=1, column=0, columnspan=2)

        self.explanation_label = Label(master, text="注意:使用Python语法数学表达式(如x**2, sin(2*x), log(2*x))。\n*输入对数函数时x范围要大于0")
        self.explanation_label.grid(row=2, column=0, columnspan=2)

        # 创建x和y轴范围的滑动条
        x_range_frame = Frame(master)
        x_range_frame.grid(row=3, column=0, columnspan=2)

        x_range_label = Label(x_range_frame, text="X轴范围:")
        x_range_label.pack(side=LEFT)

        self.x_scale_lbl = Label(x_range_frame, text="-10")
        self.x_scale_lbl.pack(side=LEFT)

        self.x_scale = Scale(master, from_=-10, to=10, resolution=0.1, orient=HORIZONTAL, length=200, command=self.update_x_scale_lbl)
        self.x_scale.set(-5)
        self.x_scale.grid(row=4, column=0, columnspan=2)

        y_range_frame = Frame(master)
        y_range_frame.grid(row=3, column=2, columnspan=2)

        y_range_label = Label(y_range_frame, text="Y轴范围:")
        y_range_label.pack(side=LEFT)

        self.y_scale_lbl = Label(y_range_frame, text="0.0")
        self.y_scale_lbl.pack(side=LEFT)

        self.y_scale = Scale(master, from_=-10, to=10, resolution=0.1, orient=HORIZONTAL, length=200, command=self.update_y_scale_lbl)
        self.y_scale.set(0)
        self.y_scale.grid(row=4, column=2, columnspan=2)

        # 创建平移滑动条和平移按钮
        self.shift_lbl = Label(master, text="平移")
        self.shift_lbl.grid(row=5, column=0)

        self.shift_scale = Scale(master, from_=-10, to=10, resolution=0.1, orient=HORIZONTAL, length=200, command=self.update_shift_lbl)
        self.shift_scale.set(0)
        self.shift_scale.grid(row=5, column=1)

        shift_button = Button(master, text="开始平移", command=self.shift_graph)
        shift_button.grid(row=5, column=2)

        # 创建绘图按钮
        plot_button = Button(master, text="绘制图像", command=self.plot_graph)
        plot_button.grid(row=5, column=3, pady=10)

        # 创建绘图画布
        self.figure = plt.Figure(figsize=(5.5, 4), dpi=100)
        self.plot_canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.plot_canvas.get_tk_widget().grid(row=6, column=0, columnspan=4)

        # 创建工具栏
        self.toolbar = NavigationToolbar2Tk(self.plot_canvas, self.master, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(row=7, column=0, columnspan=4)

        # 记录x和y轴范围和当前平移量
        self.x_min, self.x_max = -10, 10
        self.y_min, self.y_max = -10, 10
        self.shift = 0.0

        # 上一次绘图时使用的函数和轴范围以及当前平移量
        self.last_function = ""
        self.last_x_min = None
        self.last_x_max = None
        self.last_y_min = None
        self.last_y_max = None
        self.last_shift = None

    def update_x_scale_lbl(self, val):
        self.x_scale_lbl.configure(text=val)

    def update_y_scale_lbl(self, val):
        self.y_scale_lbl.configure(text=val)

    def update_shift_lbl(self, val):
        self.shift_lbl.configure(text=f"平移 ({val})")

    def plot_graph(self):
        # 获取函数和轴范围
        function = self.function_entry.get().replace('^', '**')  # 用 ** 替换 ^ 符号
        x_min = self.x_scale.get()
        x_max = self.x_scale.get() + 10
        y_min = self.y_scale.get() - 5
        y_max = self.y_scale.get() + 5

        # 检查参数是否修改
        if (function, x_min, x_max, y_min, y_max, self.shift) == \
                (self.last_function, self.last_x_min, self.last_x_max, self.last_y_min, self.last_y_max,
                 self.last_shift):
            return  # 如果没有修改就直接返回

        # 获取当前滑块的取值
        x_scale_val = self.x_scale.get()
        y_scale_val = self.y_scale.get()

        # 使用 lambdify 函数将 sympy 函数转换为 lambda 函数
        x = symbols('x')

        try:
            f = lambdify(x, function, 'numpy')
            x_vals = np.linspace(x_min, x_max, 1000)
            y_vals = f(x_vals)

            # 根据函数的取值范围自动调整坐标轴的范围
            if not np.isnan(y_vals).any():
                y_min = np.nanmin(y_vals)
                y_max = np.nanmax(y_vals)
                y_range = max(abs(y_max), abs(y_min))
            else:
                y_min, y_max = -10, 10

            if not np.isnan(x_vals).any():
                x_min = min(x_vals[0], -y_range)
                x_max = max(x_vals[-1], y_range)
            else:
                x_min, x_max = -10, 10

            # 使用相同的x和y轴范围来绘制完整的直角坐标系
            abs_range = max(abs(x_min), abs(x_max), abs(y_min), abs(y_max))
            x_min, x_max = -abs_range, abs_range
            y_min, y_max = -abs_range, abs_range
            # 绘制函数图像
            self.figure.clear()  # 清空图像
            plot = self.figure.add_subplot(111)
            plot.plot(x_vals, y_vals, label='Initial Function')  # 添加初始函数曲线
            plot.plot(x_vals + self.shift, y_vals, label='Shifted Function')  # 添加最终平移的函数曲线
            plot.set_xlim([x_min, x_max])
            plot.set_ylim([y_min, y_max])
            plot.spines['left'].set_position('center')
            plot.spines['bottom'].set_position('zero')
            plot.spines['top'].set_color('none')
            plot.spines['right'].set_color('none')

            plot.set_ylim([y_min, y_max])
            plot.grid(True)
            plot.legend()
            self.plot_canvas.draw()

            # 重新设置滑块的范围和取值
            self.x_scale.configure(from_=-10, to=10, resolution=0.1)
            self.x_scale.set(x_scale_val)
            self.y_scale.configure(from_=-10, to=10, resolution=0.1)
            self.y_scale.set(y_scale_val)

            # 保存当前参数值
            self.last_function = function
            self.last_x_min = x_min
            self.last_x_max = x_max
            self.last_y_min = y_min
            self.last_y_max = y_max
            self.last_shift = self.shift

        except Exception as e:
            messagebox.showerror("错误", str(e))

    def shift_graph(self):
        self.shift = self.shift_scale.get()
        self.plot_graph()


if __name__ == "__main__":
    root = Tk()
    my_gui = FunctionPlotter(root)
    root.mainloop()


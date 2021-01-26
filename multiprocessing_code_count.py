import os
import chardet
import tkinter as tk
import multiprocessing
import time


# 统计指定目录下的代码文件，并添加至队列中
def find_all_file(queue, path, file_type=None):
    # 判断需要统计的文件类型
    if file_type is None:
        file_type = [".py",".cpp",".java",".c",".h",".php",".asp"]
    # 若传入的为单个文件
    if os.path.isfile(path):
        if os.path.splitext(path)[1] in file_type:
            queue.put(path)
        else:
            return "文件格式有误"
    else:
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.splitext(file)[1] in file_type:
                    queue.put(os.path.join(root, file))
    return queue


# 使用多进程统计队列中的代码总行数
def all_file_code_count(queue, path, file_type=None):
    start = time.time()
    queue = find_all_file(queue, path, file_type)
    # 有效文件数
    total_file_count = queue.qsize()
    # 有效代码行数
    total_line_count = multiprocessing.Value("i", 0)
    # 总注释数
    total_annotation_count = multiprocessing.Value("i", 0)
    # 总空行数
    total_blank_count = multiprocessing.Value("i", 0)
    # 获取当前计算机的cpu核数
    cpu_num = multiprocessing.cpu_count()
    p_list = [multiprocessing.Process(target=single_file_code_count, \
        args=(queue, total_line_count, total_annotation_count, total_blank_count)) for i in range(cpu_num)]
    for p in p_list:
        p.start()
        p.join()
    end = time.time()
    return total_file_count, total_line_count.value, total_annotation_count.value, total_blank_count.value, end-start


# 统计单个文件的代码行数
def single_file_code_count(queue, total_line_count, total_annotation_count, total_blank_count):
    while not queue.empty():
        file_path = queue.get()
        # 是否多行注释的标识
        flag = False
        if not os.path.exists(file_path):
            return "file doesn't exist"
        else:
            # 首先获取文件的编码
            with open(file_path, "rb") as f:
                content = f.read()
            file_chardet = chardet.detect(content)["encoding"]
            f = open(file_path, encoding=file_chardet)
            for line in f:
                # 多行注释的处理
                if line.strip().startswith("'''") or line.strip().startswith('"""') or \
                        line.strip().endswith("'''") or line.strip().endswith('"""'):
                    if flag == True:
                        flag = False
                    else:
                        flag = True
                    total_annotation_count.value += 1
                elif line.strip().startswith("/*"):
                    flag = True
                elif line.strip().endswith("*/"):
                    flag = False
                else:
                    # 跳出多行注释才进行判断记录
                    if not flag:
                        # 空行不记录
                        if line.strip() == "":
                            total_blank_count.value += 1
                            continue
                        # 单行注释需要区分是否文件编码声明
                        elif line.strip().startswith("#") or line.strip().startswith("//"):
                            # 编码声明行
                            if line.strip().startswith("#encoding") or line.strip().startswith("#coding") \
                                    or line.strip().startswith("#-*-"):
                                total_line_count.value += 1
                            # 单行注释行
                            else:
                                total_annotation_count.value += 1
                        # 其余情况则为真正代码行
                        else:
                            total_line_count.value += 1
                    # 仍在多行注释内
                    else:
                        total_annotation_count.value += 1
            f.close()
            return total_line_count, total_annotation_count, total_blank_count


# GUI：图形化代码统计工具
def gui(queue, file_type=None):

    # 创建主窗口
    window = tk.Tk()

    # 设置主窗口标题
    window.title("代码统计工具")
    # 设置主窗口大小（长*宽）
    window.geometry("500x300")  # 小写x

    ## Label部件：界面提示语
    # 在主窗口上设置标签（显示文本）
    l = tk.Label(window, text="请输入需要统计的目录或文件：")
    # 放置标签
    l.pack()  # Label内容content区域放置位置，自动调节尺寸


    ## Entry部件：单行文本输入
    e = tk.Entry(window, bd=5, width=50)
    e.pack()

    ## 定义Button事件的处理函数
    def button_click():
        # 获取输入框的目录路径
        path = e.get()
        # 调用代码统计工具
        res = all_file_code_count(queue, path, file_type)
        # 若返回的是异常结果
        if isinstance(res, str):
            # 使用configure实现实时刷新数据
            l2.configure(text=res)
        # 返回正常结果
        else:
            file_count = res[0]
            line_count = res[1]
            annotation_count = res[2]
            blank_count = res[3]
            time_need = res[4]
            l2.configure(text="文件总数：%s\n代码行总数：%s\n注释行总数：%s\n空行总数：%s\n总耗时：%s秒\n"\
                % (file_count, line_count, annotation_count, blank_count, round(time_need, 2)))

    ## Button部件：按钮
    b = tk.Button(window, text="提交", command=button_click)
    b.pack()

    # 用于显示统计结果
    l2 = tk.Label(window, text="", width=200, height=10)
    l2.pack()

    # 主窗口循环显示
    window.mainloop()
    '''
    注意：因为loop是循环的意思，window.mainloop就会让window不断的刷新。
    如果没有mainloop，就是一个静态的window，传入进去的值就不会有循环。
    mainloop就相当于一个很大的while循环，有个while，每点击一次就会更新一次，所以我们必须要有循环。
    所有的窗口文件都必须有类似的mainloop函数，mainloop是窗口文件的关键的关键。
    '''


if __name__ == "__main__":
    queue = multiprocessing.Queue()
    gui(queue)
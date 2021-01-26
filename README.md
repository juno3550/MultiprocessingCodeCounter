# multiprocessing_code_count
 带图形界面的多进程代码行统计工具

实现框架：
* find_all_file(queue, path, file_type=None)：统计文件个数。
* all_file_code_count(queue, path, file_type=None)：使用多进程统计队列中的代码总行数。
* single_file_code_count(queue, total_line_count, total_annotation_count, total_blank_count)：作为多进程的任务函数，并传入多进程共享变量，统计单个文件的代码行数。
* gui(queue)：实现图形可视化的输入（文件或目录的路径）与输出（统计结果）。

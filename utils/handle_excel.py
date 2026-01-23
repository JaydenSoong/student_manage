import openpyxl

'''
用 openpyxl 读取 excel 文件的操作
'''
class ReadExcel:
    def __init__(self, file_path):
        # 1.加载 excel 文件
        self.workbook = openpyxl.load_workbook(file_path)
        # 2.获取当前工作薄
        self.worksheet = self.workbook.active

    # 读取的方法
    def get_data(self):
        # 3.逐行读取
        # 将最后读取的数据以列表的方式保存起来
        data = []
        for row in self.worksheet.iter_rows():
            row_data = []
            # 遍历行数据
            for cell in row:
                row_data.append(cell.value)
            data.append(row_data)
        return  data

'''
用 openpyxl 写入 excel 文件的操作
'''
class WriteExcel:
    def __init__(self, file_path, data):
        # 获取文件路径
        self.file_path = file_path
        # 获取数据
        self.data = data
        # 创建一个对象用来创建一个工作表
        self.workbook = openpyxl.Workbook()
        # 获取当前工作薄
        self.worksheet = self.workbook.active

    def write_data(self):

        # 逐行写入
        for row in self.data:
            self.worksheet.append(row)

        self.workbook.save(self.file_path)


print('__name__', __name__)

if __name__ == '__main__':
    # 准备数据
    data = [
        ['学号', '姓名', '性别', '年龄', '班级'],
        [1001, '小王', '男', 18, '5班'],
        [1002, '小张', '女', 17, '5班'],
        [1003, '小李', '男', 16, '5班'],
        [1004, '小赵', '女', 15, '5班'],
        [1005, '小孙', '男', 14, '5班'],
    ]
    write_excel = WriteExcel('/home/jayden/Documents/5年级1班2026.xlsx', data)
    write_excel.write_data()
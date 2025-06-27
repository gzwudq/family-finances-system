import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import locale
import csv
import os
import math

# 设置中文字体
try:
    locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
except:
    pass

class EditDialog:
    def __init__(self, parent, values):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑记录")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        
        # 居中显示对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 获取父窗口位置
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # 计算对话框位置
        dialog_width = 400
        dialog_height = 300
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 创建变量 - 修正索引对应关系
        # values格式: [ID, 日期, 类型, 类别, 金额, 描述]
        self.type_var = tk.StringVar(value=values[2])  # 类型
        self.category_var = tk.StringVar(value=values[3])  # 类别
        # 处理金额，去掉¥符号
        amount_str = values[4] if isinstance(values[4], str) else str(values[4])
        amount_str = amount_str.replace('¥', '').strip()
        self.amount_var = tk.StringVar(value=amount_str)
        self.description_var = tk.StringVar(value=values[5])  # 描述
        self.date_var = tk.StringVar(value=values[1])  # 日期
        
        self.result = None
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="编辑记录", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 日期
        ttk.Label(main_frame, text="日期:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        date_entry = ttk.Entry(main_frame, textvariable=self.date_var, width=20)
        date_entry.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 类型
        ttk.Label(main_frame, text="类型:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        type_combo = ttk.Combobox(main_frame, textvariable=self.type_var, width=17)
        type_combo['values'] = ('收入', '支出')
        type_combo.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 类别
        ttk.Label(main_frame, text="类别:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, width=17)
        category_combo['values'] = ('工资', '奖金', '投资', '其他收入', '餐饮', '交通', '购物', '娱乐', '医疗', '教育', '其他支出')
        category_combo.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 金额
        ttk.Label(main_frame, text="金额:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        amount_entry = ttk.Entry(main_frame, textvariable=self.amount_var, width=20)
        amount_entry.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 描述
        ttk.Label(main_frame, text="描述:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        description_entry = ttk.Entry(main_frame, textvariable=self.description_var, width=20)
        description_entry.grid(row=5, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        # 保存按钮
        save_button = ttk.Button(button_frame, text="保存", command=self.save)
        save_button.grid(row=0, column=0, padx=10)
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=self.cancel)
        cancel_button.grid(row=0, column=1, padx=10)
        
        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        
    def save(self):
        # 验证输入
        if not self.type_var.get():
            messagebox.showerror("错误", "请选择类型")
            return
        if not self.category_var.get():
            messagebox.showerror("错误", "请输入类别")
            return
        if not self.amount_var.get():
            messagebox.showerror("错误", "请输入金额")
            return
            
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("错误", "金额必须大于0")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的金额")
            return
            
        self.result = {
            'date': self.date_var.get(),
            'type': self.type_var.get(),
            'category': self.category_var.get(),
            'amount': amount,
            'description': self.description_var.get()
        }
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()

class FamilyFinanceManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("家庭收入管理系统")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 设置窗口大小
        window_width = 1200
        window_height = 800
        
        # 计算窗口居中位置
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口样式
        self.root.configure(bg='#f5f5f5')
        
        # 存储当前编辑的记录ID
        self.editing_id = None
        
        self.setup_database()
        self.create_widgets()
        self.create_menu()
        
    def setup_database(self):
        # 创建数据库连接
        self.conn = sqlite3.connect('family_finance.db')
        self.cursor = self.conn.cursor()
        
        # 创建收支记录表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT
            )
        ''')
        self.conn.commit()
        
    def create_widgets(self):
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="15")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
        
        # 创建标题
        title_frame = ttk.Frame(self.main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="💰 家庭收入管理系统", 
                               font=('Arial', 18, 'bold'), foreground='#2c3e50')
        title_label.pack()
        
        # 创建左侧输入区域框架
        input_frame = ttk.LabelFrame(self.main_frame, text="📝 添加新记录", padding="15")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # 创建输入区域
        ttk.Label(input_frame, text="类型:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, width=18, font=('Arial', 10))
        self.type_combo['values'] = ('收入', '支出')
        self.type_combo.grid(row=0, column=1, padx=5, pady=8, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="类别:", font=('Arial', 10, 'bold')).grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, width=18, font=('Arial', 10))
        self.category_combo['values'] = ('工资', '奖金', '投资', '其他收入', '餐饮', '交通', '购物', '娱乐', '医疗', '教育', '其他支出')
        self.category_combo.grid(row=1, column=1, padx=5, pady=8, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="金额:", font=('Arial', 10, 'bold')).grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=20, font=('Arial', 10))
        self.amount_entry.grid(row=2, column=1, padx=5, pady=8, sticky=(tk.W, tk.E))
        
        ttk.Label(input_frame, text="描述:", font=('Arial', 10, 'bold')).grid(row=3, column=0, padx=5, pady=8, sticky=tk.W)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(input_frame, textvariable=self.description_var, width=20, font=('Arial', 10))
        self.description_entry.grid(row=3, column=1, padx=5, pady=8, sticky=(tk.W, tk.E))
        
        # 添加按钮
        self.add_button = ttk.Button(input_frame, text="➕ 添加记录", command=self.add_transaction, 
                                   style='Accent.TButton')
        self.add_button.grid(row=4, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))
        
        # 清空按钮
        clear_button = ttk.Button(input_frame, text="🗑️ 清空", command=self.clear_inputs)
        clear_button.grid(row=5, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # 创建右侧统计区域框架
        stats_frame = ttk.LabelFrame(self.main_frame, text="📊 统计信息", padding="15")
        stats_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N), padx=(10, 0))
        
        # 统计信息标签
        self.total_income_label = ttk.Label(stats_frame, text="💰 总收入: ¥0.00", 
                                          font=('Arial', 12, 'bold'), foreground='#27ae60')
        self.total_income_label.grid(row=0, column=0, padx=5, pady=8, sticky=tk.W)
        
        self.total_expense_label = ttk.Label(stats_frame, text="💸 总支出: ¥0.00", 
                                           font=('Arial', 12, 'bold'), foreground='#e74c3c')
        self.total_expense_label.grid(row=1, column=0, padx=5, pady=8, sticky=tk.W)
        
        self.balance_label = ttk.Label(stats_frame, text="💳 结余: ¥0.00", 
                                     font=('Arial', 14, 'bold'), foreground='#2c3e50')
        self.balance_label.grid(row=2, column=0, padx=5, pady=8, sticky=tk.W)
        
        # 添加分隔线
        separator = ttk.Separator(stats_frame, orient='horizontal')
        separator.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # 添加快速操作按钮
        ttk.Label(stats_frame, text="快速操作:", font=('Arial', 10, 'bold')).grid(row=4, column=0, padx=5, pady=(10, 5), sticky=tk.W)
        
        export_button = ttk.Button(stats_frame, text="📤 导出数据", command=self.export_data)
        export_button.grid(row=5, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))
        
        # 创建记录显示区域
        display_frame = ttk.LabelFrame(self.main_frame, text="📋 收支记录", padding="15")
        display_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # 创建工具栏
        toolbar_frame = ttk.Frame(display_frame)
        toolbar_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 搜索框
        ttk.Label(toolbar_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_records)
        search_entry = ttk.Entry(toolbar_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # 刷新按钮
        refresh_button = ttk.Button(toolbar_frame, text="🔄 刷新", command=self.load_transactions)
        refresh_button.pack(side=tk.RIGHT)
        
        # 创建Treeview
        columns = ('ID', '日期', '类型', '类别', '金额', '描述')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings', height=20)
        self.tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置列标题和宽度
        self.tree.heading('ID', text='ID')
        self.tree.heading('日期', text='日期')
        self.tree.heading('类型', text='类型')
        self.tree.heading('类别', text='类别')
        self.tree.heading('金额', text='金额')
        self.tree.heading('描述', text='描述')
        
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('日期', width=100, minwidth=100)
        self.tree.column('类型', width=80, minwidth=80)
        self.tree.column('类别', width=120, minwidth=120)
        self.tree.column('金额', width=120, minwidth=120)
        self.tree.column('描述', width=250, minwidth=200)
        
        # 隐藏ID列
        self.tree.column('ID', width=0, stretch=False)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky='ns')
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 创建右键菜单
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ 编辑", command=self.edit_transaction)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ 删除", command=self.delete_transaction)
        
        # 绑定右键点击事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # 绑定双击事件
        self.tree.bind("<Double-1>", lambda e: self.edit_transaction())
        
        # 绑定回车键
        self.root.bind('<Return>', lambda e: self.add_transaction())
        
        # 加载现有记录
        self.load_transactions()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_command(label="导出Excel", command=self.export_excel)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        # 统计菜单
        stats_menu = tk.Menu(menubar, tearoff=0)
        stats_menu.add_command(label="查看详细统计", command=self.show_statistics)
        stats_menu.add_command(label="数据图形分析", command=self.show_charts)
        menubar.add_cascade(label="统计", menu=stats_menu)
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)
        self.root.config(menu=menubar)

    def show_statistics(self):
        # 统计各类别收入、支出、总计
        self.cursor.execute('SELECT type, category, SUM(amount) FROM transactions GROUP BY type, category')
        stats = self.cursor.fetchall()
        income_stats = []
        expense_stats = []
        for t, cat, amt in stats:
            if t == '收入':
                income_stats.append(f"{cat}: ¥{amt:.2f}")
            else:
                expense_stats.append(f"{cat}: ¥{amt:.2f}")
        # 总收入、总支出、结余
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "收入"')
        total_income = self.cursor.fetchone()[0] or 0
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "支出"')
        total_expense = self.cursor.fetchone()[0] or 0
        balance = total_income - total_expense
        msg = f"【收入分类统计】\n" + '\n'.join(income_stats) + \
              f"\n\n【支出分类统计】\n" + '\n'.join(expense_stats) + \
              f"\n\n总收入: ¥{total_income:.2f}\n总支出: ¥{total_expense:.2f}\n结余: ¥{balance:.2f}"
        messagebox.showinfo("详细统计", msg)

    def show_about(self):
        messagebox.showinfo("关于", "家庭收入管理系统\n作者：伍德强（AI助手协助完成）\n版本：2.0\nQQ:282149635\n微信：Gzwudq\n邮箱：wudq@qq.com\n本软件是在AI助手的协助下开发而成,旨在测\n试软件开发效果。软件免费使用，录入数据自\n己保管，本人不负任何丢失责任！")

    def clear_inputs(self):
        """清空输入框"""
        self.type_combo.set('')
        self.category_var.set('')
        self.amount_var.set('')
        self.description_var.set('')
        
    def filter_records(self, *args):
        """过滤记录"""
        search_term = self.search_var.get().lower()
        
        # 清空现有显示
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 从数据库加载记录并过滤
        self.cursor.execute('SELECT id, date, type, category, amount, description FROM transactions ORDER BY date DESC')
        for record in self.cursor.fetchall():
            # 检查是否匹配搜索条件
            if (search_term in str(record[1]).lower() or  # 日期
                search_term in str(record[2]).lower() or  # 类型
                search_term in str(record[3]).lower() or  # 类别
                search_term in str(record[4]).lower() or  # 金额
                search_term in str(record[5]).lower()):   # 描述
                
                # 格式化金额显示
                formatted_record = list(record)
                formatted_record[4] = f"¥{record[4]:.2f}"
                self.tree.insert('', 'end', values=formatted_record)
        
    def show_context_menu(self, event):
        # 获取鼠标点击位置的项
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def edit_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要编辑的记录")
            return
            
        # 获取选中项的值
        values = self.tree.item(selected_item)['values']
        
        # 创建编辑对话框
        dialog = EditDialog(self.root, values)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            # 更新数据库中的记录
            self.cursor.execute('''
                UPDATE transactions 
                SET date = ?, type = ?, category = ?, amount = ?, description = ?
                WHERE id = ?
            ''', (dialog.result['date'], dialog.result['type'], 
                  dialog.result['category'], dialog.result['amount'], 
                  dialog.result['description'], values[0]))
            self.conn.commit()
            
            # 刷新显示
            self.load_transactions()
            messagebox.showinfo("成功", "记录更新成功！")
    
    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择要删除的记录")
            return
            
        if messagebox.askyesno("确认删除", "确定要删除选中的记录吗？\n此操作不可撤销！"):
            values = self.tree.item(selected_item)['values']
            
            # 从数据库中删除记录
            self.cursor.execute('DELETE FROM transactions WHERE id = ?', (values[0],))
            self.conn.commit()
            
            # 刷新显示
            self.load_transactions()
            messagebox.showinfo("成功", "记录删除成功！")
    
    def add_transaction(self):
        # 获取输入值
        transaction_type = self.type_var.get()
        category = self.category_var.get()
        amount = self.amount_var.get()
        description = self.description_var.get()
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 验证输入
        if not transaction_type:
            messagebox.showerror("错误", "请选择类型")
            return
        if not category:
            messagebox.showerror("错误", "请输入类别")
            return
        if not amount:
            messagebox.showerror("错误", "请输入金额")
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                messagebox.showerror("错误", "金额必须大于0")
                return
                
            # 将记录插入数据库
            self.cursor.execute('''
                INSERT INTO transactions (date, type, category, amount, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (date, transaction_type, category, amount, description))
            self.conn.commit()
            
            # 清空输入框
            self.clear_inputs()
            
            # 刷新显示
            self.load_transactions()
            
            messagebox.showinfo("成功", "记录添加成功！")
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的金额")
    
    def export_data(self):
        """导出数据功能"""
        try:
            from datetime import datetime
            filename = f"家庭收支数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("家庭收支管理系统 - 数据导出\n")
                f.write("=" * 50 + "\n\n")
                
                # 写入统计信息
                self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "收入"')
                total_income = self.cursor.fetchone()[0] or 0
                
                self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "支出"')
                total_expense = self.cursor.fetchone()[0] or 0
                
                balance = total_income - total_expense
                
                f.write(f"总收入: ¥{total_income:.2f}\n")
                f.write(f"总支出: ¥{total_expense:.2f}\n")
                f.write(f"结余: ¥{balance:.2f}\n\n")
                
                # 写入详细记录
                f.write("详细记录:\n")
                f.write("-" * 50 + "\n")
                
                self.cursor.execute('SELECT date, type, category, amount, description FROM transactions ORDER BY date DESC')
                for record in self.cursor.fetchall():
                    f.write(f"{record[0]} | {record[1]} | {record[2]} | ¥{record[3]:.2f} | {record[4]}\n")
            
            messagebox.showinfo("导出成功", f"数据已导出到文件: {filename}")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出数据时发生错误: {str(e)}")
    
    def export_excel(self):
        """导出数据到Excel文件"""
        try:
            filename = f"家庭收支数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入标题行
                writer.writerow(['日期', '类型', '类别', '金额', '描述'])
                
                # 写入数据
                self.cursor.execute('SELECT date, type, category, amount, description FROM transactions ORDER BY date DESC')
                for record in self.cursor.fetchall():
                    writer.writerow([record[0], record[1], record[2], f"¥{record[3]:.2f}", record[4]])
            
            messagebox.showinfo("导出成功", f"数据已导出到Excel文件: {filename}\n\n注意：文件为CSV格式，可用Excel打开")
            
        except Exception as e:
            messagebox.showerror("导出失败", f"导出Excel文件时发生错误: {str(e)}")

    def show_charts(self):
        """显示数据图形分析"""
        try:
            # 创建图表窗口
            chart_window = tk.Toplevel(self.root)
            chart_window.title("数据图形分析")
            chart_window.geometry("1200x800")
            chart_window.resizable(True, True)
            
            # 居中显示
            chart_window.transient(self.root)
            chart_window.grab_set()
            
            # 获取数据
            self.cursor.execute('SELECT type, category, SUM(amount) FROM transactions GROUP BY type, category ORDER BY type, SUM(amount) DESC')
            data = self.cursor.fetchall()
            
            # 分离收入和支出数据
            income_data = {}
            expense_data = {}
            
            for record_type, category, amount in data:
                if record_type == "收入":
                    income_data[category] = amount
                else:
                    expense_data[category] = amount
            
            # 创建主框架
            main_frame = ttk.Frame(chart_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # 创建标题
            title_label = ttk.Label(main_frame, text="📊 家庭收支数据图形分析", 
                                   font=('Arial', 16, 'bold'))
            title_label.pack(pady=(0, 20))
            
            # 创建图表区域
            charts_frame = ttk.Frame(main_frame)
            charts_frame.pack(fill=tk.BOTH, expand=True)
            
            # 左侧图表区域
            left_frame = ttk.Frame(charts_frame)
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            # 右侧图表区域
            right_frame = ttk.Frame(charts_frame)
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
            
            # 收入饼图
            if income_data:
                income_frame = ttk.LabelFrame(left_frame, text="💰 收入分布", padding="10")
                income_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
                
                income_canvas = tk.Canvas(income_frame, width=300, height=300, bg='white')
                income_canvas.pack()
                
                self.draw_pie_chart(income_canvas, income_data, "收入")
            
            # 支出饼图
            if expense_data:
                expense_frame = ttk.LabelFrame(left_frame, text="💸 支出分布", padding="10")
                expense_frame.pack(fill=tk.BOTH, expand=True)
                
                expense_canvas = tk.Canvas(expense_frame, width=300, height=300, bg='white')
                expense_canvas.pack()
                
                self.draw_pie_chart(expense_canvas, expense_data, "支出")
            
            # 收支对比柱状图
            comparison_frame = ttk.LabelFrame(right_frame, text="⚖️ 收支对比", padding="10")
            comparison_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
            
            comparison_canvas = tk.Canvas(comparison_frame, width=400, height=300, bg='white')
            comparison_canvas.pack()
            
            self.draw_bar_chart(comparison_canvas, income_data, expense_data)
            
            # 月度趋势图
            trend_frame = ttk.LabelFrame(right_frame, text="📅 月度趋势", padding="10")
            trend_frame.pack(fill=tk.BOTH, expand=True)
            
            trend_canvas = tk.Canvas(trend_frame, width=400, height=300, bg='white')
            trend_canvas.pack()
            
            self.draw_trend_chart(trend_canvas)
            
            # 添加工具栏
            toolbar_frame = ttk.Frame(main_frame)
            toolbar_frame.pack(fill=tk.X, pady=10)
            
            # 刷新按钮
            refresh_button = ttk.Button(toolbar_frame, text="🔄 刷新图表", 
                                      command=lambda: self.refresh_charts(chart_window))
            refresh_button.pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            messagebox.showerror("错误", f"生成图表时发生错误: {str(e)}")

    def draw_pie_chart(self, canvas, data, chart_type):
        """绘制饼图"""
        if not data:
            return
            
        # 计算总和
        total = sum(data.values())
        if total == 0:
            return
            
        # 颜色列表
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
                 '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
        
        # 饼图参数
        center_x, center_y = 150, 150
        radius = 100
        start_angle = 0
        
        # 绘制饼图
        for i, (category, amount) in enumerate(data.items()):
            percentage = amount / total
            angle = percentage * 360
            
            # 绘制扇形
            color = colors[i % len(colors)]
            canvas.create_arc(center_x - radius, center_y - radius,
                            center_x + radius, center_y + radius,
                            start=start_angle, extent=angle,
                            fill=color, outline='white', width=2)
            
            # 计算标签位置
            label_angle = math.radians(start_angle + angle / 2)
            label_x = center_x + (radius * 0.7) * math.cos(label_angle)
            label_y = center_y - (radius * 0.7) * math.sin(label_angle)
            
            # 绘制标签
            canvas.create_text(label_x, label_y, text=f"{percentage:.1%}",
                             font=('Arial', 10, 'bold'), fill='white')
            
            start_angle += angle
        
        # 绘制图例
        legend_y = 280
        for i, (category, amount) in enumerate(data.items()):
            color = colors[i % len(colors)]
            x = 50 + (i % 2) * 150
            y = legend_y + (i // 2) * 20
            
            # 图例颜色块
            canvas.create_rectangle(x, y-8, x+15, y+8, fill=color, outline='black')
            # 图例文本
            canvas.create_text(x+20, y, text=f"{category}: ¥{amount:.2f}",
                             font=('Arial', 9), anchor='w')

    def draw_bar_chart(self, canvas, income_data, expense_data):
        """绘制柱状图"""
        total_income = sum(income_data.values()) if income_data else 0
        total_expense = sum(expense_data.values()) if expense_data else 0
        
        # 图表参数
        width = 350
        height = 250
        margin = 50
        
        # 绘制坐标轴
        canvas.create_line(margin, height-margin, width-margin, height-margin, width=2)  # X轴
        canvas.create_line(margin, margin, margin, height-margin, width=2)  # Y轴
        
        # 绘制柱状图
        max_value = max(total_income, total_expense)
        if max_value == 0:
            max_value = 1
            
        bar_width = 60
        bar_height_income = (total_income / max_value) * (height - 2*margin)
        bar_height_expense = (total_expense / max_value) * (height - 2*margin)
        
        # 收入柱
        x1 = margin + 50
        y1 = height - margin - bar_height_income
        canvas.create_rectangle(x1, y1, x1+bar_width, height-margin, 
                              fill='#27ae60', outline='black', width=2)
        canvas.create_text(x1+bar_width/2, y1-10, text=f"¥{total_income:.2f}",
                          font=('Arial', 10, 'bold'))
        
        # 支出柱
        x2 = margin + 150
        y2 = height - margin - bar_height_expense
        canvas.create_rectangle(x2, y2, x2+bar_width, height-margin, 
                              fill='#e74c3c', outline='black', width=2)
        canvas.create_text(x2+bar_width/2, y2-10, text=f"¥{total_expense:.2f}",
                          font=('Arial', 10, 'bold'))
        
        # 标签
        canvas.create_text(x1+bar_width/2, height-margin+20, text="收入", 
                          font=('Arial', 12, 'bold'))
        canvas.create_text(x2+bar_width/2, height-margin+20, text="支出", 
                          font=('Arial', 12, 'bold'))

    def draw_trend_chart(self, canvas):
        """绘制趋势图"""
        # 获取月度数据
        self.cursor.execute('''
            SELECT strftime('%Y-%m', date) as month, 
                   SUM(CASE WHEN type = '收入' THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN type = '支出' THEN amount ELSE 0 END) as expense
            FROM transactions 
            GROUP BY strftime('%Y-%m', date) 
            ORDER BY month
        ''')
        
        monthly_data = self.cursor.fetchall()
        if not monthly_data:
            canvas.create_text(200, 150, text="暂无月度数据", 
                             font=('Arial', 14), fill='gray')
            return
            
        # 图表参数
        width = 350
        height = 250
        margin = 50
        
        # 绘制坐标轴
        canvas.create_line(margin, height-margin, width-margin, height-margin, width=2)  # X轴
        canvas.create_line(margin, margin, margin, height-margin, width=2)  # Y轴
        
        # 计算数据范围
        all_incomes = [row[1] for row in monthly_data]
        all_expenses = [row[2] for row in monthly_data]
        max_value = max(max(all_incomes), max(all_expenses))
        if max_value == 0:
            max_value = 1
        
        # 绘制折线
        x_step = (width - 2*margin) / (len(monthly_data) - 1) if len(monthly_data) > 1 else 1
        
        # 收入线
        income_points = []
        for i, (month, income, expense) in enumerate(monthly_data):
            x = margin + i * x_step
            y = height - margin - (income / max_value) * (height - 2*margin)
            income_points.append((x, y))
            
            # 绘制点
            canvas.create_oval(x-3, y-3, x+3, y+3, fill='#27ae60', outline='#27ae60')
        
        # 连接收入点
        for i in range(len(income_points)-1):
            canvas.create_line(income_points[i][0], income_points[i][1],
                             income_points[i+1][0], income_points[i+1][1],
                             fill='#27ae60', width=2)
        
        # 支出线
        expense_points = []
        for i, (month, income, expense) in enumerate(monthly_data):
            x = margin + i * x_step
            y = height - margin - (expense / max_value) * (height - 2*margin)
            expense_points.append((x, y))
            
            # 绘制点
            canvas.create_oval(x-3, y-3, x+3, y+3, fill='#e74c3c', outline='#e74c3c')
        
        # 连接支出点
        for i in range(len(expense_points)-1):
            canvas.create_line(expense_points[i][0], expense_points[i][1],
                             expense_points[i+1][0], expense_points[i+1][1],
                             fill='#e74c3c', width=2)
        
        # 绘制图例
        canvas.create_rectangle(width-80, margin, width-60, margin+15, fill='#27ae60')
        canvas.create_text(width-50, margin+7, text="收入", font=('Arial', 10), anchor='w')
        canvas.create_rectangle(width-80, margin+25, width-60, margin+40, fill='#e74c3c')
        canvas.create_text(width-50, margin+32, text="支出", font=('Arial', 10), anchor='w')

    def refresh_charts(self, chart_window):
        """刷新图表"""
        chart_window.destroy()
        self.show_charts()

    def load_transactions(self):
        # 清空现有显示
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 从数据库加载记录
        self.cursor.execute('SELECT id, date, type, category, amount, description FROM transactions ORDER BY date DESC')
        for record in self.cursor.fetchall():
            # 格式化金额显示
            formatted_record = list(record)
            formatted_record[4] = f"¥{record[4]:.2f}"
            self.tree.insert('', 'end', values=formatted_record)
        
        # 更新统计信息
        self.update_statistics()
    
    def update_statistics(self):
        # 计算总收入
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "收入"')
        total_income = self.cursor.fetchone()[0] or 0
        
        # 计算总支出
        self.cursor.execute('SELECT SUM(amount) FROM transactions WHERE type = "支出"')
        total_expense = self.cursor.fetchone()[0] or 0
        
        # 计算结余
        balance = total_income - total_expense
        
        # 更新标签
        self.total_income_label.config(text=f"💰 总收入: ¥{total_income:.2f}")
        self.total_expense_label.config(text=f"💸 总支出: ¥{total_expense:.2f}")
        self.balance_label.config(text=f"💳 结余: ¥{balance:.2f}")
        
        # 根据结余设置颜色
        if balance >= 0:
            self.balance_label.config(foreground='#27ae60')
        else:
            self.balance_label.config(foreground='#e74c3c')
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FamilyFinanceManager()
    app.run()
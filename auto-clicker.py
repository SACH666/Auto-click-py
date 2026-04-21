import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import mouse
import pyautogui
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button
import json
import os
from datetime import datetime

class AutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Pro - 自动连点器")
        self.root.geometry("650x750")
        self.root.resizable(False, False)
        
        # 设置样式
        self.setup_styles()
        
        # 状态变量
        self.is_clicking = False
        self.is_keyboard_clicking = False
        self.click_thread = None
        self.keyboard_thread = None
        self.fixed_position = None
        self.mouse_controller = MouseController()
        self.saved_configs = []
        
        # 默认设置
        self.click_speed = tk.DoubleVar(value=10.0)  # 每秒点击次数
        self.click_duration = tk.DoubleVar(value=5.0)  # 持续时间（秒）
        self.click_interval = tk.DoubleVar(value=0.1)  # 间隔时间（秒）
        self.mouse_button = tk.StringVar(value="left")
        self.click_mode = tk.StringVar(value="current")
        self.keyboard_key = tk.StringVar(value="a")
        self.keyboard_speed = tk.DoubleVar(value=10.0)
        self.keyboard_duration = tk.DoubleVar(value=5.0)
        self.hotkey_start = tk.StringVar(value="F6")
        self.hotkey_stop = tk.StringVar(value="F7")
        
        # 创建界面
        self.create_widgets()
        
        # 注册热键
        self.register_hotkeys()
        
        # 加载配置
        self.load_configs()
        
    def setup_styles(self):
        """设置现代化样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置颜色方案
        self.colors = {
            'bg': '#2b2b2b',
            'fg': '#ffffff',
            'select': '#404040',
            'button': '#0d7377',
            'button_hover': '#14ffec',
            'entry': '#404040',
            'frame': '#323232'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # 自定义样式
        style.configure('Modern.TLabelframe', 
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       borderwidth=2,
                       relief='solid')
        
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       font=('Microsoft YaHei', 10, 'bold'))
        
        style.configure('Modern.TButton',
                       background=self.colors['button'],
                       foreground=self.colors['fg'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Microsoft YaHei', 10))
        
        style.map('Modern.TButton',
                 background=[('active', self.colors['button_hover'])])
        
        style.configure('Modern.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       font=('Microsoft YaHei', 10))
        
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['entry'],
                       foreground=self.colors['fg'],
                       borderwidth=1)
        
        style.configure('Success.TButton',
                       background='#28a745',
                       foreground='white')
        
        style.configure('Danger.TButton',
                       background='#dc3545',
                       foreground='white')
        
        style.configure('Warning.TButton',
                       background='#ffc107',
                       foreground='black')
        
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 标题
        title_frame = tk.Frame(main_container, bg=self.colors['bg'])
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="🎯 AutoClicker Pro",
                              font=('Microsoft YaHei', 20, 'bold'),
                              bg=self.colors['bg'],
                              fg='#14ffec')
        title_label.pack()
        
        # 创建标签页
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill='both', expand=True)
        
        # 鼠标连点标签页
        self.mouse_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.mouse_frame, text='🖱️ 鼠标连点')
        
        # 键盘连点标签页
        self.keyboard_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.keyboard_frame, text='⌨️ 键盘连点')
        
        # 设置标签页
        self.settings_frame = tk.Frame(self.notebook, bg=self.colors['bg'])
        self.notebook.add(self.settings_frame, text='⚙️ 设置')
        
        # 创建各个标签页的内容
        self.create_mouse_tab()
        self.create_keyboard_tab()
        self.create_settings_tab()
        
        # 状态栏
        self.create_status_bar(main_container)
        
    def create_mouse_tab(self):
        """创建鼠标连点标签页"""
        # 点击设置框架
        click_frame = ttk.LabelFrame(self.mouse_frame, 
                                     text="点击设置", 
                                     style='Modern.TLabelframe',
                                     padding=15)
        click_frame.pack(fill='x', pady=10)
        
        # 点击速度
        ttk.Label(click_frame, text="点击速度 (次/秒):", 
                 style='Modern.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        speed_frame = tk.Frame(click_frame, bg=self.colors['bg'])
        speed_frame.grid(row=0, column=1, sticky='w', pady=5)
        ttk.Entry(speed_frame, textvariable=self.click_speed, 
                 width=10, style='Modern.TEntry').pack(side='left')
        ttk.Label(speed_frame, text="次/秒", 
                 style='Modern.TLabel').pack(side='left', padx=5)
        
        # 持续时间
        ttk.Label(click_frame, text="持续时间:", 
                 style='Modern.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        duration_frame = tk.Frame(click_frame, bg=self.colors['bg'])
        duration_frame.grid(row=1, column=1, sticky='w', pady=5)
        ttk.Entry(duration_frame, textvariable=self.click_duration, 
                 width=10, style='Modern.TEntry').pack(side='left')
        ttk.Label(duration_frame, text="秒 (0=无限)", 
                 style='Modern.TLabel').pack(side='left', padx=5)
        
        # 间隔时间
        ttk.Label(click_frame, text="间隔时间:", 
                 style='Modern.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        interval_frame = tk.Frame(click_frame, bg=self.colors['bg'])
        interval_frame.grid(row=2, column=1, sticky='w', pady=5)
        ttk.Entry(interval_frame, textvariable=self.click_interval, 
                 width=10, style='Modern.TEntry').pack(side='left')
        ttk.Label(interval_frame, text="秒", 
                 style='Modern.TLabel').pack(side='left', padx=5)
        
        # 鼠标按钮选择
        ttk.Label(click_frame, text="鼠标按键:", 
                 style='Modern.TLabel').grid(row=3, column=0, sticky='w', pady=5)
        button_combo = ttk.Combobox(click_frame, textvariable=self.mouse_button,
                                   values=['left', 'right', 'middle'],
                                   state='readonly', width=15)
        button_combo.grid(row=3, column=1, sticky='w', pady=5)
        
        # 位置设置框架
        position_frame = ttk.LabelFrame(self.mouse_frame, 
                                        text="位置设置", 
                                        style='Modern.TLabelframe',
                                        padding=15)
        position_frame.pack(fill='x', pady=10)
        
        # 点击模式
        ttk.Radiobutton(position_frame, text="跟随鼠标位置", 
                       variable=self.click_mode, value="current",
                       style='Modern.TRadiobutton').pack(anchor='w', pady=2)
        ttk.Radiobutton(position_frame, text="固定位置", 
                       variable=self.click_mode, value="fixed",
                       style='Modern.TRadiobutton').pack(anchor='w', pady=2)
        
        # 固定位置设置
        fixed_frame = tk.Frame(position_frame, bg=self.colors['bg'])
        fixed_frame.pack(fill='x', pady=5)
        
        self.position_label = ttk.Label(fixed_frame, 
                                       text="未设置固定位置", 
                                       style='Modern.TLabel')
        self.position_label.pack(side='left', padx=5)
        
        ttk.Button(fixed_frame, text="📍 捕获鼠标位置", 
                  command=self.capture_position,
                  style='Modern.TButton').pack(side='left', padx=5)
        
        # 控制按钮框架
        control_frame = tk.Frame(self.mouse_frame, bg=self.colors['bg'])
        control_frame.pack(fill='x', pady=10)
        
        self.mouse_start_btn = ttk.Button(control_frame, text="▶ 开始点击",
                                         command=self.start_mouse_clicking,
                                         style='Success.TButton')
        self.mouse_start_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        self.mouse_stop_btn = ttk.Button(control_frame, text="⏹ 停止点击",
                                        command=self.stop_mouse_clicking,
                                        style='Danger.TButton',
                                        state='disabled')
        self.mouse_stop_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        # 信息显示
        self.mouse_info_label = ttk.Label(self.mouse_frame,
                                         text="准备就绪 - 按 F6 开始/停止",
                                         style='Modern.TLabel',
                                         font=('Microsoft YaHei', 9))
        self.mouse_info_label.pack(pady=10)
        
    def create_keyboard_tab(self):
        """创建键盘连点标签页"""
        # 键盘设置框架
        keyboard_frame = ttk.LabelFrame(self.keyboard_frame, 
                                        text="键盘设置", 
                                        style='Modern.TLabelframe',
                                        padding=15)
        keyboard_frame.pack(fill='x', pady=10)
        
        # 按键选择
        ttk.Label(keyboard_frame, text="按键:", 
                 style='Modern.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        key_frame = tk.Frame(keyboard_frame, bg=self.colors['bg'])
        key_frame.grid(row=0, column=1, sticky='w', pady=5)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.keyboard_key, 
                                  width=15, style='Modern.TEntry')
        self.key_entry.pack(side='left')
        ttk.Button(key_frame, text="⌨️ 捕获按键", 
                  command=self.capture_key,
                  style='Modern.TButton').pack(side='left', padx=5)
        
        # 按键速度
        ttk.Label(keyboard_frame, text="按键速度 (次/秒):", 
                 style='Modern.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        key_speed_frame = tk.Frame(keyboard_frame, bg=self.colors['bg'])
        key_speed_frame.grid(row=1, column=1, sticky='w', pady=5)
        ttk.Entry(key_speed_frame, textvariable=self.keyboard_speed, 
                 width=10, style='Modern.TEntry').pack(side='left')
        ttk.Label(key_speed_frame, text="次/秒", 
                 style='Modern.TLabel').pack(side='left', padx=5)
        
        # 持续时间
        ttk.Label(keyboard_frame, text="持续时间:", 
                 style='Modern.TLabel').grid(row=2, column=0, sticky='w', pady=5)
        key_duration_frame = tk.Frame(keyboard_frame, bg=self.colors['bg'])
        key_duration_frame.grid(row=2, column=1, sticky='w', pady=5)
        ttk.Entry(key_duration_frame, textvariable=self.keyboard_duration, 
                 width=10, style='Modern.TEntry').pack(side='left')
        ttk.Label(key_duration_frame, text="秒 (0=无限)", 
                 style='Modern.TLabel').pack(side='left', padx=5)
        
        # 控制按钮
        control_frame = tk.Frame(self.keyboard_frame, bg=self.colors['bg'])
        control_frame.pack(fill='x', pady=10)
        
        self.keyboard_start_btn = ttk.Button(control_frame, text="▶ 开始按键",
                                            command=self.start_keyboard_clicking,
                                            style='Success.TButton')
        self.keyboard_start_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        self.keyboard_stop_btn = ttk.Button(control_frame, text="⏹ 停止按键",
                                           command=self.stop_keyboard_clicking,
                                           style='Danger.TButton',
                                           state='disabled')
        self.keyboard_stop_btn.pack(side='left', padx=5, expand=True, fill='x')
        
        # 信息显示
        self.keyboard_info_label = ttk.Label(self.keyboard_frame,
                                           text="准备就绪 - 按 F8 开始/停止",
                                           style='Modern.TLabel',
                                           font=('Microsoft YaHei', 9))
        self.keyboard_info_label.pack(pady=10)
        
        # 按键提示
        tip_label = ttk.Label(self.keyboard_frame,
                             text="💡 提示: 支持特殊按键如 'enter', 'space', 'tab' 等",
                             style='Modern.TLabel',
                             font=('Microsoft YaHei', 9))
        tip_label.pack(pady=5)
        
    def create_settings_tab(self):
        """创建设置标签页"""
        # 热键设置
        hotkey_frame = ttk.LabelFrame(self.settings_frame, 
                                      text="热键设置", 
                                      style='Modern.TLabelframe',
                                      padding=15)
        hotkey_frame.pack(fill='x', pady=10)
        
        # 开始热键
        ttk.Label(hotkey_frame, text="开始热键:", 
                 style='Modern.TLabel').grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(hotkey_frame, textvariable=self.hotkey_start, 
                 width=10, style='Modern.TEntry').grid(row=0, column=1, sticky='w', pady=5, padx=5)
        
        # 停止热键
        ttk.Label(hotkey_frame, text="停止热键:", 
                 style='Modern.TLabel').grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(hotkey_frame, textvariable=self.hotkey_stop, 
                 width=10, style='Modern.TEntry').grid(row=1, column=1, sticky='w', pady=5, padx=5)
        
        ttk.Button(hotkey_frame, text="更新热键", 
                  command=self.update_hotkeys,
                  style='Modern.TButton').grid(row=2, column=0, columnspan=2, pady=10)
        
        # 配置管理
        config_frame = ttk.LabelFrame(self.settings_frame, 
                                      text="配置管理", 
                                      style='Modern.TLabelframe',
                                      padding=15)
        config_frame.pack(fill='x', pady=10)
        
        # 配置列表
        self.config_listbox = tk.Listbox(config_frame, 
                                         height=5,
                                         bg=self.colors['entry'],
                                         fg=self.colors['fg'],
                                         selectbackground=self.colors['button'])
        self.config_listbox.pack(fill='x', pady=5)
        
        # 配置按钮
        button_frame = tk.Frame(config_frame, bg=self.colors['bg'])
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="💾 保存当前配置", 
                  command=self.save_config,
                  style='Modern.TButton').pack(side='left', padx=2, expand=True, fill='x')
        
        ttk.Button(button_frame, text="📂 加载配置", 
                  command=self.load_config,
                  style='Modern.TButton').pack(side='left', padx=2, expand=True, fill='x')
        
        ttk.Button(button_frame, text="🗑️ 删除配置", 
                  command=self.delete_config,
                  style='Warning.TButton').pack(side='left', padx=2, expand=True, fill='x')
        
        # 关于信息
        about_frame = ttk.LabelFrame(self.settings_frame, 
                                     text="关于", 
                                     style='Modern.TLabelframe',
                                     padding=15)
        about_frame.pack(fill='x', pady=10)
        
        about_text = """AutoClicker Pro v1.0
一个功能强大的自动连点器

功能特点:
• 鼠标自动点击
• 键盘自动按键
• 可设置点击速度和持续时间
• 支持固定位置点击
• 全局热键支持
• 配置保存和加载"""
        
        about_label = ttk.Label(about_frame, 
                               text=about_text,
                               style='Modern.TLabel',
                               justify='left')
        about_label.pack()
        
    def create_status_bar(self, parent):
        """创建状态栏"""
        self.status_bar = ttk.Label(parent, 
                                   text="就绪",
                                   style='Modern.TLabel',
                                   relief='sunken')
        self.status_bar.pack(fill='x', pady=(10, 0))
        
    def capture_position(self):
        """捕获鼠标位置"""
        def capture():
            self.status_bar.config(text="3秒后捕获鼠标位置...")
            time.sleep(3)
            pos = pyautogui.position()
            self.fixed_position = pos
            self.position_label.config(text=f"固定位置: X={pos.x}, Y={pos.y}")
            self.status_bar.config(text=f"已捕获位置: ({pos.x}, {pos.y})")
            
        threading.Thread(target=capture, daemon=True).start()
        
    def capture_key(self):
        """捕获按键"""
        def capture():
            self.status_bar.config(text="请按下要捕获的按键...")
            key = keyboard.read_key()
            self.keyboard_key.set(key)
            self.status_bar.config(text=f"已捕获按键: {key}")
            
        threading.Thread(target=capture, daemon=True).start()
        
    def start_mouse_clicking(self):
        """开始鼠标连点"""
        if self.is_clicking:
            return
            
        try:
            speed = float(self.click_speed.get())
            duration = float(self.click_duration.get())
            interval = float(self.click_interval.get())
            
            if speed <= 0:
                raise ValueError("点击速度必须大于0")
                
        except ValueError as e:
            messagebox.showerror("错误", f"输入参数错误: {str(e)}")
            return
            
        self.is_clicking = True
        self.mouse_start_btn.config(state='disabled')
        self.mouse_stop_btn.config(state='normal')
        self.mouse_info_label.config(text="正在点击中...")
        self.status_bar.config(text="鼠标连点运行中...")
        
        self.click_thread = threading.Thread(target=self.mouse_click_worker,
                                            args=(speed, duration, interval),
                                            daemon=True)
        self.click_thread.start()
        
    def mouse_click_worker(self, speed, duration, interval):
        """鼠标点击工作线程"""
        start_time = time.time()
        click_count = 0
        
        while self.is_clicking:
            if duration > 0 and (time.time() - start_time) >= duration:
                break
                
            try:
                # 确定点击位置
                if self.click_mode.get() == "fixed" and self.fixed_position:
                    x, y = self.fixed_position
                else:
                    x, y = pyautogui.position()
                
                # 执行点击
                button = self.mouse_button.get()
                if button == "left":
                    mouse.click(button='left')
                elif button == "right":
                    mouse.click(button='right')
                elif button == "middle":
                    mouse.click(button='middle')
                    
                click_count += 1
                
                # 计算延迟
                delay = 1.0 / speed
                time.sleep(delay)
                
            except Exception as e:
                print(f"点击错误: {e}")
                break
                
        self.root.after(0, self.stop_mouse_clicking)
        self.root.after(0, lambda: self.mouse_info_label.config(
            text=f"已完成 {click_count} 次点击"))
        self.root.after(0, lambda: self.status_bar.config(
            text=f"完成 {click_count} 次点击"))
        
    def stop_mouse_clicking(self):
        """停止鼠标连点"""
        self.is_clicking = False
        self.mouse_start_btn.config(state='normal')
        self.mouse_stop_btn.config(state='disabled')
        
    def start_keyboard_clicking(self):
        """开始键盘连点"""
        if self.is_keyboard_clicking:
            return
            
        try:
            speed = float(self.keyboard_speed.get())
            duration = float(self.keyboard_duration.get())
            
            if speed <= 0:
                raise ValueError("按键速度必须大于0")
                
        except ValueError as e:
            messagebox.showerror("错误", f"输入参数错误: {str(e)}")
            return
            
        self.is_keyboard_clicking = True
        self.keyboard_start_btn.config(state='disabled')
        self.keyboard_stop_btn.config(state='normal')
        self.keyboard_info_label.config(text="正在按键中...")
        self.status_bar.config(text="键盘连点运行中...")
        
        self.keyboard_thread = threading.Thread(target=self.keyboard_click_worker,
                                               args=(speed, duration),
                                               daemon=True)
        self.keyboard_thread.start()
        
    def keyboard_click_worker(self, speed, duration):
        """键盘点击工作线程"""
        start_time = time.time()
        press_count = 0
        key = self.keyboard_key.get()
        
        while self.is_keyboard_clicking:
            if duration > 0 and (time.time() - start_time) >= duration:
                break
                
            try:
                keyboard.press_and_release(key)
                press_count += 1
                
                delay = 1.0 / speed
                time.sleep(delay)
                
            except Exception as e:
                print(f"按键错误: {e}")
                break
                
        self.root.after(0, self.stop_keyboard_clicking)
        self.root.after(0, lambda: self.keyboard_info_label.config(
            text=f"已完成 {press_count} 次按键"))
        self.root.after(0, lambda: self.status_bar.config(
            text=f"完成 {press_count} 次按键"))
        
    def stop_keyboard_clicking(self):
        """停止键盘连点"""
        self.is_keyboard_clicking = False
        self.keyboard_start_btn.config(state='normal')
        self.keyboard_stop_btn.config(state='disabled')
        
    def register_hotkeys(self):
        """注册热键"""
        try:
            keyboard.add_hotkey(self.hotkey_start.get(), 
                              self.toggle_mouse_clicking)
            keyboard.add_hotkey('F8', self.toggle_keyboard_clicking)
        except:
            pass
            
    def update_hotkeys(self):
        """更新热键"""
        try:
            keyboard.unhook_all()
            self.register_hotkeys()
            messagebox.showinfo("成功", "热键已更新")
        except Exception as e:
            messagebox.showerror("错误", f"更新热键失败: {str(e)}")
            
    def toggle_mouse_clicking(self):
        """切换鼠标点击状态"""
        if self.is_clicking:
            self.stop_mouse_clicking()
        else:
            self.start_mouse_clicking()
            
    def toggle_keyboard_clicking(self):
        """切换键盘点击状态"""
        if self.is_keyboard_clicking:
            self.stop_keyboard_clicking()
        else:
            self.start_keyboard_clicking()
            
    def save_config(self):
        """保存配置"""
        config = {
            'mouse': {
                'speed': self.click_speed.get(),
                'duration': self.click_duration.get(),
                'interval': self.click_interval.get(),
                'button': self.mouse_button.get(),
                'mode': self.click_mode.get()
            },
            'keyboard': {
                'key': self.keyboard_key.get(),
                'speed': self.keyboard_speed.get(),
                'duration': self.keyboard_duration.get()
            },
            'hotkeys': {
                'start': self.hotkey_start.get(),
                'stop': self.hotkey_stop.get()
            }
        }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"config_{timestamp}"
        
        self.saved_configs.append({'name': name, 'config': config})
        self.update_config_list()
        
        # 保存到文件
        try:
            with open('autoclicker_configs.json', 'w') as f:
                json.dump(self.saved_configs, f)
            messagebox.showinfo("成功", f"配置 '{name}' 已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
            
    def load_configs(self):
        """加载配置"""
        try:
            if os.path.exists('autoclicker_configs.json'):
                with open('autoclicker_configs.json', 'r') as f:
                    self.saved_configs = json.load(f)
                self.update_config_list()
        except:
            pass
            
    def update_config_list(self):
        """更新配置列表"""
        self.config_listbox.delete(0, tk.END)
        for config in self.saved_configs:
            self.config_listbox.insert(tk.END, config['name'])
            
    def load_config(self):
        """加载选中的配置"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个配置")
            return
            
        config = self.saved_configs[selection[0]]['config']
        
        # 应用鼠标配置
        self.click_speed.set(config['mouse']['speed'])
        self.click_duration.set(config['mouse']['duration'])
        self.click_interval.set(config['mouse']['interval'])
        self.mouse_button.set(config['mouse']['button'])
        self.click_mode.set(config['mouse']['mode'])
        
        # 应用键盘配置
        self.keyboard_key.set(config['keyboard']['key'])
        self.keyboard_speed.set(config['keyboard']['speed'])
        self.keyboard_duration.set(config['keyboard']['duration'])
        
        # 应用热键配置
        self.hotkey_start.set(config['hotkeys']['start'])
        self.hotkey_stop.set(config['hotkeys']['stop'])
        
        messagebox.showinfo("成功", "配置已加载")
        
    def delete_config(self):
        """删除选中的配置"""
        selection = self.config_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个配置")
            return
            
        del self.saved_configs[selection[0]]
        self.update_config_list()
        
        # 保存到文件
        try:
            with open('autoclicker_configs.json', 'w') as f:
                json.dump(self.saved_configs, f)
            messagebox.showinfo("成功", "配置已删除")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
        
    def on_closing(self):
        """关闭窗口时的清理工作"""
        self.is_clicking = False
        self.is_keyboard_clicking = False
        try:
            keyboard.unhook_all()
        except:
            pass
        self.root.destroy()

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    # 安装所需库
    # pip install keyboard mouse pyautogui pynput
    main()

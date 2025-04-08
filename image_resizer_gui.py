#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import io
from image_resizer import ImageResizer

class ImageResizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片大小修改工具")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # 创建图片处理器
        self.resizer = ImageResizer()
        
        # 图片路径
        self.image_path = ""
        
        # 批量处理相关变量
        self.batch_folder = ""
        self.batch_files = []
        self.batch_current_index = 0
        self.batch_mode = False
        
        # 创建界面
        self.create_widgets()
        
        # 预览图片
        self.preview_original = None
        self.preview_processed = None
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右并列的主内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 左侧 - 页签区域
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=0)
        
        # 页签区域 - 创建页签
        notebook = ttk.Notebook(left_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 单张图片处理页签
        single_frame = ttk.Frame(notebook, padding="5")
        notebook.add(single_frame, text="单张图片处理")
        
        # 批量处理页签
        batch_frame = ttk.Frame(notebook, padding="5")
        notebook.add(batch_frame, text="批量处理")
        
        # 添加页签切换事件处理
        def on_tab_changed(event):
            # 强制更新界面，解决切换页签时的显示延迟问题
            self.root.update()
        
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)
        
        # 右侧 - 参数设置区域
        right_frame = ttk.Frame(content_frame, width=450)  # 增加宽度从400到450
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0), pady=0)
        right_frame.pack_propagate(False)  # 防止子组件影响frame大小
        
        # 参数设置（对所有处理方式通用）
        self.params_frame = ttk.LabelFrame(right_frame, text="参数设置", padding="10")
        self.params_frame.pack(fill=tk.BOTH, expand=True)
        
        # 参数设置区域分为左右两部分
        params_container = ttk.Frame(self.params_frame)
        params_container.pack(fill=tk.X, pady=5)
        
        # 目标大小设置 - 放在参数容器之上
        target_label_frame = ttk.Frame(self.params_frame)
        target_label_frame.pack(fill=tk.X, pady=(5, 10), before=params_container)
        
        ttk.Label(target_label_frame, text="目标大小 (KB):").pack(anchor=tk.W, pady=(0, 5))
        
        target_entry_frame = ttk.Frame(target_label_frame)
        target_entry_frame.pack(fill=tk.X)
        
        self.target_var = tk.StringVar(value="")
        target_entry = ttk.Entry(target_entry_frame, textvariable=self.target_var, width=20)
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 使用更大的wraplength值确保文本不会被截断
        hint_label = ttk.Label(target_label_frame, text="(留空表示不设置目标大小)", wraplength=450)
        hint_label.pack(anchor=tk.W, pady=(3, 0), fill=tk.X)
        
        # 处理方法选择区域
        self.method_frame = ttk.Frame(self.params_frame)
        self.method_frame.pack(fill=tk.X, pady=5, after=target_label_frame, before=params_container)
        
        ttk.Label(self.method_frame, text="处理方法:").pack(anchor=tk.W)
        
        self.method_var = tk.StringVar(value="quality")
        quality_radio = ttk.Radiobutton(self.method_frame, text="调整质量", variable=self.method_var, value="quality", command=self.toggle_method)
        quality_radio.pack(anchor=tk.W, padx=10)
        
        dimensions_radio = ttk.Radiobutton(self.method_frame, text="调整尺寸", variable=self.method_var, value="dimensions", command=self.toggle_method)
        dimensions_radio.pack(anchor=tk.W, padx=10)
        
        # 质量设置框架 - 直接放在params_frame中，不再放在params_container中
        self.quality_frame = ttk.Frame(self.params_frame)
        # 不要在这里pack，由toggle_method控制
        
        ttk.Label(self.quality_frame, text="质量值 (1-100):").pack(anchor=tk.W, pady=(0, 5))
        
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttk.Scale(self.quality_frame, from_=1, to=100, variable=self.quality_var, orient=tk.HORIZONTAL)
        quality_scale.pack(fill=tk.X, padx=10)
        
        quality_value = ttk.Label(self.quality_frame, textvariable=self.quality_var)
        quality_value.pack()
        
        # 尺寸设置框架 - 直接放在params_frame中，与quality_frame同级
        self.dimensions_frame = ttk.Frame(self.params_frame)
        # 不要在这里pack，由toggle_method控制
        
        # 尺寸设置标题
        dim_label = ttk.Label(self.dimensions_frame, text="尺寸设置:")
        dim_label.pack(anchor=tk.W, pady=(0, 8))
        
        # 宽度高度容器
        dims_container = ttk.Frame(self.dimensions_frame)
        dims_container.pack(fill=tk.X, anchor=tk.W, pady=(0, 8))
        
        # 新宽度部分
        width_container = ttk.Frame(dims_container)
        width_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        width_label = ttk.Label(width_container, text="新宽度:")
        width_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 3))
        
        self.width_var = tk.IntVar(value=800)
        width_entry = ttk.Entry(width_container, textvariable=self.width_var, width=8)
        width_entry.pack(side=tk.TOP, fill=tk.X)
        
        # 新高度部分
        height_container = ttk.Frame(dims_container)
        height_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        height_label = ttk.Label(height_container, text="新高度:")
        height_label.pack(side=tk.TOP, anchor=tk.W, pady=(0, 3))
        
        self.height_var = tk.IntVar(value=600)
        height_entry = ttk.Entry(height_container, textvariable=self.height_var, width=8)
        height_entry.pack(side=tk.TOP, fill=tk.X)
        
        # 保持宽高比选项
        self.keep_ratio_var = tk.BooleanVar(value=True)
        keep_ratio_check = ttk.Checkbutton(self.dimensions_frame, text="保持宽高比", variable=self.keep_ratio_var)
        keep_ratio_check.pack(anchor=tk.W, pady=(0, 8))
        
        # 提示文本
        hint_text = "设置目标大小后，程序会自动调整尺寸以接近目标大小"
        target_hint = ttk.Label(self.dimensions_frame, text=hint_text, wraplength=400)
        target_hint.pack(anchor=tk.W)
        
        # 添加保存路径设置 - 移到按钮上方并统一风格
        save_path_frame = ttk.Frame(self.params_frame)
        save_path_frame.pack(fill=tk.X, pady=(15, 5))
        
        ttk.Label(save_path_frame, text="保存路径:").pack(anchor=tk.W, pady=(0, 5))
        
        save_path_entry_frame = ttk.Frame(save_path_frame)
        save_path_entry_frame.pack(fill=tk.X)
        
        # 将浏览按钮移到左侧
        browse_save_btn = ttk.Button(save_path_entry_frame, text="浏览", command=self.browse_save_path)
        browse_save_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.save_path_var = tk.StringVar()
        save_path_entry = ttk.Entry(save_path_entry_frame, textvariable=self.save_path_var, width=20)
        save_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 添加提示文本，使用更大的wraplength并统一风格
        save_path_hint = ttk.Label(save_path_frame, text="(留空表示保存到原图所在文件夹)", wraplength=450)
        save_path_hint.pack(anchor=tk.W, pady=(3, 0), fill=tk.X)
        
        # 添加处理和保存按钮到参数设置区域底部
        buttons_frame = ttk.Frame(self.params_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # 使用pack布局垂直排列按钮，每个按钮单独一行
        process_btn = ttk.Button(buttons_frame, text="处理图片", command=self.process_image)
        process_btn.pack(fill=tk.X, pady=(0, 5))
        
        save_btn = ttk.Button(buttons_frame, text="保存图片", command=self.save_image)
        save_btn.pack(fill=tk.X)
        
        # ===== 单张图片处理页面内容 =====
        # 图片选择区域（移动到单张图片处理页签内）
        file_select_frame = ttk.LabelFrame(single_frame, text="图片选择（支持的格式：JPG、JPEG、PNG、BMP、GIF、TIFF、WebP）", padding="10")
        file_select_frame.pack(fill=tk.X, pady=5)
        
        self.path_var = tk.StringVar()
        
        # 选择图片按钮
        browse_btn = ttk.Button(file_select_frame, text="选择图片", command=self.browse_image)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        path_entry = ttk.Entry(file_select_frame, textvariable=self.path_var, width=70)
        path_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(single_frame, text="图片预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # 原始图片预览
        original_frame = ttk.LabelFrame(preview_container, text="原始图片", padding="5")
        original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 2))
        
        self.original_canvas = tk.Canvas(original_frame, bg="#f0f0f0")
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 处理后图片预览
        processed_frame = ttk.LabelFrame(preview_container, text="处理后图片", padding="5")
        processed_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2, 0))
        
        self.processed_canvas = tk.Canvas(processed_frame, bg="#f0f0f0")
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)
        
        # 图片信息显示
        info_frame = ttk.Frame(preview_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # 原始图片信息
        original_info_frame = ttk.LabelFrame(info_frame, text="原始图片信息", padding="5")
        original_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 2))
        
        self.original_info = tk.Text(original_info_frame, height=5, width=30, wrap=tk.WORD)
        self.original_info.pack(fill=tk.BOTH, expand=True)
        self.original_info.config(state=tk.DISABLED)
        
        # 处理后图片信息
        processed_info_frame = ttk.LabelFrame(info_frame, text="处理后图片信息", padding="5")
        processed_info_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(2, 0))
        
        self.processed_info = tk.Text(processed_info_frame, height=5, width=30, wrap=tk.WORD)
        self.processed_info.pack(fill=tk.BOTH, expand=True)
        self.processed_info.config(state=tk.DISABLED)
        
        # ===== 批量处理页面内容 =====
        
        # 批量处理文件选择
        batch_file_frame = ttk.Frame(batch_frame)
        batch_file_frame.pack(fill=tk.X, pady=5)
        
        select_folder_btn = ttk.Button(batch_file_frame, text="选择文件夹", command=self.select_batch_folder)
        select_folder_btn.pack(side=tk.LEFT, padx=5)
        
        self.folder_var = tk.StringVar()
        folder_entry = ttk.Entry(batch_file_frame, textvariable=self.folder_var, width=50)
        folder_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # 批量处理按钮
        batch_btn_frame = ttk.Frame(batch_frame)
        batch_btn_frame.pack(fill=tk.X, pady=5)
        
        batch_process_btn = ttk.Button(batch_btn_frame, text="批量处理", command=self.batch_process)
        batch_process_btn.pack(side=tk.LEFT, padx=5)
        
        # 批量处理进度
        progress_frame = ttk.LabelFrame(batch_frame, text="处理进度", padding="10")
        progress_frame.pack(fill=tk.X, pady=5, expand=True)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="准备就绪")
        self.progress_label.pack(anchor=tk.W)
        
        # 底部区域已移除退出按钮
        
        # 初始化界面状态
        self.toggle_method()
    
    def toggle_method(self):
        method = self.method_var.get()
        
        if method == "quality":
            # 先移除尺寸设置，再显示质量设置
            self.dimensions_frame.pack_forget()
            self.quality_frame.pack(in_=self.params_frame, fill=tk.X, pady=5, after=self.method_frame)
            # 强制更新界面，解决显示延迟问题
            self.root.update()
        else:  # dimensions
            # 先移除质量设置，再显示尺寸设置
            self.quality_frame.pack_forget()
            self.dimensions_frame.pack(in_=self.params_frame, fill=tk.X, pady=5, after=self.method_frame)
            # 强制更新界面，解决显示延迟问题
            self.root.update()
    
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[
                ("所有支持的图片", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff *.webp"),
                ("JPEG图片", "*.jpg *.jpeg"),
                ("PNG图片", "*.png"),
                ("BMP图片", "*.bmp"),
                ("GIF图片", "*.gif"),
                ("TIFF图片", "*.tiff *.tif"),
                ("WebP图片", "*.webp"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            self.path_var.set(file_path)
            
            # 加载图片
            if self.resizer.load_image(file_path):
                # 显示原始图片信息
                self.update_original_info()
                
                # 显示原始图片预览
                self.show_original_preview()
                
                # 清除处理后的图片预览和信息
                self.clear_processed_preview()
    
    def update_original_info(self):
        if not self.resizer.original_image:
            return
        
        # 获取原始图片信息
        file_size = os.path.getsize(self.image_path)
        width = self.resizer.original_image.width
        height = self.resizer.original_image.height
        img_format = self.resizer.original_image.format
        
        # 更新信息显示
        self.original_info.config(state=tk.NORMAL)
        self.original_info.delete(1.0, tk.END)
        self.original_info.insert(tk.END, f"大小: {self.resizer.format_size(file_size)}\n")
        self.original_info.insert(tk.END, f"尺寸: {width} x {height}\n")
        self.original_info.insert(tk.END, f"格式: {img_format}")
        self.original_info.config(state=tk.DISABLED)
    
    def update_processed_info(self):
        if not self.resizer.processed_image:
            return
        
        # 获取处理后图片信息
        buffer = io.BytesIO()
        img_format = os.path.splitext(self.image_path)[1].lower().replace(".", "")
        if img_format == "jpg":
            img_format = "jpeg"
        
        quality = self.quality_var.get()
        if img_format.lower() in ["jpeg", "jpg"]:
            self.resizer.processed_image.save(buffer, format=img_format, quality=quality)
        else:
            self.resizer.processed_image.save(buffer, format=img_format)
        
        processed_size = len(buffer.getvalue())
        width = self.resizer.processed_image.width
        height = self.resizer.processed_image.height
        
        # 更新信息显示
        self.processed_info.config(state=tk.NORMAL)
        self.processed_info.delete(1.0, tk.END)
        self.processed_info.insert(tk.END, f"大小: {self.resizer.format_size(processed_size)}\n")
        self.processed_info.insert(tk.END, f"尺寸: {width} x {height}\n")
        
        # 根据图片格式添加不同的信息
        if self.method_var.get() == "quality":
            self.processed_info.insert(tk.END, f"质量: {quality}\n")
            
            # 对PNG格式添加特殊提示
            if img_format.lower() == "png":
                self.processed_info.insert(tk.END, "注意: PNG是无损格式,\n调整质量效果有限")
        
        self.processed_info.config(state=tk.DISABLED)
    
    def show_original_preview(self):
        if not self.resizer.original_image:
            return
        
        # 调整图片大小以适应预览区域
        preview_img = self.resize_for_preview(self.resizer.original_image)
        
        # 创建PhotoImage对象
        self.preview_original = ImageTk.PhotoImage(preview_img)
        
        # 在Canvas上显示图片
        self.original_canvas.config(width=preview_img.width, height=preview_img.height)
        self.original_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_original)
    
    def show_processed_preview(self):
        if not self.resizer.processed_image:
            return
        
        # 调整图片大小以适应预览区域
        preview_img = self.resize_for_preview(self.resizer.processed_image)
        
        # 创建PhotoImage对象
        self.preview_processed = ImageTk.PhotoImage(preview_img)
        
        # 在Canvas上显示图片
        self.processed_canvas.config(width=preview_img.width, height=preview_img.height)
        self.processed_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_processed)
    
    def clear_processed_preview(self):
        # 清除处理后的图片预览
        self.processed_canvas.delete("all")
        self.preview_processed = None
        
        # 清除处理后的图片信息
        self.processed_info.config(state=tk.NORMAL)
        self.processed_info.delete(1.0, tk.END)
        self.processed_info.config(state=tk.DISABLED)
    
    def resize_for_preview(self, img):
        # 获取预览区域大小
        max_width = 350
        max_height = 300
        
        # 计算缩放比例
        width, height = img.size
        ratio = min(max_width / width, max_height / height)
        
        # 如果图片小于预览区域，不进行缩放
        if ratio >= 1:
            return img
        
        # 缩放图片
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def process_image(self):
        if not self.resizer.original_image:
            messagebox.showerror("错误", "请先选择图片")
            return
        
        method = self.method_var.get()
        img_format = os.path.splitext(self.image_path)[1].lower().replace(".", "")
        
        if method == "quality":
            quality = self.quality_var.get()
            target_size = 0
            if self.target_var.get().strip():
                try:
                    target_size = int(self.target_var.get())
                except ValueError:
                    messagebox.showerror("错误", "目标大小必须是整数")
                    return
            
            # 处理前检查是否为PNG格式且设置了目标大小
            if img_format.lower() == "png" and target_size > 0:
                # 提前提示用户PNG格式的特殊性
                if not messagebox.askyesno("PNG格式提示", 
                                        "PNG是无损压缩格式，调整质量可能无法精确达到目标大小。\n\n" +
                                        "程序将尝试通过调整色彩深度和尺寸来接近目标大小，" +
                                        "但效果可能有限。\n\n" +
                                        "如需精确控制文件大小，建议：\n" +
                                        "1. 使用调整尺寸方法\n" +
                                        "2. 考虑保存为JPEG格式\n\n" +
                                        "是否继续?"):
                    return
            
            if not self.resizer.process_image_quality(quality, target_size):
                messagebox.showerror("错误", "处理图片失败")
                return
            
            # 检查处理后的大小是否接近目标大小
            if target_size > 0:
                buffer = io.BytesIO()
                if img_format.lower() in ["jpeg", "jpg"]:
                    self.resizer.processed_image.save(buffer, format=img_format, quality=quality)
                else:
                    self.resizer.processed_image.save(buffer, format=img_format)
                
                processed_size = len(buffer.getvalue()) / 1024  # 转换为KB
                
                # 如果是PNG格式且处理后大小与目标相差超过20%
                if img_format.lower() == "png" and abs(processed_size - target_size) > target_size * 0.2:
                    messagebox.showinfo("处理完成", 
                                      f"图片已处理，但由于PNG格式的限制，\n" +
                                      f"实际大小({processed_size:.2f}KB)与目标大小({target_size}KB)有差异。\n\n" +
                                      "建议尝试调整尺寸方法或保存为JPEG格式以获得更精确的大小控制。")
        else:  # dimensions
            width = self.width_var.get()
            height = self.height_var.get()
            keep_ratio = self.keep_ratio_var.get()
            
            if width <= 0 or height <= 0:
                messagebox.showerror("错误", "宽度和高度必须大于0")
                return
            
            if not self.resizer.process_image_dimensions(width, height, keep_ratio):
                messagebox.showerror("错误", "处理图片失败")
                return
        
        # 显示处理后的图片预览
        self.show_processed_preview()
        
        # 更新处理后的图片信息
        self.update_processed_info()
        
        # 如果不是PNG格式或没有特殊提示，显示常规成功消息
        if not (method == "quality" and img_format.lower() == "png" and 
                target_size > 0 and abs(processed_size - target_size) > target_size * 0.2):
            messagebox.showinfo("成功", "图片处理完成")
    
    def save_image(self):
        """保存处理后的图片"""
        if not self.resizer.processed_image:
            messagebox.showwarning("警告", "请先处理图片")
            return
            
        # 获取保存路径
        save_path = self.save_path_var.get()
        if not save_path:
            # 如果未指定保存路径，则使用原图所在文件夹
            save_path = os.path.dirname(self.image_path)
            
        # 构建保存文件名
        filename = os.path.basename(self.image_path)
        name, ext = os.path.splitext(filename)
        save_filename = f"{name}_processed{ext}"
        save_filepath = os.path.join(save_path, save_filename)
        
        # 保存图片
        try:
            self.resizer.save_image(save_filepath)
            messagebox.showinfo("成功", f"图片已保存到：\n{save_filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"保存图片失败：{str(e)}")
    
    def select_batch_folder(self):
        """选择批量处理的文件夹"""
        folder_path = filedialog.askdirectory(title="选择包含图片的文件夹")
        
        if folder_path:
            self.batch_folder = folder_path
            self.folder_var.set(folder_path)
            
            # 获取文件夹中的所有图片文件
            self.batch_files = []
            supported_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".webp")
            
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and file.lower().endswith(supported_extensions):
                    self.batch_files.append(file_path)
            
            if self.batch_files:
                self.progress_label.config(text=f"找到 {len(self.batch_files)} 个图片文件")
            else:
                self.progress_label.config(text="文件夹中没有支持的图片文件")
                messagebox.showinfo("提示", "所选文件夹中没有支持的图片文件")
    
    def batch_process(self):
        """批量处理图片"""
        if not self.batch_files:
            messagebox.showerror("错误", "请先选择包含图片的文件夹")
            return
        
        # 获取处理参数
        method = self.method_var.get()
        quality = self.quality_var.get()
        target_size = 0
        if self.target_var.get().strip():
            try:
                target_size = int(self.target_var.get())
            except ValueError:
                messagebox.showerror("错误", "目标大小必须是整数")
                return
        width = self.width_var.get()
        height = self.height_var.get()
        keep_ratio = self.keep_ratio_var.get()
        
        # 创建输出文件夹
        output_folder = os.path.join(self.batch_folder, "resized_images")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # 处理进度
        total_files = len(self.batch_files)
        processed_count = 0
        success_count = 0
        failed_count = 0
        
        # 批量处理
        for file_path in self.batch_files:
            # 更新进度
            processed_count += 1
            progress = (processed_count / total_files) * 100
            self.progress_var.set(progress)
            self.progress_label.config(text=f"处理中: {processed_count}/{total_files} - {file_path}")
            self.root.update()
            
            # 加载图片
            if not self.resizer.load_image(file_path):
                failed_count += 1
                continue
            
            # 处理图片
            success = False
            if method == "quality":
                success = self.resizer.process_image_quality(quality, target_size)
            else:  # dimensions
                success = self.resizer.process_image_dimensions(width, height, keep_ratio)
            
            if not success:
                failed_count += 1
                continue
            
            # 保存图片
            base_name = os.path.basename(file_path)
            output_path = os.path.join(output_folder, f"resized_{base_name}")
            
            if self.resizer.save_image(output_path, quality):
                success_count += 1
            else:
                failed_count += 1
        
        # 更新进度
        self.progress_var.set(100)
        self.progress_label.config(text=f"处理完成: 成功 {success_count} 个, 失败 {failed_count} 个")
        
        # 显示结果
        messagebox.showinfo("批量处理完成", 
                          f"处理完成:\n" +
                          f"- 总计: {total_files} 个文件\n" +
                          f"- 成功: {success_count} 个\n" +
                          f"- 失败: {failed_count} 个\n\n" +
                          f"处理后的图片保存在:\n{output_folder}")
    
    def browse_save_path(self):
        """选择保存路径"""
        save_path = filedialog.askdirectory()
        if save_path:
            self.save_path_var.set(save_path)


def main():
    root = tk.Tk()
    app = ImageResizerGUI(root)
    # 添加窗口关闭事件处理
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()


if __name__ == "__main__":
    main()
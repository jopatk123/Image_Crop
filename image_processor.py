import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading
import queue

class ImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理工具")
        self.root.geometry("900x700")
        
        self.images_queue = queue.Queue()
        self.processed_images = []
        self.current_image_index = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 文件夹选择
        folder_frame = ttk.Frame(control_frame)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(folder_frame, text="选择文件夹：").pack(anchor=tk.W)
        
        folder_select_frame = ttk.Frame(folder_frame)
        folder_select_frame.pack(fill=tk.X, pady=5)
        
        self.folder_path = tk.StringVar()
        ttk.Entry(folder_select_frame, textvariable=self.folder_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_select_frame, text="浏览", command=self.browse_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 包含子文件夹选项
        self.include_subfolders = tk.BooleanVar(value=True)
        ttk.Checkbutton(folder_frame, text="包含子文件夹", variable=self.include_subfolders).pack(anchor=tk.W)
        
        ttk.Button(folder_frame, text="加载图片", command=self.load_images).pack(fill=tk.X, pady=(5, 0))
        
        # 尺寸调整
        resize_frame = ttk.LabelFrame(control_frame, text="调整尺寸", padding="10")
        resize_frame.pack(fill=tk.X, pady=10)
        
        width_frame = ttk.Frame(resize_frame)
        width_frame.pack(fill=tk.X, pady=5)
        ttk.Label(width_frame, text="宽度：").pack(side=tk.LEFT)
        self.width_var = tk.StringVar()
        ttk.Entry(width_frame, textvariable=self.width_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        height_frame = ttk.Frame(resize_frame)
        height_frame.pack(fill=tk.X, pady=5)
        ttk.Label(height_frame, text="高度：").pack(side=tk.LEFT)
        self.height_var = tk.StringVar()
        ttk.Entry(height_frame, textvariable=self.height_var, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(resize_frame, text="调整尺寸", command=self.resize_images).pack(fill=tk.X, pady=(5, 0))
        
        # 裁剪设置
        crop_frame = ttk.LabelFrame(control_frame, text="裁剪设置", padding="10")
        crop_frame.pack(fill=tk.X, pady=10)
        
        pixels_frame = ttk.Frame(crop_frame)
        pixels_frame.pack(fill=tk.X, pady=5)
        ttk.Label(pixels_frame, text="裁剪像素：").pack(side=tk.LEFT)
        self.crop_pixels = tk.StringVar(value="100")
        ttk.Entry(pixels_frame, textvariable=self.crop_pixels, width=10).pack(side=tk.LEFT, padx=(5, 0))
        
        # 裁剪方式
        self.crop_mode = tk.StringVar(value="bottom")
        ttk.Radiobutton(crop_frame, text="从底部裁剪", variable=self.crop_mode, value="bottom").pack(anchor=tk.W)
        ttk.Radiobutton(crop_frame, text="从顶部裁剪", variable=self.crop_mode, value="top").pack(anchor=tk.W)
        
        ttk.Button(crop_frame, text="裁剪图片", command=self.crop_images).pack(fill=tk.X, pady=(5, 0))
        
        # 保存设置
        save_frame = ttk.LabelFrame(control_frame, text="保存设置", padding="10")
        save_frame.pack(fill=tk.X, pady=10)
        
        self.save_path = tk.StringVar()
        save_path_frame = ttk.Frame(save_frame)
        save_path_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(save_path_frame, textvariable=self.save_path).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(save_path_frame, text="浏览", command=self.browse_save_folder).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(save_frame, text="保存图片", command=self.save_images).pack(fill=tk.X, pady=(5, 0))
        
        # 右侧图片预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="图片预览", padding="10")
        preview_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 图片导航
        nav_frame = ttk.Frame(preview_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(nav_frame, text="上一张", command=self.prev_image).pack(side=tk.LEFT)
        self.image_counter = ttk.Label(nav_frame, text="0/0")
        self.image_counter.pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="下一张", command=self.next_image).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="删除", command=self.delete_image).pack(side=tk.LEFT, padx=(10, 0))
        
        # 图片显示区域
        self.canvas = tk.Canvas(preview_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.folder_path.set(folder_path)
    
    def browse_save_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.save_path.set(folder_path)
    
    def load_images(self):
        folder_path = self.folder_path.get()
        if not folder_path or not os.path.isdir(folder_path):
            messagebox.showerror("错误", "请选择有效的文件夹")
            return
        
        self.status_var.set("正在加载图片...")
        self.processed_images = []
        self.current_image_index = 0
        
        # 在后台线程中加载图片
        threading.Thread(target=self._load_images_thread, args=(folder_path,), daemon=True).start()
    
    def _load_images_thread(self, folder_path):
        image_files = []
        include_subfolders = self.include_subfolders.get()
        
        # 收集所有图片文件
        if include_subfolders:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                        image_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(folder_path):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    image_files.append(os.path.join(folder_path, file))
        
        # 加载图片
        for file_path in image_files:
            try:
                img = Image.open(file_path)
                self.processed_images.append({
                    'path': file_path,
                    'image': img,
                    'original': img.copy()
                })
            except Exception as e:
                print(f"无法加载图片 {file_path}: {e}")
        
        # 更新UI
        self.root.after(0, self._update_after_load)
    
    def _update_after_load(self):
        if self.processed_images:
            self.status_var.set(f"已加载 {len(self.processed_images)} 张图片")
            self.update_image_counter()
            self.display_current_image()
        else:
            self.status_var.set("未找到图片")
            self.image_counter.config(text="0/0")
            self.canvas.delete("all")
    
    def update_image_counter(self):
        if self.processed_images:
            self.image_counter.config(text=f"{self.current_image_index + 1}/{len(self.processed_images)}")
        else:
            self.image_counter.config(text="0/0")
    
    def display_current_image(self):
        if not self.processed_images:
            return
        
        self.canvas.delete("all")
        img_data = self.processed_images[self.current_image_index]
        img = img_data['image']
        
        # 调整图片大小以适应画布
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:  # 画布尚未完全初始化
            self.root.after(100, self.display_current_image)
            return
        
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        resized_img = img.resize((new_width, new_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(resized_img)
        
        # 保存引用以防止垃圾回收
        self.current_photo = photo
        
        # 在画布中央显示图片
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=photo)
        
        # 显示图片信息
        filename = os.path.basename(img_data['path'])
        dimensions = f"{img_width}x{img_height}"
        self.status_var.set(f"当前图片: {filename} ({dimensions})")
    
    def prev_image(self):
        if self.processed_images and self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_image_counter()
            self.display_current_image()
    
    def next_image(self):
        if self.processed_images and self.current_image_index < len(self.processed_images) - 1:
            self.current_image_index += 1
            self.update_image_counter()
            self.display_current_image()
    
    def resize_images(self):
        if not self.processed_images:
            messagebox.showerror("错误", "没有加载图片")
            return
        
        try:
            width = int(self.width_var.get()) if self.width_var.get() else None
            height = int(self.height_var.get()) if self.height_var.get() else None
            
            if not width and not height:
                messagebox.showerror("错误", "请至少输入宽度或高度")
                return
            
            self.status_var.set("正在调整图片尺寸...")
            threading.Thread(target=self._resize_images_thread, args=(width, height), daemon=True).start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def _resize_images_thread(self, width, height):
        for img_data in self.processed_images:
            try:
                original = img_data['original']
                orig_width, orig_height = original.size
                
                # 计算新尺寸
                if width and height:  # 同时指定宽度和高度
                    new_size = (width, height)
                elif width:  # 只指定宽度，按比例计算高度
                    ratio = width / orig_width
                    new_size = (width, int(orig_height * ratio))
                else:  # 只指定高度，按比例计算宽度
                    ratio = height / orig_height
                    new_size = (int(orig_width * ratio), height)
                
                # 调整图片尺寸
                resized_img = original.resize(new_size, Image.LANCZOS)
                img_data['image'] = resized_img
                
            except Exception as e:
                print(f"调整图片尺寸失败: {e}")
        
        # 更新UI
        self.root.after(0, lambda: self._update_after_process("尺寸调整完成"))
    
    def crop_images(self):
        if not self.processed_images:
            messagebox.showerror("错误", "没有加载图片")
            return
        
        try:
            pixels = int(self.crop_pixels.get())
            if pixels <= 0:
                messagebox.showerror("错误", "裁剪像素必须大于0")
                return
            
            crop_mode = self.crop_mode.get()
            self.status_var.set("正在裁剪图片...")
            threading.Thread(target=self._crop_images_thread, args=(pixels, crop_mode), daemon=True).start()
            
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def _crop_images_thread(self, pixels, crop_mode):
        total_images = len(self.processed_images)
        processed_count = 0
        skipped_count = 0
        
        for img_data in self.processed_images:
            try:
                img = img_data['image']
                width, height = img.size
                
                if height <= pixels:
                    skipped_count += 1
                    continue  # 图片高度小于裁剪像素，跳过
                
                if crop_mode == "bottom":
                    # 保留上部分，裁剪底部
                    crop_box = (0, 0, width, height - pixels)
                else:  # crop_mode == "top"
                    # 保留下部分，裁剪顶部
                    crop_box = (0, pixels, width, height)
                
                cropped_img = img.crop(crop_box)
                img_data['image'] = cropped_img
                processed_count += 1
                
                # 每处理5张图片更新一次状态
                if processed_count % 5 == 0:
                    self.root.after(0, lambda count=processed_count: 
                                   self.status_var.set(f"正在裁剪图片... {count}/{total_images}"))
                
            except Exception as e:
                print(f"裁剪图片失败: {e}")
        
        # 更新UI
        self.root.after(0, lambda: self._update_after_process(f"裁剪完成: 成功处理 {processed_count} 张图片，跳过 {skipped_count} 张图片"))
    
    def _update_after_process(self, message):
        self.status_var.set(message)
        self.display_current_image()
    
    def delete_image(self):
        if not self.processed_images:
            messagebox.showerror("错误", "没有图片可删除")
            return
        
        # 确认是否删除
        filename = os.path.basename(self.processed_images[self.current_image_index]['path'])
        confirm = messagebox.askyesno("确认删除", f"确定要删除图片 {filename} 吗？")
        if not confirm:
            return
        
        # 删除当前图片
        del self.processed_images[self.current_image_index]
        
        # 更新图片索引和显示
        if not self.processed_images:
            # 如果删除后没有图片了
            self.current_image_index = 0
            self.canvas.delete("all")
            self.image_counter.config(text="0/0")
            self.status_var.set("没有图片")
        else:
            # 如果删除的是最后一张图片，索引减1
            if self.current_image_index >= len(self.processed_images):
                self.current_image_index = len(self.processed_images) - 1
            
            # 更新计数器和显示
            self.update_image_counter()
            self.display_current_image()
            
        # 更新状态栏
        if self.processed_images:
            self.status_var.set(f"已删除图片，剩余 {len(self.processed_images)} 张图片")
        else:
            self.status_var.set("已删除所有图片")
    
    def save_images(self):
        if not self.processed_images:
            messagebox.showerror("错误", "没有图片可保存")
            return
        
        save_path = self.save_path.get()
        if not save_path:
            save_path = filedialog.askdirectory(title="选择保存文件夹")
            if not save_path:
                return
            self.save_path.set(save_path)
        
        if not os.path.isdir(save_path):
            try:
                os.makedirs(save_path)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建保存文件夹: {e}")
                return
        
        self.status_var.set("正在保存图片...")
        threading.Thread(target=self._save_images_thread, args=(save_path,), daemon=True).start()
    
    def _save_images_thread(self, save_path):
        saved_count = 0
        for img_data in self.processed_images:
            try:
                img = img_data['image']
                original_path = img_data['path']
                filename = os.path.basename(original_path)
                
                # 构建保存路径
                save_file_path = os.path.join(save_path, f"processed_{filename}")
                
                # 保存图片
                img.save(save_file_path)
                saved_count += 1
                
            except Exception as e:
                print(f"保存图片失败 {filename}: {e}")
        
        # 更新UI
        self.root.after(0, lambda: self.status_var.set(f"已保存 {saved_count} 张图片到 {save_path}"))


def main():
    root = tk.Tk()
    app = ImageProcessor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
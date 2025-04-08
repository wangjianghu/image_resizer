#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from PIL import Image
import io

class ImageResizer:
    def __init__(self):
        self.source_image_path = ""
        self.original_image = None
        self.processed_image = None
    
    def load_image(self, image_path):
        """加载图片"""
        try:
            self.source_image_path = image_path
            self.original_image = Image.open(image_path)
            
            # 打印原始图片信息
            file_size = os.path.getsize(image_path)
            print(f"\n原始图片信息:")
            print(f"路径: {image_path}")
            print(f"大小: {self.format_size(file_size)}")
            print(f"尺寸: {self.original_image.width} x {self.original_image.height}")
            print(f"格式: {self.original_image.format}")
            
            return True
        except Exception as e:
            print(f"\n错误: 无法打开图片: {str(e)}")
            return False
    
    def process_image_quality(self, quality=85, target_size=0):
        """通过调整质量处理图片"""
        if not self.original_image:
            print("\n错误: 请先加载图片")
            return False
        
        try:
            # 获取图片格式
            img_format = os.path.splitext(self.source_image_path)[1].lower().replace(".", "")
            if img_format == "jpg":
                img_format = "jpeg"
            
            # 复制原始图片
            self.processed_image = self.original_image.copy()
            
            # 如果设置了目标大小，则尝试达到目标大小
            if target_size > 0:
                print(f"\n尝试达到目标大小: {target_size} KB...")
                
                # 对于PNG格式，使用特殊处理方法
                if img_format.lower() == "png":
                    success = self.process_png_for_target_size(target_size * 1024)
                    if success:
                        # 计算处理后图片的大小
                        buffer = io.BytesIO()
                        self.processed_image.save(buffer, format=img_format)
                        processed_size = len(buffer.getvalue())
                        
                        # 打印处理后图片信息
                        print(f"\n处理后图片信息:")
                        print(f"大小: {self.format_size(processed_size)}")
                        print(f"尺寸: {self.processed_image.width} x {self.processed_image.height}")
                        print(f"注意: PNG是无损格式，调整质量效果有限")
                        
                        return True
                else:
                    # 对于JPEG等有损格式，使用质量调整
                    quality = self.find_quality_for_target_size(target_size * 1024, img_format)
                    print(f"找到合适的质量值: {quality}")
            
            # 计算处理后图片的大小
            buffer = io.BytesIO()
            if img_format.lower() in ["jpeg", "jpg"]:
                self.processed_image.save(buffer, format=img_format, quality=quality)
            else:
                # 对于PNG格式，提示用户质量调整效果有限
                if img_format.lower() == "png":
                    print("\n注意: PNG是无损格式，调整质量参数效果有限，建议使用调整尺寸方法或转换为JPEG格式")
                self.processed_image.save(buffer, format=img_format)
            
            processed_size = len(buffer.getvalue())
            
            # 打印处理后图片信息
            print(f"\n处理后图片信息:")
            print(f"大小: {self.format_size(processed_size)}")
            print(f"尺寸: {self.processed_image.width} x {self.processed_image.height}")
            print(f"质量: {quality}")
            
            return True
        except Exception as e:
            print(f"\n错误: 处理图片时出错: {str(e)}")
            return False
    
    def process_image_dimensions(self, width, height, keep_ratio=True):
        """通过调整尺寸处理图片"""
        if not self.original_image:
            print("\n错误: 请先加载图片")
            return False
        
        try:
            # 获取图片格式
            img_format = os.path.splitext(self.source_image_path)[1].lower().replace(".", "")
            if img_format == "jpg":
                img_format = "jpeg"
            
            if width <= 0 or height <= 0:
                print("\n错误: 宽度和高度必须大于0")
                return False
            
            # 如果保持比例，则计算新的尺寸
            if keep_ratio:
                orig_width, orig_height = self.original_image.size
                ratio = min(width / orig_width, height / orig_height)
                width = int(orig_width * ratio)
                height = int(orig_height * ratio)
                print(f"\n保持宽高比，调整后的尺寸: {width} x {height}")
            
            # 调整尺寸
            self.processed_image = self.original_image.resize((width, height), Image.LANCZOS)
            
            # 计算处理后图片的大小
            buffer = io.BytesIO()
            if img_format.lower() in ["jpeg", "jpg"]:
                self.processed_image.save(buffer, format=img_format, quality=85)
            else:
                self.processed_image.save(buffer, format=img_format)
            
            processed_size = len(buffer.getvalue())
            
            # 打印处理后图片信息
            print(f"\n处理后图片信息:")
            print(f"大小: {self.format_size(processed_size)}")
            print(f"尺寸: {self.processed_image.width} x {self.processed_image.height}")
            
            return True
        except Exception as e:
            print(f"\n错误: 处理图片时出错: {str(e)}")
            return False
    
    def process_png_for_target_size(self, target_size):
        """处理PNG图片以达到目标大小
        
        PNG是无损压缩格式，调整质量参数效果有限。此方法尝试通过以下方式达到目标大小：
        1. 调整色彩深度（从RGBA转为RGB，或降低位深度）
        2. 调整图片尺寸
        3. 使用不同的压缩级别
        4. 添加元数据或填充数据以增加文件大小
        5. 增加图片尺寸（如果需要增大文件）
        """
        print("\nPNG是无损压缩格式，尝试特殊处理方法...")
        
        # 保存原始图像副本
        original_copy = self.original_image.copy()
        best_image = None
        best_diff = float('inf')
        best_size = 0
        original_size = 0
        
        # 获取原始图片大小
        buffer = io.BytesIO()
        self.original_image.save(buffer, format='PNG')
        original_size = len(buffer.getvalue())
        print(f"原始PNG图片大小: {self.format_size(original_size)}")
        
        # 检查是否需要增大文件
        need_increase = original_size < target_size
        if need_increase:
            print(f"需要增加文件大小到: {self.format_size(target_size)}")
        
        # 尝试方法1：如果图片有Alpha通道，尝试移除它（仅当需要减小文件时）
        if not need_increase and self.original_image.mode == 'RGBA':
            print("尝试移除Alpha通道...")
            rgb_image = self.original_image.convert('RGB')
            buffer = io.BytesIO()
            rgb_image.save(buffer, format='PNG')
            current_size = len(buffer.getvalue())
            
            diff = abs(current_size - target_size)
            print(f"  移除Alpha通道后大小: {self.format_size(current_size)}")
            
            if diff < best_diff:
                best_diff = diff
                best_image = rgb_image
                best_size = current_size
        
        # 尝试方法2：调整色彩模式和位深度（仅当需要减小文件时）
        if not need_increase:
            color_modes = []
            if self.original_image.mode != 'P':
                color_modes.append(('P', 256))  # 8位调色板模式
            
            for mode, colors in color_modes:
                print(f"尝试转换为{mode}模式 ({colors}色)...")
                try:
                    converted_image = self.original_image.convert(mode, palette=Image.ADAPTIVE, colors=colors)
                    buffer = io.BytesIO()
                    converted_image.save(buffer, format='PNG')
                    current_size = len(buffer.getvalue())
                    
                    diff = abs(current_size - target_size)
                    print(f"  转换为{mode}模式后大小: {self.format_size(current_size)}")
                    
                    if diff < best_diff:
                        best_diff = diff
                        best_image = converted_image
                        best_size = current_size
                except Exception as e:
                    print(f"  转换为{mode}模式失败: {str(e)}")
        
        # 尝试方法3：调整图片尺寸（缩小，仅当需要减小文件时）
        if not need_increase and (best_size > target_size or best_image is None):
            print("尝试缩小图片尺寸...")
            
            # 从100%开始，每次减少5%
            for scale in range(100, 29, -5):  # 最小缩小到30%
                scale_factor = scale / 100.0
                width = int(self.original_image.width * scale_factor)
                height = int(self.original_image.height * scale_factor)
                
                resized_image = self.original_image.resize((width, height), Image.LANCZOS)
                
                # 如果之前找到了更好的色彩模式，应用它
                if best_image is not None and best_image.mode != resized_image.mode:
                    try:
                        resized_image = resized_image.convert(best_image.mode)
                    except:
                        pass
                
                buffer = io.BytesIO()
                resized_image.save(buffer, format='PNG')
                current_size = len(buffer.getvalue())
                
                diff = abs(current_size - target_size)
                print(f"  缩放到{scale}%后大小: {self.format_size(current_size)}")
                
                if diff < best_diff:
                    best_diff = diff
                    best_image = resized_image
                    best_size = current_size
                
                # 如果已经小于目标大小，停止缩小
                if current_size <= target_size:
                    break
        
        # 尝试方法4：增加图片尺寸（仅当需要增大文件时）
        if need_increase and (best_size < target_size or best_image is None):
            print("尝试增大图片尺寸...")
            
            # 从100%开始，每次增加10%
            base_image = best_image if best_image is not None else self.original_image
            for scale in range(110, 301, 10):  # 最大放大到300%
                scale_factor = scale / 100.0
                width = int(base_image.width * scale_factor)
                height = int(base_image.height * scale_factor)
                
                resized_image = base_image.resize((width, height), Image.LANCZOS)
                
                buffer = io.BytesIO()
                resized_image.save(buffer, format='PNG')
                current_size = len(buffer.getvalue())
                
                diff = abs(current_size - target_size)
                print(f"  放大到{scale}%后大小: {self.format_size(current_size)}")
                
                if diff < best_diff:
                    best_diff = diff
                    best_image = resized_image
                    best_size = current_size
                
                # 如果已经大于目标大小，停止放大
                if current_size >= target_size:
                    break
        
        # 尝试方法5：添加元数据填充（仅当需要增大文件且其他方法效果不佳时）
        if need_increase and (best_size < target_size or abs(best_size - target_size) > target_size * 0.1):
            print("尝试添加元数据填充...")
            
            base_image = best_image if best_image is not None else self.original_image
            
            # 创建一个新的图像，添加填充数据
            padded_image = base_image.copy()
            
            # 尝试不同大小的填充数据
            for padding_size in range(1, 21):  # 尝试1KB到20KB的填充
                padding_kb = padding_size * 1024
                
                # 创建一个临时缓冲区来保存图像和元数据
                buffer = io.BytesIO()
                
                # 保存图像
                padded_image.save(buffer, format='PNG', pnginfo=self._create_padding_metadata(padding_kb))
                current_size = len(buffer.getvalue())
                
                diff = abs(current_size - target_size)
                print(f"  添加{padding_kb/1024}KB填充后大小: {self.format_size(current_size)}")
                
                if diff < best_diff:
                    best_diff = diff
                    best_image = padded_image
                    best_size = current_size
                
                # 如果已经达到或超过目标大小，停止添加
                if current_size >= target_size:
                    break
        
        # 如果找到了合适的处理方法
        if best_image is not None:
            self.processed_image = best_image
            print(f"\n找到最佳处理方法，处理后大小: {self.format_size(best_size)}")
            
            # 如果处理后大小仍然与目标相差较大，给出建议
            if abs(best_size - target_size) > target_size * 0.1:  # 相差超过10%
                print("\n提示: PNG是无损格式，难以精确控制文件大小。")
                print("如果需要精确控制文件大小，建议考虑以下选项:")
                print("1. 使用JPEG格式保存（有损但文件更小）")
                print("2. 进一步调整图片尺寸")
                print("3. 使用专业图像优化工具")
            
            return True
        else:
            print("\n无法达到目标大小，使用原始图片")
            self.processed_image = original_copy
            return False
    
    def _create_padding_metadata(self, padding_size):
        """创建包含填充数据的元数据"""
        from PIL import PngImagePlugin
        
        # 创建元数据对象
        meta = PngImagePlugin.PngInfo()
        
        # 生成填充数据（随机字符串）
        import random
        import string
        
        # 创建一个足够大的随机字符串
        padding_chars = string.ascii_letters + string.digits
        padding_data = ''.join(random.choice(padding_chars) for _ in range(padding_size))
        
        # 添加到元数据中（分块添加，避免单个键值对过大）
        chunk_size = 1024  # 每个键值对最大1KB
        chunks = [padding_data[i:i+chunk_size] for i in range(0, len(padding_data), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            meta.add_text(f"padding_{i}", chunk)
        
        return meta
        
        # 如果找到了合适的处理方法
        if best_image is not None:
            self.processed_image = best_image
            print(f"\n找到最佳处理方法，处理后大小: {self.format_size(best_size)}")
            
            # 如果处理后大小仍然与目标相差较大，给出建议
            if abs(best_size - target_size) > target_size * 0.2:  # 相差超过20%
                print("\n提示: PNG是无损格式，难以精确控制文件大小。")
                print("如果需要精确控制文件大小，建议考虑以下选项:")
                print("1. 使用JPEG格式保存（有损但文件更小）")
                print("2. 进一步调整图片尺寸")
                print("3. 使用专业图像优化工具")
            
            return True
        else:
            print("\n无法达到目标大小，使用原始图片")
            self.processed_image = original_copy
            return False
    
    def find_quality_for_target_size(self, target_size, img_format):
        """二分查找合适的质量值"""
        min_quality = 1
        max_quality = 100
        best_quality = 85
        best_diff = float('inf')
        
        print("正在查找最佳质量值...")
        
        while min_quality <= max_quality:
            mid_quality = (min_quality + max_quality) // 2
            
            buffer = io.BytesIO()
            self.original_image.save(buffer, format=img_format, quality=mid_quality)
            current_size = len(buffer.getvalue())
            
            diff = abs(current_size - target_size)
            
            print(f"  质量: {mid_quality}, 大小: {self.format_size(current_size)}, 目标: {self.format_size(target_size)}")
            
            if diff < best_diff:
                best_diff = diff
                best_quality = mid_quality
            
            if current_size > target_size:
                max_quality = mid_quality - 1
            else:
                min_quality = mid_quality + 1
            
            # 如果已经足够接近目标大小，就停止
            if diff < target_size * 0.05:  # 5%误差内
                break
        
        return best_quality
    
    def save_image(self, output_path=None, quality=85):
        """保存处理后的图片"""
        if not self.processed_image:
            print("\n错误: 请先处理图片")
            return False
        
        try:
            # 如果没有指定输出路径，则在原始文件名前加上"resized_"
            if not output_path:
                dir_name = os.path.dirname(self.source_image_path)
                base_name = os.path.basename(self.source_image_path)
                output_path = os.path.join(dir_name, f"resized_{base_name}")
            
            # 获取保存格式
            save_format = os.path.splitext(output_path)[1].lower().replace(".", "")
            if save_format == "jpg":
                save_format = "jpeg"
            
            # 保存图片
            if save_format.lower() in ["jpeg", "jpg"]:
                self.processed_image.save(output_path, format=save_format, quality=quality)
            else:
                self.processed_image.save(output_path, format=save_format)
            
            print(f"\n图片已保存到: {output_path}")
            print(f"文件大小: {self.format_size(os.path.getsize(output_path))}")
            
            return True
        except Exception as e:
            print(f"\n错误: 保存图片时出错: {str(e)}")
            return False
    
    def format_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"


def main():
    parser = argparse.ArgumentParser(description="图片大小修改工具 - 在不改变图片格式的前提下，改变图片的大小")
    parser.add_argument("image_path", help="要处理的图片路径")
    parser.add_argument("-o", "--output", help="输出图片路径，默认为原始路径前加上'resized_'")
    parser.add_argument("-m", "--method", choices=["quality", "dimensions"], default="quality", help="处理方法: quality(调整质量) 或 dimensions(调整尺寸)，默认为quality")
    parser.add_argument("-q", "--quality", type=int, default=85, help="JPEG质量值(1-100)，默认为85")
    parser.add_argument("-t", "--target-size", type=int, default=0, help="目标文件大小(KB)，如果设置，将自动调整质量以达到目标大小")
    parser.add_argument("-w", "--width", type=int, default=0, help="调整后的宽度，仅在dimensions方法中使用")
    parser.add_argument("-ht", "--height", type=int, default=0, help="调整后的高度，仅在dimensions方法中使用")
    parser.add_argument("-k", "--keep-ratio", action="store_true", default=True, help="保持宽高比，仅在dimensions方法中使用，默认为True")
    parser.add_argument("-nk", "--no-keep-ratio", action="store_false", dest="keep_ratio", help="不保持宽高比，仅在dimensions方法中使用")
    
    args = parser.parse_args()
    
    # 创建图片处理器
    resizer = ImageResizer()
    
    # 加载图片
    if not resizer.load_image(args.image_path):
        return 1
    
    # 根据选择的方法处理图片
    if args.method == "quality":
        if not resizer.process_image_quality(args.quality, args.target_size):
            return 1
    else:  # dimensions
        if args.width <= 0 or args.height <= 0:
            print("\n错误: 使用dimensions方法时，必须指定宽度和高度")
            return 1
        
        if not resizer.process_image_dimensions(args.width, args.height, args.keep_ratio):
            return 1
    
    # 保存图片
    if not resizer.save_image(args.output, args.quality):
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
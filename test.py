import os
import glob
from tools.md2docx import get_markdown_to_word_tool

def main():
    # 获取工具实例
    markdown_to_word_tool = get_markdown_to_word_tool()
    
    # 设置输入和输出目录（使用相对路径）
    input_dir = "C:/project/horion/multimodal_dynamic/docs_summary"
    output_dir = "C:/project/horion/multimodal_dynamic/results"
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取所有 Markdown 文件
    md_files = glob.glob(os.path.join(input_dir, "*.md"))
    
    if not md_files:
        print(f"在 {input_dir} 目录下未找到 Markdown 文件")
        return
    
    print(f"找到 {len(md_files)} 个 Markdown 文件，开始处理...")
    
    # 处理每个 Markdown 文件
    for md_file in md_files:
        # 从输入文件名获取基本文件名
        base_name = os.path.basename(md_file)
        output_filename = os.path.splitext(base_name)[0] + ".docx"
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"正在处理: {md_file} -> {output_path}")
        
        # 使用run方法调用工具
        try:
            result = markdown_to_word_tool.run({
                "input_path": md_file,
                "output_path": output_path,
                "keep_bookmarks": False
            })
            
            # 打印结果
            print(result)
            print("-" * 50)
        except Exception as e:
            print(f"处理 {md_file} 时出错: {str(e)}")
            print("-" * 50)
    
    print("所有文件处理完成！")

if __name__ == "__main__":
    main()
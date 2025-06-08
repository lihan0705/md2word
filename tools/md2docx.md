# Markdown到Word转换工具 (LangChain Function Call)

## 概述

`md2docx`是一个LangChain工具，用于将Markdown文件转换为Microsoft Word (.docx)文档。该工具特别支持渲染嵌入式图表（Mermaid、Vega、Vega-Lite）并将特定的Unicode颜色图标转换为彩色文本。

## 功能特点

- **Markdown到Word转换**：基础的Markdown到Word文档转换
- **图表渲染**：
  - 自动检测并渲染Mermaid图表为PNG图像
  - 自动检测并渲染Vega和Vega-Lite图表为PNG图像
- **文本格式化**：
  - 将Unicode颜色图标（🟢绿色、🟡黄色、🔴红色、⚪白色）转换为Word中相应颜色的文本
- **Word文档格式化**：
  - 确保所有表格都具有完整的单线网格边框
  - 可选择是否删除文档中的书签（通常由Pandoc为标题添加）

## 技术架构

该工具基于以下核心组件：

1. **MarkdownConverter**：主要转换协调器，管理整个转换流程
2. **DiagramRenderer**：负责将图表代码块渲染为图像文件
3. **ASTTransformer**：修改Pandoc的抽象语法树(AST)，替换图表并应用格式化
4. **DocxFormatter**：对生成的Word文档应用后处理格式化

## 依赖项

- **pypandoc**：用于Markdown到Word的核心转换
- **altair**：用于渲染Vega和Vega-Lite图表
- **mermaid**：用于渲染Mermaid图表
- **python-docx**：(可选)用于高级Word文档格式化

## 使用方法

### 作为LangChain工具使用

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from tools.md2docx import get_markdown_to_word_tool

# 获取工具实例
markdown_to_word_tool = get_markdown_to_word_tool()

# 创建LLM
llm = OpenAI(temperature=0)

# 初始化代理
agent = initialize_agent(
    [markdown_to_word_tool],
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 使用代理执行任务
result = agent.run(
    "将'example.md'转换为Word文档，并保存为'output.docx'"
)
print(result)
```

### 直接调用工具

```python
from tools.md2docx import get_markdown_to_word_tool

# 获取工具实例
markdown_to_word_tool = get_markdown_to_word_tool()

# 方法1：使用run方法（推荐）
result = markdown_to_word_tool.run({
    "input_path": "path/to/example.md",
    "output_path": "path/to/output.docx",
    "keep_bookmarks": False
})

# 方法2：使用_run方法（直接传参）
result = markdown_to_word_tool._run(
    input_path="path/to/example.md",
    output_path="path/to/output.docx",
    keep_bookmarks=False
)

print(result)
```

## 输入参数

| 参数名 | 类型 | 必需 | 默认值 | 描述 |
|--------|------|------|--------|------|
| `input_path` | str | 是 | - | 输入Markdown文件的路径 |
| `output_path` | str | 否 | None | 输出Word文件的路径。如果未提供，将使用与输入文件相同的名称但扩展名为.docx |
| `keep_bookmarks` | bool | 否 | False | 是否保留文档中的书签 |

## 返回值

工具返回一个字符串，表示转换的结果：

- 成功时：`"转换成功！输出文件保存在: {output_path}"`
- 失败时：`"转换失败，请检查错误信息。"` 或 `"转换过程中发生错误: {error_message}"`

## 示例场景

### 示例1：基本转换

```python
from tools.md2docx import get_markdown_to_word_tool

markdown_to_word_tool = get_markdown_to_word_tool()
result = markdown_to_word_tool.run({"input_path": "report.md"})
print(result)  # 输出：转换成功！输出文件保存在: report.docx
```

### 示例2：指定输出路径

```python
from tools.md2docx import get_markdown_to_word_tool

markdown_to_word_tool = get_markdown_to_word_tool()
result = markdown_to_word_tool.run({
    "input_path": "docs/report.md",
    "output_path": "output/final_report.docx"
})
print(result)  # 输出：转换成功！输出文件保存在: output/final_report.docx
```

### 示例3：保留书签

```python
from tools.md2docx import get_markdown_to_word_tool

markdown_to_word_tool = get_markdown_to_word_tool()
result = markdown_to_word_tool.run({
    "input_path": "docs/report.md",
    "keep_bookmarks": True
})
print(result)  # 输出：转换成功！输出文件保存在: docs/report.docx
```

## 错误处理

该工具会捕获转换过程中的异常，并返回描述性错误消息。常见错误包括：

- 文件不存在
- 权限问题
- 图表渲染失败
- Pandoc转换错误

## 注意事项

1. 确保已安装所有必要的依赖项（pypandoc、altair、mermaid）
2. 对于高级Word格式化功能，需要安装python-docx
3. 某些复杂的Mermaid图表可能需要安装Graphviz
4. 确保Pandoc已安装并在系统PATH中可用

## 扩展与自定义

该工具设计为模块化的，可以通过以下方式进行扩展：

1. 添加对更多图表类型的支持（如PlantUML、Ditaa等）
2. 自定义Word文档样式和格式
3. 添加对其他Unicode图标的颜色转换支持
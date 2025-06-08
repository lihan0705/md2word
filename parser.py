import os
import sys
import json
import hashlib
import tempfile
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Any
import pypandoc
import altair as alt
from mermaid import Mermaid
from mermaid.graph import Graph

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

COLOR_ICONS = {
    "🟢": {"text": "●", "color": (0, 128, 0)},
    "🟡": {"text": "●", "color": (255, 192, 0)},
    "🔴": {"text": "●", "color": (255, 0, 0)},
    "⚪": {"text": "●", "color": (255, 255, 255)}
}

class DiagramRenderer:
    """Handles rendering of diagrams to image files"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        
    def render(self, resources: List[Dict]) -> None:
        """Render all detected diagrams"""
        for resource in resources:
            try:
                if resource['type'] == 'mermaid':
                    self._render_mermaid(resource)
                elif resource['type'] in ['vega', 'vega-lite']:
                    self._render_vega(resource)
            except Exception as e:
                print(f"Failed to render {resource['type']} diagram: {str(e)}")
                resource['error'] = True
    
    def _render_mermaid(self, resource: Dict) -> None:
        """适用于复杂图表的高清晰度渲染"""
        output_file = self.output_dir / f"mermaid_{resource['hash']}.png"
        
        # 针对复杂图表（如包含大量节点/文字）
        diagram_script = resource['content']
        base_width = 1000  # 基础宽度
        high_scale = 2.5   # 更高的缩放因子
        
        mermaid = Mermaid(
            graph=diagram_script,
            width=base_width,
            scale=high_scale
        )
        
        mermaid.to_png(output_file)
        resource['output'] = output_file
    
    def _render_vega(self, resource: Dict) -> None:
        """Render Vega/Vega-Lite diagram to PNG with higher resolution"""
        output_file = self.output_dir / f"vega_{resource['hash']}.png"
        spec = json.loads(resource['content'])
        
        if spec.get('$schema', '').startswith('https://vega.github.io/schema/vega-lite/'):
            chart = alt.Chart.from_dict(spec)
        else:
            chart = alt.Chart.from_dict({
                "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                "layer": [spec]
            })
        
        # 同时调整 scale_factor 和 dpi（示例：scale=3.0，dpi=300）
        chart.save(
            str(output_file), 
            scale_factor=3.0,  # 原图缩放倍数，提高后图片更大更清晰
            dpi=300            # 直接设置分辨率（优先于 scale_factor）
        )
        resource['output'] = output_file


class ASTTransformer:
    """Transforms Pandoc AST with diagrams and formatting"""
    
    def __init__(self, resources: List[Dict]):
        self.resources = {res['position']: res for res in resources}
    
    def transform(self, ast: Dict) -> Dict:
        """Transform AST by replacing diagrams and applying formatting"""
        if not isinstance(ast.get('blocks'), list):
            return ast
            
        for i, block in enumerate(ast['blocks']):
            if not isinstance(block, dict):
                continue
                
            pos = f"block_{i}"
            if pos in self.resources:
                self._transform_diagram_block(ast['blocks'], i, pos)
            elif block.get('t') == 'Table':
                self._process_table(block)
                
        return ast
    
    def _transform_diagram_block(self, blocks: List, index: int, position: str) -> None:
        """Replace diagram block with image or error node"""
        resource = self.resources[position]
        blocks[index] = (
            self._create_image_node(resource) if resource.get('output')
            else self._create_error_node(resource)
        )
    
    def _process_table(self, table: Dict) -> None:
        """Process table content for color icons"""
        if not isinstance(table.get('c'), list) or len(table['c']) < 5:
            return
            
        for row in table['c'][4]:
            if not isinstance(row, list):
                continue
                
            for cell in row:
                if not isinstance(cell, dict):
                    continue
                    
                for content in cell.get('c', []):
                    if isinstance(content, dict) and content.get('t') == 'Para':
                        self._process_paragraph(content)
    
    def _process_paragraph(self, para: Dict) -> None:
        """Process paragraph content for color icons"""
        if not isinstance(para.get('c'), list):
            return
            
        para['c'] = [
            self._process_text(element.get('c')) if isinstance(element, dict) and element.get('t') == 'Str'
            else element
            for element in para['c']
        ]
    
    def _process_text(self, text: str) -> List[Dict]:
        """Convert color icons to formatted spans"""
        parts = []
        buffer = ""
        
        for char in text or "":
            if char in COLOR_ICONS:
                if buffer:
                    parts.append({'t': 'Str', 'c': buffer})
                    buffer = ""
                parts.append(self._create_color_span(char))
            else:
                buffer += char
        
        if buffer:
            parts.append({'t': 'Str', 'c': buffer})
            
        return parts[0] if len(parts) == 1 else {'t': 'Span', 'c': parts}
    
    @staticmethod
    def _create_color_span(char: str) -> Dict:
        """Create formatted span for color icon"""
        icon = COLOR_ICONS[char]
        return {
            't': 'Span',
            'c': [
                ['', [], [['color', f"#{icon['color'][0]:02x}{icon['color'][1]:02x}{icon['color'][2]:02x}"]]],
                [{'t': 'Str', 'c': icon['text']}]
            ]
        }
    
    @staticmethod
    def _create_image_node(resource: Dict) -> Dict:
        """Create AST image node"""
        return {
            "t": "Para",
            "c": [{
                "t": "Image",
                "c": [
                    ["", [], []],
                    [{"t": "Str", "c": resource.get('type', 'diagram')}],
                    [str(resource['output']), ""]
                ]
            }]
        }
    
    @staticmethod
    def _create_error_node(resource: Dict) -> Dict:
        """Create AST error node"""
        return {
            "t": "Div",
            "c": [
                ["", ["error"], []],
                [
                    {"t": "Para", "c": [
                        {"t": "Strong", "c": [{"t": "Str", "c": "Diagram failed"}]},
                        {"t": "Space"},
                        {"t": "Str", "c": f"({resource.get('type', 'unknown')})"}
                    ]},
                    {"t": "CodeBlock", "c": [["", ["raw"], []], resource.get('content', '')]}
                ]
            ]
        }


class DocxFormatter:
    """Handles Word document formatting"""
    
    @staticmethod
    def format(doc_path: Path, keep_bookmarks: bool) -> None:
        """Apply formatting to Word document"""
        if not DOCX_AVAILABLE or not doc_path.exists():
            return
            
        try:
            doc = Document(doc_path)
            
            # 确保表格有完整边框
            for table in doc.tables:
                DocxFormatter._format_table(table)
            
            # 强制移除所有书签
            DocxFormatter._remove_bookmarks(doc)
            
            doc.save(doc_path)
        except Exception as e:
            print(f"Document formatting failed: {str(e)}")
    
    @staticmethod
    def _format_table(table) -> None:
        """Apply complete grid formatting to table with emphasis on left border"""
        # 首先确保表格本身有边框
        tbl_pr = table._tbl.tblPr
        tbl_borders = tbl_pr.xpath('./w:tblBorders')
        
        if not tbl_borders:
            tbl_borders = OxmlElement('w:tblBorders')
            tbl_pr.append(tbl_borders)
        else:
            tbl_borders = tbl_borders[0]
        
        # 定义所有需要的边框类型
        border_sides = ['top', 'bottom', 'left', 'right', 'insideH', 'insideV']
        
        # 为表格添加边框
        for side in border_sides:
            border = OxmlElement(f'w:{side}')
            border.set(qn('w:val'), 'single')
            border.set(qn('w:sz'), '4')
            border.set(qn('w:color'), 'auto')
            
            # 确保不重复添加边框
            existing_border = tbl_borders.find(f'w:{side}', namespaces=tbl_borders.nsmap)
            if existing_border is not None:
                tbl_borders.remove(existing_border)
                
            tbl_borders.append(border)
        
        # 确保每个单元格都有边框（特别是左侧边框）
        for row in table.rows:
            for cell in row.cells:
                tc_pr = cell._element.get_or_add_tcPr()
                
                # 确保单元格有边框元素
                tc_borders = tc_pr.xpath('./w:tcBorders')
                if not tc_borders:
                    tc_borders = OxmlElement('w:tcBorders')
                    tc_pr.append(tc_borders)
                else:
                    tc_borders = tc_borders[0]
                
                # 为单元格添加所有边框（重点处理左侧边框）
                for side in border_sides:
                    border = OxmlElement(f'w:{side}')
                    border.set(qn('w:val'), 'single')
                    border.set(qn('w:sz'), '4')
                    border.set(qn('w:color'), 'auto')
                    
                    # 确保不重复添加边框
                    existing_border = tc_borders.find(f'w:{side}', namespaces=tc_borders.nsmap)
                    if existing_border is not None:
                        tc_borders.remove(existing_border)
                        
                    tc_borders.append(border)
    
    @staticmethod
    def _remove_bookmarks(doc) -> None:
        """Remove all bookmarks from document"""
        for element in doc.element.body.iter():
            if element.tag.endswith('}bookmarkStart') or element.tag.endswith('}bookmarkEnd'):
                element.getparent().remove(element)


class MarkdownConverter:
    """Main conversion processor"""
    
    def __init__(self, args):
        self.input_path = Path(args.input)
        self.output_path = Path(args.output) if args.output else self.input_path.with_suffix('.docx')
        self.keep_bookmarks = False  # 参数保留但实际不使用
        self.working_dir = Path(tempfile.mkdtemp())
        self.resources = []
    
    def convert(self) -> bool:
        """Run the full conversion process"""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                ast = json.loads(pypandoc.convert_text(
                    f.read(),
                    to='json',
                    format='markdown',
                    extra_args=['--wrap=none']
                ))
            
            self._find_diagrams(ast)
            DiagramRenderer(self.working_dir).render(self.resources)
            ast = ASTTransformer(self.resources).transform(ast)
            
            self._generate_docx(ast)
            return True
        except Exception as e:
            print(f"Conversion failed: {str(e)}")
            return False
        finally:
            shutil.rmtree(self.working_dir, ignore_errors=True)
    
    def _find_diagrams(self, ast: Dict) -> None:
        """Locate diagrams in the AST"""
        for i, block in enumerate(ast.get('blocks', [])):
            if not isinstance(block, dict) or block.get('t') != 'CodeBlock':
                continue
                
            lang = ''
            if len(block['c']) > 0 and isinstance(block['c'][0], list):
                lang_info = block['c'][0]
                if len(lang_info) > 1 and isinstance(lang_info[1], list) and len(lang_info[1]) > 0:
                    lang = lang_info[1][0]

            content = block['c'][1] if len(block['c']) > 1 else ''
            
            if lang in ['mermaid', 'vega', 'vega-lite']:
                self.resources.append({
                    'type': lang,
                    'content': content,
                    'hash': hashlib.md5(content.encode()).hexdigest()[:8],
                    'position': f"block_{i}"
                })
    
    def _generate_docx(self, ast: Dict) -> None:
        """Generate final Word document"""
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        
        args = ['--standalone', f'--resource-path={self.working_dir}']
        
        pypandoc.convert_text(
            json.dumps(ast),
            to='docx',
            format='json',
            outputfile=str(self.output_path),
            extra_args=args
        )
        
        # 强制传递False确保书签被移除
        DocxFormatter.format(self.output_path, keep_bookmarks=False)


def parse_arguments():
    """Configure and parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Convert Markdown files to Word documents with diagram support',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input Markdown file path'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output Word file path (default: same as input with .docx extension)'
    )
    
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    converter = MarkdownConverter(args)
    
    if not converter.convert():
        sys.exit(1)
    
    if not DOCX_AVAILABLE:
        print("Note: Install python-docx for advanced formatting features")


if __name__ == "__main__":
    main()
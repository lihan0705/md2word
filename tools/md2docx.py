from typing import Dict, List, Optional, Any, Type
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field
import os
import sys
import json
import hashlib
import tempfile
import shutil
from pathlib import Path
import pypandoc
import altair as alt
from mermaid import Mermaid

# Try to import python-docx, set flag if not available
try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Define input model
class MarkdownToWordInput(BaseModel):
    """Input parameter model for Markdown to Word conversion"""
    input_path: str = Field(
        description="Path to the input Markdown file"
    )
    output_path: Optional[str] = Field(
        default=None,
        description="Path to the output Word file. If not provided, will use the same name as the input file but with .docx extension"
    )
    keep_bookmarks: bool = Field(
        default=False,
        description="Whether to keep bookmarks in the document (default is False, removing all bookmarks)"
    )

# Define tool class
class MarkdownToWordTool(BaseTool):
    """Tool for converting Markdown files to Word documents, supporting Mermaid and Vega/Vega-Lite diagram rendering"""
    name: str = "md2docx"
    description: str = """Converts Markdown files to Microsoft Word (.docx) documents, with special support for rendering embedded diagrams (Mermaid, Vega, Vega-Lite)
    and converting specific Unicode color icons (such as 🟢, 🟡, 🔴, ⚪) to colored text. The tool also applies table formatting and bookmark management.
    
    Input parameters:
    - input_path: Path to the input Markdown file (required)
    - output_path: Path to the output Word file (optional, defaults to the same name as the input file but with .docx extension)
    - keep_bookmarks: Whether to keep bookmarks in the document (default is False, removing all bookmarks)
    
    Example:
    ```python
    result = md2docx.run({"input_path": "example.md", "output_path": "output.docx"})
    ```
    """
    args_schema: Type[BaseModel] = MarkdownToWordInput
    
    # Color icon mapping
    COLOR_ICONS: Dict[str, Dict[str, Any]] = {
        "🟢": {"text": "●", "color": (0, 128, 0)},
        "🟡": {"text": "●", "color": (255, 192, 0)},
        "🔴": {"text": "●", "color": (255, 0, 0)},
        "⚪": {"text": "●", "color": (255, 255, 255)}
    }
    
    def _run(
        self, 
        input_path: str, 
        output_path: Optional[str] = None, 
        keep_bookmarks: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute Markdown to Word conversion"""
        try:
            # Create converter instance
            converter = self.MarkdownConverter(input_path, output_path, keep_bookmarks)
            
            # Execute conversion
            success = converter.convert()
            
            if success:
                return f"Conversion successful! Output file saved at: {converter.output_path}"
            else:
                return "Conversion failed, please check error messages."
        except Exception as e:
            return f"Error during conversion process: {str(e)}"
    
    class DiagramRenderer:
        """Handles rendering diagrams to image files"""
        
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
                    print(f"Unable to render {resource['type']} diagram: {str(e)}")
                    resource['error'] = True
        
        def _render_mermaid(self, resource: Dict) -> None:
            """High-resolution rendering for complex diagrams"""
            output_file = self.output_dir / f"mermaid_{resource['hash']}.png"
            
            # For complex diagrams (e.g., with many nodes/text)
            diagram_script = resource['content']
            base_width = 1000  # Base width
            high_scale = 2.5   # Higher scale factor
            
            mermaid = Mermaid(
                graph=diagram_script,
                width=base_width,
                scale=high_scale
            )
            
            mermaid.to_png(output_file)
            resource['output'] = output_file
        
        def _render_vega(self, resource: Dict) -> None:
            """Render Vega/Vega-Lite charts to high-resolution PNG"""
            output_file = self.output_dir / f"vega_{resource['hash']}.png"
            spec = json.loads(resource['content'])
            
            if spec.get('$schema', '').startswith('https://vega.github.io/schema/vega-lite/'):
                chart = alt.Chart.from_dict(spec)
            else:
                chart = alt.Chart.from_dict({
                    "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
                    "layer": [spec]
                })
            
            # Adjust both scale_factor and dpi (example: scale=3.0, dpi=300)
            chart.save(
                str(output_file), 
                scale_factor=3.0,  # Original image scaling factor, higher for clearer images
                dpi=300            # Direct resolution setting (takes precedence over scale_factor)
            )
            resource['output'] = output_file

    class ASTTransformer:
        """Transform Pandoc AST, replace diagrams and apply formatting"""
        
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
            """Process color icons in table content"""
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
            """Process color icons in paragraph content"""
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
                if char in MarkdownToWordTool.COLOR_ICONS:
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
            icon = MarkdownToWordTool.COLOR_ICONS[char]
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
                        [{"t": "Str", 'c': resource.get('type', 'diagram')}],
                        [str(resource['output']), ""]
                    ]
                }]
            }
        
        @staticmethod
        def _create_error_node(resource: Dict) -> Dict:
            """Create AST error node for failed diagram rendering.
            
            Args:
                resource: Dictionary containing error details with keys:
                    - type: Diagram type (e.g., 'plantuml', 'mermaid')
                    - content: Original diagram content
                    
            Returns:
                AST node structure in Pandoc format
            """
            return {
                "t": "Div",
                "c": [
                    ["", ["error"], []],
                    [
                        {"t": "Para", "c": [
                            {"t": "Strong", "c": [{"t": "Str", "c": "Diagram Rendering Failed"}]},
                            {"t": "Space"},
                            {"t": "Str", "c": f"({resource.get('type', 'unknown')})"}
                        ]},
                        {"t": "CodeBlock", "c": [["", ["raw"], []], resource.get('content', '')]}
                    ]
                ]
            }

    class DocxFormatter:
        """Handle Word document formatting"""
        
        @staticmethod
        def format(doc_path: Path, keep_bookmarks: bool) -> None:
            """Apply formatting to Word document"""
            if not DOCX_AVAILABLE or not doc_path.exists():
                return
                
            try:
                doc = Document(doc_path)
                
                # Ensure tables have complete borders
                for table in doc.tables:
                    MarkdownToWordTool.DocxFormatter._format_table(table)
                
                # Remove bookmarks based on parameter
                if not keep_bookmarks:
                    MarkdownToWordTool.DocxFormatter._remove_bookmarks(doc)
                
                doc.save(doc_path)
            except Exception as e:
                print(f"Document formatting failed: {str(e)}")
        
        @staticmethod
        def _format_table(table) -> None:
            """Apply complete grid formatting to table, emphasizing left borders"""
            # First ensure the table itself has borders
            tbl_pr = table._tbl.tblPr
            tbl_borders = tbl_pr.xpath('./w:tblBorders')
            
            if not tbl_borders:
                tbl_borders = OxmlElement('w:tblBorders')
                tbl_pr.append(tbl_borders)
            else:
                tbl_borders = tbl_borders[0]
            
            # Define all needed border types
            border_sides = ['top', 'bottom', 'left', 'right', 'insideH', 'insideV']
            
            # Add borders to table
            for side in border_sides:
                border = OxmlElement(f'w:{side}')
                border.set(qn('w:val'), 'single')
                border.set(qn('w:sz'), '4')
                border.set(qn('w:color'), 'auto')
                
                # Ensure no duplicate borders
                existing_border = tbl_borders.find(f'w:{side}', namespaces=tbl_borders.nsmap)
                if existing_border is not None:
                    tbl_borders.remove(existing_border)
                    
                tbl_borders.append(border)
            
            # Ensure each cell has borders (especially left border)
            for row in table.rows:
                for cell in row.cells:
                    tc_pr = cell._element.get_or_add_tcPr()
                    
                    # Ensure cell has border element
                    tc_borders = tc_pr.xpath('./w:tcBorders')
                    if not tc_borders:
                        tc_borders = OxmlElement('w:tcBorders')
                        tc_pr.append(tc_borders)
                    else:
                        tc_borders = tc_borders[0]
                    
                    # Add all borders to cell (with emphasis on left border)
                    for side in border_sides:
                        border = OxmlElement(f'w:{side}')
                        border.set(qn('w:val'), 'single')
                        border.set(qn('w:sz'), '4')
                        border.set(qn('w:color'), 'auto')
                        
                        # Ensure no duplicate borders
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
        
        def __init__(self, input_path: str, output_path: Optional[str] = None, keep_bookmarks: bool = False):
            self.input_path = Path(input_path)
            self.output_path = Path(output_path) if output_path else self.input_path.with_suffix('.docx')
            self.keep_bookmarks = keep_bookmarks
            self.working_dir = Path(tempfile.mkdtemp())
            self.resources = []
        
        def convert(self) -> bool:
            """Run the complete conversion process"""
            try:
                with open(self.input_path, 'r', encoding='utf-8') as f:
                    ast = json.loads(pypandoc.convert_text(
                        f.read(),
                        to='json',
                        format='markdown',
                        extra_args=['--wrap=none']
                    ))
                
                self._find_diagrams(ast)
                MarkdownToWordTool.DiagramRenderer(self.working_dir).render(self.resources)
                ast = MarkdownToWordTool.ASTTransformer(self.resources).transform(ast)
                
                self._generate_docx(ast)
                return True
            except Exception as e:
                print(f"Conversion failed: {str(e)}")
                return False
            finally:
                shutil.rmtree(self.working_dir, ignore_errors=True)
        
        def _find_diagrams(self, ast: Dict) -> None:
            """Locate diagrams in AST"""
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
            
            # Apply document formatting
            MarkdownToWordTool.DocxFormatter.format(self.output_path, self.keep_bookmarks)

# Usage example
def get_markdown_to_word_tool() -> MarkdownToWordTool:
    """Get an instance of the Markdown to Word conversion tool"""
    return MarkdownToWordTool()
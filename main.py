"""
Modern PDF Splitter Application
A robust, user-friendly PDF splitting tool with job history tracking
Following HCI principles for optimal user experience
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    PdfReader = PdfWriter = None


class ModernButton(Button):
    """Custom button with modern styling following HCI principles"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0.2, 0.6, 0.86, 1)  # Modern blue
        self.color = (1, 1, 1, 1)
        self.font_size = dp(14)
        self.size_hint_y = None
        self.height = dp(45)
        self.bold = True
        
        # Add rounded corners and hover effect
        with self.canvas.before:
            Color(0.2, 0.6, 0.86, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ModernLabel(Label):
    """Custom label with modern styling"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.2, 0.2, 0.2, 1)
        self.font_size = dp(14)
        self.size_hint_y = None
        self.height = dp(30)


class InfoCard(BoxLayout):
    """Card widget for displaying information with modern styling"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(120)
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        
        self.bind(pos=self._update_rect, size=self._update_rect)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


class JobHistoryItem(InfoCard):
    """Widget for displaying a job history entry"""
    
    def __init__(self, job_data: Dict, **kwargs):
        super().__init__(**kwargs)
        
        # Timestamp
        time_label = Label(
            text=f"[b]Date:[/b] {job_data['timestamp']}",
            markup=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1)
        )
        time_label.bind(size=time_label.setter('text_size'))
        
        # Source file
        source_label = Label(
            text=f"[b]Source:[/b] {Path(job_data['source_file']).name}",
            markup=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1)
        )
        source_label.bind(size=source_label.setter('text_size'))
        
        # Split method
        method_label = Label(
            text=f"[b]Method:[/b] {job_data['split_method']} | [b]Pages:[/b] {job_data['pages_info']}",
            markup=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            color=(0.2, 0.2, 0.2, 1)
        )
        method_label.bind(size=method_label.setter('text_size'))
        
        # Output info
        output_label = Label(
            text=f"[b]Output:[/b] {job_data['output_count']} file(s) created",
            markup=True,
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            color=(0.3, 0.6, 0.3, 1)
        )
        output_label.bind(size=output_label.setter('text_size'))
        
        self.add_widget(time_label)
        self.add_widget(source_label)
        self.add_widget(method_label)
        self.add_widget(output_label)


class PDFSplitterApp(App):
    """Main application class"""
    
    selected_file = StringProperty('')
    pdf_pages = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history_file = Path.home() / '.pdf_splitter_history.json'
        self.job_history: List[Dict] = []
        self.load_history()
    
    def build(self):
        """Build the main UI"""
        Window.clearcolor = (0.98, 0.98, 0.98, 1)
        Window.minimum_width = 900
        Window.minimum_height = 600
        
        # Main container
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Title bar
        title_bar = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        with title_bar.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.title_rect = RoundedRectangle(pos=title_bar.pos, size=title_bar.size, radius=[dp(10)])
        title_bar.bind(pos=self._update_title_rect, size=self._update_title_rect)
        
        title_label = Label(
            text='[b]PDF Splitter Pro[/b]',
            markup=True,
            font_size=dp(24),
            color=(1, 1, 1, 1)
        )
        title_bar.add_widget(title_label)
        main_layout.add_widget(title_bar)
        
        # Tabbed interface
        tab_panel = TabbedPanel(do_default_tab=False)
        tab_panel.background_color = (1, 1, 1, 0)
        tab_panel.tab_height = dp(50)
        
        # Main splitter tab
        splitter_tab = TabbedPanelItem(text='PDF Splitter')
        splitter_tab.add_widget(self.create_splitter_interface())
        tab_panel.add_widget(splitter_tab)
        
        # History tab
        history_tab = TabbedPanelItem(text='Job History')
        self.history_content = self.create_history_interface()
        history_tab.add_widget(self.history_content)
        tab_panel.add_widget(history_tab)
        
        main_layout.add_widget(tab_panel)
        
        return main_layout
    
    def _update_title_rect(self, instance, value):
        self.title_rect.pos = instance.pos
        self.title_rect.size = instance.size
    
    def create_splitter_interface(self):
        """Create the main PDF splitter interface"""
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # File selection section
        file_section = InfoCard()
        file_section.height = dp(140)
        
        file_label = ModernLabel(
            text='[b]Step 1: Select PDF File[/b]',
            markup=True,
            halign='left'
        )
        file_label.bind(size=file_label.setter('text_size'))
        file_section.add_widget(file_label)
        
        file_btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        select_file_btn = ModernButton(text='Browse Files')
        select_file_btn.bind(on_press=self.show_file_chooser)
        file_btn_layout.add_widget(select_file_btn)
        file_section.add_widget(file_btn_layout)
        
        self.file_info_label = Label(
            text='No file selected',
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.file_info_label.bind(size=self.file_info_label.setter('text_size'))
        file_section.add_widget(self.file_info_label)
        
        layout.add_widget(file_section)
        
        # Split method section
        method_section = InfoCard()
        method_section.height = dp(200)
        
        method_label = ModernLabel(
            text='[b]Step 2: Choose Split Method[/b]',
            markup=True,
            halign='left'
        )
        method_label.bind(size=method_label.setter('text_size'))
        method_section.add_widget(method_label)
        
        self.split_method = Spinner(
            text='Select Method',
            values=('Extract Page Range', 'Split by Page Numbers', 'Split into Equal Parts', 'Extract Single Pages'),
            size_hint_y=None,
            height=dp(45),
            background_normal='',
            background_color=(0.9, 0.9, 0.9, 1),
            color=(0.2, 0.2, 0.2, 1)
        )
        self.split_method.bind(text=self.on_method_change)
        method_section.add_widget(self.split_method)
        
        self.input_container = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(90))
        method_section.add_widget(self.input_container)
        
        layout.add_widget(method_section)
        
        # Output section
        output_section = InfoCard()
        output_section.height = dp(140)
        
        output_label = ModernLabel(
            text='[b]Step 3: Choose Output Location[/b]',
            markup=True,
            halign='left'
        )
        output_label.bind(size=output_label.setter('text_size'))
        output_section.add_widget(output_label)
        
        output_btn_layout = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        select_output_btn = ModernButton(text='Select Output Folder')
        select_output_btn.bind(on_press=self.show_output_chooser)
        output_btn_layout.add_widget(select_output_btn)
        output_section.add_widget(output_btn_layout)
        
        self.output_info_label = Label(
            text='Output: Same as source file',
            size_hint_y=None,
            height=dp(25),
            halign='left',
            valign='middle',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.output_info_label.bind(size=self.output_info_label.setter('text_size'))
        output_section.add_widget(self.output_info_label)
        
        layout.add_widget(output_section)
        
        # Execute button
        execute_btn = ModernButton(text='Split PDF', height=dp(55))
        execute_btn.background_color = (0.2, 0.7, 0.3, 1)
        execute_btn.bind(on_press=self.execute_split)
        layout.add_widget(execute_btn)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, size_hint_y=None, height=dp(8))
        layout.add_widget(self.progress_bar)
        
        # Status label
        self.status_label = Label(
            text='Ready',
            size_hint_y=None,
            height=dp(30),
            color=(0.3, 0.3, 0.3, 1)
        )
        layout.add_widget(self.status_label)
        
        layout.add_widget(BoxLayout())  # Spacer
        
        self.output_path = None
        return layout
    
    def create_history_interface(self):
        """Create the job history interface"""
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # Header with clear button
        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        header_label = ModernLabel(
            text='[b]Job History[/b]',
            markup=True,
            halign='left',
            font_size=dp(18)
        )
        header_label.bind(size=header_label.setter('text_size'))
        header.add_widget(header_label)
        
        clear_btn = ModernButton(text='Clear History', size_hint_x=0.3)
        clear_btn.background_color = (0.8, 0.3, 0.3, 1)
        clear_btn.bind(on_press=self.clear_history)
        header.add_widget(clear_btn)
        layout.add_widget(header)
        
        # Scrollable history list
        scroll = ScrollView()
        self.history_list = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None)
        self.history_list.bind(minimum_height=self.history_list.setter('height'))
        scroll.add_widget(self.history_list)
        layout.add_widget(scroll)
        
        self.update_history_display()
        return layout
    
    def on_method_change(self, spinner, text):
        """Handle split method change"""
        self.input_container.clear_widgets()
        
        if text == 'Extract Page Range':
            label = Label(
                text='Enter page range (e.g., 1-5 or 3,5,7-10):',
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                color=(0.3, 0.3, 0.3, 1)
            )
            label.bind(size=label.setter('text_size'))
            self.input_container.add_widget(label)
            
            self.range_input = TextInput(
                hint_text='e.g., 1-5, 8, 10-12',
                multiline=False,
                size_hint_y=None,
                height=dp(40),
                background_color=(1, 1, 1, 1),
                foreground_color=(0.2, 0.2, 0.2, 1),
                cursor_color=(0.2, 0.6, 0.86, 1)
            )
            self.input_container.add_widget(self.range_input)
        
        elif text == 'Split by Page Numbers':
            label = Label(
                text='Enter page numbers to split at (e.g., 3,6,9):',
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                color=(0.3, 0.3, 0.3, 1)
            )
            label.bind(size=label.setter('text_size'))
            self.input_container.add_widget(label)
            
            self.range_input = TextInput(
                hint_text='e.g., 3, 6, 9',
                multiline=False,
                size_hint_y=None,
                height=dp(40),
                background_color=(1, 1, 1, 1),
                foreground_color=(0.2, 0.2, 0.2, 1)
            )
            self.input_container.add_widget(self.range_input)
        
        elif text == 'Split into Equal Parts':
            label = Label(
                text='Number of parts:',
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                color=(0.3, 0.3, 0.3, 1)
            )
            label.bind(size=label.setter('text_size'))
            self.input_container.add_widget(label)
            
            self.range_input = TextInput(
                hint_text='e.g., 3',
                multiline=False,
                size_hint_y=None,
                height=dp(40),
                input_filter='int',
                background_color=(1, 1, 1, 1),
                foreground_color=(0.2, 0.2, 0.2, 1)
            )
            self.input_container.add_widget(self.range_input)
        
        elif text == 'Extract Single Pages':
            label = Label(
                text='Enter page numbers to extract (e.g., 1,3,5):',
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                color=(0.3, 0.3, 0.3, 1)
            )
            label.bind(size=label.setter('text_size'))
            self.input_container.add_widget(label)
            
            self.range_input = TextInput(
                hint_text='e.g., 1, 3, 5',
                multiline=False,
                size_hint_y=None,
                height=dp(40),
                background_color=(1, 1, 1, 1),
                foreground_color=(0.2, 0.2, 0.2, 1)
            )
            self.input_container.add_widget(self.range_input)
    
    def show_file_chooser(self, instance):
        """Show file chooser dialog"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        file_chooser = FileChooserListView(
            filters=['*.pdf', '*.PDF'],
            path=str(Path.home())
        )
        content.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        select_btn = ModernButton(text='Select')
        cancel_btn = ModernButton(text='Cancel')
        cancel_btn.background_color = (0.6, 0.6, 0.6, 1)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Select PDF File',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(btn):
            if file_chooser.selection:
                self.load_pdf(file_chooser.selection[0])
                popup.dismiss()
        
        def on_cancel(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        
        popup.open()
    
    def show_output_chooser(self, instance):
        """Show output folder chooser"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
        file_chooser = FileChooserListView(
            dirselect=True,
            path=str(Path.home())
        )
        content.add_widget(file_chooser)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        select_btn = ModernButton(text='Select')
        cancel_btn = ModernButton(text='Cancel')
        cancel_btn.background_color = (0.6, 0.6, 0.6, 1)
        
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Select Output Folder',
            content=content,
            size_hint=(0.9, 0.9)
        )
        
        def on_select(btn):
            if file_chooser.selection:
                self.output_path = file_chooser.selection[0]
                self.output_info_label.text = f'Output: {self.output_path}'
                popup.dismiss()
            elif file_chooser.path:
                self.output_path = file_chooser.path
                self.output_info_label.text = f'Output: {self.output_path}'
                popup.dismiss()
        
        def on_cancel(btn):
            popup.dismiss()
        
        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        
        popup.open()
    
    def load_pdf(self, filepath):
        """Load and validate PDF file"""
        try:
            if PdfReader is None:
                self.show_error("PyPDF2 not installed. Please install it first:\npip install PyPDF2")
                return
            
            self.selected_file = filepath
            reader = PdfReader(filepath)
            self.pdf_pages = len(reader.pages)
            
            filename = Path(filepath).name
            self.file_info_label.text = f'✓ {filename} ({self.pdf_pages} pages)'
            self.file_info_label.color = (0.2, 0.6, 0.2, 1)
            self.status_label.text = f'Ready - PDF loaded: {self.pdf_pages} pages'
            
        except Exception as e:
            self.show_error(f'Error loading PDF:\n{str(e)}')
            self.selected_file = ''
            self.pdf_pages = 0
    
    def execute_split(self, instance):
        """Execute PDF split operation"""
        # Validation
        if not self.selected_file:
            self.show_error('Please select a PDF file first.')
            return
        
        if self.split_method.text == 'Select Method':
            self.show_error('Please select a split method.')
            return
        
        if not hasattr(self, 'range_input'):
            self.show_error('Please configure the split parameters.')
            return
        
        if not self.range_input.text.strip():
            self.show_error('Please enter the required parameters.')
            return
        
        try:
            self.progress_bar.value = 10
            self.status_label.text = 'Processing...'
            
            # Determine output path
            output_dir = self.output_path if self.output_path else str(Path(self.selected_file).parent)
            base_name = Path(self.selected_file).stem
            
            # Execute split based on method
            method = self.split_method.text
            output_files = []
            
            if method == 'Extract Page Range':
                output_files = self.split_by_range(output_dir, base_name)
            elif method == 'Split by Page Numbers':
                output_files = self.split_by_pages(output_dir, base_name)
            elif method == 'Split into Equal Parts':
                output_files = self.split_equal_parts(output_dir, base_name)
            elif method == 'Extract Single Pages':
                output_files = self.extract_single_pages(output_dir, base_name)
            
            self.progress_bar.value = 100
            
            # Add to history
            self.add_to_history({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': self.selected_file,
                'split_method': method,
                'pages_info': self.range_input.text,
                'output_count': len(output_files),
                'output_dir': output_dir
            })
            
            self.show_success(f'Success!\n{len(output_files)} file(s) created in:\n{output_dir}')
            self.status_label.text = f'Completed - {len(output_files)} files created'
            
            # Reset progress bar after 2 seconds
            Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', 0), 2)
            
        except Exception as e:
            self.progress_bar.value = 0
            self.show_error(f'Error during split operation:\n{str(e)}')
            self.status_label.text = 'Error occurred'
    
    def split_by_range(self, output_dir, base_name):
        """Split PDF by page ranges"""
        reader = PdfReader(self.selected_file)
        ranges = self.parse_page_ranges(self.range_input.text)
        output_files = []
        
        for i, (start, end) in enumerate(ranges, 1):
            writer = PdfWriter()
            
            for page_num in range(start - 1, end):
                if 0 <= page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            output_path = os.path.join(output_dir, f'{base_name}_pages_{start}-{end}.pdf')
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            output_files.append(output_path)
        
        return output_files
    
    def split_by_pages(self, output_dir, base_name):
        """Split PDF at specified page numbers"""
        reader = PdfReader(self.selected_file)
        split_points = sorted([int(x.strip()) for x in self.range_input.text.split(',')])
        split_points = [0] + split_points + [len(reader.pages)]
        output_files = []
        
        for i in range(len(split_points) - 1):
            start = split_points[i]
            end = split_points[i + 1]
            
            if start >= end:
                continue
            
            writer = PdfWriter()
            for page_num in range(start, end):
                if 0 <= page_num < len(reader.pages):
                    writer.add_page(reader.pages[page_num])
            
            output_path = os.path.join(output_dir, f'{base_name}_part_{i+1}.pdf')
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            output_files.append(output_path)
        
        return output_files
    
    def split_equal_parts(self, output_dir, base_name):
        """Split PDF into equal parts"""
        reader = PdfReader(self.selected_file)
        num_parts = int(self.range_input.text)
        total_pages = len(reader.pages)
        pages_per_part = total_pages // num_parts
        remainder = total_pages % num_parts
        output_files = []
        
        current_page = 0
        for i in range(num_parts):
            writer = PdfWriter()
            pages_in_this_part = pages_per_part + (1 if i < remainder else 0)
            
            for j in range(pages_in_this_part):
                if current_page < total_pages:
                    writer.add_page(reader.pages[current_page])
                    current_page += 1
            
            output_path = os.path.join(output_dir, f'{base_name}_part_{i+1}_of_{num_parts}.pdf')
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            output_files.append(output_path)
        
        return output_files
    
    def extract_single_pages(self, output_dir, base_name):
        """Extract individual pages as separate PDFs"""
        reader = PdfReader(self.selected_file)
        page_numbers = [int(x.strip()) for x in self.range_input.text.split(',')]
        output_files = []
        
        for page_num in page_numbers:
            if 1 <= page_num <= len(reader.pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num - 1])
                
                output_path = os.path.join(output_dir, f'{base_name}_page_{page_num}.pdf')
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                output_files.append(output_path)
        
        return output_files
    
    def parse_page_ranges(self, range_text):
        """Parse page range text like '1-5, 8, 10-12' into list of tuples"""
        ranges = []
        parts = [p.strip() for p in range_text.split(',')]
        
        for part in parts:
            if '-' in part:
                start, end = part.split('-')
                ranges.append((int(start.strip()), int(end.strip())))
            else:
                page = int(part)
                ranges.append((page, page))
        
        return ranges
    
    def load_history(self):
        """Load job history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.job_history = json.load(f)
        except Exception as e:
            print(f'Error loading history: {e}')
            self.job_history = []
    
    def save_history(self):
        """Save job history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.job_history, f, indent=2)
        except Exception as e:
            print(f'Error saving history: {e}')
    
    def add_to_history(self, job_data):
        """Add job to history"""
        self.job_history.insert(0, job_data)  # Most recent first
        
        # Keep only last 100 entries
        self.job_history = self.job_history[:100]
        
        self.save_history()
        self.update_history_display()
    
    def update_history_display(self):
        """Update the history display"""
        self.history_list.clear_widgets()
        
        if not self.job_history:
            no_history_label = Label(
                text='No job history yet.\nSplit some PDFs to see them here!',
                halign='center',
                valign='middle',
                color=(0.5, 0.5, 0.5, 1)
            )
            self.history_list.add_widget(no_history_label)
        else:
            for job in self.job_history:
                item = JobHistoryItem(job)
                self.history_list.add_widget(item)
    
    def clear_history(self, instance):
        """Clear job history with confirmation"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        
        message = Label(
            text='Are you sure you want to clear all job history?\nThis action cannot be undone.',
            halign='center',
            valign='middle'
        )
        content.add_widget(message)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        yes_btn = ModernButton(text='Yes, Clear All')
        yes_btn.background_color = (0.8, 0.3, 0.3, 1)
        no_btn = ModernButton(text='Cancel')
        no_btn.background_color = (0.6, 0.6, 0.6, 1)
        
        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title='Confirm Clear History',
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        def on_yes(btn):
            self.job_history = []
            self.save_history()
            self.update_history_display()
            popup.dismiss()
            self.show_success('History cleared successfully!')
        
        def on_no(btn):
            popup.dismiss()
        
        yes_btn.bind(on_press=on_yes)
        no_btn.bind(on_press=on_no)
        
        popup.open()
    
    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        
        error_label = Label(
            text=message,
            halign='center',
            valign='middle',
            color=(0.8, 0.2, 0.2, 1)
        )
        content.add_widget(error_label)
        
        close_btn = ModernButton(text='Close', size_hint_y=None, height=dp(50))
        close_btn.background_color = (0.6, 0.6, 0.6, 1)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_success(self, message):
        """Show success popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))
        
        success_label = Label(
            text=message,
            halign='center',
            valign='middle',
            color=(0.2, 0.6, 0.2, 1)
        )
        content.add_widget(success_label)
        
        close_btn = ModernButton(text='OK', size_hint_y=None, height=dp(50))
        close_btn.background_color = (0.2, 0.7, 0.3, 1)
        content.add_widget(close_btn)
        
        popup = Popup(
            title='Success',
            content=content,
            size_hint=(0.6, 0.4)
        )
        
        close_btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    PDFSplitterApp().run()

#!/usr/bin/env python3
"""
Modern PDF Splitter - A Kivy-based PDF splitting application
Features:
- Split PDFs by page ranges
- Job history tracking
- Modern UI with HCI principles
- Progress tracking
- File validation
"""

import os
import sys
import json
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import PyPDF2
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.checkbox import Checkbox
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.widget import Widget
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.modalview import ModalView

# Configure window
Window.size = (1000, 700)
Window.minimum_width, Window.minimum_height = 800, 600


class ModernButton(ButtonBehavior, Widget):
    """Custom modern button with rounded corners and hover effects"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.update_graphics, pos=self.update_graphics)
        self.bind(state=self.update_graphics)
        self.color_normal = (0.2, 0.6, 0.9, 1)
        self.color_pressed = (0.1, 0.4, 0.7, 1)
        self.color_hover = (0.3, 0.7, 1.0, 1)
        self.current_color = self.color_normal
        
    def update_graphics(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.state == 'down':
                Color(*self.color_pressed)
            else:
                Color(*self.current_color)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(8)])


class JobHistoryItem(BoxLayout):
    """Individual job history item widget"""
    
    def __init__(self, job_data: Dict, on_delete_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.job_data = job_data
        self.on_delete_callback = on_delete_callback
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.spacing = dp(10)
        self.padding = [dp(10), dp(5)]
        
        self.create_widgets()
        
    def create_widgets(self):
        # Job info
        info_layout = BoxLayout(orientation='vertical', size_hint_x=0.7)
        
        # File name
        file_label = Label(
            text=f"File: {os.path.basename(self.job_data.get('input_file', 'Unknown'))}",
            text_size=(None, None),
            halign='left',
            valign='middle',
            size_hint_y=0.5,
            color=(0.2, 0.2, 0.2, 1)
        )
        
        # Timestamp and pages
        details_label = Label(
            text=f"Pages: {self.job_data.get('pages', 'N/A')} | {self.job_data.get('timestamp', 'Unknown time')}",
            text_size=(None, None),
            halign='left',
            valign='middle',
            size_hint_y=0.5,
            color=(0.5, 0.5, 0.5, 1),
            font_size=dp(12)
        )
        
        info_layout.add_widget(file_label)
        info_layout.add_widget(details_label)
        
        # Action buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_x=0.3, spacing=dp(5))
        
        view_btn = Button(
            text="View",
            size_hint_x=0.5,
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        view_btn.bind(on_press=self.view_job)
        
        delete_btn = Button(
            text="Delete",
            size_hint_x=0.5,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        delete_btn.bind(on_press=self.delete_job)
        
        button_layout.add_widget(view_btn)
        button_layout.add_widget(delete_btn)
        
        self.add_widget(info_layout)
        self.add_widget(button_layout)
        
    def view_job(self, instance):
        """Show job details in a popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        details = [
            f"Input File: {self.job_data.get('input_file', 'Unknown')}",
            f"Output Directory: {self.job_data.get('output_dir', 'Unknown')}",
            f"Pages: {self.job_data.get('pages', 'N/A')}",
            f"Timestamp: {self.job_data.get('timestamp', 'Unknown')}",
            f"Status: {self.job_data.get('status', 'Unknown')}"
        ]
        
        for detail in details:
            label = Label(
                text=detail,
                text_size=(None, None),
                halign='left',
                color=(0.2, 0.2, 0.2, 1)
            )
            content.add_widget(label)
        
        close_btn = Button(
            text="Close",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        content.add_widget(close_btn)
        
        popup = Popup(
            title="Job Details",
            content=content,
            size_hint=(0.8, 0.6),
            auto_dismiss=True
        )
        close_btn.bind(on_press=popup.dismiss)
        popup.open()
        
    def delete_job(self, instance):
        """Delete this job from history"""
        if self.on_delete_callback:
            self.on_delete_callback(self.job_data)


class PDFSplitterApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Modern PDF Splitter"
        self.icon = None  # Add icon path if available
        
        # Application state
        self.current_file = None
        self.output_directory = None
        self.job_history = []
        self.history_file = "job_history.json"
        
        # Load job history
        self.load_job_history()
        
    def build(self):
        """Build the main UI"""
        # Main container
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Title
        title = Label(
            text="Modern PDF Splitter",
            size_hint_y=None,
            height=dp(60),
            font_size=dp(28),
            color=(0.2, 0.2, 0.2, 1),
            bold=True
        )
        main_layout.add_widget(title)
        
        # Create tab-like interface
        tab_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(5))
        
        self.split_tab = Button(
            text="Split PDF",
            size_hint_x=0.5,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        self.split_tab.bind(on_press=self.show_split_tab)
        
        self.history_tab = Button(
            text="Job History",
            size_hint_x=0.5,
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        self.history_tab.bind(on_press=self.show_history_tab)
        
        tab_container.add_widget(self.split_tab)
        tab_container.add_widget(self.history_tab)
        main_layout.add_widget(tab_container)
        
        # Content area
        self.content_area = BoxLayout(orientation='vertical', spacing=dp(15))
        main_layout.add_widget(self.content_area)
        
        # Initialize with split tab
        self.show_split_tab()
        
        return main_layout
    
    def show_split_tab(self, instance=None):
        """Show the PDF splitting interface"""
        self.content_area.clear()
        
        # Update tab colors
        self.split_tab.background_color = (0.2, 0.6, 0.9, 1)
        self.history_tab.background_color = (0.7, 0.7, 0.7, 1)
        
        # File selection section
        file_section = self.create_file_section()
        self.content_area.add_widget(file_section)
        
        # Page range section
        page_section = self.create_page_range_section()
        self.content_area.add_widget(page_section)
        
        # Output directory section
        output_section = self.create_output_section()
        self.content_area.add_widget(output_section)
        
        # Action buttons
        action_section = self.create_action_section()
        self.content_area.add_widget(action_section)
        
        # Progress section
        self.progress_section = self.create_progress_section()
        self.content_area.add_widget(self.progress_section)
    
    def show_history_tab(self, instance=None):
        """Show the job history interface"""
        self.content_area.clear()
        
        # Update tab colors
        self.split_tab.background_color = (0.7, 0.7, 0.7, 1)
        self.history_tab.background_color = (0.2, 0.6, 0.9, 1)
        
        # History header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        history_title = Label(
            text="Job History",
            size_hint_x=0.7,
            font_size=dp(20),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        
        clear_btn = Button(
            text="Clear All",
            size_hint_x=0.3,
            background_color=(0.8, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        clear_btn.bind(on_press=self.clear_all_history)
        
        header.add_widget(history_title)
        header.add_widget(clear_btn)
        self.content_area.add_widget(header)
        
        # History list
        if self.job_history:
            scroll = ScrollView()
            history_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
            history_layout.bind(minimum_height=history_layout.setter('height'))
            
            for job in reversed(self.job_history):  # Show newest first
                job_item = JobHistoryItem(job, on_delete_callback=self.delete_job_from_history)
                history_layout.add_widget(job_item)
            
            scroll.add_widget(history_layout)
            self.content_area.add_widget(scroll)
        else:
            no_history = Label(
                text="No job history found.\nSplit some PDFs to see your history here!",
                font_size=dp(16),
                color=(0.5, 0.5, 0.5, 1),
                halign='center'
            )
            self.content_area.add_widget(no_history)
    
    def create_file_section(self):
        """Create file selection section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(10))
        
        # Section title
        title = Label(
            text="1. Select PDF File",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        
        # File selection row
        file_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.file_input = TextInput(
            hint_text="Click 'Browse' to select a PDF file",
            size_hint_x=0.7,
            readonly=True,
            multiline=False
        )
        
        browse_btn = Button(
            text="Browse",
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        browse_btn.bind(on_press=self.browse_file)
        
        file_row.add_widget(self.file_input)
        file_row.add_widget(browse_btn)
        
        section.add_widget(title)
        section.add_widget(file_row)
        
        return section
    
    def create_page_range_section(self):
        """Create page range selection section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120), spacing=dp(10))
        
        # Section title
        title = Label(
            text="2. Define Page Ranges",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        
        # Page range input
        range_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(10))
        
        range_label = Label(
            text="Pages (e.g., 1-5,8,10-15):",
            size_hint_x=0.4,
            halign='left'
        )
        
        self.page_range_input = TextInput(
            hint_text="Enter page ranges separated by commas",
            size_hint_x=0.6,
            multiline=False
        )
        
        range_row.add_widget(range_label)
        range_row.add_widget(self.page_range_input)
        
        # Options row
        options_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40), spacing=dp(20))
        
        self.split_by_pages_check = Checkbox(
            size_hint_x=None,
            width=dp(30),
            active=True
        )
        split_by_pages_label = Label(
            text="Split by page ranges",
            size_hint_x=0.3,
            halign='left'
        )
        
        self.split_each_page_check = Checkbox(
            size_hint_x=None,
            width=dp(30)
        )
        split_each_page_label = Label(
            text="Split each page separately",
            size_hint_x=0.3,
            halign='left'
        )
        
        options_row.add_widget(self.split_by_pages_check)
        options_row.add_widget(split_by_pages_label)
        options_row.add_widget(self.split_each_page_check)
        options_row.add_widget(split_each_page_label)
        
        section.add_widget(title)
        section.add_widget(range_row)
        section.add_widget(options_row)
        
        return section
    
    def create_output_section(self):
        """Create output directory selection section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100), spacing=dp(10))
        
        # Section title
        title = Label(
            text="3. Select Output Directory",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(16),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        
        # Output directory row
        output_row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.output_input = TextInput(
            hint_text="Click 'Browse' to select output directory",
            size_hint_x=0.7,
            readonly=True,
            multiline=False
        )
        
        output_browse_btn = Button(
            text="Browse",
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        output_browse_btn.bind(on_press=self.browse_output_directory)
        
        output_row.add_widget(self.output_input)
        output_row.add_widget(output_browse_btn)
        
        section.add_widget(title)
        section.add_widget(output_row)
        
        return section
    
    def create_action_section(self):
        """Create action buttons section"""
        section = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(20))
        
        # Preview button
        preview_btn = Button(
            text="Preview Split",
            size_hint_x=0.3,
            background_color=(0.2, 0.7, 0.3, 1),
            color=(1, 1, 1, 1)
        )
        preview_btn.bind(on_press=self.preview_split)
        
        # Split button
        split_btn = Button(
            text="Split PDF",
            size_hint_x=0.4,
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1),
            font_size=dp(16)
        )
        split_btn.bind(on_press=self.split_pdf)
        
        # Reset button
        reset_btn = Button(
            text="Reset",
            size_hint_x=0.3,
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        reset_btn.bind(on_press=self.reset_form)
        
        section.add_widget(preview_btn)
        section.add_widget(split_btn)
        section.add_widget(reset_btn)
        
        return section
    
    def create_progress_section(self):
        """Create progress tracking section"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80), spacing=dp(10))
        
        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(20)
        )
        
        # Status label
        self.status_label = Label(
            text="Ready to split PDF",
            size_hint_y=None,
            height=dp(30),
            font_size=dp(14),
            color=(0.2, 0.2, 0.2, 1)
        )
        
        # Initially hidden
        section.opacity = 0
        
        section.add_widget(self.progress_bar)
        section.add_widget(self.status_label)
        
        return section
    
    def browse_file(self, instance):
        """Open file browser for PDF selection"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        file_chooser = FileChooserListView(
            filters=['*.pdf'],
            size_hint_y=0.8
        )
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=dp(10))
        
        select_btn = Button(
            text="Select",
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        select_btn.bind(on_press=lambda x: self.select_file(file_chooser, popup))
        
        cancel_btn = Button(
            text="Cancel",
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(file_chooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title="Select PDF File",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.open()
    
    def select_file(self, file_chooser, popup):
        """Handle file selection"""
        if file_chooser.selection:
            self.current_file = file_chooser.selection[0]
            self.file_input.text = self.current_file
            popup.dismiss()
            
            # Auto-fill output directory
            if not self.output_directory:
                self.output_directory = os.path.dirname(self.current_file)
                self.output_input.text = self.output_directory
    
    def browse_output_directory(self, instance):
        """Open directory browser for output selection"""
        content = BoxLayout(orientation='vertical', spacing=dp(10))
        
        dir_chooser = FileChooserListView(
            dirselect=True,
            size_hint_y=0.8
        )
        
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2, spacing=dp(10))
        
        select_btn = Button(
            text="Select",
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        select_btn.bind(on_press=lambda x: self.select_output_directory(dir_chooser, popup))
        
        cancel_btn = Button(
            text="Cancel",
            background_color=(0.7, 0.7, 0.7, 1),
            color=(1, 1, 1, 1)
        )
        cancel_btn.bind(on_press=popup.dismiss)
        
        button_layout.add_widget(select_btn)
        button_layout.add_widget(cancel_btn)
        
        content.add_widget(dir_chooser)
        content.add_widget(button_layout)
        
        popup = Popup(
            title="Select Output Directory",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        popup.open()
    
    def select_output_directory(self, dir_chooser, popup):
        """Handle output directory selection"""
        if dir_chooser.selection:
            self.output_directory = dir_chooser.selection[0]
            self.output_input.text = self.output_directory
            popup.dismiss()
    
    def preview_split(self, instance):
        """Preview the split operation"""
        if not self.validate_inputs():
            return
        
        try:
            page_ranges = self.parse_page_ranges(self.page_range_input.text)
            total_pages = self.get_pdf_page_count()
            
            preview_text = f"Preview:\n"
            preview_text += f"Input file: {os.path.basename(self.current_file)}\n"
            preview_text += f"Total pages: {total_pages}\n"
            preview_text += f"Will create {len(page_ranges)} output files:\n\n"
            
            for i, page_range in enumerate(page_ranges, 1):
                if isinstance(page_range, tuple):
                    preview_text += f"File {i}: Pages {page_range[0]}-{page_range[1]}\n"
                else:
                    preview_text += f"File {i}: Page {page_range}\n"
            
            # Show preview popup
            content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
            
            preview_label = Label(
                text=preview_text,
                text_size=(None, None),
                halign='left',
                valign='top',
                color=(0.2, 0.2, 0.2, 1)
            )
            
            close_btn = Button(
                text="Close",
                size_hint_y=None,
                height=dp(40),
                background_color=(0.2, 0.6, 0.9, 1),
                color=(1, 1, 1, 1)
            )
            
            content.add_widget(preview_label)
            content.add_widget(close_btn)
            
            popup = Popup(
                title="Split Preview",
                content=content,
                size_hint=(0.7, 0.6),
                auto_dismiss=True
            )
            close_btn.bind(on_press=popup.dismiss)
            popup.open()
            
        except Exception as e:
            self.show_error(f"Preview error: {str(e)}")
    
    def split_pdf(self, instance):
        """Perform the PDF splitting operation"""
        if not self.validate_inputs():
            return
        
        # Start splitting in a separate thread
        thread = threading.Thread(target=self._split_pdf_thread)
        thread.daemon = True
        thread.start()
    
    def _split_pdf_thread(self):
        """PDF splitting thread function"""
        try:
            Clock.schedule_once(lambda dt: self.update_status("Starting PDF split...", 10), 0)
            
            page_ranges = self.parse_page_ranges(self.page_range_input.text)
            total_pages = self.get_pdf_page_count()
            
            # Create job entry
            job_id = len(self.job_history) + 1
            job_data = {
                'id': job_id,
                'input_file': self.current_file,
                'output_dir': self.output_directory,
                'pages': self.page_range_input.text,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'In Progress'
            }
            
            Clock.schedule_once(lambda dt: self.update_status("Opening PDF file...", 20), 0)
            
            with open(self.current_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for i, page_range in enumerate(page_ranges):
                    progress = 20 + (i * 60 // len(page_ranges))
                    Clock.schedule_once(lambda dt, p=progress: self.update_status(f"Processing file {i+1}/{len(page_ranges)}...", p), 0)
                    
                    # Create output filename
                    base_name = os.path.splitext(os.path.basename(self.current_file))[0]
                    if isinstance(page_range, tuple):
                        output_filename = f"{base_name}_pages_{page_range[0]}-{page_range[1]}.pdf"
                    else:
                        output_filename = f"{base_name}_page_{page_range}.pdf"
                    
                    output_path = os.path.join(self.output_directory, output_filename)
                    
                    # Create PDF writer
                    pdf_writer = PyPDF2.PdfWriter()
                    
                    # Add pages to writer
                    if isinstance(page_range, tuple):
                        for page_num in range(page_range[0] - 1, page_range[1]):
                            if page_num < len(pdf_reader.pages):
                                pdf_writer.add_page(pdf_reader.pages[page_num])
                    else:
                        if page_range - 1 < len(pdf_reader.pages):
                            pdf_writer.add_page(pdf_reader.pages[page_range - 1])
                    
                    # Write output file
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
            
            # Update job status
            job_data['status'] = 'Completed'
            self.job_history.append(job_data)
            self.save_job_history()
            
            Clock.schedule_once(lambda dt: self.update_status("PDF split completed successfully!", 100), 0)
            Clock.schedule_once(lambda dt: self.show_success(f"Successfully created {len(page_ranges)} files in {self.output_directory}"), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_status("Error occurred during split", 0), 0)
            Clock.schedule_once(lambda dt: self.show_error(f"Split error: {str(e)}"), 0)
    
    def validate_inputs(self):
        """Validate user inputs"""
        if not self.current_file or not os.path.exists(self.current_file):
            self.show_error("Please select a valid PDF file")
            return False
        
        if not self.output_directory or not os.path.exists(self.output_directory):
            self.show_error("Please select a valid output directory")
            return False
        
        if not self.page_range_input.text.strip():
            self.show_error("Please enter page ranges")
            return False
        
        try:
            self.parse_page_ranges(self.page_range_input.text)
        except Exception as e:
            self.show_error(f"Invalid page range format: {str(e)}")
            return False
        
        return True
    
    def parse_page_ranges(self, page_text):
        """Parse page range text into list of ranges"""
        ranges = []
        parts = page_text.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                start, end = map(int, part.split('-'))
                ranges.append((start, end))
            else:
                ranges.append(int(part))
        
        return ranges
    
    def get_pdf_page_count(self):
        """Get total number of pages in the PDF"""
        with open(self.current_file, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            return len(pdf_reader.pages)
    
    def update_status(self, message, progress):
        """Update status and progress"""
        self.status_label.text = message
        self.progress_bar.value = progress
        self.progress_section.opacity = 1
    
    def show_error(self, message):
        """Show error popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        error_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            color=(0.8, 0.2, 0.2, 1)
        )
        
        ok_btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(error_label)
        content.add_widget(ok_btn)
        
        popup = Popup(
            title="Error",
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=True
        )
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def show_success(self, message):
        """Show success popup"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        success_label = Label(
            text=message,
            text_size=(None, None),
            halign='center',
            color=(0.2, 0.7, 0.3, 1)
        )
        
        ok_btn = Button(
            text="OK",
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 0.9, 1),
            color=(1, 1, 1, 1)
        )
        
        content.add_widget(success_label)
        content.add_widget(ok_btn)
        
        popup = Popup(
            title="Success",
            content=content,
            size_hint=(0.6, 0.4),
            auto_dismiss=True
        )
        ok_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def reset_form(self, instance):
        """Reset the form to initial state"""
        self.current_file = None
        self.output_directory = None
        self.file_input.text = ""
        self.output_input.text = ""
        self.page_range_input.text = ""
        self.split_by_pages_check.active = True
        self.split_each_page_check.active = False
        self.progress_section.opacity = 0
        self.status_label.text = "Ready to split PDF"
        self.progress_bar.value = 0
    
    def load_job_history(self):
        """Load job history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.job_history = json.load(f)
        except Exception as e:
            print(f"Error loading job history: {e}")
            self.job_history = []
    
    def save_job_history(self):
        """Save job history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.job_history, f, indent=2)
        except Exception as e:
            print(f"Error saving job history: {e}")
    
    def delete_job_from_history(self, job_data):
        """Delete a job from history"""
        self.job_history = [job for job in self.job_history if job['id'] != job_data['id']]
        self.save_job_history()
        self.show_history_tab()  # Refresh the history view
    
    def clear_all_history(self, instance):
        """Clear all job history"""
        self.job_history = []
        self.save_job_history()
        self.show_history_tab()  # Refresh the history view


if __name__ == '__main__':
    PDFSplitterApp().run()
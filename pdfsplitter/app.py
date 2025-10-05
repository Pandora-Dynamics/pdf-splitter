from __future__ import annotations

import os
from typing import Optional

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window

from .core.job_manager import JobManager
from .core.models import SplitJobParams, SplitStrategy
from .os_integration import open_in_file_manager, reveal_in_file_manager


KV = r"""
#:import SplitStrategy pdfsplitter.core.models.SplitStrategy

<AppRoot>:
    orientation: 'vertical'
    spacing: dp(8)
    padding: dp(12)

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        Label:
            text: 'Kivy PDF Splitter'
            bold: True
            font_size: '20sp'
        Widget:
        Button:
            text: 'Help'
            size_hint_x: None
            width: dp(80)
            on_release: root.show_help()

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        TextInput:
            id: input_path
            hint_text: 'Select input PDF file...'
            text: root.input_path
            on_text: root.input_path = self.text
        Button:
            text: 'Browse'
            on_release: root.open_file_dialog()

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        TextInput:
            id: output_dir
            hint_text: 'Choose output directory...'
            text: root.output_dir
            on_text: root.output_dir = self.text
        Button:
            text: 'Browse'
            on_release: root.open_dir_dialog()
        Button:
            text: 'Open Folder'
            on_release: root.open_output_folder()

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        Spinner:
            id: strategy
            text: root.strategy_text
            values: ['Ranges', 'Each Page', 'Every N Pages', 'Odd Pages Together', 'Even Pages Together']
            on_text: root.on_strategy_selected(self.text)
        TextInput:
            id: ranges
            hint_text: 'Page ranges e.g. 1-3,5,10- (for Ranges)'
            text: root.ranges_text
            on_text: root.ranges_text = self.text
        TextInput:
            id: n_per
            hint_text: 'Pages per file (for Every N Pages)'
            text: '' if root.pages_per_file <= 0 else str(root.pages_per_file)
            input_filter: 'int'
            on_text: root.pages_per_file = int(self.text) if self.text.isdigit() else 0

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        TextInput:
            id: prefix
            hint_text: 'Output filename prefix'
            text: root.output_prefix
            on_text: root.output_prefix = self.text
        TextInput:
            id: zpad
            hint_text: 'Zero pad digits'
            text: str(root.zero_pad_digits)
            input_filter: 'int'
            on_text: root.zero_pad_digits = int(self.text) if self.text.isdigit() else root.zero_pad_digits
        CheckBox:
            id: keepmeta
            active: root.preserve_metadata
            on_active: root.preserve_metadata = self.active
        Label:
            text: 'Preserve metadata'

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        Button:
            text: 'Split'
            disabled: not root.can_run or root.is_running
            on_release: root.run_split()
        Button:
            text: 'Cancel'
            disabled: not root.is_running
            on_release: root.cancel_split()
        ProgressBar:
            max: 1
            value: root.progress
        Label:
            id: status
            text: root.status_text
            size_hint_x: 2

    BoxLayout:
        orientation: 'vertical'
        size_hint_y: 0.45
        spacing: dp(6)
        BoxLayout:
            size_hint_y: None
            height: dp(28)
            Label:
                text: 'Job History'
                bold: True
            Widget:
            Button:
                text: 'Refresh'
                size_hint_x: None
                width: dp(90)
                on_release: root.refresh_history()
            Button:
                text: 'Clear'
                size_hint_x: None
                width: dp(80)
                on_release: root.confirm_clear_history()
        RecycleView:
            id: history
            viewclass: 'HistoryItem'
            scroll_type: ['bars', 'content']
            bar_width: dp(10)
            RecycleBoxLayout:
                default_size: None, dp(40)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'

<HistoryItem@BoxLayout>:
    job_id: 0
    created_at: ''
    desc: ''
    status: ''
    spacing: dp(6)
    size_hint_y: None
    height: dp(40)
    Label:
        text: root.created_at
        size_hint_x: 0.3
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Label:
        text: root.desc
        size_hint_x: 0.5
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Label:
        text: root.status
        size_hint_x: 0.2
        halign: 'left'
        valign: 'middle'
        text_size: self.size
    Button:
        text: 'Open Out'
        size_hint_x: None
        width: dp(90)
        on_release: app.open_history_output(root.job_id)
    Button:
        text: 'Reveal'
        size_hint_x: None
        width: dp(80)
        on_release: app.reveal_history_output(root.job_id)
    Button:
        text: 'Re-run'
        size_hint_x: None
        width: dp(80)
        on_release: app.rerun_history_job(root.job_id)
"""


class AppRoot(BoxLayout):
    input_path = StringProperty('')
    output_dir = StringProperty('')
    strategy_text = StringProperty('Ranges')
    ranges_text = StringProperty('')
    pages_per_file = NumericProperty(0)
    output_prefix = StringProperty('split')
    zero_pad_digits = NumericProperty(3)
    preserve_metadata = BooleanProperty(True)

    is_running = BooleanProperty(False)
    progress = NumericProperty(0.0)
    status_text = StringProperty('Ready')
    help_text = StringProperty('Tip: Select an input PDF and output folder to begin.')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.job_manager = JobManager()
        Clock.schedule_once(lambda dt: self.refresh_history(), 0.2)

    @property
    def can_run(self) -> bool:
        if not (self.input_path.lower().endswith('.pdf') and os.path.exists(self.input_path) and os.path.isdir(self.output_dir)):
            return False
        strategy = self.get_strategy()
        if strategy.name == 'RANGES':
            return bool(self.ranges_text.strip())
        if strategy.name == 'EVERY_N_PAGES':
            return self.pages_per_file >= 1
        return True

    def on_strategy_selected(self, text: str) -> None:
        self.strategy_text = text

    def get_strategy(self) -> SplitStrategy:
        mapping = {
            'Ranges': SplitStrategy.RANGES,
            'Each Page': SplitStrategy.EACH_PAGE,
            'Every N Pages': SplitStrategy.EVERY_N_PAGES,
            'Odd Pages Together': SplitStrategy.ODD_TOGETHER,
            'Even Pages Together': SplitStrategy.EVEN_TOGETHER,
        }
        return mapping.get(self.strategy_text, SplitStrategy.RANGES)

    def open_file_dialog(self):
        self._open_file_popup(select_dir=False)

    def open_dir_dialog(self):
        self._open_file_popup(select_dir=True)

    def _open_file_popup(self, select_dir: bool = False):
        chooser = FileChooserIconView(filters=['*.pdf'] if not select_dir else None, dirselect=select_dir)
        chooser.path = self.output_dir if select_dir and self.output_dir else os.getcwd()
        popup = Popup(title='Select Directory' if select_dir else 'Select PDF File', content=chooser, size_hint=(0.9, 0.9))
        def on_select(instance, selection):
            if selection:
                path = selection[0]
                if select_dir:
                    self.output_dir = path
                else:
                    self.input_path = path
                    if not self.output_dir:
                        # Default output dir to input file's directory for convenience
                        self.output_dir = os.path.dirname(path)
                popup.dismiss()
        chooser.bind(on_submit=on_select, on_selection=lambda inst, sel: None)
        popup.open()

    def open_output_folder(self):
        if self.output_dir:
            open_in_file_manager(self.output_dir)

    def run_split(self):
        if self.is_running:
            return
        self.is_running = True
        self.progress = 0
        self.status_text = 'Starting...'
        params = SplitJobParams(
            input_path=self.input_path,
            output_dir=self.output_dir,
            strategy=self.get_strategy(),
            ranges_text=self.ranges_text or None,
            pages_per_file=self.pages_per_file or None,
            output_prefix=self.output_prefix or 'split',
            zero_pad_digits=max(1, int(self.zero_pad_digits)),
            preserve_metadata=bool(self.preserve_metadata),
        )
        self._handle = self.job_manager.start_job(
            params,
            on_progress=lambda p, m: Clock.schedule_once(lambda dt: self._on_progress(p, m), 0),
            on_complete=lambda res, err, jid: Clock.schedule_once(lambda dt: self._on_complete(res, err, jid), 0),
        )

    def _on_progress(self, progress: float, message: str):
        self.progress = progress
        self.status_text = message

    def _on_complete(self, result, error, job_id: int):
        self.is_running = False
        if error:
            self.status_text = f"Failed: {error}"
        else:
            self.status_text = f"Done: {len(result.output_files)} files"
        self.refresh_history()

    def cancel_split(self):
        if hasattr(self, '_handle') and self._handle:
            self._handle.cancel()
            self.status_text = 'Cancelling...'

    def refresh_history(self):
        jobs = self.job_manager.history.list_jobs(limit=200)
        items = []
        for j in jobs:
            desc = f"{os.path.basename(j.input_path)} → {os.path.basename(j.output_dir)} [{j.strategy.value}]"
            created = j.created_at.strftime('%Y-%m-%d %H:%M:%S')
            items.append({'job_id': j.id, 'created_at': created, 'desc': desc, 'status': j.status.value})
        self.ids.history.data = items

    def set_help(self, text: str):
        self.help_text = text

    def show_help(self):
        text = (
            "Quick Start:\n\n"
            "1) Select an input PDF and an output folder.\n"
            "2) Choose a split strategy. For Ranges, enter e.g. 1-3,5,10-.\n"
            "3) Set filename prefix and zero padding if desired.\n"
            "4) Click Split (Ctrl+Enter). Cancel with Esc.\n\n"
            "Shortcuts: Ctrl+O File, Ctrl+D Folder, Ctrl+Enter Split, Esc Cancel, Ctrl+H History refresh."
        )
        Popup(title='Help', content=Label(text=text), size_hint=(0.7, 0.7)).open()

    def confirm_clear_history(self):
        box = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        box.add_widget(Label(text='Clear all job history? This cannot be undone.'))
        btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        from kivy.uix.button import Button
        ok = Button(text='Clear')
        cancel = Button(text='Cancel')
        btns.add_widget(cancel)
        btns.add_widget(ok)
        box.add_widget(btns)
        popup = Popup(title='Confirm', content=box, size_hint=(0.5, 0.35))
        def do_clear(instance):
            self.job_manager.history.clear()
            self.refresh_history()
            popup.dismiss()
        ok.bind(on_release=do_clear)
        cancel.bind(on_release=lambda *_: popup.dismiss())
        popup.open()


class KivyPDFSplitter(App):
    title = 'Kivy PDF Splitter'

    def build(self):
        Builder.load_string(KV)
        root = AppRoot()
        # Keyboard shortcuts for HCI and efficiency
        def on_kbd(window, key, scancode, codepoint, modifiers):
            # Ctrl+O: open file
            if 'ctrl' in modifiers and codepoint in ('o', 'O'):
                root.open_file_dialog(); return True
            # Ctrl+D: open dir
            if 'ctrl' in modifiers and codepoint in ('d', 'D'):
                root.open_dir_dialog(); return True
            # Ctrl+Enter: run split
            if 'ctrl' in modifiers and key in (13, 271):
                if root.can_run and not root.is_running:
                    root.run_split()
                return True
            # Esc: cancel
            if key == 27:
                if root.is_running:
                    root.cancel_split()
                return True
            # Ctrl+H: refresh history
            if 'ctrl' in modifiers and codepoint in ('h', 'H'):
                root.refresh_history(); return True
            return False
        Window.bind(on_key_down=on_kbd)
        return root

    def open_history_output(self, job_id: int):
        rec = App.get_running_app().root.job_manager.history.get_job(job_id)
        if rec and rec.output_dir:
            open_in_file_manager(rec.output_dir)

    def reveal_history_output(self, job_id: int):
        rec = App.get_running_app().root.job_manager.history.get_job(job_id)
        if rec and rec.output_dir:
            reveal_in_file_manager(rec.output_dir)

    def rerun_history_job(self, job_id: int):
        app = App.get_running_app()
        rec = app.root.job_manager.history.get_job(job_id)
        if not rec:
            return
        params_dict = rec.params_json
        try:
            strategy = SplitStrategy(params_dict.get('strategy', rec.strategy.value))
        except Exception:
            strategy = rec.strategy
        params = SplitJobParams(
            input_path=params_dict.get('input_path', rec.input_path),
            output_dir=params_dict.get('output_dir', rec.output_dir),
            strategy=strategy,
            ranges_text=params_dict.get('ranges_text'),
            pages_per_file=params_dict.get('pages_per_file'),
            output_prefix=params_dict.get('output_prefix', 'split'),
            zero_pad_digits=int(params_dict.get('zero_pad_digits', 3)),
            preserve_metadata=bool(params_dict.get('preserve_metadata', True)),
        )
        app.root.input_path = params.input_path
        app.root.output_dir = params.output_dir
        app.root.strategy_text = {
            SplitStrategy.RANGES: 'Ranges',
            SplitStrategy.EACH_PAGE: 'Each Page',
            SplitStrategy.EVERY_N_PAGES: 'Every N Pages',
            SplitStrategy.ODD_TOGETHER: 'Odd Pages Together',
            SplitStrategy.EVEN_TOGETHER: 'Even Pages Together',
        }[strategy]
        app.root.ranges_text = params.ranges_text or ''
        app.root.pages_per_file = params.pages_per_file or 0
        app.root.output_prefix = params.output_prefix
        app.root.zero_pad_digits = params.zero_pad_digits
        app.root.preserve_metadata = params.preserve_metadata


def main():
    KivyPDFSplitter().run()


if __name__ == '__main__':
    main()

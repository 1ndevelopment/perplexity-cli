<<<<<<< HEAD
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextBrowser, QPushButton, QPlainTextEdit,
    QLineEdit, QLabel, QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout,
    QDialog, QDialogButtonBox, QMenuBar
)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QFont, QFontMetrics, QColor, QTextCharFormat, QTextBlockFormat, QAction
import sys
import re
import os

from wrapper import PerplexityWrapper


class ScrollingTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        # Use monospace font for consistent code display
        fixed_font = QFont("Courier New")
        fixed_font.setPointSize(11)
        self.setFont(fixed_font)

        # Initialize animation variables
        self._full_text = ""
        self._current_index = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_text)
        self._animation_speed_ms = 10  # Speed of typing animation

    def set_animated_text(self, full_text: str):
        """Start text scrolling animation with specially formatted code boxes"""

        self._timer.stop()
        self.clear()

        # Parse text into chunks: normal, inline code (`...`), and code blocks (```lang\n...```)
        self._animation_chunks = []
        pattern = re.compile(r"```[^\n]*\r?\n[\s\S]*?```|`[^`]*`", re.DOTALL)
        last_end = 0
        for m in pattern.finditer(full_text):
            if m.start() > last_end:
                self._animation_chunks.append(('text', full_text[last_end:m.start()]))
            segment = m.group(0)
            if segment.startswith("```"):
                self._animation_chunks.append(('codeblock', segment))
            else:
                self._animation_chunks.append(('inlinecode', segment))
            last_end = m.end()
        if last_end < len(full_text):
            self._animation_chunks.append(('text', full_text[last_end:]))

        self._current_chunk_index = 0
        self._current_chunk_text = ""
        self._current_char_index = 0
        self._timer.start(self._animation_speed_ms)

    def _update_text(self):
        if self._current_chunk_index >= len(self._animation_chunks):
            self._timer.stop()
            return

        chunk_type, chunk_text = self._animation_chunks[self._current_chunk_index]

        if self._current_char_index < len(chunk_text):
            self._current_char_index += 1
            self._current_chunk_text = chunk_text[:self._current_char_index]
        else:
            self._current_chunk_index += 1
            self._current_char_index = 0
            self._current_chunk_text = ""

        self.clear()
        # Compose the displayed content up to current chunk and partial char
        for i in range(self._current_chunk_index):
            t, txt = self._animation_chunks[i]
            if t == 'text':
                self._append_plain_text(txt)
            elif t == 'inlinecode':
                self._append_inline_code(txt)
            elif t == 'codeblock':
                self._append_code_block(txt)

        # Append current chunk partially
        if self._current_chunk_index < len(self._animation_chunks):
            t, txt = self._animation_chunks[self._current_chunk_index]
            if t == 'text':
                self._append_plain_text(self._current_chunk_text)
            elif t == 'inlinecode':
                # apply styling only when we have both backticks present
                if self._current_chunk_text.startswith('`') and self._current_chunk_text.endswith('`'):
                    self._append_inline_code(self._current_chunk_text)
                else:
                    self._append_plain_text(self._current_chunk_text)
            elif t == 'codeblock':
                # apply styling only when we have complete triple-backtick block
                if self._current_chunk_text.startswith('```') and self._current_chunk_text.endswith('```'):
                    self._append_code_block(self._current_chunk_text)
                else:
                    self._append_plain_text(self._current_chunk_text)

        self.moveCursor(QTextCursor.MoveOperation.End)

    def _append_plain_text(self, text: str):
        self.moveCursor(QTextCursor.MoveOperation.End)
        cursor = self.textCursor()
        cursor.setCharFormat(QTextCharFormat())
        cursor.insertText(text)

    def _append_inline_code(self, text: str):
        self.moveCursor(QTextCursor.MoveOperation.End)
        # Expecting text with surrounding backticks
        cursor = self.textCursor()
        default_fmt = QTextCharFormat()  # default application palette
        if text.startswith('```') and text.endswith('```') and len(text) >= 2:
            inner = text[1:-1]
            # opening backtick (default palette)
            cursor.setCharFormat(default_fmt)
            cursor.insertText('```')
            # styled inner
            code_fmt = QTextCharFormat()
            code_fmt.setForeground(QColor('#00ff00'))
            code_fmt.setBackground(QColor('#000000'))
            cursor.insertText(inner, code_fmt)
            # closing backtick (default palette)
            cursor.setCharFormat(default_fmta)
            cursor.insertText('```')
            # ensure subsequent text uses default palette
            cursor.setCharFormat(default_fmt)
        else:
            cursor.setCharFormat(default_fmt)
            cursor.insertText(text)

    def _append_code_block(self, text: str):
        self.moveCursor(QTextCursor.MoveOperation.End)
        # Expecting full block with ``` markers; render content styled, without markers
        cursor = self.textCursor()
        default_fmt = QTextCharFormat()
        content = text
        if text.startswith('```') and text.endswith('```'):
            # Strip first line (```lang) and closing backticks
            body = text[3:]
            # Remove leading optional language tag up to first newline
            newline_idx = body.find('\n')
            if newline_idx != -1:
                body = body[newline_idx+1:]
            content = body[:-3] if body.endswith('```') else body
        code_fmt = QTextCharFormat()
        code_fmt.setForeground(QColor('#2986CC'))
        code_fmt.setBackground(QColor('#000000'))
        cursor.insertText(content, code_fmt)
        # reset to default so following text doesn't inherit code style
        cursor.setCharFormat(default_fmt)


class ApiWorker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, api_key: str, command: str, text: str, model: str,
                 max_tokens: int, temperature: float, out_format: str):
        super().__init__()
        self.api_key = api_key
        self.command = command
        self.text = text
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.out_format = out_format

    def run(self):
        try:
            wrapper = PerplexityWrapper(self.api_key)

            # Build messages according to command
            if self.command == "search":
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant that provides accurate and up-to-date information."},
                    {"role": "user", "content": self.text}
                ]
            else:  # chat
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant."},
                    {"role": "user", "content": self.text}
                ]

            response = wrapper.chat_completion(
                messages=messages,
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )

            formatted = wrapper.format_output(response, self.out_format)
            self.finished.emit(formatted)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perplexity GUI")

        self._thread: QThread | None = None
        self._worker: ApiWorker | None = None

        root_layout = QVBoxLayout()

        # Menu bar with Settings
        self.menu_bar = QMenuBar()
        settings_menu = self.menu_bar.addMenu("Settings")
        self.action_open_settings = QAction("Open Settings", self)
        self.action_open_settings.triggered.connect(self._open_settings_dialog)
        settings_menu.addAction(self.action_open_settings)
        root_layout.setMenuBar(self.menu_bar)

        # Settings state (defaults)
        self._api_key_text = None  # if None, use env
        self._command = "search"
        self._model = "sonar-pro"
        self._temperature = 0.2
        self._max_tokens = 1000
        self._out_format = "pretty"

        # Output display (top)
        self.text_display = ScrollingTextBrowser()
        root_layout.addWidget(self.text_display)

        # Input area (below output) — two lines tall
        self.input_edit = QPlainTextEdit()
        self.input_edit.setPlaceholderText("Type your query or message here...")
        fixed_font = QFont("Courier New")
        fixed_font.setPointSize(10)
        self.input_edit.setFont(fixed_font)
        fm = QFontMetrics(fixed_font)
        self.input_edit.setFixedHeight(fm.lineSpacing() * 2 + 12)
        root_layout.addWidget(self.input_edit)

        # Buttons (below input)
        btn_row = QHBoxLayout()
        self.btn_send = QPushButton("Send")
        self.btn_send.clicked.connect(self._on_send_clicked)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
        self.btn_cancel.setEnabled(False)
        btn_row.addWidget(self.btn_send)
        btn_row.addWidget(self.btn_cancel)
        root_layout.addLayout(btn_row)

        self.setLayout(root_layout)
        self.resize(800, 600)

    def _resolve_api_key(self) -> str | None:
        if self._api_key_text:
            return self._api_key_text
        return os.getenv("PERPLEXITY_API_KEY")

    def _on_send_clicked(self):
        api_key = self._resolve_api_key()
        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Set PERPLEXITY_API_KEY or enter a key in the field.")
            return

        command = self._command
        text = self.input_edit.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Input Required", "Please enter a query or message.")
            return

        model = self._model
        max_tokens = int(self._max_tokens)
        temperature = float(self._temperature)
        out_format = self._out_format

        # UI state
        self.btn_send.setEnabled(False)
        self.btn_cancel.setEnabled(True)

        self.text_display.set_animated_text("⏳ Please wait...\n")

        # Start background worker
        self._thread = QThread()
        self._worker = ApiWorker(api_key, command, text, model, max_tokens, temperature, out_format)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.error.connect(self._on_worker_error)
        self._worker.finished.connect(self._cleanup_thread)
        self._worker.error.connect(self._cleanup_thread)
        self._thread.start()

    def _on_cancel_clicked(self):
        self._cleanup_thread()
        self.text_display.set_animated_text("⚠️ Request cancelled.\n")

    def _on_worker_finished(self, output_text: str):
        self.text_display.set_animated_text(output_text)
        self.btn_send.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _on_worker_error(self, message: str):
        QMessageBox.critical(self, "Request Failed", message)
        self.btn_send.setEnabled(True)
        self.btn_cancel.setEnabled(False)

    def _cleanup_thread(self):
        try:
            if self._thread and self._thread.isRunning():
                self._thread.quit()
                self._thread.wait(2000)
        except Exception:
            pass
        finally:
            self._worker = None
            self._thread = None

    def closeEvent(self, event):
        self._cleanup_thread()
        super().closeEvent(event)

    def _open_settings_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")

        layout = QVBoxLayout(dialog)
        
        # API Key group
        api_group = QGroupBox("API Key")
        api_form = QFormLayout()
        api_key_edit = QLineEdit()
        api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        env_key = os.getenv("PERPLEXITY_API_KEY")
        if self._api_key_text:
            api_key_edit.setText(self._api_key_text)
        else:
            if env_key:
                api_key_edit.setPlaceholderText(f"Using PERPLEXITY_API_KEY ({env_key[:6]}...{env_key[-4:]})")
            else:
                api_key_edit.setPlaceholderText("pplx-... (or set PERPLEXITY_API_KEY)")
        api_form.addRow(QLabel("API Key"), api_key_edit)
        api_group.setLayout(api_form)

        # Parameters group
        params_group = QGroupBox("Parameters")
        params_form = QFormLayout()

        command_combo = QComboBox()
        command_combo.addItems(["search", "chat"])
        command_combo.setCurrentText(self._command)
        params_form.addRow(QLabel("Command"), command_combo)

        model_combo = QComboBox()
        model_combo.addItems([
=======
#!/usr/bin/env python3
"""
Perplexity AI GUI Interface using Zenity
A graphical user interface for the Perplexity AI API wrapper
"""

import os
import sys
import subprocess
import json
import tempfile
from typing import Dict, Any, Optional, List
from wrapper import PerplexityWrapper, get_api_key

class PerplexityGUI:
    def __init__(self):
        self.api_key = None
        self.wrapper = None
        self.current_model = "sonar-pro"
        self.max_tokens = 1000
        self.temperature = 0.2
        self.chat_history = []
        
    def check_zenity(self) -> bool:
        """Check if zenity is available on the system"""
        try:
            subprocess.run(["zenity", "--version"], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def show_error(self, message: str):
        """Show an error dialog"""
        subprocess.run([
            "zenity", "--error", 
            "--title=Perplexity AI - Error",
            f"--text={message}",
            "--width=400"
        ])
    
    def show_info(self, message: str, title: str = "Perplexity AI"):
        """Show an info dialog"""
        subprocess.run([
            "zenity", "--info",
            f"--title={title}",
            f"--text={message}",
            "--width=400"
        ])
    
    def show_loading(self, message: str = "Processing..."):
        """Show a loading dialog"""
        subprocess.run([
            "zenity", "--progress",
            "--title=Perplexity AI",
            f"--text={message}",
            "--pulsate",
            "--auto-close",
            "--width=300"
        ])
    
    def get_text_input(self, prompt: str, title: str = "Perplexity AI") -> Optional[str]:
        """Get text input from user"""
        try:
            result = subprocess.run([
                "zenity", "--entry",
                f"--title={title}",
                f"--text={prompt}",
                "--width=500"
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def get_text_area_input(self, prompt: str, title: str = "Perplexity AI") -> Optional[str]:
        """Get multi-line text input from user"""
        try:
            result = subprocess.run([
                "zenity", "--text-info",
                f"--title={title}",
                f"--text={prompt}",
                "--editable",
                "--width=600",
                "--height=300"
            ], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def show_response(self, response: str, title: str = "Perplexity AI Response"):
        """Show response in a text dialog"""
        # Create a temporary file for the response
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(response)
            temp_file = f.name
        
        try:
            subprocess.run([
                "zenity", "--text-info",
                f"--title={title}",
                f"--filename={temp_file}",
                "--width=800",
                "--height=600"
            ])
        finally:
            os.unlink(temp_file)
    
    def show_question(self, question: str, title: str = "Perplexity AI") -> bool:
        """Show a yes/no question dialog"""
        try:
            result = subprocess.run([
                "zenity", "--question",
                f"--title={title}",
                f"--text={question}",
                "--width=400"
            ], capture_output=True)
            return result.returncode == 0
        except subprocess.CalledProcessError:
            return False
    
    def show_menu(self, title: str, text: str, options: List[str]) -> Optional[str]:
        """Show a menu dialog"""
        try:
            # Create options string for zenity
            options_str = " ".join([f'"{opt}"' for opt in options])
            
            result = subprocess.run([
                "zenity", "--list",
                f"--title={title}",
                f"--text={text}",
                "--column=Options",
                *options
            ], capture_output=True, text=True, check=True)
            
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
    
    def setup_api_key(self) -> bool:
        """Setup API key"""
        self.api_key = get_api_key()
        if not self.api_key:
            api_key = self.get_text_input(
                "Enter your Perplexity API key:",
                "API Key Setup"
            )
            if not api_key:
                self.show_error("No API key provided. Exiting.")
                return False
            self.api_key = api_key
        
        try:
            self.wrapper = PerplexityWrapper(self.api_key)
            return True
        except Exception as e:
            self.show_error(f"Failed to initialize API wrapper: {str(e)}")
            return False
    
    def show_settings(self):
        """Show settings dialog"""
        # Model selection
        models = [
>>>>>>> aaef2fa (Added gui.py && ppx)
            "sonar-pro",
            "llama-3.1-sonar-small-128k-chat",
            "llama-3.1-sonar-large-128k-chat",
            "llama-3.1-sonar-huge-128k-chat"
<<<<<<< HEAD
        ])
        model_combo.setCurrentText(self._model)
        params_form.addRow(QLabel("Model"), model_combo)

        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(0.0, 2.0)
        temp_spin.setSingleStep(0.1)
        temp_spin.setValue(self._temperature)
        params_form.addRow(QLabel("Temperature"), temp_spin)

        tokens_spin = QSpinBox()
        tokens_spin.setRange(1, 128000)
        tokens_spin.setValue(self._max_tokens)
        params_form.addRow(QLabel("Max Tokens"), tokens_spin)

        format_combo = QComboBox()
        format_combo.addItems(["pretty", "json"])
        format_combo.setCurrentText(self._out_format)
        params_form.addRow(QLabel("Output Format"), format_combo)

        params_group.setLayout(params_form)

        layout.addWidget(api_group)
        layout.addWidget(params_group)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)

        def accept():
            text = api_key_edit.text().strip()
            self._api_key_text = text if text else None
            self._command = command_combo.currentText()
            self._model = model_combo.currentText()
            self._temperature = float(temp_spin.value())
            self._max_tokens = int(tokens_spin.value())
            self._out_format = format_combo.currentText()
            dialog.accept()

        def reject():
            dialog.reject()

        buttons.accepted.connect(accept)
        buttons.rejected.connect(reject)

        dialog.exec()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

=======
        ]
        
        selected_model = self.show_menu(
            "Model Selection",
            "Choose AI model:",
            models
        )
        
        if selected_model:
            self.current_model = selected_model
        
        # Max tokens
        max_tokens_str = self.get_text_input(
            f"Max tokens (current: {self.max_tokens}):",
            "Max Tokens"
        )
        if max_tokens_str and max_tokens_str.isdigit():
            self.max_tokens = int(max_tokens_str)
        
        # Temperature
        temp_str = self.get_text_input(
            f"Temperature (current: {self.temperature}):",
            "Temperature"
        )
        if temp_str:
            try:
                self.temperature = float(temp_str)
            except ValueError:
                pass
        
        self.show_info("Settings updated successfully!")
    
    def perform_search(self):
        """Perform a search query"""
        query = self.get_text_input(
            "Enter your search query:",
            "Search Query"
        )
        
        if not query:
            return
        
        # Show loading dialog in background
        loading_process = subprocess.Popen([
            "zenity", "--progress",
            "--title=Perplexity AI",
            "--text=Searching...",
            "--pulsate",
            "--auto-close",
            "--width=300"
        ])
        
        try:
            response = self.wrapper.search(
                query=query,
                model=self.current_model
            )
            
            # Kill loading dialog
            loading_process.terminate()
            
            if "error" in response:
                self.show_error(f"Search failed: {response['error']}")
                return
            
            # Format response
            formatted_response = self.wrapper.format_output(response, "pretty")
            self.show_response(formatted_response, f"Search Results: {query}")
            
        except Exception as e:
            loading_process.terminate()
            self.show_error(f"Search failed: {str(e)}")
    
    def start_chat(self):
        """Start a chat conversation"""
        self.chat_history = []
        
        while True:
            # Show chat history if any
            if self.chat_history:
                history_text = "\n".join([
                    f"{'User' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
                    for msg in self.chat_history[-6:]  # Show last 6 messages
                ])
                message = self.get_text_area_input(
                    f"Chat History:\n{history_text}\n\nEnter your message:",
                    "Chat with Perplexity AI"
                )
            else:
                message = self.get_text_input(
                    "Enter your message:",
                    "Chat with Perplexity AI"
                )
            
            if not message:
                break
            
            # Add user message to history
            self.chat_history.append({"role": "user", "content": message})
            
            # Show loading dialog in background
            loading_process = subprocess.Popen([
                "zenity", "--progress",
                "--title=Perplexity AI",
                "--text=Thinking...",
                "--pulsate",
                "--auto-close",
                "--width=300"
            ])
            
            try:
                # Prepare messages for API
                messages = [
                    {"role": "system", "content": "You are a helpful AI assistant."}
                ] + self.chat_history
                
                response = self.wrapper.chat_completion(
                    messages=messages,
                    model=self.current_model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                # Kill loading dialog
                loading_process.terminate()
                
                if "error" in response:
                    self.show_error(f"Chat failed: {response['error']}")
                    continue
                
                # Extract AI response
                if "choices" in response and response["choices"]:
                    ai_response = response["choices"][0]["message"]["content"]
                    self.chat_history.append({"role": "assistant", "content": ai_response})
                    
                    # Show response
                    formatted_response = self.wrapper.format_output(response, "pretty")
                    self.show_response(formatted_response, "AI Response")
                else:
                    self.show_error("No response received from AI")
                
            except Exception as e:
                loading_process.terminate()
                self.show_error(f"Chat failed: {str(e)}")
            
            # Ask if user wants to continue
            if not self.show_question("Continue chatting?", "Continue Chat"):
                break
    
    def show_main_menu(self):
        """Show the main menu"""
        while True:
            choice = self.show_menu(
                "Perplexity AI - Main Menu",
                "Choose an option:",
                [
                    "🔍 Search Query",
                    "💬 Start Chat",
                    "⚙️ Settings",
                    "ℹ️ About",
                    "❌ Exit"
                ]
            )
            
            if not choice:
                break
            
            if "Search" in choice:
                self.perform_search()
            elif "Chat" in choice:
                self.start_chat()
            elif "Settings" in choice:
                self.show_settings()
            elif "About" in choice:
                self.show_about()
            elif "Exit" in choice:
                break
    
    def show_about(self):
        """Show about information"""
        about_text = """Perplexity AI GUI

A graphical interface for the Perplexity AI API.

Features:
• 🔍 Search queries with real-time information
• 💬 Interactive chat conversations
• ⚙️ Customizable settings (model, tokens, temperature)
• 🎨 Beautiful zenity-based interface

Version: 1.0
Author: Perplexity CLI Team"""
        
        self.show_response(about_text, "About Perplexity AI GUI")
    
    def run(self):
        """Main run method"""
        # Check if zenity is available
        if not self.check_zenity():
            print("Error: zenity is not installed or not available.")
            print("Please install zenity to use the GUI interface.")
            print("On Ubuntu/Debian: sudo apt install zenity")
            print("On Arch Linux: sudo pacman -S zenity")
            sys.exit(1)
        
        # Setup API key
        if not self.setup_api_key():
            sys.exit(1)
        
        # Show welcome message
        self.show_info(
            "Welcome to Perplexity AI GUI!\n\n"
            "This interface allows you to interact with Perplexity AI "
            "through a graphical interface using zenity dialogs.",
            "Welcome"
        )
        
        # Show main menu
        self.show_main_menu()
        
        # Show goodbye message
        self.show_info("Thank you for using Perplexity AI GUI!", "Goodbye")

def main():
    """Main entry point"""
    gui = PerplexityGUI()
    gui.run()
>>>>>>> aaef2fa (Added gui.py && ppx)

if __name__ == "__main__":
    main()

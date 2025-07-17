import sublime
import sublime_plugin
import subprocess
import os
import threading
import json
import re
from pathlib import Path


class GoCommand(sublime_plugin.TextCommand):
    """Base class for Go commands with common functionality"""

    def get_go_env(self):
        """Get Go environment variables"""
        try:
            result = subprocess.run(['go', 'env', '-json'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"Failed to get Go env: {e}")
        return {}

    def get_project_root(self):
        """Find the project root containing go.mod or fallback to current file dir"""
        view = self.view
        if not view.file_name():
            return None

        current_dir = Path(view.file_name()).parent

        # Look for go.mod up the directory tree
        for parent in [current_dir] + list(current_dir.parents):
            if (parent / 'go.mod').exists():
                return str(parent)

        # Fallback to current file directory
        return str(current_dir)

    def has_go_mod(self, directory=None):
        """Check if go.mod exists in the directory or its parents"""
        if not directory:
            directory = self.get_project_root()

        if not directory:
            return False

        current_dir = Path(directory)
        for parent in [current_dir] + list(current_dir.parents):
            if (parent / 'go.mod').exists():
                return True
        return False

    def is_single_file_program(self):
        """Check if current file is a standalone Go program"""
        file_name = self.view.file_name()
        if not file_name or not file_name.endswith('.go'):
            return False

        content = self.view.substr(sublime.Region(0, self.view.size()))

        # Check for package main and main function
        has_package_main = 'package main' in content
        has_main_func = re.search(r'func\s+main\s*\(', content)

        if not (has_package_main and has_main_func):
            return False

        # Check for imports that require modules
        import_lines = re.findall(r'import\s+(?:"([^"]+)"|`([^`]+)`)', content)

        for match in import_lines:
            import_path = match[0] or match[1]

            # Skip standard library packages
            if self.is_standard_library(import_path):
                continue

            # Any non-standard library import requires modules
            return False

        return True

    def is_standard_library(self, import_path):
        """Check if an import path is from the standard library"""
        # Standard library packages don't contain dots (except for some special cases)
        if '.' not in import_path:
            return True

        # Known standard library packages with dots
        std_lib_with_dots = [
            'golang.org/x/crypto',
            'golang.org/x/net',
            'golang.org/x/text',
            'golang.org/x/sys',
            'golang.org/x/time'
        ]

        for std_pkg in std_lib_with_dots:
            if import_path.startswith(std_pkg):
                return True

        # Relative imports (./something) require modules
        if import_path.startswith('./') or import_path.startswith('../'):
            return False

        # Everything else with dots is likely external
        return False

    def is_simple_multi_file_main(self):
        """Check if this is a simple multi-file main package (no modules needed)"""
        if not self.view.file_name():
            return False

        content = self.view.substr(sublime.Region(0, self.view.size()))

        # Must be package main
        if 'package main' not in content:
            return False

        # Check imports - only standard library allowed
        import_lines = re.findall(r'import\s+(?:"([^"]+)"|`([^`]+)`)', content)

        for match in import_lines:
            import_path = match[0] or match[1]
            if not self.is_standard_library(import_path):
                return False

        return True

    def needs_module(self, command_args):
        """Determine if a command requires a module"""
        # Commands that work without modules for single files
        single_file_commands = ['run', 'fmt', 'vet']

        # Commands that always need modules
        module_required_commands = ['get', 'mod', 'install']

        if any(arg in module_required_commands for arg in command_args):
            return True

        if any(arg in single_file_commands for arg in command_args):
            # For single file programs or simple multi-file main packages, these commands don't need modules
            if self.is_single_file_program() or self.is_simple_multi_file_main():
                return False
            # For complex projects, they do need modules
            return True

        # Build and test commands
        if any(arg in ['build', 'test'] for arg in command_args):
            # If it's a single file with package main or simple multi-file main, we can use different approach
            if self.is_single_file_program() or self.is_simple_multi_file_main():
                return False
            return True

        return False

    def show_output_panel(self, content, title="Go Output"):
        """Show output in a panel"""
        window = self.view.window()
        panel = window.create_output_panel("go_output")
        panel.set_syntax_file("Packages/Text/Plain text.tmLanguage")
        panel.run_command('append', {'characters': content})
        window.run_command('show_panel', {'panel': 'output.go_output'})

    def prompt_create_module(self, callback):
        """Prompt user to create a go.mod file"""
        window = self.view.window()

        def on_module_name(module_name):
            if module_name:
                self.create_go_mod(module_name, callback)
            else:
                self.show_output_panel("Module creation cancelled")

        # Get default module name from settings
        settings = sublime.load_settings("GoBuild.sublime-settings")
        default_name = settings.get("default_module_name", "")

        window.show_input_panel(
            "Module name (e.g., github.com/user/project):",
            default_name,
            on_module_name,
            None,
            None
        )

    def create_go_mod(self, module_name, callback=None):
        """Create a go.mod file"""
        root_dir = self.get_project_root()
        if not root_dir:
            self.show_output_panel("Could not determine project directory")
            return

        def create_thread():
            try:
                cmd = ['go', 'mod', 'init', module_name]
                result = subprocess.run(cmd, cwd=root_dir, capture_output=True,
                                      text=True, timeout=30)

                def handle_result():
                    if result.returncode == 0:
                        self.show_output_panel(f"Created go.mod with module: {module_name}")
                        if callback:
                            callback()
                    else:
                        error_msg = f"Failed to create go.mod:\n{result.stderr}"
                        self.show_output_panel(error_msg)

                sublime.set_timeout(handle_result, 0)

            except Exception as e:
                sublime.set_timeout(lambda: self.show_output_panel(f"Error creating module: {e}"), 0)

        threading.Thread(target=create_thread).start()

    def run_go_command(self, args, cwd=None, callback=None, force_check_mod=None):
        """Run a go command asynchronously with smart module handling"""
        if not cwd:
            cwd = self.get_project_root()

        # Determine if we need modules for this command
        check_mod = force_check_mod if force_check_mod is not None else self.needs_module(args)

        # Only enforce module requirement if really needed
        if check_mod and not self.has_go_mod(cwd):
            settings = sublime.load_settings("GoBuild.sublime-settings")
            auto_create = settings.get("auto_create_mod", False)  # Default to False for less intrusion

            if auto_create:
                default_name = settings.get("default_module_name", "")
                if default_name:
                    self.create_go_mod(default_name, lambda: self.run_go_command(args, cwd, callback, False))
                    return
                else:
                    self.prompt_create_module(lambda: self.run_go_command(args, cwd, callback, False))
                    return
            else:
                # Show helpful but non-blocking error message
                command_name = args[0] if args else "command"
                error_msg = (f"The '{command_name}' command requires a Go module, but no go.mod file was found.\n\n"
                           f"This project appears to need module initialization.\n\n"
                           f"Solutions:\n"
                           f"1. Run 'Go: Initialize Module' (Ctrl+Shift+G, Ctrl+Shift+M)\n"
                           f"2. Enable auto-creation in settings: 'auto_create_mod': true\n"
                           f"3. Run 'go mod init <module-name>' in terminal\n\n"
                           f"Note: Single Go files with 'package main' can often run without modules.")
                self.show_output_panel(error_msg)
                return

        def run_thread():
            try:
                cmd = ['go'] + args
                result = subprocess.run(cmd, cwd=cwd, capture_output=True,
                                      text=True, timeout=30)

                if callback:
                    sublime.set_timeout(lambda: callback(result), 0)
                else:
                    output = f"Command: {' '.join(cmd)}\nDirectory: {cwd}\n\n"
                    if result.stdout:
                        output += f"Output:\n{result.stdout}\n"
                    if result.stderr:
                        output += f"Errors:\n{result.stderr}\n"
                    output += f"\nExit code: {result.returncode}"

                    sublime.set_timeout(lambda: self.show_output_panel(output), 0)
            except subprocess.TimeoutExpired:
                sublime.set_timeout(lambda: self.show_output_panel("Command timed out"), 0)
            except Exception as e:
                sublime.set_timeout(lambda: self.show_output_panel(f"Error: {e}"), 0)

        threading.Thread(target=run_thread).start()


class GoBuildCommand(GoCommand):
    """Build the current Go package"""

    def run(self, edit):
        file_name = self.view.file_name()

        if self.is_single_file_program() and file_name:
            # For single files, compile to executable
            base_name = os.path.splitext(os.path.basename(file_name))[0]
            self.run_go_command(['build', '-o', base_name, os.path.basename(file_name)],
                              cwd=os.path.dirname(file_name), force_check_mod=False)
        elif self.is_simple_multi_file_main() and file_name:
            # For simple multi-file main package, build all files in directory
            self.run_go_command(['build', '.'],
                              cwd=os.path.dirname(file_name), force_check_mod=False)
        else:
            # For module-based projects
            self.run_go_command(['build', '.'])


class GoRunCommand(GoCommand):
    """Run the current Go file or main package"""

    def run(self, edit):
        file_name = self.view.file_name()

        if file_name and file_name.endswith('.go'):
            if self.is_single_file_program():
                # Run single file directly - no module needed
                self.run_go_command(['run', os.path.basename(file_name)],
                                  cwd=os.path.dirname(file_name), force_check_mod=False)
            elif self.is_simple_multi_file_main():
                # Run all Go files in directory for simple multi-file main package
                self.run_go_command(['run', '.'],
                                  cwd=os.path.dirname(file_name), force_check_mod=False)
            else:
                # Run as module
                self.run_go_command(['run', '.'])
        else:
            self.run_go_command(['run', '.'])


class GoTestCommand(GoCommand):
    """Run tests for current package"""

    def run(self, edit):
        file_name = self.view.file_name()

        if file_name and file_name.endswith('_test.go'):
            # For single test files
            if self.is_single_file_program():
                main_file = file_name.replace('_test.go', '.go')
                if os.path.exists(main_file):
                    # Test single file with its main file
                    self.run_go_command(['test', os.path.basename(main_file), os.path.basename(file_name)],
                                      cwd=os.path.dirname(file_name), force_check_mod=False)
                else:
                    self.run_go_command(['test', os.path.basename(file_name)],
                                      cwd=os.path.dirname(file_name), force_check_mod=False)
            else:
                self.run_go_command(['test', '-v', '.'])
        else:
            self.run_go_command(['test', '-v', '.'])


class GoTestAllCommand(GoCommand):
    """Run all tests in project"""

    def run(self, edit):
        self.run_go_command(['test', '-v', './...'])


class GoTestFunctionCommand(GoCommand):
    """Run specific test function under cursor"""

    def run(self, edit):
        # Find test function name under cursor
        cursor = self.view.sel()[0].begin()
        line_region = self.view.line(cursor)
        line_content = self.view.substr(line_region)

        # Look for test function pattern
        test_match = re.search(r'func\s+(Test\w+)', line_content)
        if test_match:
            test_name = test_match.group(1)

            file_name = self.view.file_name()
            if self.is_single_file_program() and file_name:
                # Single file test
                self.run_go_command(['test', '-run', f'^{test_name}$', os.path.basename(file_name)],
                                  cwd=os.path.dirname(file_name), force_check_mod=False)
            else:
                # Module-based test
                self.run_go_command(['test', '-v', '-run', f'^{test_name}$', '.'])
        else:
            # Search upward for test function
            current_line = self.view.rowcol(cursor)[0]
            for line_num in range(current_line, max(0, current_line - 50), -1):
                line_region = self.view.line(self.view.text_point(line_num, 0))
                line_content = self.view.substr(line_region)
                test_match = re.search(r'func\s+(Test\w+)', line_content)
                if test_match:
                    test_name = test_match.group(1)

                    file_name = self.view.file_name()
                    if self.is_single_file_program() and file_name:
                        self.run_go_command(['test', '-run', f'^{test_name}$', os.path.basename(file_name)],
                                          cwd=os.path.dirname(file_name), force_check_mod=False)
                    else:
                        self.run_go_command(['test', '-v', '-run', f'^{test_name}$', '.'])
                    return

            self.show_output_panel("No test function found near cursor")


class GoBenchmarkCommand(GoCommand):
    """Run benchmarks for current package"""

    def run(self, edit):
        if self.is_single_file_program():
            file_name = self.view.file_name()
            if file_name:
                self.run_go_command(['test', '-bench=.', '-benchmem', os.path.basename(file_name)],
                                  cwd=os.path.dirname(file_name), force_check_mod=False)
        else:
            self.run_go_command(['test', '-bench=.', '-benchmem', '.'])


class GoVetCommand(GoCommand):
    """Run go vet on current package"""

    def run(self, edit):
        if self.is_single_file_program():
            file_name = self.view.file_name()
            if file_name:
                self.run_go_command(['vet', os.path.basename(file_name)],
                                  cwd=os.path.dirname(file_name), force_check_mod=False)
        else:
            self.run_go_command(['vet', '.'])


class GoFmtCommand(GoCommand):
    """Format current file with gofmt"""

    def run(self, edit):
        file_name = self.view.file_name()
        if file_name and file_name.endswith('.go'):
            def format_callback(result):
                if result.returncode == 0 and result.stdout:
                    # Replace file content with formatted version
                    region = sublime.Region(0, self.view.size())
                    self.view.replace(edit, region, result.stdout)
                else:
                    self.show_output_panel(result.stderr or "Formatting failed")

            try:
                with open(file_name, 'r') as f:
                    content = f.read()

                def run_thread():
                    try:
                        result = subprocess.run(['gofmt'], input=content,
                                              capture_output=True, text=True, timeout=10)
                        sublime.set_timeout(lambda: format_callback(result), 0)
                    except Exception as e:
                        sublime.set_timeout(lambda: self.show_output_panel(f"Format error: {e}"), 0)

                threading.Thread(target=run_thread).start()
            except Exception as e:
                self.show_output_panel(f"Error reading file: {e}")


class GoImportsCommand(GoCommand):
    """Fix imports with goimports"""

    def run(self, edit):
        file_name = self.view.file_name()
        if file_name and file_name.endswith('.go'):
            def imports_callback(result):
                if result.returncode == 0 and result.stdout:
                    region = sublime.Region(0, self.view.size())
                    self.view.replace(edit, region, result.stdout)
                else:
                    self.show_output_panel(result.stderr or "goimports failed")

            try:
                with open(file_name, 'r') as f:
                    content = f.read()

                def run_thread():
                    try:
                        result = subprocess.run(['goimports'], input=content,
                                              capture_output=True, text=True, timeout=10)
                        sublime.set_timeout(lambda: imports_callback(result), 0)
                    except FileNotFoundError:
                        sublime.set_timeout(lambda: self.show_output_panel(
                            "goimports not found. Install with: go install golang.org/x/tools/cmd/goimports@latest"), 0)
                    except Exception as e:
                        sublime.set_timeout(lambda: self.show_output_panel(f"goimports error: {e}"), 0)

                threading.Thread(target=run_thread).start()
            except Exception as e:
                self.show_output_panel(f"Error reading file: {e}")


class GoModInitCommand(GoCommand):
    """Initialize a new Go module"""

    def run(self, edit):
        window = self.view.window()

        # Check if go.mod already exists
        if self.has_go_mod():
            self.show_output_panel("go.mod already exists in this project")
            return

        # Get default module name from settings
        settings = sublime.load_settings("GoBuild.sublime-settings")
        default_name = settings.get("default_module_name", "")

        window.show_input_panel(
            "Module name (e.g., github.com/user/project):",
            default_name,
            self.on_module_name_entered,
            None,
            None
        )

    def on_module_name_entered(self, module_name):
        if module_name:
            self.create_go_mod(module_name)


class GoModTidyCommand(GoCommand):
    """Run go mod tidy"""

    def run(self, edit):
        self.run_go_command(['mod', 'tidy'])


class GoGetCommand(GoCommand):
    """Add dependency (prompts for package name)"""

    def run(self, edit):
        window = self.view.window()
        window.show_input_panel(
            "Go get package:", "", self.on_package_entered, None, None)

    def on_package_entered(self, package):
        if package:
            self.run_go_command(['get', package])


class GoInstallCommand(GoCommand):
    """Install current package"""

    def run(self, edit):
        self.run_go_command(['install', '.'])


class GoCleanCommand(GoCommand):
    """Clean build cache and artifacts"""

    def run(self, edit):
        self.run_go_command(['clean', '-cache', '-modcache', '-testcache'], force_check_mod=False)


class GoCoverageCommand(GoCommand):
    """Generate and show test coverage"""

    def run(self, edit):
        def coverage_callback(result):
            if result.returncode == 0:
                # Show coverage profile
                self.run_go_command(['tool', 'cover', '-html=coverage.out'], force_check_mod=False)
            else:
                self.show_output_panel(result.stderr or "Coverage generation failed")

        if self.is_single_file_program():
            file_name = self.view.file_name()
            if file_name:
                self.run_go_command(['test', '-coverprofile=coverage.out', os.path.basename(file_name)],
                                  cwd=os.path.dirname(file_name), callback=coverage_callback, force_check_mod=False)
        else:
            self.run_go_command(['test', '-coverprofile=coverage.out', '.'], callback=coverage_callback)


class GoDocCommand(GoCommand):
    """Show documentation for symbol under cursor"""

    def run(self, edit):
        # Get word under cursor
        cursor = self.view.sel()[0]
        word_region = self.view.word(cursor)
        word = self.view.substr(word_region)

        if word:
            self.run_go_command(['doc', word], force_check_mod=False)
        else:
            self.show_output_panel("No symbol selected")


class GoPlaygroundCommand(GoCommand):
    """Send current file to Go Playground"""

    def run(self, edit):
        content = self.view.substr(sublime.Region(0, self.view.size()))

        def playground_thread():
            try:
                import urllib.request
                import urllib.parse

                data = urllib.parse.urlencode({'body': content}).encode()
                req = urllib.request.Request('https://play.golang.org/share', data=data)

                with urllib.request.urlopen(req, timeout=10) as response:
                    share_id = response.read().decode()
                    url = f"https://play.golang.org/p/{share_id}"

                    sublime.set_timeout(lambda: self.show_output_panel(
                        f"Playground URL: {url}\n\nURL copied to clipboard!"), 0)
                    sublime.set_timeout(lambda: sublime.set_clipboard(url), 0)

            except Exception as e:
                sublime.set_timeout(lambda: self.show_output_panel(f"Playground error: {e}"), 0)

        threading.Thread(target=playground_thread).start()


class GoEnvironmentCommand(GoCommand):
    """Show Go environment information"""

    def run(self, edit):
        def env_callback(result):
            if result.returncode == 0:
                try:
                    env_data = json.loads(result.stdout)
                    output = "Go Environment:\n" + "="*50 + "\n"
                    for key, value in sorted(env_data.items()):
                        output += f"{key}: {value}\n"

                    # Add file and module status
                    output += "\n" + "="*50 + "\n"

                    file_name = self.view.file_name()
                    if file_name:
                        output += f"Current File: {os.path.basename(file_name)}\n"
                        if self.is_single_file_program():
                            output += "File Type: ✓ Single file program (no module needed)\n"
                        else:
                            output += "File Type: Multi-file project (module recommended)\n"

                    if self.has_go_mod():
                        output += "Module Status: ✓ go.mod found\n"
                        mod_root = self.get_project_root()
                        if mod_root:
                            try:
                                with open(os.path.join(mod_root, 'go.mod'), 'r') as f:
                                    first_line = f.readline().strip()
                                    if first_line.startswith('module '):
                                        output += f"Module Name: {first_line[7:]}\n"
                            except:
                                pass
                    else:
                        output += "Module Status: ✗ No go.mod found\n"
                        if not self.is_single_file_program():
                            output += "Recommendation: Run 'Go: Initialize Module' for multi-file projects\n"

                    self.show_output_panel(output)
                except json.JSONDecodeError:
                    self.show_output_panel(result.stdout)
            else:
                self.show_output_panel(result.stderr or "Failed to get Go environment")

        self.run_go_command(['env', '-json'], callback=env_callback, force_check_mod=False)


class GoVersionCommand(GoCommand):
    """Show Go version"""

    def run(self, edit):
        self.run_go_command(['version'], force_check_mod=False)


# Auto-format on save (optional - can be enabled in settings)
class GoFormatOnSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        settings = sublime.load_settings("GoBuild.sublime-settings")
        if (settings.get("format_on_save", False) and
            view.file_name() and view.file_name().endswith('.go')):
            if settings.get("use_goimports", True):
                view.run_command('go_imports')
            else:
                view.run_command('go_fmt')

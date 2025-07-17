### Quick Start Examples

#### 1. Simple Hello World (No Module Needed)
```go
// main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```
- Save the file as `main.go`
- Press `Ctrl+Shift+G, Ctrl+R` to run
- **No go.mod required!** Plugin detects this as a single-file program

#### 2. Multi-File Project (Module Required)
```bash
mkdir myproject
cd myproject
```

Use plugin to initialize module: `Ctrl+Shift+G, Ctrl+Shift+M`
- Enter: `github.com/username/myproject`

Create proper module structure:
```go
// main.go
package main

import (
    "fmt"
    "github.com/username/myproject/utils"  // Proper module import
)

func main() {
    fmt.Println(utils.Greet("World"))
}
```

```go
// utils/greet.go
package utils

func Greet(name string) string {
    return "Hello, " + name + "!"
}
```

- Press `Ctrl+Shift+G, Ctrl+R` to run

#### Alternative: Simple Multi-File (Same Package)
If you want multiple files in the same package without modules:
```go
// main.go
package main

import "fmt"

func main() {
    fmt.Println(Greet("World"))
}
```

```go
// greet.go
package main  // Same package, no import needed

func Greet(name string) string {
    return "Hello, " + name + "!"
}
```
- This works without go.mod since it's all `package main`
- Use `go run *.go` or `go run .` to run all files

#### 3. Project with External Dependencies
```go
// main.go
package main

import (
    "fmt"
    "github.com/gorilla/mux"  // External dependency
)

func main() {
    r := mux.NewRouter()
    fmt.Println("Server starting...")
}
```

1. Initialize module: `Ctrl+Shift+G, Ctrl+Shift+M`
2. Ad# Go Build System for Sublime Text

A comprehensive Go development plugin that provides build system integration, testing, formatting, and productivity tools for Sublime Text. This plugin fills the gap left by the discontinued GoSublime package and works seamlessly with LSP-gopls.

## 📁 Project Types & Module Requirements

### ✅ No Module Needed (Works Immediately)

#### Single File Programs
```go
// hello.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```
**Commands:** `go run hello.go`, `go build hello.go`, `go fmt hello.go`

#### Simple Multi-File Main Package
```go
// main.go
package main

import "fmt"

func main() {
    fmt.Println(greet("World"))
}
```

```go
// greet.go  
package main  // Same package!

import "fmt"

func greet(name string) string {
    return fmt.Sprintf("Hello, %s!", name)
}
```
**Commands:** `go run .`, `go build .`, `go run *.go`
**Key:** All files use `package main` with only standard library imports

### 📦 Module Required

#### Multi-Package Project
```go
// main.go
package main

import (
    "fmt"
    "myproject/utils"  // Different package
)

func main() {
    fmt.Println(utils.Greet("World"))
}
```

```go
// utils/greet.go
package utils  // Different package name

func Greet(name string) string {
    return "Hello, " + name + "!"
}
```
**Need:** `go mod init myproject` first

#### External Dependencies
```go
// main.go
package main

import (
    "fmt"
    "github.com/gin-gonic/gin"  // External dependency
)

func main() {
    r := gin.Default()
    fmt.Println("Server ready")
}
```
**Need:** Module + `go get github.com/gin-gonic/gin`

### Core Build & Run
- **Build Package** (`Ctrl+Shift+G, Ctrl+B`) - Build current Go package
- **Run** (`Ctrl+Shift+G, Ctrl+R`) - Run current file or main package  
- **Install** (`Ctrl+Shift+G, Ctrl+Shift+I`) - Install current package

### Testing & Benchmarking
- **Test Package** (`Ctrl+Shift+G, Ctrl+T`) - Run tests for current package
- **Test All** (`Ctrl+Shift+G, Ctrl+Shift+T`) - Run all tests in project
- **Test Function** (`Ctrl+Shift+G, Ctrl+F`) - Run specific test under cursor
- **Benchmark** (`Ctrl+Shift+G, Ctrl+Shift+B`) - Run benchmarks
- **Coverage** (`Ctrl+Shift+G, Ctrl+C`) - Generate test coverage report

### Code Quality
- **Format** (`Ctrl+Shift+G, Ctrl+Shift+F`) - Format with gofmt
- **Fix Imports** (`Ctrl+Shift+G, Ctrl+I`) - Organize imports with goimports
- **Vet** (`Ctrl+Shift+G, Ctrl+V`) - Run go vet analysis

### Module Management
- **Go Get** (`Ctrl+Shift+G, Ctrl+G`) - Add dependency (prompts for package)
- **Mod Init** (`Ctrl+Shift+G, Ctrl+Shift+M`) - Initialize new module
- **Mod Tidy** (`Ctrl+Shift+G, Ctrl+M`) - Clean up dependencies
- **Clean** - Clean build cache and artifacts

### Documentation & Tools
- **Documentation** (`Ctrl+Shift+G, Ctrl+D`) - Show docs for symbol under cursor
- **Playground** (`Ctrl+Shift+G, Ctrl+P`) - Send current file to Go Playground
- **Environment** (`Ctrl+Shift+G, Ctrl+E`) - Show Go environment info
- **Version** (`Ctrl+Shift+G, Ctrl+Shift+V`) - Show Go version

## 📦 Installation

### Prerequisites
- Go 1.16+ installed and in PATH
- Sublime Text 3/4
- LSP-gopls plugin (recommended)

### Step 1: Find Sublime Text Packages Directory
```bash
# Windows
%APPDATA%\Sublime Text\Packages

# macOS  
~/Library/Application Support/Sublime Text/Packages

# Linux
~/.config/sublime-text/Packages
```

### Step 2: Create Plugin Directory
```bash
cd /path/to/sublime/packages
mkdir GoBuild
cd GoBuild
```

### Step 3: Install Plugin Files

Create the following files in the `GoBuild` directory:

#### `GoBuild.py` (Main Plugin File)
Download or copy the main plugin code into this file.

#### `Go.sublime-build` (Build System)
```json
{
  "shell_cmd": "go run .",
  "file_regex": "^(..[^:]*):([0-9]+):?([0-9]+)?:? (.*)$",
  "working_dir": "${project_path:${folder}}",
  "selector": "source.go",
  "variants": [
    {
      "name": "Build",
      "shell_cmd": "go build ."
    },
    {
      "name": "Test",
      "shell_cmd": "go test -v ."
    },
    {
      "name": "Test All", 
      "shell_cmd": "go test -v ./..."
    },
    {
      "name": "Benchmark",
      "shell_cmd": "go test -bench=. -benchmem ."
    },
    {
      "name": "Install",
      "shell_cmd": "go install ."
    },
    {
      "name": "Vet",
      "shell_cmd": "go vet ."
    },
    {
      "name": "Clean",
      "shell_cmd": "go clean -cache"
    },
    {
      "name": "Mod Tidy",
      "shell_cmd": "go mod tidy"
    }
  ]
}
```

#### `GoBuild.sublime-settings` (Plugin Settings)
```json
{
  "format_on_save": false,
  "use_goimports": true,
  "show_panel_on_build": true,
  "go_executable": "go",
  "gofmt_executable": "gofmt", 
  "goimports_executable": "goimports",
  "auto_create_mod": true,
  "default_module_name": ""
}
```

#### `Default.sublime-keymap` (Key Bindings)
```json
[
  { "keys": ["ctrl+shift+g", "ctrl+b"], "command": "go_build" },
  { "keys": ["ctrl+shift+g", "ctrl+r"], "command": "go_run" },
  { "keys": ["ctrl+shift+g", "ctrl+t"], "command": "go_test" },
  { "keys": ["ctrl+shift+g", "ctrl+shift+t"], "command": "go_test_all" },
  { "keys": ["ctrl+shift+g", "ctrl+f"], "command": "go_test_function" },
  { "keys": ["ctrl+shift+g", "ctrl+shift+b"], "command": "go_benchmark" },
  { "keys": ["ctrl+shift+g", "ctrl+v"], "command": "go_vet" },
  { "keys": ["ctrl+shift+g", "ctrl+shift+f"], "command": "go_fmt" },
  { "keys": ["ctrl+shift+g", "ctrl+i"], "command": "go_imports" },
  { "keys": ["ctrl+shift+g", "ctrl+m"], "command": "go_mod_tidy" },
  { "keys": ["ctrl+shift+g", "ctrl+shift+m"], "command": "go_mod_init" },
  { "keys": ["ctrl+shift+g", "ctrl+g"], "command": "go_get" },
  { "keys": ["ctrl+shift+g", "ctrl+shift+i"], "command": "go_install" },
  { "keys": ["ctrl+shift+g", "ctrl+c"], "command": "go_coverage" },
  { "keys": ["ctrl+shift+g", "ctrl+d"], "command": "go_doc" },
  { "keys": ["ctrl+shift+g", "ctrl+p"], "command": "go_playground" },
  { "keys": ["ctrl+shift+g", "ctrl+e"], "command": "go_environment" },
  { "keys": ["ctrl+shift+g", "ctrl+shift+v"], "command": "go_version" }
]
```

#### `Main.sublime-menu` (Menu Integration)
```json
[
  {
    "caption": "Tools",
    "mnemonic": "T",
    "id": "tools",
    "children": [
      {
        "caption": "Go",
        "id": "go",
        "children": [
          { "caption": "Build Package", "command": "go_build" },
          { "caption": "Run", "command": "go_run" },
          { "caption": "-" },
          { "caption": "Test Package", "command": "go_test" },
          { "caption": "Test All", "command": "go_test_all" },
          { "caption": "Test Function", "command": "go_test_function" },
          { "caption": "Benchmark", "command": "go_benchmark" },
          { "caption": "-" },
          { "caption": "Format File", "command": "go_fmt" },
          { "caption": "Fix Imports", "command": "go_imports" },
          { "caption": "Vet", "command": "go_vet" },
          { "caption": "-" },
          { "caption": "Coverage", "command": "go_coverage" },
          { "caption": "Documentation", "command": "go_doc" },
          { "caption": "Send to Playground", "command": "go_playground" },
          { "caption": "-" },
          { "caption": "Go Get Package", "command": "go_get" },
          { "caption": "Initialize Module", "command": "go_mod_init" },
          { "caption": "Mod Tidy", "command": "go_mod_tidy" },
          { "caption": "Install", "command": "go_install" },
          { "caption": "Clean", "command": "go_clean" },
          { "caption": "-" },
          { "caption": "Show Environment", "command": "go_environment" },
          { "caption": "Show Version", "command": "go_version" }
        ]
      }
    ]
  }
]
```

#### `Context.sublime-menu` (Right-click Menu)
```json
[
  {
    "caption": "Go",
    "id": "go",
    "children": [
      { "caption": "Run", "command": "go_run" },
      { "caption": "Test Function", "command": "go_test_function" },
      { "caption": "Format", "command": "go_fmt" },
      { "caption": "Fix Imports", "command": "go_imports" },
      { "caption": "Documentation", "command": "go_doc" },
      { "caption": "-" },
      { "caption": "Initialize Module", "command": "go_mod_init" }
    ]
  }
]
```

### Step 4: Install Required Go Tools

```bash
# Essential tools
go install golang.org/x/tools/cmd/goimports@latest

# Optional but recommended
go install golang.org/x/tools/cmd/godoc@latest
go install honnef.co/go/tools/cmd/staticcheck@latest
go install golang.org/x/vuln/cmd/govulncheck@latest
```

### Step 5: Restart Sublime Text

## 🚨 Troubleshooting

### "go.mod file not found" Error

**Good News:** The plugin now intelligently handles both single files and multi-file projects!

#### For Single Go Files (Hello World, etc.)
**No action needed!** The plugin automatically detects single-file programs with:
- `package main`
- `func main()`
- Only standard library imports

These files run without requiring a go.mod file.

#### For Multi-File Projects or External Dependencies
You need a Go module. Solutions:

##### Solution 1: Initialize a Module (Recommended)
Use the plugin command:
- Press `Ctrl+Shift+G, Ctrl+Shift+M` (Go Mod Init)
- Enter your module name when prompted (e.g., `github.com/username/projectname`)

Or manually:
```bash
cd /path/to/your/project
go mod init your-module-name
```

##### Solution 2: Auto-Create Module
Enable auto-creation in plugin settings:
1. Go to `Preferences > Package Settings > GoBuild > Settings`
2. Set `"auto_create_mod": true`
3. Optionally set `"default_module_name": "example.com/myproject"`

##### Solution 3: Legacy GOPATH Mode
```bash
export GOPATH=$HOME/go
mkdir -p $GOPATH/src/github.com/username/projectname
cd $GOPATH/src/github.com/username/projectname
# Place your Go files here
```

#### How the Plugin Decides
The plugin uses smart detection:
- **Single file + package main + standard library only** → No module needed
- **Multiple files or external imports** → Module required
- **Commands like `go get`, `go install`** → Always require module

### Common Issues and Solutions

#### 1. Go Command Not Found
**Error:** `'go' is not recognized as an internal or external command`

**Solutions:**
- Install Go from [golang.org](https://golang.org/dl/)
- Add Go to your PATH environment variable
- Verify with `go version` in terminal
- Restart Sublime Text after PATH changes

#### 2. goimports Not Found
**Error:** `goimports not found`

**Solution:**
```bash
go install golang.org/x/tools/cmd/goimports@latest
```

#### 3. PATH Issues in Sublime Text
**Problem:** Commands work in terminal but not in Sublime Text

**Solutions:**
- **Windows:** Add Go to System PATH, not just User PATH
- **macOS/Linux:** Add to shell profile (`.bashrc`, `.zshrc`)
```bash
export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
```
- Restart Sublime Text completely
- Check with: `Ctrl+Shift+G, Ctrl+E` (Show Environment)

#### 4. Output Panel Not Showing
**Solutions:**
- Check plugin settings: `"show_panel_on_build": true`
- Manually open: `View > Show Console`
- Use Command Palette: `View: Show Panel`

#### 5. Test Function Not Found
**Problem:** `Ctrl+Shift+G, Ctrl+F` says "No test function found"

**Solutions:**
- Ensure cursor is inside test function body
- Test functions must follow pattern: `func TestXxx(t *testing.T)`
- File must end with `_test.go`

#### 6. Import Issues
**Problem:** Imports not organizing correctly

**Solutions:**
- Install goimports: `go install golang.org/x/tools/cmd/goimports@latest`
- Enable in settings: `"use_goimports": true`
- Use `Ctrl+Shift+G, Ctrl+I` to fix imports manually

#### 7. Coverage HTML Not Opening
**Problem:** Coverage report generated but HTML doesn't open

**Solutions:**
- Check if browser is set as default for HTML files
- Manual open: `go tool cover -html=coverage.out`
- File is saved in project root as `coverage.out`

## ⚙️ Configuration

### Settings File Location
`Preferences > Package Settings > GoBuild > Settings`

### Available Settings
```json
{
  "format_on_save": false,        // Auto-format Go files on save
  "use_goimports": true,          // Use goimports instead of gofmt
  "show_panel_on_build": true,    // Show output panel automatically
  "go_executable": "go",          // Path to go binary
  "gofmt_executable": "gofmt",    // Path to gofmt binary
  "goimports_executable": "goimports", // Path to goimports binary
  "auto_create_mod": true,        // Auto-create go.mod when missing
  "default_module_name": ""       // Default module name for auto-creation
}
```

### Custom Key Bindings
Create your own shortcuts by modifying `Default.sublime-keymap`:
```json
[
  { "keys": ["f5"], "command": "go_run" },
  { "keys": ["f6"], "command": "go_test" },
  { "keys": ["ctrl+alt+f"], "command": "go_fmt" }
]
```

## 🎯 Usage Examples

### Quick Start Examples

#### 1. Simple Hello World (No Module Needed)
```go
// main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```
- Save the file as `main.go`
- Press `Ctrl+Shift+G, Ctrl+R` to run
- **No go.mod required!** Plugin detects this as a single-file program

#### 2. Multi-File Project (Module Required)
```bash
mkdir myproject
cd myproject
```

Use plugin to initialize module: `Ctrl+Shift+G, Ctrl+Shift+M`
- Enter: `github.com/username/myproject`

Create files:
```go
// main.go
package main

import (
    "fmt"
    "./utils"  // Local import - needs module
)

func main() {
    fmt.Println(utils.Greet("World"))
}
```

```go
// utils/greet.go
package utils

func Greet(name string) string {
    return "Hello, " + name + "!"
}
```

- Press `Ctrl+Shift+G, Ctrl+R` to run

#### 3. Project with External Dependencies
```go
// main.go
package main

import (
    "fmt"
    "github.com/gorilla/mux"  // External dependency
)

func main() {
    r := mux.NewRouter()
    fmt.Println("Server starting...")
}
```

1. Initialize module: `Ctrl+Shift+G, Ctrl+Shift+M`
2. Add dependency: `Ctrl+Shift+G, Ctrl+G` → Enter `github.com/gorilla/mux`
3. Run: `Ctrl+Shift+G, Ctrl+R`

#### 4. Testing Workflow
Create test file:
```go
// main_test.go
package main

import "testing"

func TestHello(t *testing.T) {
    expected := "Hello, World!"
    if result := "Hello, World!"; result != expected {
        t.Errorf("Expected %s, got %s", expected, result)
    }
}
```

- **Single file test:** Place cursor in `TestHello`, press `Ctrl+Shift+G, Ctrl+F`
- **All tests:** `Ctrl+Shift+G, Ctrl+T`
- **Coverage:** `Ctrl+Shift+G, Ctrl+C`

### Code Quality Workflow
1. **Format code:** `Ctrl+Shift+G, Ctrl+Shift+F`
2. **Fix imports:** `Ctrl+Shift+G, Ctrl+I`
3. **Run vet:** `Ctrl+Shift+G, Ctrl+V`

## 🔧 Integration with LSP-gopls

This plugin is designed to work alongside LSP-gopls:

- **LSP-gopls**: Provides IntelliSense, diagnostics, go-to-definition, etc.
- **GoBuild**: Provides build system, testing commands, and productivity tools

### Recommended Setup
1. Install LSP and LSP-gopls from Package Control
2. Install this GoBuild plugin
3. Configure both for optimal Go development

### LSP-gopls Settings
Add to your LSP settings:
```json
{
  "clients": {
    "gopls": {
      "enabled": true,
      "settings": {
        "gopls.usePlaceholders": true,
        "gopls.completeUnimported": true
      }
    }
  }
}
```

## 📋 Commands Reference

| Command | Shortcut | Description |
|---------|----------|-------------|
| `go_build` | `Ctrl+Shift+G, Ctrl+B` | Build current package |
| `go_run` | `Ctrl+Shift+G, Ctrl+R` | Run current file/package |
| `go_test` | `Ctrl+Shift+G, Ctrl+T` | Test current package |
| `go_test_all` | `Ctrl+Shift+G, Ctrl+Shift+T` | Test all packages |
| `go_test_function` | `Ctrl+Shift+G, Ctrl+F` | Test function under cursor |
| `go_benchmark` | `Ctrl+Shift+G, Ctrl+Shift+B` | Run benchmarks |
| `go_fmt` | `Ctrl+Shift+G, Ctrl+Shift+F` | Format with gofmt |
| `go_imports` | `Ctrl+Shift+G, Ctrl+I` | Fix imports |
| `go_vet` | `Ctrl+Shift+G, Ctrl+V` | Run go vet |
| `go_coverage` | `Ctrl+Shift+G, Ctrl+C` | Generate coverage |
| `go_mod_init` | `Ctrl+Shift+G, Ctrl+Shift+M` | Initialize module |
| `go_mod_tidy` | `Ctrl+Shift+G, Ctrl+M` | Clean dependencies |
| `go_get` | `Ctrl+Shift+G, Ctrl+G` | Add dependency |
| `go_install` | `Ctrl+Shift+G, Ctrl+Shift+I` | Install package |
| `go_clean` | `Ctrl+Shift+G, Ctrl+Shift+C` | Clean cache |
| `go_doc` | `Ctrl+Shift+G, Ctrl+D` | Show documentation |
| `go_playground` | `Ctrl+Shift+G, Ctrl+P` | Send to playground |
| `go_environment` | `Ctrl+Shift+G, Ctrl+E` | Show environment |
| `go_version` | `Ctrl+Shift+G, Ctrl+Shift+V` | Show version |

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Verify Go installation: `go version`
3. Check Sublime Text console: `View > Show Console`
4. Open an issue with error details and environment info

## 🙏 Acknowledgments

- Inspired by the original GoSublime package
- Built to complement LSP-gopls
- Thanks to the Go team for excellent tooling
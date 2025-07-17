# Quick Fix: "go.mod file not found" Error

## Problem
You get this error when running a single Go file:
```
go: go.mod file not found in current directory or any parent directory
```

## ✅ Immediate Solutions

### Solution 1: Use Plugin Commands (Recommended)
Instead of `Ctrl+B` (which uses `go build .`), use the plugin commands:

- **Run:** `Ctrl+Shift+G, Ctrl+R` 
- **Build:** `Ctrl+Shift+G, Ctrl+B`

These commands are smart and detect single files automatically.

### Solution 2: Use Single File Build Variant
1. Press `Ctrl+Shift+B` (Build with variants)
2. Select **"Build (Single File)"** from the list
3. This uses `go build filename.go` instead of `go build .`

### Solution 3: Manual Command
In terminal, use:
```bash
# Run single file
go run main.go

# Build single file  
go build main.go

# Build with custom output name
go build -o myprogram main.go
```

## 🔧 Understanding the Issue

### Why This Happens
- `go build .` tries to build the current directory as a package
- This requires a `go.mod` file for module-based projects
- Single files with `package main` don't need modules

### What the Plugin Should Do
The plugin should automatically detect:
- ✅ Single file with `package main` → Use `go build filename.go`
- ✅ Multiple files, same package → Use `go build .` (no module needed)
- 📦 Multiple packages or external imports → Require module

## 🚀 For Future Development

### Setting Up a Module (When Needed)
If you plan to:
- Add external dependencies
- Create multiple packages
- Share your code

Then initialize a module:
1. `Ctrl+Shift+G, Ctrl+Shift+M` (Go Mod Init)
2. Enter module name: `github.com/username/projectname`

### Example Module Structure
```
myproject/
├── go.mod
├── main.go
└── utils/
    └── helper.go
```

```go
// main.go
package main

import (
    "fmt"
    "myproject/utils"  // Module import
)

func main() {
    fmt.Println(utils.Helper())
}
```

## 🎯 Key Takeaway
**Single Go files with `package main` should work without modules!** If they don't, it's usually a tooling issue, not a Go requirement.
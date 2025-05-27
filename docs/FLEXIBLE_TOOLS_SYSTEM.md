# GP Manager - Flexible Tools System

## Overview

GP Manager now features a revolutionary flexible tools system that allows users to detach, arrange, and scale tools according to their specific workflow requirements. This system provides unprecedented customization and multi-monitor support for professional development environments.

## 🚀 Core Features

### **Detachable Tool Windows**
- **Independent Windows**: Each tool can run in its own scalable window
- **Multi-Monitor Support**: Spread tools across multiple displays
- **Custom Layouts**: Arrange tools according to your workflow
- **Persistent State**: Window positions and sizes are remembered

### **Flexible Tool Management**
- **Dock System**: Organize tools in customizable docks
- **Tab Management**: Group related tools together
- **Dynamic Arrangement**: Rearrange tools on the fly
- **Tool Registration**: Easy addition of new tools

## 🎯 Available Tools

### **Core Tools**
| Tool | Icon | Description | Detachable |
|------|------|-------------|------------|
| **Text Editor** | 📝 | Syntax highlighting editor | ✓ |
| **APK Tools** | 📱 | Android APK analysis | ✓ |
| **Archive Viewer** | 📦 | Archive file management | ✓ |
| **Hex Editor** | 🔧 | Binary file editing | ✓ |

### **Tool Capabilities**
- **Independent Scaling**: Each tool window can be resized freely
- **Always on Top**: Pin important tools above other windows
- **Full Screen**: Maximize tools for focused work
- **Custom Toolbars**: Tool-specific actions and controls

## 🎛️ User Interface

### **Main Window Layout**
```
┌─────────────────────────────────────────────────────────────┐
│ File  Edit  View  Tools  Help                              │
├─────────────────────────────────────────────────────────────┤
│ [↑] [⟳] | [←] [→] [🏠] | [Delete] | [📝] [📱] [📦] [🔧] [⧉] │
├─────────────────────────────────────────────────────────────┤
│                    │                                        │
│   File Manager     │         Tool Area                      │
│                    │  ┌─────────────────────────────────┐   │
│  [←] [→] [↑] [🏠]  │  │ + Add Dock | Layout ▼          │   │
│  [Address Bar...]  │  ├─────────────────────────────────┤   │
│                    │  │                                 │   │
│  📁 Desktop        │  │  ┌─────────────────────────┐    │   │
│  📁 Documents      │  │  │ Text Editor        [⧉] │    │   │
│  📁 Downloads      │  │  ├─────────────────────────┤    │   │
│  📁 Pictures       │  │  │                         │    │   │
│  📁 Videos         │  │  │   Editor Content        │    │   │
│                    │  │  │                         │    │   │
│                    │  │  └─────────────────────────┘    │   │
│                    │  │                                 │   │
│                    │  └─────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│ Ready                                    1 item selected    │
└─────────────────────────────────────────────────────────────┘
```

### **Detached Tool Window**
```
┌─────────────────────────────────────────────────────────────┐
│ GP Manager - Text Editor                            [─][□][×]│
├─────────────────────────────────────────────────────────────┤
│ Window  View                                                │
├─────────────────────────────────────────────────────────────┤
│ [📎 Attach] | [Tool Actions...] | [📌]                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    Tool Content                             │
│                                                             │
│                                                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Text Editor - Ready                                         │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Tool Management

### **Detaching Tools**

#### **Method 1: Menu System**
```
Tools → Detach Tools →
├── Text Editor
├── APK Tools
├── Archive Viewer
└── Hex Editor
```

#### **Method 2: Toolbar Button**
- Click the **⧉** (detach) button in the main toolbar
- Select tool from dropdown menu

#### **Method 3: Tab Context Menu**
- Right-click on tool tab
- Select "Detach to Window"

#### **Method 4: Drag & Drop** (Future Feature)
- Drag tab outside main window
- Automatically creates detached window

### **Attaching Tools**

#### **From Detached Window:**
- Click **📎 Attach** button in detached window toolbar
- Use **Window → Attach to Main Window** menu
- Keyboard shortcut: `Ctrl+Shift+A`

#### **From Main Window:**
- Tools are automatically reattached when detached window is closed
- Use dock management to reorganize attached tools

### **Window Management**

#### **Detached Window Features:**
| Feature | Description | Shortcut |
|---------|-------------|----------|
| **Always on Top** | Pin window above others | - |
| **Full Screen** | Maximize for focused work | `F11` |
| **Attach to Main** | Return to main window | `Ctrl+Shift+A` |
| **Close Window** | Hide window (can reopen) | `Ctrl+W` |

#### **Window Controls:**
- **Minimize**: Standard window minimize
- **Maximize**: Full screen on current monitor
- **Resize**: Free scaling and positioning
- **Move**: Drag to any monitor or position

## 🎨 Layout Management

### **Dock System**

#### **Dock Features:**
- **Multiple Docks**: Create unlimited tool docks
- **Flexible Arrangement**: Horizontal, vertical, or grid layouts
- **Tool Grouping**: Group related tools in same dock
- **Resizable**: Adjust dock sizes independently

#### **Dock Operations:**
```
+ Add Dock     → Create new tool dock
Layout ▼       → Choose layout style
├── Horizontal → Side-by-side arrangement
├── Vertical   → Stacked arrangement
└── Grid       → Grid-based layout
```

### **Tab Management**

#### **Tab Features:**
- **Detach Button**: Each tab has ⧉ detach button
- **Context Menu**: Right-click for options
- **Drag Reorder**: Rearrange tabs by dragging
- **Close Tabs**: Remove tools from dock

#### **Tab Context Menu:**
```
Right-click on tab →
├── Detach to Window
├── Move to Dock →
│   ├── Dock 1
│   ├── Dock 2
│   └── New Dock
└── Close Tab
```

## 🖥️ Multi-Monitor Support

### **Monitor Workflows**

#### **Development Setup:**
```
Monitor 1 (Primary)          Monitor 2 (Secondary)
┌─────────────────────┐     ┌─────────────────────┐
│   GP Manager        │     │   Text Editor       │
│   File Browser      │     │   (Detached)        │
│                     │     │                     │
│                     │     │   Code Files        │
│                     │     │                     │
└─────────────────────┘     └─────────────────────┘

Monitor 3 (Tertiary)
┌─────────────────────┐
│   Hex Editor        │
│   (Detached)        │
│                     │
│   Binary Analysis   │
│                     │
└─────────────────────┘
```

#### **Analysis Workflow:**
```
Main Monitor                 Secondary Monitor
┌─────────────────────┐     ┌─────────────────────┐
│   File Manager      │     │   APK Tools         │
│   + Archive Viewer  │     │   (Detached)        │
│                     │     │                     │
│   Browse Files      │     │   Decompile APKs    │
│                     │     │                     │
└─────────────────────┘     └─────────────────────┘
```

### **Window Persistence**
- **Position Memory**: Each tool remembers its last position
- **Size Memory**: Window dimensions are preserved
- **Monitor Assignment**: Tools reopen on correct monitor
- **State Restoration**: Always on top and other settings preserved

## ⚙️ Configuration & Settings

### **Window State Persistence**

#### **Saved Properties:**
```json
{
  "detached_window_text_editor": {
    "geometry": {
      "x": 1920,
      "y": 100,
      "width": 1200,
      "height": 800
    },
    "maximized": false,
    "always_on_top": true
  }
}
```

#### **Auto-Save Events:**
- Window resize/move
- Always on top toggle
- Window close
- Application exit

### **Tool Registration**

#### **Adding Custom Tools:**
```python
# Register new tool
window_manager.register_tool("Custom Tool", custom_widget)
tool_manager.add_tool("Custom Tool", custom_widget)

# Tool becomes detachable automatically
```

#### **Tool Requirements:**
- Must be a QWidget-based component
- Optional: Implement `get_toolbar_actions()` for custom toolbar
- Optional: Implement zoom methods for view menu integration

## 🎯 Use Cases & Workflows

### **Software Development**
1. **Main Window**: File browser and project navigation
2. **Monitor 2**: Text editor for code editing
3. **Monitor 3**: Hex editor for binary analysis
4. **Floating**: APK tools for mobile app analysis

### **Digital Forensics**
1. **Main Window**: File system navigation
2. **Detached Hex Editor**: Binary file analysis
3. **Detached Archive Viewer**: Evidence file examination
4. **Always on Top**: Notes or reference tools

### **System Administration**
1. **Primary**: File management and navigation
2. **Secondary**: Text editor for configuration files
3. **Floating**: Hex editor for system file analysis
4. **Mobile**: Archive tools for backup examination

### **Reverse Engineering**
1. **Main Display**: File browser and APK tools
2. **Secondary**: Hex editor for binary analysis
3. **Tertiary**: Text editor for notes and scripts
4. **Floating**: Archive viewer for resource extraction

## 🚀 Benefits

### **Productivity**
- **Multi-tasking**: Work with multiple tools simultaneously
- **Focus**: Dedicated windows for specific tasks
- **Efficiency**: Optimal tool arrangement for workflow
- **Flexibility**: Adapt layout to current project needs

### **Professional Features**
- **Multi-Monitor**: Full support for professional setups
- **Scalability**: Tools scale independently for optimal viewing
- **Persistence**: Layouts remembered between sessions
- **Customization**: Unlimited arrangement possibilities

### **User Experience**
- **Intuitive**: Familiar window management paradigms
- **Responsive**: Smooth window operations and scaling
- **Reliable**: Robust state management and error handling
- **Accessible**: Multiple ways to access each feature

## 🔮 Future Enhancements

### **Planned Features**
- **Drag & Drop Detachment**: Drag tabs to create windows
- **Window Snapping**: Smart window positioning
- **Layout Presets**: Save and load custom layouts
- **Tool Plugins**: Third-party tool integration
- **Workspace Management**: Multiple workspace configurations
- **Minimize to Tray**: System tray integration for tools

### **Advanced Workflows**
- **Project-based Layouts**: Different layouts per project type
- **Team Collaboration**: Share layout configurations
- **Remote Tools**: Network-based tool integration
- **Cloud Sync**: Synchronize layouts across devices

The flexible tools system transforms GP Manager into a truly professional development and analysis platform, providing the customization and multi-monitor support needed for complex workflows! 🎯✨

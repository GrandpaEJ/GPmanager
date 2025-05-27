# GP Manager - Window Controls & Save Confirmation

## Overview

GP Manager now includes comprehensive window controls and save confirmation dialogs, providing a professional desktop application experience with proper file handling safeguards.

## Window Controls Features

### Standard Window Controls
- ✅ **Minimize** - Minimize window to taskbar
- ✅ **Maximize/Restore** - Toggle between maximized and normal window state
- ✅ **Close** - Close application with save confirmation
- ✅ **Resize** - Scalable window with minimum size constraints
- ✅ **Move** - Draggable window

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+M` | Minimize window |
| `F11` | Toggle maximize/restore |
| `F11` | Toggle fullscreen mode |
| `Ctrl+Q` | Close application |
| `Ctrl+S` | Save current file |
| `Ctrl+Shift+S` | Save all files |

### Menu Integration
Window controls are accessible through:
- **View Menu** → Window controls section
- **File Menu** → Save options
- **System title bar** (default)
- **Custom title bar** (optional)

## Save Confirmation System

### Automatic Save Detection
The application automatically tracks:
- ✅ **Modified files** in text editor tabs
- ✅ **Unsaved changes** indicator in window title
- ✅ **File modification status** with visual markers (*)

### Close Confirmation Dialog
When closing the application with unsaved changes:

#### Single File Modified
```
Save changes to filename.txt?
[Save] [Discard] [Cancel]
```

#### Multiple Files Modified
```
Save changes to 3 files?

Modified files:
• file1.txt *
• file2.smali *
• file3.xml *

[Save] [Discard] [Cancel]
```

### Save Options
- **Save** - Save all modified files before closing
- **Discard** - Close without saving changes
- **Cancel** - Return to application without closing

### Tab Close Confirmation
When closing individual tabs with unsaved changes:
- Shows save confirmation for that specific file
- Offers Save/Discard/Cancel options
- Prevents accidental data loss

## Custom Title Bar (Optional)

### Features
- ✅ **Integrated window controls** (minimize, maximize, close)
- ✅ **Drag to move** window
- ✅ **Double-click to maximize**
- ✅ **Custom styling** matching application theme
- ✅ **Application icon** and title display

### Enabling Custom Title Bar
1. Go to **File** → **Preferences**
2. Navigate to **General** tab
3. Check **"Use custom title bar (requires restart)"**
4. Click **Apply** and restart the application

### Custom Title Bar Controls
- **Minimize Button** (−) - Minimizes window
- **Maximize Button** (□/❐) - Toggles maximize state
- **Close Button** (×) - Closes with save confirmation
- **Title Area** - Drag to move window, double-click to maximize

## Window State Management

### Persistent Settings
The application remembers:
- ✅ **Window size** and position
- ✅ **Maximized state**
- ✅ **Splitter positions**
- ✅ **Custom title bar preference**

### Configuration Storage
Settings are saved in `~/.gpmanager/config.json`:
```json
{
  "window_geometry": {
    "width": 1200,
    "height": 800,
    "x": 100,
    "y": 100
  },
  "window_maximized": false,
  "use_custom_titlebar": false
}
```

## Implementation Details

### Window Flags
Standard window with all controls:
```python
Qt.Window |
Qt.WindowMinimizeButtonHint |
Qt.WindowMaximizeButtonHint |
Qt.WindowCloseButtonHint
```

### Close Event Handling
```python
def closeEvent(self, event):
    if self.has_unsaved_changes():
        reply = self.show_save_confirmation()
        if reply == QMessageBox.Save:
            if self.save_all_files():
                event.accept()
            else:
                event.ignore()
        elif reply == QMessageBox.Discard:
            event.accept()
        else:  # Cancel
            event.ignore()
    else:
        event.accept()
```

### File Modification Tracking
```python
def on_file_modified(self, file_path, is_modified):
    self.unsaved_changes = is_modified
    self.update_window_title()
```

## User Experience

### Visual Indicators
- **Window Title** shows current file and modification status
- **Tab Titles** show asterisk (*) for modified files
- **Status Bar** displays file operation status

### Confirmation Dialogs
- **Clear messaging** about what will be saved/lost
- **Default to Save** to prevent accidental data loss
- **List modified files** when multiple files affected
- **Consistent styling** with application theme

### Error Handling
- **Save failures** prevent window closing
- **Permission errors** show appropriate messages
- **Graceful fallbacks** for system integration issues

## Accessibility

### Keyboard Navigation
- All window controls accessible via keyboard
- Standard shortcuts follow platform conventions
- Tab navigation through dialog elements

### Screen Reader Support
- Proper labels for all controls
- Descriptive dialog messages
- Accessible button text

## Platform Integration

### Linux Desktop Environment
- **System tray** integration (when available)
- **Window manager** compatibility
- **Desktop file** for application launcher
- **MIME type** associations for APK files

### Theme Integration
- **Dark theme** support
- **System theme** detection (future)
- **High DPI** scaling support
- **Custom styling** for better integration

## Troubleshooting

### Common Issues

#### Window Controls Not Working
- Check window flags in preferences
- Verify PyQt5 installation
- Try disabling custom title bar

#### Save Confirmation Not Appearing
- Check file modification detection
- Verify text editor integration
- Review error logs

#### Custom Title Bar Issues
- Requires restart after enabling
- May not work on all window managers
- Fallback to system title bar available

### Debug Information
Enable debug mode to see window control events:
```bash
export GPMANAGER_DEBUG=1
python3 main.py
```

## Future Enhancements

### Planned Features
- **Auto-save** functionality
- **Session restoration**
- **Multiple window** support
- **Workspace management**
- **Plugin system** for custom controls

### Customization Options
- **Title bar themes**
- **Button layouts**
- **Confirmation preferences**
- **Save behavior settings**

## Conclusion

The window controls and save confirmation system provides a professional, user-friendly experience that prevents data loss while maintaining familiar desktop application behavior. The modular design allows for easy customization and future enhancements.

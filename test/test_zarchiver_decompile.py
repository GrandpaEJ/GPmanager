#!/usr/bin/env python3
"""
Simple test script to verify ZArchiver APK decompilation
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_apk_exists():
    """Test if the ZArchiver APK exists"""
    apk_path = "/home/grandpa/Downloads/ZArchiver_1.0.10_APKPure.apk"
    
    print("=" * 60)
    print("ZArchiver APK Decompile Test")
    print("=" * 60)
    print(f"APK Path: {apk_path}")
    
    if Path(apk_path).exists():
        apk_size = Path(apk_path).stat().st_size
        print(f"✅ APK file found!")
        print(f"📊 File size: {apk_size:,} bytes ({apk_size / 1024 / 1024:.2f} MB)")
        return True, apk_path
    else:
        print("❌ APK file not found!")
        print("\n💡 Please ensure the ZArchiver APK is downloaded to:")
        print(f"   {apk_path}")
        return False, apk_path

def test_dependencies():
    """Test if dependencies are available"""
    print("\n🔍 Checking Dependencies:")
    print("-" * 30)
    
    dependencies = {
        'java': 'java -version',
        'apktool': 'apktool --version',
        'aapt': 'aapt version'
    }
    
    all_ok = True
    
    for name, command in dependencies.items():
        try:
            import subprocess
            result = subprocess.run(command.split(), 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {name}: Available")
            else:
                print(f"❌ {name}: Not working (return code: {result.returncode})")
                all_ok = False
        except FileNotFoundError:
            print(f"❌ {name}: Not found")
            all_ok = False
        except Exception as e:
            print(f"⚠️ {name}: Error checking ({str(e)})")
            all_ok = False
    
    return all_ok

def test_apktool_command(apk_path):
    """Test APKTool command directly"""
    print("\n🔨 Testing APKTool Command:")
    print("-" * 30)
    
    if not Path(apk_path).exists():
        print("❌ APK file not found, skipping command test")
        return False
    
    # Create a temporary output directory
    output_dir = Path("/tmp/zarchiver_test_decompile")
    
    try:
        import subprocess
        import shutil
        
        # Clean up any previous test
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        # Test command
        cmd = ['apktool', 'd', apk_path, '-o', str(output_dir)]
        print(f"🚀 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ APKTool decompile command succeeded!")
            
            # Check output directory
            if output_dir.exists():
                files = list(output_dir.rglob('*'))
                print(f"📁 Output directory created with {len(files)} files/folders")
                
                # Show some key files
                key_files = ['AndroidManifest.xml', 'apktool.yml', 'smali', 'res']
                for key_file in key_files:
                    key_path = output_dir / key_file
                    if key_path.exists():
                        print(f"   ✅ {key_file}")
                    else:
                        print(f"   ❌ {key_file} (missing)")
                
                # Clean up
                shutil.rmtree(output_dir)
                print("🗑️ Cleaned up test output")
                return True
            else:
                print("❌ Output directory not created")
                return False
        else:
            print(f"❌ APKTool command failed (return code: {result.returncode})")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ APKTool command timed out (>120 seconds)")
        return False
    except Exception as e:
        print(f"💥 Error running APKTool: {str(e)}")
        return False

def main():
    """Main test function"""
    print("Starting ZArchiver APK decompile test...\n")
    
    # Test 1: Check if APK exists
    apk_exists, apk_path = test_apk_exists()
    
    # Test 2: Check dependencies
    deps_ok = test_dependencies()
    
    # Test 3: Test APKTool command (only if APK exists and deps are OK)
    if apk_exists and deps_ok:
        cmd_ok = test_apktool_command(apk_path)
    else:
        cmd_ok = False
        print("\n⚠️ Skipping APKTool command test (missing APK or dependencies)")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"APK File:      {'✅ Found' if apk_exists else '❌ Missing'}")
    print(f"Dependencies:  {'✅ OK' if deps_ok else '❌ Missing'}")
    print(f"APKTool Test:  {'✅ Passed' if cmd_ok else '❌ Failed/Skipped'}")
    
    if apk_exists and deps_ok and cmd_ok:
        print("\n🎉 All tests passed! ZArchiver APK decompilation should work.")
        print("\n💡 You can now:")
        print("   1. Run MT Manager Linux: python main.py")
        print("   2. Go to APK Tools tab")
        print("   3. Browse and select the ZArchiver APK")
        print("   4. Click 'Decompile APK'")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        
        if not apk_exists:
            print("\n📥 To get the ZArchiver APK:")
            print("   1. Download from APKPure or similar site")
            print("   2. Save to /home/grandpa/Downloads/ZArchiver_1.0.10_APKPure.apk")
        
        if not deps_ok:
            print("\n🔧 To install dependencies:")
            print("   1. Run MT Manager Linux: python main.py")
            print("   2. Go to APK Tools → Setup tab")
            print("   3. Click 'Auto Install All'")
            print("   Or manually: sudo apt install default-jdk apktool aapt")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

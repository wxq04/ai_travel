"""
Flask 应用启动器
自动处理 WeasyPrint DLL 加载问题，确保应用正常启动
"""
import os
import sys
import shutil
from pathlib import Path

# ==================== 核心：DLL 加载处理 ====================
def setup_dll_environment():
    """
    设置 Windows DLL 加载环境
    这是解决 WeasyPrint 加载失败的关键
    """
    dll_dirs = [
        r"D:\packet\MSYS2\mingw64\bin",
        r"D:\packet\MSYS2\ucrt64\bin",
        r"D:\packet\MSYS2\clang64\bin",
        r"C:\msys64\mingw64\bin",
        r"C:\msys64\ucrt64\bin",
    ]
    
    found_dll = None
    for dll_dir in dll_dirs:
        dll_path = os.path.join(dll_dir, 'libgobject-2.0-0.dll')
        if os.path.exists(dll_path):
            found_dll = dll_dir
            print(f"[INFO] 找到 GTK DLL: {dll_path}")
            break
    
    if found_dll:
        # 设置环境变量
        os.environ['WEASYPRINT_DLL_DIRECTORIES'] = found_dll
        
        # Python 3.8+ 需要添加 DLL 目录
        if hasattr(os, 'add_dll_directory'):
            try:
                os.add_dll_directory(found_dll)
                print(f"[INFO] DLL 目录已注册: {found_dll}")
            except Exception as e:
                print(f"[WARNING] 注册 DLL 目录失败: {e}")
        
        # 复制关键 DLL 到 weasyprint 包目录
        try:
            weasyprint_pkg = os.path.join(sys.prefix, 'Lib', 'site-packages', 'weasyprint')
            if os.path.exists(weasyprint_pkg):
                # WeasyPrint 需要的核心 DLL 列表
                required_dlls = [
                    'libgobject-2.0-0.dll',
                    'libglib-2.0-0.dll',
                    'libgio-2.0-0.dll',
                    'libgdk-3-0.dll',
                    'libgdk_pixbuf-2.0-0.dll',
                    'libpango-1.0-0.dll',
                    'libpangocairo-1.0-0.dll',
                    'libcairo-2.dll',
                    'libfontconfig-1.dll',
                    'libfreetype-6.dll',
                ]
                
                copied = []
                for dll_name in required_dlls:
                    src = os.path.join(found_dll, dll_name)
                    dst = os.path.join(weasyprint_pkg, dll_name)
                    if os.path.exists(src) and not os.path.exists(dst):
                        try:
                            shutil.copy2(src, dst)
                            copied.append(dll_name)
                        except Exception:
                            pass
                
                if copied:
                    print(f"[INFO] 已复制 {len(copied)} 个 DLL 到 weasyprint 目录")
        except Exception as e:
            print(f"[WARNING] 复制 DLL 失败: {e}")
        
        return True
    else:
        print("[WARNING] 未找到 MSYS2/MinGW DLL，PDF 功能将不可用")
        return False

# 在导入任何可能依赖 GTK 的模块之前执行
setup_dll_environment()

# ==================== 应用启动 ====================
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app import create_app

if __name__ == '__main__':
    try:
        app = create_app('development')
        
        print("\n" + "="*50)
        print("  旅行规划师应用已成功启动!")
        print("  访问地址: http://127.0.0.1:5000")
        print("  按 Ctrl+C 停止服务")
        print("="*50 + "\n")
        
        app.run(host='127.0.0.1', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n应用已停止")
    except Exception as e:
        print(f"\n[ERROR] 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        print("\n请确保:")
        print("  1. 数据库已初始化 (python init_db.py)")
        print("  2. 所有依赖已安装 (pip install -r requirements.txt)")
        input("\n按 Enter 键退出...")
        sys.exit(1)

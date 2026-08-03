import os
import sys
import ctypes

# ==================== WeasyPrint DLL 设置 ====================
# 必须在任何 GTK/Pango 相关模块加载前设置
def setup_weasyprint_dll_path():
    """
    设置 WeasyPrint 所需的 DLL 路径。
    必须在导入 weasyprint 或任何 GTK 相关模块之前调用。
    """
    # 可能的 MSYS2/MinGW 路径
    possible_paths = [
        r"D:\packet\MSYS2\mingw64\bin",
        r"D:\packet\MSYS2\ucrt64\bin",
        r"D:\packet\MSYS2\clang64\bin",
        r"C:\msys64\mingw64\bin",
        r"C:\msys64\ucrt64\bin",
        r"C:\msys64\clang64\bin",
    ]
    
    # 如果环境变量已设置，直接使用
    dll_dirs_env = os.environ.get('WEASYPRINT_DLL_DIRECTORIES', '')
    if dll_dirs_env:
        possible_paths.insert(0, dll_dirs_env)
    
    # 检查每个路径
    for path in possible_paths:
        gobject_dll = os.path.join(path, 'libgobject-2.0-0.dll')
        if os.path.exists(gobject_dll):
            print(f"[INFO] 找到 WeasyPrint DLL: {gobject_dll}")
            
            # Python 3.8+ Windows: 添加 DLL 目录
            if hasattr(os, 'add_dll_directory'):
                try:
                    os.add_dll_directory(path)
                    print(f"[INFO] 已添加 DLL 目录: {path}")
                except Exception as e:
                    print(f"[WARNING] 添加 DLL 目录失败: {e}")
            
            # 设置环境变量（作为备用）
            os.environ['WEASYPRINT_DLL_DIRECTORIES'] = path
            
            # 尝试将 DLL 复制到 Python 目录
            python_dll_dir = os.path.join(sys.prefix, 'Lib', 'site-packages', 'weasyprint')
            if os.path.exists(python_dll_dir):
                try:
                    import shutil
                    dll_name = 'libgobject-2.0-0.dll'
                    src_dll = os.path.join(path, dll_name)
                    dst_dll = os.path.join(python_dll_dir, dll_name)
                    if not os.path.exists(dst_dll):
                        shutil.copy2(src_dll, dst_dll)
                        print(f"[INFO] DLL 已复制到: {dst_dll}")
                except Exception as e:
                    print(f"[WARNING] 复制 DLL 失败: {e}")
            
            return True
    
    print("[WARNING] 未找到 WeasyPrint 所需的 DLL 文件，PDF 功能可能不可用")
    return False

# 立即执行 DLL 设置（在任何其他导入之前）
setup_weasyprint_dll_path()

# ==================== Flask 应用启动 ====================
# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

from app import create_app

if __name__ == '__main__':
    app = create_app('development')
    print("\n" + "="*50)
    print("旅行规划师应用已启动")
    print("访问地址: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(host='127.0.0.1', port=5000, debug=False)

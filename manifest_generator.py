#manifest_generator.py

import os, hashlib, json

# Change this to point to the 'dist' folder directly 
# since your exe is at C:\Source Codes\AstroBasics-dist\dist\AstroBasics.exe
BUILD_DIR = os.path.abspath("dist\\AstroBasics") 
OUTPUT_FILE = os.path.join(BUILD_DIR, "manifest.json")

EXCLUDE_DIRS = [
    'update_cache', 'autosave', 'analysis_export', 'created chart exports',
    'saves', '__pycache__']

EXCLUDE_FILES = ['manifest.json','education_weights_config.json','csi_weights_prefs.json', 
    'life_curve_prefs.json','muhurta_advanced_prefs.json',
    'custom_astro_rules.db','.just_updated',
    'custom_astro_rules.db-shm','custom_astro_rules.db-wal','custom_astro_rules.db',
    'icon.ico', 'astro_settings.json', 'custom_vargas.json',
    'apply_update.bat', 'apply_update.sh', 
    '.hash_cache.json', 'unins000.exe', 'unins000.dat', 'custom_astro_rules.json']

# 🛡️ Prevent Nuitka build artifacts or backups from ever entering the manifest
EXCLUDE_EXTENSIONS = ['.pyc', '.pyi', '.c', '.bak']


def get_file_hash(filepath):
    """
    The Universal Hash: Immune to Git line-ending changes and IDE auto-formatting.
    Dynamically separates text from binary cleanly.
    """
    if not os.path.exists(filepath):
        return None
        
    hasher = hashlib.sha256()
    
    try:
        # 1. Quick sniff test: Read first 8KB to check for null bytes
        is_binary = False
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:
                is_binary = True
                
        if is_binary:
            # 2a. PURE BINARY: Process large files safely in memory chunks
            with open(filepath, 'rb') as f:
                for buf in iter(lambda: f.read(65536), b''):
                    hasher.update(buf)
        else:
            # 2b. PURE TEXT: Read into memory and forcibly normalize to UNIX standard
            with open(filepath, 'rb') as f:
                content = f.read()
                
            # Secondary safeguard: if a null byte exists later in the file
            if b'\x00' in content:
                hasher.update(content)
            else:
                # Strip all Windows carriage returns (\r) and trailing whitespace/newlines
                # This perfectly normalizes the file regardless of Git core.autocrlf settings
                content = content.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
                content = content.rstrip() 
                hasher.update(content)
                
    except Exception:
        return None
        
    return hasher.hexdigest()

def build_manifest():
    base_dir = BUILD_DIR
    
    if not os.path.exists(base_dir):
        print(f"Error: Could not find '{base_dir}'. Run PyInstaller first!")
        return

    print("=== AstroBasics Manifest Generator ===")
    version = input("Enter the new version number (e.g., 1.0.0): ").strip()
    if not version:
        print("Error: Version number cannot be empty. Aborting.")
        return

    # --- Read Changelog from updates_info.py ---
    var_name = "v" + version.replace(".", "_")
    changelog = "Bug fixes and performance improvements."
    
    try:
        import updates_info
        if hasattr(updates_info, var_name):
            changelog = getattr(updates_info, var_name).strip()
            print(f"\n[+] Successfully loaded styles from updates_info.py ({var_name})")
        else:
            print(f"\n[-] Variable '{var_name}' not found in updates_info.py. Using default message.")
    except ImportError:
        print("\n[-] updates_info.py not found. Using default message.")

    manifest = {
        "version": version,
        "changelog": changelog,
        "files": {}
    }
    
    stats = {"c_binaries": 0, "raw_python": 0, "other": 0}
    
    print("\nScanning files...")
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file in EXCLUDE_FILES or any(file.endswith(ext) for ext in EXCLUDE_EXTENSIONS):
                continue
                
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, base_dir)
            rel_path = rel_path.replace("\\", "/") 
            
            # Analytics Tracking
            if file.endswith((".pyd", ".so", ".dll")):
                stats["c_binaries"] += 1
            elif file.endswith(".py"):
                stats["raw_python"] += 1
            else:
                stats["other"] += 1
            
            manifest["files"][rel_path] = get_file_hash(filepath)
            
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4)
        
    print(f"\nSuccess! Generated {OUTPUT_FILE} for Version {version}")
    print("-" * 40)
    print("📦 BUILD SECURITY AUDIT:")
    print(f"   Native C-Binaries (.pyd/.so/.dll): {stats['c_binaries']}")
    print(f"   Raw Python Scripts (.py):          {stats['raw_python']}")
    print(f"   Other Assets/Data:                 {stats['other']}")
    print("-" * 40)
    
    if stats["raw_python"] > 0:
        print("\n⚠️  WARNING: Raw .py files detected in the build directory!")
        print("    If you used the Hybrid Nuitka Builder, ensure these aren't sensitive source code files.")
    
    print(f"\nTotal Files tracked: {len(manifest['files'])}")
    print("Upload this directory to GitHub to push the update live.")

if __name__ == "__main__":
    build_manifest()
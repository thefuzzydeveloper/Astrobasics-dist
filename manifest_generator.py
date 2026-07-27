# manifest_generator.py

import os, hashlib, json, base64

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print("[!] Warning: 'cryptography' library not found. Install it via 'pip install cryptography'.")

KEYS_DIR = r"F:\Gaming\Godot\Requirements\WindowsExport\keys"
PRIV_KEY_PATH = os.path.join(KEYS_DIR, "ed25519_private.pem")
PUB_KEY_PATH = os.path.join(KEYS_DIR, "ed25519_public.pem")

def get_or_generate_private_key():
    """Loads existing Ed25519 key pair or creates a new pair if missing."""
    os.makedirs(KEYS_DIR, exist_ok=True)
    if os.path.exists(PRIV_KEY_PATH):
        with open(PRIV_KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    
    print(f"[+] Key pair not found in '{KEYS_DIR}'. Generating new Ed25519 key pair...")
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    with open(PRIV_KEY_PATH, "wb") as f:
        f.write(priv_bytes)
    with open(PUB_KEY_PATH, "wb") as f:
        f.write(pub_bytes)

    print(f"[+] Keys saved to:\n    Private: {PRIV_KEY_PATH}\n    Public:  {PUB_KEY_PATH}")
    return private_key

def sign_manifest_dict(manifest_data):
    """Signs the canonical JSON byte structure and inserts the base64 signature."""
    private_key = get_or_generate_private_key()
    manifest_data.pop("signature", None)
    canonical_bytes = json.dumps(manifest_data, sort_keys=True).encode('utf-8')
    sig = private_key.sign(canonical_bytes)
    manifest_data["signature"] = base64.b64encode(sig).decode('utf-8')
    return manifest_data

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
    '.hash_cache.json', 'unins000.exe', 'unins000.dat', 'custom_astro_rules.json',
    'voting_info.py', 'updates_info.py']

EXCLUDE_EXTENSIONS = ['.pyc', '.pyi', '.c', '.bak']

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
        
    hasher = hashlib.sha256()
    
    try:
        is_binary = False
        with open(filepath, 'rb') as f:
            chunk = f.read(8192)
            if b'\x00' in chunk:
                is_binary = True
                
        if is_binary:
            with open(filepath, 'rb') as f:
                for buf in iter(lambda: f.read(65536), b''):
                    hasher.update(buf)
        else:
            with open(filepath, 'rb') as f:
                content = f.read()
                
            if b'\x00' in content:
                hasher.update(content)
            else:
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

    # Create the dynamic variable target (e.g., "1.6.0" -> "v1_6_0")
    var_name = "v" + version.replace(".", "_")
    changelog = "Bug fixes and performance improvements."
    
    # 1. Fetch Changelog
    try:
        import updates_info
        if hasattr(updates_info, var_name):
            changelog = getattr(updates_info, var_name).strip()
            print(f"\n[+] Successfully loaded changelog from updates_info.py ({var_name})")
        else:
            print(f"\n[-] Variable '{var_name}' not found in updates_info.py. Using default changelog.")
    except ImportError:
        print("\n[-] updates_info.py not found. Using default changelog.")

    manifest = {
        "version": version,
        "changelog": changelog,
        "files": {}
    }
    
    # 2. Fetch Version-Specific Voting Data
    try:
        import voting_info
        if hasattr(voting_info, var_name):
            v_data = getattr(voting_info, var_name)
            manifest["voting"] = {
                "id": v_data.get("id", f"poll_{var_name}"),
                "title": v_data.get("title", "Please cast your vote:"),
                "options": v_data.get("options", {"1": "Yes", "2": "No"})
            }
            print(f"[+] Voting Module [{manifest['voting']['id']}] added to manifest for {version}.")
        else:
            print(f"[-] No voting data found for '{var_name}' in voting_info.py. Skipping voting block.")
    except ImportError:
        print("[-] voting_info.py not found. Skipping voting block.")
        
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
            
            if file.endswith((".pyd", ".so", ".dll")):
                stats["c_binaries"] += 1
            elif file.endswith(".py"):
                stats["raw_python"] += 1
            else:
                stats["other"] += 1
            
            manifest["files"][rel_path] = get_file_hash(filepath)
            
    # Sign the manifest digitally before saving
    manifest = sign_manifest_dict(manifest)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4)
        
    print(f"\nSuccess! Generated and Digitally Signed {OUTPUT_FILE} for Version {version}")
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
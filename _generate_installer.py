# _generate_installer.py
import subprocess, sys, os, time, itertools, math, threading, shutil, json, re, uuid
from pathlib import Path

# Windows console virtual terminal support
if os.name == 'nt':
    os.system('')

# =============================================================================
# AESTHETICS & UI CONSTANTS
# =============================================================================
RESET   = "\033[0m"
GREEN   = "\033[92m"
RED     = "\033[91m"
YELLOW  = "\033[93m"
CYAN    = "\033[96m"
MAGENTA = "\033[95m"

class UIAesthetics:
    @staticmethod
    def format_time(seconds):
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    @staticmethod
    def gradient_bar(bar):
        colors = ["\033[38;5;21m","\033[38;5;27m","\033[38;5;33m","\033[38;5;39m","\033[38;5;45m","\033[38;5;51m"]
        return "".join(f"{colors[int((i / max(1, len(bar))) * (len(colors) - 1))]}{ch}" for i, ch in enumerate(bar)) + RESET

    @staticmethod
    def run_with_progress_bar(command, engine_name, cwd=None, step_info=None):
        prefix = f"[{step_info}]" if step_info else "[*]"
        print(f"\n{CYAN}{prefix} Initializing {engine_name} task...{RESET}")
        kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {}
        try:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                encoding='utf-8', 
                errors='replace', 
                cwd=cwd, 
                **kwargs
            )

            spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            spinner_cycle = itertools.cycle(spinners)
            shades = ["░", "▒", "▓", "█"]

            log_buffer = []
            current_activity = ["Compiling WixSharp assets..."]
            start_time = time.time()
            tick = 0

            def read_output():
                for line in process.stdout:
                    cleaned_line = line.strip()
                    if cleaned_line:
                        log_buffer.append(cleaned_line)
                        current_activity[0] = cleaned_line
                    if len(log_buffer) > 100:
                        log_buffer.pop(0)

            output_thread = threading.Thread(target=read_output, daemon=True)
            output_thread.start()

            while process.poll() is None:
                elapsed = time.time() - start_time
                time_str = UIAesthetics.format_time(elapsed)
                term_cols = shutil.get_terminal_size((80, 20)).columns
                spinner_char = next(spinner_cycle)

                bar_width = 25
                prefix_visible = f" {spinner_char} [{engine_name}] ["
                suffix_visible = f"] {time_str} | Trace: "
                fixed_len = len(prefix_visible) + bar_width + len(suffix_visible)

                if fixed_len >= term_cols:
                    bar_width = max(10, term_cols - len(prefix_visible) - len(suffix_visible) - 6)
                    fixed_len = len(prefix_visible) + bar_width + len(suffix_visible)

                wave = [int((1 + math.sin(tick / 3.0 + j * 0.35)) * 1.5) for j in range(bar_width)]
                raw_bar = "".join(shades[min(3, max(0, w))] for w in wave)
                colored_bar = UIAesthetics.gradient_bar(raw_bar)

                max_activity_len = term_cols - fixed_len - 4
                if max_activity_len > 5:
                    raw_activity = current_activity[0]
                    activity_text = ("..." + raw_activity[-(max_activity_len - 3):]) if len(raw_activity) > max_activity_len else raw_activity.ljust(max_activity_len)
                    full_line = f"\r{MAGENTA} {spinner_char} {CYAN}[{engine_name}] [{colored_bar}] {YELLOW}{time_str} {RESET}| {GREEN}Trace: {activity_text}{RESET}\033[K"
                else:
                    full_line = f"\r{MAGENTA} {spinner_char} {CYAN}[{engine_name}] [{colored_bar}] {YELLOW}{time_str}{RESET}\033[K"

                sys.stdout.write(full_line)
                sys.stdout.flush()
                time.sleep(0.04)
                tick += 1

            process.wait()
            output_thread.join(timeout=0.2)
            sys.stdout.write("\r" + " " * term_cols + "\r")
            sys.stdout.flush()

            if process.returncode == 0:
                print(f"{GREEN}[✔] Success: {engine_name} task complete! Total duration: {UIAesthetics.format_time(time.time() - start_time)}{RESET}")
                return True
            else:
                print(f"\n{RED}[✘] Critical Failure in {engine_name} (Exit Code {process.returncode})\n{'-'*60}\n" + "\n".join(log_buffer[-30:]) + f"\n{'-'*60}{RESET}")
                return False
        except Exception as e:
            print(f"\n[ERROR] Pipeline tracking error: {e}")
            return False

    @staticmethod
    def trigger_gui_folder_selector(title_text, initial_dir):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected = filedialog.askdirectory(title=title_text, initialdir=initial_dir)
            root.destroy()
            return selected if selected else None
        except Exception:
            return None

    @staticmethod
    def trigger_gui_file_selector(title_text, initial_dir, filetypes):
        try:
            import tkinter as tk
            from tkinter import filedialog
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected = filedialog.askopenfilename(title=title_text, initialdir=initial_dir, filetypes=filetypes)
            root.destroy()
            return selected if selected else None
        except Exception:
            return None

# =============================================================================
# SMART AUTO-DETECTION ENGINE
# =============================================================================
def scan_existing_inno_script(iss_path="installer_script.iss"):
    """Extracts metadata and registered extensions from legacy Inno scripts if present."""
    data = {"APP_NAME": None, "APP_VERSION": None, "APP_PUBLISHER": None, "MAIN_EXE": None, "EXTENSIONS": []}
    if not Path(iss_path).exists():
        return data

    try:
        with open(iss_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        name_match = re.search(r'#define\s+MyAppName\s+"([^"]+)"', content)
        if name_match: data["APP_NAME"] = name_match.group(1)

        ver_match = re.search(r'#define\s+MyAppVersion\s+"([^"]+)"', content)
        if ver_match: data["APP_VERSION"] = ver_match.group(1)

        pub_match = re.search(r'#define\s+MyAppPublisher\s+"([^"]+)"', content)
        if pub_match: data["APP_PUBLISHER"] = pub_match.group(1)

        exe_match = re.search(r'#define\s+MyAppExeName\s+"([^"]+)"', content)
        if exe_match: data["MAIN_EXE"] = exe_match.group(1)

        # Harvest file extensions from registry blocks
        ext_matches = re.findall(r'Subkey:\s*"Software\\Classes\\\.([a-zA-Z0-9_]+)"', content)
        for ext in ext_matches:
            if ext not in data["EXTENSIONS"]:
                data["EXTENSIONS"].append(ext)
    except Exception:
        pass
    return data

def auto_detect_environment():
    root_dir = Path.cwd().resolve()
    folder_name = root_dir.name
    
    # 1. Parse existing ISS if available for smart defaults
    iss_data = scan_existing_inno_script()

    # 2. Defaults lookup
    detected_app_name = iss_data["APP_NAME"] or folder_name.replace(" Latest", "").replace("-", " ").strip()
    detected_version = iss_data["APP_VERSION"] or "1.0.0"
    detected_publisher = iss_data["APP_PUBLISHER"] or "The Developer"

    # 3. Locate Target Payload Folder
    detected_payload = None
    common_payloads = [
        root_dir / "dist" / detected_app_name.replace(" ", ""),
        root_dir / "dist" / detected_app_name,
        root_dir / "dist"
    ]
    for p in common_payloads:
        if p.exists() and p.is_dir():
            detected_payload = str(p)
            break
    if not detected_payload:
        detected_payload = str(root_dir / "dist")

    # 4. Locate Main EXE
    detected_exe = iss_data["MAIN_EXE"]
    if not detected_exe and detected_payload and Path(detected_payload).exists():
        exes = [f.name for f in Path(detected_payload).glob("*.exe") if not f.name.lower().startswith("uninstall")]
        if exes:
            detected_exe = exes[0]

    # 5. Locate Icon & License
    detected_icon = str(root_dir / "icon.ico") if (root_dir / "icon.ico").exists() else None
    detected_license = str(root_dir / "license.txt") if (root_dir / "license.txt").exists() else None

    return {
        "APP_NAME": detected_app_name,
        "APP_VERSION": detected_version,
        "APP_PUBLISHER": detected_publisher,
        "TARGET_DIR": detected_payload,
        "MAIN_EXE": detected_exe or "main.exe",
        "ICON_FILE": detected_icon,
        "LICENSE_FILE": detected_license,
        "OUTPUT_INSTALLER": f"{detected_app_name.lower().replace(' ', '_')}_installer.exe",
        "EXTENSIONS": iss_data["EXTENSIONS"] or ["milan", "astrobasic", "astroanalysis", "astroresearch", "astrocomparison"],
        "SECONDARY_SHORTCUTS": []
    }

# =============================================================================
# CODE GENERATORS FOR WIXSHARP (100% MIT, EMBEDDED WIX COMPILER)
# =============================================================================
def generate_wixsharp_csproj(project_dir):
    """
    Generates net472 C# project targeting WixSharp with self-contained WixSharp.wix.bin.
    Explicitly targets x86 architecture required by the WiX Bootstrapper engine.
    """
    content = """<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net472</TargetFramework>
    <Platform>x86</Platform>
    <PlatformTarget>x86</PlatformTarget>
    <Platforms>x86</Platforms>
    <WixLocation>$(USERPROFILE)\\.nuget\\packages\\wixsharp.wix.bin\\3.14.1\\tools\\bin</WixLocation>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="WixSharp" Version="1.26.0" />
    <PackageReference Include="WixSharp.wix.bin" Version="3.14.1" />
  </ItemGroup>

</Project>
"""
    with open(project_dir / "Installer.csproj", "w", encoding="utf-8") as f:
        f.write(content)

def create_raw_bmp_file(filepath, width, height, color_rgb=(255, 255, 255), sidebar_width=0, sidebar_rgb=(30, 41, 59)):
    """Generates an uncompressed 24-bit Windows Bitmap without external dependencies."""
    import struct
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    image_size = (row_bytes + padding) * height
    file_size = 54 + image_size

    file_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    info_header = struct.pack('<IIIHHIIIIII', 40, width, height, 1, 24, 0, image_size, 2835, 2835, 0, 0)

    with open(filepath, 'wb') as f:
        f.write(file_header)
        f.write(info_header)
        pad_bytes = b'\x00' * padding
        for _ in range(height):
            row = bytearray()
            for x in range(width):
                rgb = sidebar_rgb if x < sidebar_width else color_rgb
                row.extend([rgb[2], rgb[1], rgb[0]])  # BGR order
            row.extend(pad_bytes)
            f.write(row)

def prepare_installer_assets(project_dir, cfg):
    """Creates formatted RTF terms and installer UI bitmaps."""
    # 1. Generate license.rtf detailing file associations, shortcuts, and license terms
    license_rtf_path = project_dir / "license.rtf"
    raw_license_text = ""
    if cfg.get('LICENSE_FILE') and Path(cfg['LICENSE_FILE']).exists():
        try:
            with open(cfg['LICENSE_FILE'], 'r', encoding='utf-8', errors='ignore') as f:
                raw_license_text = f.read()
        except Exception:
            pass

    if not raw_license_text.strip():
        raw_license_text = (
            f"End User License Agreement for {cfg['APP_NAME']}\n\n"
            f"Copyright (c) {cfg['APP_PUBLISHER']}. All rights reserved.\n\n"
            "Redistribution and use in binary and source forms are permitted under the terms "
            "established by the publisher."
        )

    ext_lines = "\\par ".join([f"\\bullet  *.{e.lstrip('.')} - {cfg['APP_NAME']} {e.capitalize()} File" for e in cfg.get('EXTENSIONS', [])])
    escaped_body = raw_license_text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}').replace('\n', '\\par\n')

    rtf_content = (
        "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033"
        "{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}{\\f1\\fnil\\fcharset0 Calibri;}}"
        "{\\colortbl ;\\red15\\green23\\blue42;\\red51\\green65\\blue85;\\red37\\green99\\blue235;}"
        f"\\viewkind4\\uc1\\pard\\cf1\\b\\f0\\fs22 {cfg['APP_NAME']} Installation & License Agreement\\b0\\fs18\\par"
        f"\\cf2\\f1\\fs18 Version: {cfg['APP_VERSION']} | Publisher: {cfg['APP_PUBLISHER']}\\par"
        "\\cf3\\b ____________________________________________________________________\\b0\\cf2\\par\\par"
        "\\b Configured File Associations:\\b0\\par\n"
        f"{ext_lines}\\par\\par"
        "\\b Desktop & Start Menu Shortcuts:\\b0\\par"
        "\\bullet  Desktop Shortcut: A shortcut will be automatically created on your Desktop.\\par"
        "\\bullet  Start Menu Shortcut: An application entry will be placed in your Start Menu.\\par\\par"
        "\\b License Terms:\\b0\\par\n"
        f"{escaped_body}\\par\n}}"
    )
    with open(license_rtf_path, "w", encoding="utf-8") as f:
        f.write(rtf_content)

    # 2. Generate UI Bitmaps (Dialog 493x312, Banner 493x58, Logo 64x64)
    dialog_bmp = project_dir / "dialog.bmp"
    banner_bmp = project_dir / "banner.bmp"
    logo_bmp = project_dir / "logo.bmp"

    create_raw_bmp_file(dialog_bmp, 493, 312, color_rgb=(255, 255, 255), sidebar_width=164, sidebar_rgb=(30, 41, 59))
    create_raw_bmp_file(banner_bmp, 493, 58, color_rgb=(248, 250, 252), sidebar_width=0)
    create_raw_bmp_file(logo_bmp, 64, 64, color_rgb=(255, 255, 255))

    # Composite icon onto bitmaps if PIL is available
    if cfg.get('ICON_FILE') and Path(cfg['ICON_FILE']).exists():
        try:
            from PIL import Image
            with Image.open(cfg['ICON_FILE']) as ico:
                ico_rgba = ico.convert("RGBA")

                # Logo bitmap (64x64)
                logo_img = Image.new("RGB", (64, 64), (255, 255, 255))
                ico_resized_64 = ico_rgba.resize((56, 56), Image.Resampling.LANCZOS)
                logo_img.paste(ico_resized_64, (4, 4), mask=ico_resized_64.split()[3])
                logo_img.save(str(logo_bmp), "BMP")

                # Dialog bitmap (493x312 with centered icon on sidebar)
                with Image.open(str(dialog_bmp)) as d_img:
                    ico_resized_96 = ico_rgba.resize((96, 96), Image.Resampling.LANCZOS)
                    d_img.paste(ico_resized_96, (34, 80), mask=ico_resized_96.split()[3])
                    d_img.save(str(dialog_bmp), "BMP")

                # Banner bitmap (493x58 with icon on right header)
                with Image.open(str(banner_bmp)) as b_img:
                    ico_resized_48 = ico_rgba.resize((48, 48), Image.Resampling.LANCZOS)
                    b_img.paste(ico_resized_48, (435, 5), mask=ico_resized_48.split()[3])
                    b_img.save(str(banner_bmp), "BMP")
        except Exception:
            pass

    return str(license_rtf_path), str(dialog_bmp), str(banner_bmp), str(logo_bmp)

def create_raw_bmp_file(filepath, width, height, color_rgb=(255, 255, 255), sidebar_width=0, sidebar_rgb=(30, 41, 59)):
    """Generates an uncompressed 24-bit Windows Bitmap without external dependencies."""
    import struct
    row_bytes = width * 3
    padding = (4 - (row_bytes % 4)) % 4
    image_size = (row_bytes + padding) * height
    file_size = 54 + image_size

    file_header = struct.pack('<2sIHHI', b'BM', file_size, 0, 0, 54)
    info_header = struct.pack('<IIIHHIIIIII', 40, width, height, 1, 24, 0, image_size, 2835, 2835, 0, 0)

    with open(filepath, 'wb') as f:
        f.write(file_header)
        f.write(info_header)
        pad_bytes = b'\x00' * padding
        for _ in range(height):
            row = bytearray()
            for x in range(width):
                rgb = sidebar_rgb if x < sidebar_width else color_rgb
                row.extend([rgb[2], rgb[1], rgb[0]])  # BGR format
            row.extend(pad_bytes)
            f.write(row)

def prepare_installer_assets(project_dir, cfg):
    """Generates customized RTF license terms and installer UI branding bitmaps."""
    # 1. Generate license.rtf detailing file associations, shortcuts, and license text
    license_rtf_path = project_dir / "license.rtf"
    raw_license_text = ""
    if cfg.get('LICENSE_FILE') and Path(cfg['LICENSE_FILE']).exists():
        try:
            with open(cfg['LICENSE_FILE'], 'r', encoding='utf-8', errors='ignore') as f:
                raw_license_text = f.read()
        except Exception:
            pass

    if not raw_license_text.strip():
        raw_license_text = (
            f"End User License Agreement for {cfg['APP_NAME']}\n\n"
            f"Copyright (c) {cfg['APP_PUBLISHER']}. All rights reserved.\n\n"
            "Permission is hereby granted to use this software in accordance with the application terms."
        )

    ext_items = "\\par ".join([f"\\bullet  *.{e.lstrip('.')} - {cfg['APP_NAME']} {e.capitalize()} File" for e in cfg.get('EXTENSIONS', [])])
    escaped_body = raw_license_text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}').replace('\n', '\\par\n')

    rtf_content = (
        "{\\rtf1\\ansi\\ansicpg1252\\deff0\\deflang1033"
        "{\\fonttbl{\\f0\\fnil\\fcharset0 Segoe UI;}{\\f1\\fnil\\fcharset0 Calibri;}}"
        "{\\colortbl ;\\red15\\green23\\blue42;\\red51\\green65\\blue85;\\red37\\green99\\blue235;}"
        f"\\viewkind4\\uc1\\pard\\cf1\\b\\f0\\fs22 {cfg['APP_NAME']} Installation & License Agreement\\b0\\fs18\\par"
        f"\\cf2\\f1\\fs18 Version: {cfg['APP_VERSION']} | Publisher: {cfg['APP_PUBLISHER']}\\par"
        "\\cf3\\b ____________________________________________________________________\\b0\\cf2\\par\\par"
        "\\b Configured File Associations:\\b0\\par\n"
        f"{ext_items}\\par\\par"
        "\\b Desktop & Start Menu Shortcuts:\\b0\\par"
        "\\bullet  Desktop Shortcut: A shortcut will be automatically created on your Desktop.\\par"
        "\\bullet  Start Menu Shortcut: An application entry will be placed in your Start Menu.\\par\\par"
        "\\b License Terms:\\b0\\par\n"
        f"{escaped_body}\\par\n}}"
    )
    with open(license_rtf_path, "w", encoding="utf-8") as f:
        f.write(rtf_content)

    # 2. Generate UI Bitmaps (Dialog 493x312, Banner 493x58, Logo 64x64)
    dialog_bmp = project_dir / "dialog.bmp"
    banner_bmp = project_dir / "banner.bmp"
    logo_bmp = project_dir / "logo.bmp"

    create_raw_bmp_file(dialog_bmp, 493, 312, color_rgb=(255, 255, 255), sidebar_width=164, sidebar_rgb=(30, 41, 59))
    create_raw_bmp_file(banner_bmp, 493, 58, color_rgb=(248, 250, 252), sidebar_width=0)
    create_raw_bmp_file(logo_bmp, 64, 64, color_rgb=(255, 255, 255))

    # Composite icon onto bitmaps when Pillow is available
    if cfg.get('ICON_FILE') and Path(cfg['ICON_FILE']).exists():
        try:
            from PIL import Image
            with Image.open(cfg['ICON_FILE']) as ico:
                ico_rgba = ico.convert("RGBA")

                # Bootstrapper logo (64x64)
                logo_img = Image.new("RGB", (64, 64), (255, 255, 255))
                ico_resized_64 = ico_rgba.resize((56, 56), Image.Resampling.LANCZOS)
                logo_img.paste(ico_resized_64, (4, 4), mask=ico_resized_64.split()[3])
                logo_img.save(str(logo_bmp), "BMP")

                # Welcome/Exit dialog sidebar (493x312, icon centered on left sidebar)
                with Image.open(str(dialog_bmp)) as d_img:
                    ico_resized_96 = ico_rgba.resize((96, 96), Image.Resampling.LANCZOS)
                    d_img.paste(ico_resized_96, (34, 80), mask=ico_resized_96.split()[3])
                    d_img.save(str(dialog_bmp), "BMP")

                # Top banner header (493x58, icon positioned on right)
                with Image.open(str(banner_bmp)) as b_img:
                    ico_resized_48 = ico_rgba.resize((48, 48), Image.Resampling.LANCZOS)
                    b_img.paste(ico_resized_48, (435, 5), mask=ico_resized_48.split()[3])
                    b_img.save(str(banner_bmp), "BMP")
        except Exception:
            pass

    return str(license_rtf_path), str(dialog_bmp), str(banner_bmp), str(logo_bmp)

def generate_wixsharp_program_cs(project_dir, cfg):
    """Generates pure C# WixSharp implementation based on active configuration."""
    
    # 1. Sanitize paths: strip trailing slashes so C# verbatim strings (@"...") don't escape quotes
    target_dir = str(Path(cfg['TARGET_DIR']).resolve()).rstrip(r'\/')
    icon_path = str(Path(cfg['ICON_FILE']).resolve()) if cfg.get('ICON_FILE') else "icon.ico"
    icon_filename = Path(cfg['ICON_FILE']).name if cfg.get('ICON_FILE') else "icon.ico"
    main_exe = cfg.get('MAIN_EXE', 'main.exe').strip()
    final_output = str(Path(cfg['FINAL_OUTPUT_PATH']).resolve()).rstrip(r'\/')

    # 2. Build custom UI assets (RTF agreement and bitmaps)
    license_rtf, dialog_bmp, banner_bmp, logo_bmp = prepare_installer_assets(project_dir, cfg)

    # 3. Format File Associations (Omitting Icon lets Windows inherit the EXE's icon cleanly)
    fa_blocks = []
    for ext in cfg.get("EXTENSIONS", []):
        ext_clean = ext.lstrip(".")
        desc = f"{cfg['APP_NAME']} {ext_clean.capitalize()} File"
        fa_blocks.append(f'                        new FileAssociation("{ext_clean}") {{ Description = "{desc}" }}')
    fa_code = ",\n".join(fa_blocks)
    if fa_code:
        fa_code = ",\n" + fa_code

    # 4. Format Secondary Shortcuts
    sec_shortcuts = []
    for sc in cfg.get("SECONDARY_SHORTCUTS", []):
        target_name = sc.get("target")
        shortcut_name = sc.get("name")
        sec_shortcuts.append(f'''
                        new File(mainFeature, Path.Combine(appDir, "{target_name}"),
                            new FileShortcut("{shortcut_name}", @"%ProgramMenu%") {{ Feature = mainFeature }}
                        )''')
    sec_shortcuts_code = (",\n" + ",\n".join(sec_shortcuts)) if sec_shortcuts else ""

    # Pure C# template using string replacement to eliminate Python f-string brace collisions
    template = """using System;
using System.IO;
using System.Reflection;
using System.Diagnostics;
using Microsoft.CSharp;
using System.CodeDom.Compiler;
using WixSharp;

// Disambiguate File and Dir from System.IO
using File = WixSharp.File;
using Dir = WixSharp.Dir;

class Program
{
    static int Main()
    {
        try
        {
            string appDir = @"__TARGET_DIR__";
            string mainExe = Path.Combine(appDir, @"__MAIN_EXE__");
            string iconFile = @"__ICON_PATH__";
            string outputInstaller = @"__FINAL_OUTPUT__";
            string licenseRtf = @"__LICENSE_RTF__";
            string dialogBmp = @"__DIALOG_BMP__";
            string bannerBmp = @"__BANNER_BMP__";

            if (!System.IO.File.Exists(mainExe))
                throw new FileNotFoundException($"Cannot find main application binary: {mainExe}");
            if (!System.IO.File.Exists(iconFile))
                throw new FileNotFoundException($"Cannot find application icon: {iconFile}");

            // Locate bundled WiX compiler from WixSharp.wix.bin package cache
            if (string.IsNullOrEmpty(Compiler.WixLocation) || !Directory.Exists(Compiler.WixLocation))
            {
                string userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
                Compiler.WixLocation = Path.Combine(userProfile, ".nuget", "packages", "wixsharp.wix.bin", "3.14.1", "tools", "bin");
            }

            Console.WriteLine($"[WixSharp Engine] Harvesting payload from: {appDir}");

            // Setup feature model: Core Application (Mandatory) & Desktop Shortcut (Optional, Enabled by default)
            var mainFeature = new Feature("__APP_NAME__", "Main application files and shell integration")
            {
                AttributesDefinition = "Absent=disallow;ConfigurableDirectory=INSTALLDIR"
            };
            var desktopFeature = new Feature("Desktop Shortcut", "Create a shortcut on your Desktop")
            {
                IsEnabled = true
            };

            var project = new Project("__APP_NAME__")
            {
                Version = new Version("__APP_VERSION__"),
                UpgradeCode = new Guid("__PRODUCT_GUID__"),
                InstallScope = InstallScope.perUser,
                Platform = Platform.x86,

                // FeatureTree UI displays path, allows folder browsing via [Browse...], and toggles desktop shortcut
                UI = WUI.WixUI_FeatureTree,
                LicenceFile = licenseRtf,

                ControlPanelInfo =
                {
                    Manufacturer = "__APP_PUBLISHER__",
                    ProductIcon = iconFile
                },

                Dirs = new[]
                {
                    new Dir(new Id("INSTALLDIR"), @"%LocalAppData%\\__APP_NAME__",
                        // Primary application executable with Start Menu shortcut and File Associations
                        new File(mainFeature, mainExe,
                            new FileShortcut("__APP_NAME__", @"%ProgramMenu%") { Feature = mainFeature }__FA_CODE__
                        ),

                        // Application icon asset
                        new File(mainFeature, iconFile)__SEC_SHORTCUTS__,

                        // Auto-harvest remaining folder payload
                        new Files(mainFeature, Path.Combine(appDir, "*.*"))
                        {
                            Filter = f => !f.EndsWith("__MAIN_EXE__", StringComparison.OrdinalIgnoreCase) &&
                                          !f.EndsWith("__ICON_FILENAME__", StringComparison.OrdinalIgnoreCase)
                        }
                    ),

                    // Dedicated Desktop directory containing the optional shortcut tied to desktopFeature
                    new Dir(@"%Desktop%",
                        new ExeFileShortcut("__APP_NAME__", $"[INSTALLDIR]{Path.GetFileName(mainExe)}", "")
                        {
                            Feature = desktopFeature,
                            WorkingDirectory = "INSTALLDIR"
                        }
                    )
                }
            };

            // Configure branding bitmaps via standard WiX variables
            project.WixVariables["WixUIDialogBmp"] = dialogBmp;
            project.WixVariables["WixUIBannerBmp"] = bannerBmp;

            // Build payload MSI
            string msiFile = project.BuildMsi();

            // Build single-window standalone .exe installer
            BuildStandaloneExecutable(msiFile, outputInstaller, iconFile);

            Console.WriteLine($"\\n[SUCCESS] Generated Standalone Installer: {outputInstaller}");
            return 0;
        }
        catch (Exception ex)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"\\n[WixSharp Compiler Error]: {ex.Message}");
            Console.WriteLine(ex.StackTrace);
            Console.ResetColor();
            return 1;
        }
    }

    static void BuildStandaloneExecutable(string msiPath, string exeOutputPath, string iconPath)
    {
        Console.WriteLine("[WixSharp Engine] Compiling single-window executable wrapper: " + exeOutputPath);

        var provider = new CSharpCodeProvider();
        var parameters = new CompilerParameters
        {
            GenerateExecutable = true,
            OutputAssembly = exeOutputPath,
            CompilerOptions = "/target:winexe"
        };

        if (System.IO.File.Exists(iconPath))
        {
            parameters.CompilerOptions += " /win32icon:\\"" + iconPath + "\\"";
        }

        parameters.ReferencedAssemblies.Add("System.dll");
        parameters.EmbeddedResources.Add(msiPath);

        string launcherSource =
            "using System;\\n" +
            "using System.Diagnostics;\\n" +
            "using System.IO;\\n" +
            "using System.Reflection;\\n" +
            "\\n" +
            "class Program\\n" +
            "{\\n" +
            "    [STAThread]\\n" +
            "    static int Main(string[] args)\\n" +
            "    {\\n" +
            "        string tempDir = Path.Combine(Path.GetTempPath(), \\\"Setup_\\\" + Guid.NewGuid().ToString(\\\"N\\\"));\\n" +
            "        Directory.CreateDirectory(tempDir);\\n" +
            "        string tempMsi = Path.Combine(tempDir, \\\"Setup.msi\\\");\\n" +
            "\\n" +
            "        try\\n" +
            "        {\\n" +
            "            var asm = Assembly.GetExecutingAssembly();\\n" +
            "            string resName = null;\\n" +
            "            foreach (var name in asm.GetManifestResourceNames())\\n" +
            "            {\\n" +
            "                if (name.EndsWith(\\\".msi\\\", StringComparison.OrdinalIgnoreCase))\\n" +
            "                {\\n" +
            "                    resName = name;\\n" +
            "                    break;\\n" +
            "                }\\n" +
            "            }\\n" +
            "\\n" +
            "            if (resName == null) return 1;\\n" +
            "\\n" +
            "            using (var src = asm.GetManifestResourceStream(resName))\\n" +
            "            using (var dst = File.Create(tempMsi))\\n" +
            "            {\\n" +
            "                src.CopyTo(dst);\\n" +
            "            }\\n" +
            "\\n" +
            "            string arguments = \\\"/i \\\\\\\"\\\" + tempMsi + \\\"\\\\\\\"\\\";\\n" +
            "            if (args != null && args.Length > 0)\\n" +
            "            {\\n" +
            "                arguments += \\\" \\\" + string.Join(\\\" \\\", args);\\n" +
            "            }\\n" +
            "\\n" +
            "            var psi = new ProcessStartInfo(\\\"msiexec.exe\\\", arguments)\\n" +
            "            {\\n" +
            "                UseShellExecute = false\\n" +
            "            };\\n" +
            "\\n" +
            "            var proc = Process.Start(psi);\\n" +
            "            proc.WaitForExit();\\n" +
            "            return proc.ExitCode;\\n" +
            "        }\\n" +
            "        catch\\n" +
            "        {\\n" +
            "            return 1;\\n" +
            "        }\\n" +
            "        finally\\n" +
            "        {\\n" +
            "            try\\n" +
            "            {\\n" +
            "                if (File.Exists(tempMsi)) File.Delete(tempMsi);\\n" +
            "                if (Directory.Exists(tempDir)) Directory.Delete(tempDir, true);\\n" +
            "            }\\n" +
            "            catch {}\\n" +
            "        }\\n" +
            "    }\\n" +
            "}\\n";

        CompilerResults results = provider.CompileAssemblyFromSource(parameters, launcherSource);
        if (results.Errors.HasErrors)
        {
            foreach (CompilerError err in results.Errors)
            {
                Console.WriteLine("[Executable Wrapper Error]: " + err.ErrorText);
            }
            throw new Exception("Failed to compile standalone installer executable.");
        }
    }
}
"""

    content = template.replace("__TARGET_DIR__", target_dir) \
                      .replace("__MAIN_EXE__", main_exe) \
                      .replace("__ICON_PATH__", icon_path) \
                      .replace("__ICON_FILENAME__", icon_filename) \
                      .replace("__FINAL_OUTPUT__", final_output) \
                      .replace("__LICENSE_RTF__", license_rtf) \
                      .replace("__DIALOG_BMP__", dialog_bmp) \
                      .replace("__BANNER_BMP__", banner_bmp) \
                      .replace("__APP_NAME__", cfg['APP_NAME']) \
                      .replace("__APP_VERSION__", cfg['APP_VERSION']) \
                      .replace("__PRODUCT_GUID__", cfg['PRODUCT_GUID']) \
                      .replace("__APP_PUBLISHER__", cfg['APP_PUBLISHER']) \
                      .replace("__FA_CODE__", fa_code) \
                      .replace("__SEC_SHORTCUTS__", sec_shortcuts_code)

    with open(project_dir / "Program.cs", "w", encoding="utf-8") as f:
        f.write(content)
        
# =============================================================================
# INTERACTIVE WORKSPACE CONFIGURATION & PREFERENCES
# =============================================================================
PREFS_FILE = "installer_prefs.json"

def configure_interactive_settings(current_cfg):
    root_dir = Path.cwd().resolve()
    cfg = dict(current_cfg)

    print(f"\n{CYAN}[*] Step-by-Step Interactive Configuration:{RESET}")

    # 1. App Name
    app_in = input(f"{YELLOW} -> Application Name [{cfg['APP_NAME']}]: {RESET}").strip()
    if app_in: cfg['APP_NAME'] = app_in

    # 2. Version & Publisher
    ver_in = input(f"{YELLOW} -> Version [{cfg['APP_VERSION']}]: {RESET}").strip()
    if ver_in: cfg['APP_VERSION'] = ver_in

    pub_in = input(f"{YELLOW} -> Publisher [{cfg['APP_PUBLISHER']}]: {RESET}").strip()
    if pub_in: cfg['APP_PUBLISHER'] = pub_in

    # 3. Payload Directory (with GUI picker)
    print(f"{CYAN} -> Target Directory (Containing application files and .exe){RESET}")
    print(f"    Current: {cfg['TARGET_DIR']}")
    if input(f"{YELLOW}    Open Explorer folder picker? (Y/n): {RESET}").strip().lower() != 'n':
        gui_dir = UIAesthetics.trigger_gui_folder_selector("Select Application Payload Directory", cfg['TARGET_DIR'] or str(root_dir))
        if gui_dir: cfg['TARGET_DIR'] = gui_dir
    else:
        dir_in = input(f"{YELLOW}    Enter path manually: {RESET}").strip()
        if dir_in: cfg['TARGET_DIR'] = str(Path(dir_in).resolve())

    # 4. Main Executable (with GUI picker)
    print(f"{CYAN} -> Main Application Executable (.exe){RESET}")
    print(f"    Current: {cfg['MAIN_EXE']}")
    if input(f"{YELLOW}    Open Explorer file picker? (Y/n): {RESET}").strip().lower() != 'n':
        gui_file = UIAesthetics.trigger_gui_file_selector("Select Main Executable", cfg['TARGET_DIR'], [("Executable Files", "*.exe")])
        if gui_file: cfg['MAIN_EXE'] = Path(gui_file).name
    else:
        exe_in = input(f"{YELLOW}    Enter filename manually: {RESET}").strip()
        if exe_in: cfg['MAIN_EXE'] = exe_in

    # 5. Icon File (.ico)
    print(f"{CYAN} -> Application Icon (.ico){RESET}")
    print(f"    Current: {cfg['ICON_FILE'] or 'None'}")
    if input(f"{YELLOW}    Open Explorer file picker? (Y/n): {RESET}").strip().lower() != 'n':
        gui_ico = UIAesthetics.trigger_gui_file_selector("Select Application Icon", str(root_dir), [("Icon Files", "*.ico"), ("All Files", "*.*")])
        if gui_ico: cfg['ICON_FILE'] = gui_ico
    else:
        ico_in = input(f"{YELLOW}    Enter icon path manually: {RESET}").strip()
        if ico_in: cfg['ICON_FILE'] = str(Path(ico_in).resolve())

    # 6. Registered File Associations
    current_exts = ", ".join(cfg.get("EXTENSIONS", []))
    print(f"{CYAN} -> File Associations (extensions without leading dots, comma-separated){RESET}")
    ext_in = input(f"{YELLOW}    Extensions [{current_exts}]: {RESET}").strip()
    if ext_in:
        cfg['EXTENSIONS'] = [e.strip().lstrip(".") for e in ext_in.split(",") if e.strip()]

    # 7. Secondary Shortcuts
    if input(f"{YELLOW} -> Configure secondary shortcuts (e.g., for tools/updaters)? (y/N): {RESET}").strip().lower() == 'y':
        cfg['SECONDARY_SHORTCUTS'] = []
        while True:
            gui_sec = UIAesthetics.trigger_gui_file_selector("Select Target File for Secondary Shortcut", cfg['TARGET_DIR'], [("All Files", "*.*")])
            if not gui_sec: break
            sec_name = input(f"{YELLOW}    Display Name for this shortcut [{Path(gui_sec).stem}]: {RESET}").strip() or Path(gui_sec).stem
            cfg['SECONDARY_SHORTCUTS'].append({"target": Path(gui_sec).name, "name": sec_name})
            if input(f"{YELLOW}    Add another secondary shortcut? (y/N): {RESET}").strip().lower() != 'y': break

    # 8. Output Filename
    out_in = input(f"{YELLOW} -> Output Installer Name [{cfg['OUTPUT_INSTALLER']}]: {RESET}").strip()
    if out_in: cfg['OUTPUT_INSTALLER'] = out_in

    return cfg

# =============================================================================
# MAIN PIPELINE EXECUTION
# =============================================================================
def main():
    print(f"\n{CYAN}======================================================{RESET}")
    print(f"{CYAN}     🚀 UNIVERSAL WIXSHARP INSTALLER BUILDER 🚀       {RESET}")
    print(f"{CYAN}======================================================{RESET}")

    root_dir = Path.cwd().resolve()
    current_folder_name = root_dir.name
    installer_proj_dir = root_dir / f"{current_folder_name.replace(' ', '')}Installer"

    cfg = auto_detect_environment()

    use_saved = False
    reconfigure = False

    if Path(PREFS_FILE).exists():
        try:
            with open(PREFS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                cfg.update(saved)
            print(f"{CYAN}[*] Loaded persistent installer preferences from '{PREFS_FILE}'.{RESET}")
            if input(f"{YELLOW} -> Do you want to modify settings before generating? (y/N): {RESET}").strip().lower() == 'y':
                reconfigure = True
            else:
                use_saved = True
        except Exception:
            pass

    # Ensure GUIDs are persistent across builds to preserve upgrade semantics
    if not cfg.get("PRODUCT_GUID"):
        cfg["PRODUCT_GUID"] = str(uuid.uuid4()).upper()
    if not cfg.get("UPGRADE_GUID"):
        cfg["UPGRADE_GUID"] = str(uuid.uuid4()).upper()

    if not use_saved or reconfigure:
        cfg = configure_interactive_settings(cfg)
        try:
            with open(PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=4)
            print(f"{GREEN}[+] Settings saved to '{PREFS_FILE}'.{RESET}")
        except Exception as e:
            print(f"{RED}[!] Failed to write preferences: {e}{RESET}")

    cfg['FINAL_OUTPUT_PATH'] = str(root_dir / cfg['OUTPUT_INSTALLER'])

    # Display Build Manifest
    print(f"\n{CYAN}======================================================{RESET}")
    print(f"{GREEN}        📋 INSTALLER CONFIGURATION MANIFEST 📋        {RESET}")
    print(f"{CYAN}======================================================{RESET}")
    print(f"{YELLOW} - Project Directory: {RESET}  {installer_proj_dir.name}")
    print(f"{YELLOW} - Application Name:  {RESET}  {cfg['APP_NAME']}")
    print(f"{YELLOW} - Version:           {RESET}  {cfg['APP_VERSION']}")
    print(f"{YELLOW} - Publisher:         {RESET}  {cfg['APP_PUBLISHER']}")
    print(f"{YELLOW} - Target Payload:    {RESET}  {cfg['TARGET_DIR']}")
    print(f"{YELLOW} - Main Binary:       {RESET}  {cfg['MAIN_EXE']}")
    print(f"{YELLOW} - Icon Asset:        {RESET}  {cfg['ICON_FILE']}")
    print(f"{YELLOW} - Associations:      {RESET}  {', '.join(cfg.get('EXTENSIONS', []))}")
    print(f"{YELLOW} - Secondary Items:   {RESET}  {len(cfg.get('SECONDARY_SHORTCUTS', []))}")
    print(f"{YELLOW} - Output Binary:     {RESET}  {cfg['OUTPUT_INSTALLER']}")
    print(f"{CYAN}======================================================{RESET}")

    ans = input(f"{GREEN}Press Enter to compile installer... or R to reconfigure! {RESET}").strip().lower()
    if ans == 'r':
        return main()

    # Step 1: Scaffold Isolated C# Project
    print(f"\n{CYAN}[*] Scaffolding isolated WixSharp .NET project at: {installer_proj_dir}{RESET}")
    installer_proj_dir.mkdir(parents=True, exist_ok=True)
    generate_wixsharp_csproj(installer_proj_dir)
    generate_wixsharp_program_cs(installer_proj_dir, cfg)

    # Step 2: Restore Dependencies targeting x86
    restore_success = UIAesthetics.run_with_progress_bar(
        ["dotnet", "restore", "-p:Platform=x86"], 
        "DotNet Restore", 
        cwd=str(installer_proj_dir), 
        step_info="1/2"
    )
    if not restore_success:
        print(f"{RED}[!] Failed to restore NuGet dependencies. Ensure .NET SDK is on your PATH.{RESET}")
        sys.exit(1)

    # Step 3: Build & Execute WixSharp compiler with explicit x86 platform
    build_success = UIAesthetics.run_with_progress_bar(
        ["dotnet", "build", "-p:Platform=x86"], 
        "WixSharp Compiler", 
        cwd=str(installer_proj_dir), 
        step_info="2/2"
    )

    if build_success and Path(cfg['FINAL_OUTPUT_PATH']).exists():
        size_mb = os.path.getsize(cfg['FINAL_OUTPUT_PATH']) / (1024 * 1024)
        print(f"\n{GREEN}======================================================{RESET}")
        print(f"{GREEN} [✔] SUCCESS: Single-File Installer Generated!{RESET}")
        print(f"{YELLOW} -> Location:  {cfg['FINAL_OUTPUT_PATH']}{RESET}")
        print(f"{YELLOW} -> File Size: {size_mb:.2f} MB{RESET}")
        print(f"{GREEN}======================================================{RESET}\n")
    else:
        print(f"\n{RED}[✘] Build pipeline failed to produce: {cfg['OUTPUT_INSTALLER']}{RESET}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
import os
import sys
import subprocess
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# 1. Setup Exhaustive Logging (Console + File)
log_file = "compression_log.txt"
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def check_upx(root_dir):
    """Checks if UPX is available in the system PATH or local directory."""
    local_upx = Path(root_dir) / "upx.exe"
    if local_upx.exists():
        return str(local_upx)
    
    try:
        subprocess.run(["upx", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return "upx"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def compress_file_worker(file_path, root_dir, upx_path):
    """Worker function executed by individual CPU cores."""
    try:
        orig_size = os.path.getsize(file_path)
        relative_path = os.path.relpath(file_path, root_dir)
        
        # --ultra-brute: Maximum compression attempt
        # --no-backup: Overwrite in place
        # --force: Force packing of files with GUARD_CF or similar flags
        cmd = [upx_path, "--ultra-brute", "--no-backup", "--force", file_path]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        new_size = os.path.getsize(file_path)
        
        if result.returncode == 0:
            if new_size < orig_size:
                saved = orig_size - new_size
                pct = (saved / orig_size) * 100
                return {
                    "status": "SUCCESS", "path": relative_path, "orig_size": orig_size,
                    "new_size": new_size, "saved": saved, "pct": pct
                }
            else:
                return {
                    "status": "SKIPPED_NO_GAIN", "path": relative_path, "orig_size": orig_size, "new_size": orig_size
                }
        elif result.returncode == 7:
            return {
                "status": "SKIPPED_ALREADY_PACKED", "path": relative_path, "orig_size": orig_size, "new_size": orig_size
            }
        else:
            raw_error = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
            error_lines = [line.strip() for line in raw_error.split('\n') if line.strip()]
            exact_cause = "Unknown UPX operational error"
            if error_lines:
                cause_candidates = [l for l in error_lines if "Exception" in l or "error:" in l or "cannot" in l.lower()]
                exact_cause = cause_candidates[-1] if cause_candidates else error_lines[-1]
            
            return {
                "status": "FAILED", "path": relative_path, "orig_size": orig_size, "new_size": orig_size, "error": exact_cause
            }
            
    except Exception as e:
        return {
            "status": "ERROR", "path": os.path.relpath(file_path, root_dir), "orig_size": 0, "new_size": 0, "error": str(e)
        }

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    upx_path = check_upx(root_dir)

    if not upx_path:
        logging.error("UPX executable not found! Place 'upx.exe' in this folder or add it to your system PATH.")
        return

    # 2. Interactive Choice for Transitive Search
    print("=" * 60)
    print(" UPX MULTIPROCESSING COMPRESSION ENGINE")
    print("=" * 60)
    user_choice = input("Compress transitively? (y = scan ALL subfolders / n = ONLY top-level files): ").strip().lower()
    print("-" * 60)
    
    is_transitive = user_choice in ['y', 'yes']

    num_cores = os.cpu_count()
    logging.info(f"Target Root Directory: {root_dir}")
    logging.info(f"Scanning Scope:        {'ALL SUBFOLDERS (Transitive)' if is_transitive else 'ABSOLUTE TOP-LEVEL ONLY'}")
    logging.info(f"Allocated CPU Cores:   {num_cores}")
    
    target_extensions = ('.exe', '.dll', '.pyd')
    files_to_process = []

    # File Discovery Scan based on user choice
    if is_transitive:
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.lower().endswith(target_extensions):
                    if filename.lower() == "upx.exe":
                        continue
                    files_to_process.append(os.path.join(dirpath, filename))
    else:
        # Top level scan using an immediate directory list sweep
        for entry in os.scandir(root_dir):
            if entry.is_file() and entry.name.lower().endswith(target_extensions):
                if entry.name.lower() == "upx.exe":
                    continue
                files_to_process.append(entry.path)

    total_files_found = len(files_to_process)
    logging.info(f"Discovered {total_files_found} target binaries matching criteria. Spawning workers...\n" + "-"*60)

    if total_files_found == 0:
        logging.info("No matching binaries found to process.")
        return

    total_files_compressed = 0
    total_files_skipped = 0
    total_files_failed = 0
    initial_total_size = 0
    final_total_size = 0

    # Execute tasks concurrently across the processor pool
    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        futures = {executor.submit(compress_file_worker, f, root_dir, upx_path): f for f in files_to_process}
        
        for future in as_completed(futures):
            res = future.result()
            initial_total_size += res["orig_size"]
            final_total_size += res["new_size"]
            
            logging.info(f"Processing: {res['path']}")
            logging.info(f"  -> Original Size: {res['orig_size']:,} bytes")
            
            if res["status"] == "SUCCESS":
                total_files_compressed += 1
                logging.info(f"  [SUCCESS] Compressed to: {res['new_size']:,} bytes (-{res['pct']:.2f}% / Saved: {res['saved']:,} bytes)")
            elif res["status"] == "SKIPPED_NO_GAIN":
                total_files_skipped += 1
                logging.info(f"  [SKIPPED] UPX could not reduce size further than original.")
            elif res["status"] == "SKIPPED_ALREADY_PACKED":
                total_files_skipped += 1
                logging.info(f"  [SKIPPED] File is already packed/compressed.")
            elif res["status"] == "FAILED":
                total_files_failed += 1
                logging.warning(f"  [FAILED] Exact Cause -> {res['error']}")
            elif res["status"] == "ERROR":
                total_files_failed += 1
                logging.error(f"  [ERROR] Internal exception: {res['error']}")
                
            logging.info("-" * 40)

    # 3. Final Summary Report Generation
    space_saved = initial_total_size - final_total_size
    saved_percentage = (space_saved / initial_total_size * 100) if initial_total_size > 0 else 0

    logging.info("=" * 60)
    logging.info("MULTIPROCESSING JOB COMPLETED")
    logging.info("=" * 60)
    logging.info(f"Total Target Files Encountered: {total_files_found}")
    logging.info(f"  - Successfully Compressed:    {total_files_compressed}")
    logging.info(f"  - Skipped (No gain/Packed):   {total_files_skipped}")
    logging.info(f"  - Failed/Errors:              {total_files_failed}")
    logging.info(f"Initial Total Size of Binaries: {initial_total_size:,} bytes")
    logging.info(f"Final Total Size of Binaries:   {final_total_size:,} bytes")
    logging.info(f"Total Disk Space Saved:         {space_saved:,} bytes ({saved_percentage:.2f}% smaller)")
    logging.info(f"Exhaustive log written to:      {os.path.join(root_dir, log_file)}")

if __name__ == "__main__":
    main()
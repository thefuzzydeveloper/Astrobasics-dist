# _setup_launcher.py
import sys, os, subprocess, threading
import tkinter as tk

MAGIC_SIG = b"__VPK_PAYLOAD_V1__"

def run_installer():
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__ if "__file__" in globals() else sys.argv[0])))
    splash_gif = os.path.join(base_dir, "installer_splash.gif")
    lic_file = os.path.join(base_dir, "license.txt")

    raw_lic = '========================================================================\n                   END USER LICENSE AGREEMENT (EULA)\n                      FOR NON-COMMERCIAL USE ONLY\n========================================================================\n\nIMPORTANT — READ CAREFULLY:\nBy installing, copying, accessing, or otherwise using AstroBasics Diamond Chart Pro (the "Software"), you agree to be bound by the terms of this End User License Agreement ("Agreement"). If you do not agree to the terms of this Agreement, do not install, copy, access, or use the Software.\n\n1. GRANT OF LICENSE\nThe Software is licensed, not sold. Subject to your compliance with this Agreement, the Developer grants you a personal, revocable, non-exclusive, non-transferable license to install and execute the Software on your personal device(s).\n\n2. RESTRICTIONS ON COMMERCIAL USE\nYou agree NOT to:\n   a) Sell, rent, lease, sublicense, distribute, host, or commercially exploit the Software or any modified version thereof.\n   b) Use the Software or its generated analytical reports to deceive, mislead, or commit fraud. Furthermore, you may not use the Software to provide professional or commercial astrological consulting services unless you possess independent, prior astrological insight (a formal academic credential or certificate in astrology does not solely constitute "insight").\n   c) Embed, bundle, or incorporate the Software, its source code, or its compiled dependencies into any commercial product, platform, or enterprise service.\n\n3. OWNERSHIP AND INTELLECTUAL PROPERTY\nThe Software—including but not limited to its source code, algorithms, visual layouts, styling, icons, and documentation—remains the sole and exclusive intellectual property of the Developer. This Agreement grants you only limited user privileges and transfers no title, copyright, trademark, or ownership interest.\n\n4. LOCAL DATA PRIVACY\n   a) Local Processing: All astrological computations, planetary ephemeris math, divisional varga engines, and interpretive evaluations execute strictly offline on your local device using the embedded USNO NOVAS C 3.1 astrometric engine and NASA JPL DE440 ephemerides (exceptions are stated in section 5 of this text).\n   b) User Data Sovereignty: The Developer guarantees that NO personal names, birth dates, birth times, geographic coordinates, natal charts, notes, custom rules, or exported files (.astrobasic, .json, .milan, .astroanalysis) are ever uploaded, accessed, or transmitted over any network by the provided software. All user-generated chart data remains strictly stored on your local disk.\n   c) No Background Telemetry: The Software contains no background telemetry for data collection purposes, however voluntary feedback is welcomed.\n\n5. NETWORK OPERATIONS\nThe Software initiates network connections exclusively for functional operations:\n   a) Location Geocoding: Location searches transmit solely the entered text query to the open-source OpenStreetMap (Nominatim) API and the Open-Meteo API to resolve latitude, longitude, and timezone offsets.\n   b) Software Updates: The Software connects over HTTPS to a GitHub distribution manifest to compare version hashes. Downloads are verified using SHA-256 hashes and asymmetric digital signatures (Ed25519) to prevent tampering.\n   c) Voluntary Feature Polling: Following updates, the Software may display an optional community poll. If submitted, only the numerical option index (and no other user identifiable data/anonymous data) is transmitted.\n   d) Voluntary Ratings: An optional feedback panel allows users to submit ratings and recommendations. Submissions transmit your review, chosen display name, and a one-way cryptographic SHA-256 hash derived from the system network node identifier (to prevent duplicate ratings without user accounts).\n\n6. DISCLAIMER OF WARRANTIES\nTHE SOFTWARE IS PROVIDED "AS IS" AND "AS AVAILABLE," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, SYSTEM INTEGRATION, AND NON-INFRINGEMENT. ASTROLOGY IS AN INTERPRETATIVE DISCIPLINE; THE DEVELOPER MAKES NO REPRESENTATIONS REGARDING THE ABSOLUTE ACCURACY, COMPLETENESS, OR PREDICTIVE RELIABILITY OF THE CALCULATIONS GENERATED.\n\n7. LIMITATION OF LIABILITY\nTO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE DEVELOPER BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF THE USE OF OR INABILITY TO USE THE SOFTWARE, REGARDLESS OF THE LEGAL THEORY (TORT, CONTRACT, OR OTHERWISE), EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.\n\n8. TERMINATION\nThis Agreement remains in effect until terminated. Your rights under this license terminate automatically without notice if you fail to comply with any of its terms. Upon termination, you must cease all use and uninstall all copies of the Software.\n'
    if os.path.exists(lic_file):
        try:
            with open(lic_file, "r", encoding="utf-8") as f:
                c = f.read()
                if c.strip():
                    raw_lic = c
        except Exception:
            pass

    root = tk.Tk()
    root.title("AstroBasics Setup")
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    max_w, max_h = int(sw * 0.92), int(sh * 0.88)
    scale = min(1.0, max_w / 1280.0, max_h / 760.0)
    w = max(640, int(1280 * scale))
    h = max(400, int(760 * scale))
    win_x = (sw - w) // 2
    win_y = (sh - h) // 2
    root.geometry(str(w) + "x" + str(h) + "+" + str(win_x) + "+" + str(win_y))
    root.configure(bg="#FCFAF6")

    drag_data = {"x": 0, "y": 0}
    def _start_drag(event):
        drag_data["x"] = event.x
        drag_data["y"] = event.y
    def _do_drag(event):
        dx = event.x - drag_data["x"]
        dy = event.y - drag_data["y"]
        nx = root.winfo_x() + dx
        ny = root.winfo_y() + dy
        root.geometry("+" + str(nx) + "+" + str(ny))

    outer = tk.Frame(root, bg="#FCFAF6", highlightbackground="#D4AF37", highlightthickness=1.5)
    outer.pack(fill=tk.BOTH, expand=True)
    outer.bind("<Button-1>", _start_drag)
    outer.bind("<B1-Motion>", _do_drag)

    bg_lbl = tk.Label(outer, bg="#FCFAF6")
    bg_lbl.place(x=0, y=0, width=w, height=h)
    bg_lbl.bind("<Button-1>", _start_drag)
    bg_lbl.bind("<B1-Motion>", _do_drag)

    frames = []
    if os.path.exists(splash_gif):
        try:
            from PIL import Image, ImageTk
            im = Image.open(splash_gif)
            resample_filter = getattr(getattr(Image, "Resampling", Image), "LANCZOS", getattr(Image, "LANCZOS", 1))
            n_frames = getattr(im, "n_frames", 1)
            for i in range(n_frames):
                im.seek(i)
                f_img = im.convert("RGBA").resize((w, h), resample_filter)
                frames.append(ImageTk.PhotoImage(f_img))
            im.close()
        except Exception:
            pass

    if frames:
        bg_lbl.config(image=frames[0])

    status_banner = tk.Frame(
        outer, bg="#FEFCF8",
        highlightbackground="#D4AF37", highlightthickness=1.5,
        padx=28, pady=10
    )
    status_lbl = tk.Label(
        status_banner,
        text="✨ Terms Accepted — Installing AstroBasics...",
        font=("Segoe UI", 12, "bold"),
        fg="#851D1D", bg="#FEFCF8"
    )
    status_lbl.pack()

    card_bg = "#FAF5E8"
    card = tk.Frame(
        outer, bg=card_bg,
        highlightbackground="#D4AF37", highlightthickness=1.5,
        padx=24, pady=18
    )
    card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.90, relheight=0.88)

    # 1. Header (TOP)
    hdr = tk.Frame(card, bg=card_bg)
    hdr.pack(side=tk.TOP, fill=tk.X, pady=(0, 8))
    hdr.bind("<Button-1>", _start_drag)
    hdr.bind("<B1-Motion>", _do_drag)

    title = tk.Label(hdr, text="📜  EULA", font=("Segoe UI", 18, "bold"), fg="#851D1D", bg=card_bg)
    title.pack(side=tk.LEFT)
    title.bind("<Button-1>", _start_drag)
    title.bind("<B1-Motion>", _do_drag)

    badge = tk.Label(
        hdr, text="🔒 Zero Telemetry",
        font=("Segoe UI", 10, "bold"), fg="#6E5316", bg="#FDF6E2",
        highlightbackground="#E5C365", highlightthickness=1,
        padx=12, pady=4
    )
    badge.pack(side=tk.RIGHT)

    # 2. Bottom button bar pinned at BOTTOM FIRST (guaranteed visible and never pushed off)
    btn_bar = tk.Frame(card, bg=card_bg)
    btn_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    hint = tk.Label(
        btn_bar,
        text="Please review and accept license terms to install AstroBasics.",
        fg="#5A483E", bg=card_bg,
        font=("Segoe UI", 10)
    )
    hint.pack(side=tk.LEFT)

    btn_exit = tk.Button(
        btn_bar, text="Exit",
        font=("Segoe UI", 12, "bold"),
        bg="#FFFFFF", fg="#64748B",
        activebackground="#FEE2E2", activeforeground="#B91C1C",
        relief="flat", highlightbackground="#CBD5E1", highlightthickness=1,
        padx=22, pady=8, cursor="hand2"
    )
    btn_exit.pack(side=tk.RIGHT, padx=(10, 0))

    btn_agree = tk.Button(
        btn_bar, text="I Agree ✨",
        font=("Segoe UI", 12, "bold"),
        bg="#851D1D", fg="#FFFDF8",
        activebackground="#9C2222", activeforeground="#FFFFFF",
        relief="flat", highlightbackground="#D4AF37", highlightthickness=1,
        padx=28, pady=8, cursor="hand2"
    )
    btn_agree.pack(side=tk.RIGHT)

    btn_exit.bind("<Enter>", lambda e: btn_exit.config(bg="#FEE2E2", fg="#B91C1C"))
    btn_exit.bind("<Leave>", lambda e: btn_exit.config(bg="#FFFFFF", fg="#64748B"))
    btn_agree.bind("<Enter>", lambda e: btn_agree.config(bg="#9C2222"))
    btn_agree.bind("<Leave>", lambda e: btn_agree.config(bg="#851D1D"))

    # 3. Middle text frame fills remaining vertical space
    txt_frame = tk.Frame(card, bg="#F5EEE2", highlightbackground="#D8C7A5", highlightthickness=1.5)
    txt_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    sb = tk.Scrollbar(txt_frame, bg="#E2D4BF", activebackground="#D4AF37", troughcolor="#F5EEE2", relief="flat", bd=0, width=14)
    sb.pack(side=tk.RIGHT, fill=tk.Y)

    # Extra-large legible font (15pt) with authentic Kumkum (vermilion) and Chandan (sandalwood) selection
    eula_text = tk.Text(
        txt_frame, wrap="word",
        font=("Segoe UI", 15),
        bg="#F5EEE2", fg="#2C1A14",
        selectbackground="#8A1818", selectforeground="#FFF4C2",
        selectborderwidth=0, inactiveselectbackground="#A62828",
        spacing1=5, spacing2=3, spacing3=5,
        yscrollcommand=sb.set, relief="flat", padx=18, pady=16
    )
    eula_text.insert("1.0", raw_lic)
    eula_text.config(state="disabled")
    eula_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.config(command=eula_text.yview)

    btn_exit.bind("<Enter>", lambda e: btn_exit.config(bg="#FEE2E2", fg="#B91C1C"))
    btn_exit.bind("<Leave>", lambda e: btn_exit.config(bg="#FFFFFF", fg="#64748B"))
    btn_agree.bind("<Enter>", lambda e: btn_agree.config(bg="#9C2222"))
    btn_agree.bind("<Leave>", lambda e: btn_agree.config(bg="#851D1D"))

    install_state = [False, 0]

    def _installer_thread_worker():
        try:
            temp_payload = None
            runner_bin = None
            exe_self = os.path.abspath(sys.executable)
            with open(exe_self, "rb") as ef:
                ef.seek(-len(MAGIC_SIG), os.SEEK_END)
                tag = ef.read(len(MAGIC_SIG))
                if tag == MAGIC_SIG:
                    ef.seek(-len(MAGIC_SIG) - 8, os.SEEK_END)
                    p_size = int.from_bytes(ef.read(8), "little")
                    ef.seek(-len(MAGIC_SIG) - 8 - p_size, os.SEEK_END)
                    temp_payload = os.path.join(os.environ.get("TEMP", os.environ.get("TMP", "C:/Temp")), "AstroBasics_payload_setup.exe")
                    with open(temp_payload, "wb") as pf:
                        rem = p_size
                        while rem > 0:
                            chunk = ef.read(min(rem, 2 * 1024 * 1024))
                            if not chunk:
                                break
                            pf.write(chunk)
                            rem -= len(chunk)
                    runner_bin = temp_payload

            if runner_bin and os.path.isfile(runner_bin):
                p = subprocess.run([runner_bin, "--silent"], creationflags=0x08000000)
                install_state[1] = p.returncode
            else:
                install_state[1] = -1

            if temp_payload and os.path.isfile(temp_payload):
                try:
                    os.remove(temp_payload)
                except Exception:
                    pass
        except Exception:
            install_state[1] = -1
        install_state[0] = True

    anim_state = {"idx": 0, "running": True}
    def _animate_splash():
        if not anim_state["running"] or not frames:
            return
        bg_lbl.config(image=frames[anim_state["idx"]])
        anim_state["idx"] = (anim_state["idx"] + 1) % len(frames)
        root.after(33, _animate_splash)

    def _poll_install_complete():
        if install_state[0]:
            anim_state["running"] = False
            root.destroy()
            target_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), "AstroBasics", f"AstroBasics.exe")
            if os.path.isfile(target_exe):
                subprocess.Popen([target_exe])
            os._exit(0)
        else:
            root.after(100, _poll_install_complete)

    def on_accept():
        btn_agree.config(state="disabled")
        btn_exit.config(state="disabled")
        card.place_forget()
        status_banner.place(relx=0.5, rely=0.92, anchor="center")
        if frames:
            _animate_splash()
        t = threading.Thread(target=_installer_thread_worker, daemon=True)
        t.start()
        root.after(100, _poll_install_complete)

    def on_decline():
        anim_state["running"] = False
        root.destroy()
        os._exit(0)

    btn_agree.config(command=on_accept)
    btn_exit.config(command=on_decline)

    root.mainloop()

if __name__ == "__main__":
    run_installer()

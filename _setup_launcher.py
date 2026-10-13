# _setup_launcher.py
import sys, os, subprocess, threading
from PyQt6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextBrowser, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QMovie
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QEventLoop, QSize

MAGIC_SIG = b"__VPK_PAYLOAD_V1__"

def run_installer():
    app = QApplication.instance()
    created_app = False
    if not app:
        app = QApplication(sys.argv)
        created_app = True

    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    splash_gif = os.path.join(base_dir, "installer_splash.gif")
    lic_file = os.path.join(base_dir, "license.txt")

    raw_lic = '                                                        END USER LICENSE AGREEMENT (EULA)\nFOR NON-COMMERCIAL USE ONLY\n\nIMPORTANT — READ CAREFULLY:\nBy installing, copying, accessing, or otherwise using AstroBasics Diamond Chart Pro (the "Software"), you agree to be bound by the terms of this End User License Agreement ("Agreement"). If you do not agree to the terms of this Agreement, do not install, copy, access, or use the Software.\n\n1. GRANT OF LICENSE\nThe Software is licensed, not sold. Subject to your compliance with this Agreement, the Developer grants you a personal, revocable, non-exclusive, non-transferable license to install and execute the Software on your personal device(s).\n\n2. RESTRICTIONS ON COMMERCIAL USE\nYou agree NOT to:\n   a) Sell, rent, lease, sublicense, distribute, host, or commercially exploit the Software or any modified version thereof.\n   b) Use the Software or its generated analytical reports to deceive, mislead, or commit fraud. Furthermore, you may not use the Software to provide professional or commercial astrological consulting services unless you possess independent, prior astrological insight.(A formal academic credential or certificate in astrology does not solely constitute "insight").\n   c) Embed, bundle, or incorporate the Software, its source code, or its compiled dependencies into any commercial product, platform, or enterprise service.\n\n3. OWNERSHIP AND INTELLECTUAL PROPERTY\nThe Software—including but not limited to its source code, algorithms, visual layouts, styling, icons, and documentation—remains the sole and exclusive intellectual property of the Developer. This Agreement grants you only limited user privileges and transfers no title, copyright, trademark, or ownership interest.\n\n4. LOCAL DATA PRIVACY\n   a) Local Processing: All astrological computations, planetary ephemeris math, divisional varga engines, and interpretive evaluations execute strictly offline on your local device (exceptions are stated in section 5 of this text).\n   b) User Data Sovereignty: The Developer guarantees that NO personal names, birth dates, birth times, geographic coordinates, natal charts, notes, custom rules, or exported files (.astrobasic, .json, .milan, .astroanalysis) are ever uploaded, accessed, or transmitted over any network by the provided software. All user-generated chart data remains strictly stored on your local disk.\n   c) No Background Telemetry: The Software contains no background telemetry for data collection purposes, however Voluntary feedback is welcomed.\n\n5. NETWORK OPERATIONS\nThe Software initiates network connections exclusively for functional operations:\n   a) Location Geocoding: Location searches transmit solely the entered text query to the open-source OpenStreetMap (Nominatim) API and the Open-Meteo API to resolve latitude, longitude, and timezone offsets.\n   b) Software Updates: The Software connects over HTTPS to a GitHub distribution manifest to compare version hashes. Downloads are verified using SHA-256 hashes and asymmetric digital signatures (Ed25519) to prevent tampering.\n   c) Voluntary Feature Polling: Following updates, the Software may display an optional community poll. If submitted, only the numerical option index (and no other user identifiable data/anonymous data) is transmitted.\n   d) Voluntary Ratings: An optional feedback panel allows users to submit ratings and recommendations. Submissions transmit your review, chosen display name, and a one-way cryptographic SHA-256 hash derived from the system network node identifier (to prevent duplicate ratings without user accounts).\n\n6. DISCLAIMER OF WARRANTIES\nTHE SOFTWARE IS PROVIDED "AS IS" AND "AS AVAILABLE," WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, SYSTEM INTEGRATION, AND NON-INFRINGEMENT. ASTROLOGY IS AN INTERPRETATIVE DISCIPLINE; THE DEVELOPER MAKES NO REPRESENTATIONS REGARDING THE ABSOLUTE ACCURACY, COMPLETENESS, OR PREDICTIVE RELIABILITY OF THE CALCULATIONS GENERATED.\n\n7. LIMITATION OF LIABILITY\nTO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, IN NO EVENT SHALL THE DEVELOPER BE LIABLE FOR ANY DIRECT, INDIRECT, SPECIAL, INCIDENTAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING OUT OF THE USE OF OR INABILITY TO USE THE SOFTWARE, REGARDLESS OF THE LEGAL THEORY (TORT, CONTRACT, OR OTHERWISE), EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.\n\n8. TERMINATION\nThis Agreement remains in effect until terminated. Your rights under this license terminate automatically without notice if you fail to comply with any of its terms. Upon termination, you must cease all use and uninstall all copies of the Software.'
    if os.path.exists(lic_file):
        try:
            with open(lic_file, "r", encoding="utf-8") as f:
                c = f.read()
                if c.strip():
                    raw_lic = c
        except Exception:
            pass

    win = QWidget()
    win.setWindowFlags(
        Qt.WindowType.SplashScreen |
        Qt.WindowType.FramelessWindowHint |
        Qt.WindowType.WindowStaysOnTopHint
    )
    win.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
    screen = app.primaryScreen()
    avail = screen.availableGeometry() if screen else app.screens()[0].availableGeometry()
    max_w, max_h = int(avail.width() * 0.92), int(avail.height() * 0.88)
    scale = min(1.0, max_w / 1280.0, max_h / 760.0)
    w, h = max(640, int(1280 * scale)), max(400, int(760 * scale))
    win_x = avail.x() + (avail.width() - w) // 2
    win_y = avail.y() + (avail.height() - h) // 2
    win.setGeometry(win_x, win_y, w, h)

    bg_lbl = QLabel(win)
    bg_lbl.setGeometry(0, 0, w, h)
    movie = None
    if os.path.exists(splash_gif):
        movie = QMovie(splash_gif, parent=win)
        movie.setScaledSize(QSize(w, h))
        bg_lbl.setMovie(movie)
        bg_lbl.setScaledContents(True)
        movie.jumpToFrame(0)
    else:
        bg_lbl.setStyleSheet("background-color: #FCFAF6; border-radius: 12px;")

    status_banner = QFrame(win)
    status_banner.setGeometry(140, h - 76, w - 280, 48)
    status_banner.setStyleSheet(
        "QFrame { background-color: rgba(254, 252, 248, 0.94); border: 1.5px solid rgba(212, 175, 55, 0.8); border-radius: 24px; }" +
        "QLabel { color: #851D1D; font-family: 'Segoe UI', sans-serif; font-size: 15px; font-weight: 700; }"
    )
    status_lay = QHBoxLayout(status_banner)
    status_lay.setContentsMargins(16, 6, 16, 6)
    status_lbl = QLabel("✨ Terms Accepted — Installing AstroBasics...", status_banner)
    status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    status_lay.addWidget(status_lbl)
    status_banner.hide()

    card = QFrame(win)
    card.setGeometry(48, 36, w - 96, h - 72)
    card.setStyleSheet(
        "QFrame#eulaCard { background-color: rgba(255, 253, 248, 0.95); border: 1.5px solid rgba(212, 175, 55, 0.7); border-radius: 16px; }" +
        "QLabel#titleLbl { color: #851D1D; font-family: 'Segoe UI', sans-serif; font-size: 22px; font-weight: bold; letter-spacing: 0.8px; }" +
        "QLabel#badgeLbl { background-color: rgba(212, 175, 55, 0.15); border: 1px solid rgba(212, 175, 55, 0.45); border-radius: 10px; color: #6E5316; font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600; padding: 4px 10px; }" +
        "QTextBrowser#eulaText { background-color: #FFFFFF; border: 1.5px solid #CBD5E1; border-radius: 10px; color: #0F172A; font-family: 'Segoe UI', Arial, sans-serif; font-size: 18px; line-height: 1.6; padding: 16px; }" +
        "QScrollBar:vertical { background: #FAF7F2; width: 8px; border-radius: 4px; } QScrollBar::handle:vertical { background: #D4AF37; border-radius: 4px; min-height: 24px; }" +
        "QPushButton#btnDecline { background-color: transparent; border: 1.5px solid #CBD5E1; border-radius: 8px; color: #64748B; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: 600; padding: 8px 22px; min-height: 36px; }" +
        "QPushButton#btnDecline:hover { background-color: #FEE2E2; border-color: #EF4444; color: #B91C1C; }" +
        "QPushButton#btnAccept { background-color: #851D1D; border: 1px solid #D4AF37; border-radius: 8px; color: #FFFDF8; font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: bold; padding: 8px 26px; min-height: 36px; }" +
        "QPushButton#btnAccept:hover { background-color: #9C2222; border-color: #F59E0B; }"
    )
    card.setObjectName("eulaCard")

    card_lay = QVBoxLayout(card)
    card_lay.setContentsMargins(26, 20, 26, 18)
    card_lay.setSpacing(12)

    hdr_lay = QHBoxLayout()
    title = QLabel("📜  EULA ", card)
    title.setObjectName("titleLbl")
    hdr_lay.addWidget(title)
    hdr_lay.addStretch()

    for b_text in ["🔒 Zero Telemetry"]:
        b = QLabel(b_text, card)
        b.setObjectName("badgeLbl")
        hdr_lay.addWidget(b)
    card_lay.addLayout(hdr_lay)

    eula_browser = QTextBrowser(card)
    eula_browser.setObjectName("eulaText")
    eula_browser.setPlainText(raw_lic)
    card_lay.addWidget(eula_browser)

    btn_lay = QHBoxLayout()
    btn_lay.setContentsMargins(0, 6, 0, 0)
    hint_lbl = QLabel("Please review and accept license terms to install AstroBasics.", card)
    hint_lbl.setStyleSheet("color: #475569; font-family: 'Segoe UI', sans-serif; font-size: 13px; font-weight: 600;")
    btn_lay.addWidget(hint_lbl)
    btn_lay.addStretch()

    btn_decline = QPushButton("Exit", card)
    btn_decline.setObjectName("btnDecline")
    btn_accept = QPushButton("I Agree✨", card)
    btn_accept.setObjectName("btnAccept")
    btn_lay.addWidget(btn_decline)
    btn_lay.addWidget(btn_accept)
    card_lay.addLayout(btn_lay)

    opacity_fx = QGraphicsOpacityEffect(card)
    card.setGraphicsEffect(opacity_fx)
    fade_anim = QPropertyAnimation(opacity_fx, b"opacity")
    fade_anim.setDuration(300)
    fade_anim.setStartValue(1.0)
    fade_anim.setEndValue(0.0)
    fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

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
                    temp_payload = os.path.join(os.environ.get("TEMP", os.environ.get("TMP", "C:\Temp")), "AstroBasics_payload_setup.exe")
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

    def on_card_hidden():
        card.hide()
        status_banner.show()
        if movie:
            movie.start()
        t = threading.Thread(target=_installer_thread_worker, daemon=True)
        t.start()

        def _poll_install_complete():
            if install_state[0]:
                if movie:
                    movie.stop()
                win.close()
                target_exe = os.path.join(os.environ.get("LOCALAPPDATA", ""), "AstroBasics", f"AstroBasics.exe")
                if os.path.isfile(target_exe):
                    subprocess.Popen([target_exe])
                if created_app:
                    app.quit()
                os._exit(0)
            else:
                QTimer.singleShot(100, _poll_install_complete)

        QTimer.singleShot(100, _poll_install_complete)

    fade_anim.finished.connect(on_card_hidden)

    def on_accept():
        btn_accept.setEnabled(False)
        btn_decline.setEnabled(False)
        fade_anim.start()

    def on_decline():
        if movie:
            movie.stop()
        win.close()
        if created_app:
            app.quit()
        os._exit(0)

    btn_accept.clicked.connect(on_accept)
    btn_decline.clicked.connect(on_decline)

    win.show()
    if created_app:
        app.exec()
    else:
        loop = QEventLoop()
        win.destroyed.connect(loop.quit)
        loop.exec()

if __name__ == "__main__":
    run_installer()

Here are the clean, precise find/replace blocks designed strictly for your file (`chart_renderer_4.py`). They implement the decoupled top-right status indicator, add the dynamic look-ahead forecasting engines, adjust the color-coding to include the conditional yellow state, and short-circuit the tooltips appropriately.

---

### ## Block 1: `paintEvent` Tri-State Rendering & Layout Decoupling

This block is added near the bottom of `paintEvent`. It positions the indicator circle near the absolute edge of the rendering space (`self.width()`), checks if the current canvas cell is the top-rightmost widget instance in the grid, and executes the conditional color logic.

```python
<<<<
                if self.show_aspects and self.show_arrows and self.chart_data and self.chart_data.get("aspects"):
                    asc_sign_idx = self.rotated_asc_sign_idx if getattr(self, 'rotated_asc_sign_idx', None) is not None else self.chart_data["ascendant"]["sign_index"]
                    for i, aspect in enumerate(self.chart_data["aspects"]):
                        is_node = aspect["aspecting_planet"] in ["Rahu", "Ketu"]
                        if aspect["aspecting_planet"] in self.visible_aspect_planets and (not is_node or self.show_rahu_ketu):
                            target_h_visual = ((((self.chart_data["ascendant"]["sign_index"] + aspect["target_house"] - 1) % 12) - asc_sign_idx) % 12) + 1
                            p_v = self.current_layout["planets"].get(aspect["aspecting_planet"])
                            h_v = self.current_layout["houses"].get(target_h_visual)
                            if p_v and h_v:
                                c = QColor(BRIGHT_COLORS.get(aspect["aspecting_planet"], QColor("#00ffff" if GLOBAL_DARK_MODE else 100)))
                                if GLOBAL_DARK_MODE: c = QColor.fromHsv(c.hsvHue(), 200, 255)
                                c.setAlpha(180 if GLOBAL_DARK_MODE else 150)
                                offset_x, offset_y = (i % 3 - 1) * 4, ((i + 1) % 3 - 1) * 4
                                x1, y1 = p_v["x"] + offset_x, p_v["y"] + offset_y
                                x2, y2 = h_v["x"] + offset_x, h_v["y"] + offset_y
                                dist = math.hypot(x2 - x1, y2 - y1)
                                if dist >= 70:
                                    sx, sy = x1 + ((x2 - x1) / dist) * 35, y1 + ((y2 - y1) / dist) * 35
                                    ex, ey = x2 - ((x2 - x1) / dist) * 35, y2 - ((y2 - y1) / dist) * 35
                                    active_painter.setPen(QPen(c, max(2.5 if GLOBAL_DARK_MODE else 1.5, w * 0.007), Qt.PenStyle.SolidLine))
                                    active_painter.drawLine(int(sx), int(sy), int(ex), int(ey))
                                    angle = math.atan2(ey - sy, ex - sx)
                                    active_painter.setBrush(QBrush(c))
                                    active_painter.setPen(Qt.PenStyle.NoPen)
                                    arrow_pts = [QPointF(ex, ey), QPointF(ex - 9 * math.cos(angle - math.pi / 6), ey - 9 * math.sin(angle - math.pi / 6)), QPointF(ex - 9 * math.cos(angle + math.pi / 6), ey - 9 * math.sin(angle + math.pi / 6))]
                                    active_painter.drawPolygon(QPolygonF(arrow_pts))
                if not is_animating: active_painter.end()

            if not is_animating and getattr(self, '_fg_cache', None):
                painter.drawPixmap(0, 0, self._fg_cache)

        finally:
            painter.end()
====
                if self.show_aspects and self.show_arrows and self.chart_data and self.chart_data.get("aspects"):
                    asc_sign_idx = self.rotated_asc_sign_idx if getattr(self, 'rotated_asc_sign_idx', None) is not None else self.chart_data["ascendant"]["sign_index"]
                    for i, aspect in enumerate(self.chart_data["aspects"]):
                        is_node = aspect["aspecting_planet"] in ["Rahu", "Ketu"]
                        if aspect["aspecting_planet"] in self.visible_aspect_planets and (not is_node or self.show_rahu_ketu):
                            target_h_visual = ((((self.chart_data["ascendant"]["sign_index"] + aspect["target_house"] - 1) % 12) - asc_sign_idx) % 12) + 1
                            p_v = self.current_layout["planets"].get(aspect["aspecting_planet"])
                            h_v = self.current_layout["houses"].get(target_h_visual)
                            if p_v and h_v:
                                c = QColor(BRIGHT_COLORS.get(aspect["aspecting_planet"], QColor("#00ffff" if GLOBAL_DARK_MODE else 100)))
                                if GLOBAL_DARK_MODE: c = QColor.fromHsv(c.hsvHue(), 200, 255)
                                c.setAlpha(180 if GLOBAL_DARK_MODE else 150)
                                offset_x, offset_y = (i % 3 - 1) * 4, ((i + 1) % 3 - 1) * 4
                                x1, y1 = p_v["x"] + offset_x, p_v["y"] + offset_y
                                x2, y2 = h_v["x"] + offset_x, h_v["y"] + offset_y
                                dist = math.hypot(x2 - x1, y2 - y1)
                                if dist >= 70:
                                    sx, sy = x1 + ((x2 - x1) / dist) * 35, y1 + ((y2 - y1) / dist) * 35
                                    ex, ey = x2 - ((x2 - x1) / dist) * 35, y2 - ((y2 - y1) / dist) * 35
                                    active_painter.setPen(QPen(c, max(2.5 if GLOBAL_DARK_MODE else 1.5, w * 0.007), Qt.PenStyle.SolidLine))
                                    active_painter.drawLine(int(sx), int(sy), int(ex), int(ey))
                                    angle = math.atan2(ey - sy, ex - sx)
                                    active_painter.setBrush(QBrush(c))
                                    active_painter.setPen(Qt.PenStyle.NoPen)
                                    arrow_pts = [QPointF(ex, ey), QPointF(ex - 9 * math.cos(angle - math.pi / 6), ey - 9 * math.sin(angle - math.pi / 6)), QPointF(ex - 9 * math.cos(angle + math.pi / 6), ey - 9 * math.sin(angle + math.pi / 6))]
                                    active_painter.drawPolygon(QPolygonF(arrow_pts))
                if not is_animating: active_painter.end()

            if not is_animating and getattr(self, '_fg_cache', None):
                painter.drawPixmap(0, 0, self._fg_cache)

            # --- Unified Kshaurakarma (Shaving/Haircut) Indicator ---
            if getattr(self, "chart_data", None):
                try:
                    win = self.window()
                    is_top_right_chart = False
                    if hasattr(win, 'active_charts_order') and win.active_charts_order:
                        mode_str = win._get_eng_combo_text(win.cb_layout_mode) if hasattr(win, 'cb_layout_mode') else "3 Columns"
                        num_charts = len(win.active_charts_order)
                        if mode_str == "1 Left, 2 Right (Stacked)":
                            target_idx = 1 if num_charts > 1 else 0
                        elif mode_str == "2 Columns":
                            target_idx = min(1, num_charts - 1)
                        else:
                            target_idx = min(2, num_charts - 1)
                        if win.div_titles.get(win.active_charts_order[target_idx]) == self.title:
                            is_top_right_chart = True
                    
                    if is_top_right_chart:
                        import datetime
                        self.shaving_rect = QRectF(self.width() - 45, 15, 30, 30)
                        dt_d = astro_engine.jd_to_ymdhms(self.chart_data["current_jd"])
                        idx_day = datetime.date(int(dt_d['year']), int(dt_d['month']), int(dt_d['day'])).weekday()
                        
                        panchang = self.chart_data.get("panchang", {})
                        s_lon = panchang.get("sun_lon", 0)
                        m_lon = panchang.get("moon_lon", 0)
                        
                        angle_diff = (m_lon - s_lon) % 360.0
                        tithi_index = max(0, min(29, int(angle_diff / 12.0)))
                        tithi_names = [
                            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
                            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", 
                            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
                            "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
                            "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", 
                            "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
                        ]
                        tithi = tithi_names[tithi_index]
                        total_yoga_lon = (s_lon + m_lon) % 360
                        
                        is_forbidden = (tithi in ["Ekadashi", "Chaturdashi", "Amavasya", "Purnima"] or 
                                        (s_lon % 30) < 1.0 or 
                                        (226.66 <= total_yoga_lon <= 240.0) or 
                                        idx_day in [1, 5, 6])
                        
                        is_debated = False
                        if not is_forbidden:
                            is_debated = (idx_day == 0 or tithi in ["Pratipada", "Shashthi", "Ashtami", "Navami", "Dwadashi", "Trayodashi"])
                        
                        ind_color = QColor("#FF003C") if is_forbidden else (QColor("#FFD700") if is_debated else QColor("#39FF14"))
                        painter.save()
                        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                        
                        # Ambient Outer Glow Ring
                        radial_grad = QRadialGradient(QPointF(self.width() - 30, 30), 15)
                        radial_grad.setColorAt(0.0, QColor(ind_color.red(), ind_color.green(), ind_color.blue(), 180))
                        radial_grad.setColorAt(1.0, QColor(ind_color.red(), ind_color.green(), ind_color.blue(), 0))
                        painter.setPen(Qt.PenStyle.NoPen)
                        painter.setBrush(QBrush(radial_grad))
                        painter.drawEllipse(QPointF(self.width() - 30, 30), 15, 15)
                        
                        # Core Solid Node
                        painter.setBrush(QBrush(ind_color))
                        painter.setPen(QPen(Qt.GlobalColor.white, 1.5))
                        painter.drawEllipse(QPointF(self.width() - 30, 30), 6, 6)
                        painter.restore()
                    else:
                        self.shaving_rect = None
                except Exception:
                    pass

        finally:
            painter.end()
>>>>

```

---

### ## Block 2: `_update_tooltip` Interaction Interception & Dual Timeline Forecasting

This block intercepts widget mouse tracks inside `_update_tooltip`. It bypasses minor checks completely if a critical prohibition is active, integrates minor rules directly into a single unified tooltip text flow, and parses out sequential calendar forecasts.

```python
<<<<
        def _update_tooltip(self, pos):
            from translator import _, N_
            tooltip_lbl = self._get_safe_tooltip() # Grab safe instance
            
        if not (self.SHOW_PLANET_TOOLTIPS or self.SHOW_HOUSE_TOOLTIPS) or not self.chart_data or not self.current_layout: 
            tooltip_lbl.hide()
            self._last_hovered_id = None
            return

        pos_point = QPointF(pos.x(), pos.y())
        
        # Intercept for Shaving Indicator Hitboxes
        is_shaving_hover = getattr(self, 'shaving_rect', None) and self.shaving_rect.contains(pos_point)
        is_debated_hover = getattr(self, 'debated_shaving_rect', None) and self.debated_shaving_rect.contains(pos_point)
        
        if is_shaving_hover or is_debated_hover:
            hovered_id = "shaving_primary" if is_shaving_hover else "shaving_debated"
            if hovered_id != self._last_hovered_id:
                self._last_hovered_id = hovered_id
                import datetime
                win = self.window()
                engine = win.ephemeris
                lat = win.current_lat
                lon = win.current_lon
                
                dt_d = astro_engine.jd_to_ymdhms(self.chart_data["current_jd"])
                idx_day = datetime.date(int(dt_d['year']), int(dt_d['month']), int(dt_d['day'])).weekday()
                
                panchang = self.chart_data.get("panchang", {})
                s_lon = panchang.get("sun_lon", 0)
                m_lon = panchang.get("moon_lon", 0)
                
                angle_diff = (m_lon - s_lon) % 360.0
                tithi_index = max(0, min(29, int(angle_diff / 12.0)))
                tithi_names = [
                    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
                    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", 
                    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
                    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
                    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", 
                    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
                ]
                tithi = tithi_names[tithi_index]
                total_yoga_lon = (s_lon + m_lon) % 360
                
                reasons = []
                if tithi in ["Ekadashi", "Chaturdashi", "Amavasya", "Purnima"]:
                    reasons.append(f"Forbidden on {tithi}")
                if (s_lon % 30) < 1.0:
                    reasons.append("Forbidden on Sankranti (Sun enters new sign)")
                if 226.66 <= total_yoga_lon <= 240.0:
                    reasons.append("Forbidden during Vyatipata Yoga period")
                if idx_day == 1:
                    reasons.append("Forbidden on Tuesday (Reduces lifespan by 8 months)")
                elif idx_day == 5:
                    reasons.append("Forbidden on Saturday (Reduces lifespan by 7 months)")
                elif idx_day == 6:
                    reasons.append("Restricted on Sunday (Reduces lifespan by 1 month)")
                
                minor_warnings = []
                if idx_day == 0:
                    minor_warnings.append("shaving/haircut leads to loss of dharma today")
                if tithi in ["Pratipada", "Shashthi", "Ashtami", "Navami", "Dwadashi", "Trayodashi"]:
                    minor_warnings.append(f"Debated configuration or mixed influence on {tithi}")
                
                # Dynamic Look-Ahead Ephemeris Sequence for Allowed Date (Must clear both critical and minor/debated parameters)
                next_allowed_date = "N/A"
                check_jd = self.chart_data["current_jd"] + 1.0
                for _ in range(30):
                    c_dt = astro_engine.jd_to_ymdhms(check_jd)
                    c_day = datetime.date(int(c_dt['year']), int(c_dt['month']), int(c_dt['day'])).weekday()
                    if c_day not in [0, 1, 5, 6]:
                        p_c = engine.get_panchang(check_jd, lat, lon)
                        c_sun = p_c.get("sun_lon", 0)
                        c_moon = p_c.get("moon_lon", 0)
                        
                        c_diff = (c_moon - c_sun) % 360.0
                        c_tithi_idx = max(0, min(29, int(c_diff / 12.0)))
                        c_tithi = tithi_names[c_tithi_idx]
                        c_yoga = (c_sun + c_moon) % 360
                        
                        if not (c_tithi in ["Ekadashi", "Chaturdashi", "Amavasya", "Purnima", "Pratipada", "Shashthi", "Ashtami", "Navami", "Dwadashi", "Trayodashi"] or 
                                (c_sun % 30) < 1.0 or 
                                (226.66 <= c_yoga <= 240.0)):
                            next_allowed_date = f"{int(c_dt['year'])}-{int(c_dt['month']):02d}-{int(c_dt['day']):02d}"
                            break
                    check_jd += 1.0
                
                if is_shaving_hover:
                    html = "<b>Kshaurakarma (Shaving/Haircut) Status:</b><br>"
                    if reasons:
                        html += "<span style='color:#FF003C;'><b>NOT ALLOWED TODAY</b></span><br><br>"
                        html += "<b>Critical Prohibitions:</b><br>" + "<br>".join([f"• {r}" for r in reasons])
                    else:
                        html += "<span style='color:#39FF14;'><b>ALLOWED TODAY</b></span><br><br>"
                        html += "No classical critical restrictions are active."
                else:
                    html = "<b>Kshaurakarma Debated Configurations:</b><br>"
                    if minor_warnings:
                        html += "<span style='color:#FFD700;'><b>CONCURRENT WARNINGS ACTIVE</b></span><br><br>"
                        html += "<b>Textual Assertions:</b><br>" + "<br>".join([f"• {w}" for w in minor_warnings])
                    else:
                        html += "<span style='color:#39FF14;'><b>CLEAR</b></span><br><br>"
                        html += "No minor or debated warnings are active for this configuration."
                        
                html += f"<br><br><b>Next Fully Permitted Date:</b> <span style='color:#39FF14;'><b>{next_allowed_date}</b></span>"
                tooltip_lbl.setText(html)
                tooltip_lbl.adjustSize()
            
            global_pos = self.mapToGlobal(pos_point.toPoint())
            new_x, new_y = global_pos.x() + 15, global_pos.y() + 15
            if screen := self.screen():
                sg = screen.availableGeometry()
                if new_x + tooltip_lbl.width() > sg.right(): new_x = global_pos.x() - tooltip_lbl.width() - 5
                if new_y + tooltip_lbl.height() > sg.bottom(): new_y = global_pos.y() - tooltip_lbl.height() - 5
            tooltip_lbl.move(new_x, new_y)
            tooltip_lbl.show()
            tooltip_lbl.raise_()
            return

        hovered_id, hovered_data, hovered_type = None, None, None

        if self.SHOW_PLANET_TOOLTIPS:
====
        # Intercept for Shaving Indicator Hitbox
        if getattr(self, 'shaving_rect', None) and self.shaving_rect.contains(pos_point):
            hovered_id = "shaving_indicator"
            if hovered_id != self._last_hovered_id:
                self._last_hovered_id = hovered_id
                import datetime
                win = self.window()
                engine = win.ephemeris
                lat = win.current_lat
                lon = win.current_lon
                
                dt_d = astro_engine.jd_to_ymdhms(self.chart_data["current_jd"])
                idx_day = datetime.date(int(dt_d['year']), int(dt_d['month']), int(dt_d['day'])).weekday()
                
                panchang = self.chart_data.get("panchang", {})
                s_lon = panchang.get("sun_lon", 0)
                m_lon = panchang.get("moon_lon", 0)
                
                angle_diff = (m_lon - s_lon) % 360.0
                tithi_index = max(0, min(29, int(angle_diff / 12.0)))
                tithi_names = [
                    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
                    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", 
                    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
                    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", 
                    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami", 
                    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya"
                ]
                tithi = tithi_names[tithi_index]
                total_yoga_lon = (s_lon + m_lon) % 360
                
                reasons = []
                if tithi in ["Ekadashi", "Chaturdashi", "Amavasya", "Purnima"]:
                    reasons.append(f"Forbidden on {tithi}")
                if (s_lon % 30) < 1.0:
                    reasons.append("Forbidden on Sankranti (Sun enters new sign)")
                if 226.66 <= total_yoga_lon <= 240.0:
                    reasons.append("Forbidden during Vyatipata Yoga period")
                if idx_day == 1:
                    reasons.append("Forbidden on Tuesday (Reduces lifespan by 8 months)")
                elif idx_day == 5:
                    reasons.append("Forbidden on Saturday (Reduces lifespan by 7 months)")
                elif idx_day == 6:
                    reasons.append("Restricted on Sunday (Reduces lifespan by 1 month)")
                
                # Check for minor/debated parameters only if clear of critical prohibitions
                minor_warnings = []
                if not reasons:
                    if idx_day == 0:
                        minor_warnings.append("shaving/haircut leads to loss of dharma today (Monday)")
                    if tithi in ["Pratipada", "Shashthi", "Ashtami", "Navami", "Dwadashi", "Trayodashi"]:
                        minor_warnings.append(f"Debated configuration or mixed influence on {tithi}")
                
                # Dynamic Dual Look-Ahead Ephemeris Search Sequence
                next_permitted_date = "N/A"
                next_fully_permitted_date = "N/A"
                
                # Look ahead for Next Permitted Date (Clears critical rules, minor warnings allowed)
                check_jd = self.chart_data["current_jd"] + 1.0
                for _ in range(30):
                    c_dt = astro_engine.jd_to_ymdhms(check_jd)
                    c_day = datetime.date(int(c_dt['year']), int(c_dt['month']), int(c_dt['day'])).weekday()
                    if c_day not in [1, 5, 6]:
                        p_c = engine.get_panchang(check_jd, lat, lon)
                        c_sun = p_c.get("sun_lon", 0)
                        c_moon = p_c.get("moon_lon", 0)
                        c_diff = (c_moon - c_sun) % 360.0
                        c_tithi_idx = max(0, min(29, int(c_diff / 12.0)))
                        c_tithi = tithi_names[c_tithi_idx]
                        c_yoga = (c_sun + c_moon) % 360
                        
                        if not (c_tithi in ["Ekadashi", "Chaturdashi", "Amavasya", "Purnima"] or 
                                (c_sun % 30) < 1.0 or 
                                (226.66 <= c_yoga <= 240.0)):
                            next_permitted_date = f"{int(c_dt['year'])}-{int(c_dt['month']):02d}-{int(c_dt['day']):02d}"
                            break
                    check_jd += 1.0

                # Look ahead for Next Fully Permitted Date (Must clear both critical and minor constraints)
                check_jd = self.chart_data["current_jd"] + 1.0
                for _ in range(30):
                    c_dt = astro_engine.jd_to_ymdhms(check_jd)
                    c_day = datetime.date(int(c_dt['year']), int(c_dt['month']), int(c_dt['day'])).weekday()
                    if c_day not in [0, 1, 5, 6]:
                        p_c = engine.get_panchang(check_jd, lat, lon)
                        c_sun = p_c.get("sun_lon", 0)
                        c_moon = p_c.get("moon_lon", 0)
                        c_diff = (c_moon - c_sun) % 360.0
                        c_tithi_idx = max(0, min(29, int(c_diff / 12.0)))
                        c_tithi = tithi_names[c_tithi_idx]
                        c_yoga = (c_sun + c_moon) % 360
                        
                        if not (c_tithi in ["Ekadashi", "Chaturdashi", "Amavasya", "Purnima", "Pratipada", "Shashthi", "Ashtami", "Navami", "Dwadashi", "Trayodashi"] or 
                                (c_sun % 30) < 1.0 or 
                                (226.66 <= c_yoga <= 240.0)):
                            next_fully_permitted_date = f"{int(c_dt['year'])}-{int(c_dt['month']):02d}-{int(c_dt['day']):02d}"
                            break
                    check_jd += 1.0
                
                html = "<b>Kshaurakarma (Shaving/Haircut) Rules:</b><br>"
                if reasons:
                    html += "<span style='color:#FF003C;'><b>NOT ALLOWED TODAY</b></span><br><br>"
                    html += "<b>Critical Prohibitions:</b><br>" + "<br>".join([f"• {r}" for r in reasons])
                elif minor_warnings:
                    html += "<span style='color:#FFD700;'><b>DEBATED / WARNING ACTIVE</b></span><br><br>"
                    html += "<b>Minor Warnings:</b><br>" + "<br>".join([f"• {w}" for w in minor_warnings])
                else:
                    html += "<span style='color:#39FF14;'><b>ALLOWED TODAY</b></span><br><br>"
                    html += "Shaving/Haircut allowed today."
                
                html += f"<br><br><b>Next Permitted Date:</b> <span style='color:#FFD700;'><b>{next_permitted_date}</b></span>"
                html += f"<br><b>Next Fully Permitted Date:</b> <span style='color:#39FF14;'><b>{next_fully_permitted_date}</b></span>"
                tooltip_lbl.setText(html)
                tooltip_lbl.adjustSize()
            
            global_pos = self.mapToGlobal(pos_point.toPoint())
            new_x, new_y = global_pos.x() + 15, global_pos.y() + 15
            if screen := self.screen():
                sg = screen.availableGeometry()
                if new_x + tooltip_lbl.width() > sg.right(): new_x = global_pos.x() - tooltip_lbl.width() - 5
                if new_y + tooltip_lbl.height() > sg.bottom(): new_y = global_pos.y() - tooltip_lbl.height() - 5
            tooltip_lbl.move(new_x, new_y)
            tooltip_lbl.show()
            tooltip_lbl.raise_()
            return

        hovered_id, hovered_data, hovered_type = None, None, None

        if self.SHOW_PLANET_TOOLTIPS:

```

---

### Verification Checklist

* **Grid Decoupling**: Position references look at `self.width() - 45` instead of chart boundary offsets `x` and `w`.


* **Single Rendering**: Grid coordinate mapping guarantees computation occurs solely on the active top-right panel instance.


* **Tithi Safety**: Derived values use direct math checks to protect against static Purnima display issues.


* **Look-Ahead Engine**: Displays both `Next Permitted Date` and `Next Fully Permitted Date` variants clearly.
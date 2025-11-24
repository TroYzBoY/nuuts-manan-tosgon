"""
🚀 FACE LOCK SYSTEM

- Tkinter дээр нүүр танилт (OpenCV, Deep Features)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
from PIL import Image, ImageTk
import pickle
import time
from datetime import datetime
import numpy as np
import os
from collections import Counter
import threading
import json
import platform
import sys
import subprocess


# ======================================================================
#                      FACE RECOGNITION (Tkinter)
# ======================================================================

class EnhancedFaceRecognitionSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Face Lock + Game Launcher")
        self.root.geometry("1200x700")

        # OS
        self.is_macos = platform.system() == 'Darwin'
        self.is_windows = platform.system() == 'Windows'

        # Colors
        self.bg_dark = '#0a0e27'
        self.bg_panel = '#1a1f3a'
        self.fg_primary = '#00ff9f'
        self.fg_secondary = '#ffffff'
        self.fg_muted = '#666699'
        self.root.configure(bg=self.bg_dark)

        # Face data - folder structure байгуулах
        self.face_data_dir = "face_data"
        if not os.path.exists(self.face_data_dir):
            os.makedirs(self.face_data_dir)
        
        # Person data structure: {person_id: {'name': str, 'features': [], 'quality_scores': [], 'registered_at': str}}
        self.person_data = {}
        self.known_face_features = []  # Backward compatibility
        self.known_face_names = []  # Backward compatibility
        self.face_quality_scores = []  # Backward compatibility
        self.person_ids = []  # Person ID for each feature
        self.data_file = "enhanced_face_data.pkl"
        self.threshold = 0.65

        # OpenCV
        cascade_path = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_eye.xml')

        # Video
        self.video_capture = None
        self.is_capturing = False
        self.current_mode = None
        self.fps = 0

        # Game unlock flags
        self.face_recognized = False
        self.recognized_name = None

        self.setup_ui()
        self.load_person_data_from_folders()
        self.load_data_silent()

        # ПРОГРАМ ЭХЛЭХЭД АВТОМААТАР ТАНИЛТ ЭХЛҮҮЛНЭ
        self.root.after(800, self.auto_start_recognition)

    # ---------- UI / Helper ----------

    def auto_start_recognition(self):
        """Програм асахад автоматаар танилт эхлүүлэх"""
        # Хэрэв дата байвал шууд танилт эхлүүлнэ
        if self.known_face_names:
            self.start_recognition()
        else:
            self.update_status(
                "⚠️ Дата байхгүй, эхлээд 'Нүүр бүртгэх' ашиглан бүртгэнэ үү.")

    def get_font(self, size, weight='normal'):
        if self.is_macos:
            try:
                if weight == 'bold':
                    return ('SF Pro Display', size, 'bold')
                else:
                    return ('SF Pro Text', size)
            except:
                if weight == 'bold':
                    return ('Helvetica Neue', size, 'bold')
                else:
                    return ('Helvetica Neue', size)
        elif self.is_windows:
            if weight == 'bold':
                return ('Segoe UI', size, 'bold')
            else:
                return ('Segoe UI', size)
        else:
            return ('DejaVu Sans', size, weight)

    def setup_ui(self):
        # Title bar
        title_frame = tk.Frame(self.root, bg=self.bg_panel, height=90)
        title_frame.pack(fill='x', pady=(0, 10))

        title_label = tk.Label(
            title_frame,
            text="🚀 FACE LOCK - GAME LAUNCHER",
            font=self.get_font(26, 'bold'),
            bg=self.bg_panel,
            fg=self.fg_primary
        )
        title_label.pack(pady=15)

        mode_label = tk.Label(
            title_frame,
            text="🟢 Нүүр танилт амжилттай болсны дараа тоглоом эхэлнэ",
            font=self.get_font(10, 'bold'),
            bg=self.bg_panel,
            fg=self.fg_primary
        )
        mode_label.pack()

        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_dark)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Left panel with scrollbar
        left_panel_frame = tk.Frame(main_container, bg=self.bg_panel, width=380)
        left_panel_frame.pack(side='left', fill='both', padx=(0, 10))
        
        # Canvas for scrolling
        left_canvas = tk.Canvas(
            left_panel_frame, bg=self.bg_panel,
            highlightthickness=0, borderwidth=0, width=380
        )
        left_scrollbar = tk.Scrollbar(
            left_panel_frame, orient='vertical',
            command=left_canvas.yview,
            bg=self.bg_panel,
            troughcolor=self.bg_panel,
            activebackground=self.fg_primary,
            width=12
        )
        left_panel = tk.Frame(left_canvas, bg=self.bg_panel, width=380)
        
        # Scrollable region update function
        def update_scroll_region(event=None):
            left_canvas.update_idletasks()
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
        
        left_panel.bind("<Configure>", update_scroll_region)
        
        # Create window in canvas
        canvas_window = left_canvas.create_window((0, 0), window=left_panel, anchor="nw")
        
        # Update canvas width when panel width changes
        def configure_canvas_width(event):
            canvas_width = event.width
            left_canvas.itemconfig(canvas_window, width=canvas_width)
        
        left_canvas.bind('<Configure>', configure_canvas_width)
        left_canvas.configure(yscrollcommand=left_scrollbar.set)
        
        # Pack canvas and scrollbar
        left_canvas.pack(side='left', fill='both', expand=True)
        left_scrollbar.pack(side='right', fill='y')
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            # Windows/Linux
            if event.delta:
                left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def on_mousewheel_mac(event):
            # macOS
            left_canvas.yview_scroll(-1, "units")
        
        def on_mousewheel_mac_down(event):
            # macOS
            left_canvas.yview_scroll(1, "units")
        
        # Bind mouse wheel to canvas and root
        left_canvas.bind("<MouseWheel>", on_mousewheel)
        if self.is_macos:
            left_canvas.bind("<Button-4>", on_mousewheel_mac)
            left_canvas.bind("<Button-5>", on_mousewheel_mac_down)
        
        # Also bind to root for better scrolling experience
        self.root.bind_all("<MouseWheel>", lambda e: on_mousewheel(e) if left_canvas.winfo_containing(e.x_root, e.y_root) else None)

        # Control buttons
        control_frame = tk.LabelFrame(
            left_panel,
            text="⚡ Үндсэн үйлдлүүд",
            font=self.get_font(12, 'bold'),
            bg=self.bg_panel,
            fg=self.fg_secondary,
            padx=15,
            pady=15,
            relief='flat' if self.is_macos else 'groove',
            borderwidth=1
        )
        control_frame.pack(fill='x', pady=10, padx=10)

        self.register_btn = self.create_button(
            control_frame, "🤖 Нүүр бүртгэх", self.start_registration, '#00ff9f')
        if self.is_macos and hasattr(self.register_btn, '_frame'):
            self.register_btn._frame.pack(fill='x', pady=5)
        else:
            self.register_btn.pack(fill='x', pady=5)

        self.recognize_btn = self.create_button(
            control_frame, "🎥 Танилт эхлүүлэх", self.start_recognition, '#00aaff')
        if self.is_macos and hasattr(self.recognize_btn, '_frame'):
            self.recognize_btn._frame.pack(fill='x', pady=5)
        else:
            self.recognize_btn.pack(fill='x', pady=5)

        self.stop_btn = self.create_button(
            control_frame, "⏹️ Зогсоох", self.stop_capture, '#ff4466')
        if self.is_macos and hasattr(self.stop_btn, '_frame'):
            self.stop_btn._frame.pack(fill='x', pady=5)
        else:
            self.stop_btn.pack(fill='x', pady=5)
        self.stop_btn.config(state='disabled')

        # GAME BUTTON – танигдсаны дараа идэвхжиж тоглоом эхлүүлнэ
        self.game_btn = self.create_button(
            control_frame, "🎮 Тоглоом эхлүүлэх", self.launch_game_from_button, '#ff9500')
        if self.is_macos and hasattr(self.game_btn, '_frame'):
            self.game_btn._frame.pack(fill='x', pady=5)
        else:
            self.game_btn.pack(fill='x', pady=5)
        self.game_btn.config(state='disabled')

        # Advanced settings
        advanced_frame = tk.LabelFrame(
            left_panel,
            text="🎛️ Нарийвчилсан тохиргоо",
            font=self.get_font(12, 'bold'),
            bg=self.bg_panel,
            fg=self.fg_secondary,
            padx=15,
            pady=15,
            relief='flat' if self.is_macos else 'groove',
            borderwidth=1
        )
        advanced_frame.pack(fill='x', pady=10, padx=10)

        checkbutton_bg = self.bg_panel
        checkbutton_fg = self.fg_secondary
        checkbutton_select = '#2a2f4a' if not self.is_macos else '#3a3f5a'

        self.multi_angle_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_frame, text="📐 Олон өнцгөөс авах",
            variable=self.multi_angle_var, bg=checkbutton_bg, fg=checkbutton_fg,
            selectcolor=checkbutton_select, font=self.get_font(10),
            activebackground=checkbutton_bg, activeforeground=checkbutton_fg
        ).pack(anchor='w', pady=3)

        self.quality_filter_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_frame, text="✨ Чанарын шүүлтүүр",
            variable=self.quality_filter_var, bg=checkbutton_bg, fg=checkbutton_fg,
            selectcolor=checkbutton_select, font=self.get_font(10),
            activebackground=checkbutton_bg, activeforeground=checkbutton_fg
        ).pack(anchor='w', pady=3)

        self.deep_features_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_frame, text="🧠 Deep features (LBP+HOG+ORB)",
            variable=self.deep_features_var, bg=checkbutton_bg, fg=checkbutton_fg,
            selectcolor=checkbutton_select, font=self.get_font(10),
            activebackground=checkbutton_bg, activeforeground=checkbutton_fg
        ).pack(anchor='w', pady=3)

        self.show_confidence_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            advanced_frame, text="📊 Confidence bar",
            variable=self.show_confidence_var, bg=checkbutton_bg, fg=checkbutton_fg,
            selectcolor=checkbutton_select, font=self.get_font(10),
            activebackground=checkbutton_bg, activeforeground=checkbutton_fg
        ).pack(anchor='w', pady=3)

        # Data management
        data_frame = tk.LabelFrame(
            left_panel, text="💾 Дата удирдлага",
            font=self.get_font(12, 'bold'),
            bg=self.bg_panel, fg=self.fg_secondary, padx=15, pady=15,
            relief='flat' if self.is_macos else 'groove',
            borderwidth=1
        )
        data_frame.pack(fill='x', pady=10, padx=10)

        buttons = [
            ("📂 Дата ачаалах", self.load_data, '#9966ff'),
            ("💾 Дата хадгалах", self.save_data, '#9966ff'),
            ("📤 Export JSON", self.export_json, '#ff9500'),
            ("📥 Import зураг", self.import_from_folder, '#ff9500'),
            ("👥 Хүмүүсийг харах", self.show_people_list, '#00aaff'),
            ("📈 Статистик", self.show_statistics, '#00aaff'),
            ("🗑️ Хүн устгах", self.delete_person, '#ff4466'),
        ]
        for text, cmd, color in buttons:
            btn = self.create_button(data_frame, text, cmd, color)
            if self.is_macos and hasattr(btn, '_frame'):
                btn._frame.pack(fill='x', pady=3)
            else:
                btn.pack(fill='x', pady=3)

        # Settings
        settings_frame = tk.LabelFrame(
            left_panel, text="⚙️ Тохиргоо",
            font=self.get_font(12, 'bold'),
            bg=self.bg_panel, fg=self.fg_secondary, padx=15, pady=15,
            relief='flat' if self.is_macos else 'groove',
            borderwidth=1
        )
        settings_frame.pack(fill='x', pady=10, padx=10)

        tk.Label(settings_frame, text="Threshold утга:",
                 bg=self.bg_panel, fg=self.fg_secondary, font=self.get_font(10)).pack(anchor='w')

        self.threshold_var = tk.DoubleVar(value=self.threshold)
        threshold_slider = ttk.Scale(
            settings_frame, from_=0.50, to=0.85,
            variable=self.threshold_var, orient='horizontal',
            command=self.update_threshold
        )
        threshold_slider.pack(fill='x', pady=5)

        self.threshold_label = tk.Label(
            settings_frame, text=f"Утга: {self.threshold:.2f}",
            bg=self.bg_panel, fg=self.fg_primary, font=self.get_font(9, 'bold')
        )
        self.threshold_label.pack()

        # Status display
        status_frame = tk.LabelFrame(
            left_panel, text="📊 Систем мэдээлэл",
            font=self.get_font(12, 'bold'),
            bg=self.bg_panel, fg=self.fg_secondary, padx=15, pady=15,
            relief='flat' if self.is_macos else 'groove',
            borderwidth=1
        )
        status_frame.pack(fill='both', expand=True, pady=10, padx=10)

        # Status text container with scrollbar
        status_text_container = tk.Frame(status_frame, bg=self.bg_panel)
        status_text_container.pack(fill='both', expand=True)

        monospace_font = 'Menlo' if self.is_macos else (
            'Consolas' if self.is_windows else 'Monaco')
        self.status_text = tk.Text(
            status_text_container, height=12, bg=self.bg_dark, fg=self.fg_primary,
            font=(monospace_font, 9), wrap='word', state='disabled',
            borderwidth=0, highlightthickness=0,
            insertbackground=self.fg_primary
        )
        
        # Scrollbar
        status_scrollbar = tk.Scrollbar(
            status_text_container, orient='vertical',
            command=self.status_text.yview,
            bg=self.bg_panel,
            troughcolor=self.bg_panel,
            activebackground=self.fg_primary,
            width=12
        )
        self.status_text.config(yscrollcommand=status_scrollbar.set)
        
        # Pack scrollbar and text
        self.status_text.pack(side='left', fill='both', expand=True)
        status_scrollbar.pack(side='right', fill='y')

        # Right panel - video
        right_panel = tk.Frame(main_container, bg=self.bg_panel)
        right_panel.pack(side='right', fill='both', expand=True)

        video_frame = tk.LabelFrame(
            right_panel, text="📹 Видео харагдац",
            font=self.get_font(12, 'bold'),
            bg=self.bg_panel, fg=self.fg_secondary,
            relief='flat' if self.is_macos else 'groove',
            borderwidth=1
        )
        video_frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.video_label = tk.Label(
            video_frame, bg=self.bg_dark,
            text="🎥 Видео зогссон байна\n\n✨ Танилт автоматаар эхлэх болно...",
            font=self.get_font(14), fg=self.fg_muted
        )
        self.video_label.pack(fill='both', expand=True, padx=10, pady=10)

        # Info bar
        info_frame = tk.Frame(right_panel, bg=self.bg_panel, height=40)
        info_frame.pack(fill='x', padx=10, pady=(0, 10))

        self.info_label = tk.Label(
            info_frame, text="⚡ Бэлэн",
            font=self.get_font(10), bg=self.bg_panel, fg=self.fg_primary
        )
        self.info_label.pack(side='left', padx=10, pady=5)

        self.update_status_display()

    def create_button(self, parent, text, command, color):
        if self.is_macos:
            btn_frame = tk.Frame(
                parent, bg=color, relief='flat', borderwidth=0)
            btn = tk.Button(
                btn_frame, text=text, command=command,
                bg=color, fg='#ffffff', font=self.get_font(11, 'bold'),
                relief='flat', cursor='hand2', height=2,
                activebackground=self.lighten_color(color),
                activeforeground='#ffffff',
                borderwidth=0, highlightthickness=0,
                highlightbackground=color,
                highlightcolor=color
            )
            btn.pack(fill='both', expand=True)

            def on_enter(e):
                btn_frame.config(bg=self.lighten_color(color))
                btn.config(bg=self.lighten_color(color),
                           activebackground=self.lighten_color(color),
                           highlightbackground=self.lighten_color(color))

            def on_leave(e):
                btn_frame.config(bg=color)
                btn.config(bg=color,
                           activebackground=self.lighten_color(color),
                           highlightbackground=color)

            btn_frame.bind('<Enter>', on_enter)
            btn_frame.bind('<Leave>', on_leave)
            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)
            btn._frame = btn_frame
            return btn
        else:
            btn = tk.Button(
                parent, text=text, command=command,
                bg=color, fg='#ffffff', font=self.get_font(11, 'bold'),
                relief='flat', cursor='hand2', height=2,
                activebackground=self.lighten_color(color),
                activeforeground='#ffffff',
                borderwidth=0, highlightthickness=0
            )
            btn.bind('<Enter>', lambda e: btn.config(
                bg=self.lighten_color(color)))
            btn.bind('<Leave>', lambda e: btn.config(bg=color))
            return btn

    def lighten_color(self, color):
        colors = {
            '#00ff9f': '#33ffb3', '#00aaff': '#33bbff',
            '#ff4466': '#ff6688', '#9966ff': '#aa77ff',
            '#ff9500': '#ffaa33'
        }
        return colors.get(color, color)

    # ---------- Feature extraction / comparison (same as your code) ----------

    def extract_deep_features(self, face_image):
        try:
            if face_image is None or face_image.size == 0:
                return None

            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image

            if gray.shape[0] < 20 or gray.shape[1] < 20:
                return None

            gray = cv2.resize(gray, (128, 128))
            gray = cv2.equalizeHist(gray)

            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = cv2.normalize(hist, hist).flatten()[:64]

            lbp = self.compute_lbp(gray)
            if lbp is not None and lbp.size > 0:
                lbp_hist = cv2.calcHist([lbp], [0], None, [256], [0, 256])
                lbp_hist = cv2.normalize(lbp_hist, lbp_hist).flatten()[:64]
            else:
                lbp_hist = np.zeros(64)

            hog = self.compute_hog(gray)
            if len(hog) > 128:
                hog = hog[:128]
            elif len(hog) < 128:
                hog = np.pad(hog, (0, 128 - len(hog)), 'constant')

            orb_feat = self.compute_orb_features(gray)
            if len(orb_feat) < 32:
                orb_feat = np.pad(
                    orb_feat, (0, 32 - len(orb_feat)), 'constant')

            combined = np.concatenate([hist, lbp_hist, hog, orb_feat])

            if np.any(np.isnan(combined)) or np.any(np.isinf(combined)):
                return None

            norm = np.linalg.norm(combined)
            if norm > 0:
                combined = combined / norm
            else:
                return None

            return combined.astype(np.float32)
        except Exception:
            return None

    def compute_lbp(self, image):
        height, width = image.shape
        lbp = np.zeros((height-2, width-2), dtype=np.uint8)
        for i in range(1, height-1):
            for j in range(1, width-1):
                center = image[i, j]
                code = 0
                code |= (image[i-1, j-1] >= center) << 7
                code |= (image[i-1, j] >= center) << 6
                code |= (image[i-1, j+1] >= center) << 5
                code |= (image[i, j+1] >= center) << 4
                code |= (image[i+1, j+1] >= center) << 3
                code |= (image[i+1, j] >= center) << 2
                code |= (image[i+1, j-1] >= center) << 1
                code |= (image[i, j-1] >= center) << 0
                lbp[i-1, j-1] = code
        return lbp

    def compute_hog(self, image):
        gx = cv2.Sobel(image, cv2.CV_32F, 1, 0)
        gy = cv2.Sobel(image, cv2.CV_32F, 0, 1)
        mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)
        bins = np.int32(angle / 40) % 9
        hist = []
        cell_size = 16
        for i in range(0, image.shape[0] - cell_size, cell_size):
            for j in range(0, image.shape[1] - cell_size, cell_size):
                cell_mag = mag[i:i+cell_size, j:j+cell_size]
                cell_bins = bins[i:i+cell_size, j:j+cell_size]
                cell_hist = np.zeros(9)
                for k in range(9):
                    cell_hist[k] = np.sum(cell_mag[cell_bins == k])
                hist.extend(cell_hist)
        hog_features = np.array(hist)
        if np.linalg.norm(hog_features) > 0:
            hog_features = hog_features / np.linalg.norm(hog_features)
        return hog_features

    def compute_orb_features(self, image):
        try:
            orb = cv2.ORB_create(nfeatures=50)
            keypoints, descriptors = orb.detectAndCompute(image, None)
            if descriptors is not None and len(descriptors) > 0:
                avg_desc = np.mean(descriptors, axis=0)
                if len(avg_desc) > 32:
                    return avg_desc[:32]
                else:
                    padded = np.zeros(32)
                    padded[:len(avg_desc)] = avg_desc
                    return padded
            else:
                return np.zeros(32)
        except:
            return np.zeros(32)

    def calculate_face_quality(self, face_image):
        try:
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(
                face_image.shape) == 3 else face_image
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            brightness = np.mean(gray)
            brightness_score = 100 - abs(brightness - 128)
            contrast = gray.std()
            quality = min(
                100, (sharpness * 3 + brightness_score + contrast) / 5)
            return max(0, quality)
        except:
            return 50.0

    def compare_features(self, feat1, feat2):
        try:
            feat1 = np.array(feat1, dtype=np.float32)
            feat2 = np.array(feat2, dtype=np.float32)
            if np.any(np.isnan(feat1)) or np.any(np.isnan(feat2)):
                return 0.0
            if np.any(np.isinf(feat1)) or np.any(np.isinf(feat2)):
                return 0.0
            norm1 = np.linalg.norm(feat1)
            norm2 = np.linalg.norm(feat2)
            if norm1 == 0 or norm2 == 0:
                return 0.0
            feat1_norm = feat1 / norm1
            feat2_norm = feat2 / norm2
            cos_sim = np.clip(np.dot(feat1_norm, feat2_norm), -1.0, 1.0)
            euclidean_dist = np.linalg.norm(feat1_norm - feat2_norm)
            euclidean_sim = 1 / (1 + euclidean_dist)
            similarity = 0.7 * cos_sim + 0.3 * euclidean_sim
            return np.clip(similarity, 0.0, 1.0)
        except Exception:
            return 0.0

    # ---------- Registration / Recognition ----------

    def start_registration(self):
        if self.is_capturing:
            messagebox.showwarning("Анхааруулга", "Өөр үйлдэл явагдаж байна!")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("✨ Нүүр бүртгэх")
        dialog.geometry("450x280")
        dialog.configure(bg=self.bg_panel)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="👤 Хүний нэр оруулна уу:",
                 font=self.get_font(13, 'bold'),
                 bg=self.bg_panel, fg=self.fg_secondary).pack(pady=25)

        name_entry = tk.Entry(dialog, font=self.get_font(12), width=30,
                              bg='#2a2f4a', fg=self.fg_secondary,
                              insertbackground=self.fg_primary, relief='flat', borderwidth=5)
        name_entry.pack(pady=10)
        name_entry.focus()

        tk.Label(dialog, text="📸 Зургийн тоо:",
                 font=self.get_font(10),
                 bg=self.bg_panel, fg=self.fg_secondary).pack(pady=(10, 5))

        sample_var = tk.IntVar(value=10)
        tk.Spinbox(dialog, from_=6, to=20, textvariable=sample_var,
                   font=self.get_font(11), width=10,
                   bg='#2a2f4a', fg=self.fg_secondary).pack()

        def submit():
            name = name_entry.get().strip()
            if name:
                dialog.destroy()
                self.register_name = name
                self.register_samples = sample_var.get()
                threading.Thread(target=self.register_thread,
                                 daemon=True).start()
            else:
                messagebox.showerror("Алдаа", "Нэр оруулна уу!")

        submit_btn = tk.Button(dialog, text="✓ Эхлүүлэх", command=submit,
                               bg=self.fg_primary, fg=self.bg_dark,
                               font=self.get_font(11, 'bold'),
                               cursor='hand2', height=2, relief='flat',
                               activebackground=self.lighten_color(
                                   self.fg_primary),
                               activeforeground=self.bg_dark)
        submit_btn.pack(pady=15)
        name_entry.bind('<Return>', lambda e: submit())

    def is_face_centered(self, face_rect, frame_shape, center_threshold=0.15):
        x, y, w, h = face_rect
        frame_center_x = frame_shape[1] // 2
        frame_center_y = frame_shape[0] // 2
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        dx = abs(face_center_x - frame_center_x) / frame_shape[1]
        dy = abs(face_center_y - frame_center_y) / frame_shape[0]
        return dx < center_threshold and dy < center_threshold

    def draw_center_guide(self, frame):
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        line_length = 30
        thickness = 2
        color = (100, 100, 255)
        cv2.line(frame, (center_x - line_length, center_y),
                 (center_x + line_length, center_y), color, thickness)
        cv2.line(frame, (center_x, center_y - line_length),
                 (center_x, center_y + line_length), color, thickness)
        cv2.circle(frame, (center_x, center_y), 50, color, 2)

    def clean_features(self, features_list):
        cleaned_features = []
        for features in features_list:
            try:
                features_array = np.array(features, dtype=np.float32)
                if np.any(np.isnan(features_array)) or np.any(np.isinf(features_array)):
                    continue
                norm = np.linalg.norm(features_array)
                if norm > 0:
                    features_array = features_array / norm
                else:
                    continue
                cleaned_features.append(features_array)
            except:
                continue
        return cleaned_features

    def register_thread(self):
        self.is_capturing = True
        self.current_mode = 'register'
        self.register_btn.config(state='disabled')
        self.recognize_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        self.update_status(f"\n🚀 {self.register_name} бүртгэж байна...")
        self.update_status("📍 Нүүрээ камерын төвд байрлуулна уу")
        self.info_label.config(text=f"📸 Бүртгэл: {self.register_name}")

        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.video_capture.set(cv2.CAP_PROP_FPS, 30)

        features_list = []
        quality_list = []
        count = 0
        face_positions = []
        last_capture = time.time()
        stable_frames = 0
        centered_frames = 0

        process_interval = 1.0 / 10
        last_process_time = time.time()
        last_faces = []

        while count < self.register_samples and self.is_capturing:
            ret, frame = self.video_capture.read()
            if not ret:
                break

            self.draw_center_guide(frame)
            current_time = time.time()

            if current_time - last_process_time >= process_interval:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5,
                    minSize=(120, 120), maxSize=(400, 400)
                )
                last_faces = faces
                last_process_time = current_time
            else:
                faces = last_faces

            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                x, y, w, h = faces[0]
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                roi_gray = gray[y:y+h, x:x+w]
                eyes = self.eye_cascade.detectMultiScale(
                    roi_gray, minNeighbors=8)
                has_eyes = len(eyes) >= 2
                face_center = (x + w//2, y + h//2)
                is_centered = self.is_face_centered((x, y, w, h), frame.shape)
                is_new_angle = self.is_new_angle(
                    face_center, face_positions) if self.multi_angle_var.get() else True
                face_roi = frame[y:y+h, x:x+w]
                quality = self.calculate_face_quality(face_roi)
                quality_ok = quality > 35 if self.quality_filter_var.get() else True
                ready = has_eyes and is_centered and is_new_angle and quality_ok

                if ready:
                    color = (0, 255, 0)
                    stable_frames += 1
                    centered_frames += 1
                else:
                    if not is_centered:
                        color = (0, 165, 255)
                        centered_frames = 0
                    elif not quality_ok:
                        color = (255, 0, 255)
                        centered_frames = 0
                    elif not has_eyes:
                        color = (0, 255, 255)
                        centered_frames = 0
                    else:
                        color = (0, 165, 255)
                        centered_frames = 0
                    stable_frames = 0

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                if is_centered:
                    cv2.circle(frame, face_center, 5, (0, 255, 0), -1)

                status_text = []
                if self.quality_filter_var.get():
                    status_text.append(f"Q: {quality:.0f}%")
                if not is_centered:
                    status_text.append("Центрт байрлуулна уу")
                elif not has_eyes:
                    status_text.append("Нүд харагдахгүй")
                elif ready:
                    status_text.append("✓ Бэлэн")

                if status_text:
                    text = " | ".join(status_text)
                    cv2.putText(frame, text, (x, y-10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                if ready and stable_frames >= 3 and centered_frames >= 2 and current_time - last_capture >= 0.4:
                    if self.deep_features_var.get():
                        features = self.extract_deep_features(face_roi)
                    else:
                        features = self.extract_simple_features(face_roi)
                    if features is not None and len(features) > 0:
                        try:
                            features_array = np.array(
                                features, dtype=np.float32)
                            if not np.any(np.isnan(features_array)) and not np.any(np.isinf(features_array)):
                                norm = np.linalg.norm(features_array)
                                if norm > 0:
                                    features_array = features_array / norm
                                    features_list.append(features_array)
                                    quality_list.append(quality)
                                    face_positions.append(face_center)
                                    count += 1
                                    last_capture = current_time
                                    stable_frames = 0
                                    centered_frames = 0
                                    overlay = frame.copy()
                                    cv2.circle(
                                        overlay, (frame.shape[1]//2, frame.shape[0]//2), 100, (0, 255, 0), -1)
                                    frame = cv2.addWeighted(
                                        frame, 0.6, overlay, 0.4, 0)
                                    self.update_status(
                                        f"📸 {count}/{self.register_samples} - Q: {quality:.0f}%")
                        except:
                            pass

            self.draw_progress(frame, count, self.register_samples)
            self.display_frame(frame)
            time.sleep(0.01)

        self.video_capture.release()

        if count >= 3:
            cleaned_data = []
            for i, features in enumerate(features_list):
                try:
                    features_array = np.array(features, dtype=np.float32)
                    if not np.any(np.isnan(features_array)) and not np.any(np.isinf(features_array)):
                        norm = np.linalg.norm(features_array)
                        if norm > 0:
                            features_array = features_array / norm
                            cleaned_data.append({
                                'features': features_array,
                                'quality': quality_list[i],
                                'position': face_positions[i]
                            })
                except:
                    continue

            if len(cleaned_data) >= 3:
                unique_features = []
                unique_qualities = []
                for data in cleaned_data:
                    feat = data['features']
                    is_duplicate = False
                    for existing_feat in unique_features:
                        similarity = self.compare_features(
                            feat, existing_feat)
                        if similarity > 0.95:
                            is_duplicate = True
                            break
                    if not is_duplicate:
                        unique_features.append(feat)
                        unique_qualities.append(data['quality'])

                # Хүн бүрт тусдаа ID үүсгэх (name + timestamp)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                person_id = f"{self.register_name}_{timestamp}"
                
                # Person folder үүсгэх
                person_folder = os.path.join(self.face_data_dir, person_id)
                if not os.path.exists(person_folder):
                    os.makedirs(person_folder)
                
                # Person data хадгалах
                person_features = []
                person_qualities = []
                for i, features in enumerate(unique_features):
                    person_features.append(features)
                    person_qualities.append(unique_qualities[i])
                    
                    # Backward compatibility
                    self.known_face_features.append(features)
                    self.known_face_names.append(self.register_name)
                    self.face_quality_scores.append(unique_qualities[i])
                    self.person_ids.append(person_id)
                
                # Person-specific data хадгалах
                person_data = {
                    'person_id': person_id,
                    'name': self.register_name,
                    'features': person_features,
                    'quality_scores': person_qualities,
                    'registered_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'sample_count': len(person_features)
                }
                
                person_file = os.path.join(person_folder, "person_data.pkl")
                with open(person_file, 'wb') as f:
                    pickle.dump(person_data, f)
                
                # Person data dictionary-д хадгалах
                self.person_data[person_id] = person_data

                avg_quality = np.mean(unique_qualities)
                self.update_status(
                    f"✅ {self.register_name} амжилттай бүртгэгдлээ! (ID: {person_id})")
                self.update_status(f"📊 Дундаж чанар: {avg_quality:.1f}%")
                self.update_status(
                    f"🧹 Цэвэрлэсэн: {len(unique_features)}/{len(cleaned_data)} зураг")
                self.update_status(f"📁 Хадгалагдсан: {person_folder}")
                self.save_data()
                self.update_status_display()
            else:
                self.update_status(f"❌ Хангалттай цэвэр дата байхгүй!")
        else:
            self.update_status(f"❌ Хангалттай зураг аваагүй!")

        self.stop_capture()

    def extract_simple_features(self, face_image):
        try:
            if face_image is None or face_image.size == 0:
                return None
            gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY) if len(
                face_image.shape) == 3 else face_image
            if gray.shape[0] < 20 or gray.shape[1] < 20:
                return None
            gray = cv2.resize(gray, (100, 100))
            gray = cv2.equalizeHist(gray)
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            features = cv2.normalize(hist, hist).flatten()
            if np.any(np.isnan(features)) or np.any(np.isinf(features)):
                return None
            return features.astype(np.float32)
        except:
            return None

    def is_new_angle(self, center, positions, min_diff=30):
        for pos in positions:
            dist = np.sqrt((center[0] - pos[0])**2 +
                           (center[1] - pos[1])**2)
            if dist < min_diff:
                return False
        return True

    def start_recognition(self):
        if not self.known_face_names:
            messagebox.showwarning("Анхааруулга", "Эхлээд дата ачаална уу!")
            return
        if self.is_capturing:
            messagebox.showwarning("Анхааруулга", "Өөр үйлдэл явагдаж байна!")
            return
        self.current_mode = 'recognize'
        self.is_capturing = True
        self.register_btn.config(state='disabled')
        self.recognize_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.update_status("\n🎥 AI танилт эхэллээ...")
        self.info_label.config(text="🔍 Танилт явагдаж байна...")
        threading.Thread(target=self.recognize_thread, daemon=True).start()

    def recognize_thread(self):
        self.video_capture = cv2.VideoCapture(0)
        self.video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.video_capture.set(cv2.CAP_PROP_FPS, 30)

        frame_count = 0
        last_results = {}
        fps_start = time.time()
        fps_counter = 0
        last_process_time = time.time()
        process_interval = 1.0 / 10

        stable_name = None
        stable_frames = 0
        required_stable_frames = 15  # ийм олон фрэйм дараалан танигдвал "батлагдлаа"

        while self.is_capturing:
            ret, frame = self.video_capture.read()
            if not ret:
                break

            current_time = time.time()
            frame_count += 1
            fps_counter += 1
            if current_time - fps_start >= 1.0:
                self.fps = fps_counter
                fps_counter = 0
                fps_start = current_time

            if current_time - last_process_time >= process_interval:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.2, minNeighbors=5,
                    minSize=(60, 60), maxSize=(400, 400)
                )
                new_results = {}
                best_frame_name = None
                best_frame_conf = 0.0

                for face_id, (x, y, w, h) in enumerate(faces):
                    face_roi = frame[y:y+h, x:x+w]
                    if face_roi.size == 0 or face_roi.shape[0] < 20 or face_roi.shape[1] < 20:
                        continue
                    try:
                        if self.deep_features_var.get():
                            features = self.extract_deep_features(face_roi)
                        else:
                            features = self.extract_simple_features(face_roi)
                        if features is not None and len(features) > 0:
                            features_array = np.array(
                                features, dtype=np.float32)
                            if not np.any(np.isnan(features_array)) and not np.any(np.isinf(features_array)):
                                name, confidence = self.find_best_match(
                                    features)
                                new_results[face_id] = (
                                    x, y, w, h, name, confidence)
                                if name != "Танигдаагүй" and confidence > best_frame_conf:
                                    best_frame_name = name
                                    best_frame_conf = confidence
                    except Exception:
                        continue

                # stablize recognition
                if best_frame_name and best_frame_conf >= self.threshold * 100:
                    if stable_name == best_frame_name:
                        stable_frames += 1
                    else:
                        stable_name = best_frame_name
                        stable_frames = 1
                else:
                    stable_name = None
                    stable_frames = 0

                # if stable enough and not yet unlocked
                if (stable_name is not None and
                        stable_frames >= required_stable_frames and
                        not self.face_recognized):
                    self.face_recognized = True
                    self.recognized_name = stable_name
                    self.root.after(0, self.on_face_recognized)

                last_results = new_results
                last_process_time = current_time

            for face_id, (x, y, w, h, name, confidence) in last_results.items():
                color = self.get_color(name, confidence)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
                corner_len = 20
                for (cx, cy) in [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]:
                    dx = corner_len if cx == x else -corner_len
                    dy = corner_len if cy == y else -corner_len
                    cv2.line(frame, (cx, cy), (cx+dx, cy), color, 5)
                    cv2.line(frame, (cx, cy), (cx, cy+dy), color, 5)

                if self.show_confidence_var.get() and name != "Танигдаагүй":
                    bar_width = int(w * (confidence / 100))
                    cv2.rectangle(frame, (x, y-10),
                                  (x+bar_width, y-5), color, -1)

                label_text = f"{name} ({confidence:.0f}%)" if name != "Танигдаагүй" else name
                label_y = y - 15 if y - 15 > 15 else y + h + 35
                (text_width, text_height), _ = cv2.getTextSize(
                    label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                cv2.rectangle(frame, (x, label_y - text_height - 10),
                              (x + text_width + 10, label_y), color, -1)
                cv2.putText(frame, label_text, (x + 5, label_y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # HUD + unlock progress
            self.draw_hud(frame, len(last_results))
            if not self.face_recognized:
                progress = min(
                    100, (stable_frames / required_stable_frames) * 100)
                cv2.putText(frame, f"Face Lock: {int(progress)}%",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (255, 255, 0), 2)
            else:
                cv2.putText(frame, f"UNLOCKED: {self.recognized_name}",
                            (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                            (0, 255, 0), 2)

            self.display_frame(frame)
            time.sleep(0.03)

        self.video_capture.release()
        self.stop_capture()

    def on_face_recognized(self):
        """Нүүр амжилттай танигдмагц дуудагдана"""
        self.update_status(
            f"\n✅ Нүүр амжилттай танигдлаа: {self.recognized_name}")
        self.info_label.config(
            text=f"✅ Танигдсан: {self.recognized_name} - Тоглоом эхлүүлэх боломжтой!")
        self.game_btn.config(state='normal')

        # Шууд асууж, шууд тоглоом эхлүүлэх
        if messagebox.askyesno(
            "Face Lock",
            f"{self.recognized_name} танигдлаа.\n\nТоглоомыг эхлүүлэх үү?"
        ):
            self.stop_capture()
            self.launch_game()

    def find_best_match(self, features):
        """Хүн бүрийг тусдаа таних - person_id ашиглах"""
        if not self.known_face_features and not self.person_data:
            return "Танигдаагүй", 0
        if features is None:
            return "Танигдаагүй", 0
        try:
            features = np.array(features, dtype=np.float32)
            if np.any(np.isnan(features)) or np.any(np.isinf(features)):
                return "Танигдаагүй", 0
            
            max_similarity = 0
            best_name = "Танигдаагүй"
            best_person_id = None
            
            # Person data-аас таних (шинэ систем)
            for person_id, person_info in self.person_data.items():
                person_features = person_info.get('features', [])
                person_name = person_info.get('name', 'Unknown')
                
                for known_features in person_features:
                    if known_features is None:
                        continue
                    similarity = self.compare_features(features, known_features)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        best_name = person_name
                        best_person_id = person_id
            
            # Backward compatibility - хуучин систем
            for idx, known_features in enumerate(self.known_face_features):
                if known_features is None:
                    continue
                similarity = self.compare_features(features, known_features)
                if similarity > max_similarity:
                    max_similarity = similarity
                    if idx < len(self.person_ids):
                        best_person_id = self.person_ids[idx]
                    best_name = self.known_face_names[idx] if idx < len(self.known_face_names) else "Танигдаагүй"
            
            if max_similarity >= self.threshold:
                confidence = max_similarity * 100
                # Person ID-г нэртэй хамт буцаах (хэрэв байвал)
                if best_person_id:
                    return f"{best_name} ({best_person_id.split('_')[-1]})", confidence
                return best_name, confidence
            else:
                return "Танигдаагүй", max_similarity * 100
        except Exception:
            return "Танигдаагүй", 0

    def get_color(self, name, confidence):
        if name != "Танигдаагүй":
            if confidence > 80:
                return (0, 255, 159)
            elif confidence > 70:
                return (0, 191, 255)
            else:
                return (0, 165, 255)
        return (0, 0, 255)

    def draw_hud(self, frame, face_count):
        h, w = frame.shape[:2]
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 50), (26, 31, 58), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        info = f"FPS: {self.fps} | Faces: {face_count} | Enhanced OpenCV"
        cv2.putText(frame, info, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 159), 2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(frame, timestamp, (w - 100, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    def draw_progress(self, frame, current, total):
        h, w = frame.shape[:2]
        bar_width = w - 80
        bar_height = 35
        bar_x, bar_y = 40, h - 60
        cv2.rectangle(frame, (bar_x-5, bar_y-5),
                      (bar_x + bar_width + 5, bar_y + bar_height + 5),
                      (26, 31, 58), -1)
        progress = int((current / total) * bar_width)
        cv2.rectangle(frame, (bar_x, bar_y),
                      (bar_x + progress, bar_y + bar_height),
                      (0, 255, 159), -1)
        cv2.rectangle(frame, (bar_x, bar_y),
                      (bar_x + bar_width, bar_y + bar_height),
                      (255, 255, 255), 2)
        text = f"{current}/{total} ({int(current/total*100)}%)"
        cv2.putText(frame, text, (bar_x + bar_width//2 - 60, bar_y + 23),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    def stop_capture(self):
        self.is_capturing = False
        if self.video_capture:
            self.video_capture.release()
        self.register_btn.config(state='normal')
        self.recognize_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.info_label.config(text="⚡ Бэлэн")
        self.video_label.config(
            image='',
            text="🎥 Видео зогссон байна\n\n✨ Танилтыг дахин эхлүүлэх бол товчийг дарна уу"
        )

    def display_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img.thumbnail((900, 650), Image.Resampling.LANCZOS)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk, text='')

    def update_status(self, message, clear=False):
        self.status_text.config(state='normal')
        if clear:
            self.status_text.delete(1.0, tk.END)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        # Автоматаар доошлуулах (scroll to bottom)
        self.status_text.see(tk.END)
        self.status_text.update_idletasks()  # UI шинэчлэх
        self.status_text.config(state='disabled')

    def update_status_display(self):
        self.update_status("", clear=True)
        self.update_status("🟢 Enhanced OpenCV Mode (Face Lock)")
        if self.known_face_names or self.person_data:
            # Person data-аас мэдээлэл харуулах
            if self.person_data:
                unique_persons = len(self.person_data)
                total_samples = sum(len(p.get('features', [])) for p in self.person_data.values())
                self.update_status(f"\n👥 Бүртгэлтэй: {unique_persons} хүн (тусдаа ID)")
                self.update_status(f"📊 Нийт зураг: {total_samples}")
                if self.face_quality_scores:
                    avg_quality = np.mean(self.face_quality_scores)
                    self.update_status(f"✨ Дундаж чанар: {avg_quality:.1f}%")
                self.update_status(f"🎯 Threshold: {self.threshold:.2f}\n")
                self.update_status("📋 Хүмүүс (Person ID-тай):")
                for person_id, person_info in sorted(self.person_data.items()):
                    name = person_info.get('name', 'Unknown')
                    count = len(person_info.get('features', []))
                    reg_time = person_info.get('registered_at', 'Unknown')
                    self.update_status(f"  • {name} [{person_id.split('_')[-1]}]: {count} зураг ({reg_time})")
            else:
                # Backward compatibility
                name_counts = Counter(self.known_face_names)
                self.update_status(f"\n👥 Бүртгэлтэй: {len(name_counts)} хүн")
                self.update_status(f"📊 Нийт зураг: {len(self.known_face_names)}")
                if self.face_quality_scores:
                    avg_quality = np.mean(self.face_quality_scores)
                    self.update_status(f"✨ Дундаж чанар: {avg_quality:.1f}%")
                self.update_status(f"🎯 Threshold: {self.threshold:.2f}\n")
                self.update_status("📋 Хүмүүс:")
                for name, count in sorted(name_counts.items()):
                    self.update_status(f"  • {name}: {count} зураг")
        else:
            self.update_status("\n⚠️ Бүртгэлтэй хүн байхгүй")

    def update_threshold(self, value):
        self.threshold = float(value)
        self.threshold_label.config(text=f"Утга: {self.threshold:.2f}")

    def save_data(self):
        if not self.known_face_names:
            messagebox.showwarning("Анхааруулга", "Хадгалах дата байхгүй!")
            return
        if os.path.exists(self.data_file):
            name_counts = Counter(self.known_face_names)
            total_people = len(name_counts)
            total_samples = len(self.known_face_names)
            people_list = "\n".join(
                [f"  • {name}: {count} зураг" for name, count in sorted(name_counts.items())])
            message = f"📋 БҮРТГЭЛТЭЙ ХҮМҮҮС\n" + "="*40 + "\n\n"
            message += f"👥 Нийт хүн: {total_people}\n"
            message += f"📸 Нийт зураг: {total_samples}\n\n"
            message += "📋 Хүмүүс:\n" + people_list + "\n\n"
            message += "Хадгалах уу?"
            result = messagebox.askyesno("Бүртгэлтэй хүмүүс", message)
            if not result:
                return
        try:
            cleaned_features = []
            cleaned_names = []
            cleaned_qualities = []
            for i, features in enumerate(self.known_face_features):
                try:
                    features_array = np.array(features, dtype=np.float32)
                    if np.any(np.isnan(features_array)) or np.any(np.isinf(features_array)):
                        continue
                    norm = np.linalg.norm(features_array)
                    if norm > 0:
                        features_array = features_array / norm
                        cleaned_features.append(features_array)
                        cleaned_names.append(self.known_face_names[i])
                        cleaned_qualities.append(self.face_quality_scores[i] if i < len(
                            self.face_quality_scores) else 50.0)
                except:
                    continue
            self.known_face_features = cleaned_features
            self.known_face_names = cleaned_names
            self.face_quality_scores = cleaned_qualities
            data = {
                'features': self.known_face_features,
                'names': self.known_face_names,
                'quality_scores': self.face_quality_scores,
                'person_ids': getattr(self, 'person_ids', []),
                'person_data': getattr(self, 'person_data', {}),
                'threshold': self.threshold,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': '2.2-folder-structure'
            }
            with open(self.data_file, 'wb') as f:
                pickle.dump(data, f)
            self.update_status("💾 Дата хадгалагдлаа!")
            self.update_status(f"🧹 Цэвэрлэсэн: {len(cleaned_features)} зураг")
            messagebox.showinfo(
                "Амжилт", f"Ачаалагдлаа!\n{len(set(self.known_face_names))} хүн\n{len(cleaned_features)} цэвэр зураг")
        except Exception as e:
            messagebox.showerror("Алдаа", f"Хадгалах алдаа: {e}")

    def load_person_data_from_folders(self):
        """Face data folder-оос бүх хүмүүсийн дата ачаалах"""
        if not os.path.exists(self.face_data_dir):
            return
        
        loaded_count = 0
        for person_folder in os.listdir(self.face_data_dir):
            person_path = os.path.join(self.face_data_dir, person_folder)
            if not os.path.isdir(person_path):
                continue
            
            person_file = os.path.join(person_path, "person_data.pkl")
            if os.path.exists(person_file):
                try:
                    with open(person_file, 'rb') as f:
                        person_data = pickle.load(f)
                        person_id = person_data.get('person_id', person_folder)
                        self.person_data[person_id] = person_data
                        
                        # Backward compatibility
                        person_features = person_data.get('features', [])
                        person_name = person_data.get('name', 'Unknown')
                        person_qualities = person_data.get('quality_scores', [])
                        
                        for i, features in enumerate(person_features):
                            self.known_face_features.append(features)
                            self.known_face_names.append(person_name)
                            self.face_quality_scores.append(
                                person_qualities[i] if i < len(person_qualities) else 50.0)
                            self.person_ids.append(person_id)
                        
                        loaded_count += 1
                except Exception as e:
                    print(f"Error loading person data from {person_file}: {e}")
                    continue
        
        if loaded_count > 0:
            print(f"Loaded {loaded_count} person(s) from folders")

    def load_data_silent(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'rb') as f:
                    data = pickle.load(f)
                    raw_features = data.get('features', [])
                    raw_names = data.get('names', [])
                    raw_qualities = data.get('quality_scores', [])
                    self.threshold = data.get('threshold', self.threshold)
                    try:
                        self.threshold_var.set(self.threshold)
                    except:
                        pass
                cleaned_features = []
                cleaned_names = []
                cleaned_qualities = []
                for i, features in enumerate(raw_features):
                    try:
                        features_array = np.array(features, dtype=np.float32)
                        if not np.any(np.isnan(features_array)) and not np.any(np.isinf(features_array)):
                            norm = np.linalg.norm(features_array)
                            if norm > 0:
                                features_array = features_array / norm
                                cleaned_features.append(features_array)
                                cleaned_names.append(
                                    raw_names[i] if i < len(raw_names) else "Unknown")
                                cleaned_qualities.append(
                                    raw_qualities[i] if i < len(raw_qualities) else 50.0)
                    except:
                        continue
                self.known_face_features = cleaned_features
                self.known_face_names = cleaned_names
                self.face_quality_scores = cleaned_qualities
                
                # Person IDs болон person_data ачаалах
                if 'person_ids' in data:
                    self.person_ids = data.get('person_ids', [])
                if 'person_data' in data:
                    self.person_data = data.get('person_data', {})
            except:
                pass

    def load_data(self):
        if not os.path.exists(self.data_file):
            messagebox.showwarning("Анхааруулга", "Дата файл олдсонгүй!")
            return
        try:
            with open(self.data_file, 'rb') as f:
                data = pickle.load(f)
                raw_features = data.get('features', [])
                raw_names = data.get('names', [])
                raw_qualities = data.get('quality_scores', [])
                self.threshold = data.get('threshold', self.threshold)
                self.threshold_var.set(self.threshold)
            cleaned_features = []
            cleaned_names = []
            cleaned_qualities = []
            for i, features in enumerate(raw_features):
                try:
                    features_array = np.array(features, dtype=np.float32)
                    if np.any(np.isnan(features_array)) or np.any(np.isinf(features_array)):
                        continue
                    norm = np.linalg.norm(features_array)
                    if norm > 0:
                        features_array = features_array / norm
                        cleaned_features.append(features_array)
                        cleaned_names.append(
                            raw_names[i] if i < len(raw_names) else "Unknown")
                        cleaned_qualities.append(
                            raw_qualities[i] if i < len(raw_qualities) else 50.0)
                except:
                    continue
                self.known_face_features = cleaned_features
                self.known_face_names = cleaned_names
                self.face_quality_scores = cleaned_qualities
                
                # Person IDs болон person_data ачаалах
                if 'person_ids' in data:
                    self.person_ids = data.get('person_ids', [])
                if 'person_data' in data:
                    self.person_data = data.get('person_data', {})
                
                self.update_status_display()
                cleaned_count = len(cleaned_features)
                original_count = len(raw_features)
                if cleaned_count < original_count:
                    messagebox.showinfo("Амжилт",
                                        f"Ачаалагдлаа!\n{len(set(cleaned_names))} хүн\n"
                                        f"🧹 Цэвэрлэсэн: {cleaned_count}/{original_count} зураг")
                else:
                    messagebox.showinfo(
                        "Амжилт", f"Ачаалагдлаа!\n{len(set(cleaned_names))} хүн")
        except Exception as e:
            messagebox.showerror("Алдаа", f"Ачаалах алдаа: {e}")

    def export_json(self):
        if not self.known_face_names:
            messagebox.showwarning("Анхааруулга", "Экспорт хийх дата байхгүй!")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                name_counts = Counter(self.known_face_names)
                export_data = {
                    'people': [
                        {
                            'name': name,
                            'sample_count': count,
                            'avg_quality': float(np.mean([
                                self.face_quality_scores[i]
                                for i, n in enumerate(self.known_face_names) if n == name
                            ]))
                        }
                        for name, count in name_counts.items()
                    ],
                    'total_samples': len(self.known_face_names),
                    'threshold': self.threshold,
                    'export_date': datetime.now().isoformat()
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                self.update_status(f"📤 Export: {filename}")
                messagebox.showinfo("Амжилт", "JSON амжилттай!")
            except Exception as e:
                messagebox.showerror("Алдаа", f"Export алдаа: {e}")

    def import_from_folder(self):
        folder = filedialog.askdirectory(title="Зургийн фолдер сонгох")
        if folder:
            files = [f for f in os.listdir(folder)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            if not files:
                messagebox.showwarning("Анхааруулга", "Зураг олдсонгүй!")
                return
            success = 0
            for filename in files:
                path = os.path.join(folder, filename)
                image = cv2.imread(path)
                if image is None:
                    continue
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                if len(faces) > 0:
                    face = max(faces, key=lambda r: r[2] * r[3])
                    x, y, w, h = face
                    face_roi = image[y:y+h, x:x+w]
                    features = self.extract_deep_features(face_roi) if self.deep_features_var.get(
                    ) else self.extract_simple_features(face_roi)
                    if features is not None:
                        name = os.path.splitext(
                            filename)[0].replace('_', ' ').title()
                        quality = self.calculate_face_quality(face_roi)
                        self.known_face_features.append(features)
                        self.known_face_names.append(name)
                        self.face_quality_scores.append(quality)
                        success += 1
            if success > 0:
                self.save_data()
                self.update_status_display()
                messagebox.showinfo(
                    "Амжилт", f"{success}/{len(files)} зураг импортлогдлоо!")
            else:
                messagebox.showwarning(
                    "Анхааруулга", "Амжилттай импортлосон зураг байхгүй!")

    def show_people_list(self):
        if not self.known_face_names:
            messagebox.showinfo("Мэдээлэл", "Бүртгэлтэй хүн байхгүй")
            return
        name_counts = Counter(self.known_face_names)
        message = "📋 БҮРТГЭЛТЭЙ ХҮМҮҮС\n" + "="*40 + "\n\n"
        for name, count in sorted(name_counts.items()):
            qualities = [self.face_quality_scores[i]
                         for i, n in enumerate(self.known_face_names) if n == name]
            avg_q = np.mean(qualities) if qualities else 0
            message += f"👤 {name}\n"
            message += f"   📊 Зураг: {count}\n"
            message += f"   ✨ Чанар: {avg_q:.1f}%\n\n"
        messagebox.showinfo("Бүртгэлтэй хүмүүс", message)

    def show_statistics(self):
        if not self.known_face_names:
            messagebox.showinfo("Мэдээлэл", "Статистик байхгүй")
            return
        name_counts = Counter(self.known_face_names)
        total_people = len(name_counts)
        total_samples = len(self.known_face_names)
        avg_quality = np.mean(
            self.face_quality_scores) if self.face_quality_scores else 0
        message = "📊 СТАТИСТИК\n" + "="*40 + "\n\n"
        message += f"👥 Нийт хүн: {total_people}\n"
        message += f"📸 Нийт зураг: {total_samples}\n"
        message += f"✨ Дундаж чанар: {avg_quality:.1f}%\n"
        message += f"🎯 Threshold: {self.threshold:.2f}\n\n"
        message += "📈 Хүн бүрийн зураг:\n"
        for name, count in name_counts.most_common():
            message += f"  • {name}: {count}\n"
        messagebox.showinfo("Статистик", message)

    def delete_person(self):
        if not self.known_face_names and not self.person_data:
            messagebox.showinfo("Мэдээлэл", "Бүртгэлтэй хүн байхгүй")
            return
        dialog = tk.Toplevel(self.root)
        dialog.title("🗑️ Хүн устгах")
        dialog.geometry("500x400")
        dialog.configure(bg=self.bg_panel)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="⚠️ Устгах хүнийг сонгоно уу:",
                 font=self.get_font(12, 'bold'),
                 bg=self.bg_panel, fg=self.fg_secondary).pack(pady=20)
        
        # Person data-аас жагсаалт үүсгэх
        person_list = []
        if self.person_data:
            for person_id, person_info in self.person_data.items():
                name = person_info.get('name', 'Unknown')
                count = len(person_info.get('features', []))
                reg_time = person_info.get('registered_at', 'Unknown')
                person_list.append((person_id, name, count, reg_time))
        else:
            # Backward compatibility
            name_counts = Counter(self.known_face_names)
            for name in sorted(name_counts.keys()):
                person_list.append((None, name, name_counts[name], None))
        
        listbox = tk.Listbox(dialog, font=self.get_font(11), height=12,
                             bg='#2a2f4a', fg=self.fg_secondary,
                             selectbackground=self.fg_primary,
                             selectforeground=self.bg_dark)
        listbox.pack(fill='both', expand=True, padx=20, pady=10)
        for person_id, name, count, reg_time in person_list:
            if person_id:
                display_text = f"{name} [{person_id.split('_')[-1]}] - {count} зураг ({reg_time})"
            else:
                display_text = f"{name} - {count} зураг"
            listbox.insert(tk.END, display_text)

        def delete_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Анхааруулга", "Хүн сонгоно уу!")
                return
            selected_person = person_list[selection[0]]
            person_id, name, count, reg_time = selected_person
            
            confirm = messagebox.askyesno(
                "Баталгаажуулалт",
                f"'{name}' устгах уу?\n\nБуцаах боломжгүй!"
            )
            if confirm:
                if person_id:
                    # Person folder устгах
                    person_folder = os.path.join(self.face_data_dir, person_id)
                    if os.path.exists(person_folder):
                        import shutil
                        try:
                            shutil.rmtree(person_folder)
                            self.update_status(f"🗑️ {name} (folder) устгагдлаа!")
                        except Exception as e:
                            self.update_status(f"⚠️ Folder устгахад алдаа: {e}")
                    
                    # Person data-аас устгах
                    if person_id in self.person_data:
                        del self.person_data[person_id]
                    
                    # Backward compatibility - arrays-аас устгах
                    indices = [i for i, pid in enumerate(self.person_ids) if pid == person_id]
                    for idx in sorted(indices, reverse=True):
                        if idx < len(self.known_face_features):
                            del self.known_face_features[idx]
                        if idx < len(self.known_face_names):
                            del self.known_face_names[idx]
                        if idx < len(self.face_quality_scores):
                            del self.face_quality_scores[idx]
                        if idx < len(self.person_ids):
                            del self.person_ids[idx]
                else:
                    # Backward compatibility - зөвхөн нэрээр устгах
                    indices = [i for i, n in enumerate(self.known_face_names) if n == name]
                    for idx in sorted(indices, reverse=True):
                        del self.known_face_features[idx]
                        del self.known_face_names[idx]
                        if idx < len(self.face_quality_scores):
                            del self.face_quality_scores[idx]
                        if idx < len(self.person_ids):
                            del self.person_ids[idx]
                
                self.update_status(f"🗑️ {name} устгагдлаа!")
                self.save_data()
                self.update_status_display()
                dialog.destroy()

        delete_btn = tk.Button(dialog, text="🗑️ Устгах", command=delete_selected,
                               bg='#ff4466', fg='#ffffff',
                               font=self.get_font(11, 'bold'),
                               cursor='hand2', height=2, relief='flat',
                               activebackground=self.lighten_color('#ff4466'),
                               activeforeground='#ffffff')
        delete_btn.pack(pady=10)

    # ---------- GAME LAUNCH INTEGRATION ----------

    def launch_game_from_button(self):
        """Game товчийг гараар дарахад"""
        if not self.face_recognized or not self.recognized_name:
            messagebox.showwarning(
                "Анхааруулга", "Эхлээд нүүр танилт хийгээд танигдах хэрэгтэй!")
            return
        self.launch_game()

    def launch_game(self):
        """game.py файлыг subprocess ашиглан эхлүүлэх"""
        self.update_status("🎮 Тоглоом эхлэж байна...")
        self.info_label.config(text="🎮 Тоглоом эхэллээ (pygame)...")
        
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            game_file = os.path.join(script_dir, "game.py")
            
            self.update_status(f"🔍 Шалгаж байна: {game_file}")
            
            if not os.path.exists(game_file):
                error_msg = f"game.py файл олдсонгүй!\n\nХайсан зам:\n{game_file}\n\nОдоогийн ажлын хавтас:\n{os.getcwd()}"
                self.update_status(f"❌ {error_msg}")
                messagebox.showerror("Алдаа", error_msg)
                return
            
            self.update_status(f"✅ game.py олдлоо: {game_file}")
            self.update_status(f"🚀 Тоглоом эхлүүлж байна...")
            
            # Танигдсан нэрийг command line argument болгон дамжуулах
            player_name = self.recognized_name if self.recognized_name else "Player"
            # Нэрийг URL encode хийх (special characters-д зориулж)
            import urllib.parse
            encoded_name = urllib.parse.quote(player_name)
            
            # Windows дээр CREATE_NEW_CONSOLE ашиглан тусдаа цонхонд эхлүүлэх
            if self.is_windows:
                # Windows дээр тусдаа цонхонд эхлүүлэх
                try:
                    # CREATE_NEW_CONSOLE нь тусдаа console цонх үүсгэнэ
                    CREATE_NEW_CONSOLE = 0x00000010
                    process = subprocess.Popen(
                        [sys.executable, game_file, f"--player-name={encoded_name}"],
                        cwd=script_dir,
                        creationflags=CREATE_NEW_CONSOLE,
                        shell=False
                    )
                    self.update_status(f"✅ Process эхэлсэн (PID: {process.pid}) - Player: {player_name}")
                except (AttributeError, ValueError) as e:
                    # CREATE_NEW_CONSOLE байхгүй эсвэл алдаа гарвал shell=True ашиглах
                    self.update_status(f"⚠️ CREATE_NEW_CONSOLE алдаа, shell=True ашиглаж байна: {e}")
                    process = subprocess.Popen(
                        [sys.executable, game_file, f"--player-name={encoded_name}"],
                        cwd=script_dir,
                        shell=True
                    )
                    self.update_status(f"✅ Process эхэлсэн (PID: {process.pid}) - shell=True - Player: {player_name}")
            else:
                # Mac/Linux дээр
                process = subprocess.Popen(
                    [sys.executable, game_file, f"--player-name={encoded_name}"],
                    cwd=script_dir,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    shell=False
                )
                self.update_status(f"✅ Process эхэлсэн (PID: {process.pid}) - Player: {player_name}")
            
            # Богино хугацааны дараа process амьд эсэхийг шалгах
            self.root.after(500, lambda: self.check_game_process(process))
            
            self.update_status("✅ Тоглоом эхэлсэн!")
            self.info_label.config(text="✅ Тоглоом эхэлсэн! Тоглоомын цонх нээгдлээ.")
        except Exception as e:
            error_msg = f"Тоглоом эхлэхэд алдаа гарлаа:\n\n{e}"
            self.update_status(f"❌ {error_msg}")
            messagebox.showerror("Алдаа", error_msg)
            import traceback
            traceback.print_exc()
    
    def check_game_process(self, process):
        """Тоглоомын process амьд эсэхийг шалгах"""
        if process.poll() is not None:
            # Process дууссан
            exit_code = process.returncode
            if exit_code != 0:
                self.update_status(f"⚠️ Тоглоом дууссан (Exit code: {exit_code})")
                self.info_label.config(text="⚠️ Тоглоом дууссан. Алдаа гарсан байж магадгүй.")
            else:
                self.update_status("✅ Тоглоом амжилттай дууссан")


def main():
    root = tk.Tk()
    app = EnhancedFaceRecognitionSystem(root)
    root.mainloop()


if __name__ == "__main__":
    print("="*60)
    print("🚀 FACE LOCK SYSTEM")
    print("="*60)
    print("✅ Tkinter дээр нүүр танилт")
    print("✅ dlib шаардлагагүй, зөвхөн OpenCV")
    print("="*60)
    print("\nПрограм эхэлж байна...\n")
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Програм зогссон")
    except Exception as e:
        print(f"\n❌ Алдаа: {e}")
        import traceback
        traceback.print_exc()


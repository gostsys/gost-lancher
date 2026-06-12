from __future__ import annotations

import json
import os
import shutil
import threading
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageOps

import launcher_core

try:
    from tkvideoplayer import TkinterVideo
except ImportError:
    TkinterVideo = None


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


BASE_DIR = Path(__file__).resolve().parent
CONFIG_FILE = BASE_DIR / "accounts.json"
BG_FOLDER = BASE_DIR / "backgrounds"
BG_FOLDER.mkdir(exist_ok=True)
LOGO_FILE = BASE_DIR / "logo.png"


class GostLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("GOST Launcher - Professional Edition")
        self.geometry("750x500")
        self.resizable(False, False)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.config_file = CONFIG_FILE
        self.bg_folder = BG_FOLDER

        self.config_data = {}
        self.load_config_data()

        self.current_bg_type = "none"
        self.is_muted = True
        self.is_flipped = False
        self.bg_label = None
        self.video_player = None
        self.raw_image = None
        self.preview_image = None
        self.current_view = "home"

        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0, fg_color="#141414")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        self.main_container = ctk.CTkFrame(self, fg_color="#0C0C0C", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.logo_image = None
        self.create_sidebar()
        self.create_main_panels()
        self.select_frame("home")
        self.auto_load_saved_background()

    def load_config_data(self):
        default_dir = Path(os.environ.get("APPDATA", str(Path.home()))) / ".gost_launcher"

        defaults = {
            "active_user": "GOST_Player",
            "all_accounts": ["GOST_Player"],
            "game_directory": str(default_dir),
            "active_background": "",
        }

        if not self.config_file.exists():
            self.config_data = defaults
            self.save_config_data()
            return

        try:
            with self.config_file.open("r", encoding="utf-8") as f:
                self.config_data = json.load(f)
        except Exception:
            self.config_data = defaults.copy()

        for key, value in defaults.items():
            self.config_data.setdefault(key, value)

        self.config_data["game_directory"] = str(Path(self.config_data["game_directory"]))
        active_bg = self.config_data.get("active_background", "")
        if active_bg:
            resolved = self.resolve_background_path(active_bg)
            if resolved and resolved.exists():
                self.config_data["active_background"] = self.store_background_path(resolved)
            else:
                self.config_data["active_background"] = ""

        self.save_config_data()

    def save_config_data(self):
        with self.config_file.open("w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

    def resolve_background_path(self, stored_path: str) -> Path | None:
        if not stored_path:
            return None

        p = Path(stored_path)
        candidates = []

        if p.is_absolute():
            candidates.append(p)
        else:
            candidates.append(BASE_DIR / p)
            candidates.append(self.bg_folder / p.name)

        if "\\" in stored_path:
            candidates.append(BASE_DIR / Path(stored_path.replace("\\", os.sep)))
            candidates.append(self.bg_folder / Path(stored_path).name)

        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        return None

    def store_background_path(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(BASE_DIR))
        except Exception:
            return str(path.resolve())

    def list_background_files(self):
        valid_exts = {".png", ".jpg", ".jpeg", ".mp4"}
        files = []
        for item in sorted(self.bg_folder.iterdir(), key=lambda p: p.name.lower()):
            if item.is_file() and item.suffix.lower() in valid_exts:
                files.append(item)
        return files

    def create_sidebar(self):
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="GOST",
            font=("Segoe UI", 24, "bold"),
            text_color="#00FF66",
        )
        self.logo_label.pack(pady=(25, 30))

        self.home_btn = ctk.CTkButton(
            self.sidebar_frame, text="الرئيسية", font=("Arial", 13, "bold"),
            fg_color="transparent", text_color="gray", hover_color="#222222",
            anchor="w", height=38, command=lambda: self.select_frame("home")
        )
        self.home_btn.pack(fill="x", padx=10, pady=4)

        self.accounts_btn = ctk.CTkButton(
            self.sidebar_frame, text="الحسابات", font=("Arial", 13, "bold"),
            fg_color="transparent", text_color="gray", hover_color="#222222",
            anchor="w", height=38, command=lambda: self.select_frame("accounts")
        )
        self.accounts_btn.pack(fill="x", padx=10, pady=4)

        self.settings_btn = ctk.CTkButton(
            self.sidebar_frame, text="الإعدادات", font=("Arial", 13, "bold"),
            fg_color="transparent", text_color="gray", hover_color="#222222",
            anchor="w", height=38, command=lambda: self.select_frame("settings")
        )
        self.settings_btn.pack(fill="x", padx=10, pady=4)

    def create_main_panels(self):
        # Home
        self.home_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.home_title = ctk.CTkLabel(self.home_frame, text="الصفحة الرئيسية", font=("Segoe UI", 18, "bold"), text_color="white")
        self.home_title.pack(pady=(30, 10), anchor="w", padx=40)

        self.current_user_display = ctk.CTkLabel(
            self.home_frame,
            text=f"اللاعب الحالي: {self.config_data['active_user']}",
            font=("Segoe UI", 14, "bold"),
            text_color="#00FF66",
        )
        self.current_user_display.pack(pady=10, anchor="w", padx=40)

        self.status_label = ctk.CTkLabel(self.home_frame, text="نظام الإطلاق جاهز تماماً", text_color="lightgray", font=("Arial", 12))
        self.status_label.pack(pady=(30, 5))

        self.progress_bar = ctk.CTkProgressBar(self.home_frame, width=420, fg_color="#1A1A1A", progress_color="#00FF66")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=2)

        self.progress_label = ctk.CTkLabel(self.home_frame, text="0%", font=("Arial", 11, "bold"), text_color="white")
        self.progress_label.pack(pady=2)

        self.version_menu = ctk.CTkOptionMenu(
            self.home_frame,
            values=[
                "1.21.1",
                "1.21",
                "1.20.6",
                "1.20.4",
                "1.20.1",
                "1.19.4",
                "1.18.2"
            ]
        )
        self.version_menu.set("1.20.1")
        self.version_menu.pack(pady=10)

        self.play_btn = ctk.CTkButton(
            self.home_frame, text="تشغيل اللعبة (PLAY)", font=("Segoe UI", 16, "bold"),
            fg_color="#00C853", hover_color="#009624", height=48, width=320,
            corner_radius=6, command=self.launch_game_threaded
        )
        self.play_btn.pack(pady=10)

        # Accounts
        self.accounts_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.acc_title = ctk.CTkLabel(self.accounts_frame, text="إدارة الحسابات", font=("Segoe UI", 18, "bold"), text_color="white")
        self.acc_title.pack(pady=(30, 20), anchor="w", padx=40)

        self.acc_label = ctk.CTkLabel(self.accounts_frame, text="اختر الحساب النشط للعب:", font=("Arial", 12), text_color="lightgray")
        self.acc_label.pack(pady=5, anchor="w", padx=40)

        self.acc_menu = ctk.CTkOptionMenu(
            self.accounts_frame,
            values=self.config_data["all_accounts"],
            command=self.switch_account,
            width=240,
            fg_color="#141414",
            button_color="#00C853",
            button_hover_color="#009624",
        )
        self.acc_menu.set(self.config_data["active_user"])
        self.acc_menu.pack(pady=5, anchor="w", padx=40)

        self.add_label = ctk.CTkLabel(self.accounts_frame, text="إنشاء حساب أوفلاين جديد:", font=("Arial", 12), text_color="lightgray")
        self.add_label.pack(pady=(25, 5), anchor="w", padx=40)

        self.add_row = ctk.CTkFrame(self.accounts_frame, fg_color="transparent")
        self.add_row.pack(fill="x", padx=40, pady=5)

        self.new_acc_entry = ctk.CTkEntry(
            self.add_row, placeholder_text="اسم الحساب الجديد...", width=160,
            fg_color="#141414", border_color="#222222"
        )
        self.new_acc_entry.pack(side="left", padx=(0, 10))

        self.add_btn = ctk.CTkButton(
            self.add_row, text="إضافة الحساب", width=100,
            fg_color="#00C853", hover_color="#009624", command=self.add_account
        )
        self.add_btn.pack(side="left")

        # Settings
        self.settings_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.set_title = ctk.CTkLabel(self.settings_frame, text="الإعدادات المتقدمة", font=("Segoe UI", 18, "bold"), text_color="white")
        self.set_title.pack(pady=(20, 10), anchor="w", padx=40)

        self.dir_card = ctk.CTkFrame(
            self.settings_frame,
            fg_color="#141414",
            corner_radius=8,
            height=75,
            border_width=1,
            border_color="#222222",
        )
        self.dir_card.pack(pady=5, padx=40, fill="x")
        self.dir_card.pack_propagate(False)

        self.dir_title = ctk.CTkLabel(
            self.dir_card,
            text="مسار تحميل وحفظ ملفات ماينكرافت الحالية:",
            font=("Arial", 11, "bold"),
            text_color="#00FF66",
        )
        self.dir_title.pack(anchor="w", padx=15, pady=4)

        self.path_row = ctk.CTkFrame(self.dir_card, fg_color="transparent")
        self.path_row.pack(fill="x", padx=15)

        current_path = self.config_data["game_directory"]
        display_path = current_path if len(current_path) <= 45 else current_path[:18] + "..." + current_path[-24:]
        self.dir_label = ctk.CTkLabel(self.path_row, text=display_path, font=("Consolas", 11), text_color="lightgray", anchor="w")
        self.dir_label.pack(side="left", fill="x", expand=True)

        self.change_dir_btn = ctk.CTkButton(
            self.path_row, text="تغيير المسار", font=("Arial", 11), width=90, height=26,
            fg_color="#222222", hover_color="#333333", command=self.change_directory
        )
        self.change_dir_btn.pack(side="right")

        self.bg_section_label = ctk.CTkLabel(
            self.settings_frame,
            text="تخصيص مظهر وخلفية اللانشر:",
            font=("Segoe UI", 13, "bold"),
            text_color="#00FF66",
        )
        self.bg_section_label.pack(anchor="w", padx=40, pady=(15, 5))

        self.preview_card = ctk.CTkFrame(
            self.settings_frame,
            fg_color="#101010",
            corner_radius=10,
            border_width=1,
            border_color="#222222",
            height=175,
        )
        self.preview_card.pack(fill="x", padx=40, pady=(0, 10))
        self.preview_card.pack_propagate(False)

        self.preview_title = ctk.CTkLabel(self.preview_card, text="المعاينة الحالية", font=("Arial", 11, "bold"), text_color="#00FF66")
        self.preview_title.pack(anchor="w", padx=14, pady=(10, 4))

        self.preview_image_label = ctk.CTkLabel(
            self.preview_card,
            text="لم يتم اختيار خلفية بعد",
            fg_color="#0A0A0A",
            corner_radius=8,
            width=250,
            height=125,
        )
        self.preview_image_label.pack(padx=14, pady=(0, 12), anchor="w")

        self.preview_hint = ctk.CTkLabel(
            self.preview_card,
            text="اختر ملفاً من القائمة أدناه أو ارفع ملفاً مخصصاً.",
            text_color="gray",
            font=("Arial", 11),
        )
        self.preview_hint.pack(anchor="w", padx=14, pady=(0, 10))

        self.thumbs_label = ctk.CTkLabel(
            self.settings_frame,
            text="الخلفيات الموجودة داخل المجلد:",
            font=("Arial", 12, "bold"),
            text_color="white",
        )
        self.thumbs_label.pack(anchor="w", padx=40, pady=(4, 4))

        self.thumbs_frame = ctk.CTkScrollableFrame(self.settings_frame, fg_color="transparent", height=90)
        self.thumbs_frame.pack(fill="x", padx=40, pady=(0, 5))

        self.render_background_buttons()

        self.bg_actions_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.bg_actions_frame.pack(fill="x", padx=40, pady=10)

        self.more_btn = ctk.CTkButton(
            self.bg_actions_frame, text="اختيار المزيد...", font=("Arial", 12),
            width=130, fg_color="#00C853", hover_color="#009624", command=self.open_explore_more_window
        )
        self.more_btn.pack(side="left", padx=(0, 15))

        self.custom_btn = ctk.CTkButton(
            self.bg_actions_frame, text="رفع صورة/فيديو مخصص", font=("Arial", 12),
            width=180, fg_color="#1E3D8A", hover_color="#152B61", command=self.upload_custom_media
        )
        self.custom_btn.pack(side="left")

        self.media_controls_frame = ctk.CTkFrame(
            self.settings_frame,
            fg_color="#0A0A0A",
            corner_radius=6,
            height=40,
            border_width=1,
            border_color="#222222",
        )

        self.mute_btn = ctk.CTkButton(
            self.media_controls_frame, text="🔇 كتم الصوت", font=("Arial", 11),
            width=100, fg_color="#141414", hover_color="#222222", command=self.toggle_bg_audio
        )
        self.mute_btn.pack(side="left", padx=10, pady=5)

        self.flip_btn = ctk.CTkButton(
            self.media_controls_frame, text="🔄 قلب الاتجاه", font=("Arial", 11),
            width=100, fg_color="#141414", hover_color="#222222", command=self.flip_bg_media
        )
        self.flip_btn.pack(side="left", padx=5, pady=5)

    def render_background_buttons(self):
        for child in self.thumbs_frame.winfo_children():
            child.destroy()

        files = self.list_background_files()
        if not files:
            empty_lbl = ctk.CTkLabel(self.thumbs_frame, text="لا توجد ملفات خلفية صالحة داخل المجلد.", text_color="gray")
            empty_lbl.pack(anchor="w", pady=5)
            return

        for file_path in files:
            btn = ctk.CTkButton(
                self.thumbs_frame,
                text=file_path.stem,
                font=("Arial", 11, "bold"),
                width=150,
                height=36,
                fg_color="#141414",
                hover_color="#222222",
                border_width=1,
                border_color="#333333",
                command=lambda p=file_path: self.apply_launcher_background(str(p)),
            )
            btn.pack(fill="x", padx=2, pady=3)

    def select_frame(self, name):
        self.home_frame.grid_forget()
        self.accounts_frame.grid_forget()
        self.settings_frame.grid_forget()

        self.home_btn.configure(fg_color="transparent", text_color="gray")
        self.accounts_btn.configure(fg_color="transparent", text_color="gray")
        self.settings_btn.configure(fg_color="transparent", text_color="gray")

        if name == "home":
            self.home_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
            self.home_btn.configure(fg_color="#141414", text_color="#00FF66")
        elif name == "accounts":
            self.accounts_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
            self.accounts_btn.configure(fg_color="#141414", text_color="#00FF66")
        elif name == "settings":
            self.settings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
            self.settings_btn.configure(fg_color="#141414", text_color="#00FF66")

        self.current_view = name
        if self.bg_label:
            self.bg_label.lower()
        if self.video_player:
            self.video_player.lower()

    def clean_current_background_widgets(self):
        if self.bg_label is not None:
            try:
                self.bg_label.destroy()
            except Exception:
                pass
            self.bg_label = None

        if self.video_player is not None:
            try:
                self.video_player.stop()
            except Exception:
                pass
            try:
                self.video_player.destroy()
            except Exception:
                pass
            self.video_player = None

    def update_preview_card(self, file_path: Path | None):
        if file_path is None or not file_path.exists():
            self.preview_image_label.configure(
                text="لم يتم اختيار خلفية بعد",
                image=None,
            )
            self.preview_image_label.image = None
            return

        if file_path.suffix.lower() == ".mp4":
            self.preview_image_label.configure(
                text=f"فيديو: {file_path.name}",
                image=None,
            )
            self.preview_image_label.image = None
            return

        try:
            preview = Image.open(file_path).convert("RGB")
            preview.thumbnail((250, 125), Image.Resampling.LANCZOS)

            canvas = Image.new("RGB", (250, 125), (16, 16, 16))
            x = (250 - preview.width) // 2
            y = (125 - preview.height) // 2
            canvas.paste(preview, (x, y))

            ctk_preview = ctk.CTkImage(light_image=canvas, dark_image=canvas, size=(250, 125))
            self.preview_image_label.configure(text="", image=ctk_preview)
            self.preview_image_label.image = ctk_preview
            self.preview_image = ctk_preview
        except Exception:
            self.preview_image_label.configure(text=f"تعذر عرض المعاينة: {file_path.name}", image=None)
            self.preview_image_label.image = None

    def apply_launcher_background(self, file_path):
        resolved = self.resolve_background_path(file_path) or Path(file_path)
        if not resolved.exists():
            self.gui_set_status(f"ملف الخلفية غير موجود: {resolved.name}")
            return

        self.clean_current_background_widgets()
        self.config_data["active_background"] = self.store_background_path(resolved)
        self.save_config_data()

        ext = resolved.suffix.lower()
        self.update_preview_card(resolved)

        if ext == ".mp4":
            if TkinterVideo is None:
                self.current_bg_type = "none"
                self.gui_set_status("مكتبة تشغيل الفيديو غير مثبتة. تم حفظ الملف فقط.")
                return

            self.current_bg_type = "video"
            self.media_controls_frame.pack(pady=10, padx=40, fill="x")

            self.video_player = TkinterVideo(master=self.main_container, scaled=True)
            self.video_player.grid(row=0, column=0, sticky="nsew")
            self.video_player.load(str(resolved))
            self.video_player.bind("<<Ended>>", lambda e: self.video_player.play())
            self.video_player.play()

            if self.is_muted:
                try:
                    self.video_player.mute()
                except Exception:
                    pass
        else:
            self.current_bg_type = "image"
            self.media_controls_frame.pack_forget()
            self.raw_image = Image.open(resolved)
            self.render_image_background()

        if self.current_view == "home":
            self.select_frame("home")
        elif self.current_view == "accounts":
            self.select_frame("accounts")
        elif self.current_view == "settings":
            self.select_frame("settings")

        self.gui_set_status(f"تم تطبيق الخلفية: {resolved.name}")

    def render_image_background(self):
        if self.raw_image is None:
            return

        self.update_idletasks()
        target_w = max(self.main_container.winfo_width(), 590)
        target_h = max(self.main_container.winfo_height(), 500)

        img = self.raw_image.copy()
        img = ImageOps.fit(img, (target_w, target_h), Image.Resampling.LANCZOS)

        if self.is_flipped:
            img = ImageOps.mirror(img)

        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(target_w, target_h))

        if self.bg_label is None:
            self.bg_label = ctk.CTkLabel(self.main_container, text="")
            self.bg_label.grid(row=0, column=0, sticky="nsew")

        self.bg_label.configure(image=ctk_img)
        self.bg_label.image = ctk_img
        self.bg_label.lower()

    def open_explore_more_window(self):
        explore_win = ctk.CTkToplevel(self)
        explore_win.title("كل الخلفيات المتوفرة")
        explore_win.geometry("420x350")
        explore_win.resizable(False, False)
        explore_win.attributes("-topmost", True)

        title_label = ctk.CTkLabel(explore_win, text="اختر أي ملف لتطبيقه كخلفية فورية:", font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=12)

        scroll_frame = ctk.CTkScrollableFrame(explore_win, width=380, height=260, fg_color="#141414")
        scroll_frame.pack(padx=15, pady=5, fill="both", expand=True)

        valid_files = self.list_background_files()

        if not valid_files:
            empty_lbl = ctk.CTkLabel(scroll_frame, text="المجلد فارغ حالياً! ضع فيه بعض الصور.", text_color="gray")
            empty_lbl.pack(pady=20)
            return

        for file_path in valid_files:
            btn = ctk.CTkButton(
                scroll_frame,
                text=f"📄 {file_path.name}",
                font=("Consolas", 11),
                anchor="w",
                fg_color="transparent",
                text_color="white",
                hover_color="#222222",
                command=lambda p=file_path: [self.apply_launcher_background(str(p)), explore_win.destroy()],
            )
            btn.pack(fill="x", padx=5, pady=3)

    def upload_custom_media(self):
        file_path = filedialog.askopenfilename(
            title="اختر ملف الخلفية المخصصة الخاصة بك",
            filetypes=[("Media Files", "*.png *.jpg *.jpeg *.mp4")],
        )
        if not file_path:
            return

        ext = Path(file_path).suffix.lower()
        secure_name = f"custom_active_bg{ext}"
        destination_path = self.bg_folder / secure_name

        try:
            shutil.copy(file_path, destination_path)
            self.apply_launcher_background(str(destination_path))
            self.gui_set_status("تم نسخ الميديا المخصصة وتفعيلها بنجاح!")
            self.render_background_buttons()
        except Exception as e:
            self.gui_set_status(f"فشل في نسخ الملف المخصص: {e}")

    def toggle_bg_audio(self):
        if self.current_bg_type == "video" and self.video_player:
            if self.is_muted:
                try:
                    self.video_player.unmute()
                    self.is_muted = False
                    self.mute_btn.configure(text="🔊 كتم الصوت")
                    self.gui_set_status("تم تشغيل صوت الخلفية.")
                except Exception:
                    pass
            else:
                try:
                    self.video_player.mute()
                    self.is_muted = True
                    self.mute_btn.configure(text="🔇 تشغيل الصوت")
                    self.gui_set_status("تم كتم صوت الخلفية.")
                except Exception:
                    pass

    def flip_bg_media(self):
        self.is_flipped = not self.is_flipped
        if self.current_bg_type == "image":
            self.render_image_background()
            self.gui_set_status("تم قلب اتجاه الصورة.")
        elif self.current_bg_type == "video":
            self.gui_set_status("تم تعديل اتجاه عرض الفيديو.")

    def auto_load_saved_background(self):
        saved_bg = self.config_data.get("active_background", "")
        resolved = self.resolve_background_path(saved_bg)
        if resolved and resolved.exists():
            self.apply_launcher_background(str(resolved))
        elif saved_bg:
            self.config_data["active_background"] = ""
            self.save_config_data()

    def switch_account(self, choice):
        self.config_data["active_user"] = choice
        self.save_config_data()
        self.current_user_display.configure(text=f"اللاعب الحالي: {choice}")
        self.gui_set_status(f"تم تبديل الحساب النشط إلى: {choice}")

    def add_account(self):
        new_name = self.new_acc_entry.get().strip()
        if new_name and new_name not in self.config_data["all_accounts"]:
            self.config_data["all_accounts"].append(new_name)
            self.config_data["active_user"] = new_name
            self.save_config_data()

            self.acc_menu.configure(values=self.config_data["all_accounts"])
            self.acc_menu.set(new_name)
            self.current_user_display.configure(text=f"اللاعب الحالي: {new_name}")
            self.new_acc_entry.delete(0, "end")
            self.gui_set_status(f"تم إضافة وترقية الحساب إلى {new_name} بنجاح!")

    def change_directory(self):
        chosen_dir = filedialog.askdirectory(
            initialdir=self.config_data["game_directory"],
            title="اختر مجلد حفظ ملفات ماينكرافت",
        )
        if chosen_dir:
            chosen_dir = str(Path(chosen_dir).resolve())
            self.config_data["game_directory"] = chosen_dir
            self.save_config_data()

            display_path = chosen_dir if len(chosen_dir) <= 45 else chosen_dir[:18] + "..." + chosen_dir[-24:]
            self.dir_label.configure(text=display_path)
            self.gui_set_status("تم تحديث مسار الحفظ التلقائي!")

    def gui_set_status(self, text):
        self.status_label.configure(text=text, text_color="#00FF66")

    def gui_set_progress(self, current, max_val):
        if max_val > 0:
            fraction = current / max_val
            fraction = min(max(fraction, 0.0), 1.0)
            self.progress_bar.set(fraction)
            self.progress_label.configure(text=f"{int(fraction * 100)}%", text_color="#00FF66" if fraction == 1.0 else "white")

    def launch_game_threaded(self):
        self.play_btn.configure(state="disabled", text="جاري التحميل الفعلي...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.select_frame("home")

        game_thread = threading.Thread(target=self.run_backend_launch, daemon=True)
        game_thread.start()

    def run_backend_launch(self):
        try:
            username = self.config_data["active_user"]
            game_dir = self.config_data["game_directory"]
            max_files = [0]

            def set_status_cb(text):
                self.after(0, lambda: self.gui_set_status(text))

            def set_progress_cb(val):
                self.after(0, lambda: self.gui_set_progress(val, max_files[0]))

            def set_max_cb(val):
                max_files[0] = val

            callbacks = {
                "setStatus": set_status_cb,
                "setProgress": set_progress_cb,
                "setMax": set_max_cb,
            }

            launcher_core.launch_game(username, game_dir, self.version_menu.get(), callbacks)

            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.progress_label.configure(text="100%", text_color="#00FF66"))
            self.after(0, lambda: self.status_label.configure(text="تم إطلاق عملية ماينكرافت بنجاح!", text_color="#00FF66"))
            self.after(2000, lambda: self.play_btn.configure(state="normal", text="تشغيل اللعبة (PLAY)"))

        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"خطأ في التحميل: {e}", text_color="red"))
            self.after(0, lambda: self.play_btn.configure(state="normal", text="تشغيل اللعبة (PLAY)"))


if __name__ == "__main__":
    app = GostLauncher()
    app.mainloop()
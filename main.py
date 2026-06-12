import customtkinter as ctk
import json
import threading
import os
import shutil
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import launcher_core

# محاولة استيراد مكتبة تشغيل الفيديو، وتوفير بديل آمن في حال عدم تثبيتها بعد
try:
    from tkvideoplayer import TkinterVideo
except ImportError:
    TkinterVideo = None

# إعداد المظهر الداكن البسيط الاحترافي
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green") # تحويل السمة العامة إلى الأخضر المتناسق

class GostLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GOST Launcher - Professional Edition")
        self.geometry("750x500")
        self.resizable(False, False)

        # تكوين نظام شبكة الـ Grid للتقسيم الأساسي (Sidebar + Main Panel Container)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.config_file = "accounts.json"
        self.load_config_data()
        
        # متغيرات نظام الخلفيات المتقدم
        self.bg_folder = "backgrounds"
        os.makedirs(self.bg_folder, exist_ok=True)
        
        self.current_bg_type = "none" # none, image, video
        self.is_muted = True
        self.is_flipped = False
        self.bg_label = None
        self.video_player = None
        self.raw_image = None 

        # الحاوية الرئيسية اليمنى (Carbon Dark Background)
        self.main_container = ctk.CTkFrame(self, fg_color="#0C0C0C", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # إنشاء العناصر والواجهات بالثيم الجديد
        self.create_sidebar()
        self.create_main_panels()
        
        # فتح الصفحة الرئيسية بشكل افتراضي عند التشغيل
        self.select_frame("home")
        
        # تفعيل آخر خلفية تم حفظها تلقائياً عند الإقلاع إن وجدت
        self.auto_load_saved_background()

    def load_config_data(self):
        """قراءة الحسابات وإعدادات مجلد اللعبة"""
        default_dir = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), ".gost_launcher")
        
        if not os.path.exists(self.config_file):
            self.config_data = {
                "active_user": "GOST_Player", 
                "all_accounts": ["GOST_Player"],
                "game_directory": default_dir,
                "active_background": ""
            }
            self.save_config_data()
        else:
            with open(self.config_file, "r", encoding="utf-8") as f:
                try:
                    self.config_data = json.load(f)
                except json.JSONDecodeError:
                    self.config_data = {
                        "active_user": "GOST_Player", 
                        "all_accounts": ["GOST_Player"],
                        "game_directory": default_dir,
                        "active_background": ""
                    }
            if "game_directory" not in self.config_data:
                self.config_data["game_directory"] = default_dir
            if "active_background" not in self.config_data:
                self.config_data["active_background"] = ""
            self.save_config_data()

    def save_config_data(self):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=4, ensure_ascii=False)

    def create_sidebar(self):
        """إنشاء العمود الجانبي الأيسر بثيم الكربون المظلم"""
        self.sidebar_frame = ctk.CTkFrame(self, width=160, corner_radius=0, fg_color="#141414")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        # اللوغو المشع باللون الزمردي الحاد (Emerald Highlight)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="GOST", font=("Segoe UI", 24, "bold"), text_color="#00FF66")
        self.logo_label.pack(pady=(25, 30))

        # أزرار التنقل الأساسية متناسقة مع المظهر الاحترافي
        self.home_btn = ctk.CTkButton(
            self.sidebar_frame, text="الرئيسية", font=("Arial", 13, "bold"),
            fg_color="transparent", text_color="gray", hover_color="#222222", anchor="w", height=38,
            command=lambda: self.select_frame("home")
        )
        self.home_btn.pack(fill="x", padx=10, pady=4)

        self.accounts_btn = ctk.CTkButton(
            self.sidebar_frame, text="الحسابات", font=("Arial", 13, "bold"),
            fg_color="transparent", text_color="gray", hover_color="#222222", anchor="w", height=38,
            command=lambda: self.select_frame("accounts")
        )
        self.accounts_btn.pack(fill="x", padx=10, pady=4)

        self.settings_btn = ctk.CTkButton(
            self.sidebar_frame, text="الإعدادات", font=("Arial", 13, "bold"),
            fg_color="transparent", text_color="gray", hover_color="#222222", anchor="w", height=38,
            command=lambda: self.select_frame("settings")
        )
        self.settings_btn.pack(fill="x", padx=10, pady=4)

    def create_main_panels(self):
        """إنشاء اللوحات المختلفة للقسم الرئيسي لتطفو فوق الكربون أو الخلفية الحركية"""
        
        # 1. لوحة الصفحة الرئيسية (Home Panel)
        self.home_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        self.home_title = ctk.CTkLabel(self.home_frame, text="الصفحة الرئيسية", font=("Segoe UI", 18, "bold"), text_color="white")
        self.home_title.pack(pady=(30, 10), anchor="w", padx=40)

        self.current_user_display = ctk.CTkLabel(
            self.home_frame, 
            text=f"اللاعب الحالي: {self.config_data['active_user']}", 
            font=("Segoe UI", 14, "bold"), text_color="#00FF66"
        )
        self.current_user_display.pack(pady=10, anchor="w", padx=40)

        self.status_label = ctk.CTkLabel(self.home_frame, text="نظام الإطلاق جاهز تماماً", text_color="lightgray", font=("Arial", 12))
        self.status_label.pack(pady=(40, 5))

        # شريط التقدم باللون الأخضر الماسي
        self.progress_bar = ctk.CTkProgressBar(self.home_frame, width=420, fg_color="#1A1A1A", progress_color="#00FF66")
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=2)

        self.progress_label = ctk.CTkLabel(self.home_frame, text="0%", font=("Arial", 11, "bold"), text_color="white")
        self.progress_label.pack(pady=2)

        # زر تشغيل غامر وأكثر لمعاناً (Minecraft Emerald Green)
        self.play_btn = ctk.CTkButton(
            self.home_frame, text="تشغيل اللعبة (PLAY)", font=("Segoe UI", 16, "bold"),
            fg_color="#00C853", hover_color="#009624", height=48, width=320,
            corner_radius=6, command=self.launch_game_threaded
        )
        self.play_btn.pack(pady=25)

        # 2. لوحة إدارة الحسابات (Accounts Panel)
        self.accounts_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        self.acc_title = ctk.CTkLabel(self.accounts_frame, text="إدارة الحسابات", font=("Segoe UI", 18, "bold"), text_color="white")
        self.acc_title.pack(pady=(30, 20), anchor="w", padx=40)

        self.acc_label = ctk.CTkLabel(self.accounts_frame, text="اختر الحساب النشط للعب:", font=("Arial", 12), text_color="lightgray")
        self.acc_label.pack(pady=5, anchor="w", padx=40)

        self.acc_menu = ctk.CTkOptionMenu(
            self.accounts_frame, values=self.config_data["all_accounts"], 
            command=self.switch_account, width=240, fg_color="#141414", button_color="#00C853", button_hover_color="#009624"
        )
        self.acc_menu.set(self.config_data["active_user"])
        self.acc_menu.pack(pady=5, anchor="w", padx=40)

        self.add_label = ctk.CTkLabel(self.accounts_frame, text="إنشاء حساب أوفلاين جديد:", font=("Arial", 12), text_color="lightgray")
        self.add_label.pack(pady=(25, 5), anchor="w", padx=40)

        self.add_row = ctk.CTkFrame(self.accounts_frame, fg_color="transparent")
        self.add_row.pack(fill="x", padx=40, pady=5)

        self.new_acc_entry = ctk.CTkEntry(self.add_row, placeholder_text="اسم الحساب الجديد...", width=160, fg_color="#141414", border_color="#222222")
        self.new_acc_entry.pack(side="left", padx=(0, 10))

        self.add_btn = ctk.CTkButton(self.add_row, text="إضافة الحساب", width=100, fg_color="#00C853", hover_color="#009624", command=self.add_account)
        self.add_btn.pack(side="left")

        # 3. لوحة الإعدادات المتقدمة (Settings Panel)
        self.settings_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
        self.set_title = ctk.CTkLabel(self.settings_frame, text="الإعدادات المتقدمة", font=("Segoe UI", 18, "bold"), text_color="white")
        self.set_title.pack(pady=(20, 10), anchor="w", padx=40)

        # بطاقة المسار بثيم متناسق ومحدد
        self.dir_card = ctk.CTkFrame(self.settings_frame, fg_color="#141414", corner_radius=8, height=75, border_width=1, border_color="#222222")
        self.dir_card.pack(pady=5, padx=40, fill="x")
        self.dir_card.pack_propagate(False)

        self.dir_title = ctk.CTkLabel(self.dir_card, text="مسار تحميل وحفظ ملفات ماينكرافت الحالية:", font=("Arial", 11, "bold"), text_color="#00FF66")
        self.dir_title.pack(anchor="w", padx=15, pady=4)

        self.path_row = ctk.CTkFrame(self.dir_card, fg_color="transparent")
        self.path_row.pack(fill="x", padx=15)

        current_path = self.config_data["game_directory"]
        display_path = current_path if len(current_path) <= 45 else current_path[:18] + "..." + current_path[-24:]

        self.dir_label = ctk.CTkLabel(self.path_row, text=display_path, font=("Consolas", 11), text_color="lightgray", anchor="w")
        self.dir_label.pack(side="left", fill="x", expand=True)

        self.change_dir_btn = ctk.CTkButton(self.path_row, text="تغيير المسار", font=("Arial", 11), width=90, height=26, fg_color="#222222", hover_color="#333333", command=self.change_directory)
        self.change_dir_btn.pack(side="right")

        # تخصيص مظهر وخلفية اللانشر
        self.bg_section_label = ctk.CTkLabel(self.settings_frame, text="تخصيص مظهر وخلفية اللانشر:", font=("Segoe UI", 13, "bold"), text_color="#00FF66")
        self.bg_section_label.pack(anchor="w", padx=40, pady=(15, 5))

        # حاوية عرض الصور الأساسية الثلاث
        self.thumbs_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.thumbs_frame.pack(fill="x", padx=40, pady=5)

        default_images = ["gost_void.png", "mc_isometric.png", "pixel_gost.png"]
        for img_name in default_images:
            btn = ctk.CTkButton(
                self.thumbs_frame, text=img_name.split('.')[0], font=("Arial", 11, "bold"),
                width=110, height=45, fg_color="#141414", hover_color="#222222", border_width=1, border_color="#333333",
                command=lambda name=img_name: self.apply_launcher_background(os.path.join(self.bg_folder, name))
            )
            btn.pack(side="left", padx=(0, 12))

        # صف أزرار التحكم بالتخصيص
        self.bg_actions_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.bg_actions_frame.pack(fill="x", padx=40, pady=10)

        self.more_btn = ctk.CTkButton(
            self.bg_actions_frame, text="🌌 اختيار المزيد...", font=("Arial", 12),
            width=130, fg_color="#00C853", hover_color="#009624", command=self.open_explore_more_window
        )
        self.more_btn.pack(side="left", padx=(0, 15))

        self.custom_btn = ctk.CTkButton(
            self.bg_actions_frame, text="⚙️ قسم مخصصة (صورة/فيديو)", font=("Arial", 12),
            width=180, fg_color="#1E3D8A", hover_color="#152B61", command=self.upload_custom_media
        )
        self.custom_btn.pack(side="left")

        # شريط أدوات التحكم بالفيديو والصور المخصصة
        self.media_controls_frame = ctk.CTkFrame(self.settings_frame, fg_color="#0A0A0A", corner_radius=6, height=40, border_width=1, border_color="#222222")
        
        self.mute_btn = ctk.CTkButton(self.media_controls_frame, text="🔇 كتم الصوت", font=("Arial", 11), width=100, fg_color="#141414", hover_color="#222222", command=self.toggle_bg_audio)
        self.mute_btn.pack(side="left", padx=10, pady=5)

        self.flip_btn = ctk.CTkButton(self.media_controls_frame, text="🔄 قلب الاتجاه", font=("Arial", 11), width=100, fg_color="#141414", hover_color="#222222", command=self.flip_bg_media)
        self.flip_btn.pack(side="left", padx=5, pady=5)

    def select_frame(self, name):
        """التحكم في التبديل الحركي وإبراز الزر النشط باللون الزمردي"""
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

        if self.bg_label: self.bg_label.lower()
        if self.video_player: self.video_player.lower()

    def clean_current_background_widgets(self):
        """تنظيف أدوات الخلفية لمنع الكراش أو تسريب الذاكرة"""
        if self.bg_label:
            self.bg_label.destroy()
            self.bg_label = None
        if self.video_player:
            try: self.video_player.stop()
            except: pass
            self.video_player.destroy()
            self.video_player = None

    def apply_launcher_background(self, file_path):
        """تطبيق وحفظ مسار الخلفية المحددة تلقائياً وتحديد نوعها برمجياً"""
        if not os.path.exists(file_path):
            return

        self.clean_current_background_widgets()
        ext = os.path.splitext(file_path)[1].lower()

        self.config_data["active_background"] = file_path
        self.save_config_data()

        if ext == ".mp4" and TkinterVideo is not None:
            self.current_bg_type = "video"
            self.media_controls_frame.pack(pady=10, padx=40, fill="x")
            
            self.video_player = TkinterVideo(master=self.main_container, scaled=True)
            self.video_player.grid(row=0, column=0, sticky="nsew")
            self.video_player.load(file_path)
            
            self.video_player.bind("<<Ended>>", lambda e: self.video_player.play())
            self.video_player.play()
            
            if self.is_muted:
                try: self.video_player.mute()
                except: pass
        else:
            self.current_bg_type = "image"
            self.media_controls_frame.pack_forget() 
            
            self.raw_image = Image.open(file_path)
            self.render_image_background()

        # إعادة إنعاش اللوحة الحالية لتظل تطفو في الصدارة فوق الميديا
        if self.home_frame.winfo_manager(): self.select_frame("home")
        elif self.accounts_frame.winfo_manager(): self.select_frame("accounts")
        elif self.settings_frame.winfo_manager(): self.select_frame("settings")

    def render_image_background(self):
        """تحجيم الصورة وعرضها على اللانشر"""
        if self.raw_image is None: return
        
        img = self.raw_image.resize((590, 500), Image.Resampling.LANCZOS)
        if self.is_flipped:
            img = ImageOps.mirror(img)
            
        ctk_img = ImageTk.PhotoImage(img)
        
        if self.bg_label is None:
            self.bg_label = ctk.CTkLabel(self.main_container, text="")
            self.bg_label.grid(row=0, column=0, sticky="nsew")
        
        self.bg_label.configure(image=ctk_img)
        self.bg_label.image = ctk_img
        self.bg_label.lower()

    def open_explore_more_window(self):
        """فتح واجهة منبثقة مستقلة تعرض كافة محتويات المجلد بالكامل"""
        explore_win = ctk.CTkToplevel(self)
        explore_win.title("كل الخلفيات المتوفرة")
        explore_win.geometry("420x350")
        explore_win.resizable(False, False)
        explore_win.attributes("-topmost", True)

        title_label = ctk.CTkLabel(explore_win, text="اختر أي ملف لتطبيقه كخلفية فورية:", font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=12)

        scroll_frame = ctk.CTkScrollableFrame(explore_win, width=380, height=260, fg_color="#141414")
        scroll_frame.pack(padx=15, pady=5, fill="both", expand=True)

        all_files = os.listdir(self.bg_folder)
        valid_extensions = ('.png', '.jpg', '.jpeg', '.mp4')
        
        count = 0
        for file in all_files:
            if file.lower().endswith(valid_extensions):
                count += 1
                full_p = os.path.join(self.bg_folder, file)
                btn = ctk.CTkButton(
                    scroll_frame, text=f"📄 {file}", font=("Consolas", 11),
                    anchor="w", fg_color="transparent", text_color="white", hover_color="#222222",
                    command=lambda p=full_p: [self.apply_launcher_background(p), explore_win.destroy()]
                )
                btn.pack(fill="x", padx=5, pady=3)
                
        if count == 0:
            empty_lbl = ctk.CTkLabel(scroll_frame, text="المجلد فارغ حالياً! ضع فيه بعض الصور.", text_color="gray")
            empty_lbl.pack(pady=20)

    def upload_custom_media(self):
        """رفع صورة أو فيديو مخصص وأخذ نسخة تلقائية داخل ملفات المشروع"""
        file_path = filedialog.askopenfilename(
            title="اختر ملف الخلفية المخصصة الخاصة بك",
            filetypes=[("Media Files", "*.png *.jpg *.jpeg *.mp4")]
        )
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            secure_name = f"custom_active_bg{ext}"
            destination_path = os.path.join(self.bg_folder, secure_name)
            
            try:
                shutil.copy(file_path, destination_path)
                self.apply_launcher_background(destination_path)
                self.gui_set_status("تم نسخ الميديا المخصصة وتفعيلها بنجاح!")
            except Exception as e:
                self.gui_set_status(f"فشل في نسخ الملف المخصص: {str(e)}")

    def toggle_bg_audio(self):
        """تبديل حالة كتم الصوت للفيديو الخلفي"""
        if self.current_bg_type == "video" and self.video_player:
            if self.is_muted:
                try:
                    self.video_player.unmute()
                    self.is_muted = False
                    self.mute_btn.configure(text="🔊 كتم الصوت")
                except: pass
            else:
                try:
                    self.video_player.mute()
                    self.is_muted = True
                    self.mute_btn.configure(text="🔇 تشغيل الصوت")
                except: pass

    def flip_bg_media(self):
        """قلب اتجاه الميديا المخصصة مرآتياً"""
        self.is_flipped = not self.is_flipped
        if self.current_bg_type == "image":
            self.render_image_background()
        elif self.current_bg_type == "video":
            self.gui_set_status("تم تعديل اتجاه عرض الدوران المرآتي للملف!")

    def auto_load_saved_background(self):
        """فحص وتحميل آخر مظهر محفوظ تلقائياً عند الإقلاع"""
        saved_bg = self.config_data.get("active_background", "")
        if saved_bg and os.path.exists(saved_bg):
            self.apply_launcher_background(saved_bg)

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
            self.new_acc_entry.delete(0, 'end')
            self.gui_set_status(f"تم إضافة وترقية الحساب إلى {new_name} بنجاح!")

    def change_directory(self):
        chosen_dir = filedialog.askdirectory(
            initialdir=self.config_data["game_directory"], 
            title="اختر مجلد حفظ ملفات ماينكرافت"
        )
        if chosen_dir:
            chosen_dir = os.path.normpath(chosen_dir)
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
        
        game_thread = threading.Thread(target=self.run_backend_launch)
        game_thread.daemon = True
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

            callbacks = {"setStatus": set_status_cb, "setProgress": set_progress_cb, "setMax": set_max_cb}
            launcher_core.launch_game(username, game_dir, callbacks)
            
            self.after(0, lambda: self.progress_bar.set(1.0))
            self.after(0, lambda: self.progress_label.configure(text="100%", text_color="#00FF66"))
            self.after(0, lambda: self.status_label.configure(text="تم إطلاق عملية ماينكرافت بنجاح!", text_color="#00FF66"))
            self.after(4000, lambda: self.play_btn.configure(state="normal", text="تشغيل اللعبة (PLAY)"))
            
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"خطأ في التحميل: {str(e)}", text_color="red"))
            self.after(0, lambda: self.play_btn.configure(state="normal", text="تشغيل اللعبة (PLAY)"))

if __name__ == "__main__":
    app = GostLauncher()
    app.mainloop()
    app = GostLauncher()
    app.mainloop()
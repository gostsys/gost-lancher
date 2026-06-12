import minecraft_launcher_lib
import subprocess
import os

def launch_game(username, game_dir, callbacks=None):
    """
    تشغيل إصدار 1.20.1 مع تحديد مسار الجافا المحملة تلقائياً لمنع الكراش الصامت.
    """
    os.makedirs(game_dir, exist_ok=True)
    version = "1.20.1"
    
    if callbacks:
        callbacks["setStatus"]("جاري فحص الملفات وتحميل الناقص...")
        minecraft_launcher_lib.install.install_minecraft_version(version, game_dir, callbacks)
    else:
        minecraft_launcher_lib.install.install_minecraft_version(version, game_dir)
        
    options = {
        "username": username,
        "uuid": "",  
        "token": "",
        "launcherName": "GOST_Launcher",
        "launcherVersion": "1.0"
    }

    # 🔥 الحل: البحث عن الجافا الرسمية التي حملتها المكتبة وتمريرها للاستخدام
    try:
        if callbacks: callbacks["setStatus"]("جاري تحديد مسار الجافا المتوافقة...")
        # جلب مسار جافا المخصصة لهذا الإصدار تلقائياً
        runtime_id = minecraft_launcher_lib.utils.get_environment_java_version(version, game_dir)
        java_exe = minecraft_launcher_lib.runtime.get_executable_path(runtime_id, game_dir)
        if java_exe:
            options["executablePath"] = java_exe
    except Exception:
        # في حال عدم العثور عليها، سيعتمد على جافا الجهاز الافتراضية
        pass
    
    minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
        version=version,
        minecraft_directory=game_dir,
        options=options
    )
    
    if callbacks:
        callbacks["setStatus"]("تم إطلاق عملية ماينكرافت الحقيقية بنجاح!")
        
    # تشغيل اللعبة وإبقاء المخرجات في الـ Terminal لرصد أي نقص في كرت الشاشة أو الذاكرة
    subprocess.Popen(minecraft_command)
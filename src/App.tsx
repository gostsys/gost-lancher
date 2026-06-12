import React, { useState, useEffect } from 'react';
import { Home, Users, Settings, Play, Folder, Plus, CheckCircle, Terminal, Shield } from 'lucide-react';

export default function App() {
  // الحسابات والإعدادات الحقيقية المستخرجة من مشروعك
  const [activeTab, setActiveTab] = useState<'home' | 'accounts' | 'settings'>('home');
  const [activeUser, setActiveUser] = useState('mohamad1234te');
  const [accounts, setAccounts] = useState(['GOST_Player', 'Pixel_Ghost', 'mohamad1234te']);
  const [gameDirectory, setGameDirectory] = useState('C:\\Users\\SAMSUNG\\AppData\\Roaming\\.gost_launcher');
  const [newAccount, setNewAccount] = useState('');
  
  // حالات محاكاة تشغيل اللعبة
  const [isLaunching, setIsLaunching] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('نظام الإطلاق جاهز تماماً');
  const [logs, setLogs] = useState<string[]>([]);

  // محاكاة عملية تشغيل اللعبة عند الضغط على PLAY
  const handleLaunch = () => {
    if (isLaunching) return;
    setIsLaunching(true);
    setProgress(0);
    setLogs([]);
    
    const steps = [
      { prg: 15, msg: 'جاري فحص متبقيات ملفات ماينكرافت الأصلية...', log: 'Checking local assets in .gost_launcher...' },
      { prg: 40, msg: 'جاري تحميل وتحديث ملفات إصدار 1.20.1 الناقصة...', log: 'Downloading Minecraft 1.20.1 client jar...' },
      { prg: 70, msg: 'جاري تحديد مسار الجافا المتوافقة تلقائياً...', log: 'Located runtime Java environment: javaw.exe' },
      { prg: 90, msg: 'تحضير خيارات تسجيل الدخول للحساب النشط...', log: `Setting options for user: ${activeUser}` },
      { prg: 100, msg: 'تم إطلاق عملية ماينكرافت بنجاح! استمتع باللعب.', log: 'Minecraft process started. Launching game window...' }
    ];

    steps.forEach((step, index) => {
      setTimeout(() => {
        setProgress(step.prg);
        setStatusText(step.msg);
        setLogs(prev => [...prev, `[GOST Core] ${step.log}`]);
        if (step.prg === 100) {
          setTimeout(() => {
            setIsLaunching(false);
            setStatusText('نظام الإطلاق جاهز تماماً');
          }, 4000);
        }
      }, (index + 1) * 1200);
    });
  };

  const handleAddAccount = (e: React.FormEvent) => {
    e.preventDefault();
    if (newAccount.trim() && !accounts.includes(newAccount.trim())) {
      setAccounts([...accounts, newAccount.trim()]);
      setActiveUser(newAccount.trim());
      setNewAccount('');
      setStatusText(`تم إضافة وترقية الحساب إلى ${newAccount} بنجاح!`);
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#0C0C0C] text-gray-200 font-sans overflow-hidden select-none">
      
      {/* 1. القائمة الجانبية (Sidebar) - الكربون الداكن مع اللمسة الزمردية */}
      <div className="w-52 bg-[#141414] border-r border-[#222222] flex flex-col justify-between p-4">
        <div>
          {/* شعار GOST باللون الأخضر المضيء */}
          <div className="flex items-center gap-2 px-2 py-4 mb-6">
            <Shield className="w-7 h-7 text-[#00FF66] drop-shadow-[0_0_8px_rgba(0,255,102,0.5)]" />
            <span className="text-2xl font-black tracking-wider text-white">GOST</span>
          </div>

          {/* أزرار التنقل */}
          <nav className="space-y-1">
            <button
              onClick={() => setActiveTab('home')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold transition-all ${
                activeTab === 'home' 
                  ? 'bg-[#1A1A1A] text-[#00FF66] border-l-2 border-[#00FF66]' 
                  : 'text-gray-400 hover:bg-[#1A1A1A] hover:text-gray-200'
              }`}
            >
              <Home className="w-4 h-4" />
              الرئيسية
            </button>
            <button
              onClick={() => setActiveTab('accounts')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold transition-all ${
                activeTab === 'accounts' 
                  ? 'bg-[#1A1A1A] text-[#00FF66] border-l-2 border-[#00FF66]' 
                  : 'text-gray-400 hover:bg-[#1A1A1A] hover:text-gray-200'
              }`}
            >
              <Users className="w-4 h-4" />
              الحسابات
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-bold transition-all ${
                activeTab === 'settings' 
                  ? 'bg-[#1A1A1A] text-[#00FF66] border-l-2 border-[#00FF66]' 
                  : 'text-gray-400 hover:bg-[#1A1A1A] hover:text-gray-200'
              }`}
            >
              <Settings className="w-4 h-4" />
              الإعدادات
            </button>
          </nav>
        </div>

        {/* معلومات الإصدار أسفل القائمة */}
        <div className="text-center text-xs text-gray-600 font-mono border-t border-[#222222] pt-3">
          GOST Launcher v1.0.0
        </div>
      </div>

      {/* 2. اللوحة الرئيسية (Main Panel Container) */}
      <div className="flex-1 flex flex-col justify-between p-8 bg-gradient-to-b from-[#0C0C0C] to-[#060606] relative">
        
        {/* المحتوى المتغير حسب التبويب النشط */}
        <div className="flex-1">
          {/* واجهة الصفحة الرئيسية */}
          {activeTab === 'home' && (
            <div className="space-y-6 animate-fadeIn">
              <div>
                <h1 className="text-2xl font-black text-white">الصفحة الرئيسية</h1>
                <p className="text-sm text-gray-400 mt-1">مرحباً بك في نظام تشغيل ماينكرافت المستقر.</p>
              </div>

              {/* بطاقة عرض اللاعب الحالي مع تأثير توهج الزمرد */}
              <div className="bg-[#141414] p-5 rounded-lg border border-[#222222] inline-block min-w-[280px] shadow-xl">
                <span className="text-xs font-bold uppercase tracking-wider text-gray-500 block">اللاعب الحالي النشط</span>
                <span className="text-xl font-black text-[#00FF66] mt-1 block font-mono">
                  {activeUser}
                </span>
              </div>

              {/* شاشة الأكواد واللوجات المصغرة أثناء التحميل */}
              {logs.length > 0 && (
                <div className="bg-[#050505] rounded-lg p-4 border border-[#1A1A1A] font-mono text-xs text-gray-400 max-w-xl shadow-inner space-y-1">
                  <div className="flex items-center gap-2 text-gray-500 mb-2 border-b border-[#111111] pb-1">
                    <Terminal className="w-3.5 h-3.5 text-[#00FF66]" />
                    <span>سجل نظام الإطلاق الحي (Live Stream Logs)</span>
                  </div>
                  {logs.map((log, i) => (
                    <div key={i} className="truncate">{log}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* واجهة الحسابات */}
          {activeTab === 'accounts' && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-black text-white">إدارة الحسابات</h1>
                <p className="text-sm text-gray-400 mt-1">اختر حساباً نشطاً أو قم بإنشاء مستخدم جديد.</p>
              </div>

              <div className="max-w-md space-y-4">
                <div className="bg-[#141414] p-5 rounded-lg border border-[#222222] space-y-3">
                  <label className="text-sm font-bold text-gray-400 block">اختر الحساب الحالي للعب:</label>
                  <select 
                    value={activeUser}
                    onChange={(e) => {
                      setActiveUser(e.target.value);
                      setStatusText(`تم تبديل الحساب النشط إلى: ${e.target.value}`);
                    }}
                    className="w-full bg-[#0C0C0C] border border-[#222222] rounded px-3 py-2 text-sm text-white focus:outline-none focus:border-[#00FF66] font-mono"
                  >
                    {accounts.map(acc => (
                      <option key={acc} value={acc}>{acc}</option>
                    ))}
                  </select>
                </div>

                <form onSubmit={handleAddAccount} className="bg-[#141414] p-5 rounded-lg border border-[#222222] space-y-3">
                  <label className="text-sm font-bold text-gray-400 block">إنشاء حساب أوفلاين جديد:</label>
                  <div className="flex gap-2">
                    <input 
                      type="text" 
                      placeholder="اسم الحساب الجديد..."
                      value={newAccount}
                      onChange={(e) => setNewAccount(e.target.value)}
                      className="flex-1 bg-[#0C0C0C] border border-[#222222] rounded px-3 py-1.5 text-sm text-white focus:outline-none focus:border-[#00FF66]"
                    />
                    <button 
                      type="submit"
                      className="bg-[#00C853] hover:bg-[#009624] text-black text-sm font-bold px-4 py-1.5 rounded transition-all flex items-center gap-1"
                    >
                      <Plus className="w-4 h-4" />
                      إضافة
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* واجهة الإعدادات المتقدمة */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <h1 className="text-2xl font-black text-white">الإعدادات المتقدمة</h1>
                <p className="text-sm text-gray-400 mt-1">تخصيص مسارات اللعبة والمظهر الهيكلي للانشر.</p>
              </div>

              <div className="max-w-xl bg-[#141414] p-5 rounded-lg border border-[#222222] space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold uppercase tracking-wider text-[#00FF66]">مسار تحميل وحفظ ملفات ماينكرافت الحالية:</span>
                </div>
                <div className="flex items-center gap-3 bg-[#0C0C0C] p-3 rounded border border-[#222222] font-mono text-xs text-gray-400 overflow-x-auto whitespace-nowrap">
                  <Folder className="w-4 h-4 text-gray-500 shrink-0" />
                  <span>{gameDirectory}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 3. منطقة الإطلاق السفلية الثابتة (Launch Control Bar) */}
        <div className="w-full border-t border-[#1A1A1A] pt-6 mt-4 flex flex-col items-center space-y-4">
          
          {/* نصوص الحالة والنسب المئوية */}
          <div className="w-full max-w-xl flex justify-between items-center text-xs px-1">
            <span className={`font-bold transition-colors ${statusText.includes('نجاح') || statusText.includes('جاهز') ? 'text-[#00FF66]' : 'text-gray-400'}`}>
              {statusText}
            </span>
            <span className="font-mono font-bold text-white bg-[#141414] px-2 py-0.5 rounded border border-[#222222]">
              {progress}%
            </span>
          </div>

          {/* شريط تقدم اللانشر المشع باللون الزمردي الحاد */}
          <div className="w-full max-w-xl h-2 bg-[#141414] rounded-full border border-[#222222] overflow-hidden">
            <div 
              className="h-full bg-[#00FF66] shadow-[0_0_10px_#00FF66] transition-all duration-300 ease-out rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* زر PLAY الأسطوري المخصص للألعاب */}
          <button
            onClick={handleLaunch}
            disabled={isLaunching}
            className={`w-full max-w-sm h-14 rounded-md font-black text-lg uppercase tracking-wide transition-all transform hover:scale-[1.01] active:scale-[0.99] flex items-center justify-center gap-2 shadow-2xl ${
              isLaunching 
                ? 'bg-[#141414] text-gray-600 border border-[#222222] cursor-not-allowed' 
                : 'bg-[#00C853] text-black hover:bg-[#009624] hover:shadow-[0_0_20px_rgba(0,200,83,0.4)]'
            }`}
          >
            <Play className={`w-5 open-sans h-5 ${isLaunching ? 'text-gray-600' : 'fill-black'}`} />
            {isLaunching ? 'جاري الإطلاق والتحميل...' : 'تشغيل اللعبة (PLAY)'}
          </button>
        </div>

      </div>
    </div>
  );
}

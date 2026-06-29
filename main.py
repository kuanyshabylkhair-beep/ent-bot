import logging
import json
import random
import asyncio
from pathlib import Path
from datetime import time as dtime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import pytz

TOKEN = "8922456276:AAHX1nCkvDEv6K7jeo5OJezrwdGSh_qt-Ao"
ALMATY_TZ = pytz.timezone("Asia/Almaty")
DATA_FILE = Path("users.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

QUESTIONS = {
    "История Казахстана": [
        {"q": "Когда провозглашена независимость Казахстана?", "opts": ["A) 16 декабря 1991", "B) 25 октября 1990", "C) 1 декабря 1991", "D) 21 декабря 1991"], "ans": "A", "exp": "16 декабря 1991 года — День Независимости РК."},
        {"q": "Казахское ханство основано в:", "opts": ["A) 1465 г.", "B) 1480 г.", "C) 1500 г.", "D) 1456 г."], "ans": "A", "exp": "Казахское ханство основано в 1465 году ханами Жанибеком и Кереем."},
        {"q": "Конституция РК принята в:", "opts": ["A) 1991 г.", "B) 1993 г.", "C) 1995 г.", "D) 1998 г."], "ans": "C", "exp": "Конституция РК принята на референдуме 30 августа 1995 года."},
        {"q": "Декларация о суверенитете Казахской ССР принята:", "opts": ["A) 16 декабря 1991", "B) 25 октября 1990", "C) 28 января 1993", "D) 30 августа 1995"], "ans": "B", "exp": "25 октября 1990 года — Декларация о государственном суверенитете."},
        {"q": "Абай Кунанбаев жил в:", "opts": ["A) XVII в.", "B) XVIII в.", "C) XIX – нач. XX в.", "D) XX в."], "ans": "C", "exp": "Абай Кунанбаев (1845–1904) — основоположник казахской письменной литературы."},
        {"q": "Первый хан, принявший российское подданство в 1731 г.:", "opts": ["A) Абылай хан", "B) Тәуке хан", "C) Әбілқайыр хан", "D) Кенесары хан"], "ans": "C", "exp": "Хан Младшего жуза Әбілқайыр принял российское подданство в 1731 г."},
        {"q": "Ақтабан шұбырынды — это период:", "opts": ["A) 1680–1690", "B) 1723–1727", "C) 1750–1760", "D) 1800–1810"], "ans": "B", "exp": "1723–1727 гг. — Годы Великого бедствия, нашествие джунгар."},
        {"q": "Великий Шёлковый путь проходил в направлении:", "opts": ["A) Север–Юг", "B) Запад–Восток", "C) Восток–Запад", "D) Север–Восток"], "ans": "C", "exp": "Из Китая (Восток) через Центральную Азию в Европу (Запад)."},
        {"q": "Первый президент Казахстана:", "opts": ["A) Д. Қонаев", "B) К.-Ж. Тоқаев", "C) Н.Ә. Назарбаев", "D) А. Байменов"], "ans": "C", "exp": "Нұрсұлтан Назарбаев — первый Президент РК, избран 1 декабря 1991 г."},
        {"q": "В 2022 году столица переименована обратно в:", "opts": ["A) Алматы", "B) Нур-Султан", "C) Астана", "D) Акмола"], "ans": "C", "exp": "В 2019 — Нур-Султан, в сентябре 2022 — возвращено название Астана."},
    ],
    "Математика": [
        {"q": "Корни уравнения x² - 5x + 6 = 0:", "opts": ["A) x=2; x=3", "B) x=1; x=6", "C) x=-2; x=-3", "D) x=3; x=4"], "ans": "A", "exp": "По теореме Виета: x₁+x₂=5, x₁·x₂=6 → x=2 и x=3."},
        {"q": "2³ × 2⁴ = ?", "opts": ["A) 2⁷", "B) 2¹²", "C) 4⁷", "D) 2⁸"], "ans": "A", "exp": "2³×2⁴ = 2^(3+4) = 2⁷ = 128"},
        {"q": "log₂(32) = ?", "opts": ["A) 4", "B) 5", "C) 6", "D) 3"], "ans": "B", "exp": "log₂(32) = log₂(2⁵) = 5"},
        {"q": "Сумма углов треугольника:", "opts": ["A) 360°", "B) 90°", "C) 270°", "D) 180°"], "ans": "D", "exp": "Сумма внутренних углов любого треугольника = 180°"},
        {"q": "2x - 4 > 0, тогда:", "opts": ["A) x < 2", "B) x > 2", "C) x > -2", "D) x < -2"], "ans": "B", "exp": "2x > 4 → x > 2"},
        {"q": "sin(30°) = ?", "opts": ["A) √3/2", "B) 1/2", "C) √2/2", "D) 1"], "ans": "B", "exp": "sin(30°)=1/2, sin(45°)=√2/2, sin(60°)=√3/2, sin(90°)=1"},
        {"q": "(a + b)² = ?", "opts": ["A) a²+b²", "B) a²+ab+b²", "C) a²+2ab+b²", "D) 2a²+2b²"], "ans": "C", "exp": "(a+b)² = a² + 2ab + b² — формула квадрата суммы"},
        {"q": "90 км/ч за 2,5 часа — расстояние:", "opts": ["A) 200 км", "B) 220 км", "C) 225 км", "D) 180 км"], "ans": "C", "exp": "S = 90 × 2,5 = 225 км"},
        {"q": "Площадь круга r=5 (π≈3,14):", "opts": ["A) 78,5 см²", "B) 31,4 см²", "C) 15,7 см²", "D) 157 см²"], "ans": "A", "exp": "S = π·r² = 3,14 × 25 = 78,5 см²"},
        {"q": "Площадь прямоугольника 7×9 см:", "opts": ["A) 63 см²", "B) 32 см²", "C) 56 см²", "D) 72 см²"], "ans": "A", "exp": "S = 7 × 9 = 63 см²"},
    ],
    "Биология": [
        {"q": "Энергетическая станция клетки:", "opts": ["A) Рибосома", "B) Лизосома", "C) Митохондрия", "D) Ядро"], "ans": "C", "exp": "Митохондрия синтезирует АТФ — источник энергии клетки."},
        {"q": "Фотосинтез происходит в:", "opts": ["A) Митохондриях", "B) Рибосомах", "C) Хлоропластах", "D) Ядре"], "ans": "C", "exp": "Фотосинтез в хлоропластах — там содержится хлорофилл."},
        {"q": "Хромосом в соматических клетках человека:", "opts": ["A) 23", "B) 46", "C) 48", "D) 92"], "ans": "B", "exp": "46 хромосом (23 пары). В половых клетках — 23."},
        {"q": "ДНК состоит из:", "opts": ["A) Аминокислот", "B) Нуклеотидов", "C) Жирных кислот", "D) Глюкозы"], "ans": "B", "exp": "ДНК из нуклеотидов: азотистое основание + дезоксирибоза + фосфат."},
        {"q": "Универсальная донорская группа крови:", "opts": ["A) I (0)", "B) II (A)", "C) III (B)", "D) IV (AB)"], "ans": "A", "exp": "I (0) — нет антигенов А и В. IV (AB) — универсальный реципиент."},
        {"q": "Витамин, синтезируемый под солнцем:", "opts": ["A) A", "B) B", "C) C", "D) D"], "ans": "D", "exp": "Витамин D синтезируется под УФ-лучами. Нужен для усвоения кальция."},
        {"q": "Деление клетки с сохранением хромосом:", "opts": ["A) Мейоз", "B) Митоз", "C) Амитоз", "D) Онтогенез"], "ans": "B", "exp": "Митоз — дочерние клетки с тем же набором хромосом что и материнская."},
        {"q": "Инсулин вырабатывает:", "opts": ["A) Печень", "B) Желудок", "C) Поджелудочная железа", "D) Почки"], "ans": "C", "exp": "Инсулин — β-клетки поджелудочной железы. Недостаток → диабет."},
        {"q": "Дождевые черви относятся к типу:", "opts": ["A) Плоские черви", "B) Круглые черви", "C) Кольчатые черви", "D) Членистоногие"], "ans": "C", "exp": "Дождевые черви — тип Кольчатые черви (Annelida)."},
        {"q": "Удвоение ДНК перед делением клетки:", "opts": ["A) Транскрипция", "B) Трансляция", "C) Репликация", "D) Фотосинтез"], "ans": "C", "exp": "Репликация — удвоение ДНК для передачи наследственной информации."},
    ],
    "Физика": [
        {"q": "Скорость света в вакууме:", "opts": ["A) 300 000 км/с", "B) 30 000 км/с", "C) 3 000 000 км/с", "D) 3 000 км/с"], "ans": "A", "exp": "c ≈ 3×10⁸ м/с = 300 000 км/с"},
        {"q": "Закон инерции (1-й закон Ньютона):", "opts": ["A) F=ma", "B) Тело сохраняет покой без внешних сил", "C) Действие=противодействию", "D) КПД<100%"], "ans": "B", "exp": "Тело сохраняет покой или равномерное движение без внешней силы."},
        {"q": "Единица сопротивления:", "opts": ["A) Ампер", "B) Вольт", "C) Ватт", "D) Ом"], "ans": "D", "exp": "Сопротивление в Омах (Ω). R = U/I"},
        {"q": "Сила тяжести тела 10 кг (g=10):", "opts": ["A) 1 Н", "B) 10 Н", "C) 100 Н", "D) 1000 Н"], "ans": "C", "exp": "F = m × g = 10 × 10 = 100 Н"},
        {"q": "Кинетическая энергия:", "opts": ["A) mgh", "B) mv", "C) mv²/2", "D) ma"], "ans": "C", "exp": "Ek = mv²/2. Потенциальная: Ep = mgh."},
        {"q": "Давление:", "opts": ["A) P=m/V", "B) P=F/S", "C) P=F×S", "D) P=m×g"], "ans": "B", "exp": "P = F/S. Единица — Паскаль (Па)."},
        {"q": "Период маятника зависит от:", "opts": ["A) Массы груза", "B) Длины нити", "C) Амплитуды", "D) Цвета"], "ans": "B", "exp": "T = 2π√(L/g) — зависит от длины нити L."},
        {"q": "КПД:", "opts": ["A) Полезная/затраченная×100%", "B) Затраченная/полезная×100%", "C) Сила×скорость", "D) Сила/площадь"], "ans": "A", "exp": "КПД = (Aпол/Aзатр) × 100%. Всегда < 100%."},
    ],
    "Химия": [
        {"q": "Формула воды:", "opts": ["A) HO", "B) H₂O", "C) H₂O₂", "D) OH₂"], "ans": "B", "exp": "Вода — H₂O. H₂O₂ — перекись водорода."},
        {"q": "pH нейтрального раствора:", "opts": ["A) 0", "B) 7", "C) 14", "D) 1"], "ans": "B", "exp": "pH=7 нейтральная. pH<7 — кислая. pH>7 — щелочная."},
        {"q": "Zn + HCl → выделяется:", "opts": ["A) Кислород", "B) Азот", "C) Хлор", "D) Водород"], "ans": "D", "exp": "Zn + 2HCl → ZnCl₂ + H₂↑. Металл + кислота → соль + водород."},
        {"q": "Моль — это:", "opts": ["A) Масса в граммах", "B) 6,02×10²³ частиц", "C) 22,4 л газа", "D) Молярная масса"], "ans": "B", "exp": "1 моль = 6,02×10²³ частиц (число Авогадро)."},
        {"q": "Валентность O в большинстве соединений:", "opts": ["A) I", "B) III", "C) II", "D) IV"], "ans": "C", "exp": "Кислород имеет валентность II в большинстве соединений."},
        {"q": "Символ и атомная масса Fe:", "opts": ["A) Fe, 56", "B) Fe, 26", "C) Ir, 56", "D) Fi, 52"], "ans": "A", "exp": "Железо — Fe. Ar = 56. Порядковый номер = 26."},
        {"q": "Щелочной металл из списка:", "opts": ["A) Кальций", "B) Магний", "C) Натрий", "D) Алюминий"], "ans": "C", "exp": "Щелочные металлы — I группа: Li, Na, K, Rb, Cs, Fr."},
        {"q": "Тип связи в NaCl:", "opts": ["A) Ковалентная полярная", "B) Ионная", "C) Металлическая", "D) Водородная"], "ans": "B", "exp": "NaCl — ионная связь: Na⁺ и Cl⁻."},
    ],
}

SUBJECTS = list(QUESTIONS.keys())

def load_users():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def get_user(users, uid):
    uid = str(uid)
    if uid not in users:
        users[uid] = {"name": "", "stats": {s: {"correct": 0, "total": 0} for s in SUBJECTS}, "asked": {s: [] for s in SUBJECTS}, "active": True}
    return users[uid]

def pick_question(user, subject):
    pool = QUESTIONS[subject]
    asked = user["asked"].get(subject, [])
    available = [i for i in range(len(pool)) if i not in asked]
    if not available:
        user["asked"][subject] = []
        available = list(range(len(pool)))
    idx = random.choice(available)
    user["asked"][subject].append(idx)
    return idx, pool[idx]

def get_stats_text(user):
    lines = ["📊 *Статистика по ЕНТ:*\n"]
    total_c, total_t = 0, 0
    for s in SUBJECTS:
        st = user["stats"].get(s, {"correct": 0, "total": 0})
        c, t = st["correct"], st["total"]
        total_c += c; total_t += t
        pct = round(c/t*100) if t > 0 else 0
        bar = "🟢" * (pct // 20) + "⬜" * (5 - pct // 20)
        lines.append(f"{bar} *{s}*: {c}/{t} ({pct}%)")
    if total_t > 0:
        overall = round(total_c/total_t*100)
        lines.append(f"\n🏆 *Итого: {total_c}/{total_t} ({overall}%)*")
        lines.append("🔥 Отлично!" if overall >= 80 else "💪 Хорошо!" if overall >= 60 else "📚 Нужно больше практики!")
    else:
        lines.append("\nНачни с /question 🚀")
    return "\n".join(lines)

async def send_question(bot, chat_id, subject=None):
    users = load_users()
    user = get_user(users, chat_id)
    if not user.get("active", True):
        return
    if subject is None:
        subject = random.choice(SUBJECTS)
    idx, q = pick_question(user, subject)
    save_users(users)
    text = f"📚 *{subject}*\n\n❓ {q['q']}\n\n" + "\n".join(q["opts"])
    keyboard = [[
        InlineKeyboardButton("A", callback_data=f"ans|{chat_id}|{subject}|{idx}|A"),
        InlineKeyboardButton("B", callback_data=f"ans|{chat_id}|{subject}|{idx}|B"),
        InlineKeyboardButton("C", callback_data=f"ans|{chat_id}|{subject}|{idx}|C"),
        InlineKeyboardButton("D", callback_data=f"ans|{chat_id}|{subject}|{idx}|D"),
    ]]
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name or "Ученик"
    users = load_users()
    user = get_user(users, uid)
    user["name"] = name
    user["active"] = True
    save_users(users)
    await update.message.reply_text(
        f"👋 Привет, *{name}*!\n\n🎯 Репетитор для *ЕНТ 2026-2027*\n\n"
        f"📅 Вопросы 3 раза в день:\n☀️ 08:00 · 🌤 13:00 · 🌙 19:00\n\n"
        f"📚 История КЗ, Математика, Биология, Физика, Химия\n\n"
        f"/question — вопрос сейчас\n/stats — статистика\n/stop — остановить\n\nПоехали! 🚀",
        parse_mode="Markdown"
    )
    await send_question(context.bot, uid)

async def question_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_question(context.bot, update.effective_user.id)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    user = get_user(users, update.effective_user.id)
    await update.message.reply_text(get_stats_text(user), parse_mode="Markdown")

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    uid = str(update.effective_user.id)
    if uid in users:
        users[uid]["active"] = False
        save_users(users)
    await update.message.reply_text("⏹ Остановлено. Напиши /start чтобы возобновить.")

async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("|")
    if parts[0] != "ans" or len(parts) < 5:
        return
    _, chat_id, subject, idx, chosen = parts
    idx = int(idx); chat_id = int(chat_id)
    q = QUESTIONS[subject][idx]
    is_correct = chosen == q["ans"]
    users = load_users()
    user = get_user(users, chat_id)
    st = user["stats"].setdefault(subject, {"correct": 0, "total": 0})
    st["total"] += 1
    if is_correct:
        st["correct"] += 1
    save_users(users)
    result = f"✅ *Правильно!* Молодец, {user['name']}!\n\n" if is_correct else f"❌ *Неверно.* Ты: {chosen}, правильно: *{q['ans']}*\n\n"
    result += f"💡 {q['exp']}\n\n📊 {subject}: {st['correct']}/{st['total']}"
    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(chat_id=chat_id, text=result, parse_mode="Markdown")

async def broadcast(context: ContextTypes.DEFAULT_TYPE):
    users = load_users()
    for uid, user in users.items():
        if user.get("active", True):
            try:
                await send_question(context.bot, int(uid))
                await asyncio.sleep(0.3)
            except Exception as e:
                logger.warning(f"Ошибка {uid}: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("question", question_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(answer_callback))
    app.job_queue.run_daily(broadcast, time=dtime(8, 0, tzinfo=ALMATY_TZ))
    app.job_queue.run_daily(broadcast, time=dtime(13, 0, tzinfo=ALMATY_TZ))
    app.job_queue.run_daily(broadcast, time=dtime(19, 0, tzinfo=ALMATY_TZ))
    logger.info("Бот запущен!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

import logging
import json
import random
import asyncio
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, ContextTypes
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

TOKEN = "8922456276:AAHX1nCkvDEv6K7jeo5OJezrwdGSh_qt-Ao"
ALMATY_TZ = pytz.timezone("Asia/Almaty")
DATA_FILE = Path("users.json")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════
# ВОПРОСЫ ЕНТ 2026-2027
# ══════════════════════════════════════════════
QUESTIONS = {
    "История Казахстана": [
        {"q": "Когда была провозглашена независимость Республики Казахстан?",
         "opts": ["A) 16 декабря 1991", "B) 25 октября 1990", "C) 1 декабря 1991", "D) 21 декабря 1991"],
         "ans": "A", "exp": "16 декабря 1991 года — День Независимости РК. Верховный Совет принял Конституционный закон о государственной независимости."},
        {"q": "Казахское ханство было основано в:",
         "opts": ["A) 1465 г.", "B) 1480 г.", "C) 1500 г.", "D) 1456 г."],
         "ans": "A", "exp": "Казахское ханство основано в 1465 году ханами Жанибеком и Кереем в долине реки Чу, отколовшись от Узбекского ханства."},
        {"q": "Конституция Республики Казахстан принята в:",
         "opts": ["A) 1991 г.", "B) 1993 г.", "C) 1995 г.", "D) 1998 г."],
         "ans": "C", "exp": "Действующая Конституция РК принята на референдуме 30 августа 1995 года."},
        {"q": "Декларация о государственном суверенитете Казахской ССР была принята:",
         "opts": ["A) 16 декабря 1991 г.", "B) 25 октября 1990 г.", "C) 28 января 1993 г.", "D) 30 августа 1995 г."],
         "ans": "B", "exp": "25 октября 1990 года Верховный Совет Казахской ССР принял Декларацию о государственном суверенитете — первый шаг к независимости."},
        {"q": "Абай Кунанбаев жил в:",
         "opts": ["A) XVII в.", "B) XVIII в.", "C) XIX – нач. XX в.", "D) XX в."],
         "ans": "C", "exp": "Абай Кунанбаев (1845–1904) — казахский поэт, просветитель, основоположник казахской письменной литературы."},
        {"q": "Хан Младшего жуза, первым принявший российское подданство в 1731 году:",
         "opts": ["A) Абылай хан", "B) Тәуке хан", "C) Әбілқайыр хан", "D) Кенесары хан"],
         "ans": "C", "exp": "Хан Младшего жуза Әбілқайыр принял российское подданство в 1731 году, стремясь получить защиту от джунгарских нашествий."},
        {"q": "«Годы Великого бедствия» (Ақтабан шұбырынды) — это период:",
         "opts": ["A) 1680–1690 гг.", "B) 1723–1727 гг.", "C) 1750–1760 гг.", "D) 1800–1810 гг."],
         "ans": "B", "exp": "1723–1727 гг. — массовое бегство казахов от джунгарского нашествия. Огромные потери населения, скота, разрушение аулов."},
        {"q": "Великий Шёлковый путь проходил через Казахстан в направлении:",
         "opts": ["A) Север — Юг", "B) Запад — Восток", "C) Восток — Запад", "D) Север — Восток"],
         "ans": "C", "exp": "Великий Шёлковый путь шёл из Китая (Восток) через Центральную Азию в Европу и Средиземноморье (Запад)."},
        {"q": "Первый президент Казахстана:",
         "opts": ["A) Д. Қонаев", "B) К.-Ж. Тоқаев", "C) Н.Ә. Назарбаев", "D) А. Байменов"],
         "ans": "C", "exp": "Нұрсұлтан Назарбаев — первый Президент РК, избран 1 декабря 1991 года, занимал пост до 2019 года."},
        {"q": "Столица Казахстана в 2022 году переименована обратно в:",
         "opts": ["A) Алматы", "B) Нур-Султан", "C) Астана", "D) Акмола"],
         "ans": "C", "exp": "В 2019 году Астана переименована в Нур-Султан, а в сентябре 2022 года — возвращено историческое название Астана."},
    ],
    "Математика": [
        {"q": "Найдите корни уравнения: x² - 5x + 6 = 0",
         "opts": ["A) x=2; x=3", "B) x=1; x=6", "C) x=-2; x=-3", "D) x=3; x=4"],
         "ans": "A", "exp": "По теореме Виета: x₁+x₂=5, x₁·x₂=6 → x=2 и x=3. Проверка: 4-10+6=0 ✓"},
        {"q": "Чему равно: 2³ × 2⁴?",
         "opts": ["A) 2⁷", "B) 2¹²", "C) 4⁷", "D) 2⁸"],
         "ans": "A", "exp": "При умножении степеней с одинаковым основанием показатели складываются: 2³×2⁴ = 2^(3+4) = 2⁷ = 128"},
        {"q": "Найдите значение: log₂(32)",
         "opts": ["A) 4", "B) 5", "C) 6", "D) 3"],
         "ans": "B", "exp": "log₂(32) = log₂(2⁵) = 5. Проверка: 2⁵ = 32 ✓"},
        {"q": "Чему равна сумма углов треугольника?",
         "opts": ["A) 360°", "B) 90°", "C) 270°", "D) 180°"],
         "ans": "D", "exp": "Сумма внутренних углов любого треугольника = 180°. Одна из фундаментальных теорем геометрии."},
        {"q": "Решите неравенство: 2x - 4 > 0",
         "opts": ["A) x < 2", "B) x > 2", "C) x > -2", "D) x < -2"],
         "ans": "B", "exp": "2x > 4 → x > 2. При делении на положительное число знак неравенства не меняется."},
        {"q": "Чему равен sin(30°)?",
         "opts": ["A) √3/2", "B) 1/2", "C) √2/2", "D) 1"],
         "ans": "B", "exp": "sin(30°)=1/2. Запомни: sin(30°)=1/2, sin(45°)=√2/2, sin(60°)=√3/2, sin(90°)=1"},
        {"q": "Упростите: (a + b)²",
         "opts": ["A) a² + b²", "B) a² + ab + b²", "C) a² + 2ab + b²", "D) 2a² + 2b²"],
         "ans": "C", "exp": "(a+b)² = a² + 2ab + b². Формула квадрата суммы — обязательно выучи!"},
        {"q": "Скорость поезда 90 км/ч. За 2,5 часа он проедет:",
         "opts": ["A) 200 км", "B) 220 км", "C) 225 км", "D) 180 км"],
         "ans": "C", "exp": "S = v × t = 90 × 2,5 = 225 км"},
        {"q": "Площадь круга с радиусом 5 см (π≈3,14):",
         "opts": ["A) 78,5 см²", "B) 31,4 см²", "C) 15,7 см²", "D) 157 см²"],
         "ans": "A", "exp": "S = π·r² = 3,14 × 25 = 78,5 см²"},
        {"q": "Найдите площадь прямоугольника со сторонами 7 и 9 см:",
         "opts": ["A) 63 см²", "B) 32 см²", "C) 56 см²", "D) 72 см²"],
         "ans": "A", "exp": "S = a × b = 7 × 9 = 63 см²"},
    ],
    "Биология": [
        {"q": "Какой органоид клетки называют 'энергетической станцией'?",
         "opts": ["A) Рибосома", "B) Лизосома", "C) Митохондрия", "D) Ядро"],
         "ans": "C", "exp": "Митохондрия — органоид, где происходит клеточное дыхание и синтез АТФ — основного источника энергии клетки."},
        {"q": "Фотосинтез происходит в:",
         "opts": ["A) Митохондриях", "B) Рибосомах", "C) Хлоропластах", "D) Ядре"],
         "ans": "C", "exp": "Фотосинтез происходит в хлоропластах. В них содержится хлорофилл — зелёный пигмент, поглощающий свет."},
        {"q": "Сколько хромосом в соматических клетках человека?",
         "opts": ["A) 23", "B) 46", "C) 48", "D) 92"],
         "ans": "B", "exp": "В соматических клетках — 46 хромосом (23 пары). В половых клетках — 23 хромосомы."},
        {"q": "Молекула ДНК состоит из:",
         "opts": ["A) Аминокислот", "B) Нуклеотидов", "C) Жирных кислот", "D) Глюкозы"],
         "ans": "B", "exp": "ДНК состоит из нуклеотидов. Каждый нуклеотид = азотистое основание + дезоксирибоза + фосфат."},
        {"q": "Кровь какой группы является универсальной донорской?",
         "opts": ["A) I (0)", "B) II (A)", "C) III (B)", "D) IV (AB)"],
         "ans": "A", "exp": "I (0) группа — универсальная донорская (нет антигенов А и В). IV (AB) — универсальный реципиент."},
        {"q": "Какой витамин синтезируется в коже под действием солнечного света?",
         "opts": ["A) Витамин А", "B) Витамин В", "C) Витамин С", "D) Витамин D"],
         "ans": "D", "exp": "Витамин D (кальциферол) синтезируется под УФ-лучами. Необходим для усвоения кальция и роста костей."},
        {"q": "Как называется непрямое деление клетки с сохранением набора хромосом?",
         "opts": ["A) Мейоз", "B) Митоз", "C) Амитоз", "D) Онтогенез"],
         "ans": "B", "exp": "Митоз — деление, при котором дочерние клетки получают такой же набор хромосом, как у материнской (46 у человека)."},
        {"q": "Какой орган вырабатывает инсулин?",
         "opts": ["A) Печень", "B) Желудок", "C) Поджелудочная железа", "D) Почки"],
         "ans": "C", "exp": "Инсулин вырабатывают β-клетки островков Лангерганса поджелудочной железы. Недостаток → сахарный диабет."},
        {"q": "К какому типу относятся дождевые черви?",
         "opts": ["A) Плоские черви", "B) Круглые черви", "C) Кольчатые черви", "D) Членистоногие"],
         "ans": "C", "exp": "Дождевые черви — тип Кольчатые черви (Annelida). Тело состоит из сегментов-колец. Обитают в почве."},
        {"q": "Какой процесс обеспечивает передачу наследственной информации при делении?",
         "opts": ["A) Транскрипция", "B) Трансляция", "C) Репликация", "D) Фотосинтез"],
         "ans": "C", "exp": "Репликация — удвоение ДНК перед делением. Обеспечивает точную передачу генетической информации дочерним клеткам."},
    ],
    "Физика": [
        {"q": "Скорость света в вакууме:",
         "opts": ["A) 300 000 км/с", "B) 30 000 км/с", "C) 3 000 000 км/с", "D) 3 000 км/с"],
         "ans": "A", "exp": "Скорость света c ≈ 3×10⁸ м/с = 300 000 км/с. Максимальная скорость во Вселенной."},
        {"q": "Первый закон Ньютона (закон инерции) утверждает:",
         "opts": ["A) F = ma", "B) Тело сохраняет покой/равномерное движение без внешних сил",
                  "C) Действие = противодействию", "D) КПД < 100%"],
         "ans": "B", "exp": "Первый закон Ньютона: тело сохраняет состояние покоя или равномерного прямолинейного движения, пока не действует внешняя сила."},
        {"q": "Единица измерения электрического сопротивления:",
         "opts": ["A) Ампер", "B) Вольт", "C) Ватт", "D) Ом"],
         "ans": "D", "exp": "Сопротивление измеряется в Омах (Ω). Закон Ома: R = U/I."},
        {"q": "Чему равна сила тяжести тела массой 10 кг? (g = 10 м/с²)",
         "opts": ["A) 1 Н", "B) 10 Н", "C) 100 Н", "D) 1000 Н"],
         "ans": "C", "exp": "F = m × g = 10 × 10 = 100 Н"},
        {"q": "Формула кинетической энергии:",
         "opts": ["A) Ek = mgh", "B) Ek = mv", "C) Ek = mv²/2", "D) Ek = ma"],
         "ans": "C", "exp": "Кинетическая энергия Ek = mv²/2. Потенциальная: Ep = mgh."},
        {"q": "Давление вычисляется по формуле:",
         "opts": ["A) P = m/V", "B) P = F/S", "C) P = F×S", "D) P = m×g"],
         "ans": "B", "exp": "Давление P = F/S (сила / площадь). Единица — Паскаль (Па)."},
        {"q": "Период колебаний маятника зависит от:",
         "opts": ["A) Массы груза", "B) Длины нити", "C) Амплитуды", "D) Цвета груза"],
         "ans": "B", "exp": "T = 2π√(L/g) — зависит только от длины нити L и ускорения g."},
        {"q": "КПД — это:",
         "opts": ["A) Полезная работа / затраченная × 100%", "B) Затраченная / полезная × 100%",
                  "C) Сила × скорость", "D) Сила / площадь"],
         "ans": "A", "exp": "КПД = (Aпол / Aзатр) × 100%. Всегда меньше 100% из-за потерь на трение."},
    ],
    "Химия": [
        {"q": "Формула воды:",
         "opts": ["A) HO", "B) H₂O", "C) H₂O₂", "D) OH₂"],
         "ans": "B", "exp": "Вода — H₂O. H₂O₂ — перекись водорода (другое вещество!)."},
        {"q": "pH нейтрального раствора при 25°C:",
         "opts": ["A) 0", "B) 7", "C) 14", "D) 1"],
         "ans": "B", "exp": "pH=7 — нейтральная среда. pH<7 — кислая. pH>7 — щелочная."},
        {"q": "Какой газ выделяется при реакции Zn + HCl?",
         "opts": ["A) Кислород", "B) Азот", "C) Хлор", "D) Водород"],
         "ans": "D", "exp": "Zn + 2HCl → ZnCl₂ + H₂↑. Металл + кислота → соль + водород."},
        {"q": "Что такое моль?",
         "opts": ["A) Масса в граммах", "B) 6,02×10²³ частиц", "C) Объём газа 22,4 л", "D) Молярная масса"],
         "ans": "B", "exp": "1 моль = 6,02×10²³ частиц (число Авогадро). При н.у. 1 моль газа занимает 22,4 л."},
        {"q": "Валентность кислорода в большинстве соединений:",
         "opts": ["A) I", "B) III", "C) II", "D) IV"],
         "ans": "C", "exp": "Кислород в большинстве соединений имеет валентность II (и степень окисления -2)."},
        {"q": "Символ и атомная масса железа:",
         "opts": ["A) Fe, 56", "B) Fe, 26", "C) Ir, 56", "D) Fi, 52"],
         "ans": "A", "exp": "Железо — Fe (Ferrum). Ar = 56. Порядковый номер = 26."},
        {"q": "К щелочным металлам относится:",
         "opts": ["A) Кальций", "B) Магний", "C) Натрий", "D) Алюминий"],
         "ans": "C", "exp": "Щелочные металлы — I группа: Li, Na, K, Rb, Cs, Fr. Бурно реагируют с водой."},
        {"q": "Тип химической связи в молекуле NaCl:",
         "opts": ["A) Ковалентная полярная", "B) Ионная", "C) Металлическая", "D) Водородная"],
         "ans": "B", "exp": "NaCl — ионная связь: Na⁺ и Cl⁻. Ионная связь — между металлом и неметаллом."},
    ],
    "Грамотность чтения": [
        {"q": "Главная мысль текста — это:",
         "opts": ["A) Первое предложение", "B) Основная идея автора", "C) Последний абзац", "D) Заголовок"],
         "ans": "B", "exp": "Главная мысль — то, что автор хочет донести. Может быть явной или скрытой. Часто формулируется как вывод."},
        {"q": "Какой стиль речи используется в научных статьях?",
         "opts": ["A) Разговорный", "B) Художественный", "C) Научный", "D) Публицистический"],
         "ans": "C", "exp": "Научный стиль: точность, логичность, объективность, термины. Примеры: учебники, статьи, диссертации."},
        {"q": "Аргумент в тексте-рассуждении — это:",
         "opts": ["A) Вступление к теме", "B) Доказательство тезиса", "C) Описание природы", "D) Перечисление фактов"],
         "ans": "B", "exp": "Структура рассуждения: тезис → аргументы (доказательства) → вывод."},
        {"q": "Текст описательного типа отвечает на вопрос:",
         "opts": ["A) Почему?", "B) Что произошло?", "C) Каков предмет?", "D) Что делать?"],
         "ans": "C", "exp": "Описание отвечает на вопрос 'каков предмет?'. Рассуждение — 'почему?'. Повествование — 'что произошло?'."},
    ],
}

SUBJECTS = list(QUESTIONS.keys())

# ══════════════════════════════════════════════
# РАБОТА С ДАННЫМИ
# ══════════════════════════════════════════════
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
        users[uid] = {
            "name": "",
            "stats": {s: {"correct": 0, "total": 0} for s in SUBJECTS},
            "asked": {s: [] for s in SUBJECTS},
            "active": True
        }
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
    lines = ["📊 *Твоя статистика по ЕНТ:*\n"]
    total_c, total_t = 0, 0
    for s in SUBJECTS:
        st = user["stats"].get(s, {"correct": 0, "total": 0})
        c, t = st["correct"], st["total"]
        total_c += c
        total_t += t
        pct = round(c/t*100) if t > 0 else 0
        bar = "🟢" * (pct // 20) + "⬜" * (5 - pct // 20)
        lines.append(f"{bar} *{s}*: {c}/{t} ({pct}%)")
    if total_t > 0:
        overall = round(total_c/total_t*100)
        lines.append(f"\n🏆 *Итого: {total_c}/{total_t} ({overall}%)*")
        if overall >= 80:
            lines.append("🔥 Отличная подготовка! Так держать!")
        elif overall >= 60:
            lines.append("💪 Хороший прогресс! Продолжай!")
        else:
            lines.append("📚 Нужно больше практики! Не сдавайся!")
    else:
        lines.append("\nЕщё нет ответов. Начни с /question 🚀")
    return "\n".join(lines)

# ══════════════════════════════════════════════
# ОТПРАВКА ВОПРОСА
# ══════════════════════════════════════════════
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
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ══════════════════════════════════════════════
# ХЭНДЛЕРЫ
# ══════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    name = update.effective_user.first_name or "Ученик"
    users = load_users()
    user = get_user(users, uid)
    user["name"] = name
    user["active"] = True
    save_users(users)

    text = (
        f"👋 Привет, *{name}*!\n\n"
        f"🎯 Я твой репетитор для подготовки к *ЕНТ 2026-2027*!\n\n"
        f"📅 Каждый день получай вопросы *3 раза*:\n"
        f"☀️ 08:00 — утро\n"
        f"🌤 13:00 — день\n"
        f"🌙 19:00 — вечер\n\n"
        f"📚 *Предметы:*\n"
        f"• История Казахстана\n"
        f"• Математика\n"
        f"• Биология\n"
        f"• Физика\n"
        f"• Химия\n"
        f"• Грамотность чтения\n\n"
        f"📌 *Команды:*\n"
        f"/question — вопрос прямо сейчас\n"
        f"/stats — моя статистика\n"
        f"/stop — остановить рассылку\n\n"
        f"Поехали! 🚀 Вот твой первый вопрос:"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
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
    await update.message.reply_text("⏹ Рассылка остановлена. Напиши /start чтобы возобновить.")

async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    parts = query.data.split("|")
    if parts[0] != "ans" or len(parts) < 5:
        return
    _, chat_id, subject, idx, chosen = parts
    idx = int(idx)
    chat_id = int(chat_id)

    q = QUESTIONS[subject][idx]
    is_correct = chosen == q["ans"]

    users = load_users()
    user = get_user(users, chat_id)
    st = user["stats"].setdefault(subject, {"correct": 0, "total": 0})
    st["total"] += 1
    if is_correct:
        st["correct"] += 1
    save_users(users)

    if is_correct:
        result = f"✅ *Правильно!* Молодец, {user['name']}!\n\n"
    else:
        result = f"❌ *Неверно.* Ты выбрал: {chosen}\nПравильный ответ: *{q['ans']}*\n\n"

    result += f"💡 *Объяснение:*\n{q['exp']}\n\n"
    result += f"📊 {subject}: {st['correct']}/{st['total']} правильных"

    await query.edit_message_reply_markup(reply_markup=None)
    await context.bot.send_message(chat_id=chat_id, text=result, parse_mode="Markdown")

# ══════════════════════════════════════════════
# РАССЫЛКА
# ══════════════════════════════════════════════
async def broadcast(bot):
    users = load_users()
    for uid, user in users.items():
        if user.get("active", True):
            try:
                await send_question(bot, int(uid))
                await asyncio.sleep(0.3)
            except Exception as e:
                logger.warning(f"Ошибка для {uid}: {e}")

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("question", question_cmd))
    app.add_handler(CommandHandler("stats", stats_cmd))
    app.add_handler(CommandHandler("stop", stop_cmd))
    app.add_handler(CallbackQueryHandler(answer_callback))

    scheduler = AsyncIOScheduler(timezone=ALMATY_TZ)
    scheduler.add_job(lambda: asyncio.ensure_future(broadcast(app.bot)),
                      CronTrigger(hour=8,  minute=0, timezone=ALMATY_TZ))
    scheduler.add_job(lambda: asyncio.ensure_future(broadcast(app.bot)),
                      CronTrigger(hour=13, minute=0, timezone=ALMATY_TZ))
    scheduler.add_job(lambda: asyncio.ensure_future(broadcast(app.bot)),
                      CronTrigger(hour=19, minute=0, timezone=ALMATY_TZ))

    async def on_startup(app):
        scheduler.start()
        logger.info("✅ Scheduler запущен")

    app.post_init = on_startup
    logger.info("🤖 ЕНТ-бот запускается...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

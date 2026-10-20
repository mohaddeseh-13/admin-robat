import os
import re

from dotenv import load_dotenv
from openai import AsyncOpenAI

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

import config

from rag import collection, embedding_model


load_dotenv()


# =========================
# تنظیمات
# =========================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

ADMIN_CHAT_ID = 1390883226


# =========================
# OpenRouter
# =========================

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# =========================
# مراحل فرم درخواست
# =========================

NAME, PHONE = range(2)


# =========================
# نرمال‌سازی متن
# =========================

def normalize_text(text):

    text = text.lower()

    text = text.replace("ي", "ی")
    text = text.replace("ى", "ی")
    text = text.replace("ك", "ک")

    text = text.replace("‌", " ")

    text = re.sub(
        r"[؟?!،,.:؛]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================
# Start
# =========================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "سلام 👋\n"
        "من Assistly هستم، دستیار هوشمند شما.\n"
        "سؤالتون رو بپرسید.\n\n"
        "برای ثبت درخواست می‌توانید /request را بزنید."
    )


# =========================
# Chat ID
# =========================

async def get_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        f"Chat ID شما:\n{update.effective_chat.id}"
    )


# =========================
# شروع درخواست
# =========================

async def start_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    await update.message.reply_text(
        "حتماً 🌷\n"
        "لطفاً نام و نام خانوادگی‌تون رو وارد کنید:"
    )

    return NAME


# =========================
# دریافت نام
# =========================

async def get_name(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    name = update.message.text.strip()

    if not name:

        await update.message.reply_text(
            "❌ لطفاً نام و نام خانوادگی‌تون رو وارد کنید:"
        )

        return NAME

    context.user_data["name"] = name

    await update.message.reply_text(
        "ممنون 🌷\n"
        "حالا شماره موبایل‌تون رو وارد کنید:"
    )

    return PHONE


# =========================
# دریافت شماره
# =========================

async def get_phone(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    phone = update.message.text.strip()

    if not phone.isdigit():

        await update.message.reply_text(
            "❌ شماره تماس معتبر نیست.\n"
            "لطفاً فقط اعداد شماره موبایل خود را وارد کنید:"
        )

        return PHONE

    if len(phone) != 11 or not phone.startswith("09"):

        await update.message.reply_text(
            "❌ شماره موبایل معتبر نیست.\n"
            "لطفاً شماره موبایل 11 رقمی خود را وارد کنید.\n\n"
            "مثال: 09123456789"
        )

        return PHONE

    name = context.user_data["name"]

    # =========================
    # ذخیره درخواست
    # =========================

    with open(
        "requests.txt",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"نام: {name} | شماره: {phone}\n"
        )

    # =========================
    # پیام ادمین
    # =========================

    admin_message = (
        "🔔 درخواست جدید در Assistly\n\n"
        f"👤 نام: {name}\n"
        f"📱 شماره تماس: {phone}\n\n"
        "📌 منبع: Telegram"
    )

    try:

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message
        )

        await update.message.reply_text(
            "اطلاعات شما با موفقیت ثبت شد ✅\n"
            "درخواست شما برای مسئول مربوطه ارسال شد."
        )

    except Exception as e:

        print(
            "Admin Notification Error:",
            e
        )

        await update.message.reply_text(
            "اطلاعات شما ثبت شد ✅\n"
            "اطلاعات ثبت شد اما در ارسال برای مسئول مشکلی پیش آمد."
        )

    return ConversationHandler.END


# =========================
# AI + RAG
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_message = update.message.text.strip()

    try:

        # =========================
        # نرمال‌سازی سؤال
        # =========================

        normalized_question = normalize_text(
            user_message
        )

        # =========================
        # Embedding
        # =========================

        question_embedding = (
            embedding_model
            .encode([user_message])
            .tolist()
        )

        # =========================
        # جستجوی Semantic
        # =========================

        results = collection.query(
            query_embeddings=question_embedding,
            n_results=6,
            include=[
                "documents",
                "distances"
            ]
        )

        documents = results["documents"][0]
        distances = results["distances"][0]

        # =========================
        # Keyword Matching
        # =========================

        keyword_matches = []

        question_words = set(
            normalized_question.split()
        )

        for document in documents:

            normalized_document = normalize_text(
                document
            )

            document_words = set(
                normalized_document.split()
            )

            common_words = (
                question_words
                & document_words
            )

            # کلمات خیلی عمومی را حذف می‌کنیم

            common_words = {
                word
                for word in common_words
                if len(word) >= 3
            }

            if common_words:

                keyword_matches.append(
                    document
                )

        # =========================
        # تشخیص موضوعات مهم
        # =========================

        topic_keywords = {

            "دوره": [
                "دوره",
                "دوره ها",
                "دورههای",
                "آموزشی",
                "برگزار"
            ],

            "security": [
                "security",
                "security+"
            ],

            "network": [
                "network",
                "network+"
            ],

            "ceh": [
                "ceh"
            ],

            "ثبت نام": [
                "ثبت",
                "نام",
                "ثبت نام"
            ],

            "مشاوره": [
                "مشاوره"
            ],

            "ساعت": [
                "ساعت",
                "پاسخگویی",
                "پاسخ"
            ]
        }


        matched_topics = []

        for topic, keywords in topic_keywords.items():

            if any(
                keyword in normalized_question
                for keyword in keywords
            ):

                matched_topics.append(topic)


        # =========================
        # اضافه کردن نتایج مرتبط
        # =========================

        selected_documents = []

        for document in keyword_matches:

            if document not in selected_documents:

                selected_documents.append(
                    document
                )


        for document in documents:

            if document not in selected_documents:

                selected_documents.append(
                    document
                )


        # =========================
        # اگر سؤال درباره دوره‌هاست
        # =========================

        if "دوره" in matched_topics:

            for document in documents:

                normalized_document = normalize_text(
                    document
                )

                if (
                    "network+" in normalized_document
                    or "security+" in normalized_document
                    or "ceh" in normalized_document
                ):

                    if document not in selected_documents:

                        selected_documents.insert(
                            0,
                            document
                        )

                    else:

                        selected_documents.remove(
                            document
                        )

                        selected_documents.insert(
                            0,
                            document
                        )


        # =========================
        # محدود کردن Context
        # =========================

        selected_documents = (
            selected_documents[:4]
        )


        context_text = "\n\n".join(
            selected_documents
        )


        # =========================
        # نمایش اطلاعات در ترمینال
        # =========================

        print("\n==============================")

        print(
            "Question:",
            user_message
        )

        print(
            "\nSelected Context:"
        )

        print(
            context_text
        )

        print(
            "\nSemantic Distances:"
        )

        for i, distance in enumerate(
            distances
        ):

            print(
                f"Result {i + 1}: {distance}"
            )

        print(
            "==============================\n"
        )


        # =========================
        # Prompt
        # =========================

        prompt = f"""
تو دستیار هوش مصنوعی مجموعه TRAIN هستی.

فقط و فقط بر اساس اطلاعات موجود در بخش
«اطلاعات TRAIN» پاسخ بده.

اگر پاسخ سؤال کاربر در اطلاعات TRAIN وجود ندارد:

- چیزی را حدس نزن.
- اطلاعات ساختگی تولید نکن.
- از دانش عمومی خودت استفاده نکن.
- بگو که اطلاعات کافی در دسترس نیست.

اطلاعات TRAIN:

{context_text}

سؤال کاربر:

{user_message}

پاسخ را کوتاه، طبیعی و مستقیم بده.
"""


        # =========================
        # LLM
        # =========================

        response = await client.chat.completions.create(

            model=config.CURRENT_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        answer = (
            response
            .choices[0]
            .message
            .content
        )


        await update.message.reply_text(
            answer
        )


    except Exception as e:

        print(
            "AI Error:",
            e
        )

        await update.message.reply_text(
            "متأسفم، در حال حاضر مشکلی "
            "در پردازش درخواست پیش آمده."
        )


# =========================
# Main
# =========================

def main():

    app = (
        Application
        .builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )


    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    app.add_handler(
        CommandHandler(
            "id",
            get_id
        )
    )


    request_handler = ConversationHandler(

        entry_points=[
            CommandHandler(
                "request",
                start_request
            )
        ],

        states={

            NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_name
                )
            ],

            PHONE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    get_phone
                )
            ]

        },

        fallbacks=[]
    )


    app.add_handler(
        request_handler
    )


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )


    print(
        "Assistly is running..."
    )


    app.run_polling()


# =========================
# Run
# =========================

if __name__ == "__main__":

    main()
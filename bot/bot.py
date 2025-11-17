import os
import django
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import instaloader
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging
from asgiref.sync import sync_to_async
import re
from openai import OpenAI


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


from bot.models import Profile, StoryPersistance, ChatMessage

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BOT_ID = int(BOT_TOKEN.split(':')[0])


async def save_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    
    if not msg or not msg.from_user:
        return
    
    if msg.from_user.id == BOT_ID:
        return
    
    try:
        photo_url = None
        if msg.photo:
            photo = msg.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            photo_url = file.file_path
        
        await sync_to_async(ChatMessage.objects.update_or_create)(
            chat_id=msg.chat_id,
            message_id=msg.message_id,
            defaults={
                'user_id': msg.from_user.id,
                'username': msg.from_user.first_name,
                'text': msg.text,
                'photo_url': photo_url,
                'caption': msg.caption
            }
        )
    except Exception as e:
        logger.debug(f'Error saving message: {str(e)}')

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        k_messages = int(context.args[0]) if context.args else 10
        k_messages = min(k_messages, 150)
    except (ValueError, IndexError):
        await update.message.reply_text('/summary <n_messages>')
        return
    
    try:
        chat_id = update.effective_chat.id
        
        msgs = await sync_to_async(list)(
            ChatMessage.objects.filter(chat_id=chat_id)
            .order_by('-timestamp')[:k_messages]
        )
        
        if not msgs:
            return
        
        msgs.reverse()
        
        prompt_messages = [{
            "role": "system",
            "content": "Você analisa conversas e faz resumos concisos focados em: assuntos principais, decisões e próximos passos. Seja amigável."
        }]
        
        for msg in msgs:
            content = []
            
            if msg.text:
                content.append({
                    "type": "text",
                    "text": f"[{msg.username}]: {msg.text}"
                })
            
            if msg.photo_url:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": msg.photo_url}
                })
                
                if msg.caption:
                    content.append({
                        "type": "text",
                        "text": f"[Legenda]: {msg.caption}"
                    })
            
            if content:
                prompt_messages.append({"role": "user", "content": content})
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt_messages,
            max_tokens=500,
            temperature=0.7
        )

        summary_text = response.choices[0].message.content
        await update.message.reply_text(
            f"📝 **Resumo de {len(msgs)} mensagens:**\n\n{summary_text}",
        )

    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        await update.message.reply_text(f"❌ Erro: {str(e)}")
        
            

if not os.path.exists('stories'):
    os.makedirs('stories')
if not os.path.exists('downloads'):
    os.makedirs('downloads')

L = instaloader.Instaloader()
INSTA_USER = os.getenv('INSTA_USER')
INSTA_PASS = os.getenv('INSTA_PASS')
VINTECINCO = os.getenv('CHAT_ID')

# try:
#     L.load_session_from_file(INSTA_USER)

# except FileNotFoundError:
#     L.login(INSTA_USER, INSTA_PASS)
#     L.save_session_to_file()



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('DENILSON PROGRAMAÇÕES!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text

    insta_pattern = r"https?://(?:www\.)?instagram\.com/(?:p|reel|tv)/([^/?#&]+)"
    match = re.search(insta_pattern, text)

    if not match:
        return
    shortcode = match.group(1)
    logger.info(f'Received Instagram link with shortcode: {shortcode}')

    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        caption = post.caption or "No caption"
        if len(caption) > 1024:
            caption = caption[:1021] + '...'
        
        safe_shortcode = re.sub(r'[^\w\-_.]', '_', shortcode)
        target = f"downloads/{safe_shortcode}"
        Path(target).mkdir(parents=True, exist_ok=True)
        L.dirname_pattern = target
        L.filename_pattern = "{date_utc}_{shortcode}"
        L.download_post(post, target=target)

        download_dir = Path(target)
        all_files = list(download_dir.glob('*'))

        media_files = sorted([f for f in all_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.mp4']], key=lambda x: x.stat().st_mtime)


        if not media_files:
            return

        if len(media_files) == 1:
            file = media_files[0]


            with open(file, 'rb') as f:
                if file.suffix.lower() == '.mp4':
                    await context.bot.send_video(
                        chat_id=VINTECINCO,
                        video=f,
                        caption=caption
                    )
                else:
                    await context.bot.send_photo(
                        chat_id=VINTECINCO,
                        photo=f,
                        caption=caption
                    )
        else:
            media_group = []
            for i, file in enumerate(media_files[:10]):
                with open(file, 'rb') as f:
                    if file.suffix.lower() == '.mp4':
                        media = InputMediaVideo(
                            media=f.read(),
                            caption=caption if i == 0 else None
                        )
                    else:
                        media = InputMediaPhoto(
                            media=f.read(),
                            caption=caption if i == 0 else None
                        )
                    
                    media_group.append(media)

            await context.bot.send_media_group(chat_id=VINTECINCO, media=media_group)
        
        for file in all_files:
            file.unlink()
        download_dir.rmdir()

    except Exception as e:
        logger.error(f'Error processing Instagram link: {str(e)}')
        await update.message.reply_text(f'Error processing the Instagram link: {str(e)}')

        
                

async def stories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    profiles = await sync_to_async(list)(Profile.objects.filter(active=True))

    logger.info(f"Fetching stories for {len(profiles)} profiles.")

    for profile in profiles:
        try:
            logger.info(f"Processing profile: {profile.username}")
            insta_profile = instaloader.Profile.from_username(L.context, profile.username)
            batch = []

            for story in L.get_stories(userids=[insta_profile.userid]):
                for item in story.get_items():
                    url = item.url

                    exists = await sync_to_async(StoryPersistance.objects.filter(url=url).exists)()
                    if exists:
                        continue

                    target = f'stories/{profile.username}'
                    L.download_storyitem(item, target=target)

                    story_dir = Path(target)
                    story_file = max(story_dir.glob('*'), key=os.path.getctime)

                    if item.is_video:
                        batch.append((InputMediaVideo(open(story_file, 'rb')), url, story_file))
                    else:
                        batch.append((InputMediaPhoto(open(story_file, 'rb')), url, story_file))
                    
                    if len(batch) == 10:
                        await send_batch(context, profile, batch)
                        batch = []
                        await asyncio.sleep(15)
                if batch:
                    await send_batch(context, profile, batch)


        except Exception as e:
            await update.message.reply_text(f'Error processing {profile.username}: {str(e)}')
        

async def send_batch(context, profile, media_batch):
    try:
        media_group = [m[0] for m in media_batch]
        await context.bot.send_media_group(chat_id=VINTECINCO, media=media_group)

        for _, url, file_path in media_batch:
            await sync_to_async(StoryPersistance.objects.create)(url=url, profile=profile)
            os.remove(file_path)
            logger.info(f'Processed and sent story: {url}')
    except Exception as e:
        logger.error(f'Error sending media group: {str(e)}')
        for m in media_batch:
            m[0].media.close()
        raise e
    
    
def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, save_message), group=0)
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stories", stories))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started. Listening for commands...")

    app.run_polling()

if __name__ == '__main__':
    main()
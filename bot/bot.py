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


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


from bot.models import Profile, StoryPersistance

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

    insta_pattern = r'https?://(?:www\.)?instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)'
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

        media_files = [f for f in media_files if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.mp4']]

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
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stories", stories))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Bot started. Listening for commands...")

    app.run_polling()

if __name__ == '__main__':
    main()
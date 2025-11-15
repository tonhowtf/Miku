import os
import django
from telegram import Update, InputMediaPhoto, InputMediaVideo
from telegram.ext import Application, CommandHandler, ContextTypes
import instaloader
import asyncio
from pathlib import Path
from dotenv import load_dotenv
import logging
from asgiref.sync import sync_to_async


load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


from bot.models import Profile, StoryPersistance

L = instaloader.Instaloader()
INSTA_USER = os.getenv('INSTA_USER')
INSTA_PASS = os.getenv('INSTA_PASS')
VINTECINCO = os.getenv('CHAT_ID')

L.login(INSTA_USER, INSTA_PASS)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('DENILSON PROGRAMAÇÕES!')

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
    logger.info("Bot started. Listening for commands...")

    app.run_polling()

if __name__ == '__main__':
    main()
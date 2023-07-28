import asyncio
import os
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeFilename
from datetime import datetime
from pytz import timezone
import telebot
import subprocess

# Telegram API credentials
API_ID = '14717600'
API_HASH = '1c4099bac5e396aecaacf6f98f2bd155'
TOKEN = '5738819751:AAHSTNm_Su6iv4LEM2hqv24ItcRNZ881Li8'
CHANNEL_ID = -1001851397474
chat_id3 = -804108523

# Create the Telegram client
client = TelegramClient('session', API_ID, API_HASH)
bot = telebot.TeleBot(TOKEN)

@client.on(events.NewMessage)
async def handle_message(event):
    """Handler for receiving messages."""
    text = event.message.text

    if text.startswith('http://') or text.startswith('https://'):
        # Extract the URLs from the message
        urls = [url.strip() for url in text.split() if url.startswith('http://') or url.startswith('https://')]
        result = subprocess.run(["curl", "-I", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--header", "Referer:78373fa444d18cf962d99179d6621a64", text], capture_output=True,
                         text=True)
        status_code = result.stdout.strip()
        bot.send_message(chat_id3, f'{urls} Status:{status_code}')
        #await client.send_message(chat_id3, f"{urls} Status: {status_code}")
        if not urls:
            await event.respond('No valid URLs found.')
            return

        tasks = [download_and_send(url, event.chat_id) for url in urls]
        await asyncio.gather(*tasks)

async def download_video(url):
    """Download video using ffmpeg and create a grid of thumbnails."""
    filename = f"{url.split('/')[-1]}.mp4"
    now = datetime.now()
    local_tz = timezone('America/Sao_Paulo')
    local_dt = now.astimezone(local_tz)
    title = os.path.splitext(filename)[0]
    thumbnail_grid = f"{title}.jpg"

    # Download video
    command_download = f"ffmpeg -headers 'Referer: 78373fa444d18cf962d99179d6621a64' -i '{url}' -c:v copy -c:a copy {filename}"
    process_download = await asyncio.create_subprocess_shell(command_download)
    await process_download.wait()

    # Create thumbnail grid
    command_thumbnail_grid = f"ffmpeg -i {filename} -vf 'select=not(mod(n\,16)),scale=320:-1,tile=4x4' -ss 00:00:05 -frames:v 1 {thumbnail_grid}"
    process_thumbnail_grid = await asyncio.create_subprocess_shell(command_thumbnail_grid)
    await process_thumbnail_grid.wait()

    return filename, thumbnail_grid

async def upload_video_with_thumbnail(chat_id, video_path, thumbnail_path):
    """Upload a video file with a thumbnail."""
    video = await client.upload_file(video_path)
    thumbnail = await client.upload_file(thumbnail_path)

    attributes = [
        DocumentAttributeVideo(
            duration=0,  # Set the duration to 0 for streaming support
            w=0,
            h=0,
            supports_streaming=True,
        ),
        DocumentAttributeFilename(os.path.splitext(os.path.basename(video_path))[0]),
    ]

    await client.send_file(
        CHANNEL_ID,
        video,
        thumb=thumbnail,
        attributes=attributes,
        caption=os.path.splitext(os.path.basename(video_path))[0]
    )

async def download_and_send(url, chat_id):
    """Download the video, create a thumbnail grid, and send them as a streaming video with thumbnail."""
    try:
        filename, thumbnail_grid = await download_video(url)
        # await client.send_message(chat_id3, f"Status: {status_code}")

        await upload_video_with_thumbnail(CHANNEL_ID, filename, thumbnail_grid)

        # Remove the downloaded files
        os.remove(filename)
        os.remove(thumbnail_grid)

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        #await client.send_message(chat_id, error_message)

async def main():
    try:
        # Start the Telegram client
        await client.start(bot_token=TOKEN)
        await client.run_until_disconnected()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Disconnect the client when done
        await client.disconnect()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass

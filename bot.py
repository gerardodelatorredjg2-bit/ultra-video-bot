import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import subprocess

# ========== CONFIGURACIÓN ==========
API_ID = 37453798
API_HASH = "2c86c30288e6c77fc4b6c9d4a50b2931"
BOT_TOKEN = "8232286674:AAEs4TmvAUspZi0cT1Y26CkdARUKz0eCNCo"

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directorio temporal
TEMP_DIR = "/tmp/video_bot"
os.makedirs(TEMP_DIR, exist_ok=True)

# Inicializar bot
app = Client("github_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Comando /start"""
    await message.reply_text(
        "🎬 **ULTRA VIDEO COMPRESS BOT** 🚀\n\n"
        "¡Ejecutándose en GitHub Codespaces!\n"
        "✅ Gratis - Sin tarjeta - Sin dólares\n"
        "📹 Envía cualquier video para comprimirlo\n\n"
        "🔧 **Desarrollado en Cuba 🇨🇺**"
    )

@app.on_message(filters.video | filters.document)
async def handle_video(client, message):
    """Manejar videos"""
    input_path = ""
    output_path = ""
    
    try:
        logger.info(f"Video recibido de {message.from_user.id}")
        
        # Verificar si es video
        if message.document and not message.document.mime_type.startswith('video/'):
            await message.reply_text("❌ Envía un archivo de video.")
            return
        
        # Obtener archivo
        if message.video:
            file_obj = message.video
            file_size = file_obj.file_size
        else:
            file_obj = message.document
            file_size = file_obj.file_size
        
        # Verificar tamaño
        if file_size and file_size > 2 * 1024 * 1024 * 1024:
            await message.reply_text("❌ Máximo 2GB permitido")
            return
        
        # Estado
        status_msg = await message.reply_text("📥 **Descargando video...**")
        
        # Rutas
        file_id = message.id
        input_path = os.path.join(TEMP_DIR, f"input_{file_id}.mp4")
        output_path = os.path.join(TEMP_DIR, f"output_{file_id}.mp4")
        
        # DESCARGAR
        await message.download(file_name=input_path)
        
        if not os.path.exists(input_path) or os.path.getsize(input_path) == 0:
            await status_msg.edit_text("❌ Error descargando video")
            return
        
        file_size_mb = os.path.getsize(input_path) / (1024 * 1024)
        logger.info(f"Descargado: {file_size_mb:.1f} MB")
        
        # COMPRIMIR
        await status_msg.edit_text(f"⚙️ **Comprimiendo...**\n{file_size_mb:.1f} MB")
        
        cmd = [
            'ffmpeg', '-i', input_path, '-y',
            '-c:v', 'libx264', '-crf', '28', '-preset', 'fast',
            '-c:a', 'aac', '-b:a', '64k',
            '-movflags', '+faststart',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(output_path):
            original_size = os.path.getsize(input_path)
            compressed_size = os.path.getsize(output_path)
            
            if compressed_size > 0:
                saved_percent = ((original_size - compressed_size) / original_size) * 100
                
                # ENVIAR
                await status_msg.edit_text("📤 **Enviando video...**")
                
                caption = (
                    f"✅ **Video comprimido!**\n\n"
                    f"• **Original:** {original_size / (1024*1024):.1f} MB\n"
                    f"• **Comprimido:** {compressed_size / (1024*1024):.1f} MB\n"
                    f"• **Ahorro:** {saved_percent:.1f}%\n"
                    f"🇨🇺 **Desde GitHub Cuba**"
                )
                
                await message.reply_video(
                    video=output_path,
                    caption=caption,
                    supports_streaming=True
                )
                
                await status_msg.delete()
                logger.info("✅ Video procesado exitosamente")
            else:
                await status_msg.edit_text("❌ Error: video vacío")
        else:
            await status_msg.edit_text("❌ Error en compresión")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text("❌ Error procesando video")
    
    finally:
        # Limpiar
        for temp_file in [input_path, output_path]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

@app.on_message(filters.text)
async def handle_text(client, message):
    """Manejar mensajes de texto"""
    if not message.text.startswith('/'):
        await message.reply_text(
            "🤖 **Ultra Video Compress Bot**\n\n"
            "Envía un video para comprimirlo o usa /start\n\n"
            "🚀 **GitHub Codespaces - Cuba 🇨🇺**"
        )

if __name__ == '__main__':
    print("🚀 INICIANDO BOT EN GITHUB CODESPACES...")
    print("📱 Gratis - Sin tarjeta - Sin dólares")
    print("🇨🇺 Desde Cuba para el mundo")
    print("🔧 Iniciando...")
    
    # Verificar FFmpeg
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True)
        print("✅ FFmpeg detectado")
    except:
        print("❌ FFmpeg no encontrado")
    
    print("🤖 Bot listo - Esperando mensajes...")
    app.run()

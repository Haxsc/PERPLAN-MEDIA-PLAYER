import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from video_player import ModernVideoPlayer

icon_path = os.path.join(os.path.dirname(__file__), "icons")

import asyncio
from threading import Thread

HOST = "localhost"
PORT_SELF = 5005
PORT_PEER = 5006


async def handle_client(reader, writer):
    addr = writer.get_extra_info("peername")
    print(f"[SERVER] Conectado por {addr}")
    while True:
        data = await reader.read(1024)
        if not data:
            break
        print(f"[SERVER] Recebido: {data.decode()}")
    writer.close()


async def server():
    server = await asyncio.start_server(handle_client, HOST, PORT_SELF)
    print(f"[SERVER] Escutando em {HOST}:{PORT_SELF}")
    async with server:
        await server.serve_forever()


async def client():
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT_PEER)
        print(f"[CLIENT] Conectado ao peer em {HOST}:{PORT_PEER}")
    except ConnectionRefusedError:
        print("[CLIENT] Não foi possível conectar, peer não disponível.")
        return

    async def send_messages():
        while True:
            msg = await asyncio.get_event_loop().run_in_executor(None, input)
            if msg.strip().lower() == "sair":
                writer.close()
                await writer.wait_closed()
                break
            writer.write(msg.encode())
            await writer.drain()

    async def receive_messages():
        while True:
            data = await reader.read(1024)
            if not data:
                break
            print(f"[CLIENT] Recebido: {data.decode()}")

    await asyncio.gather(send_messages(), receive_messages())


def start_server(loop):
    loop.create_task(server())
    print("[APP] Servidor iniciado no asyncio loop.")


def start_client(loop):
    asyncio.run_coroutine_threadsafe(client(), loop)
    print("[APP] Cliente iniciado manualmente no asyncio loop.")


def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Cria o QApplication antes de qualquer QWidget
    app.setWindowIcon(QIcon(os.path.join(icon_path, "road.png")))

    # armazenamento de ARGS *FUTURO DINAMICO*
    # argv_1 = sys.argv[1]
    # argv_2 = sys.argv[2]
    # argv_3 = sys.argv[3]

    # Inicia o player normalmente
    player = ModernVideoPlayer()
    player.show()

    # Cria o asyncio loop
    loop = asyncio.new_event_loop()

    # Inicia o asyncio em thread separada (não trava o Qt)
    t = Thread(target=run_asyncio_loop, args=(loop,), daemon=True)
    t.start()

    # Inicia o servidor automaticamente
    start_server(loop)

    # Verifica se o APP foi aberto com algum video ja linkado ou nao
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        if os.path.exists(video_path) and video_path.lower().endswith(
            (".mp4", ".avi", ".mkv", ".dav")
        ):
            player.playlist.append(video_path)
            player.current_video_index = 0
            player.open_file(video_path)

    sys.exit(app.exec())

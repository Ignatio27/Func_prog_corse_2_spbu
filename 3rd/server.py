import asyncio
import os

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002
separator_token = "<SEP>"
rooms = {}


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[+] {addr} connected.")
    current_room = None

    try:
        while True:
            # Читаем данные от клиента
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode(errors="ignore").strip()

            # Команда для входа в комнату
            if message.startswith("/join"):
                room_name = message.split(" ", 1)[-1].strip()
                if current_room:
                    rooms[current_room].remove(writer)
                    if not rooms[current_room]:
                        del rooms[current_room]
                current_room = room_name
                if current_room not in rooms:
                    rooms[current_room] = set()
                rooms[current_room].add(writer)
                writer.write(f"[INFO] Joined room: {current_room}\n".encode())
                await writer.drain()
                continue

            # Если клиент не подключен к комнате
            if not current_room:
                writer.write("[ERROR] Join a room first using /join <room_name>.\n".encode())
                await writer.drain()
                continue

            # Команда для отправки файла
            if message.startswith("/sendfile"):
                _, file_name = message.split(" ", 1)
                writer.write(f"[INFO] Ready to receive file: {file_name}\n".encode())
                await writer.drain()

                os.makedirs("uploads", exist_ok=True)
                file_path = f"uploads/{file_name}"

                with open(file_path, "wb") as f:
                    while True:
                        chunk = await reader.read(1024)
                        if chunk.endswith(b"<EOF>"):
                            f.write(chunk[:-5])
                            break
                        f.write(chunk)

                writer.write("[INFO] File uploaded successfully.\n".encode())
                await writer.drain()

                # Рассылка файла всем в комнате
                for client in rooms[current_room]:
                    if client != writer:
                        try:
                            client.write(f"/file {file_name}\n".encode())
                            await client.drain()
                            with open(file_path, "rb") as f:
                                while chunk := f.read(1024):
                                    client.write(chunk)
                                    await client.drain()
                            client.write(b"<EOF>")
                            await client.drain()
                        except Exception as e:
                            print(f"[ERROR] Failed to send file to a client: {e}")
                continue

            # Обработка текстовых сообщений
            formatted_message = f"{message.replace(separator_token, ': ')}"
            print(f"Room {current_room}: {formatted_message.strip()}")
            for client in rooms[current_room]:
                if client != writer:
                    client.write(formatted_message.encode())
                    await client.drain()
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        if current_room and writer in rooms.get(current_room, set()):
            rooms[current_room].remove(writer)
            if not rooms[current_room]:
                del rooms[current_room]
        print(f"[-] {addr} disconnected.")
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle_client, SERVER_HOST, SERVER_PORT)
    addr = server.sockets[0].getsockname()
    print(f"[*] Listening as {addr[0]}:{addr[1]}")

    async with server:
        await server.serve_forever()


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\n[!] Server stopped.")

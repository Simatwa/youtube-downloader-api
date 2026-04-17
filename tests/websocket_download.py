#!/usr/bin/python
# Performs download over websocket
import asyncio

import aiohttp


async def send_and_receive_message():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(
            "ws://localhost:8000/api/v1/download/ws"
        ) as websocket:
            await websocket.send_json(
                {
                    "bitrate": None,
                    "quality": "240p",
                    "url": "https://youtu.be/1-xGerv5FOk?si=Vv_FeKPF_6eDp5di",
                }
            )

            while True:
                response = await websocket.receive_json()
                detail = response["detail"]
                match response["status"]:
                    case "downloading":
                        print(
                            f">> Downloading [{detail['ext']}] : {detail['progress']} {detail['speed']} {detail['eta']}",
                            end="\r",
                        )

                    case "finished":
                        print("--Finished--", detail["filename"])

                    case "completed":
                        print("--Completed--", detail["link"])
                        break

                    case "error":
                        print("--Error--", detail)
                        break
                    case _:
                        print("--Unknown--", response)
                        continue


if __name__ == "__main__":
    asyncio.run(send_and_receive_message())

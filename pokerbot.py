import asyncio
import json
import websockets.asyncio.connection
import random



# Kaart Class
class Kaart:
    SUIT_SYMBOLS = {"harten": "♥", "ruiten": "♦", "klaveren": "♣", "schoppen": "♠"}
    SUIT_SYMBOLS = {"harten": " H ", "ruiten": " R ", "klaveren": " K ", "schoppen": " S "}

    def __init__(self, kleur, waarde):
        """
        kleur: str, bijv. "harten", "klaveren"
        waarde: str, bijv. "A", "K", "T"
        """
        self.kleur = kleur
        self.waarde = waarde

    def __str__(self):
        # lmao waarom niet
        return f"{self.waarde}{self.SUIT_SYMBOLS[self.kleur]}"


class Speler:
    def __init__(self, naam: str, coins: int, hand: list[tuple[Kaart, bool]] = None):
        """
        Parameters:
        - naam: Name of the player.
        - coins: The number of coins the player has.
        - hand: A list of tuples, each containing a Kaart instance and a boolean for face-down status.
        """
        self.naam: str = naam
        self.coins: int = coins
        self.hand: list[tuple[Kaart, bool]] = hand or []
        self.is_AanDeBeurt: bool = False
        self.is_Gepast: bool = False
        self.current_bet: int = 0

class GameState:
    def __init__(self) -> None:
        self.MAXSPELERS = 8
        self.stoelen:dict = {}  # {stoelnummer: speler_object}
        # self.AanDeBerut:str = None # uuid of player whos turn it is
        self.river = [None, None, None, None, None] # List of cards in river. None represents no card
        self.pot:int = 0
        self.highest_bet:int = 0

STATE_LOCK = asyncio.Lock()
global state
state = GameState()

shutdown_event = asyncio.Event()

async def startup_handshake(websocket: websockets.asyncio.connection.Connection, naam: str) -> str:
    print('[DEBUG] startup handshake client side started')
    try:
        await websocket.send(json.dumps({"type": "connect", "name": naam}))
        await asyncio.sleep(1)
        msg = await websocket.recv()
        event: dict = json.loads(msg)
        if not "type" in event:
            raise RuntimeError("Invalid message received during handshake")
        if event["type"] == 'error':
            errormessage = event['message']
            print(f"[ERROR] {errormessage}")
            exit()
        elif event["type"] == 'register':
            my_uuid: str = event['uuid']
        else:
            print("[ERROR] Unexpected message type during handshake.")
            exit()
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[ERROR] Connection closed unexpectedly during handshake: {e}")
        exit()
    except json.JSONDecodeError as e:
        print(f"[ERROR] Failed to decode JSON during handshake: {e}")
        exit()
    except Exception as e:
        print(f"[ERROR] Unexpected error during handshake: {e}")
        exit()
    
    print('[DEBUG] startup handshake client side finished')
    return my_uuid


async def read_messages(websocket,client_uuid)->None:
    '''This function reads the incoming messages. It modifies the gamestate'''
    global state
    async for message in websocket:
        if shutdown_event.is_set():
            break  # Stop de lus als het shutdown-event is ingesteld
        await asyncio.sleep(0.01)
        try:
            event: dict = json.loads(message)
            if not isinstance(event, dict):
                raise ValueError("Received message is not a valid dictionary.")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to decode message: {message}, Error: {str(e)}")
            continue  # Skip processing for this invalid message

        if not "type" in event:
            print(f"[ERROR] Received message with no 'type' field: {event}")
            continue

        if event["type"] == 'register': continue


        elif event["type"] == 'gamestate':
            print(f"Received gamestate update")
            try:
                nieuwe_state = GameState()
                # download gamestate
                # nieuwe_state.AanDeBeurt = event["aanDeBeurt"]
                nieuwe_state.river = [
                    Kaart(kaart["kleur"], kaart["waarde"]) if kaart else None
                    for kaart in event["river"]
                ]
                nieuwe_state.spelersdata = event["spelers"]
                
                nieuwe_state.stoelen = {}
                for stoelnummer, spelerdict in nieuwe_state.spelersdata.items():
                    stoelnummer = int(stoelnummer)
                    hand = []
                    for kaart in spelerdict["hand"]:
                        if kaart:
                            hand.append(Kaart(kaart["kleur"], kaart["waarde"]))
                        else:
                            hand.append(None)
                    speler = Speler(
                        naam=spelerdict["naam"],
                        coins=spelerdict["coins"],
                        hand=hand
                    )
                    speler.is_AanDeBeurt = spelerdict["isAanDeBeurt"]
                    speler.is_Gepast = spelerdict["isGepast"]
                    speler.current_bet = spelerdict["current_bet"]
                    nieuwe_state.stoelen[stoelnummer] = speler
                    nieuwe_state.pot = event["pot"]
                    nieuwe_state.highest_bet = event["highest bid"]
                async with STATE_LOCK:
                    state = nieuwe_state
            except KeyError as e:
                print(f"[ERROR] Missing key in gamestate update: {e}")
            except Exception as e:
                print(f"[ERROR] Unexpected error while updating gamestate: {e}")

        elif event["type"] == 'info':
            print(event['message'])
        elif event['type'] == 'error':
            print(event['message'])
        else:
            print(f'received event of type {event["type"]} which is not supported')
        pass # handle messages

# Function to handle sending messages from the queue
async def send_messages(websocket, queue, my_uuid:str)->None:
    uuid = {'uuid': my_uuid}
    while True:
        await asyncio.sleep(0)
        if shutdown_event.is_set():
            break  # Stop de lus als het shutdown-event is ingesteld
        try:
            message:dict = await queue.get()
            message.update(uuid)
            await websocket.send(json.dumps(message))
            queue.task_done()
        except websockets.ConnectionClosed:
            print("Connection to server lost.")
            exit()
        except Exception as e:
            print(f"Error sending message: {e}")

    
async def handle_networking(websocket: websockets.asyncio.connection.Connection, naam: str, queue: asyncio.Queue):
    try:
        client_uuid = await startup_handshake(websocket, naam)
        read_task = asyncio.create_task(read_messages(websocket, client_uuid))
        send_task = asyncio.create_task(send_messages(websocket, queue, client_uuid))
        await asyncio.gather(read_task, send_task)
    except websockets.exceptions.InvalidURI as e:
        print(f"[ERROR] Invalid WebSocket URI: {e}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[ERROR] WebSocket connection was closed unexpectedly: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error during networking: {e}")



# async def send_action(websocket, action):
#     message = json.dumps({"type": "action", "action": action})
#     await websocket.send(message)



# Main game loop
async def game_loop(websocket,queue:asyncio.Queue):

    actions = [ "check","check","check","check","check","check","check","check","pass", "pass", "raise 10", "raise 20", "raise 50", "raise 1"]
    while True:
        await asyncio.sleep(1)
        async with STATE_LOCK:
            state_copy = state
        if state_copy is None:
            continue
        # await queue.put({"type": "request gamestate"}) not nessesary because this bot does not change its behaviour based on gamestate
        action = random.choice(actions)
        if not "raise" in action:
            await queue.put({"type": "action", "action": action})
        else:
            await queue.put({"type": "action", "action": action.split(" ")[0], "amount": int(action.split(" ")[1])})



async def main():
    # naam:str = input("Wat is jouw naam? Maximaal 10 characters ")[:10]
    naam = "bot" + str(random.randint(0,100))
    if any(c in naam for c in ["'", '"', ",", ".", "\\", "/"]):
        print("Ongeldige karakters in naam.")
        exit()
    
    queue = asyncio.Queue() # this queue stores all messages to bne sent.

    # async with websockets.connect("ws://IPv4:8000") as websocket:
    async with websockets.connect("ws://:8000") as websocket:
        # Create tasks for Pygame and receiving messages
        pygame_task = asyncio.create_task(game_loop(websocket,queue))
        network_task = asyncio.create_task(handle_networking(websocket,naam,queue))

        # Run both tasks concurrently
        await asyncio.gather(pygame_task, network_task)

if __name__ == "__main__":
    asyncio.run(main())
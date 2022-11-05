import fastapi

chats_routet = fastapi.APIRouter(prefix="/chats")


chats_routet.websocket("/chat/{id}")
def chat_socket():
    pass

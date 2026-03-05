export const route = {
  home: "/",
  chats: "/chats",
  chat(chatId: string) {
    return `/chats/${chatId}`
  },
}

import asyncio
import threading
from tkinter import Tk, Text, Scrollbar, Button, Entry, END, VERTICAL
from ollama import AsyncClient
from httpx import HTTPStatusError


class ChatGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat with Llama")

        self.model_name = "llama3:8b-instruct-q8_0"

        self.text_area = Text(root, wrap='word', state='disabled')
        self.text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.scrollbar = Scrollbar(root, command=self.text_area.yview, orient=VERTICAL)
        self.text_area['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.grid(row=0, column=2, sticky='ns')

        self.entry = Entry(root, width=80)
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = Button(root, text="Send", command=self.on_send)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

    def on_send(self):
        user_message = self.entry.get()
        if user_message:
            self.entry.delete(0, END)
            self.append_message("You", user_message)
            self.root.after(100, self.async_chat, user_message)

    def append_message(self, sender, message):
        self.text_area.config(state='normal')
        self.text_area.insert(END, f"{sender}: {message}\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(END)

    async def chat(self, user_message):
        self.append_message("System", "Generating response...")
        message = {'role': 'user', 'content': user_message}
        response = ""
        try:
            async for part in await AsyncClient().chat(model=self.model_name, messages=[message], stream=True):
                response += part['message']['content']
            self.append_message("Llama", response)
        except HTTPStatusError as e:
            self.append_message("System", f"HTTP Error: {e.response.status_code} - {e.response.reason_phrase}")

    def async_chat(self, user_message):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.chat(user_message))
        loop.close()


def run_gui():
    root = Tk()
    app = ChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()

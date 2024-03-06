#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from typing import Callable
import Setting
import GameEngine

class Application(tk.Frame):
    def __init__(self, master: tk.Tk, title: str):
        super().__init__(master)
        self.master: tk.Tk = master
        self.title = title
        self.aff = None
        self.time = (0, 0)

        master.title(title)
        master.geometry(Setting.data.get_geometry())
        self.menu_function = {
            "start": self.start_timer,
            "stop": self.stop_timer,
            "config": self.setting_config
        }
        self.menu = tk.Menu(self.master)
        self.select_menu = tk.Menu(self.menu, tearoff=0)
        self.select_menu.add_command(
            label="デッキコードから読み込み",
            command=lambda: self.online_create_window.create_new_window()
        )
        self.select_menu.add_command(
            label="ローカルファイルから読み込み",
            command=lambda: self.local_create_window.create_new_window()
        )
        self.menu.add_command(
            label="開始",
            command=self.start
        )
        self.menu.add_command(
            label="終了",
            command=self.end
        )
        self.menu.add_cascade(
            label="デッキ選択",
            menu=self.select_menu
        )
        self.menu.add_command(
            label=" << "
        )
        self.menu.add_command(
            label=" >> "
        )
        self.menu.add_command(
            label="設定"
        )
        master.config(menu=self.menu)

        self.game_engine = GameEngine.Master(self.master)
        self.online_create_window = OnlineDeckWindow(self.game_engine, self.title_update)
        self.local_create_window = LocalDeckWindow(self.game_engine, self.title_update)
        self.game_engine.stand_by()

    def title_update(self):
        """
        ウィンドウタイトルのアップデート
        """
        self.master.title(self.title + " 選択デッキ: " + self.game_engine.card_list.name)

    def title_add(self, add_title: str):
        """
        ウィンドウタイトルのアップデート
        タイマー用
        """
        self.master.title(self.title + " " + add_title)

    def start(self):
        """
        ゲームをスタートする関数
        GameEngineのスタートとタイマーの起動
        """
        if self.game_engine.card_list.check():
            self.game_engine.start()
            self.start_timer()
        else:
            print("カードリストの枚数が不正です")

    def end(self):
        self.stop_timer()
        self.game_engine.end()

    def start_timer(self):
        print("start_timer")
        if self.aff is not None:
            self.after_cancel(self.aff)
        self.time = (0, 0)
        self._timer()

    def stop_timer(self):
        if self.aff is not None:
            self.after_cancel(self.aff)
        self.aff = None
        self.title_add("")

    def _timer(self):
        self.time = (self.time[0], self.time[1]+1)
        if self.time[1] == 60:
            self.time = (self.time[0]+1, 0)
        self.title_add(f"  Time: {self.time[0]}分: {self.time[1]}秒")
        self.aff = self.after(1000, self._timer)

    def setting_config(self):
        print("setting_config")


class NewWindow:
    """
    デッキの読み込みや設定変更等別ウィンドウの親クラス
    """
    def __init__(self):
        self.window: tk.Toplevel = None
        self.title = ""

    def create_new_window(self):
        if self.window is not None:
            self.close()
            self.window = None
        self.create()

    def create(self):
        self.window = tk.Toplevel()
        self.window.title(self.title)
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.window.destroy()
        self.window = None

class OnlineDeckWindow(NewWindow):
    def __init__(self, game_engine, call: Callable):
        super().__init__()
        self.call = call
        self.game_engine: GameEngine.Master = game_engine
        self.title = "デッキコードから読み込み"

    def create(self):
        super().create()
        self.window.geometry("400x100")
        entry_label = tk.Label(
            self.window,
            text=""
        )
        entry_label.pack(pady=5)
        frame = tk.Frame(self.window)
        frame.pack(pady=5)
        self.entry = tk.Entry(
            frame,
            width=40
        )
        paste_button = tk.Button(
            frame,
            text="Paste",
            command=self.paste
        )
        self.entry.pack(side=tk.LEFT)
        paste_button.pack(side=tk.LEFT)
        entry_button = tk.Button(
            self.window,
            text="決定",
            command=self.submit
        )
        entry_button.pack(pady=5)

    def paste(self):
        self.entry.delete(0, tk.END)
        deck_id = self.window.clipboard_get()
        if isinstance(deck_id, str):
            self.entry.insert(0, deck_id)

    def submit(self):
        self.game_engine.load_online(self.entry.get())
        self.close()

    def close(self):
        super().close()
        self.call()
        self.game_engine.stand_by()


class LocalDeckWindow(NewWindow):
    def __init__(self, game_engine, call: Callable):
        super().__init__()
        self.call = call
        self.game_engine: GameEngine.Master = game_engine
        self.title = "ローカルファイルから読み込み"
        self.dir = "Deck"
        self.image = Setting.container.create_deck_image(
            [],
            (Setting.data.card_size[0]//2, Setting.data.card_size[1]//2)
        )

    def close(self):
        self.dir = "Deck"
        super().close()
        self.call()
        self.game_engine.stand_by()

    def filename_list_create(self) -> list[str]:
        deck_files = [deck for deck in os.listdir(self.dir) if deck != "blank.txt"]
        name_list = ["□ "+ deck if os.path.isdir(f"{self.dir}/{deck}") else deck for deck in deck_files]
        return sorted(name_list, key=lambda x: (not x.startswith("□"), x))

    def deck_image_update(self):
        self.game_engine.card_list.create_image()
        self.image_label.config(image=self.game_engine.card_list.image)

    def create(self):
        super().create()
        window_size = (
            Setting.data.card_size[0] * 12 // 2,
            Setting.data.card_size[1] * 5 // 2
        )
        self.window.geometry(f"{window_size[0]+280}x{window_size[1]+50}")
        left_frame = tk.Frame(self.window)
        left_frame.pack(side=tk.LEFT)
        upper_button = tk.Button(
            left_frame,
            text="上のフォルダへ移動",
            command=lambda: parent_folder_move()
        )
        upper_button.grid(row=0, column=0, columnspan=2, pady=2)
        scroll = tk.Scrollbar(left_frame)
        deck_list_box = tk.Listbox(
            left_frame,
            selectmode="single",
            yscrollcommand=scroll.set,
            width=40,
            height=25
            )
        deck_list_box.grid(row=1, column=0, sticky=tk.N + tk.S)
        scroll.grid(row=1, column=1, sticky=tk.N + tk.S)
        scroll["command"]=deck_list_box.yview
        deck_list_box.bind("<<ListboxSelect>>", lambda e: listbox_current(deck_list_box.curselection()))
        deck_list_box.bind("<Double-Button-1>",)
        for num, deck in enumerate(self.filename_list_create()):
            deck_list_box.insert(num, deck.replace(".txt", ""))

        right_frame = tk.Frame(self.window)
        right_frame.pack(side=tk.LEFT)
        submit_button = tk.Button(
            right_frame,
            text="決定"
        )
        submit_button.grid(row=0, column=0, padx=5, pady=2)
        deckcode_entry = tk.Entry(
            right_frame,
            width=30
        )
        deckcode_entry.grid(row=0, column=1, padx=5)
        self.image_label = tk.Label(
            right_frame,
            image=self.image
        )
        self.image_label.grid(row=1, column=0, columnspan=5)
        self.deck_image_update()

        def listbox_current(index):
            deckcode_entry.delete(0, tk.END)
            self.game_engine.card_list.reset()
            name: str = deck_list_box.get(index)
            if "□" in name:
                path = name.replace("□ ", "")
                self.dir = f"{self.dir}/{path}"
                deck_list_box.delete(0, tk.END)
                for num, deck in enumerate(self.filename_list_create()):
                    deck_list_box.insert(num, deck.replace(".txt", ""))
            else:
                self.game_engine.load_local(f"{self.dir}/{name}.txt")
                deckcode_entry.insert(0, self.game_engine.card_list.code)
            self.deck_image_update()

        def parent_folder_move():
            self.game_engine.card_list.reset()
            self.deck_image_update()
            deckcode_entry.delete(0, tk.END)
            deck_list_box.delete(0, tk.END)
            self.dir = "/".join(self.dir.split("/")[0: -1])
            if not self.dir:
                self.dir = "Deck"
            for num, deck in enumerate(self.filename_list_create()):
                deck_list_box.insert(num, deck.replace(".txt", ""))







def run(name, ver):
    win = tk.Tk()
    app = Application(win, f"{name}_Version.{ver}")
    app.mainloop()

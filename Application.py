#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import messagebox, colorchooser
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

        self.master.protocol("WM_DELETE_WINDOW", lambda:self.delete_window())
        self.master.title(title)
        self.master.geometry(Setting.data.get_geometry(False, "Field"))
        self.menu = tk.Menu(self.master)
        self.select_menu = tk.Menu(self.menu, tearoff=0)
        self.select_menu.add_command(
            label="デッキコードから読み込み",
            command=lambda: [
                self.end(),
                self.online_create_window.create_new_window()
            ]
        )
        self.select_menu.add_command(
            label="ローカルファイルから読み込み",
            command=lambda: [
                self.end(),
                self.local_create_window.create_new_window()
            ]
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
            label=" << ",
            command=lambda: self.game_engine.turn_minus()
        )
        self.menu.add_command(
            label=" >> ",
            command=lambda: self.game_engine.turn_plus()
        )
        self.menu.add_command(
            label="設定",
            command=lambda: self.setting_window.create()
        )
        self.master.config(menu=self.menu)

        self.game_engine = GameEngine.Master(self.master)
        self.enemy_window = EnemyWindow()
        self.online_create_window = OnlineDeckWindow(self.game_engine, self.title_update)
        self.local_create_window = LocalDeckWindow(self.game_engine, self.title_update, self.enemy_window)
        self.game_engine.stand_by()
        self.master.bind("<Configure>", lambda e: self.window_resized())
        self.setting_window = UserSettingWindow(self.setting_close)

    def delete_window(self):
        ret = messagebox.askyesno(
            title="Information",
            message="Applicationを終了しますか？"
        )
        if ret:
            Setting.data.save_ini()
            self.master.destroy()

    def window_resized(self):
        window_data = self.master.geometry()
        window_x, window_data = window_data.split("x")
        window_x = window_x
        window_y, position_x, position_y = window_data.split("+")
        Setting.data.window_size_set(False, (window_x, window_y, position_x, position_y))
        self.game_engine.update()

    def setting_close(self):
        self.master.geometry(Setting.data.get_geometry(False, "Field"))
        self.game_engine.update()
        if self.enemy_window.window_check():
            self.enemy_window.window.geometry(Setting.data.get_geometry(True, "Field"))
            self.enemy_window.game_engine.update()

    def get_geometry(self) -> str:
        return self.master.geometry()

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
            if self.enemy_window.window_check():
                self.enemy_window.game_engine.start()
            self._start_timer()
        else:
            print("カードリストの枚数が不正です")

    def end(self):
        self._stop_timer()
        if self.enemy_window.window_check():
            self.enemy_window.game_engine.end()
        self.game_engine.end()

    def _start_timer(self):
        print("start_timer")
        if self.aff is not None:
            self.after_cancel(self.aff)
        self.time = (0, 0)
        self._timer()

    def _stop_timer(self):
        if self.aff is not None:
            self.after_cancel(self.aff)
        self.aff = None
        self.master.title(self.title + " 選択デッキ: " + self.game_engine.card_list.name)

    def _timer(self):
        self.time = (self.time[0], self.time[1]+1)
        if self.time[1] == 60:
            self.time = (self.time[0]+1, 0)
        self.title_add(f"  Time: {self.time[0]}分: {self.time[1]}秒")
        self.aff = self.after(1000, self._timer)


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
        self.window.resizable(0, 0)
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


class LocalDeckWindow(NewWindow):
    def __init__(self, game_engine, call: Callable, enemy_window):
        super().__init__()
        self.call = call
        self.game_engine: GameEngine.Master = game_engine
        self.enemy_window: EnemyWindow = enemy_window
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

    def filename_list_create(self) -> list[str]:
        deck_files = [deck for deck in os.listdir(self.dir) if deck != "blank.txt"]
        name_list = ["□ "+ deck if os.path.isdir(f"{self.dir}/{deck}") else deck for deck in deck_files]
        return sorted(name_list, key=lambda x: (not x.startswith("□"), x))

    def deck_image_update(self):
        self.game_engine.card_list.create_image()
        self.image_label.config(image=self.game_engine.card_list.image)

    def create(self):
        super().create()
        self.window.resizable(0, 0)
        self.image = Setting.container.create_deck_image(
            [],
            (Setting.data.card_size[0]//2, Setting.data.card_size[1]//2)
        )
        self.game_engine.card_list_reset()
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
        scroll["command"] = deck_list_box.yview
        deck_list_box.bind("<<ListboxSelect>>", lambda e: listbox_current(deck_list_box.curselection()))
        deck_list_box.bind("<Double-Button-1>",)
        for num, deck in enumerate(self.filename_list_create()):
            deck_list_box.insert(num, deck.replace(".txt", ""))

        right_frame = tk.Frame(self.window)
        right_frame.pack(side=tk.LEFT)
        submit_button = tk.Button(
            right_frame,
            text="決定",
            command=self.close
        )
        submit_button.grid(row=0, column=0, padx=5, pady=2)
        deck_code_frame = tk.Frame(
            right_frame
        )
        deck_label = tk.Label(
            deck_code_frame,
            text="デッキコード"
        )
        deck_label.grid(row=0, column=0)
        deck_code_frame.grid(row=0, column=1)
        deckcode_entry = tk.Entry(
            deck_code_frame,
            width=30
        )
        deckcode_entry.grid(row=0, column=1, padx=5)
        deck_code_copy_button = tk.Button(
            deck_code_frame,
            text="クリップボードにコピー",
            command=lambda: deck_code_copy()
        )
        deck_code_copy_button.grid(row=0, column=2)
        enemy_window_button = tk.Button(
            deck_code_frame,
            text="このデッキを相手に一人回し",
            command=lambda: create_enemy_window()
        )
        enemy_window_button.grid(row=0, column=3, padx=5)
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

        def deck_code_copy():
            self.window.clipboard_clear()
            self.window.clipboard_append(deckcode_entry.get())

        def create_enemy_window():
            index = deck_list_box.curselection()
            name = deck_list_box.get(index)
            self.enemy_window.create(f"{self.dir}/{name}.txt", name)


class EnemyWindow(NewWindow):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.menu = tk.Menu(self.window)
        self.menu.add_command(
            label=" << ",
            command=lambda: self.game_engine.turn_minus()
        )
        self.menu.add_command(
            label=" >> ",
            command=lambda: self.game_engine.turn_plus()
        )

    def window_check(self) -> bool:
        if self.window is not None:
            return True
        else:
            return False

    def create(self, enemy_filepath: str, title: str):
        super().create()
        self.window.protocol("WM_DELETE_WINDOW", lambda:self.delete_window())
        self.window.config(menu=self.menu)
        self.window.geometry(Setting.data.get_geometry(True, "Field"))
        self.window.title(title)
        self.window.bind("<Configure>", lambda e: self.window_resized())
        self.game_engine = GameEngine.Master(self.window, True)
        self.game_engine.load_local(enemy_filepath)
        self.game_engine.stand_by()

    def close(self):
        self.game_engine.end()
        self.window.destroy()
        self.window = None

    def delete_window(self):
        ret = messagebox.askyesno(
            title="Information",
            message="一人回しを終了しますか？"
        )
        if ret:
            self.close()

    def window_resized(self):
        window_data = self.window.geometry()
        window_x, window_data = window_data.split("x")
        window_x = window_x
        window_y, position_x, position_y = window_data.split("+")
        Setting.data.window_size_set(True, (window_x, window_y, position_x, position_y))


class UserSettingWindow(NewWindow):
    def __init__(self, close_func: Callable):
        super().__init__()
        self.title = "設定変更"
        self.close_func = close_func

    def create(self):
        super().create()
        self.window.resizable(0, 0)
        self.window.title(self.title)
        self.window.geometry("600x400")

        top_frame = tk.Frame(self.window)
        top_frame.pack()
        player_canvas_color_frame = tk.Frame(top_frame)
        player_canvas_color_frame.grid(row=0, column=0, padx=5)
        player_canvas_button = tk.Button(
            player_canvas_color_frame,
            text="自分の背景色を変更",
            command=lambda: self.color_changed("Player")
        )
        player_canvas_button.pack()
        self.player_color_label = tk.Label(
            player_canvas_color_frame,
            bg=Setting.data.canvas_color,
            width=10,
            height=5
        )
        self.player_color_label.pack(padx=5, pady=5)
        enemy_canvas_color_frame = tk.Frame(top_frame)
        enemy_canvas_color_frame.grid(row=0, column=1, padx=5)
        enemy_canvas_button = tk.Button(
            enemy_canvas_color_frame,
            text="相手の背景色を変更",
            command=lambda: self.color_changed("Enemy")
        )
        enemy_canvas_button.pack()
        self.enemy_color_label = tk.Label(
            enemy_canvas_color_frame,
            bg=Setting.data.enemy_canvas_color,
            width=10,
            height=5
        )
        self.enemy_color_label.pack(padx=5, pady=5)

        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack()
        set_button = tk.Button(
            bottom_frame,
            text="設定変更",
            width=20,
            height=2,
            command=lambda: self.submit_close()
        )
        set_button.grid(row=0, column=0, padx=5, pady=5)
        default_set_button = tk.Button(
            bottom_frame,
            text="デフォルト設定に戻す",
            width=20,
            height=2,
            command=lambda: [
                Setting.data.default_ini(),
                self.setting_window_update(),
                self.submit_close()
            ]
        )
        default_set_button.grid(row=0, column=1, padx=5, pady=5)

    def submit_close(self):
        self.close_func()
        super().close()

    def setting_window_update(self):
        self.player_color_label.config(
            bg=Setting.data.canvas_color
        )
        self.enemy_color_label.config(
            bg=Setting.data.enemy_canvas_color
        )

    def color_changed(self, key: str):
        color = colorchooser.askcolor()
        if key == "Player":
            self.player_color_label.config(bg=color[1])
            Setting.data.canvas_color = color[1]
        elif key == "Enemy":
            self.enemy_color_label.config(bg=color[1])
            Setting.data.enemy_canvas_color = color[1]
        self.window.lift()


def run(name, ver):
    win = tk.Tk()
    app = Application(win, f"{name}_Version.{ver}")
    app.mainloop()

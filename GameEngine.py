#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import random
import tkinter as tk
from tkinter import filedialog
from typing import Callable
from PIL import Image, ImageTk

import Setting
import Object

class CardList:
    """
    ゲームで使うデッキを保持する
    実際にCardオブジェクトを生成するのはゲームスタート時
    """
    def __init__(self):
        self.name: str = ""
        self.code: str = ""
        self.list: list[str] = []
        self.image: ImageTk.PhotoImage = Setting.container.create_deck_image(
            self.list,
            (Setting.data.card_size[0] //2, Setting.data.card_size[1] //2)
        )

    def reset(self):
        self.list.clear()
        self.name = ""
        self.code = ""
        self.image: ImageTk.PhotoImage = Setting.container.create_deck_image(
            self.list,
            (Setting.data.card_size[0] //2, Setting.data.card_size[1] //2)
        )

    def get(self) -> list[str]:
        return self.list.copy()

    def create_image(self):
        self.image: ImageTk.PhotoImage = Setting.container.create_deck_image(
            self.list,
            (Setting.data.card_size[0] //2, Setting.data.card_size[1] //2)
        )

    def load_local(self, filepath: str):
        self.reset()
        self.name = filepath.split("/")[-1].replace(".txt", "")
        with open(filepath, "r", encoding="utf-8") as f:
            loaddata = f.read().split("\n")
        self.list = loaddata[0:60]
        self.code = loaddata[-1]

    def load_online(self, deck_id: str):
        self.reset()
        data_list = Setting.create_deckid_list(deck_id)
        if data_list:
            c = 0
            for d in data_list:
                c += 1
                self.list.append(d)
                print(f"Scraping_CardID: {c} / 60")
            if len(data_list) != 60:
                print("デッキコードエラー\terror_id: d_002")
            else:
                self.code = deck_id
                self.name = deck_id
        else:
            print("デッキコードエラー\terror_id: d_001")

    def check(self):
        if len(self.list) == 60:
            return True
        else:
            return False

    def save(self, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            for card_id in self.list:
                f.writelines(f"{card_id}\n")
            f.writelines(self.code)


class GameSystem:
    """
    ゲームシステムの親クラス
    クリック時の関数やカード移動等の関数を予め記述しておく
    子クラスでオーバーライドして使う
    """
    def __init__(self):
        self.list: list[Object.Card] = []
        self.object_name = ""
        self.canvas: tk.Canvas = None
        self.menu: tk.Menu

    def clear(self):
        self.list.clear()

    def _canvas_bind(self):
        if self.canvas is not None:
            self.canvas.bind("<Button-1>", lambda event:self._button_1(event))
            self.canvas.bind("<Button1-Motion>", lambda event:self._button_1_motion(event))
            self.canvas.bind("<Button-3>", lambda event:self._button_3(event))
            self.canvas.bind("<ButtonRelease-1>", lambda event:self._button_release_1(event))
            self.canvas.bind("<MouseWheel>",lambda event:self._mouse_wheel(event))
            self.canvas.bind("<Double-Button-1>", lambda event:self._double_button_1(event))

    def _button_1(self, event: tk.Event):
        """
        左クリック時の処理
        """
        print(self.__class__.__name__, self._button_1.__name__)

    def _button_1_motion(self, event: tk.Event):
        """
        ドラッグ時の処理
        """
        print(self.__class__.__name__, self._button_1_motion.__name__)

    def _button_3(self, event: tk.Event):
        """
        右クリック時の処理
        """
        print(self.__class__.__name__, self._button_3.__name__)

    def _button_release_1(self, event: tk.Event):
        """
        左クリックを離した時の処理
        """
        print(self.__class__.__name__, self._button_release_1.__name__)

    def _mouse_wheel(self, event: tk.Event):
        """
        マウスホイールを回した時の処理
        """
        print(self.__class__.__name__, self._mouse_wheel.__name__)

    def _double_button_1(self, event: tk.Event):
        """
        ダブルクリック時の処理
        """
        print(self.__class__.__name__, self._double_button_1.__name__)

    def find_tag(self, event):
        """
        イベント座標から一番近いオブジェクトのtagを取得する
        返り値は(tag, None)
        イベント座標にオブジェクトが重なっている場合返り値[1]にcurrentが入る
        """
        closest_ids = self.canvas.find_closest(event.x, event.y)
        if len(closest_ids) != 0:
            tag = self.canvas.gettags(closest_ids[0])
            return tag

    def get_tag_all(self):
        return [self.canvas.gettags(num) for num in self.canvas.find_all()]

    def update(self):
        """
        FieldCanvasのオブジェクトを更新する
        """
        pass

    def canvas_update(self):
        """
        自クラスのCanvasを更新する
        """
        pass

    def close(self):
        pass

    def pop_card(self, card: Object.Card = None) -> Object.Card:
        """
        カードを別のリストに移動する関数
        card引数がNoneの場合Listの先頭要素を移動させる
        """
        if card is None:
            card = self.list.pop(0)
        else:
            self.list.remove(card)
        return card

    def pop_card_all(self, add_system: GameSystem):
        for card in self.list:
            add_system.add_card(card)
        self.list.clear()

    def add_card(self, card: Object.Card):
        self.list.append(card)

    def find_card(self, tag: str) -> Object.Card:
        for card in self.list:
            if card.id == tag:
                return card


class Master(GameSystem):
    """
    ゲーム管理をするクラス
    Fieldも管理する
    """
    def __init__(self, master):
        super().__init__()
        self.flag = False
        self.object_name = "Field"
        self.card_list: CardList = CardList()
        self.canvas = self.canvas = tk.Canvas(
            master,
            width=Setting.data.window_size[0],
            height=Setting.data.window_size[1],
            bg=Setting.data.canvas_color
        )
        self._canvas_bind()
        self.canvas.pack()
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(
            label="どく",
            command=lambda: self.card_stat_update("どく")
        )
        self.menu.add_command(
            label="やけど",
            command=lambda: self.card_stat_update("やけど")
        )
        self.menu.add_command(
            label="まひ",
            command=lambda: self.card_stat_update("まひ")
        )
        self.menu.add_command(
            label="ねむり",
            command=lambda: self.card_stat_update("ねむり")
        )
        self.menu.add_command(
            label="こんらん",
            command=lambda: self.card_stat_update("こんらん")
        )
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )
        self.coin = Object.Coin(master, self.canvas)
        self.shuffle = Object.Shuffle(master, self.canvas)
        self.vstar = Object.VstarObject(self.canvas)
        self.energy = Object.EnergyObject(self.canvas)
        self.support = Object.SupportObject(self.canvas)
        self.retreat = Object.RetreatObject(self.canvas)
        self.deck = Deck(self.move_crad, self.canvas)
        self.hand = Hand(self.move_crad, self.canvas)
        self.temp = Temp(self.move_crad, self.canvas)
        self.trash = Trash(self.move_crad, self.canvas)
        self.side = Side(self.move_crad, self.canvas)
        self.lost = Lost(self.move_crad, self.canvas)
        self.dic: dict[str, GameSystem | ChildSystem] = {
            "Field": self,
            "Deck": self.deck,
            "Hand": self.hand,
            "Temp": self.temp,
            "Trash": self.trash,
            "Side": self.side,
            "Lost": self.lost
        }
        self.play_count = 0
        self.tag = ("_")
        self.x = None
        self.y = None

    def load_online(self, deck_id: str):
        self.card_list.load_online(deck_id)
        if self.card_list.check():
            self.deck_file_save()

    def load_local(self, filepath: str):
        self.card_list.load_local(filepath)

    def deck_file_save(self):
        filepath = filedialog.asksaveasfilename(
            title='デッキ保存',
            defaultextension='.txt',
            filetypes=[("Text Files", ".txt")],
            initialdir = "Deck")
        if filepath:
            self.card_list.save(filepath)

    def stand_by(self):
        self.flag = False
        self.canvas.delete("all")
        self.coin.position_update(
            (
                Setting.data.window_size[0] //2 - Setting.data.card_size[0] // 2,
                Setting.data.window_size[1] //2 - Setting.data.card_size[0] // 2,
            )
        )

    def start(self):
        self.tag = ("_")
        self.play_count = 0
        if not self.flag:
            self.flag = True
            for _, obj in self.dic.items():
                obj.clear()
            for index, card_id in enumerate(self.card_list.get()):
                print(f"Card生成中  {index+1} / 60")
                self.deck.add_card(Object.Card(index, card_id))
        else:
            self.canvas.delete("all")
            self.pop_card_all(self.deck)
            self.hand.pop_card_all(self.deck)
            self.temp.pop_card_all(self.deck)
            self.trash.pop_card_all(self.deck)
            self.side.pop_card_all(self.deck)
            self.lost.pop_card_all(self.deck)
        self.deck.shuffle()
        for _ in range(7):
            self.move_crad("Deck", "Hand")
        for _ in range(6):
            self.move_crad("Deck", "Side")
        self.coin.position_update(
            (
                Setting.data.card_size[0] + 10,
                10
            )
        )
        self.shuffle.view()
        self.vstar.reset()
        self.energy.reset()
        self.support.reset()
        self.retreat.reset()
        self.hand.create_window()
        for _, obj in self.dic.items():
            obj.update()

    def end(self):
        self.canvas.delete("all")
        for _, obj in self.dic.items():
            obj.close()
        self.stand_by()

    def move_crad(self, source: str, move_to: str, card: Object.Card=None):
        _card = self.dic[source].pop_card(card)
        self.dic[source].update()
        self.dic[source].canvas_update()
        self.dic[move_to].add_card(_card)
        self.dic[move_to].update()
        self.dic[move_to].canvas_update()

    def add_card(self, card: Object.Card):
        super().add_card(card)
        self.canvas.create_image(
            Setting.data.window_size[0] // 2 + Setting.data.card_size[0] // 2 * self.play_count,
            Setting.data.window_size[1] - Setting.data.card_size[1],
            anchor="c",
            image=card.image_tk,
            tag=card.id
        )
        self.play_count += 1

    def update_card(self, card: Object.Card):
        """
        カードを指定してアップデートする
        """
        x, y, _, _ = self.canvas.bbox(card.id)
        self.canvas.delete(card.id)
        self.canvas.create_image(
            x, y,
            anchor="nw",
            image=card.image_tk,
            tag=card.id
        )

    def canvas_update(self):
        """
        Filedのカードのレイヤーをアップデートする
        """
        for card in self.list:
            if card.id == self.tag[0]:
                if card.hp is None:
                    self.canvas.lower(card.id)
                else:
                    self.canvas.lift(card.id)
        for tag in self.get_tag_all():
            if "System" in tag[0]:
                self.canvas.lift(tag[0])

    def card_stat_update(self, key: str):
        card = self.find_card(self.tag[0])
        card.card_stat_update(key)
        self.update_card(card)

    def _button_1(self, event: tk.Event):
        self.canvas.delete("show_image")
        self.playcount = 0
        tag = self.find_tag(event)
        self.tag = tag
        if tag[-1] == "current": #クリックした場所にオブジェクトが存在するかどうか
            if "System" in tag[0]: #クリックしたオブジェクトがシステムオブジェクトかどうか
                if "Coin" in tag[0]:
                    self.coin.toss()
                elif "Shuffle" in tag[0]:
                    self.deck.shuffle()
                    self.shuffle.shuffle_start()
                elif "Vstar" in tag[0]:
                    self.vstar.click()
                elif "Energy" in tag[0]:
                    self.energy.click()
                elif "Support" in tag[0]:
                    self.support.click()
                elif "Retreat" in tag[0]:
                    self.retreat.click()
                elif "Deck" in tag[0]:
                    self.move_crad("Deck", "Hand")
                elif "Temp" in tag[0]:
                    self.move_crad("Deck", "Temp")
                elif "Side" in tag[0]:
                    self.move_crad("Side", "Hand")
                elif "Trash" in tag[0]:
                    pass
                elif "Lost" in tag[0]:
                    pass
            else:
                self.canvas_update()
                self.canvas.addtag_withtag("move", tag[0])
                self.x = event.x
                self.y = event.y
        else:
            self.x = event.x
            self.y = event.y

    def _button_1_motion(self, event: tk.Event):
        if self.flag:
            if self.tag[-1] != "current":
                self.canvas.delete("rect")
                self.canvas.create_rectangle(
                    self.x, self.y,
                    event.x, event.y,
                    outline=Setting.get_reverse_color(Setting.data.canvas_color),
                    tag="rect"
                )
            else:
                self.canvas.move(
                    "move",
                    event.x - self.x,
                    event.y - self.y
                )
                self.x = event.x
                self.y = event.y

    def _button_release_1(self, event: tk.Event):
        if self.flag:
            if ("rect", "current") in self.get_tag_all():
                self.canvas.addtag_overlapping(
                    "move",
                    self.x, self.y,
                    event.x, event.y
                )
                for t in self.get_tag_all():
                    if "System" in t[0]:
                        self.canvas.dtag(t[0], "move")
            else:
                tag = self.find_tag(event)
                if "System" in tag[0]:
                    move_to = ""
                    if "System_Deck" in tag:
                        move_to = "Deck"
                    elif "System_Hand" in tag[0]:
                        move_to = "Hand"
                    elif "System_Temp" in tag[0]:
                        move_to = "Temp"
                    elif "System_Trash" in tag[0]:
                        move_to = "Trash"
                    elif "System_Side" in tag[0]:
                        move_to = "Side"
                    elif "System_Lost" in tag[0]:
                        move_to = "Lost"
                    if move_to:
                        move_card_id = [t[0] for t in self.get_tag_all() if "move" in t]
                        for card in [self.find_card(tag) for tag in move_card_id]:
                            self.move_crad("Field", move_to, card)
                            self.canvas.delete(card.id)

                self.canvas.dtag("move", "move")
            self.canvas.delete("rect")



    def _double_button_1(self, event: tk.Event):
        self.canvas.delete("show_image")
        tag = self.find_tag(event)
        if tag[-1] == "current":
            if "System" in tag[0]:
                self._button_1(event)
            else:
                self.card_stat_update("check")

    def _button_3(self, event: tk.Event):
        self.canvas.delete("show_image")
        if self.flag:
            tag = self.find_tag(event)
            self.tag = tag
            if tag[-1] == "current":
                if "System" in tag[0]:
                    if "Deck" in tag[0]:
                        self.deck.create_window()
                    elif "Hand" in tag[0]:
                        self.hand.create_window()
                    elif "Temp" in tag[0]:
                        self.temp.create_window()
                    elif "Trash" in tag[0]:
                        self.trash.create_window()
                    elif "Side" in tag[0]:
                        self.side.create_window()
                    elif "Lost" in tag[0]:
                        self.lost.create_window()
                else:
                    self.menu.post(event.x_root, event.y_root)

    def _mouse_wheel(self, event: tk.Event):
        if self.flag:
            tag = self.find_tag(event)
            if tag[-1] == "current":
                if not "System" in tag[0]:
                    card = self.find_card(tag[0])
                    card.hp_update(event.delta)
                    self.update_card(card)
                elif tag[0] == "System_Deck":
                    pass
                    #マリガンカウント処理




class ChildSystem(GameSystem):
    """
    対戦相手に画面共有しないデッキや手札等を管理するクラスの親クラス
    別ウィンドウでCanvasを表示するのでself.windowの記述が必要
    """
    def __init__(self, move_card: Callable, field_canvas: tk.Canvas):
        super().__init__()
        self.move_card = move_card
        self.window = None
        self.field_canvas = field_canvas
        self.canvas: tk.Canvas
        self.position: tuple[int]
        self.window_size: tuple[int]

    def _create_menu(self):
        """
        キャンバスを右クリックしたときのポップアップメニューを作成する
        windowが表示されるたびに呼び出す
        """
        self.menu = tk.Menu(self.canvas, tearoff=0)

    def create_window(self):
        """
        各ChildSystemのWindowを生成する
        """
        if self.window is not None:
            self.close()
        self.window = tk.Toplevel()
        self.window.title(self.object_name)
        self.window.geometry(f"{self.window_size[0]}x{self.window_size[1]}")
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.canvas = tk.Canvas(
            self.window,
            width=self.window_size[0],
            height=self.window_size[1],
            bg=Setting.data.canvas_color
        )
        self.canvas.pack()
        self._create_menu()
        self._canvas_bind()
        self.canvas_update()
        self.update()

    def close(self):
        """
        Windowが閉じたときに呼び出す関数
        """
        if self.window is not None:
            self.window.destroy()
            self.window = None
        self.update()

    def shuffle(self):
        random.shuffle(self.list)
        if self.window is not None:
            self.canvas_update()

    def update(self):
        """
        FieldCanvasのオブジェクトを更新する
        """
        color = "white" if self.window is None else "red"
        self.image = Setting.container.create_system_image(
            self.object_name,
            len(self.list),
            color
        )
        self.field_canvas.delete(f"System_{self.object_name}")
        self.field_canvas.create_image(
            self.position[0],
            self.position[1],
            anchor="nw",
            image=self.image,
            tag=f"System_{self.object_name}"
        )

    def canvas_update(self):
        """
        自クラスのCanvasを更新する
        """
        if self.window is not None:
            self.canvas.delete("all")
            new_line_index = self.window_size[0] // Setting.data.card_size[0] *2 -1
            for index, card in enumerate(self.list):
                row = index // new_line_index
                if row > 0:
                    index = index - row * new_line_index
                self.canvas.create_image(
                    index * (Setting.data.card_size[0] // 2),
                    row * Setting.data.card_size[1],
                    anchor = "nw",
                    image = card.image_tk,
                    tag=card.id
                )

    def add_card(self, card: Object.Card):
        super().add_card(card)
        self.update()
        if self.window is not None:
            self.canvas_update()

    def _button_1(self, event: tk.Event):
        tag = self.find_tag(event)
        if tag[-1] == "current":
            self.move_card(self.object_name, "Field", self.find_card(tag[0]))

    def _button_3(self, event: tk.Event):
        tag = self.find_tag(event)
        if tag[-1] == "current":
            self.menu.post(event.x_root, event.y_root)


class Hand(ChildSystem):
    def __init__(self, move_card, canvas):
        super().__init__(move_card, canvas)
        self.object_name = "Hand"
        self.position = (
            Setting.data.window_size[0] / 4,
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )
        self.window_size = (
            Setting.data.window_size[0],
            Setting.data.card_size[1]
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )


class Deck(ChildSystem):
    def __init__(self, move_card, canvas):
        super().__init__(move_card, canvas)
        self.object_name = "Deck"
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0],
            0
        )
        self.window_size = (
            Setting.data.card_size[0] * 8,
            Setting.data.card_size[1] * 4
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="場に出す"
        )
        self.menu.add_command(
            label="手札に入れる"
        )
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )



class Temp(ChildSystem):
    def __init__(self, move_card, canvas):
        super().__init__(move_card, canvas)
        self.object_name = "Temp"
        self.position = (
            Setting.data.window_size[0] /4 *3 - Setting.data.card_size[0],
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )
        self.window_size = (
            Setting.data.card_size[0] * 7,
            Setting.data.card_size[1]
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="場に出す"
        )
        self.menu.add_command(
            label="手札に入れる"
        )
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )



class Trash(ChildSystem):
    def __init__(self, move_card, canvas):
        super().__init__(move_card, canvas)
        self.object_name = "Trash"
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0],
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )
        self.window_size = (
            Setting.data.card_size[0] * 8,
            Setting.data.card_size[1] * 4
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="ソート"
        )
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )



class Side(ChildSystem):
    def __init__(self, move_card, canvas):
        super().__init__(move_card, canvas)
        self.object_name = "Side"
        self.position = (
            0,
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )
        self.window_size = (
            Setting.data.card_size[0] * 6,
            Setting.data.card_size[1]
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="場に出す"
        )
        self.menu.add_command(
            label="手札に入れる"
        )
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )



class Lost(ChildSystem):
    def __init__(self, move_card, canvas):
        super().__init__(move_card, canvas)
        self.object_name = "Lost"
        self.position = (0, 0)
        self.window_size = (
            Setting.data.card_size[0] * 8,
            Setting.data.card_size[1] * 2
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="画像表示"
        )
        self.menu.add_command(
            label="画像表示(Window)"
        )

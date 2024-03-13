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

    def sort(self):
        self.list.sort()
        self.canvas_update()

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
        if Setting.debug:
            print(self.__class__.__name__, self._button_1.__name__)

    def _button_1_motion(self, event: tk.Event):
        """
        ドラッグ時の処理
        """
        if Setting.debug:
            print(self.__class__.__name__, self._button_1_motion.__name__)

    def _button_3(self, event: tk.Event):
        """
        右クリック時の処理
        """
        if Setting.debug:
            print(self.__class__.__name__, self._button_3.__name__)

    def _button_release_1(self, event: tk.Event):
        """
        左クリックを離した時の処理
        """
        if Setting.debug:
            print(self.__class__.__name__, self._button_release_1.__name__)

    def _mouse_wheel(self, event: tk.Event):
        """
        マウスホイールを回した時の処理
        """
        if Setting.debug:
            print(self.__class__.__name__, self._mouse_wheel.__name__)

    def _double_button_1(self, event: tk.Event):
        """
        ダブルクリック時の処理
        """
        if Setting.debug:
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

    def add_card(self, card: Object.Card, head: bool=False):
        if head:
            self.list.insert(0, card)
        else:
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
    def __init__(self, master, enemy_flag: bool=False):
        super().__init__()
        self.enemy_flag = enemy_flag
        self.flag = False
        self.object_name = "Field"
        self.card_list: CardList = CardList()
        self.canvas = self.canvas = tk.Canvas(
            master,
            width=Setting.data.window_size[0],
            height=Setting.data.window_size[1],
            bg=Setting.data.get_canvas_color(self.enemy_flag)
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
            label="画像表示",
            command=lambda: self.create_big_image(self.find_card(self.tag[0]))
        )
        self.menu.add_command(
            label="画像表示(Window)",
            command=lambda: Object.card_view_window.window_create(self.find_card(self.tag[0]))
        )
        self.not_current_menu = tk.Menu(self.canvas, tearoff=0)
        self.not_current_menu.add_command(
            label=" << ",
            command=self.turn_minus
        )
        self.not_current_menu.add_command(
            label=" >> ",
            command=self.turn_plus
        )
        self.not_current_menu.add_command(
            label="ターンエンド",
            command=self.turn_next
        )
        self.not_current_menu.add_command(
            label="マリガン",
            command=self.start
        )
        self.coin = Object.Coin(master, self.canvas)
        self.shuffle = Object.Shuffle(master, self.canvas)
        self.vstar = Object.VstarObject(self.canvas)
        self.energy = Object.EnergyObject(self.canvas)
        self.support = Object.SupportObject(self.canvas)
        self.retreat = Object.RetreatObject(self.canvas)
        self.deck = Deck(self.enemy_flag, self.move_crad, self.add_turn, self.canvas, self.deck_shuffle)
        self.hand = Hand(self.enemy_flag, self.move_crad, self.add_turn, self.canvas, self.deck_shuffle)
        self.temp = Temp(self.enemy_flag, self.move_crad, self.add_turn, self.canvas)
        self.trash = Trash(self.enemy_flag, self.move_crad, self.add_turn, self.canvas)
        self.side = Side(self.enemy_flag, self.move_crad, self.add_turn, self.canvas)
        self.lost = Lost(self.enemy_flag, self.move_crad, self.add_turn, self.canvas)
        self.dic: dict[str, GameSystem | ChildSystem] = {
            "Field": self,
            "Deck": self.deck,
            "Hand": self.hand,
            "Temp": self.temp,
            "Trash": self.trash,
            "Side": self.side,
            "Lost": self.lost
        }
        self.turn_manager = TurnManager(
            self.deck,
            self.hand,
            self.temp,
            self.trash,
            self.side,
            self.lost
        )
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

    def card_list_reset(self):
        self.card_list.reset()

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
        for _ in range(10):
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
        self.turn_manager.reset([], "Start")

    def end(self):
        for _, obj in self.dic.items():
            if obj.object_name == "Deck":
                obj.close(True)
            else:
                obj.close()
        self.canvas.delete("all")
        self.stand_by()

    def add_turn(self, title: str):
        """
        Undo機能用の履歴を保存する関数
        """
        add_list = []
        for card in self.list:
            x, y, _, _ = self.canvas.bbox(card.id)
            add_list.append(
                (
                    (x, y),
                    card
                )
            )
        self.turn_manager.add(add_list, title)

    def turn_plus(self):
        manager_data = self.turn_manager.plus()
        for _, obj in self.dic.items():
            if obj.object_name != self.object_name:
                obj.list = manager_data[obj.object_name].copy()
                obj.update()
                obj.canvas_update()
        for tag in self.get_tag_all():
            if not "System" in tag[0]:
                self.canvas.delete(tag[0])
        self.list.clear()
        for data in manager_data["Field"]:
            self.list.append(data[1])
            self.canvas.create_image(
                data[0][0],
                data[0][1],
                anchor="nw",
                image=data[1].image_tk,
                tag=data[1].id
            )
        self.canvas_update()

    def turn_minus(self):
        manager_data = self.turn_manager.minus()
        for _, obj in self.dic.items():
            if obj.object_name != self.object_name:
                obj.list = manager_data[obj.object_name].copy()
                obj.update()
                obj.canvas_update()
        for tag in self.get_tag_all():
            if not "System" in tag[0]:
                self.canvas.delete(tag[0])
        self.list.clear()
        for data in manager_data["Field"]:
            self.list.append(data[1])
            self.canvas.create_image(
                data[0][0],
                data[0][1],
                anchor="nw",
                image=data[1].image_tk,
                tag=data[1].id
            )
        self.canvas_update()

    def move_crad(self, source: str, move_to: str, card: Object.Card=None, head: bool=False):
        """
        カードの移動を行う関数
        ChildSystemからも呼び出す
        """
        _card = self.dic[source].pop_card(card)
        self.dic[source].update()
        self.dic[source].canvas_update()
        self.dic[move_to].add_card(_card, head)
        self.dic[move_to].update()
        self.dic[move_to].canvas_update()

    def add_card(self, card: Object.Card, head: bool=False):
        super().add_card(card, head)
        self.canvas.create_image(
            Setting.data.window_size[0] // 2 + Setting.data.card_size[0] // 2 * self.play_count,
            Setting.data.window_size[1] - Setting.data.card_size[1],
            anchor="c",
            image=card.image_tk,
            tag=card.id
        )
        self.card_replace(card.id)
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

    def create_big_image(self, card: Object.Card):
        self.canvas.delete("show_image")
        image = Setting.container.get(card.card_id)
        self.big_image = ImageTk.PhotoImage(image)
        self.canvas.create_image(
            0, 0,
            anchor = "nw",
            image = self.big_image,
            tag="show_image"
        )

    def create_list_image(self, list_name: str):
        new_line_index = Setting.data.window_size[0] // Setting.data.card_size[0] *2 -1
        for index, card in enumerate(self.dic[list_name].list):
            row = index // new_line_index
            if row > 0:
                index = index - row * new_line_index
            self.canvas.create_image(
                index * (Setting.data.card_size[0] / 2),
                row * Setting.data.card_size[1],
                anchor="nw",
                image=card.image_tk,
                tag="show_image"
            )

    def card_stat_update(self, key: str):
        card = self.find_card(self.tag[0])
        card.card_stat_update(key)
        self.update_card(card)

    def turn_next(self):
        for tag in self.get_tag_all():
            if not "System" in tag[0]:
                card = self.find_card(tag[0])
                card.turn_reset()
                self.update_card(card)
        self.energy.reset()
        self.support.reset()
        self.retreat.reset()

    def card_replace(self, tag: str):
        """
        画面外に行ってしまったCardオブジェクトを画面内に戻す
        """
        add_move = 20
        left, top, right, bottom = self.canvas.bbox(tag)
        if left < 0:
            self.canvas.move(tag, -(left-add_move), 0)
        if top < 0:
            self.canvas.move(tag, 0, -(top-add_move))
        if Setting.data.window_size[0] < right:
            self.canvas.move(tag, Setting.data.window_size[0] - (right+add_move), 0)
        if Setting.data.window_size[1] < bottom:
            self.canvas.move(tag, 0, Setting.data.window_size[1] - (bottom+add_move))

    def deck_shuffle(self):
        self.deck.shuffle()
        self.shuffle.shuffle_start()
        self.add_turn("Deck_Shuffle")

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
                    self.deck_shuffle()
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
                    self.add_turn("Deck -> Hand")
                elif "Temp" in tag[0]:
                    self.move_crad("Deck", "Temp")
                    self.add_turn("Deck -> Temp")
                elif "Side" in tag[0]:
                    self.move_crad("Side", "Hand")
                    self.add_turn("Side -> Hand")
                elif "Trash" in tag[0]:
                    self.create_list_image("Trash")
                elif "Lost" in tag[0]:
                    self.create_list_image("Lost")
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
                    outline=Setting.get_reverse_color(Setting.data.get_canvas_color(self.enemy_flag)),
                    width=2,
                    tag="rect"
                )
            else:
                if not "System" in self.tag[0]:
                    self.canvas.move(
                        "move",
                        event.x - self.x,
                        event.y - self.y
                    )
                    self.x = event.x
                    self.y = event.y
                    self.play_count = 0

    def _button_release_1(self, event: tk.Event):
        if self.flag:
            if ("rect", "current") in self.get_tag_all():
                self.canvas.addtag_overlapping(
                    "move",
                    self.x, self.y,
                    event.x, event.y
                )
                self.play_count = 0
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
                        names = ""
                        move_card_id = [t[0] for t in self.get_tag_all() if "move" in t]
                        if move_card_id:
                            for card in [self.find_card(tag) for tag in move_card_id]:
                                self.move_crad("Field", move_to, card)
                                self.canvas.delete(card.id)
                                names += f"{card.name}\n"
                            self.add_turn(f"Field -> {move_to}\n{names}")
                for tag in self.get_tag_all():
                    if "move" in tag:
                        self.card_replace(tag[0])
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
        else:
            self.turn_next()

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
                elif self.find_card(tag[0]).tail_flag:
                    card = self.find_card(tag[0])
                    card.tail_flag = False
                    card._update_image_tk()
                    self.update_card(card)
                else:
                    self.menu.post(event.x_root, event.y_root)
            else:
                self.not_current_menu.post(event.x_root, event.y_root)

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
    def __init__(self, enemy_flag, move_card: Callable, add_turn: Callable, field_canvas: tk.Canvas):
        super().__init__()
        self.enemy_flag = enemy_flag
        self.move_card_method = move_card
        self.add_turn = add_turn
        self.window = None
        self.field_canvas = field_canvas
        self.canvas: tk.Canvas
        self.position: tuple[int]
        self.window_size: tuple[int]
        self.tag = "_"

    def get(self) -> list[Object.Card]:
        return self.list.copy()

    def get_geometry(self) -> str:
        return self.window.geometry()

    def move_card(self, move_to, top: bool=False):
        card = self.find_card(self.tag[0])
        self.move_card_method(self.object_name, move_to, card, top)
        if card:
            self.add_turn(f"{self.object_name} -> {move_to}\n{card.name}")

    def _create_menu(self):
        """
        キャンバスを右クリックしたときのポップアップメニューを作成する
        windowが表示されるたびに呼び出す
        """
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(
            label="場に出す",
            command=lambda: self.move_card("Field")
        )

    def _add_menu_command(self):
        """
        各ChildSystemで共通のメニューコマンドを追加する
        最後尾に追加したいので関数で追加する
        """
        self.menu.add_command(
            label="ソート",
            command=self.sort
        )
        self.menu.add_command(
            label="画像表示",
            command=lambda: self.create_big_image(self.find_card(self.tag[0]))
        )
        self.menu.add_command(
            label="画像表示(Window)",
            command=lambda: Object.card_view_window.window_create(self.find_card(self.tag[0]))
        )

    def create_window(self):
        """
        各ChildSystemのWindowを生成する
        """
        if self.window is not None:
            self.close()
        self.window = tk.Toplevel()
        self.window.title(self.object_name)
        self.window.geometry(Setting.data.get_geometry(self.enemy_flag, self.object_name))
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.resizable(0, 0)
        self.window_size = Setting.data.get_window_size(self.object_name)
        self.canvas = tk.Canvas(
            self.window,
            width=self.window_size[0],
            height=self.window_size[1],
            bg=Setting.data.get_canvas_color(self.enemy_flag)
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

    def turn_plus(self):
        pass

    def turn_minus(self):
        pass

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

    def create_big_image(self, card: Object.Card):
        self.field_canvas.delete("show_image")
        image = Setting.container.get(card.card_id)
        self.big_image = ImageTk.PhotoImage(image)
        self.field_canvas.create_image(
            0, 0,
            anchor = "nw",
            image = self.big_image,
            tag="show_image"
        )

    def add_card(self, card: Object.Card, head: bool=False):
        super().add_card(card, head)
        self.update()
        if self.window is not None:
            self.canvas_update()

    def move_card_all(self, move_to: str):
        self.tag = ("_")
        while len(self.list):
            self.move_card(move_to)
        self.add_turn(f"{self.object_name} -> {move_to}\nall")

    def _button_1(self, event: tk.Event):
        self.tag = self.find_tag(event)
        if self.tag[-1] == "current":
            self.move_card("Field")
            if self.object_name != "Hand":
                if len(self.list) == 0:
                    self.close()

    def _double_button_1(self, event: tk.Event):
        self._button_1(event)

    def _button_3(self, event: tk.Event):
        tag = self.find_tag(event)
        if tag[-1] == "current":
            self.tag = tag
            self.menu.post(event.x_root, event.y_root)


class Hand(ChildSystem):
    def __init__(self, enemy_flag, move_card, add_turn, canvas, deck_shuffle: Callable):
        super().__init__(enemy_flag, move_card, add_turn, canvas)
        self.deck_shuffle = deck_shuffle
        self.object_name = "Hand"
        self.position = (
            Setting.data.window_size[0] / 4,
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )

    def create_window(self):
        super().create_window()
        self.window.bind("<Configure>", lambda e: self.window_resized())
        self.window.resizable(1, 0)

    def window_resized(self):
        """
        Windowのサイズ変更、Windowの場所移動時に呼び出す関数
        """
        window_width = int(self.window.geometry().split("x")[0])
        self.canvas.config(
            width=window_width
        )

    def canvas_update(self):
        """
        自クラスのCanvasを更新する
        """
        if self.window is not None:
            self.canvas.delete("all")
            for index, card in enumerate(self.list):
                self.canvas.create_image(
                    index * (Setting.data.card_size[0] // 2),
                    0,
                    anchor = "nw",
                    image = card.image_tk,
                    tag=card.id
                )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="裏向きで場に出す",
            command = lambda: [
                self.find_card(self.tag[0]).card_tail(),
                self.move_card("Field")
            ]
        )
        self.menu.add_command(
            label="デッキに戻す",
            command=lambda: self.move_card("Deck")
        )
        self.menu.add_command(
            label="すべてデッキに戻す",
            command=lambda:[
                self.shuffle(),
                self.move_card_all("Deck"),
            ]
        )
        self.menu.add_command(
            label="すべてデッキに戻してシャッフル",
            command=lambda:[
                self.move_card_all("Deck"),
                self.deck_shuffle(),
            ]
        )
        self.menu.add_command(
            label="すべて場に出す",
            command=lambda: self.move_card_all("Field")
        )
        self.menu.add_command(
            label="Tempに入れる",
            command=lambda: self.move_card("Temp")
        )
        self._add_menu_command()


class Deck(ChildSystem):
    def __init__(self, enemy_flag, move_card, add_turn, canvas, deck_shuffle: Callable):
        super().__init__(enemy_flag, move_card, add_turn, canvas)
        self.object_name = "Deck"
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0],
            0
        )
        self.deck_shuffle = deck_shuffle

    def close(self, flag: bool=False):
        super().close()
        if not flag:
            self.deck_shuffle()

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="手札に入れる",
            command=lambda: self.move_card("Hand")
        )
        self.menu.add_command(
            label="Tempに入れる",
            command=lambda: self.move_card("Temp")
        )
        self.menu.add_command(
            label="シャッフルせずにWindowを閉じる",
            command=lambda: self.close(True)
        )
        self._add_menu_command()



class Temp(ChildSystem):
    def __init__(self, enemy_flag, move_card, add_turn, canvas):
        super().__init__(enemy_flag, move_card, add_turn, canvas)
        self.object_name = "Temp"
        self.position = (
            Setting.data.window_size[0] /4 *3 - Setting.data.card_size[0],
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )

    def _create_menu(self):
        super()._create_menu()
        self.menu.add_command(
            label="手札に入れる",
            command=lambda: self.move_card("Hand")
        )
        self.menu.add_command(
            label="すべて手札に入れる",
            command=lambda: self.move_card_all("Hand")
        )
        self.menu.add_command(
            label="デッキの上に戻す",
            command=lambda: self.move_card("Deck", True)
        )
        self.menu.add_command(
            label="デッキの下に戻す",
            command=lambda: self.move_card("Deck")
        )
        self._add_menu_command()



class Trash(ChildSystem):
    def __init__(self, enemy_flag, move_card, add_turn, canvas):
        super().__init__(enemy_flag, move_card, add_turn, canvas)
        self.object_name = "Trash"
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0],
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )

    def _create_menu(self):
        super()._create_menu()
        self._add_menu_command()



class Side(ChildSystem):
    def __init__(self, enemy_flag, move_card, add_turn, canvas):
        super().__init__(enemy_flag, move_card, add_turn, canvas)
        self.object_name = "Side"
        self.position = (
            0,
            Setting.data.window_size[1] - Setting.data.card_size[1]
        )

    def _create_menu(self):
        super()._create_menu()
        self._add_menu_command()

    def close(self):
        super().close()
        self.shuffle()



class Lost(ChildSystem):
    def __init__(self, enemy_flag, move_card, add_turn, canvas):
        super().__init__(enemy_flag, move_card, add_turn, canvas)
        self.object_name = "Lost"
        self.position = (0, 0)

    def _create_menu(self):
        super()._create_menu()
        self._add_menu_command()



class TurnManager:
    def __init__(self, deck, hand, temp, trash, side, lost):
        self.data = []
        self.index = 0
        self.deck: Deck = deck
        self.hand: Hand = hand
        self.temp: Temp = temp
        self.trash: Trash = trash
        self.side: Side = side
        self.lost: Lost = lost

    def reset(self, field_data, title: str):
        self.data.clear()
        self.index = 0
        dic = {
            "title": title,
            "Field": field_data,
            "Deck": self.deck.get(),
            "Hand": self.hand.get(),
            "Temp": self.temp.get(),
            "Trash": self.trash.get(),
            "Side": self.side.get(),
            "Lost": self.lost.get()
        }
        self.data.append(dic)

    def add(self, field_data, title: str):
        dic = {
            "title": title,
            "Field": field_data,
            "Deck": self.deck.get(),
            "Hand": self.hand.get(),
            "Temp": self.temp.get(),
            "Trash": self.trash.get(),
            "Side": self.side.get(),
            "Lost": self.lost.get()
        }
        self.data = self.data[:self.index+1]
        self.index += 1
        self.data.append(dic)

    def plus(self) -> dict:
        self.index += 1
        if self.index >= len(self.data)-1:
            self.index = len(self.data)-1
        return self.data[self.index]

    def minus(self) -> dict:
        self.index -= 1
        if self.index < 0:
            self.index = 0
        return self.data[self.index]

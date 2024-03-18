#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
import random
import os
import tkinter as tk
from PIL import Image, ImageTk
import Setting


class Card:
    """
    カードクラス
    """
    def __init__(self, index: int, card_id: str):
        self.card_id = card_id
        self.id = f"id_{str(index)}"
        filename = os.listdir(f"Card/{card_id}")[0]
        self.image = Setting.container.get(card_id)
        self.image_tk: ImageTk.PhotoImage
        self.check = False
        self.doku = False
        self.yakedo = False
        self.bad_stat = ""
        self.tail_flag = False
        self.category, self.name = filename.replace(".jpg", "").split("_")
        if self.category == "ポケモン":
            self.hp = 0
        else:
            self.hp = None
        self.move = False
        self._update_image_tk()

    def _get_index(self):
        return int(self.id.replace("id_", ""))

    def __lt__(self, other: Card):
        return self._get_index() < other._get_index()

    def card_tail(self):
        self.tail_flag = True
        self._update_image_tk()

    def card_reset(self):
        """
        カードを初期ステータスに戻す
        """
        if self.hp is not None:
            self.hp = 0
        self.doku = False
        self.yakedo = False
        self.bad_stat = ""
        self.check = False
        self.tail_flag = False

    def turn_reset(self):
        """
        ターン経過時の処理
        """
        self.check = False
        self._update_image_tk()

    def hp_update(self, delta):
        if self.hp is not None:
            if delta > 0:
                self.hp += 10
            else:
                self.hp -= 10
                if self.hp < 0:
                    self.hp = 0
        self._update_image_tk()

    def card_stat_update(self, key: str):
        if key == "check":
            self.check = not self.check
        elif key == "どく":
            self.doku = not self.doku
        elif key == "やけど":
            self.yakedo = not self.yakedo
        elif key in ["ねむり", "まひ", "こんらん"]:
            if self.bad_stat == key:
                self.bad_stat = ""
            else:
                self.bad_stat = key
        self._update_image_tk()

    def _get_card_icon(self, key: str) -> Image.Image:
        image = Setting.container.get(f"System_{key}")
        image.thumbnail(
            (Setting.data.card_size[0] // 3, Setting.data.card_size[0] // 3),
            Image.LANCZOS
        )
        return image

    def _update_image_tk(self):
        if self.tail_flag:
            self.image_tk = ImageTk.PhotoImage(
                Setting.container.get("System_Card").resize(Setting.data.get_card_size())
            )
        else:
            image = self.image.copy().resize(Setting.data.get_card_size())
            if self.hp is not None:
                if self.doku:
                    stat_image = self._get_card_icon("doku")
                    image.paste(
                        stat_image,
                        (0, 0),
                        mask=stat_image
                    )
                if self.yakedo:
                    stat_image = self._get_card_icon("yakedo")
                    image.paste(
                        stat_image,
                        (Setting.data.card_size[0] // 3, 0),
                        mask=stat_image
                    )
                if self.bad_stat != "":
                    if self.bad_stat == "ねむり":
                        stat_image = self._get_card_icon("nemuri")
                    elif self.bad_stat == "まひ":
                        stat_image = self._get_card_icon("mahi")
                    elif self.bad_stat == "こんらん":
                        stat_image = self._get_card_icon("konran")
                    image.paste(
                        stat_image,
                        (0, Setting.data.card_size[0] // 3),
                        mask=stat_image
                    )
                hp_image = Setting.container.create_text(self.hp, "white")
                image.paste(
                    hp_image,
                    (
                        image.size[0] - hp_image.size[0] -5,
                        image.size[1] - hp_image.size[1] -5,
                    ),
                    mask=hp_image
                )
            if self.check:
                check_image = self._get_card_icon("check")
                image.paste(
                    check_image,
                    (Setting.data.card_size[0] // 3 * 2, 0),
                    mask=check_image
                )
            self.image_tk = ImageTk.PhotoImage(image)



class Coin:
    """
    コインクラス
    回転処理は後回し
    """
    def __init__(self, master: tk.Tk, canvas: tk.Canvas):
        self.master = master
        self.canvas = canvas
        self.position = None
        self.head_image = Image.open("Misc/coin_head.png").resize((Setting.data.card_size[0], Setting.data.card_size[0]))
        self.tail_image = Image.open("Misc/coin_tail.png").resize((Setting.data.card_size[0], Setting.data.card_size[0]))
        self.image = ImageTk.PhotoImage(self.head_image)
        self.aff = None

    def position_update(self, position: tuple[int]):
        self.position = position
        self.image = ImageTk.PhotoImage(self.head_image)
        self.view()

    def view(self):
        self.canvas.delete("System_Coin")
        self.canvas.create_image(
            self.position[0],
            self.position[1],
            anchor="nw",
            image=self.image,
            tag="System_Coin"
        )

    def create_bool(self) -> bool:
        """
        ランダムでbool値を生成する
        """
        return random.random() > 0.5

    def toss(self):
        self.roll_count = random.randint(10, 20)
        if self.aff is not None:
            self.master.after_cancel(self.aff)
        self.roll()

    def roll(self):
        if self.roll_count % 2:
            img = self.head_image.copy()
        else:
            img = self.tail_image.copy()
        self.image = ImageTk.PhotoImage(img)
        self.view()
        self.roll_count -= 1
        if self.roll_count:
            self.aff = self.master.after(16, self.roll)
        else:
            self.master.after_cancel(self.aff)
            res = self.create_bool()
            if res:
                img = self.head_image.copy()
            else:
                img = self.tail_image.copy()
            self.image = ImageTk.PhotoImage(img)
            self.view()
            print("finish")


class Shuffle:
    def __init__(self, master: tk.Tk, canvas: tk.Canvas):
        self.master = master
        self.canvas = canvas
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0],
            Setting.data.card_size[1] + 10
        )
        self.image_data = Image.open("Misc/Shuffle.png").resize((Setting.data.card_size[0], Setting.data.card_size[0]))
        self.image = ImageTk.PhotoImage(self.image_data)
        self.aff = None
        self.angle = 0

    def position_update(self):
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0],
            Setting.data.card_size[1] + 10
        )
        self.view()

    def view(self):
        self.canvas.delete("System_Shuffle")
        self.canvas.create_image(
            self.position[0],
            self.position[1],
            anchor="nw",
            image=self.image,
            tag="System_Shuffle"
        )

    def shuffle(self):
        self.angle += 10
        if self.angle > 360:
            self.master.after_cancel(self.aff)
            self.aff = None
            self.angle = 0
        else:
            self.aff = self.master.after(8, self.shuffle)
        self.image = ImageTk.PhotoImage(self.image_data.rotate(self.angle))
        self.view()

    def shuffle_start(self):
        if self.aff is not None:
            self.master.after_cancel(self.aff)
            self.aff = None
            self.angle = 0
            self.image = ImageTk.PhotoImage(self.image_data.rotate(0))
            self.view()
        else:
            self.shuffle()



class CheckObject:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.flag = False
        self.object_name: str
        self.true_image: Image.Image
        self.false_image: Image.Image
        self.position: tuple[int]
        self.image: ImageTk.PhotoImage

    def click(self):
        self.flag = not self.flag
        self.view()

    def position_update(self):
        pass

    def view(self):
        if self.flag:
            self.image = ImageTk.PhotoImage(self.true_image)
        else:
            self.image = ImageTk.PhotoImage(self.false_image)
        self.canvas.delete(f"System_{self.object_name}")
        self.canvas.create_image(
            self.position[0],
            self.position[1],
            anchor="nw",
            image=self.image,
            tag=f"System_{self.object_name}"
        )

    def reset(self):
        self.flag = False
        self.view()


class VstarObject(CheckObject):
    def __init__(self, canvas) -> None:
        super().__init__(canvas)
        self.object_name = "Vstar"
        self.true_image = Image.open("Misc/Vstar_check.png").resize((Setting.data.card_size[1], Setting.data.card_size[1] //2))
        self.false_image = Image.open("Misc/Vstar.png").resize(self.true_image.size)
        self.image = ImageTk.PhotoImage(self.false_image)
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            10
        )

    def position_update(self):
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            10
        )
        self.view()

class EnergyObject(CheckObject):
    def __init__(self, canvas) -> None:
        super().__init__(canvas)
        self.object_name = "Energy"
        self.true_image = Setting.container.create_text("ENERGY", "red")
        self.false_image = Setting.container.create_text("ENERGY", "white")
        self.image = ImageTk.PhotoImage(self.false_image)
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            Setting.data.card_size[0] - 20
        )

    def position_update(self):
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            Setting.data.card_size[0] - 20
        )
        self.view()


class SupportObject(CheckObject):
    def __init__(self, canvas) -> None:
        super().__init__(canvas)
        self.object_name = "Support"
        self.true_image = Setting.container.create_text("SUPPORT", "red")
        self.false_image = Setting.container.create_text("SUPPORT", "white")
        self.image = ImageTk.PhotoImage(self.false_image)
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            Setting.data.card_size[0] + 20
        )

    def position_update(self):
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            Setting.data.card_size[0] + 20
        )
        self.view()



class RetreatObject(CheckObject):
    def __init__(self, canvas) -> None:
        super().__init__(canvas)
        self.object_name = "Retreat"
        self.true_image = Setting.container.create_text("RETREAT", "red")
        self.false_image = Setting.container.create_text("RETREAT", "white")
        self.image = ImageTk.PhotoImage(self.false_image)
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            Setting.data.card_size[0] + 60
        )

    def position_update(self):
        self.position = (
            Setting.data.window_size[0] - Setting.data.card_size[0] - Setting.data.card_size[1] - 10,
            Setting.data.card_size[0] + 60
        )
        self.view()

class CardViewWindow:
    """
    複数windowを表示しないためにObject内の変数としてクラスを保持しておく
    """
    def __init__(self):
        self.window: tk.Toplevel = None
        self.canvas: tk.Canvas
        self.image: ImageTk.PhotoImage

    def close(self):
        if self.window is not None:
            self.window.destroy()
            self.window = None

    def window_create(self, card: Card):
        if self.window is not None:
            self.close()
        image = Setting.container.get(card.card_id)
        self.image = ImageTk.PhotoImage(image)
        self.window = tk.Toplevel()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.title(card.name)
        self.window.geometry(f"{image.size[0]}x{image.size[1]}")
        canvas = tk.Canvas(
            self.window,
            width=image.size[0],
            height=image.size[1],
            bg=Setting.data.canvas_color
        )
        canvas.pack()
        canvas.create_image(
            0, 0,
            anchor = "nw",
            image = self.image,
            tag=card.id
        )

card_view_window = CardViewWindow()

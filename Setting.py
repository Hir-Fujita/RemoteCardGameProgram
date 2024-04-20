#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import os
import requests
import re
from bs4 import BeautifulSoup
import io
from PIL import Image, ImageTk, ImageDraw, ImageFont

debug = False

class Setting:
    def __init__(self):
        self.window_size: tuple[int] = None
        self.window_position :tuple[int] = None
        self.card_size: tuple[int] = None
        self.canvas_color: str = None
        self.enemy_canvas_color: str = None
        self.text_font_path: str = "Misc/meiryo.ttc"
        self.number_font_path: str = "Misc/Molot.ttc"
        self.ini = configparser.SafeConfigParser()

    def setting_load(self, section: str):
        """
        iniファイルから設定を読み込む
        section引数にデフォルトかユーザー設定を指定する
        """
        self.ini.read("Setting.ini")
        self.window_size = (
            int(self.ini.get(section, "WINDOW_WIDTH")),
            int(self.ini.get(section, "WINDOW_HEIGHT"))
            )
        self.window_position = (
            int(self.ini.get(section, "WINDOW_POSITION_X")),
            int(self.ini.get(section, "WINDOW_POSITION_Y"))
        )
        self.enemy_window_position = (
            int(self.ini.get(section, "ENEMY_WINDOW_POSITION_X")),
            int(self.ini.get(section, "ENEMY_WINDOW_POSITION_Y"))
        )
        self.card_size = (
            int(self.ini.get(section, "CARD_WIDTH")),
            int(self.ini.get(section, "CARD_HEIGHT"))
        )
        self.canvas_color: str = self.ini.get(section, "CANVAS_COLOR")
        self.enemy_canvas_color: str = self.ini.get(section, "ENEMY_CANVAS_COLOR")

    def default_ini(self):
        print("初期設定に戻します")
        self.setting_load("DEFAULT")
        self.save_ini()

    def save_ini(self):
        self.ini.set("USER_SETTING", "CARD_WIDTH", str(self.card_size[0]))
        self.ini.set("USER_SETTING", "CARD_HEIGHT", str(self.card_size[1]))
        self.ini.set("USER_SETTING", "WINDOW_WIDTH", str(self.window_size[0]))
        self.ini.set("USER_SETTING", "WINDOW_HEIGHT", str(self.window_size[1]))
        self.ini.set("USER_SETTING", "WINDOW_POSITION_X", str(self.window_position[0]))
        self.ini.set("USER_SETTING", "WINDOW_POSITION_Y", str(self.window_position[1]))
        self.ini.set("USER_SETTING", "ENEMY_WINDOW_POSITION_X", str(self.enemy_window_position[0]))
        self.ini.set("USER_SETTING", "ENEMY_WINDOW_POSITION_Y", str(self.enemy_window_position[1]))
        self.ini.set("USER_SETTING", "CANVAS_COLOR", self.canvas_color)
        self.ini.set("USER_SETTING", "ENEMY_CANVAS_COLOR", self.enemy_canvas_color)
        with open("Setting.ini", "w") as f:
            self.ini.write(f)

    def window_size_set(self, enemy_flag: bool, data: tuple[str]):
        self.window_size = (int(data[0]), int(data[1]))
        if not enemy_flag:
            self.window_position = (int(data[2]), int(data[3]))
        else:
            self.enemy_window_position = (int(data[2]), int(data[3]))

    def get_geometry(self, enemy_flag: bool, object_name: str) -> str:
        """
        geometry取得
        """
        window_size_x = self.window_size[0]
        window_size_y = self.window_size[1]
        position_x = self.window_position[0]
        position_y = self.window_position[1]
        if enemy_flag:
            position_x = self.enemy_window_position[0]
            position_y = self.enemy_window_position[1]
        if object_name == "Field":
            pass
        elif object_name == "Hand":
            window_size_y = self.card_size[1]
            position_y += self.window_size[1] + 50
        else:
            position_x += 50
            position_y += 50
            if object_name == "Deck":
                window_size_x = self.card_size[0] * 8
                window_size_y = self.card_size[1] * 4
            elif object_name == "Temp":
                window_size_x = self.card_size[0] * 7
                window_size_y = self.card_size[1]
            elif object_name == "Trash":
                window_size_x = self.card_size[0] * 8
                window_size_y = self.card_size[1] * 4
            elif object_name == "Side":
                window_size_x = self.card_size[0] * 6
                window_size_y = self.card_size[1]
            elif object_name == "Lost":
                window_size_x = self.card_size[0] * 8
                window_size_y = self.card_size[1] * 2
        return f"{window_size_x}x{window_size_y}+{position_x}+{position_y}"

    def get_window_size(self, object_name: str) -> tuple[int]:
        window_size_x = self.window_size[0]
        window_size_y = self.window_size[1]
        if object_name == "Field":
            pass
        elif object_name == "Hand":
            window_size_y = self.card_size[1]
        if object_name == "Deck":
            window_size_x = self.card_size[0] * 8
            window_size_y = self.card_size[1] * 4
        elif object_name == "Temp":
            window_size_x = self.card_size[0] * 7
            window_size_y = self.card_size[1]
        elif object_name == "Trash":
            window_size_x = self.card_size[0] * 8
            window_size_y = self.card_size[1] * 4
        elif object_name == "Side":
            window_size_x = self.card_size[0] * 6
            window_size_y = self.card_size[1]
        elif object_name == "Lost":
            window_size_x = self.card_size[0] * 8
            window_size_y = self.card_size[1] * 2
        return (window_size_x, window_size_y)

    def get_card_size(self) -> tuple[int]:
        return (self.card_size[0], self.card_size[1])

    def get_canvas_size(self, row: int, col: int) -> tuple[int]:
        x = (self.card_size[0] // 2) * (col +1)
        y = self.card_size[1] * row
        return (x, y)

    def get_canvas_color(self, flag: bool):
        if flag:
            return self.enemy_canvas_color
        else:
            return self.canvas_color



class ImageContainer:
    def __init__(self, data: Setting) -> None:
        self.data: Setting = data
        self.dic: dict[str, Image.Image] = {
            "System_Card": self.create_card_image("Misc/card.png"),
            "System_check": Image.open("Misc/check.png").convert("RGBA"),
            "System_doku": Image.open("Misc/doku.png").convert("RGBA"),
            "System_yakedo": Image.open("Misc/yakedo.png").convert("RGBA"),
            "System_nemuri": Image.open("Misc/nemuri.png").convert("RGBA"),
            "System_mahi": Image.open("Misc/mahi.png").convert("RGBA"),
            "System_konran": Image.open("Misc/konran.png").convert("RGBA"),
        }

    def get(self, card_id: str) -> Image.Image:
        if not card_id in self.dic.keys():
            if not card_id in os.listdir("Card"):
                print(f"create ImageFile {card_id}")
                r = requests.get(f"https://www.pokemon-card.com/card-search/details.php/card/{card_id}")
                soup = BeautifulSoup(r.text, "html.parser")
                name = re.findall(r'<h1 class="Heading1 mt20">(.*)</h1>', str(soup))[0]
                category = re.findall(r'<h2 class="mt20">(.*)</h2>', str(soup))[0]
                if category == "ワザ" or category == "特性":
                    category = "ポケモン"
                find_start = r'class="fit" src="'
                find_end = r'\d*"/>'
                image_url = re.findall(rf"{find_start}(.*){find_end}", str(soup))[0]
                image = Image.open(
                    io.BytesIO(requests.get(f"https://www.pokemon-card.com{image_url}").content)
                    )
                image = image.resize((500, 700))
                image = image.convert("RGB")
                os.makedirs(f"Card/{card_id}")
                image.save(f"Card/{card_id}/{category}_{name}.jpg", quality=95)
            print(f"Loading Image {card_id}")
            filename = os.listdir(f"Card/{card_id}")[0]
            self.dic[card_id] = self.create_card_image(f"Card/{card_id}/{filename}")
        return self.dic[card_id]

    def get_tk(self, card_id, size: tuple[int]) -> ImageTk.PhotoImage:
        image = self.get(card_id).resize(size)
        return ImageTk.PhotoImage(image)

    def create_card_image(self, path) -> Image.Image:
        """
        実際のカードのように四隅にα値を追加する
        """
        image = Image.open(path)
        mask = Image.open("Misc/mask.png").resize(image.size).convert('L')
        image.putalpha(mask)
        return image

    def create_deck_image(self, deck_list: list[str], size: tuple[int]) -> ImageTk.PhotoImage:
        image = Image.new("RGB", (size[0]*12, size[1]*5), "gray")
        if len(deck_list) == 60:
            column = 0
            row = 0
            for card_id in deck_list:
                img = self.get(card_id).resize(size)
                image.paste(img, (size[0]*column, size[1]*row))
                column += 1
                if column > 11:
                    column = 0
                    row += 1
        return ImageTk.PhotoImage(image)

    def create_system_image(self, text: str, length: int, color: str) -> ImageTk.PhotoImage:
        image = self.get("System_Card").resize(self.data.get_card_size())
        image.putalpha(200)
        draw = ImageDraw.Draw(image)
        draw.rectangle(
            [
                (0, 0),
                (image.size[0]-1, image.size[1]-1)
            ],
            outline="black",
            width=4
        )
        text_image = self.create_text(text, color)
        image.paste(
            text_image,
            (image.size[0] // 2 - text_image.size[0] // 2, 10),
            mask=text_image
        )
        length_image = self.create_text(length, "white")
        image.paste(
            length_image,
            (
                image.size[0] // 2 - length_image.size[0] // 2,
                image.size[1] // 2 - length_image.size[1] // 2
            ),
            mask=length_image
        )
        return ImageTk.PhotoImage(image)

    def create_text(self, text: str | int, color: str) -> Image.Image:
        if isinstance(text, str):
            font = ImageFont.truetype("Misc/Molot.ttf", self.data.card_size[0] // 3)
        else:
            font = ImageFont.truetype("Misc/Molot.ttf", self.data.card_size[0] // 2)
        image = Image.new("RGBA", (300, 300))
        draw = ImageDraw.Draw(image)
        draw.text(
            (5, 5),
            str(text),
            font=font,
            fill=color,
            stroke_width=4,
            stroke_fill="black"
        )
        return image.crop(image.split()[-1].getbbox())

def card_data_check():
    if not os.path.isdir("Card"):
        os.makedirs("Card")
    if not os.path.isdir("Deck"):
        os.makedirs("Deck")
    print("Cradフォルダの適合性確認")
    data_list = os.listdir("Card")
    count = 0
    for data in data_list:
        check = os.listdir(f"Card/{data}")
        if len(check) != 1:
            for c in check:
                os.remove(f"Card/{data}/{c}")
            os.rmdir(f"Card/{data}")
        count += 1
        print(f"{count} / {len(data_list)}")

def create_deckid_list(deck_id: str) -> list[str]:
    """
    ポケモンカード公式デッキIDからカードのIDを60枚分出力する
    """
    r = requests.get(f"https://www.pokemon-card.com/deck/result.html/deckID/{deck_id}/")
    soup = BeautifulSoup(r.text,"html.parser")
    find_start = r'"deck_.*" type="hidden" value="'
    find_end = r'\d*">'
    card_list = []
    for c in re.findall(rf'{find_start}(.*){find_end}',str(soup)):
        if c and isinstance(c, str):
            for data in c.split("-"):
                card_id, length, _ = map(str, data.split("_"))
                for _ in range(int(length)):
                    card_list.append(card_id)
    if len(card_list) == 60:
        return card_list
    else:
        return []

def get_reverse_color(color: str):
    color = color.replace("#", "")
    r, g, b = map(lambda x: int(x, 16), (color[0]+color[1], color[2]+color[3], color[4]+color[5]))
    rr, gg, bb = map(lambda x: format(255-x, "02x"), (r, g, b))
    return f"#{rr}{gg}{bb}"


data = Setting()
container = ImageContainer(data)
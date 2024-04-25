#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
アプリケーション起動用ファイル
"""

import Setting
import Application

NAME = "RemoteCardGameProgram"
VERSITON = "0.2"

def main():
    """
    Application起動
    """
    Setting.card_data_check()
    Setting.data.setting_load("USER_SETTING")
    Application.run(NAME, VERSITON)

if __name__ == "__main__":
    main()

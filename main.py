import sys
import keyboard
import pygame
import json

from threading import Thread
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QApplication, QLabel

# 读取数据文件
piano_key = json.load(open('JSON/piano_key.json', 'r', encoding='utf8'))


# 主窗口
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # 获取桌面尺寸
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        # 设置主窗口比例
        main_width = int(screen_rect.width() * 0.9)
        main_height = int(screen_rect.height() * 0.4)
        self.resize(main_width, main_height)
        # 固定窗口大小
        self.setFixedSize(self.width(), self.height())
        # 窗口居中
        self.move((screen_rect.width() - main_width) // 2, (screen_rect.height() - main_height) // 2)

        # 状态栏和标题
        self.status = self.statusBar()
        self.status.showMessage('不是88键买不起，而是赛博钢琴更有性价比！')
        self.setWindowTitle('赛博钢琴')

        # 创建容器存放琴键
        container = QWidget(self)
        self.setCentralWidget(container)

        # 遍历查询黑白键的数量，用于计算每个键宽度
        black_key_num = sum(1 for key in piano_key if 's' in key['sound'])
        white_key_num = len(piano_key) - black_key_num

        self.buttons = []
        button_width = main_width / white_key_num
        white_key_index = 0

        for index, key in enumerate(piano_key):
            button = QPushButton(container)
            button.setObjectName(key['sound'])
            button.clicked.connect(self.on_button_clicked)
            self.set_button_style(button, 's' in key['sound'])

            if 's' in key['sound']:
                button.resize(button_width * 0.8, main_height * 0.6)
                button.move((white_key_index - 1) * button_width + button_width * 0.6, 0)
                button.raise_()
            else:
                button.resize(button_width, main_height)
                button.move(white_key_index * button_width, 0)
                button.lower()
                white_key_index += 1

                self.add_label(container, key, white_key_index, button_width, main_height)

            self.buttons.append(button)

    # 匹配并添加label
    @staticmethod
    def add_label(container, key, white_key_index, button_width, main_height):
        label_map = {
            'a': '6', 'A': '6',
            'b': '7', 'B': '7',
            'c': '1', 'C': '1',
            'd': '2', 'D': '2',
            'e': '3', 'E': '3',
            'f': '4', 'F': '4',
            'g': '5', 'G': '5'
        }
        label_text = label_map.get(key['sound'][0], '') + f"\n{key['key']}"
        label = QLabel(label_text, container)
        label.move(white_key_index * button_width - button_width * 0.5, main_height - 60)

    # 初始化黑白键样式
    @staticmethod
    def set_button_style(button, is_black_key):
        if is_black_key:
            button.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: white;
                    border: 1px solid black;
                    padding: 0;
                    margin: 0;
                    text-align: center;
                }
                QPushButton::hover {
                    background-color: lightgray;
                }
                QPushButton:pressed {
                    background-color: gray;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: black;
                    border: 1px solid black;
                    padding: 0;
                    margin: 0;
                    text-align: center;
                }
                QPushButton::hover {
                    background-color: lightgray;
                }
                QPushButton:pressed {
                    background-color: gray;
                }
            """)

    # 键盘按下改变样式
    def change_button_color(self, index):
        self.buttons[index].setStyleSheet("background-color: gray;")

    # 抬起后恢复样式
    def release_button_color(self, index, is_black_key):
        self.set_button_style(self.buttons[index], is_black_key)

    # 鼠标点击播放
    def on_button_clicked(self):
        button = self.sender()
        pygame.mixer.Sound('MP3/' + button.objectName()).play()


# 初始化 PyQt 应用
app = QApplication(sys.argv)
# 实例化窗口
form = MainWindow()


# 键盘按下触发
def on_action(event):
    try:
        sound = next(item['sound'] for item in piano_key if item['key'] == event.name)
        index = next(index for index, item in enumerate(piano_key) if item['key'] == event.name)

        if event.event_type == keyboard.KEY_DOWN:
            pygame.mixer.Sound('MP3/' + sound).play()
            form.change_button_color(index)
        elif event.event_type == keyboard.KEY_UP:
            form.release_button_color(index, 's' in sound)

    except StopIteration:
        print(f"No sound file found for key: {event.name}")


# 键盘监听
def start_keyboard_listener():
    keyboard.hook(on_action)
    keyboard.wait()


def main():
    # 显示窗口
    form.show()
    # 初始化 Pygame 混音器
    pygame.mixer.init()
    # 启动键盘监听线程
    listener_thread = Thread(target=start_keyboard_listener)
    listener_thread.daemon = True
    listener_thread.start()
    # 进入事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

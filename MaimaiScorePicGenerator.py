import sys
import os
from typing import Literal
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QListWidget,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QLabel,
    QComboBox,
    QHBoxLayout,
    QCheckBox,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import requests
import random
import argparse


class DownloadThread(QThread):
    download_complete: pyqtSignal = pyqtSignal(
        str, str
    )  # 发送 (file_name, 保存的文件路径)
    file_name: str
    url: str

    def __init__(self, file_name: str, url: str):
        super().__init__()
        self.file_name = file_name
        self.url = url

    def run(self):
        """线程任务：下载文件"""
        response: requests.Response = requests.get(self.url)
        if response.status_code == 200:
            save_path = "bg.png"
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.download_complete.emit(self.file_name, save_path)  # 发送信号
        else:
            print(f"下载失败，状态码: {response.status_code}")


class MaimaiScorePicGeneratorApp(QWidget):
    song_name: str = ""
    show_first: bool = False
    show_second: bool = False
    score: float = 0.0

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("舞萌DX成绩图生成器")
        self.setGeometry(100, 100, 600, 300)
        main_layout = QHBoxLayout()  # 主水平布局

        # 右侧搜索框 + 列表 + 刷新按钮的布局
        right_layout = QVBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入关键字搜索...")
        self.search_box.textChanged.connect(self.filter_list)
        right_layout.addWidget(self.search_box)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        right_layout.addWidget(self.list_widget)

        self.refresh_button = QPushButton("刷新文件列表")
        self.refresh_button.clicked.connect(self.list_songs)
        right_layout.addWidget(self.refresh_button)

        # 左侧表单布局
        left_layout = QVBoxLayout()
        self.score_input = QLineEdit(self)
        self.score_input.setPlaceholderText("请输入成绩 (例如 100.1)")
        left_layout.addWidget(QLabel("达成率"))
        left_layout.addWidget(self.score_input)
        self.score_input.textChanged.connect(self.on_score_change)

        self.dx_rank_combo = QComboBox(self)
        self.dx_rank_combo.addItems(["1", "2", "3", "4", "5"])
        left_layout.addWidget(QLabel("DX 分数等级"))
        left_layout.addWidget(self.dx_rank_combo)

        self.difficulty_combo = QComboBox(self)
        self.difficulty_combo.addItems(["master", "remaster", "expert", "utage"])
        left_layout.addWidget(QLabel("难度"))
        left_layout.addWidget(self.difficulty_combo)

        self.song_type_combo = QComboBox(self)
        self.song_type_combo.addItems(["dx", "standard"])
        left_layout.addWidget(QLabel("谱面类型"))
        left_layout.addWidget(self.song_type_combo)

        self.play_log_check_first = QCheckBox("显示完成标", self)
        self.play_log_check_second = QCheckBox("显示Sync标", self)
        self.play_log_combo_first = QComboBox(self)
        self.play_log_combo_first.addItems(["applus", "ap", "fcplus", "fc"])
        self.play_log_combo_first.hide()
        self.play_log_combo_second = QComboBox(self)
        self.play_log_combo_second.addItems(["fdxplus", "fdx", "fsplus", "fs", "sync"])
        self.play_log_combo_second.hide()
        left_layout.addWidget(QLabel("Play Log"))
        left_layout.addWidget(self.play_log_check_first)
        left_layout.addWidget(self.play_log_combo_first)
        left_layout.addWidget(self.play_log_check_second)
        left_layout.addWidget(self.play_log_combo_second)
        self.play_log_check_first.stateChanged.connect(self.on_check_box_first_change)
        self.play_log_check_second.stateChanged.connect(self.on_check_box_second_change)
        self.play_log_check_first.setChecked(True)
        self.play_log_check_second.setChecked(True)

        # 提交按钮
        self.submit_button = QPushButton("提交", self)
        self.submit_button.clicked.connect(self.on_submit)
        left_layout.addWidget(self.submit_button)

        # 将左右两部分添加到主布局
        main_layout.addLayout(left_layout)  # 左侧是输入部分
        main_layout.addLayout(right_layout)  # 右侧是列表部分

        self.setLayout(main_layout)
        self.list_songs()
        self.set_random_icon()

    def get_all_items(self, list_widget: QListWidget) -> list[str]:
        # 获取 QListWidget 中的所有 items
        items = []
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            assert item is not None
            items.append(item.text())
        return items

    def filter_list(self):
        keyword: str = self.search_box.text().lower()
        if keyword == "":
            self.list_songs()
            return
        filtered_files: list[str] = [
            name
            for name in self.get_all_items(self.list_widget)
            if keyword in name.lower()
        ]
        self.update_list(filtered_files)

    def update_list(self, items):
        self.list_widget.clear()
        for item in items:
            self.list_widget.addItem(item)

    def list_songs(self):
        self.list_widget.clear()
        songs: list[str] = os.listdir("bgs")
        for song in songs:
            self.list_widget.addItem(Path(song).stem)

    def on_item_clicked(self, item):
        self.song_name = item.text()
        self.setWindowTitle("舞萌DX成绩图生成器: " + self.song_name)

    def on_submit(self):
        if not self.song_name:
            QMessageBox.warning(self, "错误", "请先选择歌曲")
            return

        generate_score_image(
            song_name=self.song_name,
            score=self.score,
            difficulty=self.difficulty_combo.currentText(),
            dx_rank=self.dx_rank_combo.currentText(),
            song_type=self.song_type_combo.currentText(),
            show_first=self.show_first,
            first_log=self.play_log_combo_first.currentText()
            if self.show_first
            else None,
            show_second=self.show_second,
            second_log=self.play_log_combo_second.currentText()
            if self.show_second
            else None,
        )

        QMessageBox.information(self, "完成", "图片已保存为output.png和output43.png")

    def on_score_change(self, score: str):
        try:
            self.score = float(score)
            if self.score == 101.0:
                self.play_log_combo_first.setCurrentText("applus")
            else:
                self.play_log_combo_first.setCurrentText("ap")
        except ValueError:
            QMessageBox.warning(self, "错误", "请输入正确的数字")

    def on_check_box_first_change(self, state: bool):
        self.show_first = state
        if state:
            self.play_log_combo_first.show()
        else:
            self.play_log_combo_first.hide()

    def on_check_box_second_change(self, state: bool):
        self.show_second = state
        if state:
            self.play_log_combo_second.show()
        else:
            self.play_log_combo_second.hide()

    def set_random_icon(self):
        files = [
            f for f in os.listdir("bgs/") if os.path.isfile(os.path.join("bgs/", f))
        ]
        self.setWindowIcon(QIcon(f"bgs/{random.choice(files)}"))

    def draw_text_with_outline(
        self,
        draw: ImageDraw.ImageDraw,
        position: tuple[float, float],
        text: str,
        font: ImageFont.FreeTypeFont,
        text_color: tuple[int, int, int] = (255, 255, 255),
        outline_color: tuple[int, int, int] = (0, 0, 0),
        offsets: list[tuple[int, int]] = [(-2, -2), (-2, 2), (2, -2), (2, 2)],
    ):
        for dx, dy in offsets:
            draw.text(
                (position[0] + dx, position[1] + dy),
                text,
                font=font,
                fill=outline_color,
            )
        draw.text(position, text, font=font, fill=text_color)


def generate_score_image(
    song_name: str,
    score: float,
    difficulty: Literal["master", "remaster", "expert", "utage"] | str,
    dx_rank: Literal["1", "2", "3", "4", "5"] | str,
    song_type: Literal["dx", "standard"] | str,
    show_first: bool,
    first_log: Literal["applus", "ap", "fcplus", "fc"] | str | None,
    show_second: bool,
    second_log: Literal["fdxplus", "fdx", "fsplus", "fs", "sync"] | str | None,
    output_path: str = "output.png",
    output_43_path: str = "output43.png",
):
    """通用图片生成函数"""
    # 验证背景图片存在
    bg_path = Path(f"bgs/{song_name}.png")
    if not bg_path.exists():
        bg_path = Path(f"bgs/{song_name}.jpg")
        if not bg_path.exists():
            raise FileNotFoundError(f"背景图片 {bg_path} 不存在")

    # 画布尺寸
    canvas_width = 1280
    canvas_height = 720

    if difficulty == "utage":
        background_color = (255, 111, 253, 255)
    elif difficulty == "expert":
        background_color = (255, 129, 141, 255)
    elif difficulty == "remaster":
        background_color = (218, 90, 255, 255)
    else:
        background_color = (130, 100, 200, 255)

    # 创建画布
    canvas = Image.new("RGBA", (canvas_width, canvas_height), background_color)
    canvas43 = Image.new("RGBA", (canvas_width, 960), background_color)
    draw = ImageDraw.Draw(canvas)

    # 加载曲绘
    original_img = Image.open(bg_path).convert("RGBA")
    img_width = int(1.3 * canvas_width // 3)
    img_height = int(img_width * original_img.height / original_img.width)
    original_img = original_img.resize(
        (img_width, img_height), Image.Resampling.LANCZOS
    )
    canvas.paste(original_img, (30, canvas_height // 5))

    # 画标题栏
    title_bar_color = (255, 255, 255)
    title_bar_height = 100
    draw.rounded_rectangle(
        [(20, 20), (canvas_width - 20, 20 + title_bar_height)],
        fill=title_bar_color,
        radius=10,
    )

    # 画难度
    diff = Image.open(f"assets/diff_{difficulty}.png").convert("RGBA")
    resized_diff = diff.resize((diff.width * 5 // 2, diff.height * 5 // 2))
    canvas.paste(resized_diff, (30, 30), resized_diff)

    # 写歌名
    song_name_font = ImageFont.truetype("assets/SourceHanSans-Bold.otf", 50)
    draw.text((440, 35), song_name, font=song_name_font, fill=(0, 0, 0))

    # 画谱面类型
    type_img = Image.open(f"assets/music_{song_type}.png").convert("RGBA")
    resized_type = type_img.resize((type_img.width * 3 // 2, type_img.height * 3 // 2))
    canvas.paste(resized_type, (10, 130), resized_type)

    # 处理Play Log
    def paste_log(image_name, y_pos):
        if image_name:
            log_img = Image.open(f"assets/{image_name}.png").convert("RGBA")
            scaled_log = log_img.resize(
                (log_img.width * 5 // 2, log_img.height * 5 // 2)
            )
            canvas.paste(scaled_log, (600, y_pos), scaled_log)

    logs = []
    if show_first and first_log:
        logs.append((first_log, 350))
    if show_second and second_log:
        logs.append((second_log, 500 if show_first else 400))

    for log, y in logs:
        paste_log(log, y)

    # 画DX Star
    dx_star = Image.open(f"assets/music_icon_dxstar_{dx_rank}.png").convert("RGBA")
    resized_dx_star = dx_star.resize((105, 105))
    canvas.paste(resized_dx_star, (600, 150), resized_dx_star)

    # 画分数
    int_part = str(int(score))
    decimal_part = f"{score - int(score):.4f}"[1:] + "%"
    score_font = ImageFont.truetype("assets/NotoSansCJKBold.otf", 120)
    subscore_font = ImageFont.truetype("assets/NotoSansCJKBold.otf", 80)

    def draw_text_with_outline(position, text, font):
        offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dx, dy in offsets:
            draw.text(
                (position[0] + dx, position[1] + dy), text, font=font, fill=(0, 0, 0)
            )
        draw.text(position, text, font=font, fill=(255, 255, 255))

    # 分数布局
    int_bbox = score_font.getbbox(int_part)
    score_width = int_bbox[2] - int_bbox[0]
    score_position = (700, 200)
    sub_position = (
        700 + score_width,
        200 + (int_bbox[3] - int_bbox[1]) - subscore_font.getbbox(decimal_part)[3],
    )

    draw_text_with_outline(score_position, int_part, score_font)
    draw_text_with_outline(sub_position, decimal_part, subscore_font)

    # 画评级
    rank = (
        "sssplus"
        if score >= 100.5
        else "sss"
        if score >= 100
        else "ssplus"
        if score >= 99.5
        else "ss"
        if score >= 99
        else "splus"
        if score >= 98
        else "s"
        if score >= 97
        else "aaa"
        if score >= 94
        else "aa"
        if score >= 90
        else "a"
        if score >= 80
        else "bbb"
        if score >= 75
        else "bb"
        if score >= 70
        else "b"
        if score >= 60
        else "c"
        if score >= 50
        else "d"
    )
    ranking = Image.open(f"assets/{rank}.png").convert("RGBA")
    resized_rank = ranking.resize((ranking.width * 3 // 2, ranking.height * 3 // 2))
    canvas.paste(resized_rank, (900, 400), resized_rank)

    # 保存输出
    canvas43.paste(canvas, (0, 120), canvas)
    canvas.save(output_path)
    canvas43.save(output_43_path)


def parse_args():
    """命令行参数解析"""
    parser = argparse.ArgumentParser(description="舞萌DX成绩图生成器")
    parser.add_argument(
        "--song", required=True, help="歌曲名称（bgs目录中的文件名，不带后缀）"
    )
    parser.add_argument("--score", type=float, required=True, help="达成率（如100.1）")
    parser.add_argument(
        "--difficulty", required=True, choices=["master", "remaster", "expert", "utage"]
    )
    parser.add_argument("--dx-rank", required=True, choices=["1", "2", "3", "4", "5"])
    parser.add_argument("--song-type", required=True, choices=["dx", "standard"])
    parser.add_argument("--show-first", action="store_true", help="显示完成标")
    parser.add_argument("--first-log", choices=["applus", "ap", "fcplus", "fc"])
    parser.add_argument("--show-second", action="store_true", help="显示Sync标")
    parser.add_argument(
        "--second-log", choices=["fdxplus", "fdx", "fsplus", "fs", "sync"]
    )
    parser.add_argument("--output", default="output.png", help="输出文件路径")
    parser.add_argument("--output43", default="output43.png", help="4:3比例输出路径")

    args = parser.parse_args()

    # 参数验证
    if args.show_first and not args.first_log:
        parser.error("--show-first需要配合--first-log使用")
    if args.show_second and not args.second_log:
        parser.error("--show-second需要配合--second-log使用")

    return args


if __name__ == "__main__":
    # 命令行模式
    if len(sys.argv) > 1:
        args = parse_args()
        try:
            generate_score_image(
                song_name=args.song,
                score=args.score,
                difficulty=args.difficulty,
                dx_rank=args.dx_rank,
                song_type=args.song_type,
                show_first=args.show_first,
                first_log=args.first_log,
                show_second=args.show_second,
                second_log=args.second_log,
                output_path=args.output,
                output_43_path=args.output43,
            )
            print(f"图片已成功生成：{args.output}")
            if args.output43:
                print(f"4:3比例图片已生成：{args.output43}")
        except Exception as e:
            print(f"生成失败：{str(e)}")
            sys.exit(1)

    # GUI模式
    else:
        app = QApplication(sys.argv)
        window = MaimaiScorePicGeneratorApp()
        window.show()
        sys.exit(app.exec())

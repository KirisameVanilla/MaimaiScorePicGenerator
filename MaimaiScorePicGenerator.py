from codecs import strict_errors
import sys
import os
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QMessageBox, QLabel, QComboBox, QHBoxLayout
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import requests
import random

class DownloadThread(QThread):
    download_complete: pyqtSignal = pyqtSignal(str, str)  # 发送 (file_name, 保存的文件路径)
    file_name: str
    url: str

    def __init__(self, file_name: str, url: str):
        super().__init__()
        self.file_name = file_name
        self.url = url

    def run(self):
        """ 线程任务：下载文件 """
        response: requests.Response = requests.get(self.url)
        if response.status_code == 200:
            save_path = "bg.png"
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.download_complete.emit(self.file_name, save_path)  # 发送信号
        else:
            print(f"下载失败，状态码: {response.status_code}")

class MaimaiScorePicGeneratorApp(QWidget):
    name_to_download: dict[str, str] = {}
    file_name: str = ""

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
        self.difficulty_combo.addItems(["master", "remaster", "expert"])
        left_layout.addWidget(QLabel("难度"))
        left_layout.addWidget(self.difficulty_combo)

        self.song_type_combo = QComboBox(self)
        self.song_type_combo.addItems(["dx", "standard"])
        left_layout.addWidget(QLabel("谱面类型"))
        left_layout.addWidget(self.song_type_combo)

        self.play_log_combo = QComboBox(self)
        self.play_log_combo.addItems(["applus", "ap", "fcplus", "fc"])
        left_layout.addWidget(QLabel("Play Log"))
        left_layout.addWidget(self.play_log_combo)

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

    def filter_list(self):
        keyword: str = self.search_box.text().lower()
        if keyword == "":
            self.list_songs()
            return
        filtered_files: list[str] = [name for name in self.name_to_download.keys() if keyword in name.lower()]
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
            self.name_to_download[Path(song).stem] = f"bgs/{song}"

    def on_item_clicked(self, item):
        self.file_name = item.text()
        self.setWindowTitle("舞萌DX成绩图生成器: " + self.file_name)

    def generate_pic(self, song_name: str):
        # 画布尺寸 (16:9)
        canvas_width = 1280
        canvas_height = 720
        background_color: tuple[int, ...] = (130, 100, 200, 255)

        # 创建画布
        canvas: Image.Image = Image.new("RGBA", (canvas_width, canvas_height), background_color)
        canvas43: Image.Image = Image.new("RGBA", (canvas_width, 960), background_color)
        draw: ImageDraw.ImageDraw = ImageDraw.Draw(canvas)

        # 加载曲绘并缩放放置在左侧
        original_img: Image.Image = Image.open(self.name_to_download[song_name]).convert("RGBA")
        img_width: int = (int)(1.3 * canvas_width) // 3
        img_height = int(img_width * original_img.height / original_img.width)
        original_img = original_img.resize((img_width, img_height), Image.Resampling.LANCZOS)
        canvas.paste(original_img, (30, canvas_height // 5))

        # 画标题栏
        title_bar_color: tuple[int, ...] = (255, 255, 255)
        title_bar_height = 100
        draw.rounded_rectangle([(20, 20), (canvas_width - 20, 20 + title_bar_height)], fill=title_bar_color, radius=10)

        # 画难度
        diff: Image.Image = Image.open(f"assets\\diff_{self.difficulty_combo.currentText()}.png").convert("RGBA")
        resized_diff: Image.Image = diff.resize((diff.width * 5 // 2, diff.height * 5 // 2))
        canvas.paste(resized_diff, (30, 30),resized_diff)

        # 写歌名
        song_name_font: ImageFont.FreeTypeFont = ImageFont.truetype("assets\\SourceHanSans-Bold.otf", 50)
        song_name_color: tuple[int, ...] = (0, 0, 0)
        song_name_position: tuple[int, ...] = (440, 35)
        draw.text(song_name_position, song_name, font=song_name_font, fill=song_name_color)

        # 画DX/标准
        type: Image.Image = Image.open(f"assets\\music_{self.song_type_combo.currentText()}.png").convert("RGBA")
        resized_type: Image.Image = type.resize((type.width * 3 // 2, type.height * 3 // 2))
        canvas.paste(resized_type, (10, 130),resized_type)

        # 画Play Log
        play_log_image: Image.Image = Image.open(f"assets\\{self.play_log_combo.currentText()}.png").convert("RGBA")
        resized_play_log_image = play_log_image.resize((play_log_image.width * 5 // 2, play_log_image.height * 5 // 2))
        canvas.paste(resized_play_log_image, (600, 400),resized_play_log_image)

        # 画 DX Star
        dx_star: Image.Image = Image.open(f"assets\\music_icon_dxstar_{self.dx_rank_combo.currentText()}.png").convert("RGBA")
        resized_dx_star: Image.Image = dx_star.resize((105, 105))
        canvas.paste(resized_dx_star, (600, 150), resized_dx_star)

        # 画分数
        int_part = str(int(self.score))
        decimal_part: str = f"{self.score - int(self.score):.4f}"[1:] + "%"
        score_font: ImageFont.FreeTypeFont = ImageFont.truetype("assets\\NotoSansCJKBold.otf", 120)
        subscore_font: ImageFont.FreeTypeFont = ImageFont.truetype("assets\\NotoSansCJKBold.otf", 80)

        score_position: tuple[int, ...] = (700, 200)
        int_part_bbox = score_font.getbbox(int_part)
        score_width: float = int_part_bbox[2] - int_part_bbox[0]
        score_height: float = int_part_bbox[3] - int_part_bbox[1]
        subscore_height: float = subscore_font.getbbox(decimal_part)[3] - subscore_font.getbbox(decimal_part)[1]
        subscore_position: tuple[float, float] = (700 + score_width, 200 + score_height-subscore_height)

        self.draw_text_with_outline(draw, score_position, int_part, score_font)
        self.draw_text_with_outline(draw, subscore_position, decimal_part, subscore_font)

        # 画评级
        rank = "sssplus" if self.score >= 100.5 else "sss" if self.score >= 100 else "ssplus" if self.score >= 99.5 else "ss" if self.score >= 99 else "splus" if self.score >= 98 else "s" if self.score >= 97 else "aaa" if self.score >= 94 else "aa" if self.score >= 90 else "a" if self.score >= 80 else "bbb" if self.score >= 75 else "bb" if self.score >= 70 else "b" if self.score >= 60 else "c" if self.score >= 50 else "d"
        ranking: Image.Image = Image.open(f"assets\\{rank}.png").convert("RGBA")
        resized_type = ranking.resize((ranking.width * 3 // 2, ranking.height * 3 // 2))
        canvas.paste(resized_type, (900, 400),resized_type)

        # 保存图片
        output_path = "output.png"
        output_path43 = "output43.png"
        canvas43.paste(canvas, (0, 120), canvas)
        canvas.save(output_path)
        canvas43.save(output_path43)
        canvas.show()
    
    def on_submit(self):
        if not self.file_name:
            return
        self.generate_pic(self.file_name)

    def on_score_change(self, score: str):
        self.score = float(score)
        if self.score == 101.0:
            self.play_log_combo.setCurrentText("applus")
    
    def set_random_icon(self):
        files = [f for f in os.listdir("bgs/") if os.path.isfile(os.path.join("bgs/", f))]
        self.setWindowIcon(QIcon(f"bgs/{random.choice(files)}"))
    
    def draw_text_with_outline(self, 
                               draw: ImageDraw.ImageDraw, 
                               position: tuple[float, float], 
                               text: str, 
                               font: ImageFont.FreeTypeFont, 
                               text_color: tuple[int, int, int] = (255, 255, 255), 
                               outline_color: tuple[int, int, int] = (0, 0, 0), 
                               offsets: list[tuple[int, int]] = [(-2, -2), (-2, 2), (2, -2), (2, 2)]):
        for dx, dy in offsets:
            draw.text((position[0] + dx, position[1] + dy), text, font=font, fill=outline_color)
        draw.text(position, text, font=font, fill=text_color)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MaimaiScorePicGeneratorApp()
    window.show()
    sys.exit(app.exec())

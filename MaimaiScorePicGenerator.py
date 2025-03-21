import sys
import os
from PIL import Image, ImageDraw, ImageFont
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QMessageBox, QLabel, QComboBox
from PyQt6.QtCore import QThread, pyqtSignal
from pathlib import Path
import requests

class DownloadThread(QThread):
    download_complete = pyqtSignal(str, str)  # 发送 (file_name, 保存的文件路径)

    def __init__(self, file_name, url):
        super().__init__()
        self.file_name = file_name
        self.url = url

    def run(self):
        """ 线程任务：下载文件 """
        response = requests.get(self.url)
        if response.status_code == 200:
            save_path = "bg.png"
            with open(save_path, "wb") as file:
                file.write(response.content)
            self.download_complete.emit(self.file_name, save_path)  # 发送信号
        else:
            print(f"下载失败，状态码: {response.status_code}")

class GitHubFileListApp(QWidget):
    name_to_download = {}
    file_name:str = ""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("舞萌DX成绩图生成器")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入关键字搜索...")
        self.search_box.textChanged.connect(self.filter_list)
        layout.addWidget(self.search_box)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        self.refresh_button = QPushButton("刷新文件列表")
        self.refresh_button.clicked.connect(self.list_songs)
        layout.addWidget(self.refresh_button)

        self.score_input = QLineEdit(self)
        self.score_input.setPlaceholderText("请输入成绩 (例如 100.1)")
        layout.addWidget(QLabel("达成率"))
        layout.addWidget(self.score_input)

        self.dx_rank_combo = QComboBox(self)
        self.dx_rank_combo.addItems(["1", "2", "3", "4", "5"])
        layout.addWidget(QLabel("DX 分数等级"))
        layout.addWidget(self.dx_rank_combo)

        self.difficulty_combo = QComboBox(self)
        self.difficulty_combo.addItems(["master", "remaster", "expert"])
        layout.addWidget(QLabel("难度"))
        layout.addWidget(self.difficulty_combo)

        self.song_type_combo = QComboBox(self)
        self.song_type_combo.addItems(["dx", "standard"])
        layout.addWidget(QLabel("谱面类型"))
        layout.addWidget(self.song_type_combo)

        self.finish_rank_combo = QComboBox(self)
        self.finish_rank_combo.addItems(["ap", "applus"])
        layout.addWidget(QLabel("AP/AP+"))
        layout.addWidget(self.finish_rank_combo)

        self.rank_combo = QComboBox(self)
        self.rank_combo.addItems(["sss", "sssplus"])
        layout.addWidget(QLabel("评级"))
        layout.addWidget(self.rank_combo)

         # 提交按钮
        self.submit_button = QPushButton("提交", self)
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.list_songs()

    def filter_list(self):
        keyword = self.search_box.text().lower()
        if keyword == "":
            self.list_songs()
            return
        filtered_files = [name for name in self.name_to_download.keys() if keyword in name.lower()]
        self.update_list(filtered_files)

    def update_list(self, items):
        self.list_widget.clear()
        for item in items:
            self.list_widget.addItem(item)

    def list_songs(self):
        self.list_widget.clear()
        songs = os.listdir("bgs")
        for song in songs:
            self.list_widget.addItem(Path(song).stem)
            self.name_to_download[Path(song).stem] = f"bgs/{song}"

    def on_item_clicked(self, item):
        self.file_name = item.text()

    def generate_pic(self, song_name: str):
        # 画布尺寸 (16:9)
        canvas_width = 1280
        canvas_height = 720
        background_color = (130, 100, 200, 255)  # 类似原图的紫色

        # 创建画布
        canvas = Image.new("RGBA", (canvas_width, canvas_height), background_color)
        canvas43 = Image.new("RGBA", (canvas_width, 960), background_color)
        draw = ImageDraw.Draw(canvas)

        # 加载曲绘并缩放放置在左侧
        original_img = Image.open(self.name_to_download[song_name]).convert("RGBA")
        img_width = (int)(1.3 * canvas_width) // 3
        img_height = int(img_width * original_img.height / original_img.width)
        original_img = original_img.resize((img_width, img_height), Image.Resampling.LANCZOS)
        canvas.paste(original_img, (30, canvas_height // 5))  # 左侧对齐

        # 画标题栏
        title_bar_color = (255, 255, 255)
        title_bar_height = 100
        draw.rounded_rectangle([(20, 20), (canvas_width - 20, 20 + title_bar_height)], fill=title_bar_color, radius=10)

        # 画难度
        diff = Image.open(f"assets\\diff_{self.difficulty_combo.currentText()}.png").convert("RGBA")
        resized_diff = diff.resize((diff.width * 5 // 2, diff.height * 5 // 2))
        canvas.paste(resized_diff, (30, 30),resized_diff)
        print(resized_diff.width, resized_diff.height)

        # 写歌名
        song_name_font = ImageFont.truetype("assets\\SourceHanSans-Bold.otf", 50)
        song_name_color = (0, 0, 0)
        song_name_position = (440, 35)
        draw.text(song_name_position, song_name, font=song_name_font, fill=song_name_color)

        # 画DX/标准
        type = Image.open(f"assets\\music_{self.song_type_combo.currentText()}.png").convert("RGBA")
        resized_type = type.resize((type.width * 3 // 2, type.height * 3 // 2))
        canvas.paste(resized_type, (10, 130),resized_type)

        # 画AP/AP+
        finish_rank_image = Image.open(f"assets\\{self.finish_rank_combo.currentText()}.png").convert("RGBA")
        resized_type = finish_rank_image.resize((finish_rank_image.width * 5 // 2, finish_rank_image.height * 5 // 2))
        canvas.paste(resized_type, (600, 400),resized_type)

        # 画评级
        ranking = Image.open(f"assets\\{self.rank_combo.currentText()}.png").convert("RGBA")
        resized_type = ranking.resize((ranking.width * 3 // 2, ranking.height * 3 // 2))
        canvas.paste(resized_type, (900, 400),resized_type)

        # 画 DX Star
        dx_star = Image.open(f"assets\\music_icon_dxstar_{self.dx_rank_combo.currentText()}.png").convert("RGBA")
        resized_dx_star = dx_star.resize((105, 105))
        canvas.paste(resized_dx_star, (600, 150), resized_dx_star)

        # 画分数
        score_float = float(self.score_input.text())
        int_part = str(int(score_float))
        decimal_part = f"{score_float - int(score_float):.4f}"[1:] + "%"
        score_font = ImageFont.truetype("assets\\NotoSansCJKBold.otf", 120)
        score_color = (255, 255, 255)
        outline_color = (0, 0, 0)
        offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        score_position = (700, 200)
        for dx, dy in offsets:
            draw.text((score_position[0] + dx, score_position[1] + dy), int_part, font=score_font, fill=outline_color)
        draw.text(score_position, int_part, font=score_font, fill=score_color)
        bbox = score_font.getbbox(int_part)
        score_width = bbox[2] - bbox[0]
        score_height = bbox[3] - bbox[1]

        subscore_font = ImageFont.truetype("assets\\NotoSansCJKBold.otf", 80)
        subscore_height = subscore_font.getbbox(decimal_part)[3] - subscore_font.getbbox(decimal_part)[1]
        suboffsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        subscore_position = (700+score_width, 200+score_height-subscore_height)
        for dx, dy in suboffsets:
            draw.text((subscore_position[0] + dx, subscore_position[1] + dy), decimal_part, font=subscore_font, fill=outline_color)
        draw.text(subscore_position, decimal_part, font=subscore_font, fill=score_color)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitHubFileListApp()
    window.show()
    sys.exit(app.exec())

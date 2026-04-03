import os
import sys
import threading
from functools import lru_cache
from typing import Literal
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import requests
import argparse


DXDATA_URL = "https://ghproxy.vanillaaaa.org/https://raw.githubusercontent.com/gekichumai/dxrating/refs/heads/main/packages/dxdata/dxdata.json"


class SimplifiedSong:
    def __init__(
        self,
        title: str,
        artist: str,
        image_name: str,
        types: list[str],
        searchAcronyms: list[str],
    ):
        self.title = title
        self.artist = artist
        self.image_name = image_name
        self.types = types
        self.searchAcronyms = searchAcronyms

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "artist": self.artist,
            "imageName": self.image_name,
            "types": self.types,
            "searchAcronyms": self.searchAcronyms,
        }

    def __repr__(self):
        return f"SimplifiedSong(title={self.title!r}, artist={self.artist!r}, types={self.types!r}, searchAcronyms={self.searchAcronyms})"

    def all_names(self) -> str:
        return " ".join([self.title, self.artist] + self.searchAcronyms).lower()

    def dimg_url(self) -> str:
        return f"https://shama.dxrating.net/images/cover/v2/{self.image_name}.jpg"


@lru_cache(maxsize=None)
def load_dxdata(url: str) -> dict:
    if not url:
        raise ValueError("DXDATA_URL 不能为空")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(f"无法解析 dxdata.json: {url}") from exc


def init_data() -> list[SimplifiedSong]:
    raw_data = load_dxdata(DXDATA_URL)
    songs_data = raw_data.get("songs")
    if not isinstance(songs_data, list):
        raise RuntimeError("dxdata.json 格式不正确，缺少 songs 列表")

    simplified_songs = []
    for song in songs_data:
        types = list(set(sheet["type"] for sheet in song.get("sheets", [])))
        for songtype in types:
            if songtype != "dx" and songtype != "std":
                types.remove(songtype)
        if len(types) == 0:
            types = ["dx"]
        simplified = SimplifiedSong(
            title=song.get("title", ""),
            artist=song.get("artist", ""),
            image_name=song.get("imageName", ""),
            types=types,
            searchAcronyms=song.get("searchAcronyms", []),
        )
        simplified_songs.append(simplified)

    return simplified_songs


def download_file(url: str, save_path: str) -> None:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response: requests.Response = requests.get(url, verify=False, timeout=30)
    response.raise_for_status()
    Path(save_path).write_bytes(response.content)


class MaimaiScorePicGeneratorApp:
    song_name: str = ""
    show_first: bool = False
    show_second: bool = False
    score: float = 0.0
    dxdata: list[SimplifiedSong]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("舞萌DX成绩图生成器")
        self.root.geometry("900x420")
        self.root.minsize(860, 380)

        self.search_var = tk.StringVar()
        self.score_var = tk.StringVar(value="100.0")
        self.dx_rank_var = tk.StringVar(value="1")
        self.difficulty_var = tk.StringVar(value="master")
        self.song_type_var = tk.StringVar(value="dx")
        self.play_log_first_var = tk.StringVar(value="applus")
        self.play_log_second_var = tk.StringVar(value="fdxplus")
        self.show_first_var = tk.BooleanVar(value=True)
        self.show_second_var = tk.BooleanVar(value=True)

        self.dxdata = init_data()
        self.all_titles: list[str] = []

        self._build_ui()
        self._sync_play_log_visibility()
        self.list_songs()

        self.search_var.trace_add("write", self.filter_list)
        self.score_var.trace_add("write", self.on_score_change)

    def _build_ui(self):
        main_frame = ttk.Frame(self.root, padding=12)
        main_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(main_frame)
        right_frame = ttk.Frame(main_frame)
        left_frame.pack(side="left", fill="y", padx=(0, 12))
        right_frame.pack(side="right", fill="both", expand=True)

        ttk.Label(left_frame, text="达成率").pack(anchor="w")
        self.score_input = ttk.Entry(left_frame, textvariable=self.score_var, width=28)
        self.score_input.pack(fill="x", pady=(0, 8))

        ttk.Label(left_frame, text="DX 分数等级").pack(anchor="w")
        self.dx_rank_combo = ttk.Combobox(
            left_frame,
            textvariable=self.dx_rank_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            width=26,
        )
        self.dx_rank_combo.pack(fill="x", pady=(0, 8))

        ttk.Label(left_frame, text="难度").pack(anchor="w")
        self.difficulty_combo = ttk.Combobox(
            left_frame,
            textvariable=self.difficulty_var,
            values=["master", "remaster", "expert", "utage"],
            state="readonly",
            width=26,
        )
        self.difficulty_combo.pack(fill="x", pady=(0, 8))

        self.song_type_label = ttk.Label(left_frame, text="谱面类型")
        self.song_type_label.pack(anchor="w")
        self.song_type_combo = ttk.Combobox(
            left_frame,
            textvariable=self.song_type_var,
            values=["standard", "dx"],
            state="readonly",
            width=26,
        )
        self.song_type_combo.pack(fill="x", pady=(0, 8))

        ttk.Label(left_frame, text="Play Log").pack(anchor="w", pady=(4, 0))
        self.play_log_first_check = ttk.Checkbutton(
            left_frame,
            text="显示完成标",
            variable=self.show_first_var,
            command=self.on_check_box_first_change,
        )
        self.play_log_first_check.pack(anchor="w")
        self.play_log_first_combo = ttk.Combobox(
            left_frame,
            textvariable=self.play_log_first_var,
            values=["applus", "ap", "fcplus", "fc"],
            state="readonly",
            width=26,
        )
        self.play_log_first_combo.pack(fill="x", pady=(0, 8))

        self.play_log_second_check = ttk.Checkbutton(
            left_frame,
            text="显示Sync标",
            variable=self.show_second_var,
            command=self.on_check_box_second_change,
        )
        self.play_log_second_check.pack(anchor="w")
        self.play_log_second_combo = ttk.Combobox(
            left_frame,
            textvariable=self.play_log_second_var,
            values=["fdxplus", "fdx", "fsplus", "fs", "sync"],
            state="readonly",
            width=26,
        )
        self.play_log_second_combo.pack(fill="x", pady=(0, 8))

        self.submit_button = ttk.Button(left_frame, text="提交", command=self.on_submit)
        self.submit_button.pack(fill="x", pady=(10, 0))

        ttk.Label(right_frame, text="输入关键字搜索...").pack(anchor="w")
        self.search_entry = ttk.Entry(right_frame, textvariable=self.search_var)
        self.search_entry.pack(fill="x", pady=(0, 8))

        list_area = ttk.Frame(right_frame)
        list_area.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(list_area, activestyle="dotbox")
        scrollbar = ttk.Scrollbar(
            list_area, orient="vertical", command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.listbox.bind("<<ListboxSelect>>", self.on_item_clicked)

        self.refresh_button = ttk.Button(
            right_frame, text="刷新文件列表", command=self.list_songs
        )
        self.refresh_button.pack(fill="x", pady=(8, 0))

    def get_all_items(self) -> list[str]:
        return list(self.listbox.get(0, tk.END))

    def _set_list_items(self, items: list[str]):
        self.listbox.delete(0, tk.END)
        for item in items:
            self.listbox.insert(tk.END, item)

    def filter_list(self, *_):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            self.list_songs()
            return

        matched_alias = [
            song.title for song in self.dxdata if keyword in song.all_names()
        ]
        matched_name = [title for title in self.all_titles if keyword in title.lower()]
        self._set_list_items(list(dict.fromkeys(matched_alias + matched_name)))

    def list_songs(self):
        added = set()
        self.all_titles = []
        for song in self.dxdata:
            if song.title in added:
                continue
            added.add(song.title)
            self.all_titles.append(song.title)
        self._set_list_items(self.all_titles)

    def on_item_clicked(self, _event=None):
        selection = self.listbox.curselection()
        if not selection:
            return

        self.song_name = self.listbox.get(selection[0])
        self.root.title("舞萌DX成绩图生成器: " + self.song_name)
        selected_song = where(self.dxdata, lambda x: x.title == self.song_name)
        if len(selected_song) != 1:
            return

        song = selected_song[0]
        if len(song.types) == 1:
            self.song_type_var.set("standard" if song.types[0] == "std" else "dx")
            self.song_type_label.pack_forget()
            self.song_type_combo.pack_forget()
        else:
            if not self.song_type_label.winfo_ismapped():
                self.song_type_label.pack(anchor="w")
            if not self.song_type_combo.winfo_ismapped():
                self.song_type_combo.pack(fill="x", pady=(0, 8))

    def _sync_play_log_visibility(self):
        if self.show_first_var.get():
            self.play_log_first_combo.pack(fill="x", pady=(0, 8))
        else:
            self.play_log_first_combo.pack_forget()

        if self.show_second_var.get():
            self.play_log_second_combo.pack(fill="x", pady=(0, 8))
        else:
            self.play_log_second_combo.pack_forget()

    def on_check_box_first_change(self):
        self.show_first = self.show_first_var.get()
        self._sync_play_log_visibility()

    def on_check_box_second_change(self):
        self.show_second = self.show_second_var.get()
        self._sync_play_log_visibility()

    def on_score_change(self, *_):
        score_text = self.score_var.get().strip()
        if not score_text:
            self.score = 0.0
            return

        try:
            self.score = float(score_text)
        except ValueError:
            return

        if self.score == 101.0:
            self.play_log_first_var.set("applus")
        else:
            self.play_log_first_var.set("ap")

    def _generate_image_async(self, params: dict):
        try:
            generate_score_image(**params)
        except Exception as error:
            self.root.after(
                0,
                lambda error_message=str(error): self._on_generate_failed(
                    error_message
                ),
            )
            return

        self.root.after(0, self._on_generate_success)

    def _on_generate_failed(self, error_message: str):
        self.submit_button.config(state="normal")
        messagebox.showerror("生成失败", error_message, parent=self.root)

    def _on_generate_success(self):
        self.submit_button.config(state="normal")
        messagebox.showinfo(
            "完成", "图片已保存为output.png和output43.png", parent=self.root
        )

    def on_submit(self):
        if not self.song_name:
            messagebox.showwarning("错误", "请先选择歌曲", parent=self.root)
            return

        try:
            score = float(self.score_var.get().strip())
        except ValueError:
            messagebox.showwarning("错误", "请输入正确的数字", parent=self.root)
            return

        self.score = score
        self.submit_button.config(state="disabled")
        params = dict(
            song_name=self.song_name,
            score=self.score,
            difficulty=self.difficulty_var.get(),
            dx_rank=self.dx_rank_var.get(),
            song_type=self.song_type_var.get(),
            show_first=self.show_first_var.get(),
            first_log=self.play_log_first_var.get()
            if self.show_first_var.get()
            else None,
            show_second=self.show_second_var.get(),
            second_log=self.play_log_second_var.get()
            if self.show_second_var.get()
            else None,
        )
        threading.Thread(
            target=self._generate_image_async, args=(params,), daemon=True
        ).start()

    def run(self):
        self.root.mainloop()


def resource_path(relative_path):
    # 打包后运行时会有 _MEIPASS 变量
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(getattr(sys, "_MEIPASS"), relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def where(data: list, predicate) -> list:
    return [item for item in data if predicate(item)]


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
    songs = init_data()
    selected_song: list[SimplifiedSong] = where(songs, lambda x: x.title == song_name)
    if len(selected_song) != 0:
        download_file(selected_song[0].dimg_url(), "bg.png")
    else:
        return
    bg_path = Path("bg.png")
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
    diff = Image.open(resource_path(f"assets/diff_{difficulty}.png")).convert("RGBA")
    resized_diff = diff.resize((diff.width * 5 // 2, diff.height * 5 // 2))
    canvas.paste(resized_diff, (30, 30), resized_diff)

    # 写歌名
    song_name_font = ImageFont.truetype(
        resource_path("assets/SourceHanSans-Bold.otf"), 50
    )
    draw.text((440, 35), song_name, font=song_name_font, fill=(0, 0, 0))

    # 画谱面类型
    type_img = Image.open(resource_path(f"assets/music_{song_type}.png")).convert(
        "RGBA"
    )
    resized_type = type_img.resize((type_img.width * 3 // 2, type_img.height * 3 // 2))
    canvas.paste(resized_type, (10, 130), resized_type)

    # 处理Play Log
    def paste_log(image_name, pos):
        if image_name:
            log_img = Image.open(resource_path(f"assets/{image_name}.png")).convert(
                "RGBA"
            )
            scaled_log = log_img.resize(
                (log_img.width * 5 // 2, log_img.height * 5 // 2)
            )
            canvas.paste(scaled_log, pos, scaled_log)

    logs = []
    if show_first and first_log:
        logs.append((first_log, (600, 400)))
    if show_second and second_log:
        logs.append((second_log, (590, 530) if len(logs) == 1 else (590, 400)))
    for log, pos in logs:
        paste_log(log, pos)

    # 画DX Star
    dx_star = Image.open(
        resource_path(f"assets/music_icon_dxstar_{dx_rank}.png")
    ).convert("RGBA")
    resized_dx_star = dx_star.resize((105, 105))
    canvas.paste(resized_dx_star, (600, 150), resized_dx_star)

    # 画分数
    int_part = str(int(score))
    decimal_part = f"{score - int(score):.4f}"[1:] + "%"
    score_font = ImageFont.truetype(resource_path("assets/NotoSansCJKBold.otf"), 120)
    subscore_font = ImageFont.truetype(resource_path("assets/NotoSansCJKBold.otf"), 80)

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
    ranking = Image.open(resource_path(f"assets/{rank}.png")).convert("RGBA")
    resized_rank = ranking.resize((ranking.width * 3 // 2, ranking.height * 3 // 2))
    canvas.paste(resized_rank, (900, 400), resized_rank)

    # 保存输出
    canvas43.paste(canvas, (0, 120), canvas)
    canvas.save(output_path)
    canvas43.save(output_43_path)


def main():
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
        except Exception as exc:
            print(f"生成失败：{str(exc)}")
            sys.exit(1)
        return

    try:
        app = MaimaiScorePicGeneratorApp()
    except Exception as exc:
        print(f"启动失败：{str(exc)}")
        sys.exit(1)
    app.run()


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
    main()

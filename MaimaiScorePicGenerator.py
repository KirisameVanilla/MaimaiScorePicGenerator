from typing import Literal
from PIL import Image, ImageDraw, ImageFont

base_dir = "C:\\Users\\Vanillaaaa\\Desktop\\MaimaiScorePicGenerator\\"

# 画布尺寸 (16:9)
canvas_width = 1280
canvas_height = 720
background_color = (130, 100, 200, 255)  # 类似原图的紫色

# 创建画布
canvas = Image.new("RGBA", (canvas_width, canvas_height), background_color)
canvas43 = Image.new("RGBA", (canvas_width, 960), background_color)
draw = ImageDraw.Draw(canvas)

# 加载曲绘并缩放放置在左侧
original_img = Image.open(base_dir + "bg.png").convert("RGBA")
img_width = (int)(1.3 * canvas_width) // 3
img_height = int(img_width * original_img.height / original_img.width)
original_img = original_img.resize((img_width, img_height), Image.Resampling.LANCZOS)
canvas.paste(original_img, (30, canvas_height // 5))  # 左侧对齐

# 画标题栏
title_bar_color = (255, 255, 255)
title_bar_height = 100
draw.rounded_rectangle([(20, 20), (canvas_width - 20, 20 + title_bar_height)], fill=title_bar_color, radius=10)

# 画难度
diff_master = Image.open(base_dir + "assets\\diff_master.png").convert("RGBA")
diff_remaster = Image.open(base_dir + "assets\\diff_remaster.png").convert("RGBA")
diff_expert = Image.open(base_dir + "assets\\diff_expert.png").convert("RGBA")
diff = diff_master
resized_diff = diff.resize((diff.width * 5 // 2, diff.height * 5 // 2))
canvas.paste(resized_diff, (30, 30),resized_diff)
print(resized_diff.width, resized_diff.height)

# 写歌名
song_name = "Believe the Rainbow"
song_name_font = ImageFont.truetype(base_dir + "assets\\SourceHanSans-Bold.otf", 50)
song_name_color = (0, 0, 0)
song_name_position = (440, 35)
draw.text(song_name_position, song_name, font=song_name_font, fill=song_name_color)

# 画DX/标准
music_dx = Image.open(base_dir + "assets\\music_dx.png").convert("RGBA")
music_standard = Image.open(base_dir + "assets\\music_standard.png").convert("RGBA")
type = music_standard
resized_type = type.resize((type.width * 3 // 2, type.height * 3 // 2))
canvas.paste(resized_type, (10, 130),resized_type)

# 画AP/AP+
ap = Image.open(base_dir + "assets\\ap.png").convert("RGBA")
ap_plus = Image.open(base_dir + "assets\\applus.png").convert("RGBA")
type = ap
resized_type = type.resize((type.width * 5 // 2, type.height * 5 // 2))
canvas.paste(resized_type, (600, 400),resized_type)

# 画评级
sss = Image.open(base_dir + "assets\\sss.png").convert("RGBA")
sssplus = Image.open(base_dir + "assets\\sssplus.png").convert("RGBA")
type = sssplus
resized_type = type.resize((type.width * 3 // 2, type.height * 3 // 2))
canvas.paste(resized_type, (900, 400),resized_type)

# 画 DX Star
dx_rank: Literal[1,2,3,4,5] = 4
dx_star = Image.open(base_dir + f"assets\\music_icon_dxstar_{dx_rank}.png").convert("RGBA")
resized_dx_star = dx_star.resize((105, 105))
canvas.paste(resized_dx_star, (600, 150), resized_dx_star)

# 画分数
score = "100"
score_font = ImageFont.truetype(base_dir + "assets\\NotoSansCJKBold.otf", 120)
score_color = (255, 255, 255)
outline_color = (0, 0, 0)
offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
score_position = (700, 200)
for dx, dy in offsets:
    draw.text((score_position[0] + dx, score_position[1] + dy), score, font=score_font, fill=outline_color)
draw.text(score_position, score, font=score_font, fill=score_color)
bbox = score_font.getbbox(score)
score_width = bbox[2] - bbox[0]
score_height = bbox[3] - bbox[1]

subscore = ".9642%"
subscore_font = ImageFont.truetype(base_dir + "assets\\NotoSansCJKBold.otf", 80)
subscore_height = subscore_font.getbbox(subscore)[3] - subscore_font.getbbox(subscore)[1]
suboffsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
subscore_position = (700+score_width, 200+score_height-subscore_height)
for dx, dy in suboffsets:
    draw.text((subscore_position[0] + dx, subscore_position[1] + dy), subscore, font=subscore_font, fill=outline_color)
draw.text(subscore_position, subscore, font=subscore_font, fill=score_color)

# 保存图片
output_path = base_dir + "output.png"
output_path43 = base_dir + "output43.png"
canvas43.paste(canvas, (0, 120), canvas)
canvas.save(output_path)
canvas43.save(output_path43)
canvas.show()
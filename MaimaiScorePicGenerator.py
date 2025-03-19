from PIL import Image, ImageDraw

base_dir = "C:\\Users\\Vanillaaaa\\Desktop\\MaimaiScorePicGenerator\\"

# 画布尺寸 (16:9)
canvas_width = 1280
canvas_height = 720
background_color = (130, 100, 200, 255)  # 类似原图的紫色

# 创建画布
canvas = Image.new("RGBA", (canvas_width, canvas_height), background_color)
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
diff_master = Image.open(base_dir + "diff_master.png").convert("RGBA")
diff_remaster = Image.open(base_dir + "diff_remaster.png").convert("RGBA")
diff_expert = Image.open(base_dir + "diff_expert.png").convert("RGBA")
diff = diff_remaster
resized_diff = diff.resize((diff.width * 5 // 2, diff.height * 5 // 2))
pixels = resized_diff.load()
canvas.paste(resized_diff, (30, 30),resized_diff)

# 画 "CLEAR!" 按钮
clear_button_color = (255, 220, 80)
clear_button_x = canvas_width - 150
clear_button_y = 20
clear_button_w = 120
clear_button_h = 40
draw.rounded_rectangle(
    [(clear_button_x, clear_button_y), (clear_button_x + clear_button_w, clear_button_y + clear_button_h)],
    fill=clear_button_color,
    outline="black",
    width=3
)

# 画 "ACHIEVEMENT" 区块
achievement_x = img_width + 50
achievement_y = canvas_height // 4
achievement_w = canvas_width - achievement_x - 30
achievement_h = img_height // 2

draw.rectangle(
    [(achievement_x, achievement_y), (achievement_x + achievement_w, achievement_y + achievement_h)],
    fill=(80, 50, 150),
    outline="white",
    width=3
)

# 画分数框
score_x = achievement_x + 20
score_y = achievement_y + achievement_h - 80
score_w = achievement_w - 40
score_h = 60
draw.rectangle(
    [(score_x, score_y), (score_x + score_w, score_y + score_h)],
    fill=(50, 200, 50),
    outline="black",
    width=3
)

# 画 "DETAILS" 按钮
details_x = canvas_width - 180
details_y = canvas_height - 70
details_w = 150
details_h = 50
draw.rectangle(
    [(details_x, details_y), (details_x + details_w, details_y + details_h)],
    fill=(100, 100, 255),
    outline="black",
    width=3
)

# 保存图片
output_path = base_dir + "output.png"
canvas.save(output_path)
canvas.show()
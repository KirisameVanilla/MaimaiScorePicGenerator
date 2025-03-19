import cv2
import numpy as np

base_dir = "C:\\Users\\Vanillaaaa\\Desktop\\MaimaiScorePicGenerator\\"

def draw_rounded_rectangle(img, pt1, pt2, color, thickness, corner_radius):
    x1, y1 = pt1
    x2, y2 = pt2
    
    # 绘制主体矩形
    cv2.rectangle(img, (x1 + corner_radius, y1), (x2 - corner_radius, y2), color, thickness)
    cv2.rectangle(img, (x1, y1 + corner_radius), (x2, y2 - corner_radius), color, thickness)
    
    # 绘制四个圆角
    cv2.ellipse(img, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, color, thickness)
    cv2.ellipse(img, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, color, thickness)
    cv2.ellipse(img, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, color, thickness)
    cv2.ellipse(img, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, color, thickness)

def fill_rounded_rectangle(img, pt1, pt2, color, corner_radius):
    x1, y1 = pt1
    x2, y2 = pt2
    
    # 填充主体矩形
    cv2.rectangle(img, (x1 + corner_radius, y1), (x2 - corner_radius, y2), color, -1)
    cv2.rectangle(img, (x1, y1 + corner_radius), (x2, y2 - corner_radius), color, -1)
    
    # 填充四个圆角
    cv2.ellipse(img, (x1 + corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 180, 0, 90, color, -1)
    cv2.ellipse(img, (x2 - corner_radius, y1 + corner_radius), (corner_radius, corner_radius), 270, 0, 90, color, -1)
    cv2.ellipse(img, (x1 + corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 90, 0, 90, color, -1)
    cv2.ellipse(img, (x2 - corner_radius, y2 - corner_radius), (corner_radius, corner_radius), 0, 0, 90, color, -1)

# 画布尺寸 (16:9)
canvas_width = 1280
canvas_height = 720
background_color = (200, 100, 130)  # BGR格式的紫色

# 创建画布
canvas = np.full((canvas_height, canvas_width, 3), background_color, dtype=np.uint8)

# 加载曲绘并缩放放置在左侧
original_img = cv2.imread(base_dir + "bg.png")
img_width = (int)(1.3 * canvas_width) // 3
img_height = int(img_width * original_img.shape[0] / original_img.shape[1])
original_img = cv2.resize(original_img, (img_width, img_height), interpolation=cv2.INTER_LANCZOS4)
canvas[canvas_height//5:canvas_height//5+img_height, 30:30+img_width] = original_img

# 画标题栏（白色圆角矩形）
title_bar_color = (255, 255, 255)
title_bar_height = 100
fill_rounded_rectangle(canvas, (20, 20), (canvas_width-20, 20+title_bar_height), title_bar_color, 20)

# 画难度
diff_master = cv2.imread(base_dir + "diff_master.png")
diff_remaster = cv2.imread(base_dir + "diff_remaster.png")
diff_expert = cv2.imread(base_dir + "diff_expert.png")
canvas[30:30+diff_expert.shape[0], 30:30+diff_expert.shape[1]] = diff_expert

# 画 "CLEAR!" 按钮
clear_button_color = (80, 220, 255)
clear_button_x = canvas_width - 150
clear_button_y = 20
clear_button_w = 120
clear_button_h = 40
fill_rounded_rectangle(canvas, 
             (clear_button_x, clear_button_y), 
             (clear_button_x + clear_button_w, clear_button_y + clear_button_h),
             clear_button_color, 10)
draw_rounded_rectangle(canvas, 
             (clear_button_x, clear_button_y), 
             (clear_button_x + clear_button_w, clear_button_y + clear_button_h),
             (0, 0, 0), 3, 10)

# 画 "ACHIEVEMENT" 区块
achievement_x = img_width + 50
achievement_y = canvas_height // 4
achievement_w = canvas_width - achievement_x - 30
achievement_h = img_height // 2

fill_rounded_rectangle(canvas,
             (achievement_x, achievement_y),
             (achievement_x + achievement_w, achievement_y + achievement_h),
             (80, 50, 150), 20)
draw_rounded_rectangle(canvas,
             (achievement_x, achievement_y),
             (achievement_x + achievement_w, achievement_y + achievement_h),
             (255, 255, 255), 3, 20)

# 画分数框
score_x = achievement_x + 20
score_y = achievement_y + achievement_h - 80
score_w = achievement_w - 40
score_h = 60
fill_rounded_rectangle(canvas,
             (score_x, score_y),
             (score_x + score_w, score_y + score_h),
             (50, 200, 50), 10)
draw_rounded_rectangle(canvas,
             (score_x, score_y),
             (score_x + score_w, score_y + score_h),
             (0, 0, 0), 3, 10)

# 画 "DETAILS" 按钮
details_x = canvas_width - 180
details_y = canvas_height - 70
details_w = 150
details_h = 50
fill_rounded_rectangle(canvas,
             (details_x, details_y),
             (details_x + details_w, details_y + details_h),
             (100, 100, 255), 10)
draw_rounded_rectangle(canvas,
             (details_x, details_y),
             (details_x + details_w, details_y + details_h),
             (0, 0, 0), 3, 10)

# 保存图片
output_path = base_dir + "output_cv2.png"
cv2.imwrite(output_path, canvas)

# 显示图片
cv2.imshow("Generated Image", canvas)
cv2.waitKey(0)
cv2.destroyAllWindows() 
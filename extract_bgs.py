import os
import shutil
import re

def extract_song_name(text):
    ori=text
    if text == "[X]":
        return text
    regex_1 = r"^\[[X逆両光回片息藏蔵耐覚爆疑右奏習蛸傾即嘘宴星撫狂協 NO\.123456]*\]"
    regex_2 = r" ?\[[12PEASYHARDX]*\]$"
    match = re.search(regex_1, text)
    while match:
        text = text[4:]
        match = re.search(regex_1, text)
    match = re.search(regex_2, text)
    while match:
        text = text[:match.start()]
        match = re.search(regex_2, text)
    if (ori != text):
        print(ori, "->", text)
    return text

def copy_bg_images(src_root, dest_root):
    songs = []
    for version in os.listdir(src_root):
        version_path = os.path.join(src_root, version)
        if not os.path.isdir(version_path):
            continue
        
        for song in os.listdir(version_path):
            song_name = extract_song_name(song)
            if (song_name in songs):
                continue
            songs.append(song_name)
            song_path = os.path.join(version_path, song)
            if not os.path.isdir(song_path):
                continue
            
            bg_path = os.path.join(song_path, "bg.png")
            if os.path.exists(bg_path):
                shutil.copy(bg_path, dest_root + f"{song_name}.png")
                continue

            bg_path = os.path.join(song_path, "bg.jpg")
            if os.path.exists(bg_path):
                shutil.copy(bg_path, dest_root + f"{song_name}.jpg")

src_directory = "D:\\maimai"
dest_directory = "C:\\Users\\Vanillaaaa\\Desktop\\MaimaiScorePicGenerator\\bgs\\"
copy_bg_images(src_directory, dest_directory)
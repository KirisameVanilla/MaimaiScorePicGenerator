# 舞萌DX成绩图生成器

![Tag](https://img.shields.io/badge/tag-v1.0-0A7BBB)

## 使用场景

- 手元视频封面

## 最新更新

version v1.0: [MaimaiScorePicGenerator.exe](https://github.com/KirisameVanilla/MaimaiScorePicGenerator/releases/latest/download/MaimaiScorePicGenerator.exe)

已集成所有资源文件, 只需要一个exe就能运行
曲库数据会在程序启动时从内置地址自动加载

## 使用方法

- 下载最新的 [MaimaiScorePicGenerator.exe](https://github.com/KirisameVanilla/MaimaiScorePicGenerator/releases/latest/download/MaimaiScorePicGenerator.exe)

### Chore

注意, 目前本工具的曲绘获取是从 [dxrating](https://shama.dxrating.net) 获取的, 所以离线/连接不上dxrating时无法使用

程序已经内置 `dxdata.json` 的获取地址, 启动后会自动加载

### GUI

运行 *MaimaiScorePicGenerator.exe*

GUI 已改为使用 Python 内置的 tkinter，不再依赖 PyQt6。

### 命令行(not recommended)

*注意: 带特殊符号的参数可能无法正确处理, 如"411Ψ892", 您需要在bgs文件夹中手动删除掉引号, 将其变成411Ψ892*

```
.\MaimaiScorePicGenerator.exe --song "曲名(不带后缀)" --score 100.5 --difficulty master --dx-rank 5 --song-type dx --show-first --first-log applus
```

--show-first 和 --first-log, --show-second 和 --second-log 必须同时出现

## 图例

### 16:9比例

![](examples/eg.png)

### 4:3比例

![](examples/eg43.png)

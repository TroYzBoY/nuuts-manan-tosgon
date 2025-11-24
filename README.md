# 🎮 Face Lock + 2D RPG Game

Нүүр танилтын систем болон 2D RPG тоглоомын нэгтгэсэн төсөл.

## 📁 Folder Structure

```
nuuts-manan-tosgon/
├── face_lock.py          # Face recognition систем (GUI)
├── game.py               # 2D RPG тоглоом
├── player.py             # Player класс
├── movement.py           # Movement логик
├── boss_1.py            # Boss логик
├── 1.py                  # Хуучин нэгтгэсэн файл (backup)
│
├── image/                # Тоглоомын зураг assets
│   ├── attacking/        # Attack animation
│   ├── idle/            # Idle animation
│   ├── walking/          # Walking animation
│   ├── dying/           # Death animation
│   └── *.png            # Sprite файлууд
│
├── map/                  # Тоглоомын газрын зураг
│   ├── main_map.tmx     # Үндсэн газрын зураг
│   ├── boss_*.tmx       # Boss түвшний газрын зураг
│   └── *.tsx, *.png     # Tile set файлууд
│
├── music/                # Тоглоомын хөгжүүлэг
│   ├── main_map.mp3
│   └── boss_*.mp3
│
├── sound/                # Тоглоомын дуу
│   ├── attacking.wav
│   ├── dying.wav
│   └── *.wav
│
├── data/                 # Data файлууд (auto-generated)
│   └── enhanced_face_data.pkl
│
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore файл
└── README.md            # Энэ файл
```

## 🚀 Эхлүүлэх

### 1. Dependencies суулгах

```bash
pip install -r requirements.txt
```

### 2. Face Lock систем эхлүүлэх

```bash
python face_lock.py
```

### 3. Тоглоом шууд эхлүүлэх (face lock байхгүй)

```bash
python game.py
```

## 🎯 Ашиглах

1. **Face Lock систем**:
   - `face_lock.py` ажиллуулах
   - "Нүүр бүртгэх" товчийг дараад нүүр бүртгэх
   - "Танилт эхлүүлэх" товчийг дараад танилт эхлүүлэх
   - Нүүр танигдсаны дараа тоглоом автоматаар эхэлнэ

2. **Тоглоом**:
   - WASD - Хөдөлгөөн
   - Space - Attack
   - E - Interaction
   - ESC - Menu

## 📋 Features

### Face Lock System
- ✅ OpenCV ашиглан нүүр танилт
- ✅ Deep Features (LBP + HOG + ORB)
- ✅ Multi-angle face registration
- ✅ Quality filtering
- ✅ Real-time recognition
- ✅ Tkinter GUI

### 2D RPG Game
- ✅ Pygame-based 2D game
- ✅ TMX map support
- ✅ Player movement & combat
- ✅ Enemy AI (Slimes, Bosses)
- ✅ Tower defense elements
- ✅ NPC dialogue system
- ✅ Health/Stamina/XP system
- ✅ Sound & music

## 🔧 System Requirements

- Python 3.8+
- Windows 10+ / macOS / Linux
- Webcam (face recognition-д)
- 4GB RAM minimum
- OpenGL compatible graphics

## 📝 Notes

- Face data нь `enhanced_face_data.pkl` файлд хадгалагдана
- Тоглоомын map файлууд `map/` folder-т байрлана
- Assets (images, sounds, music) нь тус тусдаа folder-т байрлана

## 🐛 Troubleshooting

**Face recognition ажиллахгүй байна:**
- Webcam зөв холбогдсон эсэхийг шалгах
- OpenCV зөв суусан эсэхийг шалгах: `python -c "import cv2; print(cv2.__version__)"`

**Тоглоом эхлэхгүй байна:**
- `map/main_map.tmx` файл байгаа эсэхийг шалгах
- Pygame зөв суусан эсэхийг шалгах: `python -c "import pygame; print(pygame.__version__)"`

**Path алдаа:**
- Бүх файлууд зөв folder-т байрласан эсэхийг шалгах
- Relative path-ууд зөв эсэхийг шалгах

## 📄 License

Энэ төсөл нь personal project юм.

## 👤 Author

nuuts-manan-tosgon

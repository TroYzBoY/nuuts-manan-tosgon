# 📁 Project Structure

## Folder Organization

```
nuuts-manan-tosgon/
│
├── 📄 Main Files
│   ├── face_lock.py          # Face recognition систем (GUI)
│   ├── game.py               # 2D RPG тоглоом
│   ├── player.py             # Player класс
│   ├── movement.py           # Movement логик
│   ├── boss_1.py            # Boss логик
│   └── 1.py                  # Хуучин нэгтгэсэн файл (backup)
│
├── 📁 Assets
│   ├── image/                # Тоглоомын зураг assets
│   │   ├── attacking/        # Attack animation sprites
│   │   ├── idle/            # Idle animation sprites
│   │   ├── walking/          # Walking animation sprites
│   │   ├── dying/           # Death animation sprites
│   │   └── *.png            # Character & enemy sprites
│   │
│   ├── map/                  # Тоглоомын газрын зураг
│   │   ├── main_map.tmx     # Үндсэн газрын зураг
│   │   ├── boss_*.tmx       # Boss түвшний газрын зураг
│   │   ├── home_inn_*.tmx   # Home/Inn газрын зураг
│   │   └── *.tsx, *.png     # Tile set файлууд
│   │
│   ├── music/                # Тоглоомын хөгжүүлэг
│   │   ├── main_map.mp3     # Үндсэн газрын хөгжүүлэг
│   │   └── boss_*.mp3        # Boss түвшний хөгжүүлэг
│   │
│   └── sound/                # Тоглоомын дуу
│       ├── attacking.wav     # Attack дуу
│       ├── dying.wav         # Death дуу
│       ├── projectile.wav    # Projectile дуу
│       └── taking_damage.wav # Damage дуу
│
├── 📁 Data (Auto-generated)
│   ├── data/                 # Data файлууд
│   │   └── enhanced_face_data.pkl  # Face recognition data
│   │
│   └── backup/               # Backup файлууд
│
├── 📄 Documentation
│   ├── README.md            # Үндсэн documentation
│   ├── PROJECT_STRUCTURE.md # Энэ файл
│   └── requirements.txt     # Python dependencies
│
└── 📄 Config
    └── .gitignore           # Git ignore файл
```

## File Descriptions

### Main Python Files

- **face_lock.py**: Face recognition систем. Tkinter GUI ашиглан нүүр танилт хийж, танигдсаны дараа тоглоом эхлүүлнэ.
- **game.py**: 2D RPG тоглоом. Pygame ашиглан бүтээгдсэн.
- **player.py**: Player класс, player-ийн логик, stats, abilities.
- **movement.py**: Movement систем, collision detection.
- **boss_1.py**: Boss логик (хэрэв байвал).

### Asset Folders

- **image/**: Бүх sprite болон animation файлууд
  - `attacking/`: Attack animation frames
  - `idle/`: Idle animation frames
  - `walking/`: Walking animation frames
  - `dying/`: Death animation frames
  - Root level: Character sprites, enemy sprites, effects

- **map/**: TMX map файлууд болон tile sets
  - `main_map.tmx`: Үндсэн тоглоомын газрын зураг
  - `boss_*.tmx`: Boss түвшний газрын зураг
  - `*.tsx`: Tile set definitions
  - `*.png`: Tile set images

- **music/**: Background music файлууд (MP3 формат)

- **sound/**: Sound effect файлууд (WAV формат)

### Data Files

- **data/**: Автоматаар үүсдэг data файлууд
  - `enhanced_face_data.pkl`: Face recognition-ийн бүртгэлтэй нүүрний мэдээлэл

### Documentation

- **README.md**: Төслийн үндсэн documentation, ашиглах заавар
- **PROJECT_STRUCTURE.md**: Энэ файл - folder structure тайлбар
- **requirements.txt**: Python package dependencies

## Path Conventions

Бүх path-ууд нь relative path ашигладаг:
- `os.path.join(os.path.dirname(os.path.abspath(__file__)), ...)` pattern ашиглана
- Энэ нь файлуудыг зөв олох боломжийг олгоно

## Notes

- `1.py` файл нь хуучин нэгтгэсэн файл, backup гэж ашиглаж болно
- `backup/` folder нь map/backup-аас ялгаатай
- Data файлууд нь `.gitignore`-д багтсан тул Git-д commit хийхгүй


# Code Refactoring Status

## ✅ Completed

1. **Folder Structure**:
   - `entities/` folder created
   - `utils/` folder created

2. **Separated Classes**:
   - ✅ `entities/state.py` - State enum
   - ✅ `entities/projectile.py` - Projectile class
   - ✅ `utils/floating_text.py` - FloatingText class
   - ✅ `utils/dialogue.py` - DialogueSystem class
   - ✅ `utils/camera.py` - Camera class
   - ✅ `utils/map.py` - GameMap class

## 🔄 In Progress

3. **Entities Classes** (Need to extract from game.py):
   - ⏳ `entities/boss.py` - Boss class
   - ⏳ `entities/tower.py` - Tower class
   - ⏳ `entities/npc.py` - NPC class
   - ⏳ `entities/slime.py` - Slime class
   - ⏳ `entities/player.py` - Player class

## 📝 Next Steps

4. **Update game.py**:
   - Remove all class definitions
   - Add imports from entities/ and utils/
   - Keep only Game class and main entry point

5. **Update face_lock.py**:
   - Organize face recognition code better
   - Separate UI components if needed

## 📁 Final Structure

```
nuuts-manan-tosgon/
├── entities/
│   ├── __init__.py
│   ├── state.py
│   ├── projectile.py
│   ├── player.py
│   ├── boss.py
│   ├── tower.py
│   ├── slime.py
│   └── npc.py
├── utils/
│   ├── __init__.py
│   ├── floating_text.py
│   ├── dialogue.py
│   ├── camera.py
│   └── map.py
├── game.py (main game loop)
├── face_lock.py
└── ...
```


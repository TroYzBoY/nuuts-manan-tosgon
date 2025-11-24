"""
GameMap class for loading and managing TMX maps
"""
import pygame
import pytmx
from pytmx.util_pygame import load_pygame
import os
import sys

# Import entities for map building
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from entities.boss import Boss
from entities.tower import Tower
from entities.npc import NPC


class GameMap:
    def __init__(self, tmx_file):
        self.current_map_file = tmx_file  # Store for tower building
        try:
            self.tmx_data = load_pygame(tmx_file)
        except Exception as e:
            print(f"Error loading TMX file: {e}")
            print("Attempting to auto-fix tileset source paths...")

            import xml.etree.ElementTree as ET

            tmx_dir = os.path.dirname(os.path.abspath(tmx_file))
            tree = ET.parse(tmx_file)
            root = tree.getroot()
            changed = False

            for tileset in root.findall('tileset'):
                src = tileset.get('source')
                if src:
                    base = os.path.basename(src)
                    candidate = os.path.join(tmx_dir, base)
                    if os.path.exists(candidate):
                        tileset.set('source', candidate)
                        changed = True
                    else:
                        placeholder_tsx = candidate
                        placeholder_img = os.path.join(
                            tmx_dir, base.replace('.tsx', '.png'))
                        try:
                            if not os.path.exists(placeholder_img):
                                try:
                                    from PIL import Image
                                    Image.new('RGBA', (32, 32), (0, 0, 0, 0)).save(
                                        placeholder_img)
                                except Exception:
                                    with open(placeholder_img, 'wb') as f:
                                        f.write(b'\x89PNG\r\n\x1a\n')

                            with open(placeholder_tsx, 'w', encoding='utf-8') as f:
                                f.write(
                                    '<?xml version="1.0" encoding="UTF-8"?>\n')
                                f.write(
                                    f'<tileset version="1.10" tiledversion="1.11.2" name="{base.replace(".tsx", "")}" tilewidth="32" tileheight="32" tilecount="1" columns="1">\n')
                                f.write(
                                    f' <image source="{os.path.basename(placeholder_img)}" width="32" height="32"/>\n')
                                f.write('</tileset>\n')

                            tileset.set('source', placeholder_tsx)
                            changed = True
                            print(
                                f"Created placeholder tileset: {placeholder_tsx}")
                        except Exception:
                            pass

            for tileset in root.findall('tileset'):
                img_elem = tileset.find('image')
                if img_elem is not None:
                    img_src = img_elem.get('source')
                    if img_src:
                        img_base = os.path.basename(img_src)
                        img_candidate = os.path.join(tmx_dir, img_base)
                        if os.path.exists(img_candidate):
                            img_elem.set('source', img_candidate)
                            changed = True
                        else:
                            try:
                                placeholder_path = img_candidate
                                if not os.path.exists(placeholder_path):
                                    try:
                                        from PIL import Image
                                        Image.new('RGBA', (32, 32), (0, 0, 0, 0)).save(
                                            placeholder_path)
                                        print(
                                            f"Created placeholder image: {placeholder_path}")
                                    except Exception:
                                        with open(placeholder_path, 'wb') as f:
                                            f.write(b'\x89PNG\r\n\x1a\n')
                                img_elem.set('source', placeholder_path)
                                changed = True
                            except Exception:
                                pass

            if changed:
                fixed_path = os.path.join(tmx_dir, os.path.basename(
                    tmx_file).replace('.tmx', '_fixed.tmx'))
                tree.write(fixed_path, encoding='utf-8', xml_declaration=True)
                print(f"Wrote fixed TMX to: {fixed_path}")

                for tileset in root.findall('tileset'):
                    src = tileset.get('source')
                    if not src:
                        continue
                    tsx_path = src
                    if not os.path.isabs(tsx_path):
                        tsx_path = os.path.join(tmx_dir, tsx_path)

                    if not os.path.exists(tsx_path):
                        continue

                    try:
                        ts_tree = ET.parse(tsx_path)
                        ts_root = ts_tree.getroot()
                        img = ts_root.find('image')
                        if img is not None:
                            img_src = img.get('source')
                            if img_src:
                                img_base = os.path.basename(img_src)
                                img_candidate = os.path.join(tmx_dir, img_base)
                                if os.path.exists(img_candidate):
                                    img.set('source', img_candidate)
                                    ts_tree.write(
                                        tsx_path, encoding='utf-8', xml_declaration=True)
                                else:
                                    placeholder_path = img_candidate
                                    if not os.path.exists(placeholder_path):
                                        try:
                                            from PIL import Image
                                            placeholder = Image.new(
                                                'RGBA', (32, 32), (0, 0, 0, 0))
                                            placeholder.save(placeholder_path)
                                            print(
                                                f"Created placeholder image: {placeholder_path}")
                                            img.set('source', placeholder_path)
                                            ts_tree.write(
                                                tsx_path, encoding='utf-8', xml_declaration=True)
                                        except Exception:
                                            try:
                                                with open(placeholder_path, 'wb') as f:
                                                    f.write(
                                                        b'\x89PNG\r\n\x1a\n')
                                                img.set(
                                                    'source', placeholder_path)
                                                ts_tree.write(
                                                    tsx_path, encoding='utf-8', xml_declaration=True)
                                                print(
                                                    f"Wrote minimal placeholder PNG: {placeholder_path}")
                                            except Exception:
                                                pass
                    except Exception:
                        pass

                try:
                    self.tmx_data = load_pygame(fixed_path)
                except Exception as load_err:
                    print("Auto-fix failed when loading the fixed TMX:", load_err)
                    raise
            else:
                print("No local tileset files found to fix the TMX.\nMake sure your .tsx files are next to the .tmx or adjust paths in the TMX.")
                raise

        self.tile_w = self.tmx_data.tilewidth
        self.tile_h = self.tmx_data.tileheight
        self.width = self.tmx_data.width
        self.height = self.tmx_data.height
        self.collision_rects = self.build_collision_rects()
        self.teleports = self.build_teleports()
        self.bosses = self.build_bosses()
        self.towers = self.build_towers()
        self.npcs = self.build_npcs()

    def build_collision_rects(self):
        rects = []
        layers = list(self.tmx_data.visible_layers)

        if layers:
            bottom_layer = layers[0]
            if isinstance(bottom_layer, pytmx.TiledTileLayer):
                if bottom_layer.properties.get("blocked") or bottom_layer.name.lower() == "collision":
                    for x, y, gid in bottom_layer.tiles():
                        if gid != 0:
                            rects.append(pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                     self.tmx_data.tilewidth, self.tmx_data.tileheight))
                    return rects

        try:
            collision_layer = self.tmx_data.get_layer_by_name("collision")
            if collision_layer and collision_layer.properties.get("blocked"):
                for x, y, gid in collision_layer.tiles():
                    if gid != 0:
                        rects.append(pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                 self.tmx_data.tilewidth, self.tmx_data.tileheight))
        except Exception as e:
            print(f"Warning: Could not load collision layer: {e}")

        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                if layer.properties.get("blocked"):
                    for x, y, gid in layer.tiles():
                        if gid != 0:
                            rects.append(pygame.Rect(x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight,
                                                     self.tmx_data.tilewidth, self.tmx_data.tileheight))
        return rects

    def build_teleports(self):
        teleports = []
        try:
            for obj in getattr(self.tmx_data, 'objects', []):
                obj_type = getattr(obj, 'type', '') or getattr(obj, 'name', '')
                if str(obj_type).lower() == 'teleport':
                    props = getattr(obj, 'properties', {}) or {}
                    dest = props.get('dest') or props.get(
                        'map') or props.get('destination')
                    dest_x = props.get('dest_x')
                    dest_y = props.get('dest_y')
                    rect = pygame.Rect(int(obj.x), int(obj.y), int(getattr(obj, 'width', 0) or 1),
                                       int(getattr(obj, 'height', 0) or 1))
                    teleports.append(
                        {'rect': rect, 'dest': dest, 'dest_x': dest_x, 'dest_y': dest_y, 'obj': obj})
        except Exception:
            pass
        return teleports

    def build_bosses(self):
        bosses = []
        try:
            for obj in getattr(self.tmx_data, 'objects', []):
                obj_type = getattr(obj, 'type', '') or getattr(obj, 'name', '')
                if str(obj_type).lower() == 'boss':
                    boss = Boss(int(obj.x), int(obj.y),
                                self.tile_w, self.tile_h)
                    bosses.append(boss)
                    print(f"Found boss at ({obj.x}, {obj.y})")
        except Exception as e:
            print(f"Error loading bosses: {e}")
        return bosses

    def build_towers(self):
        """Build towers by scanning for tower images in the image folder and placing them on the map"""
        towers = []
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_dir = os.path.join(script_dir, 'image')

        # Check what tower images are available
        available_towers = []
        tower_types = ['fire', 'water', 'void', 'ice', 'lightning', 'holy']

        for tower_type in tower_types:
            tower_img_path = os.path.join(image_dir, f'tower_{tower_type}.png')
            if os.path.exists(tower_img_path):
                available_towers.append(tower_type)
                print(f"Found tower image: tower_{tower_type}.png")

        # Get current map name to determine which towers to spawn
        try:
            map_name = os.path.basename(
                getattr(self, 'current_map_file', '')).lower()

            # Different maps get different tower configurations
            if 'winter' in map_name or 'boss' in map_name:
                tower_configs = [
                    {'x': 5, 'y': 5, 'type': 'ice'},
                    {'x': self.width - 8, 'y': 5, 'type': 'ice'},
                    {'x': 5, 'y': self.height - 8, 'type': 'water'},
                    {'x': self.width - 8, 'y': self.height - 8, 'type': 'water'},
                ]
            elif 'angel' in map_name:
                tower_configs = [
                    {'x': self.width // 2 - 3, 'y': 5, 'type': 'holy'},
                    {'x': 5, 'y': self.height // 2, 'type': 'holy'},
                    {'x': self.width - 8, 'y': self.height // 2, 'type': 'holy'},
                ]
            elif 'fire' in map_name or 'lava' in map_name:
                tower_configs = [
                    {'x': 7, 'y': 7, 'type': 'fire'},
                    {'x': self.width - 10, 'y': 7, 'type': 'fire'},
                    {'x': self.width // 2, 'y': self.height - 10, 'type': 'void'},
                ]
            else:
                tower_configs = [
                    {'x': 10, 'y': 10, 'type': 'fire'},
                    {'x': self.width - 13, 'y': 10, 'type': 'water'},
                ]

            # Create towers if the type is available
            for config in tower_configs:
                tower_type = config['type']
                if tower_type in available_towers or True:
                    x_pixel = config['x'] * self.tile_w
                    y_pixel = config['y'] * self.tile_h

                    # Check if location is not in collision
                    test_rect = pygame.Rect(
                        x_pixel, y_pixel, self.tile_w * 3, self.tile_h * 3)
                    if not any(test_rect.colliderect(r) for r in self.collision_rects):
                        tower = Tower(x_pixel, y_pixel, self.tile_w,
                                      self.tile_h, tower_type)
                        towers.append(tower)
                        print(
                            f"Spawned {tower_type} tower at ({x_pixel}, {y_pixel})")

        except Exception as e:
            print(f"Error building towers: {e}")

        return towers

    def build_npcs(self):
        npcs = []
        try:
            for obj in getattr(self.tmx_data, 'objects', []):
                obj_type = getattr(obj, 'type', '') or getattr(obj, 'name', '')
                obj_type_lower = str(obj_type).lower()

                if 'npc' in obj_type_lower or 'barman' in obj_type_lower or 'merchant' in obj_type_lower:
                    props = getattr(obj, 'properties', {}) or {}
                    custom_dialogues = []

                    i = 1
                    while True:
                        dialogue_key = f'dialogue{i}'
                        if dialogue_key in props:
                            custom_dialogues.append(props[dialogue_key])
                            i += 1
                        else:
                            break

                    npc_name = 'barman'
                    if 'barman' in obj_type_lower:
                        npc_name = 'barman'
                    elif 'merchant' in obj_type_lower:
                        npc_name = 'merchant'
                    else:
                        npc_name = obj_type

                    npc = NPC(int(obj.x), int(obj.y), self.tile_w, self.tile_h,
                              npc_name, custom_dialogues if custom_dialogues else None)
                    npcs.append(npc)
                    print(f"Found NPC '{npc_name}' at ({obj.x}, {obj.y})")
        except Exception as e:
            print(f"Error loading NPCs: {e}")
        return npcs

    def draw(self, surface, camera_x, camera_y):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, image in layer.tiles():
                    if image:
                        surface.blit(
                            image, (x*self.tile_w - camera_x, y*self.tile_h - camera_y))


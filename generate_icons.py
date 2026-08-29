"""
Hari Marg — PWA Placeholder Icon Generator
Generates saffron (#E8703A) background icons with white 'HM' text in the required sizes/names:
  - static/icons/icon-192.png (192x192)
  - static/icons/icon-512.png (512x512)
  - static/icons/icon-maskable-192.png (192x192)
  - static/icons/icon-maskable-512.png (512x512)
"""

import os
import struct
import zlib

ICON_SPECS = [
    ('icon-192.png', 192, 192),
    ('icon-512.png', 512, 512),
    ('icon-maskable-192.png', 192, 192),
    ('icon-maskable-512.png', 512, 512),
]

BG_HEX = "#E8703A"      # Saffron
BG_RGB = (232, 112, 58)
TEXT_RGB = (255, 255, 255) # White


def generate_icons_pillow(icons_dir):
    """Generate icons using Pillow library."""
    from PIL import Image, ImageDraw, ImageFont

    for filename, width, height in ICON_SPECS:
        img = Image.new("RGB", (width, height), BG_HEX)
        draw = ImageDraw.Draw(img)

        font_size = int(height * 0.4)
        font = None
        for font_name in ["arial.ttf", "DejaVuSans-Bold.ttf", "FreeSansBold.ttf"]:
            try:
                font = ImageFont.truetype(font_name, font_size)
                break
            except Exception:
                continue

        if font is None:
            try:
                font = ImageFont.load_default(size=font_size)
            except TypeError:
                font = ImageFont.load_default()

        text = "HM"
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            x = (width - text_w) / 2 - bbox[0]
            y = (height - text_h) / 2 - bbox[1]
        except AttributeError:
            text_w, text_h = draw.textsize(text, font=font)
            x = (width - text_w) / 2
            y = (height - text_h) / 2

        draw.text((x, y), text, fill="#FFFFFF", font=font)
        filepath = os.path.join(icons_dir, filename)
        img.save(filepath, "PNG")
        print(f"[Pillow] Created icon: {filepath} ({width}x{height})")


def generate_icons_fallback(icons_dir):
    """Fallback generator using standard Python library (zlib/struct) if Pillow is not available."""
    h_grid = [
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,1,1,1,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
    ]
    m_grid = [
        [1,0,0,0,1],
        [1,1,0,1,1],
        [1,0,1,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
        [1,0,0,0,1],
    ]

    grid_w, grid_h = 12, 7
    combined_grid = [h_grid[r] + [0, 0] + m_grid[r] for r in range(grid_h)]

    for filename, width, height in ICON_SPECS:
        scale = max(1, min(width // 20, height // 12))
        hm_w = grid_w * scale
        hm_h = grid_h * scale
        start_x = (width - hm_w) // 2
        start_y = (height - hm_h) // 2

        raw_rows = []
        for y in range(height):
            row_bytes = bytearray([0])
            for x in range(width):
                grid_x = (x - start_x) // scale
                grid_y = (y - start_y) // scale

                if (0 <= grid_x < grid_w) and (0 <= grid_y < grid_h) and (start_x <= x < start_x + hm_w) and (start_y <= y < start_y + hm_h):
                    if combined_grid[grid_y][grid_x] == 1:
                        row_bytes.extend(TEXT_RGB)
                    else:
                        row_bytes.extend(BG_RGB)
                else:
                    row_bytes.extend(BG_RGB)
            raw_rows.append(bytes(row_bytes))

        raw_data = b"".join(raw_rows)
        compressed_data = zlib.compress(raw_data)

        def make_chunk(chunk_type, data):
            content = chunk_type + data
            crc = zlib.crc32(content) & 0xffffffff
            return struct.pack(">I", len(data)) + content + struct.pack(">I", crc)

        signature = b"\x89PNG\r\n\x1a\n"
        ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
        ihdr_chunk = make_chunk(b"IHDR", ihdr_data)
        idat_chunk = make_chunk(b"IDAT", compressed_data)
        iend_chunk = make_chunk(b"IEND", b"")

        filepath = os.path.join(icons_dir, filename)
        with open(filepath, "wb") as f:
            f.write(signature + ihdr_chunk + idat_chunk + iend_chunk)
        print(f"[Fallback] Created icon: {filepath} ({width}x{height})")


def generate_icons():
    icons_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    try:
        generate_icons_pillow(icons_dir)
    except ImportError:
        generate_icons_fallback(icons_dir)


if __name__ == "__main__":
    generate_icons()

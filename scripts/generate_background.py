#!/usr/bin/env python3

import math
from pathlib import Path

from PIL import Image, ImageDraw


# =============================================================================
# 可调参数：通常只需要修改这一段
# =============================================================================

# 输出位置
OUTPUT_PATH = Path(__file__).resolve().parents[1] / "assets/styles/paper-background.png"

# 页面与清晰度
PAGE_SIZE_MM = (210, 297)       # A4：宽、高（毫米）
CSS_DPI = 96                    # 浏览器 CSS 的基准 DPI
RENDER_SCALE = 4                # 4 倍渲染，即最终图片约为 384 DPI

# 网格
GRID_SIZE_CSS_PX = 20           # 每个网格的边长
GRID_LINE_CSS_PX = 0.5          # 网格视觉线宽；4 倍渲染时会变成 2 个完整像素
GRID_COLOR = (239, 240, 247)    # 很浅的蓝紫灰

# 纸张底色
PAPER_COLOR = (255, 255, 253)   # 轻微暖白；纯白是 (255, 255, 255)

# 左上角柔和提亮
LIGHT_CENTER = (0.18, 0.12)     # 位置，范围 0～1
LIGHT_RADIUS = (0.34, 0.30)     # 横向、纵向影响范围
LIGHT_FALLOFF = 1.7             # 越大，过渡范围越集中
LIGHT_RGB_DELTA = (1.4, 1.5, 1.8)

# 右下角非常轻的冷色压暗
SHADE_CENTER = (0.82, 0.88)     # 位置，范围 0～1
SHADE_RADIUS = (0.40, 0.36)     # 横向、纵向影响范围
SHADE_FALLOFF = 1.8             # 越大，过渡范围越集中
SHADE_RGB_DELTA = (-2.0, -1.7, -0.5)

# 先在低分辨率下生成平滑明暗，再放大，避免随机噪点导致文件过大
TEXTURE_MAP_SIZE = (397, 561)

# PNG 无损压缩
PNG_COMPRESS_LEVEL = 9


# =============================================================================
# 生成逻辑：一般不需要修改
# =============================================================================


def gaussian_field(x, y, center, radius, falloff):
    dx = (x - center[0]) / radius[0]
    dy = (y - center[1]) / radius[1]
    return math.exp(-(dx * dx + dy * dy) * falloff)


def clamp_channel(value):
    return max(0, min(255, round(value)))


def build_paper_texture():
    width, height = TEXTURE_MAP_SIZE
    pixels = []

    for py in range(height):
        y = py / (height - 1)
        for px in range(width):
            x = px / (width - 1)

            light = gaussian_field(
                x, y, LIGHT_CENTER, LIGHT_RADIUS, LIGHT_FALLOFF
            )
            shade = gaussian_field(
                x, y, SHADE_CENTER, SHADE_RADIUS, SHADE_FALLOFF
            )

            color = tuple(
                clamp_channel(
                    PAPER_COLOR[channel]
                    + LIGHT_RGB_DELTA[channel] * light
                    + SHADE_RGB_DELTA[channel] * shade
                )
                for channel in range(3)
            )
            pixels.append(color)

    texture = Image.new("RGB", TEXTURE_MAP_SIZE)
    texture.putdata(pixels)
    return texture


def draw_grid(image, step, line_width):
    draw = ImageDraw.Draw(image)
    width, height = image.size

    for x in range(0, width, step):
        draw.rectangle(
            (x, 0, x + line_width - 1, height - 1),
            fill=GRID_COLOR,
        )

    for y in range(0, height, step):
        draw.rectangle(
            (0, y, width - 1, y + line_width - 1),
            fill=GRID_COLOR,
        )


def main():
    render_dpi = CSS_DPI * RENDER_SCALE
    page_width = round(PAGE_SIZE_MM[0] / 25.4 * render_dpi)
    page_height = round(PAGE_SIZE_MM[1] / 25.4 * render_dpi)
    grid_step = round(GRID_SIZE_CSS_PX * RENDER_SCALE)
    line_width = max(1, round(GRID_LINE_CSS_PX * RENDER_SCALE))

    texture = build_paper_texture()
    background = texture.resize(
        (page_width, page_height),
        Image.Resampling.BICUBIC,
    )
    draw_grid(background, grid_step, line_width)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    background.save(
        OUTPUT_PATH,
        format="PNG",
        optimize=True,
        compress_level=PNG_COMPRESS_LEVEL,
        dpi=(render_dpi, render_dpi),
    )

    print(f"wrote {OUTPUT_PATH}")
    print(f"size: {page_width}x{page_height}, {render_dpi} DPI")
    print(
        "grid: "
        f"{grid_step}px step, {line_width}px physical line "
        f"({line_width / RENDER_SCALE:g} CSS px)"
    )


if __name__ == "__main__":
    main()

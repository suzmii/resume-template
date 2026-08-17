#!/usr/bin/env python3

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

# 背景底图尺寸
TEXTURE_MAP_SIZE = (397, 561)

# PNG 无损压缩
PNG_COMPRESS_LEVEL = 9


# =============================================================================
# 生成逻辑：一般不需要修改
# =============================================================================






def build_paper_texture():
    return Image.new("RGB", TEXTURE_MAP_SIZE, PAPER_COLOR)


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

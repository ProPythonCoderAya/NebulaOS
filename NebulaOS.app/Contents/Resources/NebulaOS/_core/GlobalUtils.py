import xml.etree.ElementTree as ET
import cairosvg
import pygame
import math


def svgToPng(data: bytes, scale: int | float) -> bytes:
    root = ET.fromstring(data)
    width = float(root.attrib['width'])
    height = float(root.attrib['height'])
    end_data = cairosvg.svg2png(
        bytestring=data,
        output_width=width * scale,
        output_height=height * scale
    )
    return end_data


def replace_color(surf, old_c, new_c):
    img_copy = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    img_copy.fill(new_c)
    surf.set_colorkey(old_c)
    img_copy.blit(surf, (0, 0))
    return img_copy


def draw_rounded_rect(surface, color, rect, radius, alpha, *args):
    """Draws a rounded rectangle with transparency."""

    # Create a temporary surface with per-pixel alpha
    temp_surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)

    # Fill it with a unique color
    temp_surface.fill((110, 75, 58))

    # Draw the rounded rectangle in the desired color
    pygame.draw.rect(temp_surface, color, (0, 0, rect[2], rect[3]), *args, border_radius=radius)

    # Add alpha
    temp_surface = replace_color(temp_surface, color, (color[0], color[1], color[2], alpha))
    temp_surface.set_colorkey((110, 75, 58))

    # Blit onto the main surface
    surface.blit(temp_surface, (rect[0], rect[1]))


def draw_rect(surface, color, rect, br=-1, brtl=-1, brtr=-1, brbl=-1, brbr=-1):
    pygame.draw.rect(surface=surface, color=color, rect=rect, width=0, border_radius=br, border_top_left_radius=brtl, border_top_right_radius=brtr, border_bottom_left_radius=brbl, border_bottom_right_radius=brbr)


def distance(x1, y1, x2, y2):
    return math.dist((x1, y1), (x2, y2))


def sum_list(a, b):
    length = max(len(l) for l in (a, b))
    sum_list = []
    for i in range(length):
        sum_list.append(a[i] + b[i])
    return sum_list


__all__ = [
    "svgToPng",
    "replace_color",
    "draw_rounded_rect",
    "draw_rect"
]

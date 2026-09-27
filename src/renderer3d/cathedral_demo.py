import sys

import pygame
from pygame.locals import (
    DOUBLEBUF,
    OPENGL,
    QUIT,
    KEYDOWN,
    K_ESCAPE,
)

from OpenGL.GL import (
    GL_AMBIENT,
    GL_COLOR_BUFFER_BIT,
    GL_COLOR_MATERIAL,
    GL_DEPTH_BUFFER_BIT,
    GL_DEPTH_TEST,
    GL_DIFFUSE,
    GL_EXP2,
    GL_FOG,
    GL_FOG_COLOR,
    GL_FOG_DENSITY,
    GL_FOG_MODE,
    GL_FRONT_AND_BACK,
    GL_LEQUAL,
    GL_LIGHT0,
    GL_LIGHT1,
    GL_LIGHTING,
    GL_MODELVIEW,
    GL_NORMALIZE,
    GL_POSITION,
    GL_PROJECTION,
    GL_SMOOTH,
    GL_SPECULAR,
    GL_TRUE,
    GL_QUADS,
    glBegin,
    glClear,
    glClearColor,
    glColor3f,
    glColorMaterial,
    glDepthFunc,
    glEnable,
    glEnd,
    glFogi,
    glFogf,
    glFogfv,
    glLightfv,
    glLoadIdentity,
    glMaterialfv,
    glMatrixMode,
    glNormal3f,
    glPopMatrix,
    glPushMatrix,
    glRotatef,
    glShadeModel,
    glTranslatef,
    glVertex3f,
    glViewport,
)

from OpenGL.GLU import gluPerspective


WIDTH = 900
HEIGHT = 1200


# ============================================================
# Basic 3D box
# ============================================================

def draw_box(
    x,
    y,
    z,
    width,
    height,
    depth,
    color,
):
    hw = width / 2
    hd = depth / 2

    glColor3f(*color)

    glBegin(GL_QUADS)

    # Front
    glNormal3f(0, 0, 1)

    glVertex3f(
        x - hw,
        y,
        z + hd,
    )
    glVertex3f(
        x + hw,
        y,
        z + hd,
    )
    glVertex3f(
        x + hw,
        y + height,
        z + hd,
    )
    glVertex3f(
        x - hw,
        y + height,
        z + hd,
    )

    # Back
    glNormal3f(0, 0, -1)

    glVertex3f(
        x + hw,
        y,
        z - hd,
    )
    glVertex3f(
        x - hw,
        y,
        z - hd,
    )
    glVertex3f(
        x - hw,
        y + height,
        z - hd,
    )
    glVertex3f(
        x + hw,
        y + height,
        z - hd,
    )

    # Left
    glNormal3f(-1, 0, 0)

    glVertex3f(
        x - hw,
        y,
        z - hd,
    )
    glVertex3f(
        x - hw,
        y,
        z + hd,
    )
    glVertex3f(
        x - hw,
        y + height,
        z + hd,
    )
    glVertex3f(
        x - hw,
        y + height,
        z - hd,
    )

    # Right
    glNormal3f(1, 0, 0)

    glVertex3f(
        x + hw,
        y,
        z + hd,
    )
    glVertex3f(
        x + hw,
        y,
        z - hd,
    )
    glVertex3f(
        x + hw,
        y + height,
        z - hd,
    )
    glVertex3f(
        x + hw,
        y + height,
        z + hd,
    )

    # Top
    glNormal3f(0, 1, 0)

    glVertex3f(
        x - hw,
        y + height,
        z + hd,
    )
    glVertex3f(
        x + hw,
        y + height,
        z + hd,
    )
    glVertex3f(
        x + hw,
        y + height,
        z - hd,
    )
    glVertex3f(
        x - hw,
        y + height,
        z - hd,
    )

    # Bottom
    glNormal3f(0, -1, 0)

    glVertex3f(
        x - hw,
        y,
        z - hd,
    )
    glVertex3f(
        x + hw,
        y,
        z - hd,
    )
    glVertex3f(
        x + hw,
        y,
        z + hd,
    )
    glVertex3f(
        x - hw,
        y,
        z + hd,
    )

    glEnd()


# ============================================================
# Slanted arch beam
# ============================================================

def draw_beam(
    x,
    y,
    z,
    length,
    thickness,
    angle,
    color,
):
    glPushMatrix()

    glTranslatef(
        x,
        y,
        z,
    )

    glRotatef(
        angle,
        0,
        0,
        1,
    )

    draw_box(
        0,
        0,
        0,
        thickness,
        length,
        thickness,
        color,
    )

    glPopMatrix()


# ============================================================
# Pointed Gothic arch
# ============================================================

def draw_arch(
    center_x,
    base_y,
    z,
    width,
    height,
    color,
):
    half_width = width / 2

    vertical_height = height * 0.55
    sloped_length = (
        (half_width ** 2)
        + ((height - vertical_height) ** 2)
    ) ** 0.5

    angle = -(
        180.0
        / 3.14159265
    ) * (
        __import__("math").atan2(
            height - vertical_height,
            half_width,
        )
    )

    # Left upright
    draw_box(
        center_x - half_width,
        base_y,
        z,
        0.22,
        vertical_height,
        0.22,
        color,
    )

    # Right upright
    draw_box(
        center_x + half_width,
        base_y,
        z,
        0.22,
        vertical_height,
        0.22,
        color,
    )

    # Left pointed section
    draw_beam(
        center_x
        - half_width / 2,
        base_y + vertical_height,
        z,
        sloped_length,
        0.22,
        angle,
        color,
    )

    # Right pointed section
    draw_beam(
        center_x
        + half_width / 2,
        base_y + vertical_height,
        z,
        sloped_length,
        0.22,
        -angle,
        color,
    )


# ============================================================
# Cathedral structure
# ============================================================

def draw_cathedral():
    # --------------------------------
    # Materials / tones
    # --------------------------------

    floor_color = (
        0.07,
        0.045,
        0.08,
    )

    wall_color = (
        0.10,
        0.055,
        0.12,
    )

    column_color = (
        0.18,
        0.095,
        0.20,
    )

    column_capital_color = (
        0.24,
        0.13,
        0.25,
    )

    arch_color = (
        0.22,
        0.11,
        0.24,
    )

    altar_color = (
        0.26,
        0.10,
        0.20,
    )

    inner_color = (
        0.07,
        0.025,
        0.09,
    )

    # --------------------------------
    # Floor
    # --------------------------------

    draw_box(
        0,
        -0.25,
        -8,
        10.5,
        0.25,
        30,
        floor_color,
    )

    # --------------------------------
    # Side walls
    # --------------------------------

    draw_box(
        -5.3,
        0,
        -8,
        0.35,
        10.5,
        30,
        wall_color,
    )

    draw_box(
        5.3,
        0,
        -8,
        0.35,
        10.5,
        30,
        wall_color,
    )

    # --------------------------------
    # Columns
    # --------------------------------

    column_z_positions = (
        -1.0,
        -4.0,
        -7.0,
        -10.0,
        -13.0,
        -16.0,
    )

    for z in column_z_positions:

        for x in (
            -3.65,
            3.65,
        ):
            draw_box(
                x,
                0,
                z,
                0.72,
                7.0,
                0.72,
                column_color,
            )

            # Capital
            draw_box(
                x,
                7.0,
                z,
                1.1,
                0.35,
                1.1,
                column_capital_color,
            )

            # Capital top
            draw_box(
                x,
                7.35,
                z,
                0.85,
                0.18,
                0.85,
                arch_color,
            )

        # Side arches
        draw_arch(
            0,
            0,
            z,
            7.3,
            6.3,
            arch_color,
        )

    # --------------------------------
    # Ceiling ribs
    # --------------------------------

    for z in (
        -1,
        -4,
        -7,
        -10,
        -13,
        -16,
    ):
        # Left ceiling beam
        draw_beam(
            -2.35,
            8.2,
            z,
            5.0,
            0.18,
            -72,
            arch_color,
        )

        # Right ceiling beam
        draw_beam(
            2.35,
            8.2,
            z,
            5.0,
            0.18,
            72,
            arch_color,
        )

    # --------------------------------
    # Central altar block
    # --------------------------------

    draw_box(
        0,
        0,
        -19.0,
        3.2,
        1.9,
        1.3,
        altar_color,
    )

    draw_box(
        0,
        1.9,
        -19.0,
        2.25,
        2.0,
        0.9,
        column_capital_color,
    )

    # Central illuminated recess
    draw_box(
        0,
        3.9,
        -19.3,
        3.0,
        4.5,
        0.28,
        inner_color,
    )

    # Altar arch
    draw_arch(
        0,
        0,
        -19.7,
        4.2,
        8.0,
        arch_color,
    )

    # --------------------------------
    # Central aisle
    # --------------------------------

    draw_box(
        0,
        0.01,
        -8.0,
        2.4,
        0.04,
        24,
        (
            0.12,
            0.045,
            0.10,
        ),
    )


# ============================================================
# OpenGL setup
# ============================================================

def setup_opengl():
    glViewport(
        0,
        0,
        WIDTH,
        HEIGHT,
    )

    glMatrixMode(
        GL_PROJECTION
    )

    glLoadIdentity()

    gluPerspective(
        60.0,
        WIDTH / HEIGHT,
        0.1,
        100.0,
    )

    glMatrixMode(
        GL_MODELVIEW
    )

    # Depth
    glEnable(
        GL_DEPTH_TEST
    )

    glDepthFunc(
        GL_LEQUAL
    )

    # Smooth shading
    glShadeModel(
        GL_SMOOTH
    )

    # Materials use glColor
    glEnable(
        GL_COLOR_MATERIAL
    )

    glColorMaterial(
        GL_FRONT_AND_BACK,
        GL_AMBIENT
        | GL_DIFFUSE,
    )

    # Normalize lighting normals
    glEnable(
        GL_NORMALIZE
    )

    # --------------------------------
    # Lighting
    # --------------------------------

    glEnable(
        GL_LIGHTING
    )

    # Warm central light
    glEnable(
        GL_LIGHT0
    )

    glLightfv(
        GL_LIGHT0,
        GL_POSITION,
        (
            0.0,
            5.5,
            -17.5,
            1.0,
        ),
    )

    glLightfv(
        GL_LIGHT0,
        GL_AMBIENT,
        (
            0.10,
            0.045,
            0.08,
            1.0,
        ),
    )

    glLightfv(
        GL_LIGHT0,
        GL_DIFFUSE,
        (
            0.75,
            0.38,
            0.48,
            1.0,
        ),
    )

    # --------------------------------
    # Cool purple fill light
    # --------------------------------

    glEnable(
        GL_LIGHT1
    )

    glLightfv(
        GL_LIGHT1,
        GL_POSITION,
        (
            0.0,
            8.0,
            -5.0,
            1.0,
        ),
    )

    glLightfv(
        GL_LIGHT1,
        GL_AMBIENT,
        (
            0.03,
            0.015,
            0.05,
            1.0,
        ),
    )

    glLightfv(
        GL_LIGHT1,
        GL_DIFFUSE,
        (
            0.18,
            0.08,
            0.30,
            1.0,
        ),
    )

    # --------------------------------
    # Fog
    # --------------------------------

    glEnable(
        GL_FOG
    )

    glFogi(
        GL_FOG_MODE,
        GL_EXP2,
    )

    glFogfv(
        GL_FOG_COLOR,
        (
            0.008,
            0.004,
            0.015,
            1.0,
        ),
    )

    glFogf(
        GL_FOG_DENSITY,
        0.018,
    )

    # --------------------------------
    # Background
    # --------------------------------

    glClearColor(
        0.008,
        0.004,
        0.012,
        1.0,
    )


# ============================================================
# Main demo
# ============================================================

def main():
    pygame.init()

    pygame.display.set_caption(
        "Gesture Visual Controller - 3D Cathedral"
    )

    pygame.display.set_mode(
        (
            WIDTH,
            HEIGHT,
        ),
        DOUBLEBUF | OPENGL,
    )

    setup_opengl()

    clock = pygame.time.Clock()

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:

                if event.key == K_ESCAPE:
                    running = False

        # --------------------------------
        # Clear
        # --------------------------------

        glClear(
            GL_COLOR_BUFFER_BIT
            | GL_DEPTH_BUFFER_BIT
        )

        # --------------------------------
        # Camera
        # --------------------------------

        glLoadIdentity()

        glTranslatef(
            0.0,
            -2.7,
            -10.5,
        )

        # --------------------------------
        # Cathedral
        # --------------------------------

        draw_cathedral()

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
def register_koala():
    import turtle
    scale = 5
    shape = ((0, 0), (2 * scale, -1 * scale), (0, 4 * scale), (-2 * scale, -1 * scale))

    turtle.register_shape('koala', shape)
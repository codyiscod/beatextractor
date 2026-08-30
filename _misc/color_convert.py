def rgb_to_hex(r, g, b):
    # values come in 0–1 so scale up to 0–255
    r = int(r * 255)
    g = int(g * 255)
    b = int(b * 255)

    return "{:02X}{:02X}{:02X}FF".format(r, g, b)

# example usage
color = {
      "r": 0.7254902,
      "g": 0.7254902,
      "b": 0.7254902
}

hex_code = rgb_to_hex(color["r"], color["g"], color["b"])
print(hex_code)

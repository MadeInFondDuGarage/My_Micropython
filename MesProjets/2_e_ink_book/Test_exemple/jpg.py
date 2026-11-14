import t547

display = display = t547.T547()
display.init()
display.clear()
display.power(True)
#display.rotation(display.ROT_PORTRAIT)
display.jpg("oeil.jpg", 0, 0)
display.show()
display.power(False)
display.deinit()
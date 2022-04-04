from PIL import Image

im = Image.open("static/img/icon_user.png")
im2 = im.resize((60, 60))
im2.save('static/img/icon_user.png')
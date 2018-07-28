from PIL import Image, ImageDraw, ImageFont, ImageFilter
from random import randint
import hashlib


def ranchar():
	i = randint(1, 3)
	if i == 1:
		return chr(randint(65, 90))
	elif i == 2:
		return chr(randint(97, 122))
	else:
		return chr(randint(48, 57))


def rancolor():
	return (randint(64, 255), randint(64, 255), randint(64, 255))


def rancolor2():
	return (randint(32, 127), randint(32, 127), randint(32, 127))


def get_check_code():
	width = 240
	height = 60
	image = Image.new('RGB', (width, height), (255, 255, 255))
	# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 36)
	font = ImageFont.truetype('static/arial.ttf', 36)
	draw = ImageDraw.Draw(image)
	code = ''
	for x in range(width):
		for y in range(height):
			draw.point((x, y), fill=rancolor())
	for t in range(4):
		code_char = ranchar()
		code += code_char
		draw.text((60 * t + 10, 10), code_char, font=font, fill=rancolor2())
	image = image.filter(ImageFilter.BLUR)
	path = ''
	for c in range(4):
		path_char = ranchar()
		path += path_char
	image.save('static/image/code/code' + path + '.jpg', 'jpeg')
	md5 = hashlib.md5()
	md5.update(code.lower().encode(encoding='utf-8'))
	return code.lower(), md5.hexdigest(), path

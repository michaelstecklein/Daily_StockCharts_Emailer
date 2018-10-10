from PIL import Image


WHITE_TRESHOLD = 200


def __find_min_mse_line(I, value, horizontal=True, num=None):
	if horizontal: # x is rows y is cols
		coords = lambda x,y: (y,x)
		non_line_size = I.height
		line_size = I.width
	else: # vertical, x is cols y is rows
		coords = lambda x,y: (x,y)
		non_line_size = I.width
		line_size = I.height
	values = []
	for x in range(non_line_size):
		mse = 0
		for y in range(line_size):
			px_val = I.getpixel(coords(x,y))
			local_mse = (value - px_val)**2
			mse += local_mse
		mse /= float(line_size)
		values.append((x, mse))
	values.sort(key=lambda tpl: tpl[1]) # sort by MSE
	if num is None:
		return values[0][0]
	num_values = values[:num]
	num_values.sort(key=lambda tpl: tpl[0]) # sorted by row/col
	return num_values

def __right_margin_crop(I):
	c = __find_min_mse_line(I, 192, horizontal=False)
	return I.crop([c, 0, I.width, I.height])

def __horiz_trim(I):
	rows = __find_min_mse_line(I, 0, horizontal=True, num=2)
	rows.sort(key=lambda tpl: tpl[0])
	return I.crop([0, rows[0][0]+1, I.width, rows[1][0]])

def __right_trim(I):
	c = __find_min_mse_line(I, 0, horizontal=False)
	return I.crop([0, 0, c, I.height])

def __is_white_col(I, c):
	for r in range(I.height):
		if I.getpixel((c,r)) < WHITE_TRESHOLD:
			return False
	return True

def __is_white_row(I, r):
	for c in range(I.width):
		if I.getpixel((c,r)) < WHITE_TRESHOLD:
			return False
	return True

def __white_border_trim(I):
	# find left trim
	c_left = 0
	while __is_white_col(I, c_left):
		c_left += 1
	# find right trim
	c_right = I.width-1
	while __is_white_col(I, c_right):
		c_right -= 1
	# find lower trim
	r_lower = 0
	while __is_white_row(I, r_lower):
		r_lower += 1
	# find upper trim
	r_upper = I.height-1
	while __is_white_row(I, r_upper):
		r_upper -= 1
	return I.crop([c_left, r_lower, c_right+1, r_upper+1])

def __remove_nondigit_cols(I):
	''' Digits will be to the right of the last column with black in the
	first or last row. Remove these columns from front. '''
	BLK = 10
	c_crop = 0
	for c in range(I.width):
		if I.getpixel((c,0)) < BLK or I.getpixel((c,I.height-1)) < BLK:
			c_crop = c
	return I.crop([c_crop+1, 0, I.width, I.height])

def threshold_img(I, threshold):
	for r in range(I.height):
		for c in range(I.width):
			p = I.getpixel((c,r))
			if p != 0 and p != 255:
				if p < threshold:
					I.putpixel((c,r), 0)
				else:
					I.putpixel((c,r), 255)

def get_next_char(I):
	MAX_CHAR_LEN = 6
	if I is None or I.width <= 0:
		return None, None
	c_start = 0
	while c_start < I.width and __is_white_col(I, c_start):
		c_start += 1
	c_end = c_start
	while c_end < I.width and not __is_white_col(I, c_end) and c_end-c_start < MAX_CHAR_LEN:
		c_end += 1
	if c_start == I.width:
		I_char = None
	else:
		I_char = I.crop([c_start, 0, c_end, I.height])
	if c_end == I.width:
		I_remainder = None
	else:
		I_remainder = I.crop([c_end, 0, I.width, I.height])
	return I_char, I_remainder

def get_digits_from_chart(I_chart):
	I_chart = I_chart.convert('L') # b/w
	I_horiz_crop = I_chart.crop(
			[int(I_chart.width*0.85), 0, I_chart.width, int(I_chart.height*0.25)])
	I_right_margin = __right_margin_crop(I_horiz_crop)
	I_horiz_trim = __horiz_trim(I_right_margin)
	I_right_trim = __right_trim(I_horiz_trim)
	threshold_img(I_right_trim, 130)
	I_noise_trim = __remove_nondigit_cols(I_right_trim)
	I_trimmed = __white_border_trim(I_noise_trim)
	# split into chars
	I_char, I_remainder = get_next_char(I_trimmed)
	I_digits = []
	while I_char is not None:
		I_digits.append(I_char)
		I_char, I_remainder = get_next_char(I_remainder)
	return I_digits

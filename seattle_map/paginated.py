import requests
from io import BytesIO
from math import log, exp, tan, atan, pi, ceil
from PIL import Image


GOOGLE_MAPS_API_KEY = 'AIzaSyDCgp91ye2qMkd23v1tFp0bLYFTp0dJsc8'

R = 1 #6378137
X_MERC_MAX = 2*R*pi
Y_MERC_MAX = R * (log(tan(pi/4 + 85*pi/360)) - log(tan(pi/4 - 85*pi/360)))


def lon_to_x(lon):

	theta = lon*pi/180

	x_merc = R*(pi + theta)
	

	return x_merc/X_MERC_MAX*256

def lat_to_y(lat):

	phi = lat*pi/180

	y_merc = R * (log(tan(pi/4 + 85*pi/360)) - log(tan(pi/4 + phi/2)))

	return y_merc/Y_MERC_MAX*256


def xy_to_pixels(x, y, zoom = 17):

	return int(x*2**zoom), int(y*2**zoom)



def pixels_to_latlon(px, py, zoom):

	x, y = px/(2**zoom), py/(2**zoom)

	x_merc = x*X_MERC_MAX/256
	theta = x_merc/R - pi
	lon = theta*180/pi

	y_merc = y*Y_MERC_MAX/256
	phi = 2*atan(tan(pi/4 + 85*pi/360)*exp(-y_merc/R)) - pi/2

	lat = phi*180/pi

	return lat, lon

####### Locked in Parameters #######	

image_height = 640
image_width = 495

####### Params to specify ##########

lat_glob_top_left, lon_glob_top_left = 47.717169, -122.409921  # Test area 47.682740, -122.330425  Narrower area 47.717169, -122.409921 # Biggest area 47.715080, -122.438202
lat_glob_bot_right, lon_glob_bot_right = 47.512090, -122.239463 # Test area 47.675865, -122.320085 Narrower area 47.512090, -122.239463 # Total area 47.554528, -122.234731

x_images_per_page = 2
y_images_per_page = 2

zoom = 15

#####################################

px_glob_top_left, py_glob_top_left = xy_to_pixels(lon_to_x(lon_glob_top_left), lat_to_y(lat_glob_top_left), zoom)
px_glob_bot_right, py_glob_bot_right = xy_to_pixels(lon_to_x(lon_glob_bot_right), lat_to_y(lat_glob_bot_right), zoom)
delta_px = px_glob_bot_right - px_glob_top_left
delta_py = py_glob_bot_right - py_glob_top_left

num_x_pages = ceil(delta_px/image_width/x_images_per_page)
num_y_pages = ceil(delta_py/image_height/y_images_per_page)

px_glob_bot_right_rounded = px_glob_top_left + num_x_pages*x_images_per_page*image_width
py_glob_bot_right_rounded = py_glob_top_left + num_y_pages*y_images_per_page*image_height

lat_glob_bot_right_rounded, lon_glob_bot_right_rounded = pixels_to_latlon(px_glob_bot_right_rounded, py_glob_bot_right_rounded, zoom)

print("x, y images per page:", x_images_per_page, y_images_per_page)
print("zoom:", zoom)

print("Top Left lat lon:", lat_glob_top_left, lon_glob_top_left)
print("Bottom Right lat lon:", lat_glob_bot_right, lon_glob_bot_right)
print("Top Left px, py:", px_glob_top_left, py_glob_top_left)
print("Bottom Right px, py:", px_glob_bot_right, py_glob_bot_right)
print("Rounding:")
print(f"px bottom right rounded from {px_glob_bot_right} -> {px_glob_bot_right_rounded}")
print(f"py bottom right rounded from {py_glob_bot_right} -> {py_glob_bot_right_rounded}")
print(f"Delta px rounded from {delta_px} -> {num_x_pages*x_images_per_page*image_width}")
print(f"Lon global bottom right rounded from {lon_glob_bot_right} -> {lon_glob_bot_right_rounded}")
print(f"Delta py rounded from {delta_py} -> {num_y_pages*y_images_per_page*image_height}")
print(f"Lat global bottom right rounded from {lat_glob_bot_right} -> {lat_glob_bot_right_rounded}")
print("Number x, y, total pages:", num_x_pages, num_y_pages, num_x_pages*num_y_pages)
print("Number x, y, total images:", num_x_pages*x_images_per_page, num_y_pages*y_images_per_page, num_x_pages*x_images_per_page*num_y_pages*y_images_per_page)




url = 'http://maps.google.com/maps/api/staticmap'
urlparams = {
	'center': '',
    'zoom': f'{zoom}',
    'size': f'{image_width}x{image_height}',
    'scale': '1',
    'style': 'feature:poi|element:labels|visibility:off',
    'key': GOOGLE_MAPS_API_KEY
}

for page_row in range(1,num_y_pages+1):
	for page_col in range(1,num_x_pages+1):

		image = Image.new("RGB", (image_width*x_images_per_page, image_height*y_images_per_page))

		print("Page row, col:", page_row, page_col)
		px_top_left = px_glob_top_left + (page_col - 1)*x_images_per_page*image_width
		py_top_left = py_glob_top_left + (page_row - 1)*y_images_per_page*image_height

		for image_row in range(1, x_images_per_page + 1):
			for image_col in range(1, y_images_per_page + 1):

				print("Image row, col:", image_row, image_col)

				px_center = px_top_left + (image_col - 1/2)*image_width
				py_center = py_top_left + (image_row - 1/2)*image_height

				print('px_center, py_center:', px_center, py_center)

				lat, lon = pixels_to_latlon(px_center, py_center, zoom)
				print('lat_center, lon_center:', lat, lon)

				urlparams['center'] = f"{lat},{lon}"   
				response = requests.get(url, params=urlparams)
				im = Image.open(BytesIO(response.content))              
				image.paste(im, ((image_col-1)*image_width, (image_row-1)*image_height))

		image.save(f"Row_{page_row}_Col_{page_col}.png", format = "png")  




















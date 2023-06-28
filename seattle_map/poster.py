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

####### Params to specify ##########

lat_glob_top_left, lon_glob_top_left =  47.730225, -122.411856 # 4x6: 47.712749, -122.438267 
lat_glob_bot_right, lon_glob_bot_right = 47.510123, -122.244831 # 4x6: 47.510123, -122.239568 

zoom = 16

scale = 2

poster_height = 6  # feet
poster_width = 3 # 4   # feet

####### Locked in Parameters #######	

image_height = 600  # remove bottom 60
bottom_buffer = 40 #60
image_width = 280  # 360

#####################################

px_top_left, py_top_left = xy_to_pixels(lon_to_x(lon_glob_top_left), lat_to_y(lat_glob_top_left), zoom)
px_bot_right, py_bot_right = xy_to_pixels(lon_to_x(lon_glob_bot_right), lat_to_y(lat_glob_bot_right), zoom)
delta_px_raw = px_bot_right - px_top_left

num_x_images = ceil(delta_px_raw/image_width)
delta_px = num_x_images*image_width

delta_py = int(delta_px*poster_height/poster_width)
num_y_images = int(delta_py/(image_height - bottom_buffer))

lat_rounded_bot_right, lon_rounded_bot_right = pixels_to_latlon(px_top_left + delta_px, py_top_left + delta_py, zoom)


print("zoom:", zoom)
print("Inputted Top Left lat lon:", lat_glob_top_left, lon_glob_top_left)
print("Inputted Bottom Right lat lon:", lat_glob_bot_right, lon_glob_bot_right)
print(f"Delta px rounded from {delta_px_raw} -> {delta_px}")
print(f"Delta py calculated to be {delta_py}")
print(f"Bottom right lat lon calculated to be: {lat_rounded_bot_right}, {lon_rounded_bot_right}")
print("x, y, total images:", num_x_images, num_y_images, num_x_images*num_y_images)
print("Horizontal DPI:", num_x_images*image_width*scale/(poster_width*12))
print("Vertical DPI:", num_y_images*(image_height - bottom_buffer)*scale/(poster_height*12))

url = 'http://maps.google.com/maps/api/staticmap'
urlparams = {
	'center': '',
    'zoom': f'{zoom}',
    'size': f'{image_width}x{image_height}',
    'scale': f'{scale}',
    'style': 'feature:poi|element:labels|visibility:off',
    'key': GOOGLE_MAPS_API_KEY
}

image = Image.new("RGB", (image_width*num_x_images*scale, (image_height - bottom_buffer)*num_y_images*scale))

for image_row in range(0, num_x_images):
	print("Image row:", image_row)
	for image_col in range(0, num_y_images):

		# print("Image row, col:", image_row, image_col)


		px_center = px_top_left + image_col*image_width + image_width/2  
		py_center = py_top_left + image_row*image_height + image_height/2 - image_row*bottom_buffer   

		#print('px_center, py_center:', px_center, py_center)

		lat, lon = pixels_to_latlon(px_center, py_center, zoom)
		#print('lat_center, lon_center:', lat, lon)

		urlparams['center'] = f"{lat},{lon}"   
		response = requests.get(url, params=urlparams)
		im = Image.open(BytesIO(response.content))              
		image.paste(im, (image_col*image_width*scale, image_row*image_height*scale - image_row*bottom_buffer*scale))

	# image.save(f"1.png", format = "png")

	# asdfsd
		

image.save(f"1.png", format = "png")  




















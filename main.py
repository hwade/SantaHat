# -*- coding: utf-8 -*-

import cv2
import fire
import numpy as np
from tqdm import tqdm 
from PIL import Image
import face_recognition
import matplotlib.image as mpimg

def paste_img(basic_img, add_img, last_locs):
	'''
		Paste add_img to basic_img
		@basic_img: Image object
		@add_img: Image object
		@last_locs
	'''
	#basic_img = Image.open(basic_path)
	#add_img = Image.open(add_path)

	toImage = Image.new('RGB', basic_img.size)
	if len(np.array(basic_img).shape) == 3 and np.array(basic_img).shape[2] == 4:
		basic_img = basic_img.convert('RGB')

	#img_array = face_recognition.load_image_file(basic_path)
	face_locs = face_recognition.face_locations(np.array(basic_img))
	if last_locs == None:
		last_locs = face_locs

	toImage.paste(basic_img)
	for nloc in face_locs:	
		dists = [sum((np.array(nloc) - np.array(lloc))**2) for lloc in last_locs]
		last_loc = np.array(last_locs[dists.index(min(dists))])
		new_loc = last_loc + (last_loc- np.array(nloc))/10.

		width = int((new_loc[1]-new_loc[3])*1.5)
		height = int(new_loc[2]-new_loc[0])
		add_img_resize = add_img.resize((width, height), Image.ANTIALIAS)

		toImage.paste(add_img_resize, (int((new_loc[3]+new_loc[1]-5*width/7)/2), int(new_loc[0]-3*height/5)), 
					  mask=add_img_resize)

	return toImage, face_locs if len(face_locs)!=0 else None

def main(**opt):

	add_img = Image.open(opt['add_path'])

	last_locs = None
	if opt['is_video']:
		input_movie = cv2.VideoCapture(opt['video_path'])
		length = int(input_movie.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))

		fourcc = cv2.cv.CV_FOURCC(*'MJPG')
		fps = input_movie.get(cv2.cv.CV_CAP_PROP_FPS)
		width = int(input_movie.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
		height = int(input_movie.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
		output_movie = cv2.VideoWriter(opt['save_path'], fourcc, fps, (width, height))
		
		for i in tqdm(xrange(length)):
			ret, frame = input_movie.read()
			if not ret:
				break
			frame, last_locs = paste_img(Image.fromarray(frame), add_img, last_locs)
			#cv2.imshow('frame',cv2.flip(np.array(frame),1))
			#output_movie.write(cv2.flip(frame,1))
			output_movie.write(np.array(frame))
			#cv2.waitKey(1)
		input_movie.release()
		output_movie.release()
		cv2.destroyAllWindows()
	else:
		basic_img = Image.open(opt['file_path'])
		toImage, last_locs = paste_img(basic_img, add_img, last_locs)
		toImage.save(opt['save_path'])

if __name__ == '__main__':

	fire.Fire()

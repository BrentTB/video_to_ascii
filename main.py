from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np
import cv2
import moviepy.editor as mp
import os
import random
import string

show_message = True # sends messages as the code progresses
save_img = True # save each individual image of the new video
reduce_img = False # reduce the quality of the images in the video

mediaFolder = "media" # stores the videos
VideoTempFolder = "Z-temp" # stores the images if save_img = True

def main():
    type = 'v'

    if type == 'i':
        pixel_reduction = 1  # one in every 'pixel_reduction' pixels are used
        makeImage("testPic1.png", "testPic1Ascii", pixel_reduction)
    else:
        pixel_reduction = 15 # one in every 'pixel_reduction' pixels are used
        frame_reduction = 5 # one in every 'frame_reduction' frames are used
        video("loki2.mp4", "asciiVideo", pixel_reduction, frame_reduction)

def makeRandomString():
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for i in range(10))
        return random_string

def makeImage(fileName, newName, pixel_reduction):
    ''' fileName: The old file name (Assumed to be in the 'media' folder) 

    newName: The new name, not including an extention

    pixel_reduction: 1 in every 'pixel_reduction'*2 horizontal pixels are used, and 1 in every 'pixel_reduction' vertical pixels are used'''
    img = Image.open(f"{mediaFolder}/{fileName}")
    image(img, 0, pixel_reduction, 0, newName)

def videoFromImages(vid, new_file_name, frame_reduction=-1):
    ''' Used when the images have been created already

    vid: the file name of the video

    new_file_name: the new video name without any extensions
    
    frame_reduction: 1 in every frame_reduction frames are turnt into an image. Leave blank for 4fps final video'''

    vid = mediaFolder+"/" + vid
    vidcap = cv2.VideoCapture(vid)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    vidcap.release()

    if(frame_reduction == -1):
        frame_reduction = round(fps/4)

    img_array = []
    i=0
    
    # find all the images that have been created
    while(os.path.isfile(f"{VideoTempFolder}/frame{i}.png")):
        imgTmp = Image.open(f"{VideoTempFolder}/frame{i}.png")
        img_array.append(imgTmp)
        i = i+1

    frameRate = fps / frame_reduction
    make_vid(vid, new_file_name, img_array, frameRate)
    return

def video(vid, new_file_name, pixel_reduction, frame_reduction=-1):
    '''vid: the file name of the video

    new_file_name: the new video name without any extensions

    pixel_reduction: 1 in every pixel_reduction*2 horizontal pixels are used, and 1 in every pixel_reduction vertical pixels are used

    frame_reduction: 1 in every frame_reduction frames are turnt into an image. Leave blank for 4fps final video'''

    new_file_name = mediaFolder+"/"+new_file_name+".mp4"
    vid = mediaFolder+"/" + vid
    img_array = []

    vidcap = cv2.VideoCapture(vid)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print("The original video is", fps, "fps")

    if(frame_reduction == -1):
        frame_reduction = round(fps/4)

    total_frames = math.floor(vidcap.get(cv2.CAP_PROP_FRAME_COUNT) / frame_reduction)

    success, img = vidcap.read()
    imageOn, tmpC = 0, -1

    data = Image.fromarray(img)

    # repeat until the video runs out of frames
    while success:
        tmpC += 1
        if(tmpC % frame_reduction == 0):
            data = Image.fromarray(img)
            img_array.append(image(data, imageOn, pixel_reduction, total_frames))
            imageOn += 1
        success, img = vidcap.read()

    vidcap.release()

    frame_rate = fps / frame_reduction

    make_vid(vid, new_file_name, img_array, frame_rate)

def make_vid(old_file_name, new_file_name, img_array, frame_rate=4):
    '''Takes in a list of images, as well as the origional frame_reduction used (in order to edit the new framerate). Also takes in the new and old mp4 name

    Returns an mp4 file made of the inputted images'''

    if(show_message):
        print("Starting to make Video")

    height = img_array[0].height
    width = img_array[0].width

    size = (width, height)

    tmpName = f"tempVideo-{makeRandomString()}.mp4"
    out = cv2.VideoWriter(tmpName,cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, size)

    for i in range(len(img_array)):

        if (i % 50 == 0 and show_message):
            print(f"frame {i} processed")

        data = np.asarray(img_array[i])
        out.write(data)

    out.release()

    if(show_message):
        print("Done")

    add_audio(old_file_name, new_file_name, tmpName)

def add_audio(old_file_name, new_file_name, tmpName):
    '''adds the audio from the original video to the created video'''

    if(show_message):
        print("Starting to extract audio")

    tmpNameAudio = f"tempAudio-{makeRandomString()}.mp3"

    old_video = mp.VideoFileClip(f"{old_file_name}")
    old_video.audio.write_audiofile(tmpNameAudio)

    new_video = mp.VideoFileClip(tmpName)
    new_video.write_videofile(
        new_file_name, audio=tmpNameAudio)

    os.remove(tmpNameAudio)
    os.remove(tmpName)

    if(show_message):
        print("Audio Extraction done")

def image(image, index, reduction_factor, frames=0, newName=""):
    '''Takes an image, a reduction factor and a naming index

    Returns an Ascii image of the inputed image'''
    size = image.width, image.height
    data, w, h = make_grayscale(image, reduction_factor)
    txt = gray_to_text(data)
    return conv_frame(txt, w, h, index, frames, size, newName)

def make_grayscale(image, reduction_factor):
    '''Takes in image data as well as a reduction factor

    Returns a list of the grayscale data of the image, as well as the new images width and height'''

    # converts the image to grayscale
    pix_val_help = list(image.convert('L').getdata())

    height = image.height
    width = image.width
    h = math.floor(height/(2*reduction_factor))
    w = math.floor(width/reduction_factor)

    pix_val = []

    for row in range(h):
        pix_val.append([])
        for col in range(w):
            sum = 0

            for r in range(2*reduction_factor):
                for c in range(reduction_factor):
                    index = (row*reduction_factor*2 + r) * width
                    index += (col*reduction_factor + c)
                    sum += pix_val_help[index]

            sum = math.floor(sum/(2 * reduction_factor**2))
            pix_val[row].append(sum)

    return pix_val, w, h

def gray_to_text(gray):
    '''Takes in a grayscale image as a list and converts each pixel into a letter

    Returns a string of the resultant text'''

    txt = ""
    limit = "NM@B8&X§$#%ZI±+^,.- "

    for row in gray:
        for element in row:
            for index, lim in enumerate(limit):
                if(element < (index+1)*math.ceil(256/len(limit))):
                    txt += lim
                    break

        txt += "\n"

    return txt

def conv_frame(txt, w, h, index, total, size=-1, newName=""):
    '''Takes the dimensions of an image and text, as well as an index number for naming the image and the pixel resolution
    the image should be saved to (leave empty to keep the size unchanged)

    Returns an image with the inputted text'''

    if(show_message):
        # print(f"frame {index} done", end ='\r')
        print_percent_done(index, total)

    img = Image.new('RGB', (w*20, h*35), color=(255, 255, 255))

    d = ImageDraw.Draw(img)

    fnt = ImageFont.truetype("/System/Library/Fonts//Menlo.ttc", 33)
    d.multiline_text((0, 0), txt, fill=(0, 0, 0), font=fnt)

    if(size != -1 and reduce_img):
        # image files are too large, and the resuling mp4 was way too big
        img = img.resize(size, Image.ANTIALIAS)

    # img.show()

    if(newName):
        img.save(f'{mediaFolder}/{newName}.png')
    elif(save_img):
        img.save(f'{VideoTempFolder}/frame{index}.png')

    return img

def print_percent_done(index, total, bar_len=50, title='Please wait'):
    '''
    index is expected to be 0 based index. 
    0 <= index < total
    '''

    index += 1
    total += 1

    percent_done = index/total*100
    percent_done = round(percent_done, 1)

    done = round(percent_done/(100/bar_len))
    togo = bar_len-done

    done_str = '█'*int(done)
    togo_str = '░'*int(togo)

    # test this so the user cant type in terminal
    print(f'\r-> Frame {index} of {total} is being processed\t⏳{title}: [{done_str}{togo_str}] {percent_done}% done   ', end='')

    if round(percent_done) == 100:
        print('\tFrame Processing Complete'+' '*150)

if __name__ == "__main__":
    main()

# TODO: 
# make the program more efficient
# add multiprocessing 
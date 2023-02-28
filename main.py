from PIL import Image, ImageDraw, ImageFont
import math
import numpy as np
import cv2
import moviepy.editor as mp
import os

black = [0, 0, 0]
white = [255, 255, 255]

show_message = True
save_img = True
reduce_img = False

mediaFolder = "media" # media
VideoTempFolder = "Z-temp"

def main():

    # for i in range(1,15):
    #     makeImage(f"pic{i}.jpeg", f"pic{i}Ascii", 2)

    makeImage("testPic1.png", "testPic1Ascii", 1)

    # video("loki2.mp4", "test2", 15, 5)

    # best if frame_reduction is a divisor of fps (or close to a divisor, aka, fps % frame_reduction should be minimised)

def makeImage(fileName, newName, pixel_reduction):
    ''' The old file name (Assumed to be in the 'media' folder), enter with extention 

    The new name, not inclusing extention

    1 in every pixel_reduction*2 horizontal pixels are used, and 1 in every pixel_reduction vertical pixels are used'''
    img = Image.open(f"{mediaFolder}/{fileName}")
    image(img, 0, pixel_reduction, 0, newName)


def video(vid, new_file_name, pixel_reduction, frame_reduction=-1):
    '''Takes a video, and 2 reduction factors for the frame rate and pixels. Also takes in the new mp4 file name

    The new name should not include '.mp4' or any other file type

    1 in every pixel_reduction*2 horizontal pixels are used, and 1 in every pixel_reduction vertical pixels are used

    1 in every frame_reduction frames are turnt into an image. Leave blank for 4fps final video'''

    new_file_name = mediaFolder+"/"+new_file_name+".mp4"
    vid = mediaFolder+"/" + vid

    img_array = []

    if(1 == 2):  # to use already made images, use this (have to manually change repeat length)

        for i in range(620):
            imgTmp = Image.open(f"{VideoTempFolder}/frame{i}.png")
            img_array.append(imgTmp)

        make_vid(vid, new_file_name, img_array, 6)
        return

    vidcap = cv2.VideoCapture(vid)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    print("The origional video is", fps, "fps")

    if(frame_reduction == -1):
        frame_reduction = round(fps/4)

    total_frames = math.floor(vidcap.get(
        cv2.CAP_PROP_FRAME_COUNT) / frame_reduction)

    # print("The amount of frames to be pocessed is", total_frames, '\n')

    success, img = vidcap.read()
    count, tmpC = 0, 0

    data = Image.fromarray(img)

    img_array.append(image(data, count, pixel_reduction, total_frames))
    while success:
        tmpC += 1
        if(tmpC % frame_reduction == 0):
            count += 1
            data = Image.fromarray(img)
            img_array.append(image(data, count, pixel_reduction, total_frames))
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

    out = cv2.VideoWriter("tempVideo-sdvyjkl01h35f9.mp4",
                          cv2.VideoWriter_fourcc(*'mp4v'), frame_rate, size)

    for i in range(len(img_array)):

        if (i % 50 == 0 and show_message):
            print(f"frame {i} processed")

        data = np.asarray(img_array[i])
        out.write(data)

    out.release()

    if(show_message):
        print("Done")

    add_audio(old_file_name, new_file_name)


def add_audio(old_file_name, new_file_name):
    '''Takes in the name of the old and new files, extrcats the audio from the old file, and adds it to the new file'''

    if(show_message):
        print("Starting to extract audio")

    old_video = mp.VideoFileClip(rf"{old_file_name}")
    old_video.audio.write_audiofile(r"tempAudio-qkcosjd64i21a9.mp3")

    new_video = mp.VideoFileClip("tempVideo-sdvyjkl01h35f9.mp4")
    new_video.write_videofile(
        new_file_name, audio="tempAudio-qkcosjd64i21a9.mp3")

    os.remove("tempAudio-qkcosjd64i21a9.mp3")
    os.remove("tempVideo-sdvyjkl01h35f9.mp4")

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

    # Saves the grayscale image
    if(1 == 2):
        arry = np.array(pix_val)
        img = Image.fromarray(arry.astype(np.uint8))
        img.save('my.png')
        img.show()

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

    # 10-19-16
    # 20-35-33 -> using
    # 24-42-40


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
    print(
        f'\r-> Frame {index} of {total} is being processed\t⏳{title}: [{done_str}{togo_str}] {percent_done}% done   ', end='')

    if round(percent_done) == 100:
        print('\tFrame Processing Complete'+' '*150)


if __name__ == "__main__":
    main()

    '''
    Call in a loop to create terminal progress bar

    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\\r", "\\r\\n") (Str)
    '''


# # must test
# class keyboardDisable():

#     def start(self):
#         self.on = True

#     def stop(self):
#         self.on = False

#     def __call__(self):
#         while self.on:
#             msvcrt.getwch()


#     def __init__(self):
#         self.on = False
#         import msvcrt

# disable = keyboardDisable()
# disable.start()


# disable.stop()

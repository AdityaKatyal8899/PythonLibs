import ffmpeg

#Exisiting name of the video file 
input_video = input("Enter video file name: ")
input_video += '.mp4'
vid = ffmpeg.input(input_video)


#Existing name of audio file
input_audio = input("Enter audio file name ")
input_audio += '.mp3'
aud = ffmpeg.input(input_audio)

#Custom name for merged file
file_name = input("Name for the file: ")
file_name += '.mp4'
try:
  ffmpeg.output(vid, aud, file_name, vcodec='copy', acodec='aac', strict='experimental').run()
except Exception as e:
  print(f"{e}")


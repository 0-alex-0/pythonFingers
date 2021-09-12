#! /usr/bin/env python3

from pysgfplib import *
from ctypes import *
from os import listdir
from tkinter import *
from time import sleep

constant_hamster_pro20_width = 300
constant_hamster_pro20_height = 400
constant_sg400_template_size = 400
finger_width = constant_hamster_pro20_width
finger_height = constant_hamster_pro20_height


sgfplib = PYSGFPLib()

def start():
  result = sgfplib.Create()
  if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
     print("Create error\n");
     exit()
  else:
    print("Create OK\n")
  result = sgfplib.Init(SGFDxDeviceName.SG_DEV_AUTO)
  if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
     print("Init error\n");
     exit()
  else:
    print("Init OK\n")
  return result

def end():
  sgfplib.CloseDevice()
  sgfplib.Terminate()

def match(cMinutiaeBuffer1, cMinutiaeBuffer2):
  cMatched = c_bool(False)
  result = sgfplib.MatchTemplate(cMinutiaeBuffer1, cMinutiaeBuffer2, SGFDxSecurityLevel.SL_NORMAL, byref(cMatched));

  cScore = c_int(0)
  result = sgfplib.GetMatchingScore(cMinutiaeBuffer1, cMinutiaeBuffer2, byref(cScore));
  print("  Score : [" + str(cScore.value) + "]")
  return cMatched

def save_min(name, cMinutiaeBuffer):
  imageFile = open("prints/{}.min".format(name), "wb")
  imageFile.write(cMinutiaeBuffer)

def quality_check(cImageBuffer):
  cQuality = c_int(0)
  result = sgfplib.GetImageQuality(finger_width, finger_height, cImageBuffer, byref(cQuality))
  print("  Image quality : [" + str(cQuality.value) + "]")
  return cQuality.value

def capture(cap, file):
  #input("Capture {}. Please place {} on sensor and press <ENTER> ".format(cap, file));
  cImageBuffer = (c_char*finger_width*finger_height)()
  x = 0
  while (x == 0):
    result = sgfplib.GetImage(cImageBuffer)
    if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
    #imageFile = open("{}{}.raw".format(file, cap), "wb")
    #imageFile.write(cImageBuffer)
     x = 1
  #else:
    #print("  ERROR - Unable to capture image. retry\n");
    #capture(cap, file)

  qc = quality_check(cImageBuffer)

  cMinutiaeBuffer = (c_char*constant_sg400_template_size)()
  result = sgfplib.CreateSG400Template(cImageBuffer, cMinutiaeBuffer);
  if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
    #minutiaeFile = open("{}{}.min".format(file, cap), "wb")
    #minutiaeFile.write(cMinutiaeBuffer)
    pass
  else:
   print("  ERROR - Unable to create first template. Exiting\n");
   exit()

  return cMinutiaeBuffer, qc

def capture_check():
  filename = finger_input.get();
  cMinutiaeBuffer1, quality1 = capture(1, filename)
  sleep(2)
  cMinutiaeBuffer2, quality2 = capture(2, filename)
  cMatched = match(cMinutiaeBuffer1, cMinutiaeBuffer2)
  if (cMatched.value == True):
    print("MATCH");
    if quality1 >= quality2:
      save_min(filename, cMinutiaeBuffer1)
    else:
      save_min(filename, cMinutiaeBuffer1)
    return filename
  else:
    print("NO MATCH");

def check_in():
  file="check_in"
  fprints = listdir("prints")
  cMinutiaeBuffer3, quality3 = capture(0, file)
  for fprint in fprints:
    cMin = open("prints/{}".format(fprint), "rb")
    cMatched = match(cMin.read(), cMinutiaeBuffer3)
    if (cMatched.value == True):
      output.insert("end","{}[MATCH]::".format(fprint));
    else:
      #output.insert("end","{}[NO MATCH]::".format(fprint));
      pass



result = start()
result = sgfplib.OpenDevice(0)
if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
  print("  ERROR - Unable to initialize SecuGen library. Exiting\n");
  exit()
else:
  tk = Tk()
  tk.title("pythonFingers")

  frame = Frame(tk, relief=RIDGE, borderwidth=2, bg="grey")
  btnExit = Button(frame,text="Exit",command=tk.destroy)
  btnAdd = Button(frame,text="add fingerprint",command=capture_check)
  btnCheck_in = Button(frame,text="check for fingerprint",command=check_in)
  output = Text(tk, width=100, height=10, font=('Arial', 14))
  label_finger_input = Label(frame, width=38, font=('Arial', 14), bg="black", fg="white", text="NAME to ADD")
  finger_input = Entry(frame, width=38, font=('Arial', 14))

  label_finger_input.pack(side=TOP, anchor=NW)
  frame.pack(fill=BOTH,expand=1)
  btnExit.pack(side=BOTTOM, pady=10)
  btnCheck_in.pack(side=RIGHT, pady=10, anchor=NE)
  finger_input.pack(side=TOP, pady=10, anchor=NW)
  btnAdd.pack(pady=10, anchor=SW)
  output.pack(pady=5)

  tk.mainloop()

end()

#! /usr/bin/env python3

from pysgfplib import *
from ctypes import *
from os import listdir, mkdir
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

def mkEmail(name, emailInput):
  if(bool(emailInput) == True):
    email = open("emails/{}".format(name), "w")
    email.write(emailInput)

def save_min(name, cMinutiaeBuffer):
  taken = 0
  if(bool(name) == True):
    fprints = listdir("prints")
    for fprint in fprints:
      if(fprint == "{}.min".format(name)):
        taken = 1
        print("name in use")
        output.insert("end","name in use: {}   ".format(fprint));
      cMin = open("prints/{}".format(fprint), "rb")
      cMatched = match(cMin.read(), cMinutiaeBuffer)
      if (cMatched.value == True):
        taken = 1
        print("finger in use")
        output.insert("end","finger in use: {}   ".format(fprint));
    if(taken == 0):
      imageFile = open("prints/{}.min".format(name), "wb")
      imageFile.write(cMinutiaeBuffer)

def quality_check(cImageBuffer):
  cQuality = c_int(0)
  result = sgfplib.GetImageQuality(finger_width, finger_height, cImageBuffer, byref(cQuality))
  print("  Image quality : [" + str(cQuality.value) + "]")
  return cQuality.value

def capture(cap, file):
  cImageBuffer = (c_char*finger_width*finger_height)()
  x = 0
  while (x == 0):
    result = sgfplib.GetImage(cImageBuffer)
    if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
     x = 1

  qc = quality_check(cImageBuffer)

  cMinutiaeBuffer = (c_char*constant_sg400_template_size)()
  result = sgfplib.CreateSG400Template(cImageBuffer, cMinutiaeBuffer);
  if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
    pass
  else:
   print("  ERROR - Unable to create first template. Exiting\n");
   #exit()

  return cMinutiaeBuffer, qc

def capture_check():
  filename = finger_input.get()
  emailInput = email_input.get()
  if(bool(filename) == True and bool(emailInput) == True):
    cMinutiaeBuffer1, quality1 = capture(1, filename)
    sleep(2)
    cMinutiaeBuffer2, quality2 = capture(2, filename)
    cMatched = match(cMinutiaeBuffer1, cMinutiaeBuffer2)
    if (cMatched.value == True):
      output.insert("end","[FINGER ADDED]");
      if quality1 >= quality2:
        cMinutiaeBuffer = cMinutiaeBuffer1
      else:
        cMinutiaeBuffer = cMinutiaeBuffer2
      save_min(filename, cMinutiaeBuffer)
      mkEmail(filename, emailInput)
      return filename
    else:
      output.insert("end"," [FINGER NOT ADDED] ");
  else:
    output.insert("end"," [MISSING DATA] ");

def check_in():
  file="check_in"
  fprints = listdir("prints")
  cMinutiaeBuffer3, quality3 = capture(0, file)
  for fprint in fprints:
    cMin = open("prints/{}".format(fprint), "rb")
    cMatched = match(cMin.read(), cMinutiaeBuffer3)
    if (cMatched.value == True):
      output.insert("end"," {} [MATCH] ".format(fprint));
    else:
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
  frameAdd = Frame(frame, relief=RIDGE, borderwidth=2, bg="grey")
  frameCheck = Frame(frame, relief=RIDGE, borderwidth=2, bg="grey")
  frameOutput = Frame(tk, relief=RIDGE, borderwidth=2, bg="black")
  btnExit = Button(frameOutput,text="Exit",command=tk.destroy, bg="white", fg="black")
  btnAdd = Button(frameAdd,text="add fingerprint",command=capture_check)
  btnCheck_in = Button(frameCheck,text="check for fingerprint",command=check_in)
  output = Text(frameOutput, width=100, height=10, font=('Arial', 14))
  label_email_input = Label(frameAdd, width=38, font=('Arial', 14), bg="black", fg="white", text="EMAIL to ADD")
  label_finger_input = Label(frameAdd, width=38, font=('Arial', 14), bg="black", fg="white", text="NAME to ADD")
  label_finger_check = Label(frameAdd, width=38, font=('Arial', 14), bg="black", fg="white", text="Check Fingerprint")
  finger_input = Entry(frameAdd, width=38, font=('Arial', 14))
  email_input = Entry(frameAdd, width=38, font=('Arial', 14))

  frame.pack(side=TOP, fill=BOTH, expand=1)
  frameAdd.pack(side=LEFT, anchor=NW, fill=BOTH, expand=.5)
  frameCheck.pack(side=RIGHT, anchor=NE, fill=BOTH, expand=.5)
  frameOutput.pack(side=BOTTOM, fill=BOTH, expand=1)
  label_finger_input.pack(pady=5)
  finger_input.pack(pady=5)
  label_email_input.pack(pady=5)
  email_input.pack(pady=5)
  btnCheck_in.pack(pady=5)
  btnAdd.pack(pady=5)
  output.pack(pady=5)
  btnExit.pack(side=BOTTOM)

  tk.mainloop()

end()

#! /usr/bin/env python3

from pysgfplib import *
from ctypes import *
from shutil import *

constant_hamster_pro20_width = 300
constant_hamster_pro20_height = 400
constant_sg400_template_size = 400
finger_width = constant_hamster_pro20_width
finger_height = constant_hamster_pro20_height


sgfplib = PYSGFPLib()

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
  input("Capture {}. Please place {} on sensor and press <ENTER> ".format(cap, file));
  cImageBuffer = (c_char*finger_width*finger_height)()
  result = sgfplib.GetImage(cImageBuffer)
  if (result == SGFDxErrorCode.SGFDX_ERROR_NONE):
    #imageFile = open("{}{}.raw".format(file, cap), "wb")
    #imageFile.write(cImageBuffer)
    pass
  else:
    print("  ERROR - Unable to capture first image. Exiting\n");
    exit()

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

  result = sgfplib.OpenDevice(0)
  if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
     print("  ERROR - Unable to initialize SecuGen library. Exiting\n");
     exit()
  else:
    filename = input('Which finger would you like to test with (no spaces)? (e.g. lt) >> ');
    cMinutiaeBuffer1, quality1 = capture(1, filename)

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

def main_menu():
  file = capture_check()
  cMinutiaeBuffer3, quality3 = capture(3, file)
  cMin = open("prints/{}.min".format(file), "rb")
  cMatched = match(cMin.read(), cMinutiaeBuffer3)
  if (cMatched.value == True):
    print("MATCH");
  else:
    print("NO MATCH");
  sgfplib.CloseDevice()

  sgfplib.Terminate()


main_menu()

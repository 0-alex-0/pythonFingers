#! /usr/bin/env python3

from pysgfplib import *
from ctypes import *
from os import listdir, mkdir, environ
from tkinter import *
from tkinter import ttk
from time import sleep
from datetime import datetime
import smtplib

constant_hamster_pro20_width = 300
constant_hamster_pro20_height = 400
constant_sg400_template_size = 400
finger_width = constant_hamster_pro20_width
finger_height = constant_hamster_pro20_height


sgfplib = PYSGFPLib()
user = environ['USER']
emailPass = "auto eby contact@"

def start():
  result = sgfplib.Create()
  if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
    output.insert("end","Create error\n");
    #exit()
  else:
    output.insert("end","Create OK\n")
  result = sgfplib.Init(SGFDxDeviceName.SG_DEV_AUTO)
  if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
    output.insert("end","Init error\n");
    #exit()
  result = sgfplib.OpenDevice(0)
  if (result != SGFDxErrorCode.SGFDX_ERROR_NONE):
    output.insert("end","  ERROR - Unable to initialize SecuGen library. Exiting\n");
    #exit()
  else:
    output.insert("end","Init OK\n")
    btnStartScanner['state'] = DISABLED
  return result

def end():
  sgfplib.CloseDevice()
  sgfplib.Terminate()

def send_email():
  eml="auto.eby.contact@gmail.com"
  head="test"
  body="this is a test"
  server = smtplib.SMTP("smtp.gmail.com",587)
  server.starttls()
  server.login(eml, emailPass)
  msg = "From: {}\nTo: {}\nSubject: {}\n{}".format(eml, eml, head, body)
  server.sendmail("Auto Eby Contact","auto.eby.contact@gmail.com",msg)

#def select_day
#  sMonthNum = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5,"Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec"12]

def match(cMinutiaeBuffer1, cMinutiaeBuffer2):
  cMatched = c_bool(False)
  result = sgfplib.MatchTemplate(cMinutiaeBuffer1, cMinutiaeBuffer2, SGFDxSecurityLevel.SL_NORMAL, byref(cMatched));

  cScore = c_int(0)
  result = sgfplib.GetMatchingScore(cMinutiaeBuffer1, cMinutiaeBuffer2, byref(cScore));
  print("  Score : [" + str(cScore.value) + "]")
  return cMatched

def mkEmail(name, emailInput):
  if(bool(emailInput) == True):
    email = open("/home/{}/pythonFingers/emails/{}".format(user, name), "w")
    email.write(emailInput)

def save_min(name, cMinutiaeBuffer):
  taken = 0
  if(bool(name) == True):
    fprints = listdir("prints")
    for fprint in fprints:
      if(fprint == "{}".format(name)):
        taken = 1
        print("name in use")
        output.insert("end","name in use: {}   ".format(fprint));
      cMin = open("/home/{}/pythonFingers/prints/{}".format(user, fprint), "rb")
      cMatched = match(cMin.read(), cMinutiaeBuffer)
      if (cMatched.value == True):
        taken = 1
        print("finger in use")
        output.insert("end","finger in use: {}   ".format(fprint));
    if(taken == 0):
      imageFile = open("/home/{}/pythonFingers/prints/{}".format(user, name), "wb")
      imageFile.write(cMinutiaeBuffer)
      output.insert("end","[FINGER ADDED]");

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

def track_date(name):
  today = datetime.today().strftime("%Y-%m-%d")
  dateFile = open("/home/{}/pythonFingers/dates/{}".format(user, today), "a")
  dateFile.write("{}, ".format(name))

def check_in():
  file="check_in"
  fprints = listdir("prints")
  cMinutiaeBuffer3, quality3 = capture(0, file)
  for fprint in fprints:
    cMin = open("/home/{}/pythonFingers/prints/{}".format(user, fprint), "rb")
    cMatched = match(cMin.read(), cMinutiaeBuffer3)
    if (cMatched.value == True):
      output.insert("end"," {} [MATCH] ".format(fprint));
      track_date(fprint)
    else:
      pass

def check_today():
  today = datetime.today().strftime("%Y-%m-%d")
  dateFile = open("/home/{}/pythonFingers/dates/{}".format(user, today), "r")
  output.insert("end", dateFile.read())

def check_day():
  year = year_input.get()
  month = svMonth.get()
  sMonthNum = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
  monthDigit = sMonthNum[month]
  day = svDay.get()
  daycheck = "{}-{}-{}".format(year, monthDigit, day)
  try:
    dateFile = open("/home/{}/pythonFingers/dates/{}".format(user, daycheck), "r")
    output.delete('1.0', END)
    output.insert("end", "{}\n".format(daycheck))
    output.insert("end", dateFile.read())
    btn_emailSpam['state'] = NORMAL
  except:
    output.delete('1.0', END)
    output.insert("end", "Error: Cannot Find Day Record\n")
    output.insert("end", daycheck)
    btn_emailSpam['state'] = DISABLED

def emailSpam():
  check_day()
  year = year_input.get()
  month = svMonth.get()
  sMonthNum = {"Jan":"01", "Feb":"02", "Mar":"03", "Apr":"04", "May":"05", "Jun":"06", "Jul":"07", "Aug":"08", "Sep":"09", "Oct":"10", "Nov":"11", "Dec":"12"}
  monthDigit = sMonthNum[month]
  day = svDay.get()
  daycheck = "{}-{}-{}".format(year, monthDigit, day)
  dateFile = open("/home/{}/pythonFingers/dates/{}".format(user, daycheck), "r")
  emails = dateFile.read()
  splitEmails = emails.split(", ")
  splitEmails.pop(-1)
  #print(splitEmails)
  try:
    for fingerEmails in splitEmails:
      contactEmail = open("/home/{}/pythonFingers/emails/{}".format(user, fingerEmails), "r")
      contEml = contactEmail.read()
      #print("{} : {}".format(fingerEmails, contEml))
      eml="auto.eby.contact@gmail.com"
      eSubject=subject.get()
      if bool(eSubject) != True:
        output.delete('1.0', END)
        output.insert('end', 'Error: missing Subject')
        return
      eBody=body.get("1.0",END)
      #print(len(eBody))
      if len(eBody) <= 1:
        output.delete('1.0', END)
        output.insert('end', 'Error: missing Body')
        return
      eBody = "Dear {},\n    {}        Best Wishes, Eby Center".format(fingerEmails, eBody)
      server = smtplib.SMTP("smtp.gmail.com",587)
      server.starttls()
      server.login(eml, emailPass)
      msg = "From: {}\nTo: {}\nSubject: {}\n{}".format(eml, contEml, eSubject, eBody)
      server.sendmail("Auto Eby Contact","auto.eby.contact@gmail.com",msg)
    btn_emailSpam['state'] = DISABLED
  except:
    output.delete('1.0', END)
    output.insert('end', 'Error: cannot spam')
    btn_emailSpam['state'] = DISABLED

def clear_output():
  output.delete('1.0', END)
  output.insert("end", "Error: Cannot Find Day Record\n")

#result = start()
#result = sgfplib.OpenDevice(0)
sDay = ["01","02","03","04","05","06","07","08","09","10","11","12","13","14","15","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31"]
sMonth = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

tk = Tk()
tk.title("pythonFingers")

frame = Frame(tk, relief=RIDGE, borderwidth=2, bg="grey")
frameAdd = Frame(frame, relief=RIDGE, borderwidth=2, bg="grey")
frameCheck = Frame(frame, relief=RIDGE, borderwidth=2, bg="grey")
frameOutput = Frame(tk, relief=RIDGE, borderwidth=2, bg="black")
btnExit = Button(frameOutput,text="Exit",command=tk.destroy, bg="white", fg="black")
btnAdd = Button(frameAdd,text="add fingerprint",command=capture_check)
btnCheck_in = Button(frameCheck,text="check in",command=check_in)
btnStartScanner = Button(frameCheck,text="start scanner",command=start)
btnCheck_today = Button(frameCheck,text="check today",command=check_today)
btnOutput_clear = Button(frameOutput,text="clear output",command=clear_output)
btnSend_email = Button(frameOutput,text="Send Email",command=send_email)
output = Text(frameOutput, width=80, height=4, font=('Arial', 14))

label_email_input = Label(frameAdd, width=38, font=('Arial', 14), bg="black", fg="white", text="EMAIL to ADD")
label_finger_input = Label(frameAdd, width=38, font=('Arial', 14), bg="black", fg="white", text="NAME to ADD")
label_finger_check = Label(frameAdd, width=38, font=('Arial', 14), bg="black", fg="white", text="Check Fingerprint")
finger_input = Entry(frameAdd, width=38, font=('Arial', 14))
email_input = Entry(frameAdd, width=38, font=('Arial', 14))

dayEmailFrame = Frame(frameOutput)

dayFrame = Frame(dayEmailFrame, relief=RIDGE, borderwidth=2, bg="grey")
label_day = Label(dayFrame,  width=15, font=('Arial', 14), bg="white", fg="black", text="Pick day to spam")
label_month = Label(dayFrame,  width=5, font=('Arial', 14), bg="white", fg="black", text="  Month: ")
label_year = Label(dayFrame,  width=5, font=('Arial', 14), bg="white", fg="black", text=" Year: ")
svDay = StringVar(tk)
svDay.set("1")
svDay.set(sDay[0])
DayMenu = OptionMenu(dayFrame, svDay, *sDay)
svMonth = StringVar(tk)
svMonth.set("Jan")
svMonth.set(sMonth[0])
MonthMenu = OptionMenu(dayFrame, svMonth, *sMonth)
year_input = Entry(dayFrame, width=10, font=('Arial', 14))
btn_viewDay = Button(dayFrame,text="Check the Day",command=check_day)
btn_emailSpam = Button(dayFrame,text="Spam them!",command=emailSpam, state=DISABLED)

emailFrame = Frame(dayEmailFrame, width=100, bg="grey")
label_subject = Label(emailFrame,  width=90, font=('Arial', 14), bg="black", fg="white", text="Email Subject")
subject = Entry(emailFrame, width=100, font=('Arial', 14))
label_body = Label(emailFrame,  width=90, font=('Arial', 14), bg="black", fg="white", text="Email Body")
body = Text(emailFrame, width=100, height=4, font=('Arial', 14))

frame.pack(side=TOP, fill=BOTH, expand=1)
frameAdd.pack(side=LEFT, anchor=NW, fill=BOTH, expand=.5)
frameCheck.pack(side=RIGHT, anchor=NE, fill=BOTH, expand=.5)
frameOutput.pack(side=BOTTOM, fill=BOTH, expand=1)

label_finger_input.pack(pady=5)
finger_input.pack(pady=5)
label_email_input.pack(pady=5)
email_input.pack(pady=5)
btnStartScanner.pack(pady=5)
btnCheck_in.pack(pady=5)
btnCheck_today.pack(pady=15)
btnAdd.pack(pady=5)
output.pack(pady=10, side=TOP)
btnOutput_clear.pack(pady=5)

dayEmailFrame.pack(side=TOP)
dayFrame.pack(side=TOP, anchor=N, expand=1)
btnSend_email.pack(pady=15)
btnExit.pack(side=BOTTOM)
label_day.pack(side=LEFT, pady=15)
DayMenu.pack(side=LEFT, pady=15)
label_month.pack(side=LEFT, pady=15)
MonthMenu.pack(side=LEFT, pady=15)
label_year.pack(side=LEFT, pady=15)
year_input.pack(side=LEFT, pady=15)
btn_viewDay.pack(side=LEFT, pady=15)
btn_emailSpam.pack(side=LEFT, pady=15)
emailFrame.pack(side=BOTTOM, pady=15)
label_subject.pack()
subject.pack()
label_body.pack()
body.pack()


tk.mainloop()

end()

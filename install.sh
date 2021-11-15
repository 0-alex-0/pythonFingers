#!/bin/bash
# chmod +x install.sh
sudo
sudo cp libpysgfplib.so /usr/local/lib/libpysgfplib.so
mkdir /home/$USER/pythonFingers
mkdir /home/$USER/pythonFingers/dates
mkdir /home/$USER/pythonFingers/emails
mkdir /home/$USER/pythonFingers/prints
cp 0fingerscanner /home/$USER/pythonFingers/0fingerscanner
cp fingerprint.jpeg /home/$USER/pythonFingers/fingerprint.jpeg
sudo cp pythonFinger.desktop /usr/share/applications/pythonFinger.desktop
cp pysgfplib.py /home/$USER/pythonFingers/pysgfplib.py
cp sgfdxdevicename.py /home/$USER/pythonFingers/sgfdxdevicename.py
cp sgfdxerrorcode.py /home/$USER/pythonFingers/sgfdxerrorcode.py
cp sgfdxsecuritylevel.py /home/$USER/pythonFingers/sgfdxsecuritylevel.py

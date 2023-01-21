# Campsite Reserver
 
This is a python script which attempts to automate the process of reserving sites on camping.gov.hk It is especially made for sought-after campsites recently launched by Hong Kong Govenment

# Dependencies

 + OS X or *nix variant

 + Python

 + Selenium (current release)

 + geckodriver (current release)

 + Firefox (current release)
    
 + If you're unfamiliar with the above tools, and using OS X: You already have a version of Python preinstalled.

 + You can install Selenium by opening a Terminal window and entering the following command: sudo easy_install selenium or pip install selenium

 + On OS X you can install the geckodriver using homebrew, like so: brew install geckodriver

# Running the script

Copy checker_example.ini to checker.ini and edit all the fields as required. You must have a HKID # for each reservation that you are trying to make. See below the campsite ID

Once you've edited the configuration file, open up a Terminal window in the directory containing this script and enter the command python ./main.py to run the script.

Recommended use pattern is to begin the script shortly before reservations are due to open, with a low number of retries. Recreation.gov network usage is monitored and you risk account termination if you just leave this running all day.

Note: If you find, after playing with this script, that you have lots of Firefox windows open, you can kill them all on a Unix based platform with a command like $ killall firefox-bin.

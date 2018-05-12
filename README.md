USTCourseExtract
===
This is a public repo for course detail extraction from HKUST through [HKUST Class Schedule & Quota](https://w5.ab.ust.hk/wcq/cgi-bin/1740/).

USTCourseExtract is developed using python3.

##    How to use
1. Install python3
2. Install lxml
3. Install requests

For macOS, open Terminal 
```
brew install python3
pip3 install lxml
pip3 install requests
```

If database is not updated, use `update` command to update desire semester.
**Recommend updating from oldest to latest**

Type `help` to view more command

##    Library used
* html
* Enum
* Path
* requests
* json
* re

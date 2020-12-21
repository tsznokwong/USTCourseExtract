# USTCourseExtract

This is a public repo for course detail extraction from HKUST through [HKUST Class Schedule & Quota](https://w5.ab.ust.hk/wcq/cgi-bin/1740/).

USTCourseExtract is developed using python3.

## How to use

1. Install python3
2. Install libraries in requirements.txt

For macOS, open Terminal

```
brew install python3
pip3 install -r requirements.txt
```

If database is not updated, use `update` command to update desire semester.
**Recommend updating from oldest to latest**

Type `help` to view more command

## Library used

- html
- Enum
- Path
- requests
- json
- re

from lxml import html
from enum import Enum
from pathlib import Path
import requests
import json
import re

# Constant
WebData = 'https://w5.ab.ust.hk/wcq/cgi-bin/'
headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Safari/604.1.38'}
CSV = 'courses.csv'
save = 'courseTree'
database = 'database'
Semesters = ["FALL", "WINTER", "SPRING", "SUMMER"]
# Constant END

# Global var
command = ""
Subjects = []
Database = {"semesters": []}
# Global var END

class printType(Enum):
    Simple = 1
    Complete = 2
    List = 3
# class printType END

# Print type adjust
def printTypeAdjust(userPrintType, default):
    if userPrintType == None:
        return default
    return userPrintType
# Print type adjust END

# Print course
def printCourse(course: {}, type = printType.Simple):
    space = " - "
    if len(course["Code"]) == 4:
        space = "  - "
    print (course["Subject"] + course["Code"] + space + course["Title"] + " (" + course["Credit"] + ")")
    Attributes = []
    if type != printType.List:
        Attributes.extend(["Attribute", "Prerequisite Str", "Corequisite Str", "Exclusion Str"])
    if type == printType.Complete:
        Attributes.extend(["Colist With Str", "Previous Code", "Description", "Offer In"])
    for attr in Attributes:
        if course[attr] != "-":
            print(attr.strip(" Str") + ": \t", end = "")
            if attr != "Offer In":
                print(course[attr])
            else:
                print(course["Offer In"][0], end = "")
                for sem in course["Offer In"][1:]:
                    print(", " + sem, end = "")
                print("\n")
# Print course END

def printCoursesInSubject(subject: {}, type = printType.List):
    for course in subject["courses"]:
        printCourse(course, type)

# Binary search
def binarySearch(array: [], target, attribute = ""):
    if len(array) == 1:
        return 0
    if len(array) == 0:
        return -1
    mid = int(len(array) / 2)
    if array[mid][attribute] < target:
        return mid + binarySearch(array[mid:], target, attribute)
    elif array[mid][attribute] > target:
        return binarySearch(array[:mid], target, attribute)
    else:
        return mid
# Binary search END

# Linear search
def linearSearch(array: [], target):
    for item in array:
        if item == target:
            return array.index(item)
    return -1
# Linear search END

# Standardize input
def standardize(text):
    text = text.upper()
    text = text.strip()
    return text
# Standardize input END

# Input semester
def inputSemester():
    while True:
        semester = input("Semester [Fall | Winter | Spring | Summer]: ")
        semester = standardize(semester)
        if linearSearch(Semesters, semester) != -1:
            return semester
        print("Invalid Semester.")
# Input semester END

# Find subject
def findSubject(subjects: [], subject):
    subjectIndex = binarySearch(subjects, subject, "name")
    if subjectIndex == -1:
        subjects.append({"name": subject, "courses": []})
    elif subjects[subjectIndex]["name"] != subject:
        if subjects[subjectIndex]["name"] < subject:
            subjectIndex += 1
        subjects.insert(subjectIndex, {"name": subject, "courses": []})
    return subjectIndex
# Find subject END

def identifyPrintType(sections: []):
    if linearSearch(sections, "-L") != -1:
        return printType.List
    elif linearSearch(sections, "-S") != -1:
        return printType.Simple
    elif linearSearch(sections, "-C") != -1:
        return printType.Complete

def removeOptions(sections: []):
    for section in sections:
        if section[0] == "-":
            sections.remove(section)
    return sections

# Retrieve database
if Path(save).exists():
    with open(save, 'r') as file:
        Subjects = json.load(file)
if Path(database).exists():
    with open(database, 'r') as file:
        Database = json.load(file)
# Retrieve database END

while command != "EXIT":
    try:
        command = standardize(input("Enter command: "))
        cmdSections = command.split(" ")
        if cmdSections[0] == "UPDATE":
#            UPDATE COMMAND
            Class = requests.get(WebData)
            ClassTree = html.fromstring(Class.content)
            semesterAvailable = ClassTree.xpath('//li[@class="term"]/div[@class="termselect"]/a/text()')
    
            sem = inputSemester()
            year = '16'
            for title in semesterAvailable:
                if title.find(sem.title()) != -1:
                    year = title[2:4]
            extractWebData = WebData + year + str(Semesters.index(sem) + 1) + '0/'
            thisSem = year + sem
            try:
                Class = requests.get(extractWebData)
            except requests.ConnectionError as e:
                print("Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
                print(str(e))
                continue
            except requests.Timeout as e:
                print("Timeout Error.")
                continue
            except requests.HTTPError as e:
                print("HTTP Error. Technical Detials given below.\n")
                print(str(e))
                continue
            if Class.status_code == 200:
                print("Connection Success")
                ClassTree = html.fromstring(Class.content)
                semester = ClassTree.xpath('//li[@class="term"]/a[@href="#"]/text()')
                print(semester[0])
                extractWebData = WebData + semester[0][2:4] + str(Semesters.index(semester[0][8:-1].upper()) + 1) + '0/'
                Sub = ClassTree.xpath('//div[@class="depts"]/a/text()')
                total = len(Sub)
                cnt = 0
                for subject in Sub:
                    Class = requests.get(extractWebData + 'subject/' + subject)
                    if Class.status_code == 200:
                        print("Retrieving %s --- %.1f%%" % (subject, cnt / total * 100), end = "\r")
                        cnt += 1
                        subjectIndex = findSubject(Subjects, subject)
                        ClassTree = html.fromstring(Class.content)
                        courseName = ClassTree.xpath('//h2/text()')
                        for i in range(len(courseName)):
                            name = courseName[i]
                            newCourse = {"Subject": name[0:4], "Code": name[5: name.find(" ", 5)], "Title": name[name.find(" ", 5) + 3: name.find(" ", -10)], "Credit": name[name.find(" ", -8) - 1: name.find(" ", -8)], "Attribute": "-",    "Exclusion Str": "-", "Prerequisite Str": "-", "Corequisite Str": "-", "Description": "-", "Colist With Str": "-", "Vector": "-", "Previous Code": "-", "Offer In": [semester[0][:-1]]}

                            courseAttributes = ClassTree.xpath('//div[@id="classes"]/div[@class="course"][' + str(i + 1) + ']/div[@class="courseinfo"]/div[@class="courseattr popup"]/div/table/tr/th/text()')
                            courseData = ClassTree.xpath('//div[@id="classes"]/div[@class="course"][' + str(i + 1) + ']/div[@class="courseinfo"]/div[@class="courseattr popup"]/div/table/tr/td/text()')
                            j = 0
                            for attr in courseAttributes:
                                if j >= len(courseData):
                                    break
                                if attr == "ATTRIBUTES":
                                    s = ""
                                    while courseData[j][0: 11] == "Common Core" or courseData[j][0: 10] == "CommonCore":
                                        if courseData[j].find("4Y") != -1:
                                            s += courseData[j][courseData[j].find("("): courseData[j].find(")") + 1]
                                        j += 1
                                    medium = ["[CA]", "[PU]", "[C]", "GEE"]
                                    for m in medium:
                                        if j >= len(courseData):
                                            break
                                        if courseData[j].find(m) != -1:
                                            s += m
                                            j += 1
                                    newCourse["Attribute"] = s
                                else:
                                    if attr == "EXCLUSION":
                                        newCourse["Exclusion Str"] = courseData[j]
                                    elif attr == "PRE-REQUISITE":
                                        newCourse["Prerequisite Str"] = courseData[j]
                                    elif attr == "CO-REQUISITE":
                                        newCourse["Corequisite Str"] = courseData[j]
                                    elif attr == "DESCRIPTION":
                                        newCourse["Description"] = courseData[j]
                                    elif attr == "CO-LIST WITH":
                                        newCourse["Colist With Str"] = courseData[j]
                                    elif attr == "VECTOR":
                                        newCourse["Vector"] = courseData[j]
                                    elif attr == "PREVIOUS CODE":
                                        newCourse["Previous Code"] = courseData[j]
                                    else:
                                        newCourse["Description"] += " " + courseData[j]
                                    j += 1
                            courseIndex = binarySearch(Subjects[subjectIndex]["courses"], newCourse["Code"], "Code")
                            if courseIndex == -1:
                                Subjects[subjectIndex]["courses"].append(newCourse)
                            elif Subjects[subjectIndex]["courses"][courseIndex]["Code"] != newCourse["Code"]:
                                if Subjects[subjectIndex]["courses"][courseIndex]["Code"] < newCourse["Code"]:
                                    courseIndex += 1
                                Subjects[subjectIndex]["courses"].insert(courseIndex, newCourse)
                            else:
                                offerIn = Subjects[subjectIndex]["courses"][courseIndex]["Offer In"]
                                if linearSearch(offerIn, newCourse["Offer In"][0]) == -1:
                                    newCourse["Offer In"].extend(offerIn)
                                else:
                                    newCourse["Offer In"] = offerIn
                                Subjects[subjectIndex]["courses"][courseIndex] = newCourse
                print("Retrieving %s --- 100.0%%" % subject)
                with open(save, 'w') as file:
                    json.dump(Subjects, file)
                if linearSearch(Database["semesters"], thisSem):
                    print("NEW SEMESTER ADDED")
                    with open(database, 'w') as file:
                        json.dump(Database, file)
                print("Completed")
    
        elif cmdSections[0] == "PRINT":
#            PRINT COMMAND
            userPrintType = identifyPrintType(cmdSections)
            cmdSections = removeOptions(cmdSections)
            if len(cmdSections) == 1:
                cmdSections.append("ALL")
            for section in cmdSections[1:]:
                cnt = 0
                if section == "ALL":
                    for subject in Subjects:
                        printCoursesInSubject(subject, printTypeAdjust(userPrintType, printType.List))
                        cnt += len(subject["courses"])
                elif section == "SUBJECT":
                    print("Subjects in Database(%d) :" % len(Subjects))
                    for subject in Subjects:
                        if (Subjects.index(subject) + 1) % 15 > 0:
                            print(subject["name"], end = " ")
                        else:
                            print(subject["name"])
                    print()
                else:
                    subjectResult = binarySearch(Subjects, section[:4], "name")
                    if subjectResult == -1:
                        print("No subjects in database. Please update database.")
                    elif Subjects[subjectResult]["name"] == section[:4]:
                        subject = Subjects[subjectResult]
                        if len(section) == 4:
                            printCoursesInSubject(subject, printTypeAdjust(userPrintType, printType.List))
                            cnt += len(subject["courses"])
                        else:
                            courseResult = binarySearch(subject["courses"], section[4:], "Code")

                            if courseResult == -1:
                                print("No courses in %s." % subject["name"])
                            elif subject["courses"][courseResult]["Code"] == section[4:]:
                                printCourse(subject["courses"][courseResult], printTypeAdjust(userPrintType, printType.Complete))
                                cnt += 1
                            else:
                                print("%s is not found." % section)
                    else:
                        print("%s is not found." % section)
                if cnt > 0:
                    print("%d Courses(s) have been printed." % cnt)

        
        elif cmdSections[0] == "PRINTSEM":
#           Print SEMESTER
            userPrintType = identifyPrintType(cmdSections)
            cmdSections = removeOptions(cmdSections)
            Sems = cmdSections[1:]
            if len(Sems) == 0:
                print("Enter semester: [", end = "")
                for sem in Database["semesters"][:-1]:
                    print(sem, end = " |")
                Sems = input(Database["semesters"][-1] + "]: ")
                Sems = standardize(Sems).split(" ")
            for sem in Sems:
                if linearSearch(Database["semesters"], sem) == -1:
                    print("%s is not found." % sem)
                    continue
                theSem = "20" + sem[:2] + "-" + str(int(sem[:2]) + 1) + " " + sem[2:].title()
                print("Semester: %s" % theSem)
                for subject in Subjects:
                    for course in subject["courses"]:
                        if linearSearch(course["Offer In"], theSem) != -1:
                            printCourse(course, printTypeAdjust(userPrintType, printType.List))
                        

        elif cmdSections[0] == "EXPORTCSV":
#            Export CSV
#            print("EXPORTCSV is banned now.")
#            continue
            if len(Subjects) == 0 or len(Subjects[0]["courses"]) == 0:
                print("Incomplete database. Please update database")
                continue
            with open(CSV, 'w') as file:
                for key in Subjects[0]["courses"][0]:
                    file.write(key.upper() + ",")
                file.write("\n")
                separator = "\",\""
                for subject in Subjects:
                    for course in subject["courses"]:
                        for key, value in course.items():
                            if key == "Subject":
                                file.write("\"" + value)
                            elif key == "Description":
                                desc = value.replace("\"","\"\"")
                                desc = desc.replace("\n", "")
                                file.write(separator + desc)
                            else:
                                file.write(separator + str(value))
                        file.write("\"\n")
            
        elif cmdSections[0] == "IMPORTCSV":
#            FAULTY
            print("IMPORTCSV is banned now.")
            continue
            file = open('coursesNew.csv', 'r')
            importCSVSubjects = []
            for line in file:
                data = line[1: -2].split("\",\"")
                if data[0] == "UBJECT,CODE,TITLE,CREDIT,ATTRIBUTE,EXCLUSIONSTR,PREREQUISITESTR,COREQUISITESTR,DESCRIPTION,COLISTWITHSTR,VECTOR,PREVIOUSCODE,OFFER IN":
                    continue
                subjectIndex = findSubject(importCSVSubjects, data[0])

                newCourse = {"Subject": "", "Code": "", "Title": "", "Credit": "", "Attribute": "-",    "Exclusion Str": "-", "Prerequisite Str": "-", "Corequisite Str": "-", "Description": "-", "Colist With Str": "-", "Vector": "-", "Previous Code": "-", "Offer In": []}
                for attr, datum in zip(newCourse.keys(), data):
                    if attr == "Offer In":
                        newCourse["Offer In"] = datum[2: -2].split("\', \'")
                    else:
                        if attr == "Description":
                            datum = datum.replace("\"\"", "\"")
                        newCourse[attr] = datum
                courseIndex = binarySearch(importCSVSubjects[subjectIndex]["courses"], newCourse["Code"], "Code")
                if courseIndex == -1:
                    importCSVSubjects[subjectIndex]["courses"].append(newCourse)
                elif importCSVSubjects[subjectIndex]["courses"][courseIndex]["Code"] != newCourse["Code"]:
                    if importCSVSubjects[subjectIndex]["courses"][courseIndex]["Code"] < newCourse["Code"]:
                        courseIndex += 1
                    importCSVSubjects[subjectIndex]["courses"].insert(courseIndex, newCourse)
                else:
                    importCSVSubjects[subjectIndex]["courses"][courseIndex] = newCourse
            
            with open(save, 'w') as file:
                json.dump(importCSVSubjects, file)

        elif cmdSections[0] == "HELP":
            print("print (SUBJECTCODE) (COURSECODE) (all) (subject) (-l) (-s) (-c)...")
            print("printsem <Semester> (-l) (-s) (-c) ...")
            print("update <Semester>")
            print("exportcsv ")
            print("importcsv")

        elif command == "TEST":
            print("TESTING SECTION")

        
    except KeyboardInterrupt:
        print("Force quit program")
        break


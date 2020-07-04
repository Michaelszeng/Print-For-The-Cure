import time
import xlwt
from xlwt import Workbook
from ShippingInfo_6_27_20 import *   #change depending on shipping day

workbookBox = Workbook()
workbookBag = Workbook()
sheetBox = workbookBox.add_sheet('6.27.20')
sheetBag = workbookBag.add_sheet('6.27.20')
style = xlwt.easyxf('font: bold 1')

# row, column
sheetBox.write(0, 0, 'Full Name', style)
sheetBox.write(0, 1, 'Address1', style)
sheetBox.write(0, 2, 'City', style)
sheetBox.write(0, 3, 'State', style)
sheetBox.write(0, 4, 'Zipcode', style)
sheetBox.write(0, 5, 'Type PPE', style)
sheetBox.write(0, 6, 'Amount', style)
sheetBox.write(0, 7, 'Email', style)

sheetBag.write(0, 0, 'Full Name', style)
sheetBag.write(0, 1, 'Address1', style)
sheetBag.write(0, 2, 'City', style)
sheetBag.write(0, 3, 'State', style)
sheetBag.write(0, 4, 'Zipcode', style)
sheetBag.write(0, 5, 'Type PPE', style)
sheetBag.write(0, 6, 'Amount', style)
sheetBag.write(0, 7, 'Email', style)
style = xlwt.easyxf('font: bold off')

#finds index of first address so next loop doesn't go out of bounds
addressIndex = 0
for i in range(len(data1)-22):
    addressSearcher = data1[i:i+21]
    if addressSearcher == "Requester's Address: ":
        addressIndex = i
        break


data = data1.replace("\n", " ").replace("\r", " ")

#loops backwards up to the first address (found in prev loop) so it doesn't go out of bounds
# for i in reversed(range(len(data) - addressIndex)):
#     addressSearcher = data[i:i+21]
#     if addressSearcher == "Requester's Address: ":
#         iCounterStartValue = i
#         iCounter = i
#         while True:
#             #name ends when the next 19 chars are "Type of PPE Requested: "
#             if "Type of PPE Requested: " in data[21+iCounter:21+iCounter+23] or iCounter-iCounterStartValue > 80:   #max address length = 80
#                 break
#             if data[i:i+2] == "\\n":
#                 print("hello")
#                 dataHalfOne = data[0:i]
#                 dataHalfTwo = data[i+2:]
#                 data = dataHalfOne + "  " + dataHalfTwo
#             iCounter += 1

# print(data)

currentRow = 1
for i in range(len(data)-22):
    emailSearcher = data[i:i+19]
    nameSearcher = data[i:i+18]
    addressSearcher = data[i:i+21]
    typePPESearcher = data[i:i+23]
    numSearcher = data[i:i+25]

    email = ""
    if emailSearcher == "Requester's Email: ":
        iCounterStartValue = i
        iCounter = i
        while True:
            #name ends when the next 19 chars are "Requester's Email: "
            if "Requester's Phone Number:" in data[19+iCounter:19+iCounter+25] or iCounter-iCounterStartValue > 80:   #max email length = 80
                break
            email += data[19+iCounter:20+iCounter]
            iCounter += 1
        email2 = email    #have to make a new var bc for some reason the value of name always gets reudced to an empty string somehow


    name = ""
    if nameSearcher == "Requester's Name: ":
        iCounterStartValue = i
        iCounter = i
        while True:
            #name ends when the next 19 chars are "Requester's Email: "
            if "Requester's Email: " in data[18+iCounter:19+iCounter+19] or iCounter-iCounterStartValue > 30:   #max name length = 30
                break
            name += data[18+iCounter:19+iCounter]
            iCounter += 1
        name2 = name    #have to make a new var bc for some reason the value of name always gets reudced to an empty string somehow


    fullAddress = ""
    if addressSearcher == "Requester's Address: ":
        iCounterStartValue = i
        iCounter = i
        while True:
            #name ends when the next 19 chars are "Type of PPE Requested: "
            if "Type of PPE Requested: " in data[21+iCounter:21+iCounter+23] or iCounter-iCounterStartValue > 80:   #max address length = 80
                break
            fullAddress += data[21+iCounter:22+iCounter]
            iCounter += 1


        addressList = fullAddress.split(" ")
        # print(addressList)
        safetyCounter = 0
        while True:
            found = False
            for i in range(len(addressList)-1):
                #removing periods from address item
                addressItemNoPeriod = ""
                for char in addressList[i]:
                    if char != "." and char!= ",":
                        addressItemNoPeriod += char
                addressList[i] = addressItemNoPeriod

                #deleting address items that are just blank spaces
                # print(addressList[i])
                # if addressList[i] == "":
                #     addressList.pop(i)
                #     found = True
                #     break
                try:
                    addressList.remove('')
                    found = True
                    break
                except:
                    time.sleep(0.0001)
                try:
                    addressList.remove('\r')
                    found = True
                    break
                except:
                    time.sleep(0.0001)
                try:
                    addressList.remove('\n')
                    found = True
                    break
                except:
                    time.sleep(0.0001)
                try:
                    addressList.remove('us')
                    found = True
                    break
                except:
                    time.sleep(0.0001)


            if found == False or safetyCounter > 5:
                break
            safetyCounter += 1

        # for i in range(len(addressList)-1):
        #     addressItemNoPeriod = ""
        #     for char in addressList[i]:
        #         if char != "." and char!= ",":
        #             addressItemNoPeriod += char
        #     addressList[i] = addressItemNoPeriod
        #
        #     try:
        #         addressList.remove('')
        #     except:
        #         print()
        #     try:
        #         addressList.remove('\r')
        #     except:
        #         print()
        #     try:
        #         addressList.remove('\n')
        #     except:
        #         print()
        addressList.append('us')
        print(addressList)

        zip = addressList[len(addressList)-2]
        state = addressList[len(addressList)-3]
        notCityThings  = ["str", "st", "street", "ave", "avenue", "blvd", "boulevard", "rd", "road", "ln", "lane", "dr", "drive", "ct", "court", "way", "pl", "place", "pkwy", "parkway", "cir", "circle", "ctr", "cntr", "center", "plaza", "highway", "terrace", "trrc", "trail", "trl", "crossing", "N", "S", "W", "E", "NW", "NE", "SW", "SE", "floor"]
        if len(addressList[len(addressList)-5]) <= 2 and addressList[len(addressList)-5].lower() != "of" or "#" in addressList[len(addressList)-5]:   #if it is likely an apt/suite number
            city = addressList[len(addressList)-4]
            separator = " "
            address = separator.join(addressList[0:len(addressList)-4])
        else:
            try:
                int(addressList[len(addressList)-5])
                city = addressList[len(addressList)-4]
                separator = " "
                address = separator.join(addressList[0:len(addressList)-4])
            except:
                partOfCityName = True
                for thing in notCityThings:     #a road, street, etc.
                    if addressList[len(addressList)-5].lower() == thing:
                        city = addressList[len(addressList)-4]
                        separator = " "
                        address = separator.join(addressList[0:len(addressList)-4])
                        partOfCityName = False

                if partOfCityName == True:
                    city = addressList[len(addressList)-5] + " " + addressList[len(addressList)-4]
                    separator = " "
                    address = separator.join(addressList[0:len(addressList)-5])

    typePPE=""
    if typePPESearcher == "Type of PPE Requested: ":
        iCounterStartValue = i
        iCounter = i
        while True:
            if "Amount of PPE Requested: " in data[23+iCounter:23+iCounter+25] or iCounter-iCounterStartValue > 120:   #max typePPE length = 120
                break
            typePPE += data[iCounter+23:iCounter+24]
            iCounter += 1
        type2 = typePPE     #have to make a new var bc for some reason the value of typePPE always gets reudced to an empty string somehow
        # print(typePPE)


    num=""
    if numSearcher == "Amount of PPE Requested: ":
        iCounterStartValue = i
        iCounter = i
        while True:
            if " date for the requested PPE: " in data[25+18+iCounter:25+18+iCounter+29] or iCounter-iCounterStartValue > 4:   #max num length = 4
                break
            num += data[iCounter+25:iCounter+26]
            iCounter += 1


        numbers = '1234567890'
        numPunct = num
        num = ""
        for char in numPunct:
           if char in numbers:
               num = num + char

        num = int(num)
        # print("typePPE: " + type2)
        if "3D Printed Face Shields" in type2:
            packageType = "Box"
        elif "Personal Touchless Door Opener" in type2:
            if num > 8:
                packageType = "Box"
            else:
                packageType = "Bag"
        elif "Face Mask Comfort Strap" in type2:
            if num > 125:
                packageType = "Box"
            elif num < 10:
                packageType = "env"
            else:
                packageType = "Bag"
        elif "Touch-less Door Handle" in type2:
            if num > 1:
                packageType = "Box"
            else:
                packageType = "Bag"
        # print(packageType)

        if packageType == "Box":
            sheetBox.write(currentRow, 7, email2, style)
            sheetBox.write(currentRow, 6, num, style)
            sheetBox.write(currentRow, 5, type2, style)
            sheetBox.write(currentRow, 4, zip, style)
            sheetBox.write(currentRow, 3, state, style)
            sheetBox.write(currentRow, 2, city.replace(',', ''), style)
            sheetBox.write(currentRow, 1, address.replace(',', ''), style)
            sheetBox.write(currentRow, 0, name2, style)
        elif packageType == "Bag":
            sheetBag.write(currentRow, 7, email2, style)
            sheetBag.write(currentRow, 6, num, style)
            sheetBag.write(currentRow, 5, type2, style)
            sheetBag.write(currentRow, 4, zip, style)
            sheetBag.write(currentRow, 3, state, style)
            sheetBag.write(currentRow, 2, city.replace(',', ''), style)
            sheetBag.write(currentRow, 1, address.replace(',', ''), style)
            sheetBag.write(currentRow, 0, name2, style)
        elif packageType == "env":
            print(email2)
        currentRow += 1



workbookBox.save("ShippingBoxes.xls")
workbookBag.save("ShippingEnvelopes.xls")

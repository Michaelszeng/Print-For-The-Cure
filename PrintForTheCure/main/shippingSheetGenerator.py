import xlwt
from xlwt import Workbook
from ShippingInfo_6_4_20 import *   #change depending on shipping day

workbook = Workbook()
sheet = workbook.add_sheet('6.4.20')
style = xlwt.easyxf('font: bold 1')

# row, column
sheet.write(0, 0, 'Full Name', style)
sheet.write(0, 1, 'Address1', style)
sheet.write(0, 2, 'City', style)
sheet.write(0, 3, 'State', style)
sheet.write(0, 4, 'Zipcode', style)
style = xlwt.easyxf('font: bold off')

currentRow = 1
for i in range(len(data)-22):
    nameSearcher = data[i:i+18]
    addressSearcher = data[i:i+21]

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

        sheet.write(currentRow, 0, name, style)

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
        for i in range(len(addressList)-1):
            if len(addressList[i]) == 0:
                addressList.pop(i)
        print(addressList)
        zip = addressList[len(addressList)-2]
        state = addressList[len(addressList)-3]
        if "," in addressList[len(addressList)-5]:
            city = addressList[len(addressList)-4]
            separator = " "
            address = separator.join(addressList[0:len(addressList)-4])
        else:
            city = addressList[len(addressList)-5] + " " + addressList[len(addressList)-4]
            separator = " "
            address = separator.join(addressList[0:len(addressList)-5])

        sheet.write(currentRow, 4, zip, style)
        sheet.write(currentRow, 3, state, style)
        sheet.write(currentRow, 2, city.replace(',', ''), style)
        sheet.write(currentRow, 1, address.replace(',', ''), style)
        currentRow += 1



workbook.save("Shipping.xls")

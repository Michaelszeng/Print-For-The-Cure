from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode
from django.template import loader
from django.http import FileResponse, Http404
# Custom imports added
# Need timezone for date/time published
from django.utils import timezone
import datetime
# These are needed for user authentication and persistence
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# Google library for address validations (used in doctorRequest)
from i18naddress import InvalidAddress, normalize_address

# Google Distance Matrix API Imports
import googlemaps
import json
import urllib.request
import urllib.parse
import random
from .models import Donor
from .models import RequestModel
from .models import Email
from .models import DonorDate
from .models import RequesterDate
# from .gmail import *
# from .sendGrid import *
from .pythonMail import *
from .GoogleAPIKey import *
import string
import numpy as geek
from math import radians, cos, sin, asin, sqrt
import time


def home(request):
    #SENDING DONOR/REQUESTER EMAIL LIST TO PFTC@GMAIL.COM (To activate, delete the DonorDate and RequesterDate objects through admin)
    donorDates = DonorDate.objects.all()
    requesterDates = RequesterDate.objects.all()
    if len(donorDates) == 0:
        print("Creating new donorDate Object")
        newDonorDate = DonorDate(date=timezone.now().date() - datetime.timedelta(days = 22))
        newDonorDate.save()
        print("______________________________SENDING DONOR EMAIL LIST______________________________")
        subject = "DONOR EMAIL LIST"
        message_text = "Donor Email List: \n"
        allUsers = User.objects.all()
        for user1 in User.objects.all():
            try:
                donor = Donor.objects.get(user = user1)
                message_text += user1.email
                message_text += "\n"
            except:
                print("User %s doesn't have donor" % user1.username)
        donorDates = DonorDate.objects.all()
        donorDates[0].date = timezone.now().date()
        donorDates[0].save()
        sendMessage(message_text, subject, "printforthecure@gmail.com")
    if len(requesterDates) == 0:
        print("Creating new requesterDate Object")
        newRequesterDate = RequesterDate(date=timezone.now().date() - datetime.timedelta(days = 22))
        newRequesterDate.save()
        print("______________________________SENDING REQUESTER EMAIL LIST______________________________")
        subject = "REQUESTER EMAIL LIST"
        message_text = "Requester Email List: \n"
        allRequests = RequestModel.objects.all()
        for request in allRequests:
            message_text += request.email
            message_text += "\n"
        requesterDates = RequesterDate.objects.all()
        requesterDates[0].date = timezone.now().date()
        requesterDates[0].save()
        sendMessage(message_text, subject, "printforthecure@gmail.com")

    # if len(donorDates) == 0:
    #     print("Creating new donorDate Object")
    #     newDonorDate = DonorDate(date=timezone.now().date() - datetime.timedelta(days = 22))
    #     newDonorDate.save()
    # else:
    #     print("DonorDate Obj Exists")
    #     if timezone.now().date() > donorDates[0].date + datetime.timedelta(days = 21):
    #         print("______________________________SENDING DONOR EMAIL LIST______________________________")
    #         subject = "DONOR EMAIL LIST"
    #         message_text = "Donor Email List: \n"
    #         allUsers = User.objects.all()
    #         for user1 in User.objects.all():
    #             try:
    #                 donor = Donor.objects.get(user = user1)
    #                 message_text += user1.email
    #                 message_text += "\n"
    #             except:
    #                 print("User %s doesn't have donor" % user1.username)
    #         donorDates[0].date = timezone.now().date()
    #         donorDates[0].save()
    #         sendMessage(message_text, subject, "printforthecure@gmail.com")
    # if len(requesterDates) == 0:
    #     print("Creating new requesterDate Object")
    #     newRequesterDate = RequesterDate(date=timezone.now().date() - datetime.timedelta(days = 22))
    #     newRequesterDate.save()
    # else:
    #     print("RequesterDate Obj Exists")
    #     if timezone.now().date() > requesterDates[0].date + datetime.timedelta(days = 21):
    #         print("______________________________SENDING REQUESTER EMAIL LIST______________________________")
    #         subject = "REQUESTER EMAIL LIST"
    #         message_text = "Requester Email List: \n"
    #         allRequests = RequestModel.objects.all()
    #         for request in allRequests:
    #             message_text += request.email
    #             message_text += "\n"
    #         requesterDates[0].date = timezone.now().date()
    #         requesterDates[0].save()
    #         sendMessage(message_text, subject, "printforthecure@gmail.com")
    #     time.sleep(2)
    #END

    #temporary: to recover the 300 shields request that expired
    # for requestModel in RequestModel.objects.all():
    #     if requestModel.numPPE == 300:
    #         print(requestModel.email)
    #         requestModel.status = 0
    #         requestModel.save()

    # print("Shields Being Requested: " + str(getCurrentRequestedShields(request)))
    # active = 0
    # expired = 0
    # claimed = 0
    # msged = 0
    # for requestModel in RequestModel.objects.all():
    #     if requestModel.status == 0:
    #         active += 1
    #     elif requestModel.status == 1:
    #         expired += 1
    #     elif requestModel.status == 2:
    #         claimed += 1
    #     elif requestModel.status == 3:
    #         msged += 1
    # print("Total active requests: " + str(active))
    # print("Total expired requests: " + str(expired))
    # print("Total claimed requests: " + str(claimed))
    # print("Total claimed and messaged requests: " + str(msged))

    claimRate = getClaimRate(request)

    claimedPPE = 0
    claimedRequests = 0

    requestersServed = []
    statesServed = []
    organizationsServed = []
    for requestModel in RequestModel.objects.all():
        if requestModel.status == 2 or requestModel.status == 3:
            claimedPPE += requestModel.numPPE   #increment the number of claimed PPE
            claimedRequests = claimedRequests + 1
            requesterName = (requestModel.fName + requestModel.lName).lower()
            requesterOrganization = (requestModel.organization).lower().strip()
            if requesterName not in requestersServed:
                requestersServed.append(requesterName)
            if requestModel.state not in statesServed:
                statesServed.append(requestModel.state)
            if requesterOrganization not in organizationsServed:
                organizationsServed.append(requesterOrganization)

        if requestModel.status == 2:
            #If it's been more than 10 days since the delivery date, and the request has been claimed, send the automated email msg asking for a donation
            if timezone.now().date() > requestModel.delivDate + datetime.timedelta(days=18):
                # print("PPE Delivery Successful?")

                subject = "PPE Delivery Successful?"
                #sendgrid version
                # message_text = "Hi,<br /><br />We just wanted to check in to make sure your requested PPE has been delivered by your donor, or that a delivery had been arranged? If not, please make sure to contact your donor to ensure you will get the PPE you need.<br /><br />If you have received your PPE, we hope it is helping you or your coworkers stay safe! Since Print For The Cure personally handles many requests, and reimburses all of our donors, we hope you can help the project continue by supporting it at our gofundme: https://www.gofundme.com/f/printforthecure<br /><br />If you have any questions, please let use know!"

                #pythonMail version
                message_text = "Hi,\n\nWe just wanted to check in to make sure your requested PPE has been delivered by your donor, or that a delivery had been arranged? If not, please make sure to contact your donor to ensure you will get the PPE you need.\n\nIf you have received your PPE, we hope it is helping! If you are comfortable, we would appreciate if you would send us a photo of the PPE in use, which we may display on the website. Print For The Cure handles many requests, and attempts to reimburse all of donors, we hope you can join the movement by supporting it at our gofundme: https://www.gofundme.com/f/printforthecure\n\nIf you have any questions, please let us know!"
                try:
                    sendMessage(message_text, subject, requestModel.email)
                except:
                    print()
                newEmail = Email(recipient=requestModel.email, subject=subject, sentDate=timezone.now().date())
                newEmail.save()
                # try:    #ensure fake emails don't crash website
                #     service = getService()
                #     subject = "PPE Delivery Successful?"
                #     message_text = "Hi,\n\nWe just wanted to check in to make sure your requested PPE has been delivered by your donor, or that a delivery had been arranged? If not, please make sure to contact your donor to ensure you will get the PPE you need.\n\nIf you have received your PPE, we hope it is helping you or your coworkers stay safe! Since Print For The Cure personally handles many requests, and reimburses all of our donors, we hope you can help the project continue by supporting it at our gofundme: https://www.gofundme.com/f/printforthecure\n\nIf you have any questions, please let use know!"
                #     message = makeMessage("printforthecure@gmail.com", requestModel.email, subject, message_text)
                #     sendMessage(service, 'me', message)
                # except:
                #     print("PPE Delivery Successful Email Failed To Send")

                requestModel.status = 3
                requestModel.save()

    claimedPPE = claimedPPE - geek.mod(claimedPPE, 10)
    numRequestersServed = len(requestersServed)
    numStatesServed = len(statesServed)
    numOrganizationsServed = len(organizationsServed)
    numDonors = 0
    for user1 in User.objects.all():
        #print(vars(user1))
        try:
            donor = Donor.objects.get(user = user1)
            numDonors = numDonors + 1
        except:
            print("User %s doesn't have donor" % user1.username)

    print("claimedPPE: " + str(claimedPPE))

    # print(request.user.is_authenticated)
    if request.method == 'POST':
        if 'login' in request.POST.keys():
            return HttpResponseRedirect("/login/")
        if 'logout' in request.POST.keys():
            print(request.user.is_authenticated)
            logout(request)
            return HttpResponseRedirect("/login/")
        elif 'submitRequest' in request.POST.keys():
            return HttpResponseRedirect("/requestPPE/")
        elif 'mapView' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")
        elif 'shield' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-shield/")
        elif 'hook' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-maskstrap/")
        elif 'opener' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-dooropener/")
        elif 'handle' in request.POST.keys():
            return HttpResponseRedirect("/catalogue-handle/")
        elif 'guide' in request.POST.keys():
            return HttpResponseRedirect("/donorGuide/")
        elif 'leaderboard' in request.POST.keys():
            return HttpResponseRedirect("/donorLeaderboards/")
        elif 'donate' in request.POST.keys():
            return redirect("https://www.gofundme.com/f/printforthecure")
        elif 'wishlist' in request.POST.keys():
            return redirect("https://www.amazon.com/hz/wishlist/ls/3CZR7482U6HP?ref_=wl_share")

    template = loader.get_template('main/home.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated,
        'claimRate': claimRate,
        'claimedPPE': claimedPPE,
        'claimedRequests': claimedRequests,
        'requestersServed': numRequestersServed,
        'organizationsServed': numOrganizationsServed,
        'statesServed': numStatesServed,
        'numDonors':numDonors
    }
    return HttpResponse(template.render(context, request))

def catalogueShield(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/shield.html')
    context = {}
    return HttpResponse(template.render(context, request))

def catalogueMaskStrap(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/hook.html')
    context = {}
    return HttpResponse(template.render(context, request))

def catalogueDoorOpener(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/opener.html')
    context = {}
    return HttpResponse(template.render(context, request))

def catalogueHandle(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/handle.html')
    context = {}
    return HttpResponse(template.render(context, request))

def donorGuidePDF(request):
    try:
        return FileResponse(open('C:\\Users\\Michael Zeng\\Documents\\Programming\\Project Face Shield mk2\\PrintForTheCure\\main\\donorGuide.pdf', 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()
    # with open('C:\\Users\\Michael Zeng\\Documents\\Programming\\Project Face Shield mk2\\PrintForTheCure\\main\\donorGuide.pdf', 'r') as pdf:
    #     response = HttpResponse(pdf.read(), contenttype='application/pdf')
    #     response['Content-Disposition'] = 'inline;filename=donorGuide.pdf'
    #     return response
    # pdf.closed

def donorRegistration(request):
    failMessage = ""
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")
        elif request.POST['password'] == request.POST['passwordConfirm']:
            # try:
            #     address = normalize_address({
            #     'country_code': request.POST['country'],
            #     'country_area': request.POST['state'],
            #     'city': request.POST['city'],
            #     'postal_code': request.POST['zipCode']})
            # except InvalidAddress as e:
            #     print("failed")
            #     print(e.errors)
            #     failMessage += "Sorry, Address Validation failed. Please enter a valid address for delivery.\n"
            users = User.objects.all()
            usernames = []
            for user in users:
                usernames.append(user.username)
            if request.POST['username'] in usernames:
                failMessage += "Sorry, username is already taken! Please choose another one. "
            if (len(request.POST['username']) < 1) or (len(request.POST['password']) < 1) or (len(request.POST['email']) < 1) or (len(request.POST['fName']) < 1) or (len(request.POST['lName']) < 1):
                failMessage += "Please ensure all fields are filled out."
            elif (len(failMessage) == 0):
                newUser = User(username=request.POST['username'], password=request.POST['password'], email=request.POST['email'], first_name=request.POST['fName'], last_name=request.POST['lName'])
                newUser.set_password(request.POST['password'])
                newUser.save()
                newDonor = Donor(user=newUser, ppe=0, address=request.POST['address'], city=request.POST['city'], state=request.POST['state'], country=request.POST['country'], zipCode=request.POST['zipCode'], registrationDate=timezone.now())
                newDonor.save()

                user = authenticate(username=request.POST['username'], password=request.POST['password'])
                login(request, user)

                subject = "PrintForTheCure Registration Details"
                #sendgrid version
                # message_text = "Thank you for registing with PrintForTheCure! Now you can get started claiming and fulfilling PPE requests on printforthecure.com!<br /><br />Your Username: %s" % (request.POST['username'])

                #pythonMail version
                message_text = "Thank you for registing with PrintForTheCure! Now you can get started claiming and fulfilling PPE requests on printforthecure.com!\n\nYour Username: %s" % (request.POST['username'])
                sendMessage(message_text, subject, request.POST['email'])
                # print("Registration email sent")
                newEmail = Email(recipient=request.POST['email'], subject=subject, sentDate=timezone.now().date())
                newEmail.save()

                # try:    #ensure fake emails don't crash website
                #     service = getService()
                #     #Donor Email
                #     subject = "PrintForTheCure Registration Details"
                #     message_text = "Thank you for registing with PrintForTheCure! Now you can get started claiming and fulfilling PPE requests on printforthecure.com!\n\nYour Username: %s" % (request.POST['username'])
                #     message = makeMessage("printforthecure@gmail.com", request.POST['email'], subject, message_text)
                #     sendMessage(service, 'me', message)
                # except:
                #     print("email verification failed")

                return HttpResponseRedirect("/registrationSuccessful/")
        else:
            failMessage += "Passwords do not match. "
    template = loader.get_template('main/register.html')
    context = {     #all inputs for the html go in these brackets
        'failMessage': failMessage
    }
    return HttpResponse(template.render(context, request))

def registrationSuccessful(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/registrationSuccessful.html')
    context = {}
    return HttpResponse(template.render(context, request))

def donorLogin(request):
    if request.method == "POST":
        # This tests if the form is the log *in* form
        if 'username' in request.POST.keys():
            # IF so, try to authentircate
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                # IF success, then use the login function so the session persists.
                login(request, user)
                return HttpResponseRedirect("/")
            else:
                pass
        elif 'register' in request.POST.keys():
            return HttpResponseRedirect("/noLongerActive")
            # return HttpResponseRedirect("/register")
    # After we check the forms, set a flag for use in the template.
    if request.user.is_authenticated:
        template = loader.get_template('main/home.html')
        authenticated = True
    else:
        template = loader.get_template('main/donorLogin.html')
        authenticated = False
    # Find the template
    context = {
        'authenticated': authenticated
    }
    return HttpResponse(template.render(context, request))

def noLongerActive(request):
    template = loader.get_template('main/noLongerActive.html')
    context = {

    }
    return HttpResponse(template.render(context, request))

def doctorRequest(request):
    validationStatus = ""
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")
        print(vars(request.POST))

        validated = True
        try:
            address = normalize_address({
            'country_code': request.POST['country'],
            'country_area': request.POST['state'],
            'city': removeASCII(request.POST['city']),
            'postal_code': removeASCII(request.POST['zipCode']),
            'street_address': removeASCII(request.POST['address'])})
        except InvalidAddress as e:
            print("failed")
            print(e.errors)
            validated = False
            validationStatus += "Sorry, Address Validation failed. Please enter a valid address for delivery.\n"
        if request.POST['typePPE'] == "handle":
            try:
                typeHandle = request.POST['typeHandle']
            except:
                validated = False
                validationStatus += "Please include a type of door handle. "
        if (len(request.POST['fName']) < 1) or (len(request.POST['lName']) < 1) or (len(request.POST['email']) < 1):
            validated = False
            validationStatus += "Please ensure all fields are filled out. "
        if timezone.now().date() + datetime.timedelta(days=4) > datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day'])):
            validated = False
            validationStatus += "Please set the delivery date later. "
        if request.POST['confirmEmail'] != request.POST['email']:
            validated = False
            validationStatus += "Please ensure both email boxes contain the same, valid email address."
        if validated:
            print("Address Validation Succeeded")

            if request.POST['typePPE'] == "handle":
                newRequest = RequestModel(id=RequestModel.objects.latest('orderDate').id + random.randrange(1, 100, 1), status=0, fName=removeASCII(request.POST['fName']), lName=removeASCII(request.POST['lName']), email=removeASCII(request.POST['email'].replace(" ", "")), phone=removeASCII(request.POST['phone']), organization=removeASCII(request.POST['organization']), numPPE=request.POST['numPPE'], typePPE=request.POST['typePPE'], typeHandle=request.POST['typeHandle'], address=removeASCII(request.POST['address']), city=removeASCII(request.POST['city']), state=request.POST['state'], country=request.POST['country'], lat=request.POST['lat'], lng=request.POST['lng'], zipCode=request.POST['zipCode'], delivDate=datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day'])) , orderDate=timezone.now(), notes=removeASCII(request.POST['otherNotes']))
                print(request.POST['lat'] + ", " + request.POST['lng'])
                newRequest.save()
            else:
                newRequest = RequestModel(id=RequestModel.objects.latest('orderDate').id + random.randrange(1, 100, 1), status=0, fName=removeASCII(request.POST['fName']), lName=removeASCII(request.POST['lName']), email=removeASCII(request.POST['email'].replace(" ", "")), phone=removeASCII(request.POST['phone']), organization=removeASCII(request.POST['organization']), numPPE=request.POST['numPPE'], typePPE=request.POST['typePPE'], typeHandle="", address=removeASCII(request.POST['address']), city=removeASCII(request.POST['city']), state=request.POST['state'], country=request.POST['country'], lat=request.POST['lat'], lng=request.POST['lng'], zipCode=request.POST['zipCode'], delivDate=datetime.date(int(request.POST['year']), int(request.POST['month']), int(request.POST['day'])) , orderDate=timezone.now(), notes=removeASCII(request.POST['otherNotes']))
                print(request.POST['lat'] + ", " + request.POST['lng'])
                newRequest.save()

            requestObj = RequestModel.objects.get(id=newRequest.id)

            subject = "Request For PPE Submitted!"
            ppeType = ""
            if "shield" in requestObj.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestObj.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestObj.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            elif "opener" in requestObj.typePPE:
                ppeType = "Personal Touchless Door Opener"
            #sendgrid version
            # message_text = "Thank You For Submitting a Request For PPE!<br /><br />Request Details: <br />Requester's Name: %s %s<br />Requester's Email: %s<br />Requester's Phone Number: %s<br />Requester's Address: %s %s %s %s %s<br /><br />Type of PPE Requested: %s<br />Amount of PPE Requested: %s<br />ideal \"Deliver By\" date of requested PPE: %s<br /><br />Other Notes From the Requester: %s<br /><br />You will be emailed again either when a donor chooses to claim and fulfill your request, or if your request expires before any donors get the chance. We hope you you stay protected during these times!" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes)

            #pythonMail version
            message_text = removeASCII("Thank You For Submitting a Request For PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %s\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes From the Requester: %s\n\nYou will be emailed again either when a donor chooses to claim and fulfill your request, or if your request expires before any donors get the chance. We hope you you stay protected during these times!" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes))
            sendMessage(message_text, subject, requestObj.email)
            newEmail = Email(recipient=requestObj.email, subject=subject, sentDate=timezone.now().date())
            newEmail.save()

            # service = getService()
            # #Donor Email
            # subject = "Request For PPE Submitted!"
            # ppeType = ""
            # if "shield" in requestObj.typePPE:
            #     ppeType = "3D Printed Face Shields"
            # elif "strap" in requestObj.typePPE:
            #     ppeType = "Face Mask Comfort Strap"
            # elif "handle" in requestObj.typePPE:
            #     ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            # elif "opener" in requestObj.typePPE:
            #     ppeType = "Personal Touchless Door Opener"
            # message_text = "Thank You For Submitting a Request For PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %s\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes From the Requester: %s\n\nYou will be emailed again either when a donor chooses to claim and fulfill your request, or if your request expires before any donors get the chance. We hope you you stay protected during these times!" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, requestObj.delivDate, requestObj.notes)
            # message = makeMessage("printforthecure@gmail.com", requestObj.email, subject, message_text)
            # sendMessage(service, 'me', message)

            return HttpResponseRedirect("/requestSubmitSuccessful/")

    template = loader.get_template('main/submitRequest.html')
    context = {     #all inputs for the html go in these brackets
        'validationStatus': validationStatus
    }
    return HttpResponse(template.render(context, request))

def requestSubmitSuccessful(request):
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/requestSubmitSuccessful.html')
    context = {}
    return HttpResponse(template.render(context, request))

def map(request):
    #GEOCODES 0.0,0.0 REQUESTS; IF THIS CAUSES TOO MAY GEOCODE REQUESTS FOR OUR BUDGET, WE'LL REMOVE IT
    for requestModel in RequestModel.objects.all():
        print(requestModel.lat)
        if requestModel.status == 0 and requestModel.lat-0.0 < 0.1 and requestModel.lng-0.0 < 0.1:   #don't use ==0 since double comparisions are bad
            try :
                address = requestModel.address
                url = ('https://maps.googleapis.com/maps/api/geocode/json' + '?address={}' + '&key={}').format(urllib.parse.quote(address, safe=""), key)
                response = urllib.request.urlopen(url)
                responseJSON = json.loads(response.read())
                requestModel.lat = responseJSON.get("results")[0].get("geometry").get("location").get("lat")
                requestModel.lng = responseJSON.get("results")[0].get("geometry").get("location").get("lng")
                requestModel.save()
            except:
                print("geocoding failed, status = ZERO_RESULTS")
                requestModel.delete()
    #END GEOCODING

    allUnclaimedRequests = []
    addresses = []
    counter = 0
    for requestModel in RequestModel.objects.all():
        if timezone.now().date() > requestModel.delivDate + datetime.timedelta(days=3) and requestModel.status == 0:
            print("Deleting RequestModel (date passed): " + str(requestModel.delivDate))
            requestModel.status = 1
            requestModel.save()

            subject = "Request For PPE Submitted!"
            ppeType = ""
            if "shield" in requestModel.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestModel.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestModel.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestModel.typeHandle
            elif "opener" in requestModel.typePPE:
                ppeType = "Personal Touchless Door Opener"
            #sendgrid version
            # message_text = "We are sorry to notify you that your request for PPE has expired without being claimed. Your request Details:<br /><br /><br />Requester's Name: %s %s<br />Requester's Email: %s<br />PPE Delivery Address: %s %s %s %s %s<br /><br />Type of PPE Requested: %s<br />Amount of PPE Requested: %s<br />Ideal \"Deliver By\" date of requested PPE: %s<br /><br />Other Notes For the Donor: %s<br /><br />As the website is just launching, we are gathering more donors to help ensure our essential workers can get the PPE they need. Please request again on https://printforthecure.com and we will do our best to help you next time. Thank you for your understanding.<br /><br />Please contact us at printforthecure@gmail.com with any questions." % (requestModel.fName, requestModel.lName, requestModel.email, requestModel.address, requestModel.city, requestModel.state, requestModel.zipCode, requestModel.country, ppeType, requestModel.numPPE, requestModel.delivDate, requestModel.notes)

            #pythonMail version
            message_text = "We are sorry to notify you that your request for PPE has expired without being claimed. Your request Details:\n\n\nRequester's Name: %s %s\nRequester's Email: %s\nPPE Delivery Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %s\nIdeal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nWe are always gathering more donors to help ensure our essential workers can get the PPE they need. Please request again on https://printforthecure.com and we will do our best to help you next time. Thank you for your understanding.\n\nPlease contact us at printforthecure@gmail.com with any questions." % (removeASCII(requestModel.fName), removeASCII(requestModel.lName), removeASCII(requestModel.email), removeASCII(requestModel.address), removeASCII(requestModel.city), removeASCII(requestModel.state), removeASCII(requestModel.zipCode), removeASCII(requestModel.country), ppeType, requestModel.numPPE, requestModel.delivDate, removeASCII(requestModel.notes))
            sendMessage(message_text, subject, requestModel.email)
            newEmail = Email(recipient=requestModel.email, subject=subject, sentDate=timezone.now().date())
            newEmail.save()

            # service = getService()
            # subject = "Request For PPE Expired"
            # ppeType = ""
            # if "shield" in requestModel.typePPE:
            #     ppeType = "3D Printed Face Shields"
            # elif "strap" in requestModel.typePPE:
            #     ppeType = "Face Mask Comfort Strap"
            # elif "handle" in requestModel.typePPE:
            #     ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestModel.typeHandle
            # elif "opener" in requestModel.typePPE:
            #     ppeType = "Personal Touchless Door Opener"
            # message_text = "We are sorry to notify you that your request for PPE has expired without being claimed. Your request Details:\n\n\nRequester's Name: %s %s\nRequester's Email: %s\nPPE Delivery Address: %s %s %s %s %s\n\nType of PPE Requested: %d\nAmount of PPE Requested: %s\nIdeal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nAs the website is just launching, we are gathering more donors to help ensure our essential workers can get the PPE they need. Please request again on https://printforthecure.com and we will do our best to help you next time. Thank you for your understanding.\n\nPlease contact us at printforthecure@gmail.com with any questions." % (requestModel.fName, requestModel.lName, requestModel.email, requestModel.address, requestModel.city, requestModel.state, requestModel.zipCode, requestModel.country, ppeType, requestModel.numPPE, requestModel.delivDate, requestModel.notes)
            # message = makeMessage("printforthecure@gmail.com", requestModel.email, subject, message_text)
            # sendMessage(service, 'me', message)

        if requestModel.status == 0:
            address = requestModel.address + " " + requestModel.city + " " + requestModel.state + " " + requestModel.zipCode
            addressId = "address" + str(counter)
            addresses.append({'addressId': addressId, 'address': address})
            allUnclaimedRequests.append(requestModel)
            counter += 1
    # print(addresses)

    if request.method == 'POST':
        if 'requestObjId' in request.POST.keys():
            print("hi")
            if request.user.is_authenticated:
                base_url = '/confirmation1/'  # 1 /products/
                query_string =  urlencode({'requestObjId': request.POST['requestObjId']})  # 2 category=42
                url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
                return HttpResponseRedirect(url)  # 4
            else:
                return HttpResponseRedirect('/notLoggedIn/')

    template = loader.get_template('main/mapView.html')
    context = {     #all inputs for the html go in these brackets
        'authenticated': request.user.is_authenticated,
        'allRequests': allUnclaimedRequests,
        'addresses': addresses,
        'key': key,
    }
    return HttpResponse(template.render(context, request))

def requestPopup(request):
    template = loader.get_template('main/requestPopup.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def take_first(elem):
    return elem[0]

def nearbyRequests(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/notLoggedIn/")

    allUnclaimedRequests = []

    #Set the default sortBy method
    previousSortBy = "delivDate"
    sortBy = "delivDate"

    if request.method == 'POST':
        print("request.POST.keys(): " + str(request.POST.keys()))
        print("sortBy: " + sortBy)
        print("previouseSortBy: " + previousSortBy)
        if request.user.is_authenticated:
            currentSortBy = request.POST['sortBy']
            print("CurrentSortBy: " + str(currentSortBy))
            # print("REQUEST POST KEYS")
            # print(request.POST.keys())
            # print(request.POST['sortBy'])
            if 'sortBy' in request.POST.keys():
                if request.POST['sortBy'] == 'delivDate':
                    sortBy = "delivDate"
                    print("------date")
                    #Below uses date to sort the list of requests from most urgent to least
                    allDateNumbers = []
                    for requestModel in RequestModel.objects.all():
                        if requestModel.status == 0:
                            allUnclaimedRequests.append(requestModel)
                            print(10000*requestModel.delivDate.year + 100*requestModel.delivDate.month + requestModel.delivDate.day)
                            allDateNumbers.append(10000*requestModel.delivDate.year + 100*requestModel.delivDate.month + requestModel.delivDate.day)

                    keydict = dict(zip(allUnclaimedRequests, allDateNumbers))
                    allUnclaimedRequests.sort(key=keydict.get)
                    # print(allUnclaimedRequests)
                elif request.POST['sortBy'] == 'distance':
                    sortBy = "distance"
                    print("------distance")
                    #Below uses Google's Distance Matrix API to sort the list of requests from nearest to furthest
                    donor = Donor.objects.get(user = request.user)

                    addressList = donor.address.split()
                    addressFormatted = ""
                    for word in addressList:
                        addressFormatted += word
                        addressFormatted += "+"

                    cityList = donor.city.split()
                    cityFormatted = ""
                    for word in cityList:
                        addressFormatted += word
                        addressFormatted += "+"

                    origin = addressFormatted + cityFormatted + donor.state + "+" + donor.zipCode

                    donorLat = donor.lat
                    donorLng = donor.lng
                    if donorLat - 0.0 < 0.2 and donorLng - 0.0 < 0.2:
                        url = ('https://maps.googleapis.com/maps/api/geocode/json' + '?address={}' + '&key={}').format(urllib.parse.quote(origin, safe=""), key)
                        response = urllib.request.urlopen(url)
                        responseJSON = json.loads(response.read())
                        donor.lat = responseJSON.get("results")[0].get("geometry").get("location").get("lat")
                        donor.lng = responseJSON.get("results")[0].get("geometry").get("location").get("lng")
                        donor.save()

                    allUnclaimedRequests = []
                    distancesList = []
                    for requestModel in RequestModel.objects.all():
                        if requestModel.status == 0:
                            allUnclaimedRequests.append(requestModel)
                            distance = calcDistance(donorLat, requestModel.lat, donorLng, requestModel.lng)
                            distancesList.append(distance)

                    keydict = dict(zip(allUnclaimedRequests, distancesList))
                    allUnclaimedRequests.sort(key=keydict.get)
                    print("distancesList: " + str(distancesList))

                    # destination = []
                    # allDistances = []
                    # numDestinations = 1
                    # numApiCalls = 1
                    # for requestModel in RequestModel.objects.all():
                    #     # print("mod result" + str(geek.mod(numDestinations, 25)))
                    #     if requestModel.status == 0 and numDestinations > 25 and geek.mod(numDestinations, 25) == 1:
                    #         # print(str(numDestinations) + " " + str(geek.mod(numDestinations, 25)) + " reached 25 limit for destinations")
                    #         numApiCalls = 2
                    #         destination = "|".join(destination)
                    #         url = ('https://maps.googleapis.com/maps/api/distancematrix/json' + '?origins={}' + '&destinations={}' + '&key={}').format(urllib.parse.quote(origin, safe=""), urllib.parse.quote(destination, safe=""), key)
                    #         response = urllib.request.urlopen(url)
                    #         responseJSON = json.loads(response.read())
                    #
                    #         # print(responseJSON)
                    #         for item in (responseJSON.get("rows", "none")[0].get("elements", "none")):
                    #             if (item.get("status", "none") != 'NOT_FOUND'):
                    #                 distanceStr = item.get("distance", "none").get("value", "none")
                    #                 allDistances.append(distanceStr)
                    #                 #print(item.get("distance", "none").get("text", "none"))
                    #         destination = []
                    #
                    #     if requestModel.status == 0:
                    #
                    #         addressList = requestModel.address.split()
                    #         addressFormatted = ""
                    #         for word in addressList:
                    #             addressFormatted += word
                    #             addressFormatted += "+"
                    #
                    #         cityList = requestModel.city.split()
                    #         cityFormatted = ""
                    #         for word in cityList:
                    #             addressFormatted += word
                    #             addressFormatted += "+"
                    #
                    #         destination.append(addressFormatted + cityFormatted + requestModel.state + "+" + requestModel.zipCode)
                    #     numDestinations = numDestinations + 1
                    #
                    # destination = "|".join(destination)
                    # url = ('https://maps.googleapis.com/maps/api/distancematrix/json' + '?origins={}' + '&destinations={}' + '&key={}').format(urllib.parse.quote(origin, safe=""), urllib.parse.quote(destination, safe=""), key)
                    # response = urllib.request.urlopen(url)
                    # responseJSON = json.loads(response.read())
                    #
                    # for item in (responseJSON.get("rows", "none")[0].get("elements", "none")):
                    #     if (item.get("status", "none") != 'NOT_FOUND'):
                    #         distanceStr = item.get("distance", "none").get("value", "none")
                    #         # print("hi" + str(distanceStr))
                    #         allDistances.append(distanceStr)
                    #         #print(item.get("distance", "none").get("text", "none"))
                    #
                    # for requestModel in RequestModel.objects.all():
                    #     if requestModel.status == 0:
                    #         allUnclaimedRequests.append(requestModel)
                    #
                    # #Insertion Sorting
                    # #Sort the distances, then rearrange allUnclaimedRequests
                    # # for i in range(1, len(allDistances)):
                    # #     j = i
                    # #     while j>=1 and allDistances[j] < allDistances[j-1]:
                    # #         allDistances[j], allDistances[j-1] = allDistances[j-1], allDistances[j]
                    # #         allUnclaimedRequests[j], allUnclaimedRequests[j-1] = allUnclaimedRequests[j-1], allUnclaimedRequests[j]
                    # #         j -= 1
                    #
                    # #Dict Python Sorting
                    # keydict = dict(zip(allUnclaimedRequests, allDistances))
                    # allUnclaimedRequests.sort(key=keydict.get)
                    # # print(allUnclaimedRequests)
            previouseSortBy = sortBy
            if 'confirmClaims' in request.POST.keys():
                print("sortBy: " + sortBy)
                print("previouseSortBy: " + previousSortBy)
                print("------------------------CONFIRMING CLAIM")
                # print("request.post: ", vars(request))
                base_url = '/confirmation/?requestObjIds='
                for keyIndex, postKey in enumerate(request.POST.keys()):
                    if "checkBox" in postKey:
                        idNum = postKey[8:]
                        print(idNum)
                        base_url += idNum + '+'
                        # query_string = urlencode({'requestObjId' + str(keyIndex): idNum})

                # url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
                url = base_url
                print(url)
                return HttpResponseRedirect(url)
            # else:
            # if 'requestObjId' in request.POST.keys():
            #     # print("Request ID: " + request.POST['requestModelId'])
            #
            #     # print("Request Object: " + str(vars(requestObj)))
            #     #return HttpResponseRedirect('/confirmation/' + '?' + "requestId=" + )
            #
            #     base_url = '/confirmation/'  # 1 /products/
            #     query_string =  urlencode({'requestObjIds=': request.POST['requestObjId']})  # 2 category=42
            #     url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            #     return HttpResponseRedirect(url)  # 4
    else:
        #Below uses date to sort the list of requests from most urgent to least
        allDateNumbers = []
        for requestModel in RequestModel.objects.all():
            if requestModel.status == 0:
                allUnclaimedRequests.append(requestModel)
                print(10000*requestModel.delivDate.year + 100*requestModel.delivDate.month + requestModel.delivDate.day)
                allDateNumbers.append(10000*requestModel.delivDate.year + 100*requestModel.delivDate.month + requestModel.delivDate.day)

        keydict = dict(zip(allUnclaimedRequests, allDateNumbers))
        allUnclaimedRequests.sort(key=keydict.get)
        print(allUnclaimedRequests)

    if sortBy == "delivDate":
        sortedNotBy = "distance"
    else:
        sortedNotBy = "delivDate"

    template = loader.get_template('main/nearbyRequests.html')
    context = {     #all inputs for the html go in these brackets
        'sortBy': sortBy,
        'sortedNotBy': sortedNotBy,
        'allRequests': allUnclaimedRequests,
        'authenticated': request.user.is_authenticated,
    }
    return HttpResponse(template.render(context, request))

def requestDetails(request):
    template = loader.get_template('main/requestDetails.html')
    context = {}
    return HttpResponse(template.render(context, request))

def notLoggedIn(request):
    if request.method == 'POST':
        if 'return' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")

    template = loader.get_template('main/notLoggedIn.html')
    context = {     #all inputs for the html go in these brackets

    }
    return HttpResponse(template.render(context, request))

def confirmClaim(request):
    counter = 2
    print("URL IDs: " + request.GET.get("requestObjIds"))
    idList = request.GET.get("requestObjIds").split(" ")
    del idList[-1]
    print(idList)

    requestObjs = []
    for id in idList:
        requestObjs.append(RequestModel.objects.get(id=int(id)))

    print(requestObjs)


    # for key in request.GET:
    #     valueId = key.get("requestObjIds")
    #     print("getKey: ", valueId)
    #     requestObjs.append(RequestModel.objects.get(id=int(valueId)))
    #     counter = counter + 1

    #OLD SINGLE CLAIM VERSION
    # requestModelId = request.GET.get('requestObjId')  # 5
    # print(requestModelId)
    # requestObj = RequestModel.objects.get(id=requestModelId)

    if request.method == 'POST':
        if 'yes' in request.POST.keys():
            for requestObj in requestObjs:

                #Donor Email
                subject = "Claimed Request For PPE"
                ppeType = ""
                if "shield" in requestObj.typePPE:
                    ppeType = "3D Printed Face Shields"
                elif "strap" in requestObj.typePPE:
                    ppeType = "Face Mask Comfort Strap"
                elif "handle" in requestObj.typePPE:
                    ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
                elif "opener" in requestObj.typePPE:
                    ppeType = "Personal Touchless Door Opener"
                #sendgrid version
                #message_text = "Thank You For Claiming a request for PPE!<br /><br />Request Details: <br />Requester's Name: %s %s<br />Requester's Email: %s<br />Requester's Phone Number: %s<br />Requester's Organization: %s<br />Requester's Address: %s %s %s %s %s<br /><br />Type of PPE Requested: %s<br />Amount of PPE Requested: %d<br />ideal \"Deliver By\" date for the requested PPE: %s<br /><br />Other Notes From the Requester: %s<br /><br />Delivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. <br /><br />Thank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )<br />If you are interested in receiving a donation as a reward, we suggest that you communicate to your requester directly. To get a reimbursement, contact Print For The Cure at printforthecure@gmail.com." % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes)

                #pythonMail version
                message_text = removeASCII("Thank You For Claiming a request for PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date for the requested PPE: %s\n\nOther Notes From the Requester: %s\n\nDelivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. \n\nThank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )\nIf you are interested in receiving a donation as a reward, we suggest that you communicate to your requester directly. To get a reimbursement, contact Print For The Cure at printforthecure@gmail.com." % (removeASCII(requestObj.fName), removeASCII(requestObj.lName), removeASCII(requestObj.email), removeASCII(requestObj.phone), removeASCII(requestObj.organization), removeASCII(requestObj.address), removeASCII(requestObj.city), requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, str(requestObj.delivDate), removeASCII(requestObj.notes)))
                sendMessage(message_text, subject, request.user.email)
                newEmail = Email(recipient=request.user.email, subject=subject, sentDate=timezone.now().date())
                newEmail.save()


                # service = getService()
                # #Donor Email
                # subject = "Claimed Request For PPE"
                # ppeType = ""
                # if "shield" in requestObj.typePPE:
                #     ppeType = "3D Printed Face Shields"
                # elif "strap" in requestObj.typePPE:
                #     ppeType = "Face Mask Comfort Strap"
                # elif "handle" in requestObj.typePPE:
                #     ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
                # elif "opener" in requestObj.typePPE:
                #     ppeType = "Personal Touchless Door Opener"
                # message_text = "Thank You For Claiming a request for PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date for the requested PPE: %s\n\nOther Notes From the Requester: %s\n\nDelivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. \n\nThank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )\nIf you are interested in receiving a donation as a reward, we suggest that you communicate to your requester directly. To get a reimbursement, contact Print For The Cure at printforthecure@gmail.com." % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes)
                # message = makeMessage("printforthecure@gmail.com", request.user.email, subject, message_text)
                # try:
                #     sendMessage(service, 'me', message)
                # except:
                #     print("message failed to send")

                #Doctor Email
                try:
                    donor = Donor.objects.get(user = request.user)
                except:
                    print("retrieving donor failed")
                subject = "Request For PPE Claimed"
                #sendgrid version
                # message_text1 = "Your Request for PPE has been claimed by a donor!<br /><br />Request Details: <br />Requester's Name: %s %s<br />Requester's Email: %s<br />Requester's Phone Number: %s<br />Requester's Organization: %s<br />Requester's Address:<br />%s<br />%s, %s %s<br /><br />Type of PPE Requested: %s<br />Amount of PPE Requested: %d<br />ideal \"Deliver By\" date of requested PPE: %s<br /><br />Other Notes For the Donor: %s<br /><br />Your Donor's Name: %s<br />Donor's Email: %s<br /><br />We suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.<br /><br />It is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice message, or even a small monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes, request.user.get_full_name(), request.user.email)

                #pythonMail version
                try:
                    message_text1 = removeASCII("Your Request for PPE has been claimed by a donor!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address:\n%s\n%s, %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nYour Donor's Name: %s\nDonor's Email: %s\n\nWe suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.\n\nIt is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice message, or even a small monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (removeASCII(requestObj.fName), removeASCII(requestObj.lName), requestObj.email, removeASCII(requestObj.phone), removeASCII(requestObj.organization), removeASCII(requestObj.address), requestObj.city, requestObj.state, requestObj.zipCode, ppeType, requestObj.numPPE, str(requestObj.delivDate), removeASCII(requestObj.notes), request.user.get_full_name(), request.user.email))
                    sendMessage(message_text1, subject, requestObj.email)
                    newEmail = Email(recipient=requestObj.email, subject=subject, sentDate=timezone.now().date())
                    newEmail.save()
                except:
                    print("Message Failed To Send")

                #Doctor Email
                # donor = Donor.objects.get(user = request.user)
                # subject = "Request For PPE Claimed"
                # message_text1 = "Your Request for PPE has been claimed by a donor!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address:\n%s\n%s, %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nYour Donor's Name: %s\nDonor's Email: %s\n\nWe suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.\n\nIt is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice message, or even a small monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes, request.user.get_full_name(), request.user.email)
                # message = makeMessage("printforthecure@gmail.com", requestObj.email, subject, message_text1)
                # try:
                #     sendMessage(service, 'me', message)
                # except:
                #     print("message failed to send")

                requestObj.status = 2
                requestObj.save()

                try:
                    donor = Donor.objects.get(user = request.user)
                    donor.ppe += requestObj.numPPE
                    donor.requests += 1
                    if requestObj.typePPE == "shield":
                        print("Donor claimed shield")
                        donor.shields += requestObj.numPPE
                    elif requestObj.typePPE == "strap":
                        print("Donor claimed shield")
                        donor.straps += requestObj.numPPE
                    elif requestObj.typePPE == "opener":
                        print("Donor claimed shield")
                        donor.openers += requestObj.numPPE
                    elif requestObj.typePPE == "handle":
                        print("Donor claimed shield")
                        donor.handles += requestObj.numPPE
                    donor.save()
                except:
                    print("retrieving donor failed")

            base_url = '/thankyou/'  # 1 /products/
            query_string =  urlencode({'requestDetails': message_text})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            return HttpResponseRedirect(url)  # 4


        elif 'no' in request.POST.keys():
            return HttpResponseRedirect("/nearbyRequests/")
    template = loader.get_template('main/confirmClaim.html')
    context = {     #all inputs for the html go in these brackets
        'requestObjs': requestObjs,
    }
    return HttpResponse(template.render(context, request))

def confirmClaim1(request):
    requestModelId = request.GET.get('requestObjId')  # 5
    print(requestModelId)
    requestObj = RequestModel.objects.get(id=requestModelId)

    if request.method == 'POST':
        if 'yes' in request.POST.keys():

            #Donor Email
            subject = "Claimed Request For PPE"
            ppeType = ""
            if "shield" in requestObj.typePPE:
                ppeType = "3D Printed Face Shields"
            elif "strap" in requestObj.typePPE:
                ppeType = "Face Mask Comfort Strap"
            elif "handle" in requestObj.typePPE:
                ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            elif "opener" in requestObj.typePPE:
                ppeType = "Personal Touchless Door Opener"
            #sendgrid version
            # message_text = "Thank You For Claiming a request for PPE!<br /><br />Request Details: <br />Requester's Name: %s %s<br />Requester's Email: %s<br />Requester's Phone Number: %s<br />Requester's Organization: %s<br />Requester's Address: %s %s %s %s %s<br /><br />Type of PPE Requested: %s<br />Amount of PPE Requested: %d<br />ideal \"Deliver By\" date for the requested PPE: %s<br /><br />Other Notes From the Requester: %s<br /><br />Delivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. <br /><br />Thank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )<br />If you are interested in receiving a donation as a reward, we suggest that you communicate to your requester directly. To get a reimbursement, contact Print For The Cure at printforthecure@gmail.com." % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes)

            #pythonMail version
            message_text = removeASCII("Thank You For Claiming a request for PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address:\n%s\n%s, %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date for the requested PPE: %s\n\nOther Notes From the Requester: %s\n\nDelivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. \n\nThank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )\nIf you are interested in receiving a donation as a reward, we suggest that you communicate to your requester directly. To get a reimbursement, contact Print For The Cure at printforthecure@gmail.com." % (removeASCII(requestObj.fName), removeASCII(requestObj.lName), removeASCII(requestObj.email), removeASCII(requestObj.phone), removeASCII(requestObj.organization), removeASCII(requestObj.address), requestObj.city, requestObj.state, requestObj.zipCode, ppeType, requestObj.numPPE, str(requestObj.delivDate), removeASCII(requestObj.notes)))
            sendMessage(message_text, subject, request.user.email)
            newEmail = Email(recipient=request.user.email, subject=subject, sentDate=timezone.now().date())
            newEmail.save()

            # service = getService()
            # #Donor Email
            # subject = "Claimed Request For PPE"
            # ppeType = ""
            # if "shield" in requestObj.typePPE:
            #     ppeType = "3D Printed Face Shields"
            # elif "strap" in requestObj.typePPE:
            #     ppeType = "Face Mask Comfort Strap"
            # elif "handle" in requestObj.typePPE:
            #     ppeType = "Touch-less Door Handle; %s (Link: https://www.materialise.com/en/hands-free-door-opener/technical-information)" % requestObj.typeHandle
            # elif "opener" in requestObj.typePPE:
            #     ppeType = "Personal Touchless Door Opener"
            # message_text = "Thank You For Claiming a request for PPE!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address:\n%s\n%s, %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date for the requested PPE: %s\n\nOther Notes From the Requester: %s\n\nDelivery Instructions: We suggest that you connect with your requester directly. Donors are expected to ship the PPE directly to the requester, however you may use an alternate method of delivery *if you come to an agreement with your requester*. \n\nThank you for contributing to the battle against Covid-19! We hope you continue donating on our platform! : )\nIf you are interested in receiving a donation as a reward, we suggest that you communicate to your requester directly. To get a reimbursement, contact Print For The Cure at printforthecure@gmail.com." % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes)
            # message = makeMessage("printforthecure@gmail.com", request.user.email, subject, message_text)
            # sendMessage(service, 'me', message)

            #Doctor Email
            try:
                donor = Donor.objects.get(user = request.user)
            except:
                print("retrieving donor failed")
            subject = "Request For PPE Claimed"
            #sendgrid verison
            # message_text1 = "Your Request for PPE has been claimed by a donor!<br /><br />Request Details: <br />Requester's Name: %s %s<br />Requester's Email: %s<br />Requester's Phone Number: %s<br />Requester's Organization: %s<br />Requester's Address:<br />%s<br />%s, %s %s<br /><br />Type of PPE Requested: %s<br />Amount of PPE Requested: %d<br />ideal \"Deliver By\" date of requested PPE: %s<br /><br />Other Notes For the Donor: %s<br /><br />Your Donor's Name: %s<br />Donor's Email: %s<br /><br />We suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.<br /><br />It is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice message, or even a small monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes, request.user.get_full_name(), request.user.email)

            #pythonMail version
            try:
                message_text1 = removeASCII("Your Request for PPE has been claimed by a donor!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nYour Donor's Name: %s\nDonor's Email: %s\n\nWe suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.\n\nIt is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice message, or even a small monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes, request.user.get_full_name(), request.user.email))
                sendMessage(message_text1, subject, requestObj.email)
                newEmail = Email(recipient=requestObj.email, subject=subject, sentDate=timezone.now().date())
                newEmail.save()
            except:
                print("Message Failed To Send")

            # #Doctor Email
            # donor = Donor.objects.get(user = request.user)
            # subject = "Request For PPE Claimed"
            # message_text1 = "Your Request for PPE has been claimed by a donor!\n\nRequest Details: \nRequester's Name: %s %s\nRequester's Email: %s\nRequester's Phone Number: %s\nRequester's Organization: %s\nRequester's Address: %s %s %s %s %s\n\nType of PPE Requested: %s\nAmount of PPE Requested: %d\nideal \"Deliver By\" date of requested PPE: %s\n\nOther Notes For the Donor: %s\n\nYour Donor's Name: %s\nDonor's Email: %s\n\nWe suggest contacting your donor directly regarding method of delivery for your request PPE. Donors typically ship directly to your given address, however alternate methods can be used if an agreement is reached with the donor.\n\nIt is truly from the generosity of donors that many doctors and essential workers can receive help during these times. We engourage you to send a very nice message, or even a small monetary donation to keep your donor's spirits high, and to help them continue to do good. We hope our platform serves you well! : )" % (requestObj.fName, requestObj.lName, requestObj.email, requestObj.phone, requestObj.organization, requestObj.address, requestObj.city, requestObj.state, requestObj.zipCode, requestObj.country, ppeType, requestObj.numPPE, str(requestObj.delivDate), requestObj.notes, request.user.get_full_name(), request.user.email)
            # message = makeMessage("printforthecure@gmail.com", requestObj.email, subject, message_text1)
            # sendMessage(service, 'me', message)

            base_url = '/thankyou1/'  # 1 /products/
            query_string =  urlencode({'requestDetails': message_text})  # 2 category=42
            url = '{}?{}'.format(base_url, query_string)  # 3 /products/?category=42
            requestObj.status = 2
            requestObj.save()

            try:
                donor = Donor.objects.get(user = request.user)
                donor.ppe += requestObj.numPPE
                donor.requests += 1
                if requestObj.typePPE == "shield":
                    print("Donor claimed shield")
                    donor.shields += requestObj.numPPE
                elif requestObj.typePPE == "strap":
                    print("Donor claimed strap")
                    donor.straps += requestObj.numPPE
                elif requestObj.typePPE == "opener":
                    print("Donor claimed opener")
                    donor.openers += requestObj.numPPE
                elif requestObj.typePPE == "handle":
                    print("Donor claimed handle")
                    donor.handles += requestObj.numPPE
                donor.save()
            except:
                print("retrieving donor failed")

            return HttpResponseRedirect(url)  # 4


        elif 'no' in request.POST.keys():
            return HttpResponseRedirect("/requestsVisual/")
    template = loader.get_template('main/confirmClaim1.html')
    context = {     #all inputs for the html go in these brackets
        'requestObj': requestObj,
    }
    return HttpResponse(template.render(context, request))

def thankYou(request):
    requestDetails = request.GET.get('requestDetail')
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/thankYou.html')
    context = {
        'requestDetails': requestDetails
    }
    return HttpResponse(template.render(context, request))

def thankYou1(request):
    requestDetails = request.GET.get('requestDetail')
    if request.method == 'POST':
        if 'returnHome' in request.POST.keys():
            return HttpResponseRedirect("/")

    template = loader.get_template('main/thankYou.html')
    context = {
        'requestDetails': requestDetails
    }
    return HttpResponse(template.render(context, request))

def leaderboards(request):
    allUsers = User.objects.all()
    usernamesSorted = []
    namesSorted = []
    ppeSorted = []
    shieldsSorted = []
    strapsSorted = []
    openersSorted = []
    handlesSorted = []
    requestsSorted = []
    citiesSorted = []
    numDonors = 0
    for user1 in User.objects.all():
        #print(vars(user1))
        try:
            donor = Donor.objects.get(user = user1)
            numDonors = numDonors + 1
        except:
            print("User %s doesn't have donor" % user1.username)
        else:
        # if hasattr(user1, 'Donor'):     #hasattr() checks if the user has a linked donor obj
            donor = Donor.objects.get(user = user1)
            ppeSorted.append(donor.ppe)
            namesSorted.append(user1.first_name + " " + user1.last_name)
            shieldsSorted.append(donor.shields)
            strapsSorted.append(donor.straps)
            openersSorted.append(donor.openers)
            handlesSorted.append(donor.handles)
            requestsSorted.append(donor.requests)
            citiesSorted.append(donor.city)
            if "printforthecure" in user1.username:
                usernamesSorted.append("Organized Initiatives")
            else:
                usernamesSorted.append(user1.username)

    #Insertion Sorting
    for i in range(1, len(ppeSorted)):
        j = i
        while j>=1 and ppeSorted[j] > ppeSorted[j-1]:
            ppeSorted[j], ppeSorted[j-1] = ppeSorted[j-1], ppeSorted[j]
            usernamesSorted[j], usernamesSorted[j-1] = usernamesSorted[j-1], usernamesSorted[j]
            namesSorted[j], namesSorted[j-1] = namesSorted[j-1], namesSorted[j]
            shieldsSorted[j], shieldsSorted[j-1] = shieldsSorted[j-1], shieldsSorted[j]
            strapsSorted[j], strapsSorted[j-1] = strapsSorted[j-1], strapsSorted[j]
            openersSorted[j], openersSorted[j-1] = openersSorted[j-1], openersSorted[j]
            handlesSorted[j], handlesSorted[j-1] = handlesSorted[j-1], handlesSorted[j]
            requestsSorted[j], requestsSorted[j-1] = requestsSorted[j-1], requestsSorted[j]
            citiesSorted[j], citiesSorted[j-1] = citiesSorted[j-1], citiesSorted[j]
            j -= 1

        print(ppeSorted)

    usernamesAndCities = dict(zip(usernamesSorted, citiesSorted))
    print(usernamesAndCities)

    if request.method == 'POST':
        if 'login' in request.POST.keys():
            return HttpResponseRedirect("/login/")
        if 'logout' in request.POST.keys():
            print(request.user.is_authenticated)
            logout(request)
            return HttpResponseRedirect("/login/")

    template = loader.get_template('main/leaderboards.html')
    context = {
        'authenticated': request.user.is_authenticated,
        'usernamesSorted': usernamesSorted,
        'namesSorted': namesSorted,
        'ppeSorted': ppeSorted,
        'shieldsSorted': shieldsSorted,
        'strapsSorted': strapsSorted,
        'openersSorted': openersSorted,
        'handlesSorted': handlesSorted,
        'requestsSorted': requestsSorted,
        'citiesSorted': citiesSorted,
        'usernamesAndCities': usernamesAndCities,
        'numDonors': numDonors
    }
    return HttpResponse(template.render(context, request))

def terms(request):
    template = loader.get_template('main/terms.html')
    return HttpResponse(template.render({}, request))

def pp(request):
    template = loader.get_template('main/pp.html')
    return HttpResponse(template.render({}, request))

def test(request):
    template = loader.get_template('main/fileName.html')
    context = {}
    return HttpResponse(template.render(context, request))

def status(request):
    return JsonResponse({'online':'true'})

def getClaimRate(request):
    #determine rate from # PPE
    # totalRequestedPPE = 0.0
    # claimedRequestedPPE = 0.0
    # for requestModel in RequestModel.objects.all():
    #     if requestModel.status == 1:
    #         totalRequestedPPE += requestModel.numPPE
    #     if requestModel.status == 2:
    #         claimedRequestedPPE += requestModel.numPPE
    #         totalRequestedPPE += requestModel.numPPE
    #
    # claimRate = claimedRequestedPPE/totalRequestedPPE

    #determine rate from # requests
    totalRequests = 0
    claimedRequests = 0
    for requestModel in RequestModel.objects.all():
        if requestModel.status == 1:
            totalRequests += 1
        elif requestModel.status == 2:
            claimedRequests += 1
            totalRequests += 1
        elif requestModel.status == 3:
            claimedRequests += 1
            totalRequests += 1

    claimRate = (claimedRequests + 0.0)/(totalRequests + 0.0)

    print("claimed requests: " + str(claimedRequests))
    print("total requests claimed and expired: " + str(totalRequests))
    print("Claimrate (not including pending requests): " + str(claimRate))
    claimRate = int(claimRate * 100)
    claimRateStr = str(claimRate)
    return claimRateStr

def getCurrentRequestedShields(request):
    result = 0
    for requestModel in RequestModel.objects.all():
        if requestModel.status == 0:
            if requestModel.typePPE == "shield":
                result += requestModel.numPPE

    return result

def removeASCII(s):
    # print("string: " + str(all(ord(c) < 128 for c in s)))
    for i in range(len(s)):
        if ord(s[i]) > 128:
            s = s[:i] + ' ' + s[i + 1:]
    # print(s)
    return s

def calcDistance(lat1, lat2, lon1, lon2):
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles
    r = 6371
    # calculate the result
    return(c * r)

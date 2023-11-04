import datetime
import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import *
# from rest_framework.views import APIView
from rest_framework import status
from api.models import Attendance
from api.models import Booking,Venue,User as user,Attendee
from api.serializers import AttendanceResponseSerializer
# from rest_framework.permissions import IsAuthenticated,AllowAny
from api.jwt_util import decode_user
# from datetime import datetime, date, timedelta
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
# from django.contrib.auth.models import User
from django.http import JsonResponse
# from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.

class DashboardController():
    @api_view(['GET'])
    # @permission_classes([IsAuthenticated])
    def getSignedIn(request):
        
        # auth_header=request.META['HTTP_AUTHORIZATION']
        # # pra mawa ang word na Bearer
        # token=auth_header[7:len(auth_header)+1]
        # print(token)
        # user=decode_user(token)
        # owner=user['user_id']
        
        # if(user['role']!='admin'):
        #     return Response({'message':'admin only view'},status=status.HTTP_401_UNAUTHORIZED)
        res=Attendance.objects.filter(isSignedIn=True,)
        serializer=AttendanceResponseSerializer(res,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    @api_view(['GET'])
    def getOngoing(request):
        conferenceRoomA=0
        conferenceRoomB=0
        coworkingSpace=0
        timeNow=datetime.datetime.now().time()
        res=Attendance.objects.filter(isSignedIn=True)
        print(timeNow)
        for attendanceObj in res:
            if(attendanceObj.booking.endTime>timeNow and timeNow>=attendanceObj.booking.startTime):
                if(attendanceObj.venueName=='Conference Room A'):
                    conferenceRoomA+=1
                elif(attendanceObj.venueName=='Conference Room B'):
                    conferenceRoomB+=1
                elif(attendanceObj.venueName=='Coworking Space'):
                    coworkingSpace+=1
        return Response({"conferenceRoomA":conferenceRoomA,"conferenceRoomB":conferenceRoomB,"coworkingSpace":coworkingSpace}, status=status.HTTP_200_OK)
    @api_view(['GET'])
    def getWaiting(request):
        conferenceRoomA=0
        conferenceRoomB=0
        coworkingSpace=0
        timeNow=datetime.datetime.now().time()
        res=Attendance.objects.filter(isSignedIn=True)
        for attendanceObj in res:
            if(attendanceObj.booking.endTime>timeNow and timeNow<attendanceObj.booking.startTime):
                if(attendanceObj.venueName=='Conference Room A'):
                    conferenceRoomA+=1
                elif(attendanceObj.venueName=='Conference Room B'):
                    conferenceRoomB+=1
                elif(attendanceObj.venueName=='Coworking Space'):
                    coworkingSpace+=1
        return Response({"conferenceRoomA":conferenceRoomA,"conferenceRoomB":conferenceRoomB,"coworkingSpace":coworkingSpace}, status=status.HTTP_200_OK)
    
    @api_view(['GET'])
    def getOverstaying(request):
        conferenceRoomA=0
        conferenceRoomB=0
        coworkingSpace=0
        timeNow=datetime.datetime.now()
        timePlusFive=timeNow+datetime.timedelta(minutes=5)
        res=Attendance.objects.filter(isSignedIn=True)
        for attendanceObj in res:
            if((attendanceObj.booking.endTime<timePlusFive.time() and attendanceObj.date==datetime.datetime.now().date() )or attendanceObj.date<datetime.datetime.now().date()):
                if(attendanceObj.venueName=='Conference Room A'):
                    conferenceRoomA+=1
                elif(attendanceObj.venueName=='Conference Room B'):
                    conferenceRoomB+=1
                elif(attendanceObj.venueName=='Coworking Space'):
                    coworkingSpace+=1
        return Response({"conferenceRoomA":conferenceRoomA,"conferenceRoomB":conferenceRoomB,"coworkingSpace":coworkingSpace}, status=status.HTTP_200_OK)
    @api_view(['GET'])
    def getExpected(request):
        conferenceRoomA=0
        conferenceRoomB=0
        coworkingSpace=0
        timeNow=datetime.datetime.now().time()
        res=Booking.objects.filter(date=datetime.datetime.now().date(),startTime__gt=timeNow)
        print("res:")
        print(res.count())
        for booking in res:
            
            attendeeCount=Attendee.objects.filter(booking=booking).count()
            print(attendeeCount)
            if(booking.venue.id==1):
                coworkingSpace= coworkingSpace+attendeeCount
            elif(booking.venue.id==2):
                conferenceRoomA= conferenceRoomA+attendeeCount
            elif(booking.venue.id==3):
                conferenceRoomB=conferenceRoomB+attendeeCount
        return Response({"conferenceRoomA":conferenceRoomA,"conferenceRoomB":conferenceRoomB,"coworkingSpace":coworkingSpace}, status=status.HTTP_200_OK)
    @api_view(['GET'])
    def signOutAll(request):
        res=Attendance.objects.filter(isSignedIn=True)
        for attendance in res:
            if attendance.booking.endTime<datetime.datetime.now().time():
                attendance.isOverstaying=True
            attendance.isSignedIn=False
            attendance.signOutTime=datetime.datetime.now().time()
            attendance.save()
            
            return JsonResponse({"message":"All users logged out"},status=status.HTTP_200_OK)
    # @api_view(['GET'])
    # def getCurrentBookings(request):
    #     # auth_header=request.META['HTTP_AUTHORIZATION']
    #     # # pra mawa ang word na Bearer
    #     # token=auth_header[7:len(auth_header)+1]
    #     # print(token)
    #     # user=decode_user(token)
    #     # owner=user['user_id']
    #     week_start = date.today()
    #     week_start -= timedelta(days=week_start.weekday())
    #     week_end = week_start + timedelta(days=14)        
    #     obj = Booking.objects.filter(date__gte=week_start,date__lt=week_end,status="Booked",)
    #     serializer = BookingSerializer(obj,many=True)
    #     return Response(serializer.data,status=status.HTTP_200_OK)
    
    # @api_view(['POST'])
    # def saveBooking(request):       
    #     if request.method=='POST':
    #         serializer= BookingRequestSerializer(data=request.data)   
                
    #         if serializer.is_valid():
    #             date=serializer.validated_data['date']
    #             # calculate hours_difference
    #             startTime=serializer.validated_data['startTime']
    #             endTime=serializer.validated_data['endTime']
    #             duration=datetime.combine(date,endTime)-datetime.combine(date,startTime)
    #             hours_difference = (duration).total_seconds()/3600.0
    #             serializer._validated_data['duration']=hours_difference
    #             # set status to booked
    #             serializer._validated_data['status']='Booked'
    #             serializer.save()
    #             response_data={
    #                 'message':'Succesfully booked'
    #             }
    #             return Response(serializer.data,status=status.HTTP_201_CREATED)
    #         return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)
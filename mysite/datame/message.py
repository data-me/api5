import pytz, datetime
from .models import *
from django.http import JsonResponse
from django.http import JsonResponse
from rest_framework.views import APIView
# Email
from django.core.mail import send_mail
from django.conf import settings
#======

class Notification_view(APIView):
    def post(self, request, format=None):
        try:
            data = request.POST
            # Ensure user who is sending notification email is admin (staff)
            User.objects.filter(is_staff=True).get(id=request.user.id)

            subject = data['subject']
            message = data['body']
            email_from = settings.EMAIL_HOST_USER # Email sender
            print('Email from:', settings.EMAIL_HOST_PASSWORD)
            # Collecting all emails
            all_users = User.objects.all().exclude(id=request.user.id)

            recipient_list = []
            for user in all_users:
                recipient_list.append(user.email)
            #====================
            print(recipient_list)
            # Sending individual email for each user
            for recipient in recipient_list:
                try:
                    if recipient != "":
                        receiver = []
                        receiver.append(recipient)
                        print('================================')
                        send_mail( subject, message, email_from, receiver, fail_silently=False)
                        print('A message was sent')
                        print('================================')
                except Exception as e:
                    print(e)
                    print('Message was not sent to:', recipient)
            return JsonResponse({"message":"Successfully created new notifications for users"})
        except Exception as e:
            return JsonResponse({"message":"Oops, something went wrong"})


#para dashboard
class Messages_view(APIView):
    def get(self, request, format=None):
        user_logged = User.objects.all().get(pk = request.user.id)
        if (user_logged.is_superuser or user_logged.is_staff):
            try:    
                messages = Message.objects.all().values()
                return JsonResponse(list(messages), safe=False)
            except:
                print("there are no messages")
        return JsonResponse({"message":"Oops, something went wrong"})

class Message_view(APIView):
    def post(self, request, format=None):
        try:
            data = request.POST
            title = data['title']
            body = data['body']
            moment = datetime.datetime.utcnow()
            #receiverId = User.objects.all().get(user = data['receiverId'])
            username = data['username']
            isAlert = False
            receiver = User.objects.all().get(username = username)
            senderId = request.user
            print('Messager senderId =>', senderId)

            new_message = Message.objects.create(title=title, body=body, moment=moment, receiver=receiver, sender=senderId, isAlert= isAlert)

            return JsonResponse({"message":"Successfully created new message"})
        except Exception as e:
            print(e)
            return JsonResponse({"message":"El usuario no existe / User doesn't exists"})
    def get(self, request, format=None):
        try:
            data = request.GET
            user = request.user
            messages = []
            try:
                messages = Message.objects.all().filter(receiver = user).order_by('-moment').values()
                Message.objects.all().filter(receiver = user).update(viewed = True)
                
            except:
                print("You have 0 messages")

            return JsonResponse(list(messages), safe=False)
        except:
            return JsonResponse({"message":"Oops, something went wrong"})

class Unvieweds_view(APIView):
     def get(self, request, format=None):
         try:
            data = request.GET
            user = request.user
            messages = Message.objects.all().filter(receiver = user,viewed = False).count()
            return JsonResponse({"message": messages})
         except:
            return JsonResponse({"message":"Oops, something went wrong"})
             
        
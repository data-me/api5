from .models import *
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, NOT
import traceback
import datetime
from django.forms.models import model_to_dict
from django.contrib.auth import logout

from django.utils import timezone


#para dashboard de admin
class User_view(APIView):
    def get(self, request, format=None):
        try:
            data = request.GET
            user = request.user
            users = []
            try:
                users = User.objects.all().values('username')
                print(users)
            except:
                print("There are no users")

            return JsonResponse(list(users), safe=False)
        except:
            return JsonResponse({"message":"Oops, something went wrong"})

#para dashboard de admin
class Companies_view(APIView):
    def get(self, request, format=None):
        try:
            data = request.GET
            user = request.user
            companies = []
            if (user.is_superuser or user.is_staff):
                try:
                    companies = Company.objects.all().values('name')
                except:
                    print("There are no companies")

                return JsonResponse(list(companies), safe=False)
        except:
            return JsonResponse({"message":"Oops, something went wrong"})

class Company_view(APIView):
    def get(self, request, format=None):
        if request.method == "GET":
            data = request.GET
            logged_user = User.objects.all().get(pk = request.user.id)
            print('logged_user: ' + str(logged_user))
            try:
                    companyId = data['companyId']
                    thiscompany = Company.objects.all().filter(pk = companyId).values('name', 'description', 'nif', 'logo', 'user__username')

            except Exception as e:
                    companyRecuperada = Company.objects.all().get(user = logged_user)
                    thiscompany = Company.objects.all().filter(user = logged_user).values()


            return JsonResponse(list(thiscompany), safe=False)

class DataScientist_view(APIView):
    def get(self, request, format=None):
        if request.method == "GET":
            data = request.GET
            logged_user = User.objects.all().get(pk = request.user.id)
            print('logged_user: ' + str(logged_user))
            try:
                    dataScientistId = data['dataScientistId']
                    thisds = DataScientist.objects.all().filter(pk = dataScientistId).values('name','surname','photo','address','phone','user__email', 'user__username')

            except Exception as e:
                    thisds = DataScientist.objects.all().filter(user = user_logged).values('name','surname','photo','address','phone','user__email', 'user__username')


            return JsonResponse(list(thisds), safe=False)

class Register_view(APIView):
    permission_classes = (~IsAuthenticated,)
    def post(self, request, format=None):
        try:
            data = request.POST
            type = data['type']
            username = data['username']
            password = data['password']
            name = data['name']
            confirm_terms = data['confirmTerms']

            if (User.objects.filter(username = username).exists()):
                    res = JsonResponse({"message":"Sorry, username already exists"})
            elif(confirm_terms=='not_accepted'):
                    res = JsonResponse({"message":"Need confirmation of terms and conditions"})
            else:
                if (type == 'DS'):
                    group = Group.objects.get(name = 'DataScientist')
                    surname = data['surname']
                    photo = data['photo']
                    address = data['address']
                    phone = data['phone']
                    email = data['email']
                    newUser = User.objects.create(username = username, password = password, email = email)
                    newUser.set_password(password)
                    newUser.groups.add(group)
                    newUser.save()
                    newDs = DataScientist.objects.create(user = newUser, name = name, surname = surname, photo = photo, address = address, phone = phone)
                    CV.objects.create(owner = newDs)
                    res = JsonResponse({"message":"Successfully created new Data Scientist. Welcome!"})

                    print('Creating a NEW DS alert message for adming user')

                    # Alert message
                    title = '[ALERT MESSAGE] New data scientist was registered'
                    body = 'Data scientist with DsID: '+str(newDs.id)+' was registered'
                    moment = datetime.datetime.utcnow()
                    username = 'admin'
                    isAlert = True
                    receiver = User.objects.all().get(username = username)
                    senderId = newUser

                    new_message = Message.objects.create(title=title, body=body, moment=moment, receiver=receiver, sender=senderId, isAlert= isAlert)

                     # Welcome message
                    title = 'Welcome to DataMe! | ¡Bienvenido a DataMe!'
                    body = 'Welcome '+str(newDs.name)+"! it's a pleasure have you here. | ¡Bienvenido " +str(newDs.name)+"! Es un placer tenerte con nosotros"
                    moment = datetime.datetime.utcnow()
                    username = newUser.username
                    isAlert = False
                    receiver = User.objects.all().get(username = username)
                    senderId = User.objects.all().get(username = 'admin')

                    new_message = Message.objects.create(title=title, body=body, moment=moment, receiver=receiver, sender=senderId, isAlert= isAlert)


                    print('Sucessfully created new alert message')

                if (type == 'C'):
                    group = Group.objects.get(name = 'Company')
                    description = data['description']
                    nif = data['nif']
                    logo = data['logo']
                    email = data['email']
                    newUser = User.objects.create(username = username, password = password, email = email)
                    newUser.set_password(password)
                    newUser.groups.add(group)
                    newUser.save()
                    newC = Company.objects.create(user = newUser, name = name, description = description, nif = nif, logo = logo)
                    res = JsonResponse({"message":"Successfully created Company. Welcome!"})

                    print('Creating a NEW COMPANY alert message for adming user')

                    # Alert message
                    title = '[ALERT MESSAGE] New company was registered'
                    body = 'Company with CompanyID: '+str(newC.id)+' was registered'
                    moment = datetime.datetime.utcnow()
                    username = 'admin'
                    isAlert = True
                    receiver = User.objects.all().get(username = username)
                    senderId = newUser

                    new_message = Message.objects.create(title=title, body=body, moment=moment, receiver=receiver, sender=senderId, isAlert= isAlert)

                    title = 'Welcome to DataMe! | ¡Bienvenido a DataMe!'
                    body = 'Welcome '+str(newC.name)+"! it's a pleasure have you here. | ¡Bienvenido " +str(newC.name)+"! Es un placer tenerte con nosotros."
                    moment = datetime.datetime.utcnow()
                    username = newUser.username
                    isAlert = False
                    receiver = User.objects.all().get(username = username)
                    senderId = User.objects.all().get(username = 'admin')

                    new_message = Message.objects.create(title=title, body=body, moment=moment, receiver=receiver, sender=senderId, isAlert= isAlert)


                    print('Sucessfully created new alert message')
            return res
        except Exception as e:
            print(e)
            return JsonResponse({"message":"Oops, something went wrong" + str(e)})

class list_dataScientists(APIView):
    def get(self, request, format=None):
        if request.method == "GET":
            logged_user = User.objects.all().get(pk=request.user.id)
            try:
                if not logged_user.is_staff:
                    return JsonResponse({"message": "Sorry! Only an administrator can list all data scientists."})
                dataScientist_list = DataScientist.objects.all().values()

            except:
                traceback.print_exc()
                return JsonResponse({"message": "Sorry! Something went wrong..."})
            return JsonResponse(list(dataScientist_list), safe=False)

class list_companies(APIView):
    def get(self, request, format=None):
        if request.method == "GET":
            logged_user = User.objects.all().get(pk=request.user.id)
            try:
                if not logged_user.is_staff:
                    return JsonResponse({"message": "Sorry! Only an administrator can list all companies."})
                companies_list = Company.objects.all().values()

            except:
                traceback.print_exc()
                return JsonResponse({"message": "Sorry! Something went wrong..."})
            return JsonResponse(list(companies_list), safe=False)

class list_staff(APIView):
    def get(self, request, format=None):
        if request.method == "GET":
            logged_user = User.objects.all().get(pk=request.user.id)
            try:
                if not logged_user.is_staff:
                    return JsonResponse({"message": "Sorry! Only an administrator can list all staff."})
                staf_list = User.objects.filter(is_staff=True).values()

            except:
                traceback.print_exc()
                return JsonResponse({"message": "Sorry! Something went wrong..."})
            return JsonResponse(list(staf_list), safe=False)

class delete_user(APIView):
    def post(self, request, format=None):
        try:
            logged_user = User.objects.all().get(pk=request.user.id)
            if not logged_user.is_staff:
                return JsonResponse({"message": "Sorry! Only an administrator can delete users."})
            user_id = request.POST['user_id']
            userToDelete = User.objects.get(pk=user_id)
            userToDelete.delete()
            return JsonResponse({"message": "Successfully deleted user"})
        except:
            traceback.print_exc()
            return JsonResponse({"message": "Sorry! Something went wrong deleting a user..."})

class delete_me(APIView):
    def post(self, request, format=None):
        try:
            logged_user = User.objects.all().get(pk=request.user.id)
            logout(request)
            logged_user.delete()
            return JsonResponse({"message": "Your user has been successfully deleted.",
                                 "success": True})
        except:
            traceback.print_exc()
            return JsonResponse({"message": "Sorry! Something went wrong deleting your user...",
                                "success": False})
class dashboard(APIView):
    def get(self, request, format=None):
        try:
            dataset1 = []
            apliesPerDate = Apply.objects.all().values('')
        except:
            traceback.print_exc()
            return JsonResponse({"message": "Sorry! Something went wrong"})

class change_info(APIView):
    def post(self, request, format=None):
        try:
            user_logged = User.objects.all().get(pk = request.user.id)
            data = request.POST
            if (user_logged.groups.filter(name='DataScientist').exists()):
                name = data['name']
                surname = data['surname']
                email = data ['email']
                photo = data ['photo']
                address = data ['address']
                phone = data ['phone']
                DataScientist.objects.all().filter(user = user_logged).update(name = name, surname = surname, photo = photo, address = address, phone = phone)
                User.objects.all().filter(pk = user_logged.id).update(email = email)
                return JsonResponse({"message": "User updated"})
            elif (user_logged.groups.filter(name='Company').exists()):
                name = data['name']
                description = data['description']
                logo = data['logo']

                #if(request.POST.get('email') and (request.POST.get('email') != user_logged.email)):
                #    email = data['email']
                #    User.objects.all().filter(pk = user_logged.pk, id = user_logged.id ).update(email = email)

                Company.objects.all().filter(user = user_logged).update(name = name, description = description, logo = logo)
                return JsonResponse({"message": "Updated!"})
            else:
                return JsonResponse({"message":"Who are you?"})
        except Exception as e:
            return JsonResponse({"message": "Sorryyyy! Something went wrong..." + str(e)})

class get_user_logged(APIView):
    def get(self, request, format=None):
        try:
            user_logged = User.objects.all().get(pk = request.user.id)
            if (user_logged.groups.filter(name='DataScientist').exists()):
                res = DataScientist.objects.all().filter(user = user_logged).values('name','surname','photo','address','phone','user__email')
            elif(user_logged.groups.filter(name='Company').exists()):
                res = Company.objects.all().filter(user = user_logged).values('name','description','nif','logo','user__email')

            return JsonResponse(list(res), safe = False)
        except Exception as e:
            return JsonResponse({"message": "Sorry! Something went wrong..." + str(e)})

class whoami(APIView):
    def get(self, request, format=None):
            try:
                ds = request.user.datascientist
                user_plan = UserPlan.objects.order_by('id').filter(dataScientist=ds).last()

                ads="true"
                if user_plan:
                    hoy = timezone.now()
                    if user_plan.expirationDate >= hoy:
                        ads="false"
                return JsonResponse({'user_type': 'ds','ads':ads})
            except:
                try:
                    request.user.company
                    return JsonResponse({'user_type': 'com','ads':'false'})
                except:
                    try:
                        user_logged = request.user
                        if(user_logged.is_superuser or user_logged.is_staff):
                            return JsonResponse({'user_type': 'admin','ads':'false'})
                    except:
                        return JsonResponse({'user_type': 'None','ads':'true'})

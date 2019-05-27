import pytz, datetime
from .models import *
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.db.models import Count

from pagos.models import OfferPaypalBill

class Offer_view(APIView):
    def get(self, request, format=None):
        try:
            data = request.GET
            if data.get('search_title') != None and data.get('search_price') != None and data.get('search_date') != None:
                try:
                    date_now = datetime.datetime.utcnow()
                    final_result = []
                    thisDS = DataScientist.objects.all().get(user = request.user)
                    applies = Apply.objects.all().filter(dataScientist = thisDS)
                    user_applied_offers = [a.offer.id for a in applies]
                    if data.get('search_price') != "undefined" and data.get('search_price') != "":
                        if data.get('search_title') != "undefined":
                            if data.get('search_date') != "undefined" and data.get('search_date') != "":
                                # Time management
                                date = data.get('search_date').split(" ")[0].split("-")
                    
                                limit_time =  datetime.datetime(int(date[0]), int(date[1]), int(date[2]), 10, 10, 0, 0, pytz.UTC)
                                ofertas = Offer.objects.filter(Q(title__contains = data['search_title']) | Q(description__contains = data['search_title']),Q(price_offered__lte = float(data['search_price']) ), limit_time__gte = date_now, finished=False).exclude(id__in=user_applied_offers).annotate(num_applicantions=Count('apply')).values()
                                result = list(ofertas)
                                for idx, o in enumerate(result):
                                    if(o['limit_time'] < limit_time):
                                        final_result.append(o)
                            else:
                                final_result = Offer.objects.filter(Q(title__contains = data['search_title']) | Q(description__contains = data['search_title']),Q(price_offered__lte = float(data['search_price']) ), limit_time__gte = date_now, finished=False).exclude(id__in=user_applied_offers).values()
                        else:
                            final_result = Offer.objects.filter(Q(price_offered__lte = float(data['search_price'])), limit_time__gte = date_now, finished=False).exclude(id__in=user_applied_offers).values()
                        return JsonResponse(list(final_result), safe=False)
                    else:                     
                        if data.get('search_date') != "undefined" and data.get('search_date') != "":
                            # Time management
                            date = data.get('search_date').split(" ")[0].split("-")
                    
                            limit_time =  datetime.datetime(int(date[0]), int(date[1]), int(date[2]), 10, 10, 0, 0, pytz.UTC)
                            if data.get('search_title') != "undefined" and data.get('search_title') != "":
                                ofertas = Offer.objects.filter(Q(title__contains = data['search_title']) | Q(description__contains = data['search_title']), limit_time__gte = date_now, finished=False).exclude(id__in=user_applied_offers).annotate(num_applicantions=Count('apply')).values()
                            else:
                                ofertas = Offer.objects.filter(limit_time__gte = date_now, finished=False).exclude(id__in=user_applied_offers).values()
                            result = list(ofertas)
                            for idx, o in enumerate(result):
                                if(o['limit_time'] < limit_time):
                                    final_result.append(o)
                        else:
                            if data.get('search_title') != "undefined" and data.get('search_title') != "":
                                final_result = Offer.objects.filter(Q(title__contains = data['search_title']) | Q(description__contains = data['search_title']), limit_time__gte = date_now, finished=False).exclude(id__in=user_applied_offers).annotate(num_applicantions=Count('apply')).values()
                        return JsonResponse(list(final_result), safe=False)
                except:
                    return JsonResponse({"message":"Sorry! Something went wrong..."})

            elif data.get('offerId') != None:
                ofertas = Offer.objects.filter(id = data['offerId']).values()
                return JsonResponse(list(ofertas), safe=False)
            else:
                ofertas = []
                try:
                    thisCompany = Company.objects.all().get(user = request.user)
                    # All offers instead only those who don't have an applicant
                    bills = OfferPaypalBill.objects.all().filter(pagado=False)
                    bills_ids = [a.offer.id for a in bills]
                    ofertas = Offer.objects.all().filter(company = thisCompany).exclude(id__in=bills_ids).annotate(num_applicantions=Count('apply')).values()
                except:
                    date = datetime.datetime.utcnow()
                    thisDS = DataScientist.objects.all().get(user = request.user)
                    applies = Apply.objects.all().filter(dataScientist = thisDS)
                    user_applied_offers = [a.offer.id for a in applies]
                    # All offers whos time has not come yet
                    bills = OfferPaypalBill.objects.all().filter(pagado=False)
                    bills_ids = [a.offer.id for a in bills]
                    ofertas = Offer.objects.all().filter(limit_time__gte = date, finished=False).exclude(id__in=user_applied_offers).exclude(id__in=bills_ids).annotate(num_applicantions=Count('apply')).values()
                return JsonResponse(list(ofertas), safe=False)
        except:
            return JsonResponse({"message":"Sorry! Something went wrong..."})
    def post(self, request, format=None):
        try:
            data = request.POST
            title = data['title']
            description = data['description']
            price_offered = data['price_offered']
            limit_time = data['limit_time']
            contract = data['contract']
            files = data['files']
            thisCompany = Company.objects.all().get(user = request.user)
            # Time management
            date = limit_time.split(" ")[0].split("-")
            hour = limit_time.split(" ")[1].split(":")

            limit_time =  datetime.datetime(int(date[0]), int(date[1]), int(date[2]), int(hour[0]), int(hour[1]), 0, 0, pytz.UTC)


            new_offer = Offer.objects.create(title=title, description=description, price_offered=float(price_offered), limit_time=limit_time, contract=contract, files=files, company = thisCompany)


            print('La data que devuelve es: ' + str(data))
            print('Sucessfully created new offer')
            print('Creating a NEW OFFER alert message for adming user')
            
            # Alert message
            title = '[ALERT MESSAGE] New offer was created'
            body = 'Company with CompanyID: '+str(thisCompany.id)+' created new offer with OfferID: '+str(new_offer.id) +' and using title: '+str(new_offer.title)
            moment = datetime.datetime.utcnow()
            username = 'admin'
            isAlert = True
            receiver = User.objects.all().get(username = username)
            senderId = request.user

            new_message = Message.objects.create(title=title, body=body, moment=moment, receiver=receiver, sender=senderId, isAlert= isAlert)

            print('Sucessfully created new alert message')
            return JsonResponse({"message":"Successfully created new offer","offer_id":new_offer.id})
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong..."})

    def delete (self, request, offer_id, format=None):
        try:

            thisCompany = Company.objects.all().get(user = request.user)
            ofertasCompany = Offer.objects.all().filter(company = thisCompany).values()
            
            lookup_url_kwarg = "offer_id"
            offer = Offer.objects.get(id = self.kwargs.get(lookup_url_kwarg))
            if(thisCompany == offer.company):
                applies = Apply.objects.all().filter(offer = offer)
                if(applies.first() == None):
                    offer.delete()   
                    return JsonResponse({"message":"Successfully deleted offer"})
                else:
                    # ERROR HERE AT DELETEING OFFER
                    return JsonResponse({"message":"This offer has at least one application / Esta oferta tiene al menos una solicitud"})
            else:
                return JsonResponse({"message":"You do not own this offer"})
        except Exception as e:
            print(e)
            return JsonResponse({"message":"Sorry! Something went wrong..."+ str(e)})
    
class change_Offer(APIView):
    def post(self, request, offer_id, format=None):
        try:
            data = request.POST
            title = data['title']
            description = data['description']
            thisCompany = Company.objects.all().get(user = request.user)
            lookup_url_kwarg = "offer_id"
            offer = Offer.objects.get(id = self.kwargs.get(lookup_url_kwarg))
            if(thisCompany == offer.company):
                applies = Apply.objects.all().filter(offer = offer)
                print(applies)
                if(applies.first() == None):
                    Offer.objects.all().filter(pk = offer_id).update(title=title, description=description)
                    return JsonResponse({"message": "Offer updated / Oferta modificada"})
                else:
                    return JsonResponse({"message":"This offer has at least one application, you cannot edit it / Esta oferta tiene al menos una solicitud, no puede editarla"})                   
            else:
                return JsonResponse({"message":"You do not own this offer"})
        except Exception as e:
            return JsonResponse({"message": "Sorry! Something went wrong..." + str(e)})

class Offer_admin_view(APIView):
    def get(self, request, format=None):
        try:
            logged_user = request.user

            if logged_user.is_superuser or logged_user.is_staff:

                response = []

                offers = Offer.objects.all().values()

                for offer in offers:
                    company = Company.objects.get(id = offer.get('company_id'))
                    response.append({
                        'offer_id' : str(offer.get('id')),
                        'title' : str(offer.get('title')),
                        'description' : str(offer.get('description')),
                        'price_offered' : str(offer.get('price_offered')),
                        'creation_date' : str(offer.get('creation_date')),
                        'limit_time' : str(offer.get('limit_time')),
                        'finished' : str(offer.get('finished')),
                        'files' : str(offer.get('files')),
                        'contract' : str(offer.get('contract')),
                        'company_id' : str(offer.get('company_id')),
                        'company_name' : company.name
                    })

                return JsonResponse(list(response), safe = False)

            else:
                return JsonResponse({"message":"Sorry! You don't have access to this resource..."})

        except:
            return JsonResponse({"message":"Sorry! Something went wrong..."})
    
    def delete(self, request, offer_id, format=None):
        try:
            logged_user = request.user

            if logged_user.is_superuser or logged_user.is_staff:
                lookup_url_kwarg = "offer_id"

                offer = Offer.objects.get(id = self.kwargs.get(lookup_url_kwarg))

                message = Message.objects.create(receiver = offer.company.user, sender = logged_user, title = 'Your offer: ' + str(offer) + ', was deleted', body = 'Our administrators detected that your offer was in some way inappropriate')

                offer.delete()

            return JsonResponse({"message":"Successfuly deleted offer"})

        except Exception as e:
            return JsonResponse({"message" : str(e)})

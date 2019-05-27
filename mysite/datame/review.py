import pytz, datetime
from .models import *
from django.http import JsonResponse
from rest_framework.views import APIView
from django.db.models import Q
from operator import itemgetter

class Review_view(APIView):
    def post(self, request, format=None):
        try:
            data = request.POST
            reviewedId = data['reviewedId']
            score = data['score']
            comments = data['comments']
            reviewer = User.objects.all().get(pk = request.user.id)
            reviewed = User.objects.all().get(pk = reviewedId)
            if(Review.objects.all().filter(reviewer = reviewer,reviewed = reviewed).exists()):
               return JsonResponse({"message":"User has already reviewed | El usuario ya ha hecho una critica"})
            Review.objects.create(reviewed = reviewed, reviewer = reviewer, score = score, comments = comments)
            
            return JsonResponse({"message":"Successfully created new review"})
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})
class Review_Users_view(APIView):
    def get(self, request, format=None):
        try:
            reviewer = User.objects.all().get(pk = request.user.id)
            users = Review.objects.all().filter(reviewer = reviewer).values("reviewed_id")
            return JsonResponse(list(users), safe=False)
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})
class Reviews_view(APIView):
    def get(self, request, format=None):
        try:
            reviews = Review.objects.all().values()
            return JsonResponse(list(reviews), safe=False)
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})

class Reviews_Company_view(APIView):
    def get(self, request, format=None):
        try:
            result = []

            reviews = Review.objects.all().values()
            
            for review in reviews:
                reviewerid = review['reviewer_id']
                reviewer_O = User.objects.get(pk = reviewerid) 
                reviewedid = review['reviewed_id'] 
                reviewed_O = User.objects.get(pk = reviewedid) 
                print(reviewerid)
                print(reviewer_O)
                print(reviewedid)
                print(reviewed_O)
                
                if(reviewer_O.groups.filter(name='Company').exists()):
                    print(1)
                    reviewer_name = Company.objects.values('name').all().get(user = reviewer_O)
                    print(reviewer_name)
                    reviewed_name = DataScientist.objects.values('name').all().get(user = reviewed_O)
                    print(reviewed_name)
                    result.append({
                            'id' : str(review['id']),
                            'reviewer_name' : str(reviewer_name['name']),
                            'reviewed_name' : str(reviewed_name['name']),
                            'score' : str(review['score']),
                            'comments' : str(review['comments'])
                        });
                    
                    

            return JsonResponse(list(result), safe=False)        
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})

class Reviews_DataScientist_view(APIView):
    def get(self, request, format=None):
        try:

            result = []

           
            reviews = Review.objects.all().values()
            for review in reviews:
                reviewerid = review['reviewer_id']
                reviewer_O = User.objects.get(pk = reviewerid) 
                reviewedid = review['reviewed_id']
                reviewed_O = User.objects.get(pk = reviewedid) 
                if(reviewer_O.groups.filter(name='DataScientist').exists()):
                    reviewer_name = DataScientist.objects.values('name').all().get(user = reviewer_O)
                    print(reviewer_name)
                    reviewed_name = Company.objects.values('name').all().get(user = reviewed_O)
                    print(reviewed_name)
                    result.append({
                            'id' : str(review['id']),
                            'reviewer_name' : str(reviewer_name['name']),
                            'reviewed_name' : str(reviewed_name['name']),
                            'score' : str(review['score']),
                            'comments' : str(review['comments'])
                        });
  
           
            return JsonResponse(list(result), safe=False)        
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})

class Ranking_DataScientist_view(APIView):
    def get(self, request, format=None):
        try:
            valores =[]

            global average
            
            def myFunc(e):
                return e['average']

            reviews = Review.objects.all().values().distinct('reviewed_id')

            
            
            print(reviews) 
            for review in reviews:
                reviewerid = review['reviewer_id']
                reviewer_O = User.objects.get(pk = reviewerid) 
                reviewedid = review['reviewed_id']
                reviewed_O = User.objects.get(pk = reviewedid) 
                if(reviewed_O.groups.filter(name='DataScientist').exists()): 
                    #obtengo la company a la que va dirigida UNA review
                    reviewed_name = DataScientist.objects.values('name').all().get(user = reviewed_O)
                    #print(reviewed_name)

                    #reviews con reviewedid de una company en concreto
                    reviewed_reviews = Review.objects.all().filter(reviewed_id = reviewedid).values().distinct()
            
                    count = 0 #numero de reviews para un datascientist concreto
                    score = 0
                    average = 0
                    scores = []
                    for rr in reviewed_reviews: 
                        count = count + 1
                        print ('count:' + str(count))
                        score = rr['score']
                        print ('score:' + str(score))
                        
                        
                        scores.append(score)
                        print('scores', scores)
                        average = sum(scores) / count
                        print('average', average)

                        comments = rr['comments']

                    valores.append({
                        'reviewed_name' : str(reviewed_name['name']),
                        'average' : float(average),
                        'comments' : str(comments)
                    });
            
            valores.sort(key = myFunc,reverse=True)
            print('valores: ', valores)

            
            return JsonResponse(list(valores), safe=False)        
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})


class Ranking_Company_view(APIView): #quien es revisada es la company
    def get(self, request, format=None):
        try:

            valores =[]

            global average

            

            def myFunc(e):
                return e['average']

            reviews = Review.objects.all().values().distinct('reviewed_id')
            
            #print(reviews)  
            for review in reviews:
                reviewerid = review['reviewer_id']
                reviewer_O = User.objects.get(pk = reviewerid) 
                reviewedid = review['reviewed_id']
                reviewed_O = User.objects.get(pk = reviewedid) 
                if(reviewed_O.groups.filter(name='Company').exists()): 
                    #obtengo la company a la que va dirigida UNA review
                    reviewed_name = Company.objects.values('name').all().get(user = reviewed_O)
                    #print(reviewed_name)

                    #reviews con reviewedid de una company en concreto
                    reviewed_reviews = Review.objects.all().filter(reviewed_id = reviewedid).values().distinct()
                    count = 0 #numero de reviews para un datascientist concreto
                    score = 0
                    average = 0
                    scores = []
                    for rr in reviewed_reviews:
                        count = count + 1
                        print('count: ',count)
                        score = rr['score']
                        print('score: ',score)

                        scores.append(score)
                        print('scores', scores)
                        average = sum(scores) / count
                        print('average', average)

                        #average = (average + float(score)) / count 
                        #print('average', average)

                        comments = rr['comments'] 
                    valores.append({
                        'reviewed_name' : str(reviewed_name['name']),
                        'average' : float(average),
                        'comments' : str(comments)
                    });
            
            valores.sort(key = myFunc,reverse=True)
            print('valores: ', valores)
     
            return JsonResponse(valores, safe=False)        
        except Exception as e:
            return JsonResponse({"message":"Sorry! Something went wrong... | Oops! Algo ha salido mal..." + str(e)})
    
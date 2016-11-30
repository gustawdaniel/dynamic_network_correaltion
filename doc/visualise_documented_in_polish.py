#-*- coding: utf-8 -*-

# Jeśli chodzi o kod, jest to praktycznie ta sama wersja,
# jaka jest w głównym katalogu, żeby działała przenieś ją
# do głównego katalogu, ta wersja została napisana we wrześniu
# 2015, natomiast ta z głównego katalogu była odrobinę oczyszczona
# i przetłumaczona w listopadzie 2016.

import os # potrzebne do wczytywania listy plików
import datetime # do operacji na czasie
import numpy # do korelacji

import xmlrpclib # do wyświetlania 
import time # do oczekiwania między przerwami

# podłączamy się do serwera wyświetlającego obraz
server_url = 'http://127.0.0.1:20738/RPC2'
server = xmlrpclib.Server(server_url)
G = server.ubigraph

G.clear() # czyścimy jego zawartość

##################################################################
#                          KONFIGURACJA                          #
##################################################################

class Config:   
    def __init__(self):
        self.state = 1
    # na ile znaczące jest otwarcie max min i zamknięcie, powinny sumować się do 1
    op = 0.25
    hi = 0.25
    lo = 0.25
    cl = 0.25

    free_mem = 1 # opcja zwalniająca pamięć, nie pozwala później odwoływać się do 
    # czasów i cen orginalnie pobranych z plików wejściowych

    # sleep = 0.01 # ułamek sekundy 
    sleep = 0.0001
    memory = 100 # ile dni wstecz uwzględniana jest korelacja?
    # boundary = 0 # przy jakiej korelacji pojawiają się i znikają połączenia (-1,1)
    boundary= 0.7

config = Config()

##################################################################
#                          DEFINICJE                             #
##################################################################



class Company:
    'Company zawiera informacje o firmie potrzebne do obliczeń'
    def __init__(self, filename):
        self.filename = filename
        self.dates = []
        self.prices = []

        self.prices_evryday = [] # tabela stosowana zamiast dates i prices po
        # określeniu czasu dla którego wykonujemy symulacje

        self.vertex_id = Company.vertex_id
        Company.vertex_id +=1


    vertex_id = 0


    min_date = 0
    max_date = 0

    name = ''

    def debug_print():
        print "name: ",self.name
        print "filename: ",self.filename
        print "vertex: ",self.vertex_id
        print "min_date: ",self.min_date
        print "max_date: ",self.max_date
        print "max price: ",max(self.prices)
        print "min price: ",min(self.prices)

    def in_range(self,date):# czy date jest w zakresie
        if(date > self.min_date and date < self.max_date):
            return 1
        else:
            return 0        

# czy int time jest wewnatrz tablicy date
# # funkcja stosowana podczas interpolacji i wyświetlania
# def in_range(date,time): 
#   if(time > min(date) and time < max(date)):
#       return 1
#   else:
#       return 0 

##################################################################
#                          INTERFACE                             #
##################################################################

print "Wybierz pliki z danymi wejściowymi"

i = 1
paths = []
while 1:
    path = raw_input("Podaj ścierzkę do pliku "+ str(i)+ ", lub ENTER aby zakończyć: ")
    if len(path) == 0:
        break
    i = i+1
    paths.append(path)
    # print path, len(path), paths

if len(paths)==0: #obsługa błędu 
    print "\nNie wybrałeś wystarczającej liczby plików.\nZapoznaj się z dokumentacją na stronie xn--1ea.pl/stock.\n"
    exit()

directory=''
if len(paths)==1: # obsługa katalogu
    directory = paths[0]
    print "Trwa ładowanie plików z katalogu :" + str(directory)
    paths = os.listdir(directory) # nazwy plikow

else:
    print "Trwa ładowanie podanych plików:"

##################################################################
#                     ŁADOWANIE LISTY PLIKÓW                     #
##################################################################

companies = [] # lista firm jeszcze pusta

files_content=[] # zawartosc plikow
for path in paths:# przygotowanie
    files_content.append(open(str(directory)+'/'+str(path), 'r').readlines())
    company = Company(path) # tworzymy firmę
    companies.append(company) # dodajemy do listy
    print paths.index(path), path


print "Trwa przetwarzanie plików"

print "Ucinanie nagłówków"

for file_content in files_content:# usuniecie naglowkow
    file_content.pop(0)


date = []
price = []

min_date = 99999999999 # szukanie min i max date
max_date = 0

epoch = datetime.datetime.utcfromtimestamp(0)

##################################################################
#           ŁADOWANIE ZAWARTOŚĆI PLIKÓW DO PAMIĘCI               #
##################################################################

print "Zapisywanie zawartości"

date=[]
price =[]
for i in range(0,len(files_content)): # dla kazdego pliku 
    for line in files_content[i]: # wez linue
        l = line.rstrip().split(',') # rozbij przecinkami
        date.append((datetime.datetime.strptime(l[1], "%Y%m%d").date()-epoch.date()).days)
        # do tablicy dat dla danego pliku dodaj nowa date w dniach od epoki
        price.append(round(
            float(l[2])*config.op+
            float(l[3])*config.hi+
            float(l[4])*config.lo+
            float(l[5])*config.cl,4))
        # oraz cene z tego dnia - srednia otwarcia, zamkniecia min i max ceny
    min_date = min(min_date,date[0]) # jesli nie bylo wczesniejszego dnia, to ustaw tutaj
    max_date = max(max_date,date[-1]) # jesli nie bylo pozniejszego 

    companies[i].name = l[0]
    companies[i].dates = date
    companies[i].prices = price
    companies[i].min_date = date[0]
    companies[i].max_date = date[-1]

    date=[]
    price=[]
    print i+1, "/", len(files_content)
# numpy.interp(value_x,array_x,array_y)

##################################################################
#           OKREŚLANIE CZASU DLA KTÓREGO OBLICZAMY               #
##################################################################

print "Wybór czasu wizualizacji: "
print "Czas podany jest w dniach od 1 stycznia 1970"
print "Nazwa instrumentu         początek notwań      koniec notowań"
min_max = max_date
max_min = min_date
for company in companies:
    min_max = min(min_max, company.max_date)
    max_min = max(max_min, company.min_date)
    print repr(company.name).ljust(25),repr(company.min_date).ljust(20),repr(company.max_date).ljust(20)
print "Najszerszy możliwy przedział: ",min_date,max_date
print "Przedział w którym wszystkie instrumenty są notowane: ",max_min,min_max

min_user = raw_input("Podaj początkowy dzień obliczeń, ENTER - Najwęższy przedział: ")
if (len(min_user)==0):
    min_user = max_min
else:
    min_user = int(min_user)
max_user = raw_input("Podaj końcowy dzień obliczeń, ENTER - Najwęższy przedział: ")
if (len(max_user)==0):
    max_user = min_max
else:
    max_user = int(max_user)
memory = raw_input("Podaj zakres wsteczny obliczania korelacji, ENTER - 100: ")
if (len(memory)==0):
    memory = config.memory
else:
    memory = int(memory)

##################################################################
#                    INTERPOLACJA CEN                            #
##################################################################

print "Trwa interpolacja cen"

# print "min memm, max ",min_user, memory, max_user

for company in companies:
    for date in range(min_user-memory,max_user):
        if company.in_range(date):
            price = round(numpy.interp(date,company.dates,company.prices),4)
        else:
            price = 0
        company.prices_evryday.append(price)
    print repr(company.vertex_id+1).ljust(3),"/",repr(Company.vertex_id).ljust(6), repr(company.name).ljust(20)
    if(config.free_mem):# zwalnianie pamięci
        company.dates = []
        company.prices = []
    # print "Dla spółki ", company.name
    # print "Data początkowa ", min_user-memory
    # print "Data końcowa ", max_user
    # print "Długość prices_evryday ", len(company.prices_evryday)


##################################################################
#                    OBLICZANIE KORELACJI                        #
##################################################################

print "Trwa obliczanie korelacji"

corr=[]
line =[]
corrs =[] # ogromna macierz warstwowa ze wszystkimi korelacjami,
# w praktyce można ją uprościć do macierzy trójkątnej bo jest symetryczna
# for x in range(memory,max_date-min_date):
numpy.seterr(divide='ignore', invalid='ignore')# ignorowanie błędów które
# pojawiają się jeśli korelacja jest liczona na identycznych ciągach

for date in range(0,max_user-min_user):
    corr = numpy.corrcoef([company.prices_evryday[date:date+memory] for company in companies])
    corrs.append(corr)

##################################################################
#                  TWORZENIE MACIERZY ŁĄCZEŃ                     #
##################################################################

print "Trwa inicjalizacja macierzy połączeń"

e = [[0 for x in range(Company.vertex_id)] for x in range(Company.vertex_id)]# tablica laczen

##################################################################
#              TWORZENIE POCZĄTKOWYCH WIERZCHOŁKÓW               #
##################################################################


for ind in range(0,Company.vertex_id):
    if (companies[ind].prices_evryday[0] != 0): 
        G.new_vertex_w_id(ind)
        G.set_vertex_attribute(ind,'label', companies[ind].name);

##################################################################
#              TWORZENIE POCZĄTKOWYCH KRAWĘDZI                   #
##################################################################

for ind1 in range(0,Company.vertex_id):
    for ind2 in range(ind1+1,Company.vertex_id):
        if corrs[0][ind1][ind2] >= config.boundary:
            e[ind1][ind2] = G.new_edge(ind1, ind2)

##################################################################
#      WIZUALIZACJA DUNAMICZNEJ SIECI KORELACYJNEJ               #
##################################################################

# dla każdej chwili czasu
for x in range(1,len(corrs)):
    # dla każdej spółki
    for ind1 in range(0,Company.vertex_id):
        # jeśli nawa spółka zaczyna być notowana dodaj ją
        if companies[ind1].prices_evryday[x-1] == 0 and companies[ind1].prices_evryday[x] != 0:
            G.new_vertex_w_id(ind1)
            G.set_vertex_attribute(ind1,'label', companies[ind1].name);
            print x," (a):v ",ind1          
        # dla każdej kolejnej spóki o indeksie większym niż poprzednia
        for ind2 in range(ind1+1,Company.vertex_id):
            # jeśli połączenie pojawiło się dodaj je
            if corrs[x-1][ind1][ind2] < config.boundary and corrs[x][ind1][ind2] >= config.boundary:
                e[ind1][ind2] = G.new_edge(ind1, ind2)
                print x," (a):e ",ind1,ind2
            # jeśli połączenie zniknęło usuń je
            if corrs[x-1][ind1][ind2] >= config.boundary and corrs[x][ind1][ind2] < config.boundary:
                G.remove_edge(e[ind1][ind2])
                print x," (r):e ",ind1,ind2
            time.sleep(config.sleep)
        if companies[ind1].prices_evryday[x-1] != 0 and companies[ind1].prices_evryday[x] == 0:
            G.remove_vertex(ind1)
            print x," (r):v ",ind1          






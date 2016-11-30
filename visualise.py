# -*- coding: utf-8 -*-

import os  # for loading files
import datetime  # for time operations
import numpy  # for calculation correlation

import xmlrpclib  # for visualise by ubigraph
import time  # for waiting between steps

#  connect to server displaying image
server_url = 'http://127.0.0.1:20738/RPC2'
server = xmlrpclib.Server(server_url)
G = server.ubigraph

G.clear()  # clear image before start


##################################################################
#                          Configuration                         #
##################################################################

class Config:
    def __init__(self):
        self.state = 1

    # weights of open, highest, lowest and close price for calculating correlation
    op = 0.25
    hi = 0.25
    lo = 0.25
    cl = 0.25

    free_mem = 1  # option for free memory

    sleep = 0.001  # time of sleeping between steps
    memory = 100  # How many days before actual data should be taken in correlation?
    # boundary = 0 #
    boundary = 0.7  # correlation boundary between showed and hidden connection in graph


config = Config()


##################################################################
#                          Definitions                           #
##################################################################

class Company:
    """Company contains info about company needed to calculations"""

    def __init__(self, filename):
        self.filename = filename
        self.dates = []
        self.prices = []

        self.prices_evryday = []  # table used instead dates and prices after assigning time of simulation

        self.vertex_id = Company.vertex_id
        Company.vertex_id += 1

    vertex_id = 0
    min_date = 0
    max_date = 0
    name = ''

    def debug_print(self):
        print "name: ", self.name
        print "filename: ", self.filename
        print "vertex: ", self.vertex_id
        print "min_date: ", self.min_date
        print "max_date: ", self.max_date
        print "max price: ", max(self.prices)
        print "min price: ", min(self.prices)

    def in_range(self, date):  # czy date jest w zakresie
        if self.min_date < date < self.max_date:
            return 1
        else:
            return 0

        ##################################################################
        #                          Interface                             #
        ##################################################################

print "Select files with input data"

i = 1
paths = []
while 1:
    path = raw_input("Get path to files " + str(i) + ", or ENTER to finish: ")
    if len(path) == 0:
        break
    i += 1
    paths.append(path)
    print path, len(path), paths

if len(paths) == 0:  # if error
    print "\nYou do not chosen enough number of files.\nRead docs or contact with author: gustaw.daniel@gmial.com.\n"
    exit()

directory = ''
if len(paths) == 1:  # catalog
    directory = paths[0]
    print "Loading from catalog :" + str(directory)
    paths = os.listdir(directory)  # names of files

else:
    print "Loading given files:"

##################################################################
#                     Loading list of files                      #
##################################################################

companies = []  # empty list of companies

files_content = []  # empty content of files
for path in paths:  # for any path
    files_content.append(open(str(directory) + '/' + str(path), 'r').readlines())
    company = Company(path)  # create company
    companies.append(company)  # append to companies list
    print paths.index(path), path

print "Processing files"

print "Cutting headers"

for file_content in files_content:  # removing headers
    file_content.pop(0)

date = []
price = []

min_date = 99999999999  # searching min and max date common for companies
max_date = 0

epoch = datetime.datetime.utcfromtimestamp(0)

##################################################################
#           Loading files to memory                              #
##################################################################

print "Saving content"

for i in range(0, len(files_content)):  # for any file
    for line in files_content[i]:  # get line
        l = line.rstrip().split(',')  # split by coma
        date.append((datetime.datetime.strptime(l[1], "%Y%m%d").date() - epoch.date()).days)
        # append date in days form epoch to date array
        price.append(round(
            float(l[2]) * config.op +
            float(l[3]) * config.hi +
            float(l[4]) * config.lo +
            float(l[5]) * config.cl, 4))
        # and price as mean with proper weights to price array
    min_date = min(min_date, date[0])  # if there was no date before this one, set this date there
    max_date = max(max_date, date[-1])  # and in similar way set latest date

    companies[i].name = l[0]
    companies[i].dates = date
    companies[i].prices = price
    companies[i].min_date = date[0]
    companies[i].max_date = date[-1]

    date = []
    price = []
    print i + 1, "/", len(files_content)

##################################################################
#           Selecting time of simulation                         #
##################################################################

print "Selecting time of visualisation: "
print "Time given is in days from 01.01.1970"
print "Company name         start of date      end of data"
min_max = max_date
max_min = min_date
for company in companies:
    min_max = min(min_max, company.max_date)
    max_min = max(max_min, company.min_date)
    print repr(company.name).ljust(25), repr(company.min_date).ljust(20), repr(company.max_date).ljust(20)
print "Union (at least one company on stock): ", min_date, max_date
print "Intersection (all companies on stock): ", max_min, min_max

min_user = raw_input("Set first day of simulation, ENTER - Intersection: ")
if len(min_user) == 0:
    min_user = max_min
else:
    min_user = int(min_user)
max_user = raw_input("Set last day of simulation, ENTER - Intersection: ")
if len(max_user) == 0:
    max_user = min_max
else:
    max_user = int(max_user)
memory = raw_input("Set range of calculating correlation, ENTER - 100: ")
if len(memory) == 0:
    memory = config.memory
else:
    memory = int(memory)

##################################################################
#                    Interpolation of prices                     #
##################################################################

print "Prices are interpolated"

# print "min memm, max ",min_user, memory, max_user

for company in companies:
    for date in range(min_user - memory, max_user):
        if company.in_range(date):
            price = round(numpy.interp(date, company.dates, company.prices), 4)
        else:
            price = 0
        company.prices_evryday.append(price)
    print repr(company.vertex_id + 1).ljust(3), "/", repr(Company.vertex_id).ljust(6), repr(company.name).ljust(20)
    if config.free_mem:  # free memory
        company.dates = []
        company.prices = []

##################################################################
#                    Calculation of correlations                 #
##################################################################

print "Calculating of correlation"

corr = []
line = []
correlations = []  # Huge layer matrix with any correlations,

numpy.seterr(divide='ignore', invalid='ignore')  # ignoring of warnings that we get
# calculating correlation on identical lists

for date in range(0, max_user - min_user):
    corr = numpy.corrcoef([company.prices_evryday[date:date + memory] for company in companies])
    correlations.append(corr)

##################################################################
#                  Creating matrix of connections                #
##################################################################

print "Trwa inicjalizacja macierzy połączeń"

e = [[0 for x in range(Company.vertex_id)] for y in range(Company.vertex_id)]  # matrix of connections

##################################################################
#              Creation of initial vertexes                      #
##################################################################


for ind in range(0, Company.vertex_id):
    if companies[ind].prices_evryday[0] != 0:
        G.new_vertex_w_id(ind)
        G.set_vertex_attribute(ind, 'label', companies[ind].name)

##################################################################
#              Creation initial connections                      #
##################################################################

for ind1 in range(0, Company.vertex_id):
    for ind2 in range(ind1 + 1, Company.vertex_id):
        if correlations[0][ind1][ind2] >= config.boundary:
            e[ind1][ind2] = G.new_edge(ind1, ind2)

##################################################################
#      Visualisation of dynamic correlation network              #
##################################################################

# for any time
for x in range(1, len(correlations)):
    # for any company
    for ind1 in range(0, Company.vertex_id):
        # if company starts be noted, create them
        if companies[ind1].prices_evryday[x - 1] == 0 and companies[ind1].prices_evryday[x] != 0:
            G.new_vertex_w_id(ind1)
            G.set_vertex_attribute(ind1, 'label', companies[ind1].name)
            print x, " (a):v ", ind1
        # for any company with index higher than last one
        for ind2 in range(ind1 + 1, Company.vertex_id):
            # if connection occurs, add this
            if correlations[x - 1][ind1][ind2] < config.boundary <= correlations[x][ind1][ind2]:
                e[ind1][ind2] = G.new_edge(ind1, ind2)
                print x, " (a):e ", ind1, ind2
            # if connection vanishes, delete this
            if correlations[x - 1][ind1][ind2] >= config.boundary > correlations[x][ind1][ind2]:
                G.remove_edge(e[ind1][ind2])
                print x, " (r):e ", ind1, ind2
            time.sleep(config.sleep)
        if companies[ind1].prices_evryday[x - 1] != 0 and companies[ind1].prices_evryday[x] == 0:
            G.remove_vertex(ind1)
            print x, " (r):v ", ind1

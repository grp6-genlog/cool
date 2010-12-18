#!/usr/bin/python
#
# @Author Cyrille Dejemeppe

from django.conf import settings
import os, sys
sys.path.insert(0, os.path.join(settings.PROJECT_PATH,'modules'))

import datetime, random
from django.contrib.auth.models import User
from profiles.models import UserProfile
from requests.models import Request
from offers.models import Offer
from rides.models import Ride
from proposals.models import Proposal, RoutePoints
from utils import get_distance,get_time_at_point, total_seconds


def compute_fee(proposal, departure, arrival):
    dep = RoutePoints.objects.get(id=departure)
    arr = RoutePoints.objects.get(id=arrival)
    total=0.
    last = dep
    for index in range(dep.order+1, arr.order+1):
        tmp = RoutePoints.objects.get(order=index,proposal=proposal)
        total+=get_distance((last.latitude,last.longitude),(tmp.latitude,tmp.longitude))
        last= tmp
    return total*proposal.money_per_km
    

def match_proposal(propID):
    """
    This operation try to match the specified proposal with each request of the DB
    
    @pre : DB has been initialized and is the SQL database
    offermanager_port has been initialized and is the port of the OfferManager module
    
    propId is the id of a proposal in the database
    
    @post : DB has not been modified.
    for each request matching the specified proposal, a message is sent to OfferManager through its port:
    ('buildoffer',requestID,proposalID) with requestID, the database ID of the matching request
    """
    infos=Proposal.objects.get(id=propID)
    requests=Request.objects.filter(nb_requested_seats__lte=infos.number_of_seats)

    for request in requests:
        found = False
        for offer in Offer.objects.filter(request=request):
            if Ride.objects.filter(offer=offer):
                found=True
                break
        if not found:
            route_points = RoutePoints.objects.filter(proposal=infos).order_by('order')
            valid_pair = list()
            for i in xrange(len(route_points)-2):
                if get_distance((request.departure_point_lat,request.departure_point_long),(route_points[i].latitude,route_points[i].longitude))<request.departure_range:
                    for j in range(i+1,len(route_points)):
                        if get_distance((request.arrival_point_lat,request.arrival_point_long),(route_points[j].latitude,route_points[j].longitude))<request.arrival_range:
                            valid_pair.append((i,j))
            for (i,j) in valid_pair:
                    #delete all not in time arrival
                if total_seconds(abs(get_time_at_point([(r.latitude,r.longitude) for r in route_points],j,infos.departure_time,infos.arrival_time)-request.arrival_time)) < request.max_delay:
                    build_offer(request.id, infos.id,
                                (
                                    route_points[i].latitude,
                                    route_points[i].longitude,
                                    get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                                   i,infos.departure_time,infos.arrival_time),
                                    route_points[i].id
                                ),
                                (
                                    route_points[j].latitude,
                                    route_points[j].longitude,
                                    get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                                   j,infos.departure_time,infos.arrival_time),
                                    route_points[j].id
                                 ))

def build_offer(requestID,proposalID,departure,arrival):
    """
    Create a new offer in the database (a new entry in the offer table) for the request and the proposal.
    @pre: requestID is the ID of a request in db
    proposalID is the ID of a proposal in db
    It doesn't already exist an offer in the db for this couple requestID, proposalID
    
    @post:    A new offer is created in the db for the couple request proposal with the following states:
    status = pending
    DriverOk = false
    nonDriverOk = false
    """
    proposals=Proposal.objects.filter(id=proposalID)
    
    if len(proposals)==0:
        raise "Try to build an offer from a proposal that doesn't exist"
    fee=compute_fee(proposals[0], departure[3], arrival[3])
    
    offer=Offer()
    offer.request=Request.objects.get(id=requestID)
    offer.proposal=Proposal.objects.get(id=proposalID)
    offer.status='P'
    offer.driver_ok=False
    offer.non_driver_ok=False
    offer.pickup_point_lat=departure[0]
    offer.pickup_point_long=departure[1]
    offer.pickup_time = departure[2]
    offer.drop_point_lat=arrival[0]
    offer.drop_point_long=arrival[1]
    offer.drop_time = arrival[2]
    offer.pickup_point = RoutePoints.objects.get(id=departure[3])
    offer.drop_point = RoutePoints.objects.get(id=arrival[3])
    offer.total_fee=fee
    offer.save()

def match_request(requestID):
    """
    This operation try to match the specified proposal with each request of the DB
    
    @pre : DB has been initialized and is the SQL database
    offermanager_port has been initialized and is the port of the OfferManager module
    
    requestId is the id of a request in the database
    
    @post : DB has not been modified.
    for each proposal matching the specified request, a message is sent to OfferManager through its port:
    ('buildoffer',requestID,proposalID) with proposalID, the database ID of the matching proposal
    """
    request=Request.objects.get(id=requestID)
    proposals=Proposal.objects.filter(number_of_seats__gte=request.nb_requested_seats)
    for infos in proposals:
        route_points = RoutePoints.objects.filter(proposal=infos).order_by('order')
        valid_pair = list()
        for i in xrange(len(route_points)-2):
            if get_distance((request.departure_point_lat,request.departure_point_long),(route_points[i].latitude,route_points[i].longitude))<request.departure_range:
                for j in range(i+1,len(route_points)):
                    if get_distance((request.arrival_point_lat,request.arrival_point_long),(route_points[j].latitude,route_points[j].longitude))<request.arrival_range:
                        valid_pair.append((i,j))
        for (i,j) in valid_pair:
            #delete all not in time arrival
            if total_seconds(abs(get_time_at_point([(r.latitude,r.longitude) for r in route_points],j,infos.departure_time,infos.arrival_time)-request.arrival_time)) < request.max_delay:
                build_offer(requestID,
                            infos.id,
                            (
                                route_points[i].latitude,
                                route_points[i].longitude,
                                get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                               i,infos.departure_time,infos.arrival_time),
                                route_points[i].id
                            ),
                            (
                                route_points[j].latitude,
                                route_points[j].longitude,
                                get_time_at_point([(r.latitude,r.longitude) for r in route_points],
                                               j,infos.departure_time,infos.arrival_time),
                                route_points[j].id
                             ))

def printlist(mylist):
    tmp =''
    for e in mylist:
        tmp += e
    print tmp

def add_in_rp_list(rp, rp_list, order):
    if order == 1:
        for i in xrange(len(rp_list)):
            if (rp[0]**2) + (rp[1]**2) < (rp_list[i][0]**2) + (rp_list[i][1]**2):
                rp_list.insert(i,rp)
                break
    else:
        for k in xrange(len(rp_list)):
            if (rp[0]**2) + (rp[1]**2) > (rp_list[k][0]**2) + (rp_list[k][1]**2):
                rp_list.insert(k,rp)
                break

def create_user(uname, firstname, lastname, mail, pwd):
    time_now = datetime.datetime.today()
    u = User.objects.create_user(uname, mail, pwd)
    u.first_name = firstname
    u.last_name = lastname
    u.save()
    return u

def create_profile(user, nb_seats, birthdate, smoke_bool, communities, moneyperkm, gender, bank_account, car_id, phone_nb, car_desc):
    p = UserProfile()
    p.user = user
    p.number_of_seats = nb_seats
    p.date_of_birth = birthdate
    p.smoker = smoke_bool
    p.communities = communities
    p.money_per_km = moneyperkm
    p.gender = gender
    p.bank_account_number = bank_account
    p.account_balance = random.randint(0,500)
    p.car_id = car_id
    p.phone_number = phone_nb
    p.car_description = car_desc
    p.save()
    return p

def create_request(user, dep_p_lat, dep_p_long, dep_ran, ar_p_lat, ar_p_long, ar_ran, ar_time, max_del, nb_seats, cancel_margin):
    r = Request()
    r.user = user
    r.departure_point_lat = dep_p_lat
    r.departure_point_long = dep_p_long
    r.departure_range = dep_ran
    r.arrival_point_lat = ar_p_lat
    r.arrival_point_long = ar_p_long
    r.arrival_range = ar_ran
    r.arrival_time = ar_time
    r.max_delay = max_del
    r.nb_requested_seats = nb_seats
    r.cancellation_margin = cancel_margin
    r.status = 'P'
    r.save()
    match_request(r.id)

def create_proposal(user, car_id, car_desc, nb_seats, moneyperkm, dep_time, ar_time, route_points_list):
    p = Proposal()
    p.user = user
    p.car_id = car_id
    p.car_description = car_desc
    p.number_of_seats = nb_seats
    p.money_per_km = moneyperkm
    p.departure_time = dep_time
    p.arrival_time = ar_time
    p.status = 'P'
    p.save()
    
    order = 0
    for (latitude, longitude) in route_points_list:
        rp = RoutePoints()
        rp.proposal = p
        rp.latitude = latitude
        rp.longitude = longitude
        rp.order = order
        rp.save()
        order += 1
    match_proposal(p.id)


def create_users(nb_users, male_first_name_list, female_first_name_list, last_name_list, server_list, pwd_list, communities_list, car_desc_list, route_points_list):
    counter = 1
    counter2 = 0
    advancement_list = ['[',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',']']
    for i in xrange(nb_users):
        if counter > counter2 * nb_users/50:
            counter2 += 1
            advancement_list[counter2] = '='
            printlist(advancement_list)
        counter += 1
        # Chosing all the random fields for user and profile tables
        gender = random.randint(0,1) == 1
        if gender:
            f_name_ind = random.randint(0, len(male_first_name_list) - 1)
            first_name = male_first_name_list[f_name_ind]
            gender = 'M'
        else:
            f_name_ind = random.randint(0, len(female_first_name_list) - 1)
            first_name = female_first_name_list[f_name_ind]
            gender = 'F'
        l_name_ind = random.randint(0, len(last_name_list) - 1)
        last_name = last_name_list[l_name_ind]
        uname = first_name + '_' + last_name + str(random.randint(0,999))
        server_ind = random.randint(0, len(server_list) - 1)
        email = first_name + '.' + last_name + '@' + server_list[server_ind] + '.com'
        pwd_ind = random.randint(0, len(pwd_list) - 1)
        password = uname #pwd_list[pwd_ind] + str(random.randint(0,999))
        com_ind_list = list()
        for i in xrange(random.randint(1,5)):
            com_ind_list.append(random.randint(0, len(communities_list) - 1))
        communities = ''
        for com_ind in list(set(com_ind_list)):
            communities += communities_list[com_ind] + ','
        car = random.randint(0,1) == 1
        if car:
            car_desc_ind = random.randint(0, len(car_desc_list) - 1)
            car_description = car_desc_list[car_desc_ind]
        else:
            car_description = None

        birthdate = datetime.date(random.randint(1950,1990), random.randint(1,12), random.randint(1,28))
        bank_account = str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + '-' + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + '-' + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))
        car_id = chr(random.randint(65,90)) + chr(random.randint(65,90)) + chr(random.randint(65,90)) + '-' + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))
        phone_nb = '0'+ str(random.randint(0,9)) + str(random.randint(0,9)) + '/' + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))
        if car:
            nb_seats = random.randint(1,5)
        else:
            nb_seats = 0

        # Creating a new user and his/her profile:
        user = create_user(uname, first_name, last_name, email, password)
        userprofile = create_profile(user, nb_seats, birthdate, random.randint(0,1) == 1, communities, random.uniform(0.01, 0.25), gender, bank_account, car_id, phone_nb, car_description)

        # Chosing all the random fields for request and proposal tables
        for j in xrange(random.randint(0,2)):
            dep_p_ind = random.randint(0, len(route_points_list) - 1)
            ar_p_ind = random.randint(0, len(route_points_list) - 1)
            dep_p_lat = route_points_list[dep_p_ind][0]
            dep_p_long = route_points_list[dep_p_ind][1]
            dep_ran = random.uniform(0.5, 25.0)
            ar_p_lat = route_points_list[ar_p_ind][0]
            ar_p_long = route_points_list[ar_p_ind][1]
            ar_ran = random.uniform(0.5, 25.0)
            ar_time = datetime.datetime(2010, 12, random.randint(20,31), random.randint(7,22), random.randint(0,59), 0)
            max_del = random.randint(300,3600)
            nb_seats= random.randint(1,4)
            cancel_margin = datetime.datetime(2010, 12, (ar_time.day-random.randint(0,1)), (ar_time.hour - random.randint(0,ar_time.hour)),ar_time.minute,ar_time.second)
            create_request(userprofile, dep_p_lat, dep_p_long, dep_ran, ar_p_lat, ar_p_long, ar_ran, ar_time, max_del, nb_seats, cancel_margin)


        if car:
            for k in xrange(random.randint(0,2)):
                car_id = userprofile.car_id
                car_desc = userprofile.car_description
                nb_seats = userprofile.number_of_seats
                moneyperkm = userprofile.money_per_km
                dep_time = datetime.datetime(2010, 12, random.randint(20,31), random.randint(7,22), random.randint(0,59), 0)
                rp_list = list()
                for rp in xrange(random.randint(2, 10)):
                    rp_list.append(route_points_list[random.randint(0, len(route_points_list) - 1)])
                
                route_p_list = [(-8000.0,-8000.0)]
                order = random.randint(0,1)
                for e in list(set(rp_list)):
                    add_in_rp_list(e, route_p_list, order)
                
                route_p_list.remove((-8000.0,-8000.0))
                
                if len(route_p_list) < 2:
                    route_p_list.insert(0,(50.885015567679545, 5.096008367836475))
                    
                dist = get_distance(route_p_list[0],route_p_list[-1])
                ar_time = dep_time + datetime.timedelta(minutes=int(dist))
                create_proposal(userprofile, car_id, car_desc, nb_seats, moneyperkm, dep_time, ar_time, route_p_list)

def main():
    male_name_list = ['Jacob','Michael','Ethan','Joshua','Daniel','Alexander','Anthony','William','Christopher','Matthew','Jayden','Andrew','Joseph','David',
                      'Noah','Aiden','James','Ryan','Logan','John','Nathan','Elijah','Christian','Gabriel','Benjamin','Jonathan','Tyler','Samuel','Nicholas',
                      'Gavin','Dylan','Jackson','Brandon','Caleb','Mason','Angel','Hiro','Evan','Jack','Kevin','Jose','Neo','Luke','Sangoku','Justin','Lucas',
                      'Zachary','Jordan','Robert','Aaron','Anakin','Thomas','Cameron','Hunter','Austin','Adrian','Connor','Owen','Raito','Jason','Julian',
                      'Merlin','Charles','Luis','Carter','Juan','Chase','Diego','Jeremiah','Morpheus','Cloud','Adam','Carlos','Sebastian','Liam','Hayden',
                      'Nathaniel','Henry','Jesus','Ian','Tristan','Bryan','Sean','Cole','Alex','Eric','Brutus','Jaden','Carson','Blake','Saul','Cooper',
                      'Dominic','Naruto','Caden','Josiah','Kyle','Colton','Kaden','Eli']
    female_name_list = ['Emma','Isabella','Emily','Madison','Ava','Olivia','Sophia','Abigail','Elizabeth','Chloe','Samantha','Addison','Natalie','Mia','Alexis',
                        'Alyssa','Hannah','Ashley','Ella','Sarah','Grace','Taylor','Brianna','Lily','Hailey','Anna','Victoria','Kayla','Lillian','Lauren',
                        'Kaylee','Allison','Savannah','Nevaeh','Gabriella','Sofia','Makayla','Trinity','Riley','Julia','Leah','Aubrey','Jasmine','Audrey',
                        'Katherine','Morgan','Brooklyn','Destiny','Sydney','Alexa','Kylie','Brooke','Kaitlyn','Evelyn','Layla','Madeline','Kimberly','Zoe',
                        'Jessica','Peyton','Alexandra','Claire','Madelyn','Maria','Matrix','Arianna','Jocelyn','Amelia','Angelina','Trinity','Andrea','Maya',
                        'Valeria','Sophie','Rachel','Vanessa','Aaliyah','Mariah','Gabrielle','Katelyn','Ariana','Bailey','Camila','Jennifer','Melanie','Gianna',
                        'Charlotte','Paine','Autumn','Yuna','Faith','Sara','Isabelle','Caroline','Genesis','Isabel','Mary','Zoey','Gracie','Megan']
    last_name_list = ['Adams','Allen','Anderson','Bailey','Baker','Barnes','Bell','Bennett','Brooks','Brown','Butler','Campbell','Carter','Clark','Collins','Cook',
                      'Cooper','Cox','Cruz','Davis','Anderson','Edwards','Evans','Fisher','Flores','Foster','Nakamura','Davids','Gray','Green','Gutierrez','Gomez',
                      'Hall','Harris','Nakamura','Hill','Howard','Hughes','Jackson','James','Jenkins','Johnson','Jones','Kelly','King','Lee','Lewis','Long',
                      'Lopez','Martin','Uzumaki','Miller','Mitchell','Moore','Morales','Morgan','Morris','Murphy','Myers','Nelson','Nguyen','Ortiz','Parker',
                      'Perry','Peterson','Phillips','Powell','Price','Perez','Ramirez','Reed','Reyes','Richardson','Rivera','Roberts','Robinson','Rodriguez',
                      'Rogers','Ross','Russell','Sanders','Scott','Smith','Stewart','Sullivan','Sanchez','Taylor','Thomas','Thompson','Torres','Turner','Walker',
                      'Ward','Watson','White','Williams','Wilson','Wood','Wright','Young']
    server_list = ['axigen','bincimapd','bongo','bluebottle','citadel','communigate','contactoffice','cyrus','dbmail','dovecot','eudora','firstclass','gordano',
                   'hamster','hexamail','hmailserver','indimail','ipswitch','meldware','kerio','mailtraq','novell','open-xchange','oracle','smartermail',
                   'surgemail','synovel','wingate','xmail','zarafa','zimbra']
    pwd_list = ['123456','password','phpbb','qwerty','12345','jesus','12345678','1234','abc123','letmein','test','love','123','password1','hello','monkey',
                'dragon','trustno1','111111','iloveyou','1234567','shadow','123456789','christ','sunshine','master','computer','princess','tigger','football',
                'angel','jesus1','123123','whatever','freedom','killer','asdf','soccer','superman','michael','cheese','internet','joshua','fuckyou','blessed',
                'baseball','starwars','0','42','jordan','faith','summer','ashley','buster','heaven','pepper','7777777','hunter','lovely','andrew','thomas',
                'angels','charlie','daniel','1111','jennifer','single','hannah','qazwsx','happy','matrix','pass','aaaaaa','654321','amanda','nothing','ginger',
                'mother','snoopy','jessica','welcome','pokemon','iloveyou1','11111','mustang','helpme','justin','jasmine','orange','testing','apple','michelle',
                'peace','secret','1','grace','william','iloveyou2','nicole','666666']
    communities_list = ['UCl','KUL','Star wars','Konoha','CIA','FBI','ULB','SS','Ubuntu','Emacs','Yakuza','Mafia','Red army','Al Quaeda','Army','US government',
                        'FIFA','UEFA','SKL','NFL','The ring','Harvard','NBA','Mac hater','James Brown fans','SAMU','Assassin','The order','INGI','MAP','KIMA',
                        'COOL','Fan of Merlin','Air force','Super tron','Inception','DRUGS','CLONE']
    car_desc_list = [' S AC Cars 427 S/C 66','S Acura CL 3.2 Type-S 01','S Acura CL 3.2 Type-S 03','S Acura DN-X Concept 02','S Acura HSC Concept 04',
                     'S Acura INTEGRA TYPE R 01','P/S Acura NSX 91','P Acura NSX RM 91','S Acura NSX 04','S Acura NSX Coupe 97','S Acura RSX Type-S 04',
                     'P AEM S2000 (SEMA Gran Turismo Awards 2005)','S Alfa Romeo 147 2.0 TWIN SPARK 02','S Alfa Romeo 147 GTA 02',
                     'P Alfa Romeo 147 TI 2.0 TWIN SPARK 06','S Alfa Romeo 155 2.5 V6 TI 93','S Alfa Romeo 156 2.5 V6 24V 98',
                     'S Alfa Romeo 166 2.5 V6 24V Sportronic 98','P Alfa Romeo 8C Competizione 08','P Alfa Romeo Brera Sky Window 3.2 JTS Q4 06',
                     'S Alfa Romeo Giulia Sprint GTA 1600 65','S Alfa Romeo Giulia Sprint Speciale 63',
                     'P Alfa Romeo GIULIA TZ2 carrozzata da ZAGATO CN.AR750106 65 (Pebble Beach Concours d elegance Gran Turismo Trophy 2009)',
                     'S Alfa Romeo GT 3.2 V6 24V 04','S Alfa Romeo GTV 3.0 V6 24V 01','S Alfa Romeo Spider 3.0i V6 24V 01','S Alfa Romeo Spider 1600 Duetto 66',
                     'S Alpine A110 1600S 73','S Alpine A310 1600VE 73','S Amuse Carbon R (R34) 04','P Amuse NISMO 380RS Super Leggera','S Amuse S2000 GT1 04',
                     'P Amuse S2000 GT1 Turbo','S Amuse S2000 R1 04','S Amuse S2000 Street Version 04','P Art Morrison Corvette 60 (SEMA Gran Turismo Awards 2006)',
                     'S Aston Martin DB7 Vantage Coupe 00','S Aston Martin DB9 Coupe 03','P Aston Martin DB9 Coupe 06','S Aston Martin V8 Vantage 99',
                     'S Aston Martin Vanquish 04','S Audi A2 1.4 02','S Audi A3 3.2 quattro 03','S Audi A4 Touring Car 04','S Audi Abt Audi TT-R Touring Car 02',
                     'S Audi Le Mans quattro 03','S Audi Nuvolari quattro 03','S Audi Pikes Peak quattro 03','S Audi quattro 82','P Audi R8 4.2 FSI R tronic 07',
                     'P Audi R8 5.2 FSI quattro 09','S Audi R8 LMS Race Car 09','S Audi R8 LMS Race Car (Team PlayStation) 09','S Audi R8 Race Car 01',
                     'S Audi R8 Race Car (Audi PlayStation Team ORECA) 05','P Audi R10 TDI Race Car 06','S Audi RS 4 01','S Audi RS 6 02',
                     'S Buick Special 62 (SEMA Gran Turismo Awards 2003)','S Cadillac CIEN Concept 02','S Callaway C12 03','S Caterham Seven Fire Blade 02',
                     'S Chaparral 2D Race Car 67','S Chaparral 2J Race Car 70','P Chevrolet 2010 Dale Earnhardt Jr.',
                     'AMP Energy/National Guard CHEVROLET IMPALA 10','P Chevrolet 2010 Jeff Gordon #24 DuPont CHEVROLET IMPALA 10',
                     'P Chevrolet 2010 Jimmie Johnson #48 Lowe\'s CHEVROLET IMPALA 10','P Chevrolet 2010 Juan Montoya #42 Target CHEVROLET IMPALA 10',
                     'P Chevrolet 2010 Tony Stewart #14 Office Depot Old Spice CHEVROLET IMPALA 10','S Chevrolet Camaro IROC-Z Concept 88','S Citroen C3 1.6 02',
                     'P Citroen C4 Coupe 2.0VTS 05','S Citroen C5 V6 Exclusive 03','P Citroen Citroen C4 WRC 08','P/S Citroen GT by Citroen Concept 08',
                     'P Citroen GT by Citroen Race Car','S Daihatsu SIRION X4 (J) 00','S Daihatsu STORIA CX 2WD 98','S Daihatsu STORIA CX 4WD 98',
                     'S Daihatsu STORIA X4 00','S DMC DeLorean S2 04','P Dodge Challenger R/T 70','S Dodge Viper GTS-R Team Oreca Race Car 00',
                     'S Dodge Viper SRT10 03','P Dodge Viper SRT10 ACR 08','P Ferrari 330 P4 Race Car 67','P Ferrari 430 Scuderia 07','P Ferrari 458 Italia 09',
                     'P Ferrari 512BB 76','S Fiat 500 R 72','S Fiat Barchetta Giovane Due 00','P Ford Focus ST 06','S Ford Focus ST170 03','S Ford Ford GT 02',
                     'S Ford Ford GT 05','S Honda Castrol MUGEN NSX (JGTC) 00','S Honda CITY Turbo II 83','S Honda CIVIC 1500 3door 25i 83',
                     'S Honda CIVIC 1500 3door CX 79']

    route_points_list = [(51.104901597287146, 3.4269104339182377),(51.111799359288014, 5.239654574543238),(50.51133060530523, 5.267120394855738),(49.968182569011724, 5.458557195961475),(50.09380282770382, 3.5038147307932377),(50.86629801972728, 4.800201449543238),(50.85589612171209, 3.2236633636057377),(50.158601346149815, 4.513732977211475),(51.15316431532614, 5.898834262043238),(51.50463952950513, 4.502746649086475),(50.78093392042112, 2.5032349303364754),(50.732283037120425, 3.9204712584614754),(50.572073903534324, 6.095764227211475),(50.65572944615896, 4.623596258461475),(51.14765110760071, 4.294006414711475),(51.374523601460275, 4.843322820961475),(50.32722825732965, 5.216857977211475),(50.42531856595681, 4.074279852211475),(49.69890426086907, 5.568420477211475),(50.41131808144422, 5.810119695961475)]
        
    create_users(1000, male_name_list, female_name_list, last_name_list, server_list, pwd_list, communities_list, car_desc_list, route_points_list)

main()

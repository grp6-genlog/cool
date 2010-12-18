import threading,pickle
import google_tools_json,json
import datetime

class WaitCallbacks(object):
    _active = {}
    _active_lock = threading.Lock()
    _message = {}
    _message_lock = threading.Lock()

    

    @classmethod
    def is_pending(cls, u):
        with cls._active_lock:
            if u in cls._active:
                return cls._active.get(u) == 'pending'
            else:
                return False
            
    @classmethod
    def declare(cls, u):
        with cls._active_lock:
            while u in cls._active:
                pass
            cls._active.update({u:'pending'})
            
    @classmethod
    def free(cls, u):
        with cls._active_lock:
            if u in cls._active:
                cls._active.pop(u)

    @classmethod
    def update(cls, u, status):
        with cls._active_lock:
            cls._active.update({u:status})
            
            
    @classmethod
    def status(cls, u):
        with cls._active_lock:
            if u in cls._active:
                return cls._active.get(u)
            else:
                return None
                


    @classmethod
    def erase_message(cls, u):
        with cls._message_lock:
            if u in cls._message:
                cls._message.pop(u)

    @classmethod
    def update_message(cls, u, msg):
        with cls._message_lock:
            cls._message.update({u:status})
    
    @classmethod
    def message_present(cls, u):
        with cls._message_lock:
            return u in cls._message
            
    @classmethod
    def get_message(cls, u):
        with cls._message_lock:
            if u in cls._message:
                return cls._message.get(u)
            else:
                return None

class AddressCache():
    dico = None
    lock = None
    
    def __init__(self):
        self.dico = dict()
        self.lock = threading.Lock()

    def load(self,filename):
        try:
            f_in = open(filename,'r')
            self.lock.acquire()
            self.dico = pickle.load(f_in)
            self.lock.release()
            f_in.close()
        except:
            pass
    
    def save(self,filename):
        try:
            f_out = open(filename,'w')
            pickle.dump(self.dico,f_out)
            f_out.close()
        except:
            pass
    
    def get_address(self,coord):
        rep = str(coord[0])+','+str(coord[1])
        if rep in self.dico:
            return self.dico[rep][0]
        else:
            addr = json.loads(google_tools_json.location_to_address(rep).read())
            address = None
            if len(addr['results'])==0:
                address = "No address"
            else:
                address = addr['results'][0]['formatted_address']

            with self.lock:
                self.dico[rep] = (address,datetime.datetime.now())

            return address
            
            

 
#
# Utility to check the integrity of an IBAN bank account No.
# Python 2.5.1

# Sample IBAN account numbers.
#-----------------------------
# BE31435411161155
# CH5108686001256515001
# GB35MIDL40253432144670


# Dictionaries - Refer to ISO 7064 mod 97-10 
letter_dic={"A":10, "B":11, "C":12, "D":13, "E":14, "F":15, "G":16, "H":17, "I":18, "J":19, "K":20, "L":21, "M":22,
            "N":23, "O":24, "P":25, "Q":26, "R":27, "S":28, "T":29, "U":30, "V":31, "W":32, "X":33, "Y":34, "Z":35}

# ISO 3166-1 alpha-2 country code
country_dic={"AL":[28,"Albania"],
             "AD":[24,"Andorra"],
             "AT":[20,"Austria"],
             "BE":[16,"Belgium"],
             "BA":[20,"Bosnia"],
             "BG":[22,"Bulgaria"],
             "HR":[21,"Croatia"],
             "CY":[28,"Cyprus"],
             "CZ":[24,"Czech Republic"],
             "DK":[18,"Denmark"],
             "EE":[20,"Estonia"],
             "FO":[18,"Faroe Islands"],
             "FI":[18,"Finland"],
             "FR":[27,"France"],
             "DE":[22,"Germany"],
             "GI":[23,"Gibraltar"],
             "GR":[27,"Greece"],
             "GL":[18,"Greenland"],
             "HU":[28,"Hungary"],
             "IS":[26,"Iceland"],
             "IE":[22,"Ireland"],
             "IL":[23,"Israel"],
             "IT":[27,"Italy"],
             "LV":[21,"Latvia"],
             "LI":[21,"Liechtenstein"],
             "LT":[20,"Lithuania"],
             "LU":[20,"Luxembourg"],
             "MK":[19,"Macedonia"],
             "MT":[31,"Malta"],
             "MU":[30,"Mauritius"],
             "MC":[27,"Monaco"],
             "ME":[22,"Montenegro"],
             "NL":[18,"Netherlands"],
             "NO":[15,"Northern Ireland"],
             "PO":[28,"Poland"],
             "PT":[25,"Portugal"],
             "RO":[24,"Romania"],
             "SM":[27,"San Marino"],
             "SA":[24,"Saudi Arabia"],
             "RS":[22,"Serbia"],
             "SK":[24,"Slovakia"],
             "SI":[19,"Slovenia"],
             "ES":[24,"Spain"],
             "SE":[24,"Sweden"],
             "CH":[21,"Switzerland"],
             "TR":[26,"Turkey"],
             "TN":[24,"Tunisia"],
             "GB":[22,"United Kingdom"]}



def check_validity(n):
    if int(n)%97 !=1:
        result=0                                                # False
    else:
        result=1                                                # True
    return result

def IBAN_check(IBAN):
    print "IBAN account No. :",IBAN
    length = len(IBAN)
    country = IBAN[:2]
    if country_dic.has_key(country):
        data = country_dic[country]
        length_c = data[0]
        name_c = data[1]
        if length == length_c:
            print name_c,"/ IBAN length",length_c,"OK!"
            header = IBAN[:4]                                   # Get the first four characters
            body = IBAN[4:]                                     # And the remaining characters
            IBAN = body+header                                  # Move the first block at the end
            IBAN_ = list(IBAN)                                  # Transform string into a list
            string_="" 
            for index in range(len(IBAN_)):                     # Convert letters to integers
                if letter_dic.has_key(IBAN_[index]):
                    value = letter_dic[IBAN_[index]]
                    IBAN_[index] = value
            for index in range(len(IBAN_)):                     # Transform list into a string
                string_ = string_ + str(IBAN_[index])
            valid = check_validity(string_)                              # Check validity
            if not valid:
                print "Not a valid IBAN account No."
                return False
            else:
                print "IBAN account No. accepted."              # Rebuild the original IBAN
                return True
        else:
            print name_c,"/ Wrong IBAN code length!"
            return False
    else:
        print "Wrong IBAN country code!"
        return False

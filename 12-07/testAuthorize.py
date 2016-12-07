import BigBrotherBank
import RSAWrapper
import pickle
from Crypto.PublicKey import RSA


def test():
    n = 3
    m = 2
    
    id1 = _get_client_id_from_global_name("mannsi")
    id2 = _get_client_id_from_global_name("caro")
    id3 = _get_client_id_from_global_name("mannsi")
    
    pubKey1 = RSA.importKey(open("mannsiPrivateKey.pem",'rb'))
    pubKey2 = RSA.importKey(open("caroPrivateKey.pem", 'rb'))
    
    p1 = 2.0
    p2 = 1.0
    p3 = 3.0
    
    r1 = 1.0
    r2 = 5.0
    
    param_list = [n, m, id1, p1, id2, p2, id3, p3, id1, r1, id2, r2]
    
    list_to_sign = "".join([str(param_list[x]) for x in range(len(param_list))])
    
    sig1 = RSAWrapper.sign(list_to_sign, pubKey1)
    sig2 = RSAWrapper.sign(list_to_sign, pubKey2)
    sig3 = RSAWrapper.sign(list_to_sign, pubKey1)
    
    param_list.append(sig1)
    param_list.append(sig2)
    param_list.append(sig3)
     
    bbb = BigBrotherBank.BigBrotherBank("Database.pickle")
    trans_id = bbb.authorize(param_list)
    
    if trans_id == None:
        print "ERROR - transaction not successful"
    
    ver = bbb.verify(id2, r2, trans_id)
    
    if trans_id == None and ver == False:
        print "Verification works correctly"
    elif ver == True:
        print "Test passed!!!"
    else:
        print "ERROR - verification not successful"
    
    

def _get_client_id_from_global_name(client_name):
    try:
        global_client_dict = pickle.load(open("client_register.pickle", "rb"))
        print global_client_dict
        return global_client_dict[client_name]
    except:
        return ""
    
test()
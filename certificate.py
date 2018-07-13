# coding:utf-8
# To use Bouncy Castle certificate generator both needs CertMaker.dll and BCMakeCert.dll 

import pickle

def prepareCert(FC):
    try: 
        with open('cert', 'rb') as handle:
            certificate = pickle.load(handle)            
            if certificate:
                FC.FiddlerApplication.Prefs.SetStringPref("fiddler.certmaker.bc.key", certificate['key'])
                FC.FiddlerApplication.Prefs.SetStringPref("fiddler.certmaker.bc.cert", certificate['cert'])
    except IOError as err:
        print"\n!! File Error:"+str(err)
    
    # when json file above load and call SetStringPref() method
    # FC.CertMaker.rootCertExists() will be True
    if not FC.CertMaker.rootCertExists():   
        FC.CertMaker.createRootCert()
        FC.CertMaker.trustRootCert() 
        
        cert = FC.FiddlerApplication.Prefs.GetStringPref("fiddler.certmaker.bc.cert", None)
        key = FC.FiddlerApplication.Prefs.GetStringPref("fiddler.certmaker.bc.key", None)
        certificate = {'key':key,'cert':cert}
        with open('cert', 'wb') as handle:
            pickle.dump(certificate, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
    else:
        print "\n!! Root Certificate Exists **"

import io
import pycurl
import json

def asr(filename):
    """
    http://curl.haxx.se/libcurl/c/curl_easy_setopt.html
    http://code.activestate.com/recipes/576422-python-http-post-binary-file-upload-with-pycurl/
    http://pycurl.cvs.sourceforge.net/pycurl/pycurl/tests/test_post2.py?view=markup
    """
    url = 'http://127.0.0.1:7777/filemode/?productcode=DEMO&transactionid=0&language=kor'
    c = pycurl.Curl()
    #c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.URL, url)
    fout = io.BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, fout.write)

    c.setopt(c.HTTPPOST, [
                ("uploadfieldname",
                 (c.FORM_FILE, filename,
                  c.FORM_CONTENTTYPE, "audio/wav"))])
    c.perform()
    response_code = c.getinfo(pycurl.RESPONSE_CODE)
    if response_code == 200 :
        response_data = fout.getvalue().decode('UTF-8')
        res = json.loads(response_data, encoding='UTF-8')
        if res['rcode'] <= 0:
            out = 'fail'
        else:
            out = res['result']
    else:
        out = 'fail'
    c.close()
    return out


if __name__ == '__main__':
    f = open('testlist.txt', 'r')
    l = f.read()
    print(l)
    l = ['.\\speaker_recog\\ceslea_data' + x for x in l.split('\n') if x != '']
    f.close()
    print(l)
    #f = open('.\\speaker_recog\\ceslea_data\\ami\\ami.wav', 'rb')
    #f.read()
    #f.close()
    ll = [asr(x) for x in l]
    print(list(set(ll)))
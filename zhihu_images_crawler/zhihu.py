'''
web crawler for zhihu question page
'''
import urllib.request
import os
import re
import json

def downloadPage():
    global url, imgDir, pageIndex
    req_header = {
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    req = urllib.request.Request(url, headers=req_header)
    print('Downloading page', pageIndex, '...')
    data = ''
    try:
        data = urllib.request.urlopen(req, timeout=5).read()
    except:
        print('connect timeout...')
        return -1

    if data != '':
        with open(imgDir + '/webpageContent_' + str(pageIndex) + '.json', 'wb') as fs:
            fs.write(data)
    print('Page', pageIndex, 'downloaded.')
    return 0


def downloadImg():
    global url, imgDir, _id, pageIndex, fail
    with open(imgDir + '/webpageContent_' + str(pageIndex) + '.json', 'rb') as fs:
        webpageContent = fs.read()
    reg = r' src="(https.+?\.(?:png|jpg|gif))"'
    img_reg = re.compile(reg)
    imgUrlList = map(lambda x: re.findall(img_reg, x['content']),
                     json.loads(webpageContent.decode('utf-8'))['data'])
    imgIndex = 0  # image per page index
    for imgUrls in list(imgUrlList):
        for imgUrl in imgUrls:
            suffix = imgUrl[-3:]
            try:
                urllib.request.urlretrieve(
                    imgUrl, imgDir + '/%s.%s' % (str(_id) + '_' + str(pageIndex) + '_' + str(imgIndex), suffix))
                print('>>>Download Image Success: imgId:', _id, 'pageIndex:',
                      pageIndex, 'imageIndex:', imgIndex)
            except Exception as e:
                print('>>>Download Image Error: imgId:', _id, 'pageIndex:', pageIndex,
                      'imageIndex:', imgIndex, 'reason:',  e)
                fail['failNum'] += 1
                fail['imgIndex'].append(
                    {'index': str(_id) + '_' + str(pageIndex) + '_' + str(imgIndex), 'reason': e})
            finally:
                imgIndex += 1
                _id += 1

flag = False
pageIndex = 0  # page index
_id = 0  # img index
fail = {'failNum': 0, 'imgIndex': []}
url = "https://www.zhihu.com/api/v4/questions/" + input('Please input Zhihu question ID:') + "/answers?include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B*%5D.topics&offset=&limit=3&sort_by=default&platform=desktop"
imgDir = 'images'
dirList = [x.lower() for x in os.listdir('.') if os.path.isdir(x)]
if imgDir not in dirList + ['']:
    os.mkdir(imgDir)
while downloadPage() != -1:
    downloadImg()
    with open(os.path.join(imgDir, 'webpageContent_' + str(pageIndex) + '.json'), 'rb') as fs:
        webpageContentDict = json.loads(fs.read())
    if not webpageContentDict['paging']['is_end']:
        pageIndex += 1
        url = webpageContentDict['paging']['next']
    else:
        flag = True
        break

print('---------Job done.---------')
print('Fail Number:', fail['failNum'])
print('Fail Image Index:')
for x in fail['imgIndex']:
    print(x)
input('Press any key to continue...')

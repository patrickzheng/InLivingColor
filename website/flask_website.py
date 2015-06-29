from flask import Flask, request, send_from_directory, render_template, url_for

app = Flask(__name__)

from flask import Response


from cassandra.cluster import Cluster

# Connect to keyspace 'inlivingcolor'
cluster = Cluster()
session = cluster.connect('inlivingcolor')

from os.path import abspath, dirname
# app.root_path = abspath(dirname(__file__))


# @app.route("/")
# @app.route("/index")
# def hello():
#     return "Hello World!"
# from _configuration import *
# from cassandra.cluster import Cluster

from us_counties import *
# Connect to keyspace 'inlivingcolor'
# cluster = Cluster()
# session = cluster.connect('inlivingcolor')


def GetCountsForHighMaps():
    resp = session.execute("SELECT region,county,count FROM allcountsbatch WHERE granularity='county/all' AND country='United States'")

    output = []
    for row in resp:
        if row[0] == '_' or row[1] == '_':
            continue

        countyname = "%s, %s" % (row[1], us_state_abbrev[row[0]])
        # baldwin, al

        try:
            output += [dict(name=countyname,
                           code=codesbycounty[countyname.lower()],
                           value=row[2],
                          )]

        except:
            # These don't have a code that I know of:
            # Kalawao, HI
            # Brooklyn, NY
            # Staten Island, NY
            pass

    return output

highmapsdata = GetCountsForHighMaps()




@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@app.route('/collageplus/<path:path>')
def send_collageplus(path):
    return send_from_directory('collageplus', path)

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def root():
    # return url_for('static',filename='index.html')
    # return app.route_path
    return render_template("inlivingcolor.html", highmapsdata=highmapsdata)



@app.route("/images/<photoid>.jpg")
def images(photoid):
    # return 'hi'
    #     # import base64
    try:
        rows = session.execute("SELECT thumbjpg FROM thumbnails WHERE photoid='%s'"%(photoid))

        jpgdata = rows[0][0]
        return Response(jpgdata, mimetype='image/jpeg')

    except:
        return "404"



@app.route("/C1/<RRGGBB>/<P1>")
def C1(RRGGBB, P1):

    r = int(RRGGBB[:2], 16)
    g = int(RRGGBB[2:4], 16)
    b = int(RRGGBB[4:6], 16)

    tol = 30

    try:
        rows = session.execute("""
            SELECT photoid FROM bigindex WHERE lucene='{
            query : {type:"boolean", must:[
                        {type:"range", field:"c1c1r", lower:"%d", upper:"%d"   },
                        {type:"range", field:"c1c1g", lower:"%d", upper:"%d"   },
                        {type:"range", field:"c1c1b", lower:"%d", upper:"%d"   }
                        ]}
            }' limit 30;"""%(r-tol, r+tol, g-tol, g+tol, b-tol, b+tol))

        return str([row[0] for row in rows])

    except:
        return "404"

from datetime import datetime
from elasticsearch import Elasticsearch

# by default we connect to localhost:9200
es = Elasticsearch()



@app.route("/colorsearch/(<r1>,<g1>,<b1>,<p1>)(<r2>,<g2>,<b2>,<p2>)(<r3>,<g3>,<b3>,<p3>)/<tol>")
def colorsearch(r1,g1,b1,p1,r2,g2,b2,p2,r3,g3,b3,p3,tol):


    RGBP1 = (int(r1), int(g1), int(b1), int(p1))
    RGBP2 = (int(r2), int(g2), int(b2), int(p2))
    RGBP3 = (int(r3), int(g3), int(b3), int(p3))
    tol = int(tol)


    Ps, RGBPs_orig = zip(*sorted(((int(p1), RGBP1), (int(p2), RGBP2), (int(p3), RGBP3)), reverse=True))

    # tol = 40

    # if p1 < p2:
    #     RGBP2, RGBP1 = RGBP1, RGBP2
        # r2, g2, b2, p2, r1, g1, b1, p1 = r1, g1, b1, p1, r2, g2, b2, p2


    ######################
    # construct query string
    #
# {"range":{"c2c1r":{"gte":60,"lte":140}}},{"range":{"c2c1g":{"gte":30,"lte":110}}},{"range":{"c2c1b":{"gte":160,"lte":240}}},{"range":{"c2p1":{"gte":40,"lte":120}}},{"range":{"c2c2r":{"gte":110,"lte":190}}},{"range":{"c2c2g":{"gte":0,"lte":80}}},{"range":{"c2c2b":{"gte":-20,"lte":60}}}
    from itertools import permutations

    for RGBPs in permutations(RGBPs_orig):
        output = ""
        N = len(RGBPs)
        for i,RGBP in enumerate(RGBPs):
            colortemp = '{"range":{"c%dc%d%s":{"gte":%d,"lte":%d}}},'
            probtemp = '{"range":{"c%dp%d":{"gte":%d,"lte":%d}}},'

            for j,color in enumerate(['r','g','b']):
                # output += colortemp % (N,i+1,color,RGBP[j]-tol,RGBP[j]+tol)
                if RGBP[3] > 0:
                    output += colortemp % (N,i+1,color,RGBP[j]-tol,RGBP[j]+tol)
                else: # if the color is not included, then let it match anything
                    output += colortemp % (N,i+1,color,-30,286)

            if i < N-1:
                output += probtemp % (N,i+1,RGBP[3]-2*tol,RGBP[3]+2*tol)
        output = output[:-1]


        query = '{"fields":["photoid","thumbw","thumbh","url"],"query":{"bool":{"must": [%s]}}}'%output

        rsp = es.search(index='inlivingcolor', doc_type='colorcluster', size=100, body=query)

        pixinfos = [dict(photoid=item['fields']['photoid'][0],
                  width=100*item['fields']['thumbw'][0]/item['fields']['thumbh'][0],
                  height=100,
                  url=item['fields']['url'][0],
                 ) for item in rsp['hits']['hits']]
        output = "".join(['<a href="{url}"><img src="https://s3-us-west-1.amazonaws.com/inlivingcolor/geotagged/thumbs/{photoid}.jpg" width={width} height={height}></a>'.format(**pixinfo) for pixinfo in pixinfos])
        # output =  "".join(['<img src="https://s3-us-west-1.amazonaws.com/inlivingcolor/geotagged/thumbs/{photoid}.jpg" width={width} height={height}>'.format(**pixinfo) for pixinfo in pixinfos])

    output += '<script type="text/javascript"><!-- collage(); //--></script>'
    return output



@app.route("/colorsearch/(<r1>,<g1>,<b1>,<p1>)(<r2>,<g2>,<b2>,<p2>)/<tol>")
def colorsearch2(r1,g1,b1,p1,r2,g2,b2,p2,tol):


    RGBP1 = (int(r1), int(g1), int(b1), int(p1))
    RGBP2 = (int(r2), int(g2), int(b2), int(p2))
    tol = int(tol)


    Ps, RGBPs_orig = zip(*sorted(((int(p1), RGBP1), (int(p2), RGBP2)), reverse=True))

    # tol = 40

    # if p1 < p2:
    #     RGBP2, RGBP1 = RGBP1, RGBP2
        # r2, g2, b2, p2, r1, g1, b1, p1 = r1, g1, b1, p1, r2, g2, b2, p2


    ######################
    # construct query string
    #
# {"range":{"c2c1r":{"gte":60,"lte":140}}},{"range":{"c2c1g":{"gte":30,"lte":110}}},{"range":{"c2c1b":{"gte":160,"lte":240}}},{"range":{"c2p1":{"gte":40,"lte":120}}},{"range":{"c2c2r":{"gte":110,"lte":190}}},{"range":{"c2c2g":{"gte":0,"lte":80}}},{"range":{"c2c2b":{"gte":-20,"lte":60}}}
    from itertools import permutations

    for RGBPs in permutations(RGBPs_orig):
        output = ""
        N = len(RGBPs)
        for i,RGBP in enumerate(RGBPs):
            colortemp = '{"range":{"c%dc%d%s":{"gte":%d,"lte":%d}}},'
            probtemp = '{"range":{"c%dp%d":{"gte":%d,"lte":%d}}},'

            for j,color in enumerate(['r','g','b']):
                # output += colortemp % (N,i+1,color,RGBP[j]-tol,RGBP[j]+tol)
                if RGBP[3] > 0:
                    output += colortemp % (N,i+1,color,RGBP[j]-tol,RGBP[j]+tol)
                else: # if the color is not included, then let it match anything
                    output += colortemp % (N,i+1,color,-30,286)

            if i < N-1:
                output += probtemp % (N,i+1,RGBP[3]-2*tol,RGBP[3]+2*tol)
        output = output[:-1]


        query = '{"fields":["photoid","thumbw","thumbh","url"],"query":{"bool":{"must": [%s]}}}'%output

        rsp = es.search(index='inlivingcolor', doc_type='colorcluster', size=100, body=query)

        pixinfos = [dict(photoid=item['fields']['photoid'][0],
                  width=100*item['fields']['thumbw'][0]/item['fields']['thumbh'][0],
                  height=100,
                  url=item['fields']['url'][0],
                 ) for item in rsp['hits']['hits']]
        output = "".join(['<a href="{url}"><img src="https://s3-us-west-1.amazonaws.com/inlivingcolor/geotagged/thumbs/{photoid}.jpg" width={width} height={height}></a>'.format(**pixinfo) for pixinfo in pixinfos])
        # output =  "".join(['<img src="https://s3-us-west-1.amazonaws.com/inlivingcolor/geotagged/thumbs/{photoid}.jpg" width={width} height={height}>'.format(**pixinfo) for pixinfo in pixinfos])

    output += '<script type="text/javascript"><!-- collage(); //--></script>'
    return output

@app.route("/colorsearch/(<r1>,<g1>,<b1>,<p1>)(<r2>,<g2>,<b2>,<p2>)/<tol>/<text>")
def colorsearch2text(r1,g1,b1,p1,r2,g2,b2,p2,tol,text):


    RGBP1 = (int(r1), int(g1), int(b1), int(p1))
    RGBP2 = (int(r2), int(g2), int(b2), int(p2))
    tol = int(tol)


    Ps, RGBPs_orig = zip(*sorted(((int(p1), RGBP1), (int(p2), RGBP2)), reverse=True))

    # tol = 40

    # if p1 < p2:
    #     RGBP2, RGBP1 = RGBP1, RGBP2
        # r2, g2, b2, p2, r1, g1, b1, p1 = r1, g1, b1, p1, r2, g2, b2, p2


    ######################
    # construct query string
    #
# {"range":{"c2c1r":{"gte":60,"lte":140}}},{"range":{"c2c1g":{"gte":30,"lte":110}}},{"range":{"c2c1b":{"gte":160,"lte":240}}},{"range":{"c2p1":{"gte":40,"lte":120}}},{"range":{"c2c2r":{"gte":110,"lte":190}}},{"range":{"c2c2g":{"gte":0,"lte":80}}},{"range":{"c2c2b":{"gte":-20,"lte":60}}}
    from itertools import permutations

    for RGBPs in permutations(RGBPs_orig):
        output = ""
        N = len(RGBPs)
        for i,RGBP in enumerate(RGBPs):
            colortemp = '{"range":{"c%dc%d%s":{"gte":%d,"lte":%d}}},'
            probtemp = '{"range":{"c%dp%d":{"gte":%d,"lte":%d}}},'

            for j,color in enumerate(['r','g','b']):
                # output += colortemp % (N,i+1,color,RGBP[j]-tol,RGBP[j]+tol)
                if RGBP[3] > 0:
                    output += colortemp % (N,i+1,color,RGBP[j]-tol,RGBP[j]+tol)
                else: # if the color is not included, then let it match anything
                    output += colortemp % (N,i+1,color,-30,286)

            if i < N-1:
                output += probtemp % (N,i+1,RGBP[3]-2*tol,RGBP[3]+2*tol)
        output = output[:-1]


        query = '{"fields":["photoid","thumbw","thumbh","url"],"query":{"bool":{"must": [%s]}}}'%output

        rsp = es.search(index='inlivingcolor', doc_type='colorcluster', size=100, body=query)

        pixinfos = [dict(photoid=item['fields']['photoid'][0],
                  width=100*item['fields']['thumbw'][0]/item['fields']['thumbh'][0],
                  height=100,
                  url=item['fields']['url'][0],
                 ) for item in rsp['hits']['hits']]
        output = "".join(['<a href="{url}"><img src="https://s3-us-west-1.amazonaws.com/inlivingcolor/geotagged/thumbs/{photoid}.jpg" width={width} height={height}></a>'.format(**pixinfo) for pixinfo in pixinfos])
        # output =  "".join(['<img src="https://s3-us-west-1.amazonaws.com/inlivingcolor/geotagged/thumbs/{photoid}.jpg" width={width} height={height}>'.format(**pixinfo) for pixinfo in pixinfos])

    output += '<script type="text/javascript"><!-- collage(); //--></script>'
    return output




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)


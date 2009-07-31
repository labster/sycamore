# -*- coding: utf-8 -*-
"""
    Sycamore - Overview map display macro.

    @copyright: 2008 Alex Mandel <tech@wildintellect.com>
    @copyright: 2009 Brent Laabs <bslaabs@gmail.com>
    @license: GNU GPL, see COPYING for details.
"""
# Imports
import urllib
import socket

from Sycamore import config
from Sycamore import wikiutil
from Sycamore import wikidb
from Sycamore import caching

from Sycamore.Page import Page
from Sycamore.action import Files

SOCKET_TIMEOUT = 5 # to prevent us from hanging if google, osm or other maps source hangs

socket.setdefaulttimeout(SOCKET_TIMEOUT)

def execute(macro, args, formatter):
    """
    Executes the [[Map]] macro.
    Displays an overview map using OpenLayers
    """
    request = macro.request
    script_loc = ""
    #GoogleMaps API reference
    gmaps_api_key = request.config.gmaps_api_key or config.gmaps_api_key
    #script_loc = ('<script src="http://maps.google.com/maps?file=api&v=2&key=%s" '
    #       'type="text/javascript"></script>' % gmaps_api_key)
    #script_loc += ('<script src="%s/wiki/gmap.js" type="text/javascript"></script>' % config.web_dir)
    
    #OpenLayers reference
    script_loc += ('<script type="text/javascript" src="http://openlayers.org/api/OpenLayers.js"></script>')
    script_loc +=('<script src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>')

    #base map
    map_html= mapJS(request)
   #add points
   #map_html += plotpoints(macro)
    map_html += plotpoints2(macro, prep_geojson(macro))
    map_html += checkboxJS()
    map_html += """
    /**
         * Function: addMarker
         * Add a new marker to the markers layer given the following lonlat, 
         *     popupClass, and popup contents HTML. Also allow specifying 
         *     whether or not to give the popup a close box.
         * 
         * Parameters:
         * ll - {<OpenLayers.LonLat>} Where to place the marker
         * popupClass - {<OpenLayers.Class>} Which class of popup to bring up 
         *     when the marker is clicked.
         * popupContentHTML - {String} What to put in the popup
         * closeBox - {Boolean} Should popup have a close box?
         * overflow - {Boolean} Let the popup overflow scrollbars?
         */
        function addMarker(lat, lon, popupClass, popupContentHTML, field, closeBox, overflow) {

            var ll = new OpenLayers.LonLat(lat,lon).transform(map.displayProjection,map.projection);

            var feature = new OpenLayers.Feature(markers[field], ll); 
            feature.closeBox = closeBox;
            feature.popupClass = popupClass;
            feature.data.popupContentHTML = popupContentHTML;
            feature.data.overflow = (overflow) ? "auto" : "hidden";
            feature.data.icon = icons[field].clone();

            // takes the attributes of feature to create a point
            var marker = feature.createMarker();

            var markerClick = function (evt) {
                if (this.popup == null) {
                    this.popup = this.createPopup(this.closeBox);
                    map.addPopup(this.popup);
                    this.popup.show();
                } else {
                    this.popup.toggle();
                }
                currentPopup = this.popup;
                OpenLayers.Event.stop(evt);
            };
            marker.events.register("mousedown", feature, markerClick);

            markers[field].addMarker(marker);
        };
//]]>
        window.onload = init;
        </script>"""

    # Start Assembling the map legend
    # TODO : Layers doesn't actually work, eventually
    ######   fetch layers from map config table

    marker_table = ''
    i = 0
    while i<20:
        if i<5: chkd = ' checked'
        else: chkd = ''
        if request.config.map_names[i]:
            marker_table += '<tr><td><input type="checkbox" name="i%s" ' % i + \
                            'onclick="switchvis(%s);"%s></td>' % (i,chkd) + \
                            '<td><img src="%s"></td><td>%s</td></tr>' % (marker_url(request,
                            'marker%s.png' % i), request.config.map_names[i])
        i = i + 1
    

    # String to create the html for the map's legend
    legend_html = """
        <div class="maptabs">
                <a href="#places" class="maptab">Places</a>
                <a href="#legend" class="maptab">Legend</a>
                <a href="#layers" class="maptab">Layers</a>
        </div>
        <div class="maptabcontents">
                <div class="maptabcontent" id="places">
                <form id="classes"><table class="mapplaces">
                """
    legend_html += marker_table
    legend_html += """
                </table></form>
                </div>
                
                <div class="maptabcontent" id="legend">
                        <img src="http://www.openstreetmap.org/images/keymapnik13.png">
                </div>
                
                <div class="maptabcontent" id="layers">
                        <h2>Layers</h2>
                        <form id="layersform"><table class="mapplaces">
                        <tr><td><input type="radio" name="wikilayers" value="mapnik" checked
                                 onClick="map.setBaseLayer(mapnik);"></td><td>Open Street Map</td></tr>
                        <tr><td><input type="radio" name="wikilayers" value="boogle"
                                 onClick="map.setBaseLayer(boogle);"></td><td>Google Maps -
                                 Airphoto/Street overlay</td></tr>
                        </table></form>
                        <p>%s</p>
                        <p>%s</p>
                </div>
        </div>
    """ % (prep_geojson(macro)[19], macro.request.relative_dir)



    # Write the html+js string to print out the map and legend
    html = ('<html><head>%s</head>'
            '<body style="padding:0;margin:0;">'
            '<div id="map" class="full">'
            '</div>%s</body></html>' % (script_loc, map_html))
    html += ('<div class="maplegend">%s</div>' % (legend_html))
    request.http_headers()
    request.write(html)
    return ''

###########################################################


def mapJS(request):
    """
    Create a string containing javascript for google map
    page = the page object
    place = place object of center of map
    nearby = dictionary of nearby places
    """

    jtags = "["
    for tag in request.config.map_tags:
        jtags += '"%s",' % tag
    jtags+= '"allother"]'

    out = """ 
    <script type="text/javascript">
//<![CDATA[
var map,markers;
var currentPopup;
atags = %s;

function init() {
    map = new OpenLayers.Map('map',
        { maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
            numZoomLevels: 19,
            maxResolution: 156543.0399,
            units: 'm',
            projection: new OpenLayers.Projection("EPSG:900913"),
            displayProjection: new OpenLayers.Projection("EPSG:4326"),
            controls: [
                      new OpenLayers.Control.LayerSwitcher(),
                     new OpenLayers.Control.PanZoomBar(),
                     new OpenLayers.Control.MouseToolbar(),
                     new OpenLayers.Control.Permalink(),
                     new OpenLayers.Control.ScaleLine(),
                     new OpenLayers.Control.Permalink('permalink'),
                     new OpenLayers.Control.MousePosition(),
                     // new OpenLayers.Control.OverviewMap(),
                     new OpenLayers.Control.KeyboardDefaults()
                    ]
            });
var mapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik (updated weekly)");
map.addLayers([mapnik]);

markers = []; i=0;
for (i=0; i<20; i++) {
    markers.push(new OpenLayers.Layer.Markers(name=atags[i]));
    map.addLayer(markers[i]);
    if (i>5) { markers[i].display(0); }
}



var lonLat = new OpenLayers.LonLat(%s, %s).transform(map.displayProjection,  map.projection);

map.setCenter(lonLat, 12);
addMarkers();
};
""" % ( jtags, request.config.longitude, request.config.latitude )

    return out

###########################################################

def plotpoints(macro):
    cursor = macro.request.cursor
    #TODO: How should we limit the number of points returned on the full map?
    cursor.execute('SELECT pagename_propercased,x,y FROM mappoints WHERE wiki_id=%s' % str(macro.request.config.wiki_id))
    
    rows = cursor.fetchall()
    if rows: 
        lis = []
        fmarkersJS = """
function addMarkers(){
    var ll, popupHTML;
    var popupClass = OpenLayers.Popup.FramedCloud;
"""
        fmarkersJS += write_icons(macro.request)
        
        for row in rows:
            lis.append({'name':row[0],'longitude':row[1],'latitude':row[2]})
            pointcode = markerJS(row[2], row[1], row[0])
            fmarkersJS += pointcode + "\n"
        
        fmarkersJS += """};
        """ 
        return fmarkersJS
    return ''

###########################################################

def plotpoints2(macro, json):
    """
    New and improved
    """

    markersJS = """
    function addMarkers(){
      var ll, popupHTML;
      var popupClass = OpenLayers.Popup.FramedCloud;
      features = [];
    """

    markersJS += write_icons(macro.request)

    for feature in json:
        markersJS += 'features.push(%s);\n' % feature

    markersJS += """
     for (i=0; i<20; i++) {
       for each (point in features[i].features) {
         popupContentHTML = '<a href="' + point.properties.url + '">' + point.id  +  "</a>";
         addMarker(Number(point.geometry.coordinates[0]),Number(point.geometry.coordinates[1]),popupClass,popupContentHTML, i,true);       
       } }   
    };"""

#         popupContentHTML = '<a href="' + point["properties"]["url"] + '">' + point["id"]  +  "</a>";


    return markersJS


###########################################################

def write_icons(request):
    """
    Gets the marker settings from the wiki config and writes them as a javascript syntax array
    all wrapped up in a python string.
    """
    jsout = 'icons = ['

    i = 0
    while i < 20:
        jsout += 'new OpenLayers.Icon("%s", ' % marker_url(request, "marker%s.png" % i)
        jsout += 'new OpenLayers.Size(%s, %s), ' % (request.config.map_marker_sizes[i][0], request.config.map_marker_sizes[i][1])
        jsout += 'new OpenLayers.Pixel('
        if request.config.map_markers[i] in [0, 3, 6]:
            jsout += '0, '
        elif request.config.map_markers[i] in [1, 4, 7]:
            jsout += '-%s/2, ' % request.config.map_marker_sizes[i][0]
        else:
            jsout += '-%s, ' % request.config.map_marker_sizes[i][0]
        if request.config.map_markers[i] in [0, 1, 2]:
            jsout += '0)'
        elif request.config.map_markers[i] in [3, 4, 5]:
            jsout += '-%s/2)' % request.config.map_marker_sizes[i][1]
        else:
            jsout += '-%s)' % request.config.map_marker_sizes[i][1]
        jsout += "), "
        i += 1
    jsout += '];'
    return jsout

###########################################################

def prep_geojson(macro):
    """
    Compiles teh GeoJSON representation of our map database.
    Probably move this somewhere else eventually
    Returns an array of json objects, one for each tag
    TODO: page security settings
    """
    import geojson
    feature_classes = [ [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [], [] ]
    json = []
    cursor = macro.request.cursor
    
    cursor.execute('SELECT pagename_propercased, x, y, tag FROM mappoints WHERE wiki_id=%s' % str(macro.request.config.wiki_id))
    rows = cursor.fetchall()
    if not rows: return ''  #FIX: this causes stack trace if nothing's in the map table
    arbid = 0 #arbitrary id for GeoJSON format
    for row in rows:
        (pagename, longitude, latitude, tag) = row
        i = 0
        written = False
        while i < 19:
            if tag == macro.request.config.map_tags[i]:
                pass
                #write geojson
                feature_classes[i].append(geojson.Feature(geometry=geojson.Point(coordinates=[latitude, longitude]),
                    id=pagename, properties={'tag': tag, 'url': (macro.request.relative_dir + '/' + pagename)}) )
                written = True
            i = i + 1
        if not written:
            #write to other
            feature_classes[19].append(geojson.Feature(geometry=geojson.Point(coordinates=[latitude, longitude]),
                id=pagename, properties={'tag': tag, 'url': (macro.request.relative_dir + '/' + pagename)}) )
        arbid += 1

    for group in feature_classes:
        json.append( geojson.dumps(
            geojson.FeatureCollection(features=group, properties={'projection':'EPSG:4326'}) ))
    return json       
        



###########################################################


def markerJS(lat, lon, name):
    """
    Find locations and populate a JS function to add them one by one with their proper links and names. 
    Need to find a better option like loading the layer as text, GeoRSS etc to save load time and reduce server load.
    """
    #replace apostrophes with escape char apostrophe so it doesn't ruin the javascript
    chrsub = unichr(0x5C)+unichr(0x27)
    newname = name.replace("'",chrsub)
    
    """
    html = ( "var ll = new OpenLayers.LonLat(%s,%s).transform(map.displayProjection,map.projection);"
                "popupClass = OpenLayers.Popup.FramedCloud;"
                "popupContentHTML = '<a href=\"%s\">%s</a>';"
                "addMarker(ll,popupClass,popupContentHTML,true);" % (lat, lon, newname, newname))
    """

    html = (    "popupContentHTML = '<a href=\"%s\">%s</a>';"
                "addMarker(%s,%s,popupClass,popupContentHTML,true);" % (newname, newname, lat, lon))

    return html

###########################################################

def checkboxJS():
    """
    Javascript function to make the checkboxen work.
    """

    return """
boxes = [ 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]
function switchvis(i) {
     boxes[i] = -1*boxes[i]+1;
     markers[i].display(boxes[i]);
}
"""




###########################################################


def marker_url(request, markername):
    """
    Gets the correct URL for markers stored on your local wiki_settings/map page
    """

    return Files.getAttachUrl("%s/%s" % (config.wiki_settings_page,
                      config.wiki_settings_page_map), markername, request)


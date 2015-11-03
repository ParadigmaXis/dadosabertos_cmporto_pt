"""
from geoserver_integration import upload_shapefile_resource
upload_shapefile_resource('http://poseidon/geoserver', '123456', '../../Downloads/2015-7-31-16-50-29-718__Cont_troco_CAOP2015.zip')
"""
from tempfile import mkdtemp
from zipfile import is_zipfile, BadZipfile, ZipFile, ZIP_STORED, ZIP_DEFLATED
import json, os, requests

def upload_shapefile_resource(geoserver_url, geoserver_user, geoserver_password, resource_uuid, zip_filename):
    # open zip file
    zipfile = ZipFile(zip_filename, mode = 'r')

    # obtain list of files inside and assert there is only one .shp file
    namelist = zipfile.namelist()
    shapefiles = [n for n in namelist if n.lower().endswith('.shp')]
    if len(shapefiles) != 1:
        raise Exception('Zip does not contain one .shp file.')

    # extract zip file contents to a temp dir
    tempdir = mkdtemp()
    zipfile.extractall(tempdir)

    # create a zip file with file names adjusted to naming convention
    shapefile = shapefiles[0][:-4]
    tempzipfilename = '{0}/shp-{1}.zip'.format(tempdir, resource_uuid)
    tempzipfile = ZipFile(tempzipfilename, mode = 'w', compression = ZIP_DEFLATED)

    for entry in namelist:
        entryfilename = '{0}/{1}'.format(tempdir, entry)
        if entry.startswith(shapefile):
            tempzipfile.write(entryfilename, arcname = 'shp-{0}{1}'.format(resource_uuid, entry[len(shapefile):]))
        else:
            tempzipfile.write(entryfilename, arcname = entry)
    tempzipfile.close()
    zipfile.close()

    AUTH = (geoserver_user, geoserver_password)

    # check if workspace already exists
    response = requests.get('{0}/rest/workspaces'.format(geoserver_url), auth=AUTH, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        raise Exception(response.text)

    def workspace_exists(content, resource_uuid):
        if not isinstance(content, dict):
            return False
        workspaces = content.get('workspaces', {}) or {}
        workspacelist = workspaces.get('workspace', []) or []
        return len([w for w in workspacelist if w['name'] == 'shp-{0}'.format(resource_uuid)]) > 0

    if not workspace_exists(response.json(), resource_uuid):
        # create workspace with the correct naming convention
        response = requests.post('{0}/rest/workspaces'.format(geoserver_url), data=json.dumps({'workspace': {'name': 'shp-{0}'.format(resource_uuid)}}), auth=AUTH, headers={'Content-Type': 'application/json'})
        print response, response.text
        params = {}
    else:
        print 'Workspace already exists'
        params = {'update': 'overwrite'}
    # upload the zip file to the server
    # this creates the datastore and the layer with the correct naming convention
    # or overwrites the datastore
    response = requests.put('{0}/rest/workspaces/shp-{1}/datastores/shp-{1}/file.shp'.format(geoserver_url, resource_uuid), params=params, data=open(tempzipfilename, 'rb'), auth=AUTH, headers={'Content-Type': 'application/zip'})
    print response, response.text

    # remove the temp dir and its contents
    for root, dirs, files in os.walk(tempdir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(tempdir)

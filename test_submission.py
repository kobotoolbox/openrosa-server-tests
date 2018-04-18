#SUBMISSION_ENDPOINT = 'https://kc.du.kbtdev.org/jnm/submission'
SUBMISSION_ENDPOINT = 'http://172.17.0.1:8001/straw/submission'
SUCCESS_STATUS_CODE = 201
DUPLICATE_STATUS_CODE = 202

# Assumption: you have the following XForm
xform_xml = '''
<?xml version="1.0" encoding="utf-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>several pic</h:title>
    <model>
      <instance>
        <amwV6jGLBYNfcbJYpdx8Gb id="amwV6jGLBYNfcbJYpdx8Gb" version="vxhtSrJdxTeZ9jN46sz97J">
          <formhub>
            <uuid/>
          </formhub>
          <start/>
          <end/>
          <vidja/>
          <group_wx5aj87 jr:template="">
            <piccy/>
          </group_wx5aj87>
          <__version__/>
          <meta>
            <instanceID/>
          </meta>
        </amwV6jGLBYNfcbJYpdx8Gb>
      </instance>
      <bind jr:preload="timestamp" jr:preloadParams="start" nodeset="/amwV6jGLBYNfcbJYpdx8Gb/start" type="dateTime"/>
      <bind jr:preload="timestamp" jr:preloadParams="end" nodeset="/amwV6jGLBYNfcbJYpdx8Gb/end" type="dateTime"/>
      <bind nodeset="/amwV6jGLBYNfcbJYpdx8Gb/vidja" required="false()" type="binary"/>
      <bind nodeset="/amwV6jGLBYNfcbJYpdx8Gb/group_wx5aj87/piccy" required="false()" type="binary"/>
      <bind calculate="'vxhtSrJdxTeZ9jN46sz97J'" nodeset="/amwV6jGLBYNfcbJYpdx8Gb/__version__" type="string"/>
      <bind calculate="concat('uuid:', uuid())" nodeset="/amwV6jGLBYNfcbJYpdx8Gb/meta/instanceID" readonly="true()" type="string"/>
      <bind calculate="'75a131543caa470d95f90b0bbcc28c12'" nodeset="/amwV6jGLBYNfcbJYpdx8Gb/formhub/uuid" type="string"/>
    </model>
  </h:head>
  <h:body>
    <upload mediatype="video/*" ref="/amwV6jGLBYNfcbJYpdx8Gb/vidja">
      <label>vidja</label>
    </upload>
    <group ref="/amwV6jGLBYNfcbJYpdx8Gb/group_wx5aj87">
      <label>Group</label>
      <repeat nodeset="/amwV6jGLBYNfcbJYpdx8Gb/group_wx5aj87">
        <upload mediatype="image/*" ref="/amwV6jGLBYNfcbJYpdx8Gb/group_wx5aj87/piccy">
          <label>piccy</label>
        </upload>
      </repeat>
    </group>
  </h:body>
</h:html>
'''

# An example submission (instance) would look like:
instance_example_xml = '''
<?xml version="1.0"?>
<amwV6jGLBYNfcbJYpdx8Gb xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:orx="http://openrosa.org/xforms" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" id="amwV6jGLBYNfcbJYpdx8Gb" version="vxhtSrJdxTeZ9jN46sz97J">
<formhub>
    <uuid>75a131543caa470d95f90b0bbcc28c12</uuid>
</formhub>
<start>2018-04-17T22:59:27.493-04</start>
<end>2018-04-17T23:00:06.187-04</end>
<vidja>1524020384170.mp4</vidja>
<group_wx5aj87>
    <piccy>1524020399598.jpg</piccy>
</group_wx5aj87>
<__version__>vxhtSrJdxTeZ9jN46sz97J</__version__>
<meta>
    <instanceID>uuid:d12a59ba-b602-473e-8604-a9e53d44a5bf</instanceID>
</meta>
</amwV6jGLBYNfcbJYpdx8Gb>
'''

# XPaths of things in the instance that we'd like to change:
instance_xpaths = {
    'instance_id': '/amwV6jGLBYNfcbJYpdx8Gb/meta/instanceID',
    'start': '/amwV6jGLBYNfcbJYpdx8Gb/start',
    'end': '/amwV6jGLBYNfcbJYpdx8Gb/end',
    'video': '/amwV6jGLBYNfcbJYpdx8Gb/vidja',
    'image_in_repeating_group': '/amwV6jGLBYNfcbJYpdx8Gb/group_wx5aj87/piccy',
}

### End of stuff that should probably be in a fixture

import os
import uuid
import getpass
import tzlocal
import datetime
import requests
from lxml import etree
from StringIO import StringIO
from tempfile import NamedTemporaryFile

# Maybe useful later for developing tests that read back submission data?
'''
_username = None
_password = None

def get_username():
    global _username
    if _username is None:
        _username = raw_input('Please enter your username: ')
    return _username

def get_password():
    global _password
    if _password is None:
        _password = getpass.getpass('Please enter your password: ')
    return _password
'''

def localnow():
 return tzlocal.get_localzone().localize(datetime.datetime.now())

def construct_instance_xml(instance_id=None,
                       start=None,
                       end=None,
                       video=None,
                       images=None):
    if instance_id is None:
        instance_id = 'uuid:' + str(uuid.uuid4())
    if end is None:
        end = localnow().isoformat()
    if start is None:
        start = (localnow() - datetime.timedelta(minutes=1)).isoformat()
    if isinstance(images, basestring):
        images = [images]
    elif images is None:
        images = []

    tree = etree.fromstring(instance_example_xml.strip())
    def get_element(arbitrary_name):
        return tree.xpath(instance_xpaths[arbitrary_name])[0]

    get_element('instance_id').text = instance_id
    get_element('start').text = start
    get_element('end').text = end
    if video is None:
        tree.remove(get_element('video'))
    else:
        get_element('video').text = video

    image_element = get_element('image_in_repeating_group')
    image_group_element = image_element.getparent()
    last_image_group_element = image_group_element
    for image in images:
       new_group_element = tree.makeelement(image_group_element.tag)
       new_image_element = tree.makeelement(image_element.tag)
       new_image_element.text = image
       new_group_element.append(new_image_element)
       last_image_group_element.addnext(new_group_element)
       last_image_group_element = new_group_element
    # trash the stand-in group from the example XML
    tree.remove(image_group_element)
    return etree.tostring(tree)

def post_submission(xml, attachment_paths=None):
    ''' attachment filenames must match XML field values '''
    if isinstance(attachment_paths, basestring):
        attachment_paths = [attachment_paths]
    elif attachment_paths is None:
        attachment_paths = []
    request_files = [
        ('xml_submission_file', ('instance.xml', StringIO(xml)))
    ]
    for attachment_path in attachment_paths:
        name = os.path.split(attachment_path)[-1]
        request_files.append(
            (name, (name, open(attachment_path, 'rb')))
        )
    return requests.post(SUBMISSION_ENDPOINT, files=request_files)

### The following tests don't even manipulate the XML to match the attachments;
### they just rely on KC saving every attachment it receives. FIXME

def test_minimal_submission():
    response = post_submission(construct_instance_xml())
    response.raise_for_status()
    assert response.status_code == SUCCESS_STATUS_CODE

def test_minimal_duplicate_submission():
    xml = construct_instance_xml()
    response_codes = []
    for i in range(2):
        response = post_submission(xml)
        response.raise_for_status()
        response_codes.append(response.status_code)
    assert response_codes == [SUCCESS_STATUS_CODE, DUPLICATE_STATUS_CODE]

def test_minimal_attachment_in_second_request():
    xml = construct_instance_xml()
    response = post_submission(xml)
    response.raise_for_status()
    assert response.status_code == SUCCESS_STATUS_CODE

    try:
        attachment = NamedTemporaryFile(prefix='minimal', delete=False)
        attachment.write('minimal file contents in second request')
        attachment.close()
        response = post_submission(xml, attachment.name)
    finally:
        os.remove(attachment.name)
    response.raise_for_status()
    assert response.status_code == SUCCESS_STATUS_CODE

def test_duplicate_minimal_attachment():
    xml = construct_instance_xml()
    try:
        attachment = NamedTemporaryFile(prefix='minimal', delete=False)
        attachment.write('minimal file contents submitted twice')
        attachment.close()
        response_codes = []
        for i in range(2):
            response = post_submission(xml, attachment.name)
            response.raise_for_status()
            response_codes.append(response.status_code)
    finally:
        os.remove(attachment.name)
    assert response_codes == [SUCCESS_STATUS_CODE, DUPLICATE_STATUS_CODE]

def test_mixed_new_and_duplicate_minimal_attachments():
    # first request with no attachments
    xml = construct_instance_xml()
    response = post_submission(xml)
    response.raise_for_status()
    assert response.status_code == SUCCESS_STATUS_CODE

    try:
        attachments = []
        attachment = NamedTemporaryFile(prefix='minimal', delete=False)
        attachment.write('minimal file contents')
        attachment.close()
        attachments.append(attachment)

        attachment = NamedTemporaryFile(prefix='second_minimal', delete=False)
        attachment.write('second minimal file contents')
        attachment.close()
        attachments.append(attachment)

        # second request with first attachment only
        response = post_submission(xml, attachments[0].name)
        response.raise_for_status()
        assert response.status_code == SUCCESS_STATUS_CODE

        # third request with both attachments
        response = post_submission(xml, [x.name for x in attachments])
        response.raise_for_status()
        assert response.status_code == SUCCESS_STATUS_CODE
    finally:
        for attachment in attachments:
            os.remove(attachment.name)

def test_minimal_attachments_with_same_name_but_different_contents():
    # FIXME: this passes, but KC actually overwrites the first contents with
    # the second. We'll have to read the submission and attachments from KC's
    # API to make this test useful. See also
    # https://github.com/kobotoolbox/kobocat/issues/124
    xml = construct_instance_xml()
    try:
        attachment = NamedTemporaryFile(prefix='minimal', delete=False)
        attachment.write('same name, first minimal contents')
        attachment.close()
        response = post_submission(xml, attachment.name)
        response.raise_for_status()
        assert response.status_code == SUCCESS_STATUS_CODE

        attachment = open(attachment.name, 'wb')
        attachment.write('same name, second minimal contents')
        attachment.close()
        response = post_submission(xml, attachment.name)
        response.raise_for_status()
        assert response.status_code == SUCCESS_STATUS_CODE
    finally:
        os.remove(attachment.name)

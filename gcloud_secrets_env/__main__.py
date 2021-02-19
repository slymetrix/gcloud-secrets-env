import os
import re
import sys
import string
import six
import google.auth
from google.cloud import secretmanager

DEFAULT_PREFIX = 'secret'
SECRET_PREFIX_ENV_VAR = 'GCP_SECRETS_PREFIX'

_, PROJECT_ID = google.auth.default()
CLIENT = secretmanager.SecretManagerServiceClient()

PREFIX = None
if SECRET_PREFIX_ENV_VAR in os.environ:
    PREFIX = os.environ[SECRET_PREFIX_ENV_VAR]

if not PREFIX:
    PREFIX = DEFAULT_PREFIX

PATTERN = '^' + re.escape(PREFIX) + ':(?:(.*?)/)?(.+?)(?:#(.*?))?$'

SINGLE_QUOTE = "'"
ESCAPED = {
    "'": "\\'",
}

def sh_string(s):
    orig_s = s
    if isinstance(s, six.binary_type):
        s = s.decode('latin1')
    if '\x00' in s: ##
        log.error("sh_string(): Cannot create a null-byte")

    if not s:
        quoted_string = "''" ##
        if isinstance(orig_s, six.binary_type):
            quoted_string = quoted_string.encode('latin1')
        return quoted_string

    chars = set(s)
    very_good = set(string.ascii_letters + string.digits + "_+.,/-") ##

    # Alphanumeric can always just be used verbatim.
    if chars <= very_good:
        return orig_s

    # If there are no single-quotes, the entire thing can be single-quoted
    if not (chars & set(ESCAPED)):
        quoted_string = "'%s'" % s ##
        if isinstance(orig_s, six.binary_type):
            quoted_string = quoted_string.encode('latin1')
        return quoted_string

    # If there are single-quotes, we can single-quote around them, and simply
    # escape the single-quotes.
    quoted_string = '' ##
    quoted = False
    for char in s: ##
        if char not in ESCAPED:
            if not quoted:
                quoted_string += SINGLE_QUOTE
                quoted = True
            quoted_string += char ##
        else:
            if quoted:
                quoted = False
                quoted_string += SINGLE_QUOTE
            quoted_string += ESCAPED[char]

    if quoted:
        quoted_string += SINGLE_QUOTE

    if isinstance(orig_s, six.binary_type):
        quoted_string = quoted_string.encode('latin1')
    return quoted_string

def sh_prepare(variables, export = False):
    out = []
    export = 'export ' if export else ''

    for k, v in variables.items():
        out.append('%s%s=%s' % (export, k, sh_string(v)))

    return ';'.join(out)

def convert_keys():
    for key in os.environ:
        match = re.search(PATTERN, os.environ[key])
        if match:
            project = match.group(1) if match.group(1) else PROJECT_ID
            name = match.group(2)
            version = match.group(3) if match.group(3) else 'latest'

            key_path = secretmanager.SecretManagerServiceClient.secret_version_path(project, name, version)
            value = CLIENT.access_secret_version(key_path).payload.data.decode('UTF-8')
            
            yield key, value

if len(sys.argv) == 1:
    for key, value in convert_keys():
        print(sh_prepare({key: value}, True))
else:
    for key, value in convert_keys():
        os.environ[key] = value
        os.execvp(sys.argv[1], sys.argv[1:])
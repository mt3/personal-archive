"""
Tools for dealing with the .gmail.json files generated by
download_gmail_folder.py.
"""

import sys
import re
import email.parser
import datetime
import dateutil.parser

def ParseMessagePair(msg, parse_type=None):
  """Returns structured data about the message given a [body, header] pair.
  
  If parse_type is specified, then any MIME part matching that type will be
  extracted into the 'content' output parameter. If it is unspecified, then
  'content' will point to the raw message data.
  """
  body = msg[0][1]
  header = msg[1][1]
  body = re.sub(r'\r\n', '\n', body)

  out = {}

  fp = email.parser.FeedParser()
  fp.feed(header)
  fp.feed(body)
  m = fp.close()
  assert m
  if not m['Date']:
    # TODO(danvk): what are these?
    return None

  out['subject'] = m['Subject']
  out['from'] = m['From']
  try:
    dt = dateutil.parser.parse(m['Date'])
  except ValueError as e:
    # TODO(danvk): look into these
    sys.stderr.write('Unable to parse %s\n' % m['Date'])
    # TODO(danvk): use send timestamp instead
    return None

  out['date'] = dt
  if not parse_type:
    out['contents'] = body
  else:
    for part in m.walk():
      if part.get_content_type() == parse_type:
        out['contents'] = part.get_payload()
        break

  return out

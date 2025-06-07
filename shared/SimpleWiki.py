import requests


class SimpleWiki:
  def __init__(self, wiki_url):
    self.session = requests.Session()
    self.api_url = f"{wiki_url}/api.php" if not wiki_url.endswith('api.php') else wiki_url
    self.csrf_token = None

  def login(self, username, password):
    # Step 1: Get login token
    login_token_params = {
      'action': 'query',
      'meta': 'tokens',
      'type': 'login',
      'format': 'json'
    }

    r = self.session.get(self.api_url, params=login_token_params)
    login_token = r.json()['query']['tokens']['logintoken']

    login_params = {
      'action': 'login',
      'lgname': username,
      'lgpassword': password,
      'lgtoken': login_token,
      'format': 'json'
    }
    r = self.session.post(self.api_url, data=login_params)

    if r.json()['login']['result'] != 'Success':
      raise Exception('Login failed')

    csrf_params = {
      'action': 'query',
      'meta': 'tokens',
      'format': 'json'
    }
    r = self.session.get(self.api_url, params=csrf_params)
    self.csrf_token = r.json()['query']['tokens']['csrftoken']

  def create_or_update_page(self, page_title, page_content):
    """
    Creates or updates a page on the server using the provided title and content. The user must
    be logged in with a valid CSRF token before invoking this function. The provided title
    specifies the page to be created or updated, and the provided content is the text that
    will populate the page.

    :param page_title: The title of the page to be created or updated.
    :type page_title: str
    :param page_content: The content to populate the page with.
    :type page_content: str
    :return: The JSON response from the server after attempting to create or update the page.
    :rtype: dict
    :raises Exception: If the user is not logged in (missing CSRF token).
    """
    if not self.csrf_token:
      raise Exception("Must login first")

    edit_params = {
      'action': 'edit',
      'title': page_title,
      'text': page_content,
      'token': self.csrf_token,
      'format': 'json',
    }
    r = self.session.post(self.api_url, data=edit_params)
    return r.json()

  def rename_page(self, old_title, new_title, reason=''):
    """
    Renames a page on the platform by updating its title. The operation involves
    sending a POST request to the API with the necessary parameters. A CSRF token
    is required to perform this action. This function also allows specifying a
    reason for the title change and updates associated information such as talk
    pages. It ensures no redirect is created for the old title.

    :param old_title: The current title of the page to be renamed.
    :type old_title: str
    :param new_title: The new desired title for the page.
    :type new_title: str
    :param reason: The reason for renaming the page. Defaults to an empty string.
    :type reason: str, optional
    :return: The JSON response from the server after attempting to rename the page.
    :rtype: dict
    :raises Exception: If the CSRF token is not set, indicating the user is not
        logged in.
    """
    if not self.csrf_token:
        raise Exception("Must login first")

    move_params = {
        'action': 'move',
        'from': old_title,
        'to': new_title,
        'reason': reason,
        'token': self.csrf_token,
        'format': 'json',
        'movetalk': '1',
        'noredirect': '0'
    }

    r = self.session.post(self.api_url, data=move_params)
    return r.json()

  def upload_file(self, file_source, filename, comment='', text='', ignore_warnings=False):
    """
    Uploads a file to the wiki. The file can be provided either as a local filepath
    or as bytes (e.g., from an HTTP POST request).

    :param file_source: Path to the file to upload or the file content as bytes
    :type file_source: str or bytes
    :param filename: Destination filename on the wiki
    :type filename: str
    :param comment: Upload comment
    :type comment: str, optional
    :param text: Initial page text for the file
    :type text: str, optional
    :param ignore_warnings: Whether to ignore warnings
    :type ignore_warnings: bool, optional
    :return: The JSON response from the server after attempting to upload the file
    :rtype: dict
    :raises Exception: If the user is not logged in (missing CSRF token)
    """
    if not self.csrf_token:
      raise Exception("Must login first")

    # Prepare the upload parameters
    upload_params = {
      'action': 'upload',
      'filename': filename,
      'comment': comment,
      'text': text,
      'token': self.csrf_token,
      'format': 'json',
    }

    if ignore_warnings:
      upload_params['ignorewarnings'] = '1'

    files = None

    # Handle file source based on type
    if isinstance(file_source, str):
      # If file_source is a string, treat it as a file path
      with open(file_source, 'rb') as file:
        files = {'file': file}
        r = self.session.post(self.api_url, data=upload_params, files=files)
    else:
      # If file_source is not a string, treat it as bytes
      files = {'file': (filename, file_source)}
      r = self.session.post(self.api_url, data=upload_params, files=files)

    return r.json()
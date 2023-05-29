import os

from django.shortcuts import redirect
from django.conf import settings
from django.views import View
from google.oauth2 import client
from googleapiclient.discovery import build

my_secret = os.environ['SECRET_KEY']

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = client.flow_from_clientsecrets(
            {"web":{"client_id":"131497760679-ogjttu38gf200qn8fd0jm6icelrnl33h.apps.googleusercontent.com","project_id":"silent-album-388111","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://127.0.0.1:8080/rest/v1/calendar/redirect","http://127.0.0.1:8080/rest/v1/calendar/init/"],"javascript_origins":["http://127.0.0.1:8080"]}}),
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        authorization_url, state = flow.authorization_url(access_type='offline')
        request.session['google_auth_state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        if 'code' not in request.GET or 'state' not in request.GET:
            return HttpResponseBadRequest('Missing parameters')

        state = request.GET['state']
        if state != request.session.get('google_auth_state'):
            return HttpResponseBadRequest('Invalid state')

        flow = client.flow_from_clientsecrets(
            {"web":{"client_id":"131497760679-ogjttu38gf200qn8fd0jm6icelrnl33h.apps.googleusercontent.com","project_id":"silent-album-388111","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"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","redirect_uris":["http://127.0.0.1:8080/rest/v1/calendar/redirect","http://127.0.0.1:8080/rest/v1/calendar/init/"],"javascript_origins":["http://127.0.0.1:8080"]}},
            scopes=['https://www.googleapis.com/auth/calendar.events'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
            code=request.GET['code']
        )
        credentials = flow.credentials

        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        # Process the events as needed

        return JsonResponse({'events': events})


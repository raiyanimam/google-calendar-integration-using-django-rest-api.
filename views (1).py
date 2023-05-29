import os

from django.shortcuts import redirect
from django.conf import settings
from django.views import View
from google.oauth2 import client
from googleapiclient.discovery import build

my_secret = os.environ['SECRET_KEY']

class GoogleCalendarInitView(View):
    def get(self, request):
        flow = client.flow_from_clientsecrets(settings.GOOGLE_CLIENT_SECRETS_FILE
            ),
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
            settings.GOOGLE_CLIENT_SECRETS_FILE),
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


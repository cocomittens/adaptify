from django.shortcuts import redirect, render
from common.supabase_client import supabase

def oauth_login(request):
    provider = request.GET.get('provider')
    auth_url = supabase.auth.get_provider_url(provider)
    return redirect(auth_url)

def oauth_callback(request):
    access_token = request.GET.get('access_token')
    user = supabase.auth.sign_in(access_token=access_token)
    if user:
        return redirect('/')
    else:
        return redirect('/login/')

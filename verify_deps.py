import sys

try:
    import selenium
    print("selenium: OK")
except ImportError:
    print("selenium: Missing")

try:
    import streamlit
    print("streamlit: OK")
except ImportError:
    print("streamlit: Missing")

try:
    import plotly
    print("plotly: OK")
except ImportError:
    print("plotly: Missing")

try:
    import requests
    print("requests: OK")
except ImportError:
    print("requests: Missing")

try:
    import google.auth
    print("google.auth: OK")
except ImportError:
    print("google.auth: Missing")

try:
    import google_auth_oauthlib
    print("google_auth_oauthlib: OK")
except ImportError:
    print("google_auth_oauthlib: Missing")

try:
    import google.apps.meet
    print("google.apps.meet: OK")
except ImportError:
    print("google.apps.meet: Missing")

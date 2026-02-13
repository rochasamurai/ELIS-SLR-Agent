import os
import requests


def check_environment():
    """Check that required environment variables are set."""
    API_KEY = os.getenv("SCOPUS_API_KEY")
    INST_TOKEN = os.getenv("SCOPUS_INST_TOKEN")

    if not API_KEY:
        raise EnvironmentError("Missing SCOPUS_API_KEY in environment variables.")
    if not INST_TOKEN:
        raise EnvironmentError("Missing SCOPUS_INST_TOKEN in environment variables.")

    return API_KEY, INST_TOKEN


def test_scopus_connection():
    """Test connection to Scopus API."""
    API_KEY, INST_TOKEN = check_environment()

    headers = {
        "X-ELS-APIKey": API_KEY,
        "X-ELS-Insttoken": INST_TOKEN,
        "Accept": "application/json",
    }

    url = "https://api.elsevier.com/content/search/scopus"
    params = {"query": "TITLE(electoral integrity)", "count": 1}

    response = requests.get(url, headers=headers, params=params)

    print("Status Code:", response.status_code)
    try:
        response.raise_for_status()
        data = response.json()
        print("Query OK. First result:")
        print(data["search-results"]["entry"][0])
    except Exception as e:
        print("Error querying Scopus API:", str(e))
        print("Response text:", response.text)


if __name__ == "__main__":
    test_scopus_connection()

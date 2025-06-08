from crewai_tools import BaseTool
import requests # Ensure requests library is available in the environment

class SimpleGetRequestTool(BaseTool):
    name: str = "Simple GET Request Tool"
    description: str = "Performs a GET request to the specified URL and returns the text content. Input must be the URL."

    def _run(self, url: str) -> str:
        try:
            # Basic check for common protocols
            if not url.startswith(("http://", "https://")):
                return "Error: Invalid URL. Must start with http:// or https://"

            response = requests.get(url, timeout=10) # Added timeout
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.text
        except requests.exceptions.Timeout:
            return f"Error: Request timed out for URL: {url}"
        except requests.exceptions.HTTPError as e:
            return f"Error: HTTP error occurred for URL: {url}. Status code: {e.response.status_code}. Response: {e.response.text[:200]}"
        except requests.exceptions.RequestException as e:
            return f"Error making GET request to URL: {url}. Error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred for URL: {url}. Error: {str(e)}"

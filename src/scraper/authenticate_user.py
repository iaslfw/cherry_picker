from requests import Response, Session, exceptions
from src.configs.site_data import cookies, headers


def authenticate_user(base_url: str) -> tuple[Response, Session]:
    try:
        session = Session()
        url = f"{base_url}id=12873"
        response = session.get(url, cookies=cookies, headers=headers)

        print(session.cookies.get_dict())

        return response, session

    except exceptions.RequestException as e:
        print(f"An error occurred during authentication: {e}")
        return Response(), Session()

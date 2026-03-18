import os


from dotenv import load_dotenv
from src.scraper.setup_scraper import setup_scraper
from src.scraper.authenticate_user import authenticate_user

load_dotenv()

COURSE_URL = os.getenv("COURSE_BASE_LINK")


def main():
    print("Hello from uni-looter!")

    try:
        if not COURSE_URL:
            raise ValueError(
                "COURSE_BASE_LINK is not set in the environment variables."
            )

        data, session = authenticate_user(COURSE_URL)
        setup_scraper(data, session)
    except ValueError as e:
        print(f"An error occurred:\n{e}")


if __name__ == "__main__":
    main()

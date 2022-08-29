from dotenv import load_dotenv
from os import getenv

load_dotenv()


def main():
    reseller_id = input("Enter reseller id: ")
    site_url = getenv("SITE_LINK")


if __name__ == "__main__":
    main()

import os

from dotenv import load_dotenv
from typesafe_sdk import TypeSafeClient, Noul


# Load variables from .env
load_dotenv()

api_key = os.getenv("TYPESAFE_API_KEY")

if not api_key:
    raise RuntimeError(
        "TYPESAFE_API_KEY is not set. Check your .env file."
    )


# Create Jev client
with TypeSafeClient(api_key=api_key) as client:

    query = "Write a Python program to reverse a linked list."

    result = client.system_one(
        state=query,
        questions={
            "is_coding": Noul(
                instructions="Is this query asking for programming or coding help?"
            )
        },
    )

    print("\n==============================")
    print("        JEV DECISION")
    print("==============================")

    print("Query:")
    print(query)

    print("\nJev response:")
    print(result)

    print("\nCoding probability:")
    print(result.nouls["is_coding"].noul)

import asyncio
import json

from onfire_blackbird import run


async def main():
    # Example usage of blackbird async function
    print("Running Blackbird search...")

    # Search for a single username
    results = await run(usernames=["johndoe"], json_output=True, no_nsfw=True, verbose=True, ai=False)

    # Pretty print the results
    print("\nResults:")
    print(json.dumps(results, indent=2))

    # The results would contain found accounts in the "username_results" key
    # You can also search for emails with the "emails" parameter

    # Example with multiple usernames
    # results = await run(usernames=["johndoe", "janedoe"], json_output=True)

    # Example with email search
    # results = await run(emails=["example@example.com"], json_output=True)


if __name__ == "__main__":
    asyncio.run(main())

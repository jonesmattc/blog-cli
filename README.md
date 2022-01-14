# blog-cli
Notion-powered microblogging CLI tool


To run:
Install requirements from Pipfile (requests, click, pyyaml)
Create a Notion Integration at https://www.notion.so/my-integrations
Note your `Internal Integration Token`
Share access to your integration for the database you wish to use for your journal. This is required for the integration to be able to see your database.


`python main.py configure` will prompt you for your Notion API key (`Internal Integration Token`) and the Notion database to add your notes to. You can choose any database you want.

Once configured, you can run `python main.py blog` to enter your notes. These will automatically get appended to a per-month file for the month you're running it in.

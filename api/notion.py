from datetime import date

import requests


def get_journal_database(search, api_key):
    search_result = requests.post("https://api.notion.com/v1/search", json={
        "query": search,
        "sort": {
            "direction": "ascending",
            "timestamp": "last_edited_time"
        }
    }, headers={
        'Authorization': f'Bearer {api_key}',
        'Notion-Version': '2021-08-16'
    })

    if not search_result.ok:
        print("Unable to access Notion API. Please check that your API key is configured correctly")
        return None

    search_contents = search_result.json()

    assert search_contents['object'] == 'list'

    if not search_contents['results']:
        print("Unable to find a journal database in your notion workspace.\nPlease make sure Journal exists in your workspace.")
        return None

    options = []

    index = 0
    for result in search_contents['results']:
        if result['object'] != 'database':
            continue
        options.append({"name": result["title"][0]["text"]["content"], "id": result["id"], "index": index})
        index += 1

    return options


def get_current_months_journal(db_id, api_key):
    current_month_title = date.today().strftime('%Y-%b')
    print(current_month_title, db_id)
    query_result = requests.post(f"https://api.notion.com/v1/databases/{db_id}/query", json={
        "filter": {
            "property": "title",
            "text": {
                "equals": "2022-Jan"
            }
        },
        "sorts": [
            {
                "direction": "descending",
                "property": "Name"
            }
        ]
    }, headers={
        'Authorization': f'Bearer {api_key}',
        'Notion-Version': '2021-08-16'
    })

    if not query_result.ok:
        print("Unable to access Notion API. Please check that your API key is configured correctly")
        return None

    search_contents = query_result.json()
    assert search_contents['object'] == 'list'

    if not search_contents['results']:
        print('creating a new page')
        return create_new_journal_page(current_month_title, db_id, api_key)

    return search_contents['results'][0]['id']


def create_new_journal_page(title, parent_db_id, api_key):
    create_result = requests.post(f"https://api.notion.com/v1/pages", headers={
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2021-08-16"
    }, json={
        "parent": {
            "type": "database_id", "database_id": parent_db_id
        },
        "properties": {
            "Name": {
                "title": [{
                    "text": {
                        "content": title
                    }
                }]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "text": [{
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }]
                }
            }
        ]
    })

    return create_result.json()['id']


def append_entry(contents, api_key, page_id):
    append_result = requests.patch(f"https://api.notion.com/v1/blocks/{page_id}/children", headers={
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": "2021-08-16"
    }, json={
        "children": [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "text": [{
                    "type": "text",
                    "text": {
                        "content": contents,
                        "link": None
                    }
                }]
            }
        }]
    })

    return append_result.ok

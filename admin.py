from config import ASSISTANT_MODEL, get_config, client, save_config


def get_vector_store_id():
    config = get_config()
    if "vector_store_id" not in config or not config["vector_store_id"]:
        new_store = client.beta.vector_stores.create()
        config["vector_store_id"] = new_store.id
        save_config(config)

    return config["vector_store_id"]


def create_assistant(name, instructions):
    assistant_id = get_assistant_id()
    if not assistant_id:
        new_assistant = client.beta.assistants.create(
            model=ASSISTANT_MODEL,
            instructions=instructions,
            name=name,
            tools=[
                {
                    "type": "file_search",
                }
            ],
            tool_resources={
                "file_search": {"vector_store_ids": [get_vector_store_id()]}
            },
        )
        config = get_config()
        config["assistant_id"] = new_assistant.id
        save_config(config)
    else:
        client.beta.assistants.update(
            assistant_id=assistant_id, instructions=instructions
        )


def get_assistant_id():
    config = get_config()
    return config["assistant_id"] if "assistant_id" in config else None


def add_knowledge(filename, file):
    file_object = client.files.create(file=(filename, file), purpose="assistants")
    store_id = get_vector_store_id()
    client.beta.vector_stores.files.create(
        vector_store_id=store_id, file_id=file_object.id
    )


def reset_knowledge():
    store_id = get_vector_store_id()
    files = client.beta.vector_stores.files.list(vector_store_id=store_id)
    for file in files:
        client.beta.vector_stores.files.delete(
            vector_store_id=store_id, file_id=file.id
        )
        client.files.delete(file.id)

import torch.nn.functional as F


def pad_to_shape(tensor, target_shape, pad_value=0):
    c, d, h, w = tensor.shape
    td, th, tw = target_shape
    pd = td - d
    ph = th - h
    pw = tw - w
    return F.pad(tensor, (0, pw, 0, ph, 0, pd), value=pad_value)


def messages_for_apply_template(conversations_list):
    processed_conversations_list = []
    extracted_texts = []

    for conversation in conversations_list:
        import copy

        processed_conversation = copy.deepcopy(conversation)
        extracted_text = None

        if processed_conversation:
            last_index = len(processed_conversation) - 1
            last_message = processed_conversation[last_index]

            if (
                isinstance(last_message, dict)
                and last_message.get("role") == "assistant"
            ):
                content = last_message.get("content")

                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            extracted_text = item.get("text")
                            break

                del processed_conversation[last_index]

        processed_conversations_list.append(processed_conversation)
        extracted_texts.append(extracted_text)

    return processed_conversations_list, extracted_texts

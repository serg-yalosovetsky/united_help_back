from typing import Optional


def str_to_bool(string: str) -> Optional[bool]:
    ret = None
    if not string:
        return None
    if string.lower() == 'true':
        ret = True
    if string.lower() == 'false':
        ret = False
    return ret


def index_in_list(list_: list[str], search: str) -> int:
    '''
    return positive index if search in list_
    else return -1
    '''
    if search in list_:
        for i, lis_ in enumerate(list_):
            if search == lis_:
                return i
    else:
        return -1


DATETIME_FORMAT = '%d_%m_%Y-%H_%M_%S'
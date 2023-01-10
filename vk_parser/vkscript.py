from vk_api.execute import VkFunction
from vk_parser import show_parsing_state
import math


def execute(vk, method, owner_id, count, offset_delta, requests_num, limit=None):
    steps = math.ceil(limit / (offset_delta * requests_num)) if limit else 1
    results = []
    offset = 0

    for step in range(steps):
        stop_parsing = show_parsing_state()
        if stop_parsing:
            print('stopped')
            break

        result = vk_script_func(vk, method=method, owner_id=owner_id, count=count,
                                offset_delta=offset_delta, offset=offset, requests_num=requests_num)
        offset += offset_delta * requests_num
        results.extend(result)

        if not result:
            break

    return results


vk_script_func = VkFunction(args=('method', 'owner_id', 'count',
                                  'offset_delta', 'offset', 'requests_num'), clean_args=('method',),
                            code='''
    var count_loop = 0;
    var items = [];
    var ids = [];
    var offset = %(offset)s;

    while(count_loop<%(requests_num)s){
    items = API.%(method)s({'owner_id': %(owner_id)s, 'count': %(count)s, 'offset': offset}); 
    if(!items && items.length < 1) {
    count_loop = 99;
    } else {
    ids = ids + items.items@.id;
    count_loop = count_loop + 1;
    offset = offset + %(offset_delta)s;
    }
    }
    return ids;
          '''
                            )
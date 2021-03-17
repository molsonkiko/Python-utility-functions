import traceback

bad_json = {'a': 1, 'b': 3, '6': 7, '9': 'ball', 
            'jub': {'uy': [1, 2, 3], 
                    'yu': [
                        [6, {'y': 'b', 'm': 9}], 10], 
            'status': 'jubar'}}

def is_iterable(x):
    return hasattr(x,'__iter__') and not isinstance(x,str)

def json_extract(json,path):
    '''json: an arbitrary object containing nested arrays (cf. tuples and lists) and dicts.
path: tuple, list, or single string or int. A partial ORDERED path to sub-objects of 
    interest. This could just be one key or index.
    The path can contain sub-tuples or sub-lists. Any key inside a sub-tuple is a valid
    place to visit at that step in the path.
    For example, the path (('yu','uy'),1,0) represents any path where you first visit
    the key 'yu' OR 'uy', and then the key 1, and then the key 0.
Returns: A list, all values that can be reached by a path that includes the input "path".
Examples:
>>> json_extract([[1,[2,3]],[4]],(1,0)) #reaches [0][1][0] and [1][0]
[2,4]
>>> bad_json = {'a': 1, 'b': 3, '6': 7, '9': 'ball', 'jub': {'uy': [1, 2, 3], 'yu': [[6, {'y': 'b', 'm': 9}], 10], 'status': 'jubar'}}
>>> json_extract(bad_json,'status')
['jubar']
>>> json_extract(bad_json, ('jub','uy',1))
[2]
>>> json_extract(bad_json,('jub','yu',2)) #returns nothing inside bad_json['jub']['yu'] has the key 2. 
[]
>>> json_extract(bad_json,('yu',1,'y')) #note that the path is ['jub']['yu'][0][1]['y']; this function will find paths that have an arbitrary unspecified key in between specified keys.
['b']
>>> json_extract(bad_json,(('uy','yu'),1)) #go to 'uy' OR 'yu', then 1.
[2, {'y': 'b', 'm': 9}, 10]
>>> json_extract({'a':{'b':1,'a':2,'c':3},'b':{'b':4,'a':5},'c':6},(('a','b'),('a','b')))
[1, 2, 4, 5]
    Inspired by, but NOT copied from https://hackersandslackers.com/extract-data-from-complex-json-python/ and
    https://bcmullins.github.io/parsing-json-python/
    '''
    _arr = [] #holds all the matching records
    if type(path) not in [tuple,list]:
        path = [path]
    if len(path)==0:
        return []
    def extract(graph,path,arr=_arr,curpath = None):
        if type(graph)==dict:
            iterator = iter(graph)
        else:
            iterator = range(len(graph))
        if curpath is None:
            curpath = []
        path0_is_itbl = is_iterable(path[0])
        for curnode in iterator:
            newgraph = graph[curnode]
            if path0_is_itbl:
                if len(path)==1 and curnode in path[0]:
                    arr.append(newgraph)
                    continue
            else:
                if len(path)==1 and curnode == path[0]:
                    #since the path loses the first node each time you find a node that matches
                    #the first node in the path, once the path has length one and curnode matches
                    #the first element in the path, the originally specified path is satisfied.
                    arr.append(newgraph)
                    continue
            if is_iterable(newgraph): #if newgraph is an array or dict
                if path0_is_itbl:
                    if curnode in path[0]:
                        #continue recursively searching, this time for any paths that match
                        #the rest of the path (not including the first node in the path, which
                        #we already found).
                        placeholder = extract(newgraph, path[1:], arr, curpath + [curnode])
                    else:
                        placeholder = extract(newgraph, path, arr, curpath + [curnode])
                else:       
                    if curnode == path[0]:
                        #continue recursively searching, this time for any paths that match
                        #the rest of the path (not including the first node in the path, which
                        #we already found).
                        placeholder = extract(newgraph, path[1:], arr, curpath + [curnode])
                    else:
                        placeholder = extract(newgraph, path, arr, curpath + [curnode])
        return arr

    return extract(json,path)


def show_json_structure(json,show_parents_only = False,keys_of_interest = tuple()):
    '''Returns a pretty-print string of the keys (and, if show_parents_only is False, 
    the values in arrays) in a json object.
If show_parents_only is True, it only prints keys and indices of arrays if those indices
    or keys have a child that is also a json object and not just a scalar.
If keys_of_interest is not empty, only show the keys_of_interest and their children.

Example:
>>> bad_json = {'a': 1, 'b': 3, '6': 7, '9': 'ball', 'jub': {'uy': [1, 2, 3], 'yu': [[6, {'y': 'b', 'm': 9}], 10], 'status': 'jubar'}}
>>> show_json_structure(bad_json)
{
'a'
'b'
'6'
'9'
'jub'
    {
    'uy'
        [
        1
        2
        3
        ],
    'yu'
        [
        0
            [
            6
            1
                {
                'y'
                'm'
                },
            ],
        10
        ],
    'status'
    },
}
>>> show_json_structure(bad_json,True)
{
'jub'
    {
    'uy'
        [
        ],
    'yu'
        [
        0
            [
            1
                {
                },
            ],
        ],
    },
}
>>> show_json_structure(bad_json,False,('jub','uy',2)
{
'jub'
    {
    'uy'
        [
        ],
    'yu'
        [
        0
            [
            1
                {
                },
            ],
        ],
    },
}
    '''
    if not is_iterable(keys_of_interest):
        keys_of_interest = [[keys_of_interest]]
    else:
        keys = []
        for key in keys_of_interest:
            if is_iterable(key):
                keys.append(key)
            else:
                keys.append([key])
        keys_of_interest = keys
    print(keys_of_interest)
    def repr_if_string(x):
        if type(x)==str:
            return repr(x)
        else:
            return str(x)
    out_arr = []
    def traverse(arr = out_arr,**kwargs):
        graph = kwargs.get('graph')
        depth = kwargs.get('depth',0)
        keys_of_interest = kwargs.get('keys_of_interest',tuple())
        if type(graph)==dict:
            iterator = iter(graph)
            arr.append('\t'*depth + '{')
        else:
            iterator = range(len(graph))
            arr.append('\t'*depth + '[')
        #curpath = kwargs.get('curpath',[])
        for curnode in iterator:
            newgraph = graph[curnode]
            if len(keys_of_interest)==0 or curnode in keys_of_interest[0]:
                if is_iterable(newgraph):
                    arr.append('\t'*depth + repr_if_string(curnode))
                    #curpath = curpath + [curnode]
                    placeholder = traverse(arr, graph = newgraph,
                                            depth= depth+1,
                                            keys_of_interest=keys_of_interest[1:])
                elif not show_parents_only:
                    if type(graph)==dict:
                        arr.append('\t'*depth + repr_if_string(curnode))
                    else:
                        arr.append('\t'*depth + repr_if_string(newgraph))
        if type(graph)==dict:
            arr.append('\t'*depth + '},')
        else:
            arr.append('\t'*depth + '],')
    
    try:
        traverse(out_arr,graph=json,keys_of_interest = keys_of_interest)
        return '\n'.join(out_arr)[:-1]
    except:
        print(traceback.format_exc())
        
        

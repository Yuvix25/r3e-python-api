import re
import mmap
import json
import struct

SIZES = {'Int32': 4, 'Int16': 2, 'Int8': 1, 'Float32': 4, 'Float64': 8, 'Double': 8, 'Single': 4, 'UInt32': 4, 'UInt16': 2, 'UInt8': 1, 'Int64': 8, 'UInt64': 8, 'Boolean': 1, 'Byte': 1, 'SByte': 1, 'Char': 2, 'String': 4, 'Void': 0, 'byte': 1, 'sbyte': 1, 'char': 2, 'string': 4, 'void': 0}
STRUCT_TYPES = {'Single': 'f', 'Double': 'd', 'Int32': 'i', 'Int16': 'h', 'Int8': 'b', 'Float32': 4, 'Float64': 8, 'UInt32': 'I', 'UInt16': 'H', 'UInt8': 'B', 'Int64': 'q', 'UInt64': 'Q', 'Boolean': '?', 'Byte': 'B', 'SByte': 'b', 'Char': 'c', 'String': 's', 'Void': 'x', 'byte': 'B', 'sbyte': 'b', 'char': 'c', 'string': 's', 'void': 'x'}


def get_struct_string(positions):
    res = ''
    val_type = positions['type']
    if 'children' in positions:
        if type(positions['children']) == list:
            val_type = val_type.split('[')[0]
            if val_type in STRUCT_TYPES:
                res += str(len(positions['children'])) + STRUCT_TYPES[val_type]
            else:
                for i in range(len(positions['children'])):
                    res += get_struct_string(positions['children'][i])
        else:
            for position in positions['children']:
                res += get_struct_string(positions['children'][position])
    elif positions['type'] in STRUCT_TYPES:
        res += STRUCT_TYPES[positions['type']]
    
    return res

def read_data_from_struct(data, positions):
    struct_string = '<' + get_struct_string(positions)
    start = positions['start']
    end = positions['end']
    return unflatten_struct_data(struct.unpack(struct_string, data[start:end]), positions)


def get_child_amount(position):
    if 'children' in position:
        if type(position['children']) == list:
            return sum([get_child_amount(position['children'][i]) for i in range(len(position['children']))])
        else:
            return sum([get_child_amount(position['children'][i]) for i in position['children']])
    else:
        size = (position['end'] - position['start']) // SIZES[position['type']]
    return size

def unflatten_struct_data(data, positions):
    res = {}
    if 'children' in positions:
        if type(positions['children']) == list:
            res = []
            i = 0
            for position in positions['children']:
                size = get_child_amount(position)
                res.append(unflatten_struct_data(data[i:i+size], position))
                i += size

            if positions['type'].startswith('byte'):
                string_res = ''
                for i in res:
                    try:
                        if i != 0 and i != tuple():
                            string_res += chr(i)
                    except:
                        pass
                res = string_res
        else:
            i = 0
            for name, position in sorted(list(positions['children'].items()), key=lambda x: x[1]['start']):
                size = get_child_amount(position)
                res[name] = unflatten_struct_data(data[i:i+size], position)
                i += size
    else:
        res = data[0] if (type(data) == list or type(data) == tuple) and len(data) == 1 else data
    
    return res
    


def replace_if_equals(string, old, new):
    return new if string == old else string

def read_struct_positions(data, struct_name, generic_type=None, start=0):
    """
    Reads a struct from the data and returns a dictionary with the struct's fields and positions, in the following format:
    {
        'field_name': {
            'start': int,
            'end': int,
            'type': str,
            'children': dict # same formt as this dict, only if exists.
        }
    }
    """

    if struct_name in STRUCT_TYPES:
        return {
            'start': start,
            'end': SIZES[struct_name] + start,
            'type': struct_name,
        }

    struct = -1
    generic_var_name = None
    for i, line in enumerate(data):
        if line.startswith('internal struct ' + struct_name):
            struct = i
            if '<' in line:
                generic_var_name = line.split('<')[1].split('>')[0]
            break
    
    if struct == -1:
        return None

    children = {}
    res = {
        'start': start,
        'end': 0,
        'type': struct_name,
        'children': children,
    }
    before = start
    for i in range(struct + 1, len(data)):
        line = data[i]

        if line.startswith('public'):
            line_type = line.split(' ')[1]
            line_name = line.split(' ')[2].split(';')[0]
            sub_type = None

            if '<' in line_type:
                line_type, sub_type = line_type.split('<')
                sub_type = sub_type.split('>')[0]

                if generic_var_name:
                    line_type = replace_if_equals(line_type, generic_var_name, generic_type)
                    sub_type = replace_if_equals(sub_type, generic_var_name, generic_type)

            elif generic_var_name:
                line_type = replace_if_equals(line_type, generic_var_name, generic_type)
            
            modify_size = -1
            if '[' in line_type:
                line_type = line_type.split('[')[0]
                message = Exception('Error identifying array length of field ' + line_name + ' in struct ' + struct_name)

                if i == 0:
                    raise message
                
                prev_line = data[i - 1]
                if not prev_line.startswith('[MarshalAs(UnmanagedType.ByValArray'):
                    raise message
                
                try:
                    length = int(re.findall(r'\d+', prev_line)[0])
                except:
                    raise message
                
                children[line_name] = {
                    'start': before,
                    'end': 0,
                    'type': line_type + '[]',
                    'children': [],
                }
                obj = read_struct_positions(data, line_type, sub_type, before)
                children[line_name]['end'] = (obj['end'] - obj['start']) * length + before
                for _ in range(length):
                    children[line_name]['children'].append(obj)
                    obj = obj.copy()
                    size = obj['end'] - obj['start']
                    obj['start'] += size
                    obj['end'] += size

                    before += size
                
                continue

            children[line_name] = read_struct_positions(data, line_type, sub_type, before)

            if modify_size != -1:
                children[line_name]['end'] = children[line_name]['start'] + modify_size

            before += children[line_name]['end'] - children[line_name]['start']
            
            res['end'] = children[line_name]['end']
        
        elif line.startswith('}'):
            break

    return res



def convert(infile, outfile=None):
    data = open(infile, 'r').read()

    # data = data.replace('    ', '').replace('\t', '').replace('\r', '').split('\n')
    data = re.sub(r'\n\s+', '\n', data).replace('\t', '').replace('\r', '').split('\n')

    res = read_struct_positions(data, 'Shared')

    if outfile:
        json.dump(res, open(outfile, 'w'), indent=4)
    
    return res


def get_value(data, field, converted_data):
    positions = convert('./r3e_api/data.cs', 'Shared')

    for field_name in field.split('.'):
        if field_name not in positions['children']:
            try:
                field_name = int(field_name)
            except:
                raise Exception('Field ' + field_name + ' not found in struct ' + positions['type'])
        
        positions = positions['children'][field_name]

    return read_data_from_struct(data, positions)

class R3ESharedMemory:
    def __init__(self):
        self._mmap_data = None
        self._converted_data = None
    
    def update_offsets(self):
        self._converted_data = convert('./r3e_api/data.cs')
    
    @property
    def mmap_data(self):
        if not self._mmap_data:
            self.update_buffer()
        
        return self._mmap_data

    @property
    def converted_data(self):
        if self._converted_data is None:
            self.update_offsets()
        return self._converted_data

    def update_buffer(self):
        mmap_file = mmap.mmap(-1, 40960, "Local\\$R3E",  access=mmap.ACCESS_READ) # read the shared memory file
        mmap_file.seek(0)

        self._mmap_data = mmap_file.read()
        return self._mmap_data
    
    def get_value(self, field):
        return get_value(self._mmap_data, field, self.converted_data)

if __name__ == '__main__':
    shared = R3ESharedMemory()
    shared.update_buffer()
    print(shared.get_value('DriverData.0'))

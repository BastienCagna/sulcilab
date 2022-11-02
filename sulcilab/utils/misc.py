import os.path as op
from typing import Iterable, List
from sulcilab.database import Base


def split_label_name(name):
    if name.endswith('_left'):
        if name[-6] == '.':
            return name[:-6], "L"
        return name[:-5], "L"
    elif name.endswith('_right'):
        if name[-7] == '.':
            return name[:-7], "R"
        return name[:-6], "R"
    return name, "X"


def filt_keys(d: dict, keys: List[str]) -> dict:
    return {k: d[k] for k in keys}


def _sqlalchemy_to_pydantic_instance(object, schema: dict, definitions: List[dict]):
    """ Convert an SQLALchemy object to its Pydantic schema """

    # The result will be a dictionnary that match the pydantic schema
    result = {}
    # For attribute of the schema
    for attr, infos in schema['properties'].items():
        # If the attribute is not in the object, if it is manadory, raise an error else continue to the next attribute
        if not hasattr(object, attr):
            if attr in schema['required']:
                raise ValueError('Attribute {} is required for {}.'.format(attr, schema['title']))
            else:
                continue

        # Get the attribute value
        val = getattr(object, attr)

        # Then, convert if is not a basic type (string, number...)
        # For enums
        if hasattr(val, "value"):
            result[attr] = val.value
        # For SQLAlchemy object or list of objects
        elif isinstance(val, Base) or (isinstance(val, list) and len(val) > 0 and isinstance(val[0], Base)):
            if '$ref' in infos.keys():
                subschema = definitions[infos['$ref'].split('/')[-1]]
                result[attr] = _sqlalchemy_to_pydantic_instance(val, subschema, definitions)
            # If the attribuute is a list
            elif 'items' in infos.keys() and '$ref' in infos['items'].keys():
                subschema = definitions[infos['items']['$ref'].split('/')[-1]]
                result[attr] = []
                for v in val:
                    result[attr].append(_sqlalchemy_to_pydantic_instance(v, subschema, definitions))
            else:
                raise ValueError('Malformed Pydantic schema.')
        else:
            result[attr] = val
    return result
            

def sqlalchemy_to_pydantic_instance(object, pmodel):
    """ Convert one or a list of SQLALchemy objects to its Pydantic schema """
    # Ge the Pydantic description as dict
    schema = pmodel.schema()

    # Then convert either as a list or a single object
    if isinstance(object, Iterable):
        return list(_sqlalchemy_to_pydantic_instance(o, schema, schema['definitions']) for o in object)
    else:
        return _sqlalchemy_to_pydantic_instance(object, schema, schema['definitions'])

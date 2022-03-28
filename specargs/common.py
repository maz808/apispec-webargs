from http import HTTPStatus
from typing import Any, Dict, Union, TYPE_CHECKING, Type

from attrs import define, field, frozen
from cattrs import GenConverter
from marshmallow import Schema, fields

from .framework import parser

if TYPE_CHECKING:
    from in_poly import InPoly
else:
    InPoly = "InPoly"


ArgMap = Union[Schema, Dict[str, Union[fields.Field, Type[fields.Field]]], Type[Schema]]

con = GenConverter()


@frozen
class Webargs:
    schema_or_inpoly: Union[Schema, InPoly] = field(converter=lambda x: ensure_schema_or_inpoly(x))
    location: str


def ensure_schema_or_inpoly(argpoly: Union[ArgMap, InPoly]) -> Union[Schema, InPoly]:
    '''Produces a marshmallow `Schema` or an :class:`InPoly` from the input if possible

    `Schema` and :class:`InPoly` instances are returned immediately. Dictionaries mapping names to marshmallow `Field`
    instances are converted into `Schema` instances using the webargs `parser`. `Schema` classes are called to produce
    `Schema` instances. All other objects raise a `TypeError`.

    Args:
        argpoly: The object from which to produce a `Schema` or :class:`InPoly` instance

    Raises:
        :exc:`TypeError`: If given an object from which a `Schema` or :class:`InPoly` instance cannot be produced
    '''
    from .in_poly import InPoly
    if isinstance(argpoly, Schema) or isinstance(argpoly, InPoly): return argpoly
    if isinstance(argpoly, dict): return parser.schema_class.from_dict(argpoly)()
    if isinstance(argpoly, type(Schema)): return argpoly()
    raise TypeError(f"Unable to produce Schema or InPoly from {argpoly}!")


@define
class Response:
    '''An object used for specifying the data and status code returned by a view function/method'''
    data: Any
    status_code: HTTPStatus = field(converter=HTTPStatus, default=HTTPStatus.OK)

    def __init__(self, data: Any, status_code: Union[HTTPStatus, int]):
        '''Initializes a :class:`~specargs.Response` object
        
        Args:
            data: The data to be returned in the response. May be serialized depending on whether/how the returning
                view function/method has been decorated with :func:`~specargs.use_response`
            status_code: The status code of the response
        '''
        self.__attrs_init__(data, status_code)

from typing import Literal, Optional, overload


class RequestData:
    def __init__(self, type_: Literal["CALL", "GET"],
                 func_name: Optional[str] = None, args: Optional[tuple] = None,
                 kwargs: Optional[dict] = None,
                 event_get: Optional[bool] = None, var_name: Optional[str] = None
                 ) -> None:
        self.type = type_
        self.func_name = func_name or ""
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.event_get = event_get or False
        self.var_name = var_name or ""


class Request:
    def __init__(self, data: RequestData) -> None:
        self.data: RequestData = data

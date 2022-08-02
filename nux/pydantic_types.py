import pydantic


Phone = pydantic.constr(regex=r"^\+7\d{10}$")

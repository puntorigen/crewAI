from typing import Type, get_args, get_origin, Union
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PydanticSchemaParser(BaseModel):
    model: Type[BaseModel]

    def get_schema(self) -> str:
        """
        Public method to get the schema of a Pydantic model.
        :return: String representation of the model schema.
        """
        return "{\n" + self._get_model_schema(self.model) + "\n}"

    def _get_model_schema(self, model: Type[BaseModel], depth=0) -> str:
        lines = []
        indent = ' ' * 4 * (depth + 1)
        for field_name, field_info in model.model_fields.items():
            print(f"DEBUG field_name: {field_name}, field_info:",field_info)
            field_type = field_info.type_
            field_type_str = self._get_field_type(field_type, depth + 1)
            lines.append(f"{indent}'{field_name}': {field_type_str}")

        return ",\n".join(lines)

    def _get_field_type(self, field_type, depth) -> str:
        origin = get_origin(field_type)
        args = get_args(field_type)

        if origin is list:
            item_type = args[0]
            if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                nested_schema = self._get_model_schema(item_type, depth + 1)
                return f"[{{\n{nested_schema}\n{' ' * 4 * depth}}}]"
            else:
                return f"[{item_type.__name__}]"
        elif origin is Union:
            types = ", ".join([self._get_field_type(arg, depth) for arg in args if arg is not type(None)])
            return f"Union[{types}]"
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return f"{{\n{self._get_model_schema(field_type, depth)}\n{' ' * 4 * depth}}}"
        elif isinstance(field_type, type):
            return f"'{field_type.__name__}'"
        else:
            return f"'{str(field_type)}'"  # Fallback for other complex types
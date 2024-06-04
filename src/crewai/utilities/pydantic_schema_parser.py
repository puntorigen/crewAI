from typing import Type, get_args, get_origin
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class PydanticSchemaParser(BaseModel):
    model: Type[BaseModel]

    def get_schema(self) -> str:
        """
        Public method to get the schema of a Pydantic model.

        :param model: The Pydantic model class to generate schema for.
        :return: String representation of the model schema.
        """
        return self._get_model_schema(self.model)

    def _get_model_schema(self, model: Type[BaseModel], depth=0) -> str:
        lines = []
        for field_name, field_info in model.__fields__.items():
            field_type_str = self._get_field_type(field_info.outer_type_, depth + 1)
            lines.append(f"{' ' * 4 * depth}- {field_name}: {field_type_str}")

        return "\n".join(lines)

    def _get_field_type(self, field_type, depth) -> str:
        origin = get_origin(field_type)
        args = get_args(field_type)

        if origin is list:  # This covers cases like List[x]
            item_type = args[0]
            if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                nested_schema = self._get_model_schema(item_type, depth + 1)
                return f"List[\n{nested_schema}\n{' ' * 4 * depth}]"
            else:
                return f"List[{item_type.__name__}]"
        elif origin is Union:  # This covers Optional[x] and other unions
            types = ", ".join([self._get_field_type(arg, depth) for arg in args])
            return f"Union[{types}]"
        elif isinstance(field_type, type) and issubclass(field_type, BaseModel):
            return f"\n{self._get_model_schema(field_type, depth)}"
        elif isinstance(field_type, type):
            return field_type.__name__
        else:
            return str(field_type)  # Fallback for other complex types
import copy
import pydantic


def rehydrate_partial(model: pydantic.BaseModel, partial: dict, **props):
    return model.parse_obj(
        copy.deepcopy(partial)
            .update(props)
    )
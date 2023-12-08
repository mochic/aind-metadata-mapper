from aind_data_schema import rig, base



# def recurse_aind_model(model: base.AindModel) -> None:
#     for field_name, field_value in model.__fields__.items():
#         if isinstance(field_value, base.AindModel):
#             return (field_name, recurse_aind_model(field_value), )
#         elif isinstance(field_value, list):
#             return (field_name, list(map(
#                 recurse_aind_model,
#                 field_value,
#             ), ))
#         else:
#             return (field_name, field_value, )
        

def recurse_aind_model(model: base.AindModel) -> None:
    for field_name, field_value in model.__fields__.items():
        if isinstance(field_value, base.AindModel):
            return (field_name, recurse_aind_model(field_value), )
        elif isinstance(field_value, list):
            return (field_name, list(map(
                recurse_aind_model,
                field_value,
            ), ))
        else:
            return (field_name, field_value, )


def update_rig(*updates: base.AindModel, rig: rig.Rig) -> rig.Rig:
    updated = {}
    for update in updates:
        for prop_name, prop_value in recurse_aind_model(rig):
            if issubclass(prop_value, update.__class__):
                merge_models()
        else:
            pass
            merge_devices(rig.devices[device_name], device)


# if __name__ == "__main__":
#     sys_args = sys.argv[1:]
#     etl = SubjectEtl.from_args(sys_args)
#     etl.run_job()
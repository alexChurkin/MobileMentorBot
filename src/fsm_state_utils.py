from aiogram.fsm.context import FSMContext


# Переопределяет текущее состояние целиком
async def rewrite_state(state: FSMContext, new_data: dict):
    await state.set_data(new_data)


# Добавляет к текущему состоянию новые поля из new_data
# (также может перезаписать поля, если они уже были заданы ранее)
async def edit_state(state: FSMContext, new_data: dict):
    old_data = await state.get_data()
    updated_data = dict()
    # Записываются старые данные
    for key, value in old_data.items():
        updated_data[key] = value

    # Поверх записываются новые
    for key, value in new_data.items():
        updated_data[key] = value

    await state.set_data(updated_data)

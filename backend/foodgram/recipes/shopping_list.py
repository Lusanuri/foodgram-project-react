def get_shopping_list(shopping_cart):
    list_of_ingredients = {}
    content = "----------- Список покупок -----------\n\n"
    for recipe in shopping_cart:
        items = recipe.recipe_ingredient.select_related("ingredient").all()
        for item in items:
            in_list = list_of_ingredients.get(item.ingredient)
            if in_list:
                list_of_ingredients[item.ingredient] += item.amount
            else:
                list_of_ingredients[item.ingredient] = item.amount
    for ingredient, amount in list_of_ingredients.items():
        content += (f"* {ingredient} ({ingredient.measurement_unit})" +
                    f" — {amount}\n")
    content += "\n--------------------------------------"
    return content

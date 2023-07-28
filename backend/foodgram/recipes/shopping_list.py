from django.http import HttpResponse


def get_shopping_list(request):
    filename = "products_for_recipes.txt"
    content = "----------- Список покупок -----------\n\n"
    list_of_ingredients = {}
    cart = request.user.shopping_cart.select_related("recipe").all()
    recipes_in_cart = [item.recipe for item in cart]
    for recipe in recipes_in_cart:
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
    response = HttpResponse(content, content_type="text/plain")
    response["Content-Disposition"] = ("attachment; " +
                                       "filename={0}".format(filename))
    return response

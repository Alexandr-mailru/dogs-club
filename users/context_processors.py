def roles(request):
    user = request.user
    is_mod = False
    if user.is_authenticated:
        is_mod = getattr(user, "role", None) in ("admin", "moderator") or user.is_staff
    return {"is_moderator": is_mod}

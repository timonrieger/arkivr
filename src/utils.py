from sqlalchemy import or_


def get_ressources(db, ressource_model, user_model, cache=None, filter=None):
    if filter:
        search_filters = [
            or_(
                ressource_model.name.ilike(f"%{search_arg}%"),
                ressource_model.description.ilike(f"%{search_arg}%"),
                ressource_model.category.ilike(f"%{search_arg}%"),
                ressource_model.tags.ilike(f"%{search_arg}%"),
                ressource_model.medium.ilike(f"%{search_arg}%"),
                ressource_model.link.ilike(f"%{search_arg}%"),
            )
            for search_arg in filter
        ]
        return (
            db.session.query(ressource_model, user_model.username)
            .join(user_model, user_model.id == ressource_model.user_id)
            .filter(or_(*search_filters))
            .order_by(ressource_model.added.desc())
            .all()
        )
    else:
        ressources = cache.get("all_ressources")
        if not ressources:
            ressources = (
                db.session.query(ressource_model, user_model.username)
                .join(user_model, user_model.id == ressource_model.user_id)
                .order_by(ressource_model.added.desc())
                .all()
            )
            cache.set("all_ressources", ressources, timeout=60 * 60 * 24 * 7 * 52)
        return ressources


def get_missing_fields(data, required):
    missing = []
    for r in required:
        if r not in data:
            missing.append(r)
    return missing

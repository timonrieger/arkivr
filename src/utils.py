from sqlalchemy import or_

def get_ressources(ressource_model, cache=None, filter=None):
  if filter:
      print(f"filter {filter}")
      search_filters = [
        or_(
            ressource_model.name.ilike(f"%{search_arg}%"),
            ressource_model.description.ilike(f"%{search_arg}%"),
            ressource_model.category.ilike(f"%{search_arg}%"),
            ressource_model.tags.ilike(f"%{search_arg}%"),
            ressource_model.medium.ilike(f"%{search_arg}%"),
            ressource_model.link.ilike(f"%{search_arg}%"),
        ) for search_arg in filter
      ]
      return ressource_model.query.filter(or_(*search_filters)).order_by(ressource_model.added.desc()).all()
  else:
    ressources = cache.get('all_ressources')
    if not ressources:
        ressources = ressource_model.query.order_by(ressource_model.added.desc()).all()
        cache.set('all_ressources', ressources, timeout=60 * 60 * 24 * 7 * 52)
    return ressources
  
def get_missing_fields(data, required):
    missing = []
    for r in required:
        if r not in data:
            missing.append(r)
    return missing
from rest_framework import filters


class CustomSearchFilter(filters.SearchFilter):
    def get_search_fields(self, view, request):
        has_params = request.query_params
        if has_params:
            mapping = {'genre': 'genre__slug',
                       'category': 'category__slug',
                       'year': 'year',
                       'name': 'name'
                       }
            for search, field in mapping.items():
                if request.query_params.get(search):
                    self.search_param = search
                    return [field]
        return super(CustomSearchFilter, self).get_search_fields(view, request)

import string

from django.db.models import Q

from django.views.generic.list_detail import object_list
from django.db import connection

from glossary.models import Term

def term_list(request, **kwargs):
    """
    Return a list of all terms

    """

    ec = {"a_z": string.lowercase}

    # NOTE: This does nothing until Django 1.2 arrives with support for
    # reverse relationships in select_related(). In the meantime it'd be
    # necessary to do something ugly like retrieve synonyms and restructure the
    # data within Python. Caching is easier...
    terms = Term.objects.select_related("synonyms")

    if "q" in request.GET:
        query = request.GET['q']
        ec['query'] = query
        terms = terms.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(synonyms__title__icontains=query)
        ).distinct()
    else:
        initial = request.GET.get("l", "a").lower()
        ec['starts_with'] = initial
        terms = terms.filter(title__istartswith=ec['starts_with'])

    terms = terms.extra(select={"lower_title": "LOWER(%s.title)" % Term._meta.db_table }).order_by("lower_title")
    
    used_letters = []
    
    # Optimized version for Postgres:
    if connection.client.executable_name == "psql":
        cursor = connection.cursor()
        cursor.execute("""SELECT DISTINCT LOWER(SUBSTR(title, 1, 1)) AS initial FROM glossary_term ORDER BY initial""")
        used_letters = [ i[0] for i in cursor.fetchall() ]
    else:
        for i in ec["a_z"]:
            # NOTE: In Django 1.2 this could be .exists():
            if Term.objects.filter(title__istartswith=i).count() > 0:
                used_letters.append(i)

    return object_list(request, 
                        queryset=terms, 
                        extra_context={'ec': ec,
                                        'starts_with': ec['starts_with'],
                                        'a_z': ec['a_z'],
                                        'used_letters': used_letters},
                        **kwargs)

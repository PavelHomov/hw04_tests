from django.core.paginator import Paginator

from .constants import POSTS_PAGE


def paginator_func(request, post_list):
    """Функция paginator."""
    paginator_variable = Paginator(post_list, POSTS_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator_variable.get_page(page_number)

    return page_obj

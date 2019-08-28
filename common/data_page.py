from django.core.paginator import Paginator


def pagination(data, page_size, page, page_type=1):
    """
    分页
    :param data: 需要进行分页的数据
    :param page_size: 每页放置多少数据
    :param page: 当前页码
    :param page_type 分页栏是显示风格
                    1:显示省略号
                    2：只显示5页数据，没有省略号
    :return: page对象和页码范围对象
    """
    # page_size = 1
    paginator = Paginator(data, per_page=page_size)

    # 获取第page页内容
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 如果当前页码大于总页数，则显示第一页
    if page > paginator.num_pages:
        page = 1

    data_page = paginator.page(page)

    # 对页码进行特殊控制
    # 1.如果总页数小于等于5页则显示所有页
    num_pages = paginator.num_pages
    if page_type == 1:
        if num_pages <= 5:
            pages = range(1, num_pages + 1)  # [1,2,3,4,5]

        # 2.如果当前页是前3页则显示前5页 [1,2,3,4,5,6]
        elif page <= 3:
            pages = list([1, 2, 3, '...', num_pages])

        # 3.如果当前页是后3页则显示后5页
        elif num_pages - page <= 2:  # [1,2,3,4,5,6]
            pages = list([1, 2, '...',num_pages-2, num_pages-1, num_pages])

        # 4.如果是其它情况，则显示当前页的前两页，当前页，当前页的后两页
        else:
            page = int(page)
            pages = list([1, '...', page-1, page, page+1, '...', num_pages])
    else:
        if num_pages <= 5:
            pages = range(1, num_pages+1)  # [1,2,3,4,5]

        # 2.如果当前页是前3页则显示前5页 [1,2,3,4,5,6]
        elif page <= 3:
            pages = range(1, 6)

        # 3.如果当前页是后3页则显示后5页
        elif num_pages - page <= 2:  # [1,2,3,4,5,6]
            pages = range(num_pages-4, num_pages+1)

        # 4.如果是其它情况，则显示当前页的前两页，当前页，当前页的后两页
        else:
            pages = range(page - 2, page + 3)

    return data_page, pages



def index_conversion(page_no, local_paginate, remote_paginate):
    """
    Returns a tuple with two tuples:
        (
            (startpage_remote, startitem_remote),
            (endpage_remote, enditem_remote)
        )
    indexes start at 0
    """
    startitem = (page_no-1) * local_paginate  # first item to show
    enditem = (page_no * local_paginate) -1
    startpage_remote = startitem // remote_paginate
    startitem_remote = startitem % remote_paginate
    endpage_remote = enditem // remote_paginate
    enditem_remote = enditem % remote_paginate

    return ( (startpage_remote, startitem_remote),
             (endpage_remote, enditem_remote)
           )

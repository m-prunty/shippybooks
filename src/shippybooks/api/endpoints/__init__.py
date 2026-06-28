# *************************************************************************** #
#                                                                             #
#                                                        :::      ::::::::    #
#    __init__.py                                       :+:      :+:    :+:    #
#                                                    +:+ +:+         +:+      #
#    By: maprunty <maprunty@student.42heilbronn.d  +#+  +:+       +#+         #
#                                                +#+#+#+#+#+   +#+            #
#    Created: 2026/06/26 17:04:42 by maprunty         #+#    #+#              #
#    Updated: 2026/06/26 17:05:07 by maprunty        ###   ########.fr        #
#                                                                             #
# *************************************************************************** #

from .books import router as books_router
from .notifications import router as notifications_router
from .orders import router as orders_router

__all__ = ["books_router", "orders_router", "notifications_router"]

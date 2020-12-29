from PyMimircache.cache.lru import LRU
from PyMimircache.cache.fifo import FIFO

class T2(LRU):
    def __init__(self, size, ghostlist, **kwargs):
        super().__init__(size, **kwargs)
        self.ghostlist = ghostlist
    
    def access(self, req_item, **kwargs):
        """
        request access cache, it updates cache metadata,
        it is the underlying method for both get and put

        :param **kwargs:
        :param req_item: 
        :return: None
        """

        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id

        if self.has(req_id):
            self._update(req_item)
            return True
        else:
            self._insert(req_item)
            if len(self.cacheline_dict) > self.cache_size:
                evict_item = self.evict()
                self.ghostlist.access(evict_item)
            return False

class FIFO_POP_HIT(FIFO):
    def __init__(self, size, promote_list, **kwargs):
        super().__init__(size, **kwargs)
        self.promote_list = promote_list 

    def _update(self, req_id, **kwargs):
        self.cacheline_dict.move_to_end(req_id, last=False)
        evict_item = self.evict()
        self.promote_list.access(evict_item)


class T1(T2, FIFO_POP_HIT):
    def __init__(self, size, ghostlist, promote_list, **kwargs):
        T2.__init__(size, ghostlist, **kwargs)
        FIFO_POP_HIT.__init__(size, promote_list, **kwargs)
        
        
class ARC:
    def __init__(self, cache_size):
        self.cache_size = cache_size 

        self.b2 = FIFO_POP_HIT(cache_size/2)


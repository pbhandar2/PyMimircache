# coding=utf-8
"""
Pranav Bhandari 

- Rewrote ARC for PyMimircache (last tested 12/28/2020 using ../../test/testCacheAlg/test_ARC.py)
"""

from PyMimircache.cache.abstractCache import Cache
from PyMimircache.cache.lru import LRU
from PyMimircache.cache.fifo import FIFO
from PyMimircache.cacheReader.requestItem import Req

class InsertEvictLRU(LRU):
    def __init__(self, cache_size, **kwargs):
        """
        This class uses a LRU but instead of a simple insert, 
        it does insert and also returns the evicted item if there is 
        one. 

        This is used to implement the top lists or the main cache, T1 
        and T2. If an item is evicted on an insertion to T1 or T2, it 
        has to be returned because the evicted items need to be recorded
        in the ghost lists. 

        :param **kwargs:
        :param cache_size: 
        """
        super().__init__(cache_size, **kwargs)

    def access(self, req_item, **kwargs):
        """
        On cache access, update the cache and return a hit flag 
        and the evicted item if there is one. 

        :param **kwargs:
        :param req_item: cache request 
        :return: hit flag, evicted item 
        """

        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id

        evict_item = None 
        if self.has(req_id):
            self._update(req_item)
            return True, evict_item
        else:
            self._insert(req_item)
            if len(self.cacheline_dict) > self.cache_size:
                evicted_item = self.evict()
            return False, evict_item 

class HitEvictFIFO(FIFO):
    def __init__(self, cache_size, **kwargs):
        """
        This class uses a FIFO but on a cache hit, it evicts the item
        that was hit. 

        This is used to implement the ghost list where on a hit, the item id 
        has to be evicted. This is also true for the T1 list where on a hit, 
        the item is evicted from T1 and promoted to T2. 

        :param **kwargs:
        :param cache_size: 
        """
        super().__init__(cache_size, **kwargs)

    def _update(self, req_id, **kwargs):
        """
        On a cache hit, evict and return the item. 

        :param **kwargs:
        :param req_id: the cache request id 
        """
        self.cacheline_dict.move_to_end(req_id, last=False)
        evict_item = self.evict()
        return evict_item 

    def access(self, req_item, **kwargs):
        """
        On cache access, update the cache and return a hit flag 
        and the evicted item if there is one. 

        :param **kwargs:
        :param req_item: the cache request 
        :return: hit flag, evicted item 
        """

        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id

        evict_item = None 
        if self.has(req_id):
            evict_item = self._update(req_item)
            return True, evict_item 
        else:
            self._insert(req_item)
            if len(self.cacheline_dict) > self.cache_size:
                evict_item = self.evict()
            return False, evict_item 


class T1(HitEvictFIFO, InsertEvictLRU):
    def __init__(self, cache_size, **kwargs):
        """
        This class represents the T1 list that requires both characteristics 
        of evict on hit from HitEvictFIFO, when there is a hit in T1 and the 
        item has to be removed from T1 and promoted to T2, and InsertEvictLRU,
        when size of T1 is greater than the target size (p) and there is an eviction 
        from T1 to B1. 

        :param **kwargs:
        :param cache_size: 
        """
        HitEvictFIFO.__init__(self, cache_size, **kwargs)
        InsertEvictLRU.__init__(self, cache_size, **kwargs)


class ARC(Cache):
    def __init__(self, cache_size, ghostlist_size=-1, **kwargs):
        """
        ARC (Adaptive Replacement Cache) replacement policy. 

        :param cache_size: the cache size which is split into L1 and L2, also 
            the maximum possible size of L1 and L2
        :param ghostlist_size: the size of the ghost list of L1 and L2, defaults 
            to half the size of the cache 
        :return: None 
        """

        super().__init__(cache_size, **kwargs)
        self.p = 0
        self._lambda = 1 
        self.count = 0 # for debug 
        
        if ghostlist_size == -1:
            self.ghostlist_size = self.cache_size/2

        self.t1 = T1(cache_size)
        self.t2 = InsertEvictLRU(cache_size)
        self.b1 = HitEvictFIFO(self.ghostlist_size)
        self.b2 = HitEvictFIFO(self.ghostlist_size)
        
    def has(self, req_id, **kwargs):
        """
        :param **kwargs:
        :param req_id: the element for search
        :return: whether the request id is in the cache 
        """
        if self.t1.has(req_id) or self.t2.has(req_id):
            return True
        else:
            return False

    def _replace(self, req_id, **kwargs):
        """
        The replace subroutine, evict a page from either T1 or T2 and demote 
        a cache entry from B1 or B2 respectively, based on the value of the 
        tuning parameter p and the size of T1. 

        :param **kwargs:
        :param req_id: the cache request id 
        :return: None
        """

        if len(self.t1)>0 and (len(self.t1)>self.p or (self.b2.has(req_id) and len(self.t1)==self.p)):
            evict_id = self.t1.evict()
            self.b1.access(evict_id)
        else:
            if len(self.t2) > 0:
                evict_id = self.t2.evict()
                self.b2.access(evict_id)

    def ghost_has(self, req_id, **kwargs):
        """
        :param req_id: the cache request id 
        :return: whether the request id is in the ghost cache 
        """

        if self.b1.has(req_id) or self.b2.has(req_id):
            return True
        else:
            return False

    def _update(self, req_id, **kwargs):
        """ 
        On a ARC cache hit, if hit item in T1, promote 
        to T2, else update in T2. 
             
        :param **kwargs:
        :param req_id: the cache request id 
        :return: None
        """

        if self.t1.has(req_id):
            _, evict_item = self.t1.access(req_id)
            self.t2._insert(evict_item)
        elif self.t2.has(req_id):
            self.t2._update(req_id)


    def _ghost_update(self, req_id, **kwargs):
        """ 
        When there is a hit in the ghost cache, evict a page
        from either T1 or T2 based on tuning parameter p and 
        size of T1, then admit the hit item to T2. 

        :param **kwargs:
        :param req_id: the cache request id 
        :return: None
        """

        # CASE 2: item is in b1
        if self.b1.has(req_id):
            self.p = min(self.p+self._lambda, self.cache_size)
            self.b1._update(req_id)
        elif self.b2.has(req_id):
            # CASE 3: item is in b2
            self.p = max(self.p-self._lambda, 0)
            self.b2._update(req_id)
        
        self._replace(req_id)
        self.t2._insert(req_id)


    def _insert(self, req_id, **kwargs):
        """
        :param **kwargs:
        :param req_id:
        :return: None 
        """
        self.t1._insert(req_id)

    def evict(self, **kwargs):
        """
        evict one element from the cache line into ghost list, then check ghost list,
        if oversize, then evict one from ghost list
        :param **kwargs:
        :param: element: the missed request
        :return: content of element evicted into ghost list
        """
        pass

    def access(self, req_item, **kwargs):
        """
        :param **kwargs: 
        :param req_item: the element in the reference, it can be in the cache, or not
        :return: None
        """

        # make sure the end of file is reached for testing 
        if self.count > 113870:
            print("Access {}".format(req_item))
        self.count += 1

        # CASE 1: item is in t1 or t2 (cache hit)
        if self.has(req_item):
            self._update(req_item)
            return True
        else:

            # CASE 2 and 3: Found in ghostlist, still a cache miss 
            if self.ghost_has(req_item):
                self._ghost_update(req_item)
            else:
                # CASE 4: Cache Miss

                # CASE 4A
                if len(self.t1)+len(self.b1) == self.cache_size:
                    if len(self.t1) < self.cache_size:
                        self.b1.evict()
                        self._replace(req_item)
                    else:
                        self.t1.evict()
                elif len(self.t1)+len(self.b1) < self.cache_size:
                    # CASE 4B
                    if len(self.t1)+len(self.b1)+len(self.t2)+len(self.b2) >= self.cache_size:
                        if len(self.t1)+len(self.b1)+len(self.t2)+len(self.b2) == 2*self.cache_size:
                            self.b2.evict()
                        self._replace(req_item)

                self.t1._insert(req_item)

            return False

    def __repr__(self):
        return "ARC, given size: {}, T1 size: {}, T2 size: {}, B1 size: {}, B2 size: {}, target T1 size (p): {}".format(
            self.cache_size, len(self.t1), len(self.t2), len(self.b1), len(self.b2), self.p)

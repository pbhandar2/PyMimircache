import sys
import os
import random

from mimircache.cache.abstractCache import cache
from mimircache.utils.LinkedList import LinkedList


class RR(cache):
    def __init__(self, cache_size=1000):
        super().__init__(cache_size)
        self.cacheDict = dict()  # key -> linked list node (in reality, it should also contains value)
        self.cache_line_list = []  # to save all the keys, otherwise needs to populate from cache_dict every time


    def checkElement(self, element):
        '''
        :param element: the key of cache request
        :return: whether the given key is in the cache or not
        '''
        if element in self.cacheDict:
            return True
        else:
            return False

    def _updateElement(self, element):
        ''' the given element is in the cache, when it is requested again,
         usually we need to update it to new location, but in random, we don't need to do that
        :param element: the key of cache request
        :return: None
        '''

        pass

    def _insertElement(self, element):
        '''
        the given element is not in the cache, now insert it into cache
        :param element: the key of cache request
        :return: None
        '''
        if len(self.cacheDict) >= self.cache_size:
            self._evictOneElement()
        self.cacheDict[element] = ""
        self.cache_line_list.append(element)

    def _printCacheLine(self):
        for i in self.cacheDict:
            try:
                print(i.content, end='\t')
            except:
                print(i.content)

        print(' ')

    def _evictOneElement(self):
        '''
        evict one element from the cache line
        if we delete one element from list every time, it would be O(N) on
        every request, which is too expensive, so we choose to put a hole
        on the list every time we delete it, when there are too many holes
        we re-generate the cache line list
        :return: None
        '''
        rand_num = random.randrange(0, len(self.cache_line_list))
        element = self.cache_line_list[rand_num]
        count = 0
        while not element:
            rand_num = random.randrange(0, len(self.cache_line_list))
            element = self.cache_line_list[rand_num]
            count += 1

        # mark this element as deleted, put a hole on it
        self.cache_line_list[rand_num] = None

        if (count > 10):
            # if there are too many holes, then we need to resize the list
            new_list = [e for e in self.cache_line_list if e]
            del self.cache_line_list
            self.cache_line_list = new_list

        del self.cacheDict[element]

    def addElement(self, element):
        '''
        :param element: the key of cache request, it can be in the cache, or not in the cache
        :return: True if element in the cache
        '''
        if self.checkElement(element):
            self._updateElement(element)
            return True
        else:
            self._insertElement(element)
            return False

    def __repr__(self):
        return "Random Replacement, given size: {}, current size: {}".format(self.cache_size,
                                                                             len(self.cacheDict),
                                                                             super().__repr__())

# coding=utf-8
"""
this module provides unittest for ARC replacement policy
"""

import os
import sys
import random 
sys.path.append(os.path.join(os.getcwd(), "../"))
import unittest

from PyMimircache.cacheReader.plainReader import PlainReader
from PyMimircache.profiler.pyGeneralProfiler import PyGeneralProfiler
from PyMimircache.cache.arc import ARC

DAT_FOLDER = "../data/"
if not os.path.exists(DAT_FOLDER):
    if os.path.exists("../../data/"):
        DAT_FOLDER = "../../data/"
    elif os.path.exists("../../PyMimircache/data/"):
        DAT_FOLDER = "../../PyMimircache/data/"
    elif os.path.exists("../PyMimircache/data/"):
        DAT_FOLDER = "../PyMimircache/data/"
    else:
        raise RuntimeError("cannot find data")


class ARCAlgTest(unittest.TestCase):

    def get_hot_cache(self, cache_size):
        """
        return a hot ARC cache 
        """
        arc_cache = ARC(cache_size)
        for i in range(arc_cache.cache_size):
            arc_cache.access(i)

            # p should not be updated and size of T1 and T2 should be constrained 
            self.assertTrue(len(arc_cache.t1)+len(arc_cache.t2)<=arc_cache.cache_size)
            self.assertTrue(arc_cache.p==0)
        return arc_cache

    def fill_half_t2(self, arc_cache, cache_size):
        cache_list = list(arc_cache.t1.cacheline_dict.items())
        for i in range(int(cache_size/2)):
            arc_cache.access(cache_list[i][0])
        return arc_cache 

    def add_cache_miss(self, arc_cache, cache_size, num_miss):
        for i in range(cache_size, cache_size+num_miss):
            arc_cache.access(i)
        return arc_cache

    def add_cache_hits(self, arc_cache, num_hits):
        pass

    def case_1(self, cache_size):

        arc_cache = self.get_hot_cache(cache_size)

        # L1 Hit 

        # the last request should be in L1 but not in L2         
        self.assertTrue(arc_cache.t1.has(cache_size-1))
        self.assertFalse(arc_cache.t2.has(cache_size-1))

        arc_cache.access(cache_size-1)

        # now the request should be in L2 but not in L1 
        self.assertFalse(arc_cache.t1.has(cache_size-1))
        self.assertTrue(arc_cache.t2.has(cache_size-1))

        # L2 Hit 
        # check to make sure the first entry of T2 is cache_size-1 
        self.assertTrue(next(reversed(arc_cache.t2.cacheline_dict)), cache_size-1)

        # add elements to L2 list with some L1 hits 
        arc_cache.access(cache_size-2)

        # check to make sure the first entry of T2 is now cache_size-2 from cache_size-1 
        self.assertTrue(next(reversed(arc_cache.t2.cacheline_dict)), cache_size-2)

        arc_cache.access(cache_size-1)

        # check to make sure the first entry of T2 is back to cache_size-1 from cache_size-2 
        self.assertTrue(next(reversed(arc_cache.t2.cacheline_dict)), cache_size-1)

    def case_2(self, cache_size):
        
        arc_cache = self.get_hot_cache(cache_size)

        # Setup the cache 
        arc_cache = self.fill_half_t2(arc_cache, cache_size)
        arc_cache = self.add_cache_miss(arc_cache, cache_size, 3)

        # Case 2: Item found in B1

        # Subcase 1: T1 size > p 
        # Should evict from T1 and add to T2

        prev_t1_size = len(arc_cache.t1)
        prev_t2_size = len(arc_cache.t2)

        # B1 Hit 
        arc_cache.access(3)

        # T1 should decrease by 1 and T2 should increase by 1 
        self.assertTrue(prev_t1_size-1==len(arc_cache.t1))
        self.assertTrue(prev_t2_size+1==len(arc_cache.t2))

    def case_3(self, cache_size):

        arc_cache = self.get_hot_cache(cache_size)

        # Setup the cache 
        arc_cache = self.fill_half_t2(arc_cache, cache_size)
        arc_cache = self.add_cache_miss(arc_cache, cache_size, 3)

    def test_pyARC_miss_rate(self):
        sizes = [5,10,25,20,25,50,100,150,500]
        for s in sizes:
            arc_cache = ARC(s)
            reader = PlainReader("{}/trace.txt".format(DAT_FOLDER))
            req = reader.read_one_req()
            hit_count = 0 
            total_req = 0 
            while req:
                if arc_cache.access(req):
                    hit_count += 1
                total_req += 1
                req = reader.read_one_req()
            
            print(s, hit_count, total_req, total_req-hit_count, (total_req-hit_count)/total_req)


    def test_pyARC_plain(self):
        reader = PlainReader("{}/trace.txt".format(DAT_FOLDER))
        cache_size = 4

        self.case_1(cache_size)
        self.case_2(cache_size)
        self.case_3(cache_size)

        # # Fill the cache for future tests 
        # for i in range(25*cache_size):
        #     arc_cache.access(i, )

        #     # p should not be updated and size of T1 and T2 should be constrained 
        #     self.assertTrue(len(arc_cache.t1)+len(arc_cache.t2)<=arc_cache.cache_size)
        #     self.assertTrue(arc_cache.p==0)

        # # Test Case 1: x is in L1 or L2 

        # # the last request should be in L1 but not in L2         
        # self.assertTrue(arc_cache.t1.has(25*cache_size-1))
        # self.assertFalse(arc_cache.t2.has(25*cache_size-1))

        # arc_cache.access(25*cache_size-1)

        # # now the request should be in L2 but not in L1 
        # self.assertFalse(arc_cache.t1.has(25*cache_size-1))
        # self.assertTrue(arc_cache.t2.has(25*cache_size-1))


        # # Test Case 2: x is in B1 

        # # fill the L2 and empty out the L1 
        # for i in range(25*cache_size-2, 25*cache_size-5, -1):
        #     self.assertTrue(arc_cache.access(i))

        # # cause evictions to populate the B1 
        # self.assertFalse(arc_cache.access(25*cache_size-5)) 
        # self.assertFalse(arc_cache.access(25*cache_size-6)) 
        # self.assertFalse(arc_cache.access(25*cache_size-7)) 

        # prev_t1_size = len(arc_cache.t1) 
        # prev_t2_size = len(arc_cache.t2) 

        # # cause a hit in B1 
        # # Test Subcase: p=0, T1 size>0=1, so should shed T2 entry as p will be increased to 1 
        # self.assertFalse(arc_cache.access(25*cache_size-6))

        # # the item should be in T2 now 
        # self.assertTrue(arc_cache.t2.has(25*cache_size-6))

        # # T1 shouldnt have it 
        # self.assertFalse(arc_cache.t1.has(25*cache_size-6))

        # # B1 shouldn't have it 
        # self.assertFalse(arc_cache.b1.has(25*cache_size-6))

        # # Cache size should remain same. 
        # # This should cause evict from L2 and then admit again. 
        # self.assertTrue(prev_t2_size==len(arc_cache.t2))
        # self.assertTrue(prev_t1_size==len(arc_cache.t1))

        # # p is updated to 1 
        # self.assertTrue(arc_cache.p == 1)

        # prev_t1_size = len(arc_cache.t1) 
        # prev_t2_size = len(arc_cache.t2)


        # # cause another hit in B1
        # # Test SubCase: p=1, T1 size=1=p, so should shed t2 entry was p will be increased to 2 
        # self.assertFalse(arc_cache.access(25*cache_size-5))

        # # the item should be in T2 now 
        # self.assertTrue(arc_cache.t2.has(25*cache_size-5))

        # # T1 shouldnt have it 
        # self.assertFalse(arc_cache.t1.has(25*cache_size-5))

        # # p is updated to 2 
        # self.assertTrue(arc_cache.p == 2)

        # # B1 shouldn't have it 
        # self.assertFalse(arc_cache.b1.has(25*cache_size-6))

        # # Cache size should remain same. 
        # # This should cause evict from L2 and then admit again. 
        # self.assertTrue(prev_t2_size==len(arc_cache.t2))
        # self.assertTrue(prev_t1_size==len(arc_cache.t1))

        # # Test Case 3: B2 hit 

        # prev_t1_size = len(arc_cache.t1) 
        # prev_b2_size = len(arc_cache.b2)

        # # B2 Hit 
        # # Test Case: when p=2, l1_size=1 so p>l1_size, evict L2
        # self.assertFalse(arc_cache.access(25*cache_size-2))

        # # the item should be in T2 now 
        # self.assertTrue(arc_cache.t2.has(25*cache_size-2))

        # # T1 shouldnt have it 
        # self.assertFalse(arc_cache.t1.has(25*cache_size-2))

        # # p should decrease to 1 
        # self.assertTrue(arc_cache.p==1)

        # # test if the algorithm will drop an T1 page now and decrease T1 size
        # self.assertTrue(prev_t1_size==len(arc_cache.t1))
        # self.assertTrue(prev_t2_size==len(arc_cache.t2))

        # # a miss to increase L1 size and p 
        # self.assertFalse(arc_cache.access(25*cache_size-13))


        # prev_t1_size = len(arc_cache.t1) 
        # prev_b2_size = len(arc_cache.b2)

        # # B2 Hit 
        # # Test Case: when p is equal to T1 size and cache hit in B2 
        # self.assertFalse(arc_cache.access(25*cache_size-4))

        # # the item should be in T2 now 
        # self.assertTrue(arc_cache.t2.has(25*cache_size-4))

        # # T1 shouldnt have it 
        # self.assertFalse(arc_cache.t1.has(25*cache_size-4))

        # # p should decrease to 0
        # self.assertTrue(arc_cache.p==0)

        # # test if the algorithm will drop an T1 page now and decrease T1 size
        # assert(prev_t1_size-1==len(arc_cache.t1))
        # assert(prev_b2_size-1==len(arc_cache.b2))

        # # cache miss to increase the size of T1
        # self.assertFalse(arc_cache.access(25*cache_size-9))

        # prev_t1_size = len(arc_cache.t1) 
        # prev_b2_size = len(arc_cache.b2)

        # # Cache Miss
        # # Case 4B - A only replace 
        # self.assertFalse(arc_cache.access(25*cache_size-15))

        # # it should remove a L1 page and add one so no change in L1/L2 size  
        # assert(prev_t1_size==len(arc_cache.t1))
        # assert(prev_b2_size==len(arc_cache.b2))

        # arc_cache.access(25*cache_size-9)
        # arc_cache.access(25*cache_size-16)
        # arc_cache.access(25*cache_size-17)
        # arc_cache.access(25*cache_size-4)
        # arc_cache.access(25*cache_size-16)

        # print(arc_cache)
        
        # # Case 4B - B T1+T2+B1+B2=2c 
        # arc_cache.access(25*cache_size-18)

        # # should remove LRU page from B2 but then again add it back



if __name__ == "__main__":
    unittest.main()
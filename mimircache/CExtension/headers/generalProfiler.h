//
//  generalProfiler.h
//  generalProfiler
//
//  Created by Juncheng on 5/24/16.
//  Copyright © 2016 Juncheng. All rights reserved.
//

#ifndef generalProfiler_h
#define generalProfiler_h

#include <stdio.h>
#include <stdlib.h>
#include <glib.h>
#include "reader.h"
#include "glib_related.h"






long long* get_hit_count_seq(READER* reader, long size, long long begin, long long end);
float* get_hit_rate_seq(READER* reader, long size, long long begin, long long end);
float* get_miss_rate_seq(READER* reader, long size, long long begin, long long end);
long long* get_reuse_dist_seq(READER* reader, long long begin, long long end);
long long* get_rd_distribution(READER* reader, long long begin, long long end);
long long* get_reversed_reuse_dist(READER* reader, long long begin, long long end);


#endif /* generalProfiler_h */

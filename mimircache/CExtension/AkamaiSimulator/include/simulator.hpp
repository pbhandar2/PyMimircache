//
//  simulator.cpp
//  akamaiSimulator
//
//  Created by Juncheng on 7/11/17.
//  Copyright © 2017 Juncheng. All rights reserved.
//


#ifndef simulator_HPP
#define simulator_HPP





#ifdef __cplusplus
extern "C"
{
#endif
    
#include <stdio.h>
#include <glib.h>
    
#include "cache.h"
#include "cacheHeader.h"
#include "reader.h"
#include "csvReader.h"
    
#ifdef __cplusplus
}
#endif



#include "constAkamaiSimulator.hpp"
#include "cacheLayer.hpp"
#include "cacheServer.hpp"
#include "cacheLayerThread.hpp"
#include "cacheServerThread.hpp"
#include "akamaiStat.hpp"




#define AKAMAI_CSV_PARAM_INIT (new_csvReader_init_params(5, -1, 1, -1, FALSE, '\t', -1))
#define AKAMAI3_CSV_PARAM_INIT (new_csvReader_init_params(6, -1, 1, -1, FALSE, '\t', -1))


namespace akamaiSimulator {
    
    
    void akamai_run(std::vector<std::string> traces,
                    double *boundaries,
                    unsigned long* cache_sizes,
                    int akamai_data_type);

}






#endif


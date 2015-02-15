 %module tsparser
  %{
  /* Includes the header in the wrapper code */
  #include "../src/TS_parser.h"
  %}
  
  %apply  const char *STRING_ARRAY { const char *ts_raw_data}

  /* Parse the header file to generate wrappers */
  %include "../src/TS_parser.h"
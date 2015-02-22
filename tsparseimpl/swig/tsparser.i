 %module tsparser
  %{
  /* Includes the header in the wrapper code */
  	extern unsigned ts_get_type(const char *ts_raw_data);
  %}
  
  /*%apply  const char *STRING_ARRAY { const char *ts_raw_data}*/

	extern unsigned ts_get_type(const char *ts_raw_data);
 
 

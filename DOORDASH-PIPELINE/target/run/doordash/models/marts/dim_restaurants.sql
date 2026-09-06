
  
    

        create or replace transient table DOORDASH.marts.dim_restaurants
         as
        (select 
restaurant_id, 
restaurant_name, 
city, cuisine, 
rating, 
rating_count, 
cost_for_two
from DOORDASH.staging.stg_restaurants
        );
      
  
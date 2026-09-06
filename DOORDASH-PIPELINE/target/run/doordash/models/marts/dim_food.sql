
  
    

        create or replace transient table DOORDASH.marts.dim_food
         as
        (select f_id, food_name, veg_or_non_veg from DOORDASH.staging.stg_food
        );
      
  
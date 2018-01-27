# Environmental Visual Examiner (EVE)
***College of the Canyons Association of Computing Machinery Research Project***
- [**CIMIS - Weather Data API**](http://et.water.ca.gov/Home/Index)

View our [**project abstraction**](https://docs.google.com/document/d/1yDm8ZhQO4J5V0nz4npQUcugwjEzfE0l4rJVBd1Fd8Nk/edit?usp=sharing) for a summary of how this system should work. To view more of the research completed so far, view our [**google drive**](https://drive.google.com/drive/folders/0B4uU1kLqkZiAc2NfbnluOFQxalk?usp=sharing)

## Design
This configuration is using AWS IoT, DynamoDB, and Lambda services from AWS. A pre-defined **eve_user** table in DynamoDB holds information about the user's garden plot for querying. An MQTT client is setup through AWS IoT to subscribe and publish from/to the raspberry pi at scheduled intervals using configuration details from [sensor_reader.py](https://github.com/cocacm/eve-pi/blob/master/sensor_reader.py) (certification must be created and linked to the pi using the topic **thing01/data**). A rule is then used to insert published sensor values into our DynamoDB **eve_data** table.

From DynamoDB, our [water_alg](https://github.com/cocacm/eve-aws/tree/master/water_alg) Lambda function is triggered, which requests eto from the CIMIS API, queries the plant factor from our **eve_pf** table, and calculates whether watering is required. The results are then written back to the same item in our **eve_data** table. Lasty, an MQTT message is published back to the pi with watering instructions, which are then executed.

## DynamoDB
Three tables are used for the execution of this pipeline, their names and schema are listed below, strings are used for most of the attributes to maintain the integrity of the data when storing:

**eve_user** - **pre-defined values, create an item for testing*
- *user_id*: String (PRIMARY KEY)
- *location*: String (SORT KEY)
- *date_created*: String
- *plant_spec*: String
- *plant_type*: String
- *plot_size*: String

**eve_pf** - **uses information from [UCANR](http://ucanr.edu/sites/UrbanHort/Water_Use_of_Turfgrass_and_Landscape_Plant_Materials/Plant_Factor_or_Crop_Coefficient__What%E2%80%99s_the_difference/) resources**
- *plant_type*: String (PRIMARY KEY)
- *plant_factor*: Number

**eve_data** - **lists with sensor, user, and alg info are inserted into this table**
- *date_time*: String (PRIMARY KEY)
- *data*: Dict
  * *date_time*: String (PRIMARY KEY)
  * *temp*: Number
  * *humid*: Number
  * *light*: Number
  * *moist*: Number
- *user_info*: List
  * *0*: String (user_id)
  * *1*: String (plant_type)
  * *2*: String (plant_spec)
  * *3*: String (plot_size)
- *water_alg*: List
  * *0*: String (pf)
  * *1*: String (eto)
  * *2*: String (gal_water_reserve)
  
## Lambda
When configuring the Lambda function, a DynamoDB trigger must be selected to invoke the function when an item is inserted into the **eve_data** table. A deployment package (zip) must also be created which contains the dependencies for the function installed directly into the project folder. To do this, run `pip3 install requests -t <project_folder>` The zip must then be uploaded to Lambda and unpacked so that AWS may find the [**main.py**](https://github.com/cocacm/eve-aws/blob/master/water_alg/main.py) script. The handler for the Lambda function is *main.water_alg*

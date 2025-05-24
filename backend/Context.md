# Field

Field features are great for entity enrichments from one-to-one or many-to-one relations. It is commonly used to enrich an entity with simple, non aggregate fields from related assets or entities.

Main use cases

1. Add a field feature from a data asset with the same level of granularity as the entity (one-to-one relationship)

2. Add a field feature from a related entity with one-to-one relationship

3. Add a feature from a parent entity (many-to-one relationship)

Simple field feature

In this example, we define two simple `field` features for the entity `customer`:

# customer.yml
features: 

- type: field
  name: organization_size
  asset: db_prod.core.organizations
  field: size
  data_type: number
  filters: null
  
- type: field
  name: is_us_customer
  asset: db_prod.core.geos
  join_name: login_geo
  data_type: boolean
  field: iff(name = 'US', true, false)
  filters: null

type
The feature type. 
In case of field features, it should be set to field.

name
Give the field feature a name. 

asset
The data asset with the field to be added as feature to our entity.
asset should be the full path: "db.schema.name".

asset has to be related to our entity (see related data asset).

join_name [optional]
In case multiple join patterns are defined between an entity and a data asset, join_name is used to determine which join path to use for a specific feature.

In the example above, we are joining the entity customer to the geos asset using the login_geo join path name. For more information about using multiple join paths between an entity and a data asset, visit the related data assets page.

data_type [optional]
Specify the feature data type. 
If no data_type specified, Lynk will assume the data type is string.

The options for data types are:

string - For any type of string data type

number - For any type of number data type. For example: integer, float, decimal etc..

bool - For boolean data type.

datetime  - For any type of time-based data type. For example: date, timestamp, datetime etc..

field 
The name of the field we would like to get from the related asset, in order to enrich our entity. 

field can be any SQL expression which does not include aggregate functions. 

filters
Custom filters to be applied on the data asset. See filters page for in depth information on how to apply filters. 



# Metric 

Metric features are great for aggregations from one-to-many relations.
It is commonly used to enrich an entity with aggregated fields from one-to-many related assets or entities.

When we create a metric feature, we apply a measure aggregation to the level of an entity.

Simple metric feature
In this example, we define simple metric features for the entity customer:

Copy
# customer.yml

features:
  
- type: metric
  name: orders_count
  asset: db_prod.core.orders
  measure: orders_count
  data_type: number
  filters: null

- type: metric
  name: successful_orders_count
  asset: db_prod.core.orders
  measure: orders_count
  data_type: number
  time_field: order_date
  filters:
  - type: field
    field: order_status
    operator: is
    values:
    - success
type
The feature type.
In case of metric features, it should be set to metric.

name
Give the metric feature a name.

asset
The data asset with the measure to be aggregated to the level of our entity.
asset should be the full path: "db.schema.name".

asset has to be related to our entity (see related data asset).

join_name [optional]
In case multiple join patterns are defined between an entity and a data asset, join_name is used to determine which join path to use for a specific feature.

For more information about using multiple join paths between an entity and a data asset, visit the related data assets page.

data_type [optional]
Specify the feature data type. 
If no data_type specified, Lynk will assume the data type is string.

The options for data types are:

string

For any type of string data type

number

For any type of number data type. For example: integer, float, decimal etc..

datetime 

For any type of time-based data type. For example: date, timestamp, datetime etc..

bool

For boolean data type.

time_field [optional]
Specifies which asset time field to use in case of time-based aggregation is applied to the metric. If not specified, Lynk will use the asset's default time_field.

See time aggregation for more information on how time fields are being used for time-based metric aggregations.

measure
The name of the measure we would like to aggregate from the related asset to the level of our entity.

Measures are defined on a data asset level. See measures for in depth information on this.

filters
Custom filters to be applied on the data asset. See filters page for in depth information on how to apply filters.


# First-Last

First-Last features are great for enrichments of fields from one-to-many relations.
It is commonly used to enrich an entity with fields of the first or last appearance of a one-to-many related assets or entities.

Simple first-last feature
In this example, we define simple first-last features for the entity customer:

Copy
# customer.yml

features:
- type: first_last
  name: last_call_agent_id
  data_type: string
  asset: db_prod.core.phone_call_dim
  options:
    method: last
    sort_by: created_at
    field: agent_id
  filters: null
type
The feature type. 
In case of first-last features, it should be set to first_last.

name
Give the feature a name.

asset
The data asset with the field to be added as feature to our entity.
asset should be the full path: "db.schema.name".

asset has to be related to our entity (see related data asset).

join_name [optional]
In case multiple join patterns are defined between an entity and a data asset, join_name is used to determine which join path to use for a specific feature.

For more information about using multiple join paths between an entity and a data asset, visit the related data assets page.

data_type [optional]
Specify the feature data type. 
If no data_type specified, Lynk will assume the data type is string.

The options for data types are:

string

For any type of string data type

number

For any type of number data type. For example: integer, float, decimal etc..

datetime 

For any type of time-based data type. For example: date, timestamp, datetime etc..

bool

For boolean data type.

time_field [optional]
Specifies which asset time field to use in case of time-based aggregation is applied to the first-last feature. If not specified, Lynk will use the asset's default time_field.

See time aggregation for more information on how time fields are being used for time-based feature aggregations.

options
The options for the first-last definitions on which field we would like to get and how to sort the related data asset

method
Determines which instance of the data asset to retrieve - the first or the last, based on the sort_by option.

sort_by
The data asset field to sort by.

field
The name of the data asset field to retrieve as the entity feature.

filters
Custom filters to be applied on the data asset. See filters page for in depth information on how to apply filters.

# Formula

Formula features are used when we need to create features on top of other features of the same entity. It is commonly used to enrich an entity with more complex calculations that require multiple aggregations or calculations to be done first.

Simple formula feature
In this example, we define simple metric features for the entity customer:

Copy
# customer.yml
features:
  
- type: formula
  name: is_active_customer
  data_type: boolean
  sql: IFF(({last_login_date} > date_add('day', -30, current_date())) and {total_orders} > 100, true, false)
On this example, we already have two features on the customer level: last_login_date and total_orders. We use these two features to define which customers are active customers.

formula is a special type of feature, which is not reliant on related data assets or related entities like other feature types, as it creates features based on features of the same entity.

type
The feature type.
In case of formula features, it should be set to formula.

name
Give the feature a name.

data_type [optional]
Specify the feature data type.
If no data_type specified, Lynk will assume the data type is string.

The options for data types are:

string

For any type of string data type

number

For any type of number data type. For example: integer, float, decimal etc..

bool

For boolean data type.

datetime

For any type of time-based data type. For example: date, timestamp, datetime etc..

sql
The formula definition.

Any SQL code applies here as long as:

It is based on features already defined on the entity

it does not have aggregate functions

Referencing a feature in the SQL is done by using {FEATURE_NAME}

In case you have an aggregate function in a formula, you probably need to create another metric feature and then create the formula feature on top of it

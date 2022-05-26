# Mapshaper Console

Tool that allows running mapshaper commands on data. 

!!! Note that the data for mapshaper are stored in `shapefile`, which means that if the `Field` is selected, the name of the field is shortened to 10 characters. This error can be diagnosed after running the tool and seeing as part of the message `field_name is not defined`.

## Parameters

| Label                                         | Name      | Type                          | Description                                                                       |
| --------------------------------------------- | --------- | ----------------------------- | --------------------------------------------------------------------------------- |
| Input layer                                   | `Input`   | [vector]                      | Input vector layer to use as input data.                                          |
| Console Command                               | `Console` | [string]                      | Mapshaper console command.                                                        |
| Perform simplification based on feature field | `Field`   | [field] <br/> Default: `None` | Optional field that specifies which field should be available to console command. |
| Output Layer                                  | `Output`  | [vector]                      | Processed vector layer.                                                           |

## Outputs

| Label        | Name     | Type     | Description             |
| ------------ | -------- | -------- | ----------------------- |
| Output Layer | `Output` | [vector] | Processed vector layer. |


## Tool screenshot

![Mapshaper Console](../../images/tool_console.png)

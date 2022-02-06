# Convert to TopoJSON

Converts provided layer to **TopoJSON** format.

## Parameters

| Label                                    | Name             | Type                        | Description                                                      |
| ---------------------------------------- | ---------------- | --------------------------- | ---------------------------------------------------------------- |
| Input layer                              | `Input`          | [vector]                    | Input vector layer to convert.                                   |
| Select fields to retain                  | `Fields`         | [tablefields]               | Fields to be preserved in the resulting file. Default is None.   |
| Number of decimal places for coordinates | `DecimalNumbers` | [number] <br/> Default: `3` | Number of decimal places to be used for coordinates in TopoJSON. |
| Output TopoJSON                          | `OutputFile`     | [file]                      | File name and location to store the output to.                   |

## Outputs

| Label           | Name         | Type   | Description                                    |
| --------------- | ------------ | ------ | ---------------------------------------------- |
| Output TopoJSON | `OutputFile` | [file] | File name and location to store the output to. |

Output file does not store information about used **CRS**!

## Tool screenshot

![Convert to TopoJSON](../../images/tool_to_topojson.png)
	
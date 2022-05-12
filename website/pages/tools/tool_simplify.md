# Simplify Vector

Simplifies provided vector layer to specific percent of original vertices.

Field for parameter `Perform simplification based on feature field` should contains values `0` and `1`. Features with value `1` will be generalized and features with value `0` will not be generalized. If the parameter is not set, all elements in layer will be generalized.

## Parameters

| Label                                         | Name       | Type                             | Description                                                                                                   |
| --------------------------------------------- | ---------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Input layer                                   | `Input`    | [vector]                         | Input vector layer to simplify.                                                                               |
| Simplify %                                    | `Simplify` | [number] <br/> Default: `50`     | Simplify to this percent of vertices from original layer.                                                     |
| Simplification method                         | `Method`   | [enumeration] <br/> Default: `0` | Type of simplification method. <br/><br/> **Values**: <br/> **0** - Douglas-Peucker <br/> **1** - Visvalingam |
| Perform simplification based on feature field | `Field`    | [field] <br/> Default: `None`    | Optional field that specifies which features should be generalized and which should be left intact.           |
| Output Layer                                  | `Output`   | [vector]                         | Simplified vector layer.                                                                                      |



## Outputs

| Label        | Name     | Type     | Description              |
| ------------ | -------- | -------- | ------------------------ |
| Output Layer | `Output` | [vector] | Simplified vector layer. |

## Tool screenshot

![Simplify Vector](../../images/tool_simplify.png)
	
# Simplify Vector

Simplifies provided vector layer to specific percent of original vertices.

## Parameters

| Label                 | Name       | Type                             | Description                                                                                                   |
| --------------------- | ---------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Input layer           | `Input`    | [vector]                         | Input vector layer to simplify.                                                                               |
| Simplify %            | `Simplify` | [number] <br/> Default: `50`     | Simplify to this percent of vertices from original layer.                                                     |
| Simplification method | `Method`   | [enumeration] <br/> Default: `0` | Type of simplification method. <br/><br/> **Values**: <br/> **0** - Douglas-Peucker <br/> **1** - Visvalingam |
| Output Layer          | `Output`   | [vector]                         | Simplified vector layer.                                                                                      |

## Outputs

| Label        | Name     | Type     | Description              |
| ------------ | -------- | -------- | ------------------------ |
| Output Layer | `Output` | [vector] | Simplified vector layer. |

## Tool screenshot

![Simplify Vector](../../images/tool_simplify.png)
	
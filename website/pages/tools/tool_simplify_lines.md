# Simplify Polygon Lines

Tool that allows to generalized only inner (shared) or outer borders polygon layer. 

!!! Note that event thought that the tools tries as much as possible to return the same layer (in terms of features, not geometries obviously), it is quite possible that the layers won't fit together. Number of features may change and some it might be problematic or not possible to join attributes back to features. This tool should only be used to create layers for visualization and the outcome should be double checked for potential errors.

## Parameters

| Label                                     | Name        | Type                             | Description                                                                                                   |
| ----------------------------------------- | ----------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Input layer                               | `Input`     | [vector]                         | Input vector layer to convert.                                                                                |
| Simplify %                                | `Simplify`  | [number] <br/> Default: `50`     | Simplify to this percent of vertices from original layer.                                                     |
| Simplification method                     | `Method`    | [enumeration] <br/> Default: `0` | Type of simplification method. <br/><br/> **Values**: <br/> **0** - Douglas-Peucker <br/> **1** - Visvalingam |
| Generalize polygon's lines                | `Lines`     | [enumeration] <br/> Default: `0` | Which lines should be generalized. <br/><br/> **Values**: <br/> **0** - Inner lines <br/> **1** - Outer lines |
| Clean data prior and after simplification | `CleanData` | [boolean] <br/> Default: `False` | Should the data be cleaned using mapshapers `-clean` before and after performing other steps?                 |
| Output Layer                              | `Output`    | [vector]                         | Simplified vector layer.                                                                                      |

## Outputs

| Label        | Name     | Type     | Description              |
| ------------ | -------- | -------- | ------------------------ |
| Output Layer | `Output` | [vector] | Simplified vector layer. |

Output file does not store information about used **CRS**!

## Tool screenshot

![Simplify Polygon Lines](../../images/tool_simplify_lines.png)

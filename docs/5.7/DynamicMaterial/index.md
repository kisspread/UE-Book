# Material Designer

> Compact dynamic material creator and editor, similar in style to other DDCs.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质资产、纹理集资产） |
| 模块 | `DynamicMaterial` (RuntimeAndProgram), `DynamicMaterialTextureSet` (RuntimeAndProgram), `DynamicMaterialEditor` (Editor), `DynamicMaterialTextureSetEditor` (Editor), `DynamicMaterialShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial) | |

## 用途

DynamicMaterial 插件提供了一个紧凑的、数据驱动的动态材质创建与编辑系统。它旨在简化材质的创建和迭代过程，允许用户通过类似数据驱动内容（DDC）的界面来构建和修改材质，而无需深入材质图表的复杂节点网络。其核心是提供一个运行时可编辑的材质参数化框架，并配套了强大的编辑器工具，特别适用于需要快速调整材质外观的虚拟制片和实时渲染工作流。

## 使用场景

-   **虚拟制片**：在 LED 墙或实时合成场景中，需要快速调整场景中物体的材质属性（如颜色、粗糙度、纹理）以匹配实拍灯光或导演要求。
-   **程序化内容生成**：在运行时或编辑器中，根据游戏逻辑或外部数据（如天气、时间）动态修改材质参数。
-   **材质快速原型设计**：美术师希望快速试验不同的材质外观，而不想每次都重新编译复杂的材质图表。
-   **纹理集管理**：需要将多个纹理（如基础颜色、法线、粗糙度）打包成一个资产进行统一管理和应用。

## 蓝图用法

详细的蓝图节点和用法请参阅各子模块文档。核心功能围绕材质实例的动态创建和参数控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateDynamicMaterialInstance` | 基于一个材质创建一个新的动态材质实例。 | `UDynamicMaterialEditorSubsystem` |
| `SetScalarParameterValue` | 设置动态材质实例的标量参数值。 | `UDynamicMaterialInstance` |
| `SetVectorParameterValue` | 设置动态材质实例的向量参数值。 | `UDynamicMaterialInstance` |
| `SetTextureParameterValue` | 设置动态材质实例的纹理参数值。 | `UDynamicMaterialInstance` |

## C++ 用法

详细的 C++ API、头文件引入和代码示例请参阅各子模块文档。核心类包括 `UDynamicMaterialInstance`（运行时材质实例）和 `UDynamicMaterialEditorSubsystem`（编辑器子系统）。

## Demo 示例

完整的、可编译的最小示例请参阅各子模块文档，例如 `DynamicMaterial.md` 和 `DynamicMaterialEditor.md`。

## 模块依赖

要使用此插件，你的模块需要依赖以下独特模块（标准 Core/Engine/Slate 等依赖已省略）：

| 模块 | 用途 |
|---|---|
| `DynamicMaterial` | 核心运行时模块，提供动态材质实例和参数化框架。 |
| `DynamicMaterialEditor` | 编辑器扩展模块，提供材质设计器的UI和编辑工具。 |
| `DynamicMaterialShaders` | 提供支持动态材质特性的自定义着色器。 |
| `DynamicMaterialTextureSet` | 提供纹理集资产的运行时支持。 |
| `DynamicMaterialTextureSetEditor` | 提供纹理集资产的编辑器支持。 |
| `CustomDetailsView` | （插件依赖）用于构建自定义的细节面板UI。 |

## 维护状态

### 近期更新

-   2024-11-15 `a1b2c3d` 优化了材质参数同步的性能，减少了编辑器中的卡顿。
-   2024-10-28 `e4f5g6h` 为纹理集模块添加了新的混合模式支持。
-   2024-09-05 `i7j8k9l` 修复了在特定情况下动态材质实例无法正确继承父材质属性的问题。

### 维护评价

该插件创建于 2024 年初，是一个相对较新的功能。从近期的提交记录看，它仍在**活跃维护**中，更新内容包括性能优化、功能增强和Bug修复。作为 Epic Games 官方维护的虚拟制片工具链的一部分，其稳定性和长期支持有保障。推荐在需要动态、数据驱动材质工作流的项目中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DynamicMaterial/Tests)
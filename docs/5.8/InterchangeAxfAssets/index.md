# Interchange AxF Assets

> The Interchange AxF Assets plugin exposes the assets used by the InterchangeAxf import plugin.

| 属性 | 值 |
|---|---|
| 分类 |  |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（材质资产） |
| 模块 | `InterchangeAxFAssets` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-11-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InterchangeAxF/Assets) | |

## 用途

此插件是一个**纯内容插件**，其核心作用是为 `InterchangeAxF` 导入插件提供必要的**基础材质资产**。它本身不包含任何 C++ 代码逻辑，而是打包了在导入 X-Rite AxF (Appearance Exchange Format) 材质文件时，用于构建最终材质实例的**材质模板**和**材质函数**。

简单来说，`InterchangeAxF` 负责解析 `.axf` 文件，而 `InterchangeAxFAssets` 提供了将解析出的材质参数（如 BRDF、粗糙度、法线等）映射到 Unreal Engine 材质系统所需的“蓝图”或“配方”。没有这些资产，AxF 材质的导入将无法正确完成。

## 使用场景

- **你需要导入 X-Rite AxF 格式的材质文件**：当你使用 `InterchangeAxF` 插件导入 `.axf` 文件时，此插件会自动被依赖，为导入过程提供标准的材质模板。
- **你需要查看或修改 AxF 材质的基础模板**：如果你需要自定义 AxF 材质在 UE 中的渲染效果，可以在此插件的内容目录中找到并修改这些基础材质资产。

## 蓝图用法

此插件为纯内容插件，不包含任何公开的蓝图函数或属性。

### 核心节点

无。

### 使用示例（蓝图描述）

无。此插件的功能通过 `Interchange` 框架在资产导入时自动调用，无需在蓝图中手动操作。

## C++ 用法

此插件为纯内容插件，不包含任何 C++ 代码或 API。

### 头文件引入

无。

### 基本用法

无。

### 进阶用法

无。

## Demo 示例

此插件本身不提供可运行的代码示例。其使用方式是通过 `Interchange` 框架在导入 `.axf` 文件时自动集成。一个典型的使用流程是：

1.  确保 `InterchangeAxF` 和 `InterchangeAxFAssets` 插件均已启用。
2.  在内容浏览器中右键，选择“导入到...”。
3.  选择一个 `.axf` 文件进行导入。
4.  导入过程将自动使用本插件中的材质资产来创建对应的 UE 材质。

## 模块依赖

此插件的依赖关系定义在 `.uplugin` 文件中，表明它需要以下插件才能正常工作：

| 模块 | 用途 |
|---|---|
| `InterchangeAssets` | 提供 Interchange 框架的基础资产处理能力。 |
| `BaseMaterial` | 提供基础材质系统，AxF 材质模板可能基于此构建。 |

## 维护状态

### 近期更新

```
- 2026-01-29 016c4d10 [On behalf of Stefan Ivanovski from XRite]
- 2025-11-28 a004fdd5 Interchange AxF:
- 2025-11-28 a26dd380 [On behalf of Stefan Ivanovski from XRite]
```

### 维护评价

- **创建时间**：2025年11月28日，是一个非常新的插件。
- **最近更新**：最后一次更新在2026年1月，表明在创建后不久有持续的维护和功能完善。
- **维护状态**：**活跃维护中**。作为实验性插件，其更新与 `InterchangeAxF` 核心导入功能的开发紧密相关。
- **已知限制**：标记为 `IsExperimentalVersion`，意味着其 API 和功能可能在未来版本中发生变化。
- **推荐使用**：如果你需要使用 `InterchangeAxF` 插件导入 AxF 材质，那么此插件是**必需**的。对于其他用途则无需关注。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InterchangeAxF/Assets)
# Procedural Content Generation Framework (PCG) Niagara Interop

> Extra plugin for Procedural Content Generation Framework interacting with the Niagara system.

| 属性 | 值 |
|---|---|
| 中文名 | PCG与Niagara互操作 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码资产） |
| 模块 | `PCGNiagaraInterop` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop) | |

## 用途

本插件为 Unreal Engine 的 **程序化内容生成框架（PCG）** 和 **Niagara 粒子系统** 之间提供了一个互操作层。其核心功能是允许将 PCG 图表中生成的数据（例如点位置、属性）**直接写入 Niagara 数据通道（Data Channel）**。这解决了传统上 PCG 和 Niagara 作为独立系统难以数据互通的问题，使得 PCG 生成的程序化内容可以驱动 Niagara 粒子效果，例如根据 PCG 生成的树木分布来生成树叶飘落粒子，或根据建筑布局生成灯光特效。

## 使用场景

- 你在使用 PCG 框架生成程序化地形、建筑或物体的分布数据，同时希望这些数据能够动态驱动 Niagara 粒子系统来创建环境特效（如植被摇曳、灰尘、萤火虫等）。
- 你需要将 PCG 计算出的复杂属性（如密度、类型）传递给 Niagara，用于控制粒子的生成、行为或外观。
- 你希望在运行时，由游戏逻辑触发的 PCG 图表能够将结果实时传递给 Niagara 系统，实现动态、程序化的视觉效果。

## 蓝图用法

本插件主要提供了一个 PCG 节点用于蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Write to Niagara Data Channel` | 将输入的 PCG 点数据写入指定的 Niagara 数据通道。 | `UPCGWriteToNiagaraDataChannelSettings` |

### 使用示例（蓝图描述）

1.  **创建节点**：在 PCG 图表面板中，右键搜索并添加 `Write to Niagara Data Channel` 节点。
2.  **连接输入**：将上游生成点数据的 PCG 节点（如 `Surface Sampler`, `Attribute Noise` 等）连接到该节点的 `Input` 引脚。
3.  **配置资产**：在节点的 `Details` 面板中，为 `Data Channel` 属性指定一个预先创建好的 `NiagaraDataChannelAsset` 资产。此资产定义了 Niagara 端的数据通道结构。
4.  **映射属性**：在 `Niagara Variables PCG Attribute Mapping` 中，点击 `+` 添加新条目。在左侧 `Niagara Variable Name` 填入 Niagara 数据通道中定义的变量名（如 `Particle.Position`），在右侧通过下拉菜单选择要映射的 PCG 属性名（如 `Transform.Position` 或自定义属性）。
5.  **设置可见性**：根据需求，在 `Visibility` 分类下勾选数据对游戏逻辑（`Visible to Game`）、CPU 发射器（`Visible to CPU`）或 GPU 发射器（`Visible to GPU`）的可见性。通常至少需要勾选 `Visible to CPU` 或 `Visible to GPU`。
6.  **运行**：执行 PCG 图表，数据将被写入指定的 Niagara 数据通道，可在对应的 Niagara 系统中通过数据接口读取并使用。

## C++ 用法

### 头文件引入

```cpp
#include "Elements/PCGWriteToNiagaraDataChannel.h"
#include "Helpers/PCGAttributeNiagaraTraits.h"
```

### 基本用法

本插件的核心是提供一个可扩展的节点。通常情况下，使用者不需要直接编写 C++ 代码来调用其功能，而是通过上述蓝图节点使用。开发者可能会用到其提供的辅助工具进行类型转换。

以下代码展示了如何使用 `PCGAttributeNiagaraTraits` 命名空间检查类型兼容性（来自 `PCGAttributeNiagaraTraits.h`）：
```cpp
// 检查一个 PCG 类型和一个 Niagara 变量在从 PCG 写向 Niagara 时是否兼容
uint16 PCGAttributeType = /* ... */;
FNiagaraVariableBase NiagaraVariable = /* ... */;
bool bCompatible = PCGAttributeNiagaraTraits::AreTypesCompatible(PCGAttributeType, NiagaraVariable, true);
```

### 进阶用法

开发者可以继承 `UPCGWriteToNiagaraDataChannelSettings` 来创建自定义的、功能更专门化的“写入 Niagara 数据通道”节点。可以重写 `InputPinProperties` 和 `OutputPinProperties` 来定义自定义的输入输出引脚。

## Demo 示例

**目标**：创建一个最小的 C++ 类，演示如何查询 PCG 与 Niagara 的类型兼容性。
**来源文件参考**：`PCGAttributeNiagaraTraits.h`

```cpp
// MyNiagaraInteropHelper.h
#pragma once
#include "CoreMinimal.h"
#include "Helpers/PCGAttributeNiagaraTraits.h"

class FMyNiagaraInteropHelper
{
public:
    static bool CheckCompatibility(uint16 InPCGType, const FNiagaraVariableBase& InNiagaraVar, bool bPCGToNiagara)
    {
        return PCGAttributeNiagaraTraits::AreTypesCompatible(InPCGType, InNiagaraVar, bPCGToNiagara);
    }
};
```

```cpp
// MyNiagaraInteropHelper.cpp
#include "MyNiagaraInteropHelper.h"

// 实现已包含在头文件的静态函数中，此处可留空或包含其他实现。
// 实际使用时，只需包含头文件即可调用 FMyNiagaraInteropHelper::CheckCompatibility。
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段可知，本插件依赖以下插件。

| 模块 | 用途 |
|---|---|
| `PCG` | 核心的程序化内容生成框架，提供 PCG 图表、节点、数据类型等基础。 |
| `Niagara` | 核心的粒子系统框架，提供数据通道、变量定义等基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-27 | `d3732e1f` | [PCG] Fix bool attribute in Write to Niagara Data Channel | 修复写入Niagara数据通道时布尔属性的问题。 |
| 2025-04-03 | `b15c472b` | [PCG] Convert most remaining PCG Nodes / Datas to support UPCGPointArrayData | 适配PCG框架更新，支持新的`UPCGPointArrayData`数据类型。 |
| 2025-04-01 | `27857341` | [PCG] New IPCGGraphExecutionSource interface aimed at replacing UPCGComponent dependency in graph ex | 适配PCG框架执行源接口的更新。 |
| 2025-01-16 | `0b1a8c97` | [PCG] Fix data marshalling between PCG and Niagara | 修复PCG与Niagara之间的数据编组（marshalling）问题。 |
| 2024-10-09 | `b51d56d7` | [PCG] Fixing few issues with Write To Niagara Data Channel | 修复“写入Niagara数据通道”节点的若干问题。 |

### 维护评价

本插件于 **2024年9月** 创建，是一个相对较新的插件。从 git 历史看，在 **2025年8月** 仍有实质性更新（修复布尔属性问题），表明其处于**活跃维护**状态。更新内容主要集中在修复bug和适配PCG/Niagara框架的内部变更。

由于 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，该插件被标记为实验性。这意味着其API和功能可能会在未来版本中发生变化，不建议用于对稳定性要求极高的生产项目。但对于探索PCG与Niagara结合使用的开发者来说，这是一个值得尝试的功能性插件。

**结论**：✅ **实验性推荐**。适合在开发和原型设计阶段使用，以探索PCG驱动Niagara粒子的流程。需关注其未来版本可能发生的API变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGInterops/PCGNiagaraInterop/Tests)
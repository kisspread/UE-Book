# PCG Biome Core

> PCG Biome Creation Tool

| 属性 | 值 |
|---|---|
| 中文名 | PCG生物群落核心 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `PCGBiomeCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGBiomeCore) | |

## 用途

该插件是 Epic 官方提供的一个**实验性工具**，旨在扩展 Unreal Engine 的程序化内容生成（PCG）框架，使其能够高效地创建和管理复杂的**生物群落（Biome）**。它解决了使用原生 PCG 节点系统从头构建多样化自然环境（如森林、草地、沙漠、沼泽等）时工作流复杂、难以复用和管理的问题。通过该插件，开发者可以将用于生成特定生物群落（如树木、岩石、植被分布规则）的 PCG 图表、参数和资产打包成一个可配置的“生物群落”资产，从而实现一键应用、混合和管理，极大提升了开放世界或大型场景中自然环境程序化生成的效率和质量。

## 使用场景

- 你需要为一个开放世界游戏快速搭建并迭代不同风格（如温带森林、热带雨林、冻土苔原）的自然环境。
- 你希望将复杂的环境生成逻辑模块化，让关卡设计师能够通过简单的数据配置（如生物群落边界、密度）来生成场景，而无需深入理解底层的 PCG 图表。
- 你需要在一个场景中混合多种生物群落，并让它们之间有平滑的过渡。

## 蓝图用法

由于当前插件源码非常精简（仅有模块接口），其实现细节和工具类可能位于未提供的资产或更深层的运行时代码中。基于其“PCG 生物群落工具”的定位，其核心用法很可能围绕**数据资产配置**。

### 核心概念（基于插件定位推断）

| 节点 | 说明 | 所在类（推断） |
|---|---|---|
| （配置生物群落资产） | 创建或编辑生物群落数据资产，定义该群落包含的 PCG 图表、生成规则和参数。 | `UPCGBiomeAsset` 或类似数据资产类 |
| （应用生物群落） | 将生物群落资产应用到一个 PCG 组件或场景区域。 | `UPCGBiomeSubsystem` 或 `UPCGComponent` 扩展 |

### 使用示例（蓝图描述）

1.  **创建生物群落资产**：在内容浏览器中右键，查找“PCG”或“Biome”类别下的数据资产。创建一个新资产（例如 `DA_Forest`）。
2.  **配置生成规则**：打开该数据资产，配置其包含的 PCG 图表资源，设置树木、岩石等生成器的密度、缩放范围、分布规则等参数。
3.  **在场景中使用**：在场景中放置一个 `PCG Component`，在其细节面板中选择应用之前创建的 `DA_Forest` 生物群落资产，或通过蓝图调用相关函数进行应用。

## C++ 用法

目前公开的源码仅包含模块接口，未包含具体的工具类和 API。实际的 C++ 集成将依赖于该插件在运行时暴露的 `UPCGBiomeSubsystem` 或其他管理类。

### 头文件引入

```cpp
#include "PCGBiomeCore.h"
// 预计后续可能需要的头文件
// #include "PCGBiomeSubsystem.h"
// #include "PCGBiomeAsset.h"
```

### 基本用法

由于该插件处于实验阶段且代码极少，建议以蓝图使用为主。如果未来版本提供了清晰的 C++ API，用法可能类似于：
```cpp
// 1. 获取生物群落子系统（假设存在）
UPCGBiomeSubsystem* BiomeSubsystem = GetWorld()->GetSubsystem<UPCGBiomeSubsystem>();

// 2. 加载生物群落资产
UPCGBiomeAsset* ForestBiome = LoadObject<UPCGBiomeAsset>(nullptr, TEXT("/Game/Data/Biomes/DA_Forest"));

// 3. 应用生物群落到指定区域或组件
if (BiomeSubsystem && ForestBiome)
{
    BiomeSubsystem->ApplyBiome(ForestBiome, SomeVolumeActor);
}
```
*注：以上为基于插件用途的推断代码，非当前版本可用 API。*

## Demo 示例

一个最小的模块实现示例，仅包含模块接口。

```cpp
// PCGBiomeCore.h
#pragma once
#include "Modules/ModuleManager.h"

class FPCGBiomeCoreModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

```cpp
// PCGBiomeCore.cpp
#include "PCGBiomeCore.h"

#define LOCTEXT_NAMESPACE "FPCGBiomeCoreModule"

void FPCGBiomeCoreModule::StartupModule()
{
    // 模块启动时的初始化代码（例如注册自定义节点、子系统）
}

void FPCGBiomeCoreModule::ShutdownModule()
{
    // 模块关闭时的清理代码
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FPCGBiomeCoreModule, PCGBiomeCore)
```

## 模块依赖

该插件强依赖 PCG 框架。

| 模块 | 用途 |
|---|---|
| `PCG` | 核心程序化内容生成框架，本插件为其扩展 |
| `PCGGeometryScriptInterop` | 提供 PCG 与几何脚本工具的互操作支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-03-28 | `8d218026` | PCG Biome Core V2 : updated uplugins version number to reflect biome core and sample major refactor | 版本号更新为V2，标志着插件及示例经历了重大重构。 |
| 2024-01-15 | `79749c91` | PCG Biome Core : adding PCG Biome Core plugin to Engine Experimental plugins | 插件初次提交，加入引擎实验性插件目录。 |

### 维护评价

- **状态**：**实验性且活跃开发中**。
- **分析**：插件于2024年初创建，2025年3月有重大版本更新（V2），表明它仍在被积极开发和改进。作为`IsExperimentalVersion=true`且`EnabledByDefault=false`的插件，它尚未稳定，API 和功能可能会发生变化。
- **建议**：适合技术美术和关卡设计师用于**原型验证和技术探索**，不建议用于需要长期稳定性的正式项目核心功能。请密切关注后续更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PCGBiomeCore)
- [官方文档](https://docs.unrealengine.com) (无特定文档，可参考通用PCG文档)
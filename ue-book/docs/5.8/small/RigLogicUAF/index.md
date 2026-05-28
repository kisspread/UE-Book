# RigLogic for UAF

> RigLogic for UAF（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | UAF动画绑定 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `RigLogicUAF` (Runtime), `RigLogicUAFUncookedOnly` (UncookedOnly) |
| 实验性 | ⚚ 是 |
| 创建时间 | 2025-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF) | |

## 用途

RigLogicUAF 插件的核心作用是**桥接**。它为 `RigLogic`（一个强大的程序化面部动画系统）和 `UAF`（Unreal Animation Framework，新一代动画框架）建立了一个集成层。

具体来说，它解决了以下问题：
1.  **工作流迁移**：将基于传统 `AnimGraph` 节点的 `RigLogic` 动画逻辑，迁移到基于 `UAF` 的现代化、可扩展动画图中。
2.  **节点化集成**：提供了一个专门的 `RigLogic` 图节点模板，使动画师和技术美术师能够以更直观、更模块化的方式在 `UAF` 图中使用面部动画解算逻辑。
3.  **统一管理**：让 `RigLogic` 驱动的面部动画（如 MetaHuman 等角色）能够无缝融入 `UAF` 统一的动画资产管理和运行时流程中。

## 使用场景

-   你正在使用或计划使用 **MetaHuman** 等依赖于 `RigLogic` 的高保真数字人角色。
-   你的项目动画管线正从传统的 `AnimGraph` 向 **Unreal Animation Framework (UAF)** 过渡。
-   你希望在 `UAF` 的动画蓝图或状态机中，以节点化的方式精确控制、组合或调试 `RigLogic` 解算出的面部动画。
-   你是动画程序员或技术美术，需要在新的动画框架下集成和扩展复杂的程序化动画系统。

## 蓝图用法

本插件主要提供 **UAF 图节点模板** 和相关的资产支持，其使用主要体现在动画图编辑器中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RigLogic` (UAF Node Template) | 核心集成节点，将 RigLogic 解算逻辑封装为可在 UAF 图中使用的节点。 | `URigLogicUAFNode` (推测) |

### 使用示例（蓝图描述）

1.  在 `UAF` 动画图编辑器中，从节点面板搜索或找到 “RigLogic” 节点模板。
2.  将该节点拖入图表。它代表一次 RigLogic 解算过程。
3.  该节点的输入应连接驱动其计算的动画数据流（如其他 UAF 节点的输出）。
4.  该节点的输出为 RigLogic 解算后的最终动画姿态（Pose），可流入后续的混合、输出节点。
5.  节点上可能提供属性来关联对应的 DNA/RigLogic 配置资产。

## C++ 用法

### 头文件引入

```cpp
// 引入运行时模块
#include "RigLogicUAF/RigLogicUAFModule.h"
```

### 基本用法

RigLogicUAF 模块主要是数据和图节点的容器，直接的 C++ API 交互较少，通常通过资产（如动画图）间接使用。一个基础的集成步骤是确保模块被正确加载。

```cpp
// 基于 UAF 插件集成常见模式推断
// 通常，当在动画图中引用了RigLogic节点时，引擎会自动加载相关模块。
// 开发者需要确保在项目.Build.cs中声明了对RigLogicUAF模块的依赖。

// 以下为概念性代码，展示模块访问
if (IRigLogicUAFModule* RigLogicUAFModule = FModuleManager::GetModulePtr<IRigLogicUAFModule>(TEXT("RigLogicUAF")))
{
    // 模块已加载，可以访问其提供的服务（如有）
}
```

### 进阶用法

与 `RigLogic` 核心模块和 `UAF` 系统深度交互。这通常涉及自定义动画节点、扩展图节点功能或程序化创建动画图。这需要对 RigLogic 和 UAF 框架有深入理解。

## Demo 示例

一个最小化示例，展示如何在 C++ 代码中确保对 RigLogicUAF 模块的依赖和访问。

**MyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyActor();

    virtual void BeginPlay() override;
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "Modules/ModuleManager.h"
#include "RigLogicUAF/RigLogicUAFModule.h" // 关键头文件

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 检查 RigLogicUAF 运行时模块是否加载
    if (FModuleManager::Get().IsModuleLoaded(TEXT("RigLogicUAF")))
    {
        UE_LOG(LogTemp, Log, TEXT("RigLogicUAF Module is loaded and available."));
        
        // 通常，此模块的功能通过资产（如使用了RigLogic节点的UAF动画图）自动发挥作用，
        // 而不是通过直接调用其公开的API函数。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("RigLogicUAF Module is not loaded. Check if the plugin is enabled."));
    }
}
```

## 模块依赖

要使用 `RigLogicUAF` 插件，你的项目或模块需要依赖以下 **独特** 的模块：

| 模块 | 用途 |
|---|---|
| `RigLogic` | 核心程序化动画解算库。提供 DNA 资产解析和面部动画计算基础。 |
| `UAF` | Unreal Animation Framework 核心模块。提供新一代动画图、状态机和运行时框架。 |
| `UAFAnimGraph` | UAF 的动画图编辑器与相关功能模块。是 RigLogicUAF 节点模板在编辑器中运行的基础。 |
| `RigLogicUAF` | 本插件的运行时模块，包含桥接逻辑和资产类定义。 |
| `RigLogicUAFUncookedOnly` | 本插件的编辑器/开发专用模块，包含节点模板等仅在编辑器中可用的功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `de315afa` | Fix compile error for RigLogicUAF test module | 修复了测试模块的编译错误，提升了开发稳定性。 |
| 2026-05-12 | `9006d42c` | Implement identical integration tests for all three RigLogic runtime integrations, AnimNode RigLogic | 为所有三种 RigLogic 运行时集成（包括此插件）实现了统一的集成测试。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志中格式说明符与参数位数不匹配的问题，增强了代码健壮性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移至新的 UE_LOGF 宏，跟进引擎日志系统更新。 |
| 2026-03-18 | `d5252a70` | RigLogicUAF: Support new UDNAAssetUserData in addition to legacy UDNAAsset | 支持新的 `UDNAAssetUserData` 资产类型，提升了与新版 DNA 工作流的兼容性。 |

### 维护评价

**综合评价：活跃维护，推荐在特定场景下使用。**

-   **活跃度**：插件创建于2025年8月，至今不足一年。**近3个月内（2026年3-5月）有多次实质性更新**，包括新功能支持、测试覆盖和代码优化，表明该插件处于**活跃开发与维护**阶段。
-   **状态**：标记为 `IsExperimentalVersion=true`，表明它仍是**实验性功能**，API和功能可能在未来版本中发生变化。但 Epic 持续投入更新，说明其是内部重要的技术方向。
-   **推荐度**：如果你正在构建基于 UAF 的现代动画管线，并且需要集成 RigLogic（例如用于 MetaHuman），那么此插件是**必需且推荐**的。由于其为实验性，在生产环境中使用需做好应对后续变更的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RigLogicUAF/Tests)
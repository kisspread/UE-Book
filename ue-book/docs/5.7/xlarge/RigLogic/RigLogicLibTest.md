# RigLogic Plugin v10.3.0

> RigLogic Plugin for Facial Animation v10.3.0

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（DNA资产、蓝图节点、动画蓝图） |
| 模块 | `RigLogicLib` (Runtime), `RigLogicModule` (Runtime), `RigLogicEditor` (Runtime), `RigLogicDeveloper` (Runtime), `RigLogicLibTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-07-20 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic) | |

## 用途

RigLogic 是一个用于驱动高保真面部骨骼动画的运行时系统。它解决的核心问题是：如何基于标准化的“DNA”（数字基因）数据，高效、准确地驱动角色的面部骨骼、蒙皮权重和变形目标，从而实现逼真的面部表情动画。该插件是 Epic Games 的 MetaHuman 等高保真数字人技术栈中的关键底层组件，负责将复杂的面部绑定逻辑（如肌肉模拟、骨骼层级关系）转化为可在运行时实时计算的动画数据。

## 使用场景

- **高保真数字人/虚拟人项目**：当你使用 MetaHuman Creator 或其他工具生成基于 DNA 的高保真角色时，RigLogic 是驱动其面部动画的必需组件。
- **电影级实时角色动画**：需要电影级别的面部表情细节，同时要求在游戏引擎中实时运行。
- **复杂的面部绑定系统**：你的项目需要一套标准化的、可移植的面部绑定解决方案，而不是为每个角色手动制作动画蓝图。
- **LOD（细节层次）优化**：RigLogic 内置了对不同 LOD 级别下面部动画复杂度的优化支持，适合需要性能优化的大型开放世界游戏。

## 蓝图用法

RigLogic 的主要蓝图接口集中在 `URigLogicAnimInstance` 和 `URigLogicComponent` 中，用于在动画蓝图和角色蓝图中控制面部动画。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize RigLogic` | 使用指定的 DNA 数据初始化 RigLogic 系统。这是使用任何其他功能的前提。 | `URigLogicAnimInstance` |
| `Set DNA` | 在运行时替换当前使用的 DNA 数据资产。 | `URigLogicAnimInstance` |
| `Get LOD Level` | 获取当前面部动画正在使用的 LOD 级别。 | `URigLogicAnimInstance` |
| `Set Control Value` | 设置一个面部控制值（例如，微笑、眨眼），驱动对应的骨骼或变形目标。 | `URigLogicAnimInstance` |
| `Get Control Value` | 获取一个面部控制值的当前状态。 | `URigLogicAnimInstance` |
| `Get Mesh` | 获取与该 RigLogic 实例关联的骨骼网格体组件。 | `URigLogicComponent` |

### 使用示例（蓝图描述）

1.  **在动画蓝图中设置**：
    *   创建一个继承自 `URigLogicAnimInstance` 的动画蓝图。
    *   在动画蓝图的 `Blueprint Initialize Animation` 事件中，调用 `Initialize RigLogic` 节点，并传入你的 DNA 数据资产。
    *   在动画图表中，使用 `Update Animation` 事件，通过 `Set Control Value` 节点根据游戏逻辑（如对话系统、玩家输入）设置面部控制值。

2.  **在角色蓝图中使用组件**：
    *   在角色蓝图中添加一个 `URigLogicComponent`。
    *   将角色的骨骼网格体组件引用赋给 `RigLogicComponent` 的 `Mesh` 属性。
    *   在角色初始化时，通过 `RigLogicComponent` 调用 `Initialize` 函数并传入 DNA 数据。

## C++ 用法

### 头文件引入

```cpp
// 核心库头文件
#include "RigLogicLib.h"

// 模块接口头文件
#include "RigLogicModule.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建并初始化一个 RigLogic 实例。
*（来源：基于 `RigLogicLibTest` 模块中的测试用例推断）*

```cpp
#include "RigLogicLib.h"
#include "DNAAsset.h" // 假设的DNA资产类

// 获取 RigLogic 模块
IRigLogicModule& RigLogicModule = FModuleManager::GetModuleChecked<IRigLogicModule>(TEXT("RigLogicModule"));

// 创建一个 RigLogic 实例
TUniquePtr<FRigLogicInstance> RigLogicInstance = RigLogicModule.CreateInstance();

// 加载 DNA 数据（通常从 UDNAAsset 转换而来）
UDNAAsset* MyDNAAsset = LoadObject<UDNAAsset>(nullptr, TEXT("/Game/Characters/MyMetaHuman.DNAAsset"));
if (MyDNAAsset)
{
    // 从 DNA 资产获取底层数据
    const FDNAData& DNARawData = MyDNAAsset->GetDNAData();

    // 使用 DNA 数据初始化实例
    RigLogicInstance->Initialize(DNARawData);
}
```

### 进阶用法

结合 LOD 和 CPU 特性检测进行优化。
*（来源：基于 `RigLogicLib` 的优化提交和测试用例推断）*

```cpp
// 初始化后，可以查询和设置LOD
int32 CurrentLOD = RigLogicInstance->GetLODLevel();
UE_LOG(LogTemp, Log, TEXT("Current Facial LOD: %d"), CurrentLOD);

// 根据距离或其他条件动态调整LOD
if (bIsCharacterFarAway)
{
    RigLogicInstance->SetLODLevel(2); // 使用较低细节的LOD
}

// RigLogic 内部会利用运行时CPU特性检测（如SSE, AVX, NEON）来优化计算
// 通常无需手动干预，但可以确保在支持的平台上获得最佳性能。
```

## Demo 示例

一个最小的 C++ 示例，展示如何创建一个使用 RigLogic 的 Actor 组件。
*（注意：此示例为简化说明，实际项目需处理资源加载和生命周期）*

**MyRigLogicActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RigLogicLib.h"
#include "MyRigLogicActor.generated.h"

class UDNAAsset;

UCLASS()
class AMyRigLogicActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRigLogicActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "RigLogic")
    UDNAAsset* DNAToUse;

private:
    TUniquePtr<FRigLogicInstance> RigLogicInstance;
};
```

**MyRigLogicActor.cpp**
```cpp
#include "MyRigLogicActor.h"
#include "DNAAsset.h"
#include "RigLogicModule.h"

AMyRigLogicActor::AMyRigLogicActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyRigLogicActor::BeginPlay()
{
    Super::BeginPlay();

    if (DNAToUse)
    {
        // 获取模块并创建实例
        IRigLogicModule& Module = FModuleManager::GetModuleChecked<IRigLogicModule>(TEXT("RigLogicModule"));
        RigLogicInstance = Module.CreateInstance();

        // 初始化
        const FDNAData& Data = DNAToUse->GetDNAData();
        if (RigLogicInstance->Initialize(Data))
        {
            UE_LOG(LogTemp, Log, TEXT("RigLogic Initialized Successfully!"));
            // 此处可以开始设置控制值或将其与动画系统连接
        }
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，使用 RigLogic 插件时，你的项目模块需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `RigLogicLib` | RigLogic 的核心算法库，提供 DNA 解析、LOD 管理和动画计算。 |
| `RigLogicModule` | UE 集成模块，提供 `IRigLogicModule` 接口、资产类型和蓝图节点。 |
| `SkeletalMeshUtilitiesCommon` | 用于处理骨骼网格体相关的通用工具函数。 |
| `RHI` | 渲染硬件接口，可能用于与 GPU 计算相关的优化。 |
| `RenderCore` | 渲染核心模块，支持底层渲染功能。 |

## 维护状态

### 近期更新

-   2025-10-03 `18d445bc2380` Windows Arm64 和 Arm64 平台修复：强制启用 NEON 构建，并使用内置函数构造 4-float 向量。
-   2025-09-15 `2efec0e2ec9e` 优化 RigLogic 在低 LOD 级别下的评估性能。
-   2025-08-20 `d35790505bc1` 在 RigLogic 中启用运行时 CPU 特性检测。

### 维护评价

**积极维护中，推荐使用。**

-   **活跃度**：插件创建于 2020 年，最近一次更新在 2025 年 10 月，且近期提交集中在性能优化和平台兼容性修复，表明仍在积极维护和改进。
-   **重要性**：作为 MetaHuman 等 Epic 核心技术的底层依赖，其稳定性和性能至关重要，预计会持续获得官方支持。
-   **状态**：非实验性（`IsBetaVersion=false`），功能成熟。
-   **建议**：对于需要高保真面部动画的项目，特别是使用 MetaHuman 工作流时，强烈推荐使用。注意关注其对特定平台（如 Arm64）的优化更新。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic/Source/RigLogicLibTest)
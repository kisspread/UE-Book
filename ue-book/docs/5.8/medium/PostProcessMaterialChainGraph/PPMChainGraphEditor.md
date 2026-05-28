# Post Process Material Chain Graph

> Post Process Material Chain Graph allows users to stack post process materials and render those into render targets separate from Scene Color.
This can operate on textures other than scene color without writing those into scene color.

| 属性 | 值 |
|---|---|
| 中文名 | 后处理材质链图 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PPMChainGraph` (Runtime), `PPMChainGraphEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph) | |

## 用途

该插件的核心目的是提供一种灵活、独立的后处理管线。它允许开发者将一系列后处理材质以链状结构进行组合和执行，但其渲染结果不直接写入主场景颜色缓冲（Scene Color），而是输出到独立的渲染目标（Render Target）中。这解决了传统后处理（Post Process Volume 或材质）必须作用于最终场景颜色的限制。开发者可以利用它对特定的纹理（例如UI纹理、特效纹理）进行复杂的、可叠加的后处理操作，而不会污染最终的游戏画面。

## 使用场景

-   你需要在游戏运行时对UI或某个特效叠加动态模糊、色相偏移等效果，但不想影响场景中的其他元素。
-   你希望实现一个可重用、可配置的“后处理特效包”，通过图形化界面配置后处理材质的输入、顺序和混合方式，然后应用到任意纹理上。
-   你需要将多个后处理步骤（如去噪、色调映射、锐化）封装成一个独立的处理流程，用于非标准的渲染通道（如离线渲染、特效预处理）。

## 蓝图用法

该插件的核心逻辑主要通过资产配置和Actor驱动，未提供直接的运行时蓝图函数节点。其使用主要通过以下方式：

### 核心资产

| 资产 | 说明 |
|---|---|
| `UPPMChainGraph` | 核心资产，用于配置后处理材质链。在编辑器中创建和编辑。 |
| `APPMChainGraphActor` | 用于在运行时驱动 `UPPMChainGraph` 资产执行的Actor。 |

### 使用示例（蓝图描述）

1.  **创建配置资产**：在内容浏览器中右键 -> 杂项 -> Post Process Material Chain Graph，创建一个新的 `PPMChainGraph` 资产。
2.  **配置材质链**：双击打开资产，在细节面板中配置输入纹理（Inputs）和通道（Passes）。在通道中，可以指定使用的后处理材质实例（必须实现 `IPPMChainGraphPassInterface` 接口）、输入来源和输出目标。
3.  **放置驱动Actor**：在场景中放置一个 `PPMChainGraphActor`，将其 `ChainGraph` 属性指向你创建的 `PPMChainGraph` 资产。
4.  **配置输入输出**：通过 `PPMChainGraphActor` 的属性，将需要处理的纹理指定为输入，并在需要时设置输出目标。
5.  **运行时执行**：当 `PPMChainGraphActor` 所在场景激活时，配置的材质链会自动执行，并将结果渲染到指定的渲染目标。

## C++ 用法

### 头文件引入

```cpp
#include "PPMChainGraph.h"
// 如果需要使用 Actor
#include "Actors/PPMChainGraphActor.h"
```

### 基本用法

该插件主要通过资产化配置使用，直接创建 Actor 并设置对应的配置资产是最常见的用法。

```cpp
// 假设已在某个管理类或 Actor 中
UPROPERTY(EditAnywhere, Category = "PPM Chain")
TObjectPtr<UPPMChainGraph> MyChainGraphConfig;

// 在场景中生成驱动 Actor
void AMyManager::SpawnChainGraphActor()
{
    FActorSpawnParameters SpawnParams;
    APPMChainGraphActor* ChainGraphActor = GetWorld()->SpawnActor<APPMChainGraphActor>(
        APPMChainGraphActor::StaticClass(),
        FVector::ZeroVector,
        FRotator::ZeroRotator,
        SpawnParams
    );

    if (ChainGraphActor && MyChainGraphConfig)
    {
        ChainGraphActor->SetChainGraph(MyChainGraphConfig);
    }
}
```

*（示例基于插件 Actor 结构推断）*

### 进阶用法

要实现自定义的后处理通道，需要创建材质并实现 `IPPMChainGraphPassInterface` 接口。这是扩展该插件功能的主要方式。

```cpp
// MyCustomPassInterface.h
#pragma once
#include "PPMChainGraphPassInterface.h" // 假设接口头文件路径
#include "MyCustomPassInterface.generated.h"

UINTERFACE()
class UMyCustomPassInterface : public UPPMChainGraphPassInterface
{
    GENERATED_BODY()
};

class IMyCustomPassInterface : public IPPMChainGraphPassInterface
{
    GENERATED_BODY()

public:
    // 可以在这里定义额外的蓝图可调用或可配置方法
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "PPM Chain")
    void ConfigurePass(const FPPMChainGraphInput& Input);
};
```

然后，你的后处理材质需要创建为一个材质实例，并设置其父类为实现了 `IMyCustomPassInterface` 的材质。

## Demo 示例

下面是一个简单的自定义后处理通道接口实现示例：

### MyCustomPassInterface.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "PPMChainGraphPassInterface.h"
#include "MyCustomPassInterface.generated.h"

UINTERFACE(BlueprintType)
class UMyCustomPassInterface : public UPPMChainGraphPassInterface
{
    GENERATED_BODY()
};

class MYPROJECT_API IMyCustomPassInterface : public IPPMChainGraphPassInterface
{
    GENERATED_BODY()

public:
    // 可选的额外蓝图可调用方法
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "PPM Chain Pass")
    float GetCustomIntensity() const;
};
```

### MyCustomPassMaterialFunction (示意，非C++代码)
在材质编辑器中，创建一个材质或材质函数，使其“实现接口”中包含 `IMyCustomPassInterface`，并实现 `GetCustomIntensity` 函数节点。然后，在 `PPMChainGraph` 资产的通道配置中，将此材质指定为 `Pass Material`。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PPMChainGraph` | 运行时核心模块，定义链图资产、Actor和接口。依赖 `UnrealEd` (用于资产编辑) |
| `UnrealEd` | 用于资产编辑器和细节定制。由于 PPMChainGraph 依赖它，使用者通常间接依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `5c7314c3` | Fix Color Correct Regions render rect being truncated when dynamic resolution scales below 1.0. | 修复动态分辨率缩放低于1.0时，颜色校正区域渲染矩形被截断的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 性能分析相关宏。 |
| 2025-02-18 | `8c3ee882` | PPMChainGraph: Export public classes & structs, per third-party request. | 根据第三方请求，导出 PPMChainGraph 的公共类和结构体。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 在整个 Engine/ 目录下替换 `IsValid(this)`。 |

### 维护评价

该插件创建于2024年初，是一个相对年轻的实验性功能。从近期提交记录看，其维护活动主要集中在引擎级别的代码清理和兼容性修复（如日志宏迁移、废弃宏替换），而非功能性的重大更新或Bug修复。最近的实质性改动（导出公共符号）发生在一年前。由于它仍标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，表明它仍处于开发验证阶段，API和功能可能不稳定。**推荐用于实验和原型开发，暂不建议在生产环境中作为核心依赖使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/PostProcessMaterialChainGraph)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中发现)
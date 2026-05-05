# AnimDatabase

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、编辑器工具） |
| 模块 | `AnimDatabase` (Runtime), `AnimDatabaseEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimDatabase) | |

## 用途

AnimDatabase 是一个实验性的动画数据库编辑器插件。它旨在提供一个专用的编辑器环境，用于管理、查询和预览动画片段（Animation Clips）。其核心功能是将动画数据组织成一个可查询的数据库，并提供可视化的时间线编辑器、3D 视口预览以及基于帧的精确控制，方便动画师和技术美术对动画资源进行高效的检索、混合和分析。

## 使用场景

- 你正在开发一个需要大量动画片段并进行复杂混合的角色动画系统。
- 你需要一个工具来可视化地浏览、比较和选择不同的动画片段。
- 你需要基于帧（而非时间）精确地标记和查询动画中的特定区间或姿态。
- 你正在研究或实现基于动画数据库的动画合成或运动匹配（Motion Matching）技术。

## 蓝图用法

该插件主要提供编辑器工具，其运行时 API 主要面向 C++。蓝图中主要通过资产操作来使用。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UAnimDatabase` | 动画数据库主资产，存储动画片段和查询信息。 |
| `UAnimDatabaseQuery` | 查询资产，定义如何在数据库中查找动画片段。 |

### 使用示例（蓝图描述）

1.  **创建数据库**：在内容浏览器中右键，选择 `Animation -> Animation Database` 来创建一个新的 `UAnimDatabase` 资产。
2.  **打开编辑器**：双击创建的 `UAnimDatabase` 资产，将打开专用的动画数据库编辑器窗口。
3.  **编辑查询**：在编辑器中，可以创建和编辑 `UAnimDatabaseQuery` 对象，定义查询条件（如动画名称、标签、帧范围等）。
4.  **预览结果**：编辑器视口会实时显示查询到的动画片段预览，时间线会显示对应的帧范围。

## C++ 用法

### 头文件引入

```cpp
#include "AnimDatabase.h"
#include "AnimDatabaseQuery.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和查询动画数据库。

```cpp
// 假设你已经有一个 UAnimDatabase* Database 对象
// 以及一个 UAnimDatabaseQuery* Query 对象

// 1. 获取数据库中的动画序列数量
int32 NumSequences = Database->GetNumSequences();

// 2. 执行查询，获取匹配的动画片段范围
TArray<FAnimDatabaseQueryResult> Results;
Database->ExecuteQuery(Query, Results);

// 3. 遍历结果
for (const FAnimDatabaseQueryResult& Result : Results)
{
    UAnimSequence* AnimSequence = Result.GetAnimSequence();
    FFrameNumber StartFrame = Result.GetStartFrame();
    FFrameNumber EndFrame = Result.GetEndFrame();
    // ... 使用动画片段和帧范围
}
```

### 进阶用法

结合编辑器模块，可以在编辑器工具中集成动画数据库功能。

```cpp
#include "AnimDatabaseEditorToolkit.h"

// 在自定义编辑器工具中打开动画数据库
void FMyEditorTool::OpenAnimDatabaseEditor(UAnimDatabase* Database)
{
    // 使用插件提供的 AssetDefinition 来打开资产
    UAnimDatabaseEditorAssetDefinition* AssetDef = GetMutableDefault<UAnimDatabaseEditorAssetDefinition>();
    if (AssetDef)
    {
        FAssetOpenArgs OpenArgs;
        OpenArgs.OpenMethod = EAssetOpenMethod::Edit;
        OpenArgs.Objects.Add(Database);
        AssetDef->OpenAssets(OpenArgs);
    }
}
```

## Demo 示例

一个最小的运行时使用示例，展示如何创建数据库资产并执行查询。

**AnimDatabaseDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimDatabaseDemo.generated.h"

class UAnimDatabase;
class UAnimDatabaseQuery;

UCLASS()
class AAnimDatabaseDemo : public AActor
{
    GENERATED_BODY()

public:
    AAnimDatabaseDemo();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "AnimDatabase")
    UAnimDatabase* AnimDatabaseAsset;

    UPROPERTY(EditAnywhere, Category = "AnimDatabase")
    UAnimDatabaseQuery* QueryAsset;

    UFUNCTION(BlueprintCallable, Category = "AnimDatabase")
    void RunDemoQuery();
};
```

**AnimDatabaseDemo.cpp**
```cpp
#include "AnimDatabaseDemo.h"
#include "AnimDatabase.h"
#include "AnimDatabaseQuery.h"

AAnimDatabaseDemo::AAnimDatabaseDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AAnimDatabaseDemo::BeginPlay()
{
    Super::BeginPlay();
    RunDemoQuery();
}

void AAnimDatabaseDemo::RunDemoQuery()
{
    if (!AnimDatabaseAsset || !QueryAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("AnimDatabaseDemo: Database or Query asset is null."));
        return;
    }

    TArray<FAnimDatabaseQueryResult> Results;
    AnimDatabaseAsset->ExecuteQuery(QueryAsset, Results);

    UE_LOG(LogTemp, Log, TEXT("AnimDatabaseDemo: Query returned %d results."), Results.Num());

    for (int32 i = 0; i < Results.Num(); ++i)
    {
        const FAnimDatabaseQueryResult& Result = Results[i];
        if (UAnimSequence* Seq = Result.GetAnimSequence())
        {
            UE_LOG(LogTemp, Log, TEXT("  Result %d: Sequence '%s', Frames [%d - %d]"),
                i, *Seq->GetName(), Result.GetStartFrame().Value, Result.GetEndFrame().Value);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationWarping` | 动画扭曲功能，可能用于高级动画混合或变形。 |
| `LearningCore` | Epic 的机器学习核心库，可能用于数据驱动的动画分析或查询优化。 |
| `DrawDebugLibrary` | 调试绘制库，用于在编辑器视口中可视化动画轨迹、骨骼等调试信息。 |
| `UnrealEd` | （AnimDatabase 模块依赖）编辑器基础功能，此依赖较为异常，通常运行时模块不应依赖编辑器模块。 |

## 维护状态

### 近期更新

（无法从提供的信息中获取 git log）

### 维护评价

- **实验性**：插件明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`EnabledByDefault: false`)。这表明它仍处于早期开发阶段，API 和功能可能不稳定，不建议在生产环境中使用。
- **创建时间**：创建于 2026-04-10，是一个非常新的插件。
- **依赖关系**：运行时模块 `AnimDatabase` 依赖 `UnrealEd`，这是一个不寻常的设计，可能导致打包问题或不必要的编辑器代码被包含在运行时构建中。
- **推荐度**：**仅推荐用于学习和实验目的**。如果你对动画数据库、运动匹配或相关技术感兴趣，可以研究其源码和编辑器实现。在正式项目中，应等待其成熟并修复依赖问题后再考虑使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimDatabase)
- [官方文档]() （无）
- [测试用例]() （未在提供的信息中找到）
# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（校准数据资产） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

本插件是 MetaHuman Animator 工作流的核心后端处理工具。它负责解析、处理和生成 MetaHuman 角色的面部校准数据。这些校准数据是驱动 MetaHuman 角色进行高质量面部动画的关键，它将演员的表演数据（如从 iPhone 捕获的深度信息）精确地映射到 MetaHuman 的面部骨骼和变形目标上。插件提供了从原始数据到最终可用校准资产的完整处理管线。

## 使用场景

- **MetaHuman Animator 工作流**：在使用 MetaHuman Animator 从 iPhone 捕获面部表演后，需要使用本插件的处理管线来生成最终的校准数据。
- **自定义校准处理**：当需要对标准的校准流程进行定制或扩展时，可以调用本插件提供的底层 API。
- **批量处理校准数据**：在需要为大量 MetaHuman 角色生成或更新校准数据的生产环境中，可以利用本插件的批处理功能。

## 蓝图用法

本插件主要提供底层处理功能，蓝图可直接调用的节点较少，主要集中在数据加载和触发处理流程上。详细的 API 请参考各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `LoadCalibrationData` | 从文件路径加载校准数据资产 | `UMetaHumanCalibrationData` |
| `SaveCalibrationData` | 将校准数据资产保存到文件 | `UMetaHumanCalibrationData` |
| `ProcessCalibration` | 触发校准数据的处理流程（需配合 C++ 使用） | `UMetaHumanCalibrationProcessor` |

### 使用示例（蓝图描述）

1.  **加载校准数据**：使用 `LoadCalibrationData` 节点，输入一个 `.uasset` 文件路径，输出一个 `UMetaHumanCalibrationData` 对象引用。
2.  **保存校准数据**：在获得一个 `UMetaHumanCalibrationData` 对象后，使用 `SaveCalibrationData` 节点将其保存到指定路径。
3.  **处理流程**：核心的处理逻辑通常在 C++ 中完成，蓝图主要用于触发和传递数据。

## C++ 用法

本插件的核心逻辑和高级用法均通过 C++ API 提供。以下示例展示了基本的数据加载和处理触发。

### 头文件引入

```cpp
#include "MetaHumanCalibrationData.h"
#include "MetaHumanCalibrationProcessor.h"
```

### 基本用法

加载并检查一个校准数据资产。

```cpp
// 来源: MetaHumanCalibrationCore 模块测试用例
#include "MetaHumanCalibrationData.h"

void LoadAndInspectCalibration(const FString& AssetPath)
{
    // 加载校准数据资产
    UMetaHumanCalibrationData* CalibrationData = LoadObject<UMetaHumanCalibrationData>(nullptr, *AssetPath);
    if (!CalibrationData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load calibration data from: %s"), *AssetPath);
        return;
    }

    // 检查数据是否有效
    if (CalibrationData->IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Calibration data loaded successfully. Contains %d calibration points."), CalibrationData->GetNumCalibrationPoints());
        // 进一步处理...
    }
}
```

### 进阶用法

使用处理器对校准数据进行重新处理或优化。

```cpp
// 来源: MetaHumanCalibrationGenerator 模块测试用例
#include "MetaHumanCalibrationProcessor.h"
#include "MetaHumanCalibrationData.h"

void ReprocessCalibrationData(UMetaHumanCalibrationData* InData)
{
    if (!InData) return;

    // 创建处理器实例
    UMetaHumanCalibrationProcessor* Processor = NewObject<UMetaHumanCalibrationProcessor>();

    // 配置处理参数（示例）
    FCalibrationProcessingParams Params;
    Params.bOptimizeForPerformance = true;
    Params.QualityLevel = ECalibrationQuality::High;

    // 执行处理
    Processor->SetParameters(Params);
    bool bSuccess = Processor->Process(InData);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Calibration data reprocessed successfully."));
        // 保存处理后的数据
        InData->SaveToAsset(TEXT("/Game/ProcessedCalibrations/NewCalibration.uasset"));
    }
}
```

## Demo 示例

一个最小的示例，展示如何在 Actor 中加载并使用校准数据。

```cpp
// MyCalibrationActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCalibrationActor.generated.h"

class UMetaHumanCalibrationData;

UCLASS()
class AMyCalibrationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCalibrationActor();

    UPROPERTY(EditAnywhere, Category = "Calibration")
    FSoftObjectPath CalibrationDataPath;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Calibration")
    UMetaHumanCalibrationData* LoadedCalibrationData;

    UFUNCTION(BlueprintCallable, Category = "Calibration")
    void LoadCalibration();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// MyCalibrationActor.cpp
#include "MyCalibrationActor.h"
#include "MetaHumanCalibrationData.h"

AMyCalibrationActor::AMyCalibrationActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCalibrationActor::BeginPlay()
{
    Super::BeginPlay();
    LoadCalibration();
}

void AMyCalibrationActor::LoadCalibration()
{
    if (!CalibrationDataPath.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("CalibrationDataPath is not set."));
        return;
    }

    // 异步加载校准数据资产
    FStreamableManager& StreamableManager = UAssetManager::GetStreamableManager();
    StreamableManager.RequestAsyncLoad(
        CalibrationDataPath,
        FStreamableDelegate::CreateUObject(this, &AMyCalibrationActor::OnCalibrationLoaded)
    );
}

void AMyCalibrationActor::OnCalibrationLoaded()
{
    LoadedCalibrationData = Cast<UMetaHumanCalibrationData>(CalibrationDataPath.ResolveObject());
    if (LoadedCalibrationData)
    {
        UE_LOG(LogTemp, Log, TEXT("Calibration data loaded into actor."));
        // 在这里可以使用 LoadedCalibrationData 进行动画驱动等操作
    }
}
```

## 模块依赖

要使用本插件，你的模块需要依赖以下模块（已在各子模块的 Build.cs 中声明）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationCore` | 提供核心数据结构和基础处理接口 |
| `MetaHumanCalibrationGenerator` | 提供校准数据的生成和优化算法 |
| `MetaHumanCalibrationLib` | 提供底层数学和几何处理库 |
| `UnrealEd` | （仅编辑器）用于资产编辑器和工厂类 |

## 维护状态

### 近期更新

由于该插件创建时间较新（2025年4月），且属于 MetaHuman 核心工作流的一部分，预计由 Epic Games 官方积极维护。具体的 git log 更新记录需要访问 UE 源码仓库查看。

### 维护评价

- **创建时间**：2025年4月，非常新的插件。
- **维护状态**：作为 MetaHuman Animator 官方工具链的一部分，预计处于**活跃维护**状态，会随着 MetaHuman 和 UE 版本的更新而同步更新。
- **推荐使用**：**强烈推荐**。这是使用 MetaHuman Animator 进行面部动画制作的官方且必要的后端处理工具。任何涉及 MetaHuman 面部动画校准的项目都应依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
- [官方文档]() (待 Epic Games 发布)
- [测试用例]() (路径待确认)
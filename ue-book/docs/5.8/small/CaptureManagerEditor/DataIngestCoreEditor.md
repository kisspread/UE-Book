# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产创建逻辑） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

该插件是 Unreal Engine 虚拟制作流程的核心组件，专门用于处理来自 MetaHuman Animator 等捕捉设备的原始数据（如多视图视频序列、深度信息、音频和相机校准数据）。它解决的核心问题是将这些外部工具生成的“捕获存档”数据自动化地转换为引擎内可直接使用的标准资产（如 `UImgMediaSource`、`USoundWave`、`UCameraCalibration`），并智能管理这些资产的命名、路径和关联关系，从而大幅简化从表演捕捉到数字角色创建的工作流。

## 使用场景

- 你使用 MetaHuman Animator 完成了对一位演员的面部表演捕捉，生成了一个包含视频、校准等文件的捕获存档。你可以使用此插件，一键将这些数据导入引擎，自动创建对应的图像序列源、音频波形和镜头文件资产，为后续的 MetaHuman 驱动做好准备。
- 在虚拟制作片场，你使用多台摄像机和 Live Link Hub 设备同步拍摄了场景。此插件可以辅助你导入和管理这些多机位的捕捉数据，并与 Live Link 系统协同工作。
- 你需要为项目中的数字角色建立一套标准化的捕捉数据导入和管理流程，此插件提供了底层的资产创建和命名策略。

## 蓝图用法

该插件的核心功能主要在 C++ 层面提供，用于构建资产导入管线。蓝图层面主要通过 `CaptureManagerIngestBlueprint` 和 `CaptureManagerDeviceBlueprint` 模块暴露功能。以下是基于核心模块（DataIngestCoreEditor）推断出的核心逻辑节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BuildAssetData` | 根据原始的 `FIngestCaptureData` 和命名策略，构建出可用于资产创建的 `FCreateAssetsData` 结构体。 | `UE::CaptureManager` (全局函数) |
| `CreateAssets_GameThread` | 在游戏线程上，根据 `FCreateAssetsData` 列表批量创建所有捕获资产，并返回创建结果信息。 | `FIngestAssetCreator` |
| `GetAssetIfExists` | 检查指定路径下是否存在某个资产，如果存在则返回。 | `FIngestAssetCreator` |

### 使用示例（蓝图描述）

在蓝图中，你通常会使用高级的 `CaptureManagerIngestBlueprint` 模块提供的节点来发起导入。其底层工作流程大致如下：
1.  调用一个节点（例如 `Import Capture Data`）来解析捕获存档，获得一个 `FIngestCaptureData` 对象。
2.  使用 `FAssetNamingStrategy` 来确定每个子资产（视频序列、音频等）的预期名称和路径。
3.  调用 `BuildAssetData` 节点，将原始数据和命名策略转换为结构化的 `FCreateAssetsData`。
4.  最后，调用 `CreateAssets_GameThread` 节点，传入 `FCreateAssetsData` 数组，执行实际的资产创建操作。该节点会返回一个结果数组，指示每个 Take 的创建成功或失败信息。

## C++ 用法

该插件的 C++ API 主要用于构建自定义的资产导入管线或集成到更大的工具中。

### 头文件引入

```cpp
#include "DataIngestCoreEditor/Public/IngestAssetCreator.h"
#include "DataIngestCoreEditor/Internal/CaptureManagerIngestPreparation.h"
#include "DataIngestCoreEditor/Public/DataIngestCoreError.h"
```

### 基本用法

以下示例展示了如何使用 `FAssetNamingStrategy` 和 `FIngestAssetCreator` 来创建资产。数据来源假设为从某处解析得到的 `FIngestCaptureData`。

```cpp
// 文件路径: 基于 Public/IngestAssetCreator.h 和 Internal/CaptureManagerIngestPreparation.h 推断
// 假设 `IngestCaptureData` 已通过某种方式获得 (例如从捕获存档文件解析)
FIngestCaptureData IngestCaptureData = ...;

// 1. 创建资产命名策略
UE::CaptureManager::FAssetNamingStrategy NamingStrategy(IngestCaptureData);

// 2. 根据原始数据和命名策略，构建用于资产创建的结构化数据
UE::CaptureManager::FCreateAssetsData CreateAssetsData = UE::CaptureManager::BuildAssetData(IngestCaptureData, NamingStrategy);

// 3. 将单个 Take 的数据放入数组 (批量处理时会包含多个)
TArray<UE::CaptureManager::FCreateAssetsData> CreateAssetDataList;
CreateAssetDataList.Add(CreateAssetsData);

// 4. 定义回调以接收每个 Take 的创建结果
auto PerTakeCallback = UE::CaptureManager::FIngestAssetCreator::FPerTakeCallback::CreateLambda(
    [](const UE::CaptureManager::FIngestAssetCreator::FPerTakeResult& Result)
    {
        if (Result.Value.HasError())
        {
            UE_LOG(LogTemp, Error, TEXT("Take %d creation failed: %s"), Result.Key, *Result.Value.GetError().GetMessage().ToString());
        }
        else
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d created successfully."), Result.Key);
        }
    }
);

// 5. 在游戏线程上执行资产创建
TArray<UE::CaptureManager::FCaptureDataAssetInfo> CreatedAssets =
    UE::CaptureManager::FIngestAssetCreator::CreateAssets_GameThread(CreateAssetDataList, PerTakeCallback);
```

### 进阶用法

进阶用法涉及更精细的错误处理和资产检查。可以使用 `FAssetCreationError` 类来解析错误类型，并使用 `FCaptureDataAssetInfo` 结构体来验证创建后的资产信息。

```cpp
// 接上例的 `CreatedAssets`
for (const UE::CaptureManager::FCaptureDataAssetInfo& AssetInfo : CreatedAssets)
{
    // 检查图像序列资产
    for (const UE::CaptureManager::FCaptureDataAssetInfo::FImageSequence& ImgSeq : AssetInfo.ImageSequences)
    {
        if (ImgSeq.Asset)
        {
            UE_LOG(LogTemp, Log, TEXT("Created Image Sequence: %s, Timecode: %s"),
                *ImgSeq.Asset->GetName(),
                *ImgSeq.Timecode.ToString());
        }
    }
    // 检查音频资产
    for (const UE::CaptureManager::FCaptureDataAssetInfo::FAudio& Audio : AssetInfo.Audios)
    {
        if (Audio.Asset)
        {
            UE_LOG(LogTemp, Log, TEXT("Created Audio: %s"), *Audio.Asset->GetName());
        }
    }
    // 可以类似地检查 DepthSequences 和 Calibrations
}
```

## Demo 示例

一个最小的示例，演示如何创建一个带有自定义命名策略的资产导入任务。

**MyCustomIngestor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DataIngestCoreEditor/Internal/CaptureManagerIngestPreparation.h"
#include "DataIngestCoreEditor/Public/IngestAssetCreator.h"

class FMyCustomIngestor
{
public:
    /** 执行一次简单的资产导入 */
    void RunIngestExample(const UE::CaptureManager::FIngestCaptureData& Data);

private:
    /** 自定义一个命名策略，例如给所有资产加上项目前缀 */
    class FProjectPrefixNamingStrategy : public UE::CaptureManager::FAssetNamingStrategy
    {
    public:
        using FAssetNamingStrategy::FAssetNamingStrategy;

        // 重写某个资产的获取名称方法，添加前缀
        UE::CaptureManager::FString GetCaptureDataAssetName() const override
        {
            return TEXT("ProjectA_") + FAssetNamingStrategy::GetCaptureDataAssetName();
        }
    };
};
```

**MyCustomIngestor.cpp**
```cpp
#include "MyCustomIngestor.h"

void FMyCustomIngestor::RunIngestExample(const UE::CaptureManager::FIngestCaptureData& Data)
{
    // 使用自定义命名策略
    FProjectPrefixNamingStrategy NamingStrategy(Data);

    // 构建创建数据
    UE::CaptureManager::FCreateAssetsData CreateData = UE::CaptureManager::BuildAssetData(Data, NamingStrategy);

    TArray<UE::CaptureManager::FCreateAssetsData> DataList;
    DataList.Add(CreateData);

    // 简单的同步回调（仅用于演示）
    auto Callback = UE::CaptureManager::FIngestAssetCreator::FPerTakeCallback::CreateLambda(
        [](const UE::CaptureManager::FIngestAssetCreator::FPerTakeResult& Result)
        {
            // 简单打印结果
        }
    );

    // 创建资产
    TArray<UE::CaptureManager::FCaptureDataAssetInfo> Results =
        UE::CaptureManager::FIngestAssetCreator::CreateAssets_GameThread(DataList, Callback);

    // 处理结果...
    if (!Results.IsEmpty())
    {
        // 例如，访问第一个 Take 的第一个图像序列资产
        UE_LOG(LogTemp, Log, TEXT("First asset in first take: %s"),
            Results[0].ImageSequences.Num() > 0 ? *Results[0].ImageSequences[0].Asset->GetName() : TEXT("None"));
    }
}
```

## 模块依赖

由于 `DataIngestCoreEditor` 模块的 Build.cs 未直接提供，依赖关系主要基于其功能推断。其主要依赖于以下模块来完成资产导入：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 用于创建和管理 `UImgMediaSource` 类型的图像序列资产。 |
| `CameraCalibrationCore` | 用于处理 `UCameraCalibration` 和镜头文件资产。 |
| `AssetTools` | 提供底层的资产创建、导入任务（`UAssetImportTask`）管理功能。 |

*无特殊依赖（仅标准 Core/Engine/Slate 等）*。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将 DeviceBlueprint 模块中的设备术语通用化，提高兼容性。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式摄取蓝图 API 移至 “Blocking” 子类别，优化蓝图节点组织。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块，扩展设备蓝图功能。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退了某个变更。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | （同上）新增 CaptureManagerDeviceBlueprint 模块。 |

### 维护评价

该插件创建于 2025 年初，非常年轻。从近期（2026 年 4 月）的 git 历史来看，提交频率非常高，且包含了新功能的添加（DeviceBlueprint 模块）、API 的优化重组（移动阻塞 API）和术语通用化等实质性更新。这表明该插件处于 **活跃维护** 状态，是 Epic Games 虚拟制作工具链中正在积极开发和完善的部分。作为一个默认禁用的插件，它很可能服务于特定的高级工作流或仍在集成测试中。**推荐在虚拟制作相关项目中评估和使用。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]() (暂无)
- [测试用例]() (测试文件路径未在提供信息中明确，通常可能位于 `Engine/Tests/` 下)
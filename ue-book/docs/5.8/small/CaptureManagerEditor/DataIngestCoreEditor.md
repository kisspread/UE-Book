# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产、蓝图模块、设置） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

该插件是 Epic Games 虚拟制作工具链的核心部分，主要用于将现场捕获的**数字人扫描数据**（如 MetaHuman 捕获）从捕获设备或 Live Link Hub 导入到 Unreal Engine 中，并自动创建必要的资产。它解决的核心问题是将复杂的捕获存档数据（包含图像序列、深度序列、音频、相机校准等）高效、自动地转换为引擎可用的资产（如 `UFootageCaptureData`、`UImgMediaSource`、`UCameraCalibration`、`USoundWave` 等），并处理资产命名、路径规划和元数据关联。

简单来说，它是连接**物理世界捕获**与**虚拟世界引擎资产**的桥梁，简化了高质量数字人或场景资产的生产流程。

## 使用场景

- **数字人创作**：你在使用 MetaHuman 等技术捕获真人表演后，需要将捕获数据导入 UE 以创建和编辑数字人。此插件自动化了整个导入和资产创建过程。
- **虚拟制片**：在 LED 虚拟制片中，你可能需要将实拍镜头与实时渲染的虚拟场景合成，该插件可以帮你导入并管理这些镜头的源素材。
- **资产流水线**：你的工作室建立了自动化的资产导入流水线，需要批量、可靠地将捕获设备生成的原始数据转换为 UE 资产，并与 Live Link 等系统集成。

## 蓝图用法

当前提供的 `DataIngestCoreEditor` 模块主要提供 C++ API 用于资产创建，未直接暴露蓝图节点。蓝图功能由其他模块（如 `CaptureManagerIngestBlueprint`）提供。请参阅该模块的文档获取蓝图接口。

### 核心节点

由于核心资产创建逻辑位于 C++ 中，蓝图层更多用于触发流程和参数配置。以下为概念性节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Ingest Assets` | 触发整个资产导入和创建流程 | `UCaptureManagerIngestBlueprint` (推测) |
| `Get Import Progress` | 查询当前导入任务的进度和状态 | `UCaptureManagerIngestBlueprint` (推测) |

### 使用示例（蓝图描述）

蓝图中通常的调用流程是：
1. 从 `Capture Manager Device Blueprint` 模块获取设备连接和会话信息。
2. 配置导入参数（如命名模板、输出路径），这些参数可能在 `Capture Manager Editor Settings` 中设置。
3. 调用类似 “Start Ingest” 的蓝图节点，该节点内部会调用 `FIngestAssetCreator` 等 C++ API。
4. 监听进度和完成回调，获取创建好的资产引用。

## C++ 用法

核心的资产创建逻辑位于 `DataIngestCoreEditor` 模块中，主要通过 `FIngestAssetCreator` 和 `FAssetNamingStrategy` 类实现。

### 头文件引入

```cpp
#include "IngestAssetCreator.h"
#include "CaptureManagerIngestPreparation.h" // 用于 FAssetNamingStrategy
```

### 基本用法

从源码中可以看到，主要的资产创建流程是：
1. 使用 `FAssetNamingStrategy` 根据捕获数据和设置，为即将生成的资产计算出正确的名称和路径。
2. 调用 `BuildAssetData` 将原始捕获数据 `FIngestCaptureData` 和命名策略转换为结构化的 `FCreateAssetsData`。
3. 使用 `FIngestAssetCreator::CreateAssets_GameThread` 批量创建资产并获取结果。

```cpp
// 1. 准备捕获数据（通常从解析后的存档中获得）
FIngestCaptureData IngestCaptureData = ...;

// 2. 创建命名策略
UE::CaptureManager::FAssetNamingStrategy NamingStrategy(IngestCaptureData, ImportID, DeviceName);

// 3. 构建资产创建所需的数据结构
UE::CaptureManager::FCreateAssetsData CreateAssetsData = UE::CaptureManager::BuildAssetData(IngestCaptureData, NamingStrategy);

// 4. 创建资产（必须在 GameThread 调用）
TArray<UE::CaptureManager::FCaptureDataAssetInfo> CreatedAssets = 
    UE::CaptureManager::FIngestAssetCreator::CreateAssets_GameThread({CreateAssetsData}, PerTakeCallback);

// 5. 处理结果，例如获取创建的 FootageCaptureData 资产
if (CreatedAssets.Num() > 0)
{
    const auto& AssetInfo = CreatedAssets[0];
    // AssetInfo.ImageSequences, AssetInfo.Calibrations 等包含了创建好的资产引用
}
```
**注意**：`CreateAssets_GameThread` 必须在游戏线程调用。

### 进阶用法

可以处理多 Take 的批量导入，并利用回调函数跟踪每个 Take 的创建进度和错误。

```cpp
// 准备多个 Take 的数据
TArray<FCreateAssetsData> AllTakesData;
// ... 填充多个 FCreateAssetsData ...

// 定义回调，处理每个 Take 的结果
FIngestAssetCreator::FPerTakeCallback Callback = [](const FIngestAssetCreator::FPerTakeResult& Result)
{
    int32 TakeId = Result.Get<0>();
    const FIngestAssetCreator::FAssetCreationResult& CreationResult = Result.Get<1>();
    if (CreationResult.HasValue())
    {
        UE_LOG(LogTemp, Log, TEXT("Take %d assets created successfully."), TakeId);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create assets for Take %d: %s"), TakeId, *CreationResult.GetError().GetMessage().ToString());
    }
};

// 批量创建
TArray<FCaptureDataAssetInfo> AllCreatedTakes = 
    FIngestAssetCreator::CreateAssets_GameThread(AllTakesData, Callback);
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在编辑器工具或命令行工具中调用核心 API 来创建资产。假设我们已经解析出了一个 `FIngestCaptureData` 对象。

**MyIngestTool.h**
```cpp
// MyIngestTool.h
#pragma once

#include "CoreMinimal.h"

class UFootageCaptureData;
namespace UE::CaptureManager { struct FIngestCaptureData; }

class FMyIngestTool
{
public:
    /** 模拟导入一个捕获数据包 */
    static UFootageCaptureData* ImportSingleCaptureData(const UE::CaptureManager::FIngestCaptureData& InData);
};
```

**MyIngestTool.cpp**
```cpp
// MyIngestTool.cpp
#include "MyIngestTool.h"
#include "IngestAssetCreator.h"
#include "CaptureManagerIngestPreparation.h"
#include "FootageCaptureData.h"

UFootageCaptureData* FMyIngestTool::ImportSingleCaptureData(const UE::CaptureManager::FIngestCaptureData& InData)
{
    // 1. 创建命名策略（这里使用简单的 ImportID）
    const FString ImportID = FGuid::NewGuid().ToString();
    UE::CaptureManager::FAssetNamingStrategy NamingStrategy(InData, ImportID, TEXT("DefaultDevice"));

    // 2. 构建资产创建数据
    UE::CaptureManager::FCreateAssetsData CreateData = UE::CaptureManager::BuildAssetData(InData, NamingStrategy);

    // 3. 创建资产 (在GameThread调用)
    TArray<UE::CaptureManager::FCaptureDataAssetInfo> CreatedAssets =
        UE::CaptureManager::FIngestAssetCreator::CreateAssets_GameThread(
            {CreateData},
            /*PerTakeCallback=*/[](const auto&){} // 空回调
        );

    // 4. 尝试查找或创建主 FootageCaptureData 资产
    if (CreatedAssets.Num() > 0)
    {
        const FString& PackagePath = CreateData.PackagePath;
        const FString& AssetName = CreateData.CaptureDataAssetName;

        // 使用 API 获取已创建的资产，或创建一个新的主资产来关联它们
        UFootageCaptureData* FootageData = UE::CaptureManager::FIngestAssetCreator::GetOrCreateAsset<UFootageCaptureData>(PackagePath, AssetName);
        if (FootageData)
        {
            // 将创建的序列、音频等资产关联到 FootageData (这部分逻辑可能在更上层)
            // FootageData->ImageSequences = CreatedAssets[0].ImageSequences;
            // ... 等等
            UE_LOG(LogTemp, Log, TEXT("Successfully prepared FootageCaptureData at %s"), *FootageData->GetPathName());
        }
        return FootageData;
    }

    return nullptr;
}
```

## 模块依赖

根据模块功能和命名推测，此插件（特别是当前分析的 `DataIngestCoreEditor` 模块）可能依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 处理 `UImgMediaSource` 资产的创建 |
| `CameraCalibration` | 处理 `UCameraCalibration` 资产的创建 |
| `LiveLinkInterface` | 与 Live Link 系统集成，用于设备发现和数据流 |
| `LiveLinkHub` | 核心的 Live Link Hub 功能 |
| `CaptureManagerCore` (推测) | 可能提供基础的捕获数据结构 `FIngestCaptureData` 等 |

**注意**：完整的依赖关系需要查看每个模块的 `.Build.cs` 文件。对于编辑器工具，还可能依赖 `AssetTools`, `ContentBrowser` 等模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将设备蓝图中的设备术语通用化，提升代码灵活性。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将阻塞式的摄入蓝图 API 移至一个“阻塞”子类别下，使蓝图节点组织更清晰。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增了 `CaptureManagerDeviceBlueprint` 模块，用于设备相关的蓝图功能。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 回退了之前的提交 CL53274396。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次尝试添加 `CaptureManagerDeviceBlueprint` 模块（后被回退并重新添加）。 |

### 维护评价

- **活跃维护**：该插件创建于 2025 年初，**2026 年 4 月底仍有密集的功能性提交**（添加新模块、重构 API 分类），表明其处于**非常活跃的开发和维护状态**。
- **稳定性**：最新的提交记录显示，团队正在快速迭代其蓝图接口和模块结构，说明该插件可能仍处于**功能完善期**，API 和结构可能还会发生变化。
- **推荐使用**：如果你是 Epic 的虚拟制作工具链（如 MetaHuman 捕获工作流）的用户或开发者，此插件是核心组件，**推荐关注和使用**。对于外部开发者，鉴于其活跃的开发状态，建议密切跟踪官方更新，并做好应对 API 变更的准备。

**警告**：由于更新非常频繁，在生产环境中使用时，请确保锁定与你的 UE 版本匹配的插件版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档](https://docs.unrealengine.com) (无专门文档，可能在 Virtual Production 或 MetaHuman 文档中提及)
- [测试用例] (未在插件目录内发现测试文件，可能位于 `Engine/Tests/` 下)
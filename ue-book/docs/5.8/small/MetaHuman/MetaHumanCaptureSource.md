# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-02-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个功能全面的工具包，旨在将真实演员的面部表演转化为驱动 MetaHuman 数字人类资产的动画。它解决的核心问题是：如何高效、准确地从电影或视频素材中捕捉演员的面部动作，并将其应用于高保真数字角色。该插件包含了从数据导入（Ingest）、面部追踪（Face Contour Tracking）、动画求解（Animation Solving）到最终资产生成和管理的完整管线。它是连接真实世界表演与数字 MetaHuman 资产的核心桥梁，用于影视、游戏或虚拟制作中创建逼真的人类角色动画。

## 使用场景

- **影视特效与预演**：在虚拟制片或后期制作中，为 MetaHuman 角色快速创建基于真实演员表演的面部动画。
- **游戏角色动画**：使用真实表演数据批量生成大量 NPC 的对话或情绪动画。
- **数字人直播**：驱动 MetaHuman 虚拟形象进行实时或离线直播。
- **面部动画研究**：利用其先进的追踪和求解算法作为研究基础。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Startup` | 启动捕获源并获取可用 Take 信息。 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新并返回当前可用的 Take 信息列表。 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置导入数据的目标目录和资产路径。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 获取指定 Take 的详细信息。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeIds` | 获取所有可用 Take 的 ID 列表。 | `UMetaHumanCaptureSourceSync` |
| `CanStartup` | 检查捕获源是否可以启动。 | `UMetaHumanCaptureSourceSync` |
| `IsProcessing` | 检查当前是否正在处理任务。 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消指定 Take 列表的处理任务。 | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

1.  **创建捕获源对象**：在蓝图中使用 `Construct Object from Class` 节点，选择 `MetaHumanCaptureSourceSync` 类创建一个实例。
2.  **配置捕获源**：设置对象的属性，如 `CaptureSourceType` (例如 `LiveLinkFaceArchives`) 和 `StoragePath` (指向包含录制数据的文件夹)。
3.  **启动与获取 Take**：调用 `Startup` 节点连接设备或扫描文件。成功后，调用 `Refresh` 节点获取所有可用表演 (Take) 的列表，结果是一个 `FMetaHumanTakeInfo` 数组。
4.  **设置输出路径**：使用 `SetTargetPath` 节点指定导入数据在项目中的存放位置。
5.  **处理与监控**：选择需要处理的 Take ID，调用处理相关的节点。在循环中使用 `IsProcessing` 和 `GetTakeProgress` (如果可用) 节点监控进度，并使用 `CancelProcessing` 处理用户中断。

## C++ 用法

**重要提示**：`MetaHumanCaptureSource` 模块及相关类在 UE 5.7 中已被标记为废弃 (Deprecated)，功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。以下示例展示了旧版 API 的用法。

### 头文件引入

```cpp
#include "MetaHumanCaptureSourceSync.h"
```

### 基本用法

（来源：基于 `UMetaHumanCaptureSourceSync` 类接口推断）

```cpp
// 创建一个同步捕获源实例（通常由资产工厂或脚本创建）
UMetaHumanCaptureSourceSync* CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();

// 配置捕获源参数
CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
CaptureSource->StoragePath.Path = TEXT("/Game/MetaHuman/Recordings/Actor01");

// 启动并初始化，获取 Take 信息
CaptureSource->Startup();
TArray<FMetaHumanTakeInfo> Takes = CaptureSource->Refresh();

// 设置导入目标路径
CaptureSource->SetTargetPath(TEXT("/Game/MetaHuman/Imported"), TEXT("/Game/MetaHuman/Takes"));

// 获取单个 Take 的详细信息
FMetaHumanTakeInfo SingleTakeInfo;
bool bSuccess = CaptureSource->GetTakeInfo(Takes[0].Id, SingleTakeInfo);
```

### 进阶用法

结合 `UMetaHumanCaptureSource` 资产和 `UMetaHumanCaptureSourceSync` API 进行更完整的流水线操作，包括处理状态检查和取消。

```cpp
// 假设已经有一个加载的 UMetaHumanCaptureSource 资产
UMetaHumanCaptureSource* SourceAsset = /* ... */;

// 使用资产的参数创建同步包装器（简化示例）
UMetaHumanCaptureSourceSync* SyncWrapper = NewObject<UMetaHumanCaptureSourceSync>();
SyncWrapper->CaptureSourceType = SourceAsset->CaptureSourceType;
SyncWrapper->StoragePath = SourceAsset->StoragePath;
// ... 其他参数映射

SyncWrapper->Startup();

// 获取 Take 列表
TArray<FMetaHumanTakeInfo> AvailableTakes = SyncWrapper->Refresh();

// 选择前两个 Take 进行处理
TArray<int32> TakeIdsToProcess = { AvailableTakes[0].Id, AvailableTakes[1].Id };

// 开始处理（异步）
// SyncWrapper->StartProcessingTakes(TakeIdsToProcess); // 假设有此函数

// 模拟监控循环
while (SyncWrapper->IsProcessing())
{
    // 可以在这里查询每个 Take 的进度
    for (int32 TakeId : TakeIdsToProcess)
    {
        // float Progress = SyncWrapper->GetTakeProgress(TakeId); // 假设有此函数
        // UE_LOG(LogTemp, Log, TEXT("Take %d Progress: %f"), TakeId, Progress);
    }

    // 模拟延迟
    FPlatformProcess::Sleep(0.5f);
}

// 处理完成，获取结果 Take 数据
// TArray<FMetaHumanTake> ImportedTakes = SyncWrapper->GetTakes(TakeIdsToProcess);

// 清理
SyncWrapper->Shutdown();
```

## Demo 示例

一个最小化的、用于从 LiveLink Face 录制文件导入单个 Take 的示例。

**文件: `MetaHumanCaptureDemo.h`**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCaptureSourceSync.h"

class FMetaHumanCaptureDemo
{
public:
    static bool ImportSingleTakeFromArchive(const FString& ArchivePath, const FString& OutputPath);
};
```

**文件: `MetaHumanCaptureDemo.cpp`**
```cpp
#include "MetaHumanCaptureDemo.h"

bool FMetaHumanCaptureDemo::ImportSingleTakeFromArchive(const FString& ArchivePath, const FString& OutputPath)
{
    // 创建同步捕获源
    UMetaHumanCaptureSourceSync* CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();

    // 配置为 LiveLink Face 录制文件模式
    CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
    CaptureSource->StoragePath.Path = ArchivePath;

    // 启动
    CaptureSource->Startup();

    // 刷新以扫描文件
    TArray<FMetaHumanTakeInfo> Takes = CaptureSource->Refresh();
    if (Takes.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("No takes found in archive: %s"), *ArchivePath);
        CaptureSource->Shutdown();
        return false;
    }

    // 设置输出路径
    CaptureSource->SetTargetPath(OutputPath, TEXT("/Game/MetaHuman/Imported"));

    // 获取第一个 Take
    FMetaHumanTakeInfo FirstTake = Takes[0];
    UE_LOG(LogTemp, Log, TEXT("Found take: %s with %d frames"), *FirstTake.Name, FirstTake.NumFrames);

    // 处理该 Take (注意：蓝图中可能需要额外的触发处理节点)
    // 在 C++ 中，`GetTakes` 函数通常用于获取已导入或准备好的 Take 资产。
    // 实际的“导入”或“处理”操作可能需要在蓝图中触发，或通过其他 API 调用。

    // 清理
    CaptureSource->Shutdown();
    return true;
}
```

## 模块依赖

由于该插件包含大量内部模块且依赖关系复杂，以下是使用该插件进行开发时可能需要依赖的特殊模块（不包含标准 Core/Engine 依赖）。

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureSource` | 核心捕获源资产和同步 API。 |
| `MetaHumanIdentity` | 用于创建和管理 MetaHuman 身份资产（基础骨骼网格体）。 |
| `MetaHumanPerformance` | 用于处理表演数据并生成最终动画序列。 |
| `MetaHumanToolkit` | 提供编辑器工具和 UI 以支持整个工作流。 |
| `MetaHumanPipeline` | 底层数据处理管线框架。 |
| `MetaHumanCaptureUtils` | 捕获相关的通用工具函数。 |
| `MetaHumanFaceContourTracker` | 面部特征点追踪算法。 |
| `MetaHumanFaceFittingSolver` | 面部网格体拟合求解器。 |
| `MetaHumanFaceAnimationSolver` | 面部动画参数求解器。 |
| `MetaHumanDepthGenerator` | 从立体图像序列生成深度信息。 |
| `MetaHumanConfig` | 管理 MetaHuman 相关的配置和资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

- **活跃维护**：最近一次更新在2026年5月，频率高且内容涉及功能改进和 bug 修复，表明该插件仍在积极开发和维护中。
- **生命周期注意**：插件核心模块之一 `MetaHumanCaptureSource` 在 UE 5.7 中已被废弃，功能迁移至 `CaptureManager/CaptureManagerDevices`。这预示着插件架构正在演进。对于新项目，建议关注新的 `CaptureManager` 模块。
- **推荐使用**：对于需要创建 MetaHuman 角色的项目，此插件是官方推荐的工具包。尽管部分 API 发生变化，但其核心功能和工具链对于高质量数字人类创作至关重要。建议参照最新官方文档使用，并关注模块的迁移情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)（假设链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests)（路径推断）
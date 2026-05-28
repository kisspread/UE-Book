# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MetaHumanCaptureSource` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-01 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包插件，其核心功能是为 MetaHuman 角色生成高质量的面部动画。它解决了从真实世界捕获的面部表演数据（如 iPhone 的 ARKit 数据或专业的头戴式摄像机 HMC 数据）到 UE 动画序列的自动化转换问题。整个流程包括导入捕获素材、自动追踪面部特征、基于面部网格进行求解适配、以及最终生成驱动 MetaHuman 骨骼网格的动画序列。这个插件是 MetaHuman 虚拟制片和实时动画工作流的基石。

## 使用场景

- 你有一个演员使用 iPhone 上的 LiveLink Face 应用录制了面部表演 → 使用 `LiveLinkFaceConnection` 或 `LiveLinkFaceArchives` 源类型导入数据，并生成 MetaHuman 动画。
- 你的工作室使用专业的头戴式摄像机（HMC）拍摄了面部表演档案 → 使用 `HMCArchives` 源类型进行立体深度重建并导入。
- 你希望从音频文件自动生成面部动画（语音驱动） → 使用 `Speech2Face` 功能（属于 MetaHumanSpeech2Face 模块）。
- 你需要批量处理大量的捕获素材并自动生成动画序列 → 使用 `MetaHumanBatchProcessor` 模块。
- 你需要对已有的 MetaHuman 角色进行高质量的面部追踪和动画适配 → 使用 `MetaHumanPerformance` 资产配合 `FaceAnimationSolver`。

## 蓝图用法

**重要提示**：根据源码，`MetaHumanCaptureSource` 模块下的大部分类型和 API 在 **UE 5.7** 中已被标记为 `UE_DEPRECATED`。它们的功能正在被迁移至 `CaptureManager/CaptureManagerDevices` 模块。以下列出的是该模块 **当前（UE 5.6 及以下）** 提供的蓝图 API，但请注意其废弃状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Startup` | 启动捕获源，连接设备或扫描文件，获取可用 Take 列表。 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新可用 Take 列表。 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置素材导入后的目标文件夹路径（磁盘和内容浏览器）。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 获取指定 Take ID 的详细信息（名称、帧率、分辨率等）。 | `UMetaHumanCaptureSourceSync` |
| `GetTakes` | 获取指定 Take ID 列表对应的完整 Take 数据（包含视频、深度图、音频路径）。 | `UMetaHumanCaptureSourceSync` |
| `Shutdown` | 关闭捕获源连接并清理资源。 | `UMetaHumanCaptureSourceSync` |
| `CanStartup` | 检查当前是否可以启动。 | `UMetaHumanCaptureSourceSync` |
| `IsProcessing` | 检查是否正在处理（导入）素材。 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消对指定 Take 列表的导入处理。 | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

1.  **从设备导入数据**：
    *   创建一个 `MetaHumanCaptureSourceSync` 对象（或使用资产）。
    *   设置其 `CaptureSourceType` 为 `LiveLinkFaceConnection`，并填入设备 IP 地址。
    *   调用 `Startup` 节点。
    *   在 `OnGetTakesFinished` 委托触发后，使用 `GetTakeIds` 和 `GetTakeInfo` 遍历可用 Take。
    *   选择目标 Take，调用 `SetTargetPath` 设置导入路径。
    *   最后，将选中的 Take ID 列表传入 `GetTakes` 节点，即可触发异步导入流程，导入完成后在指定路径生成资产。

2.  **从文件夹批量导入**：
    *   创建 `MetaHumanCaptureSourceSync` 对象。
    *   设置其 `CaptureSourceType` 为 `LiveLinkFaceArchives`，并将 `StoragePath` 设置为包含多个 Take 文件夹的父目录。
    *   调用 `Startup`，即可扫描并列出所有可用的 Take。
    *   后续流程同上。

## C++ 用法

**重要提示**：此模块在 UE 5.7 中已被废弃，新代码应使用 `CaptureManager/CaptureManagerDevices` 模块。以下用法基于模块当前（已废弃）的实现。

### 头文件引入

```cpp
#include "MetaHumanCaptureSource.h"
#include "MetaHumanCaptureSourceSync.h"
```

### 基本用法

以下示例展示了如何通过 `FIngester` 类（`MetaHumanCaptureSource` 模块的核心入口）从 LiveLink Face 存档中异步导入 Take。

```cpp
// 来源：基于 Public/MetaHumanCaptureIngester.h 的接口使用推断

#include "MetaHumanCaptureIngester.h"
#include "MetaHumanTakeData.h"

using namespace UE::MetaHuman;

void ImportFromLiveLinkFaceArchive()
{
    // 1. 准备参数
    FDirectoryPath StoragePath;
    StoragePath.Path = TEXT("/Game/MetaHuman/Captures/LiveLinkFaceData");
    
    FIngesterParams Params(
        EMetaHumanCaptureSourceType::LiveLinkFaceArchives,
        StoragePath,
        FDeviceAddress(), // 对于存档类型，设备地址无效
        0,               // 控制端口
        true,            // 压缩深度文件
        false,           // 复制图像到项目（对于LLF存档通常为false）
        10.0f,           // 最小深度距离
        25.0f,           // 最大深度距离
        EMetaHumanCaptureDepthPrecisionType::Eightieth,
        EMetaHumanCaptureDepthResolutionType::Full
    );

    // 2. 创建 Ingester
    FIngester Ingester(Params);

    // 3. 启动并异步获取Take列表
    Ingester.Startup(ETakeIngestMode::Async);

    // 4. 设置导入目标路径（例如：内容浏览器中的文件夹）
    Ingester.SetTargetPath(
        TEXT("/Game/MetaHuman/Imported"), // 磁盘目标目录
        TEXT("/Game/MetaHuman/Imported")  // 资产目标路径
    );

    // 5. 刷新Take列表
    Ingester.Refresh(FIngester::FRefreshCallback::CreateLambda([](FMetaHumanCaptureVoidResult Result)
    {
        if (Result.bIsValid)
        {
            UE_LOG(LogTemp, Log, TEXT("Take list refreshed successfully."));
        }
    }));

    // 6. 在刷新完成后的某个时刻（例如在轮询或委托中），导入指定的Take
    TArray<TakeId> TakeIdsToImport = {0, 1}; // 假设从刷新结果中获取
    Ingester.GetTakes(TakeIdsToImport, FIngester::FGetTakesCallbackPerTake::CreateLambda(
        [](FMetaHumanCapturePerTakeVoidResult PerTakeResult)
        {
            if (PerTakeResult.Result.bIsValid)
            {
                UE_LOG(LogTemp, Log, TEXT("Take %d imported successfully."), PerTakeResult.TakeId);
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Failed to import Take %d: %s"), PerTakeResult.TakeId, *PerTakeResult.Result.Message);
            }
        }
    ));
}
```

### 进阶用法：连接设备并远程控制录制

此示例展示了如何通过 `FIngester` 连接到 LiveLink Face 设备，并发送命令控制其开始/停止录制。这依赖于 `Commands` 子系统。

```cpp
// 来源：基于 Public/Commands/LiveLinkFaceConnectionCommands.h 和相关API推断

#include "MetaHumanCaptureIngester.h"
#include "Commands/LiveLinkFaceConnectionCommands.h"

using namespace UE::MetaHuman;

void ControlLiveLinkFaceDevice()
{
    // ... 初始化 Ingester，设置类型为 LiveLinkFaceConnection，填写IP和端口 ...
    FIngester Ingester(Params);

    Ingester.Startup();

    // 注册并执行命令
    auto StartCommand = MakeShared<FStartCaptureCommandArgs>(
        TEXT("MySlate"), // 场景板名称
        1,               // Take 编号
        TOptional<FString>(TEXT("ActorSubject")),
        TOptional<FString>(TEXT("ScenarioA")),
        TOptional<TArray<FString>>({TEXT("tag1"), TEXT("tag2")})
    );

    // 发送开始录制命令
    bool bStarted = Ingester.ExecuteCommand(StartCommand);
    if (bStarted)
    {
        UE_LOG(LogTemp, Log, TEXT("Start capture command sent."));
        // ... 一段时间后 ...
        auto StopCommand = MakeShared<FStopCaptureCommandArgs>(true); // 停止并获取Take
        Ingester.ExecuteCommand(StopCommand);
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何使用 `MetaHumanCaptureSourceSync` 类从存档导入 Take。

```cpp
// MetaHumanCaptureExample.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanCaptureSourceSync.h"

class FMetaHumanCaptureExample
{
public:
    void RunExample();
private:
    UPROPERTY()
    TObjectPtr<UMetaHumanCaptureSourceSync> CaptureSource;
};
```

```cpp
// MetaHumanCaptureExample.cpp
#include "MetaHumanCaptureExample.h"
#include "MetaHumanTakeData.h"

void FMetaHumanCaptureExample::RunExample()
{
    // 创建CaptureSource对象（通常在蓝图中通过资产创建，这里用C++ NewObject演示）
    CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();

    // 配置
    CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
    CaptureSource->StoragePath.Path = TEXT("E:/LiveLinkFaceCaptures");
    CaptureSource->CopyImagesToProject = false;

    // 启动并扫描
    CaptureSource->Startup();

    // 获取Take列表
    TArray<FMetaHumanTakeInfo> TakeInfos = CaptureSource->Refresh();
    if (TakeInfos.Num() > 0)
    {
        // 选择第一个Take进行导入
        TArray<TakeId> IdsToIngest = {TakeInfos[0].Id};
        
        // 设置导入目标
        CaptureSource->SetTargetPath(
            TEXT("D:/UEProjects/MetaHumanDemo/Content/Imported"), // 磁盘路径
            TEXT("/Game/Imported") // 内容路径
        );

        // 执行导入
        CaptureSource->GetTakes(IdsToIngest);
        UE_LOG(LogTemp, Log, TEXT("Ingestion started for Take: %s"), *TakeInfos[0].Name);

        // 在实际项目中，这里需要轮询 IsProcessing() 或使用委托来等待完成。
        // 例如：
        while (CaptureSource->IsProcessing())
        {
            FPlatformProcess::Sleep(0.1f);
        }
        UE_LOG(LogTemp, Log, TEXT("Ingestion completed."));
    }

    // 清理
    CaptureSource->Shutdown();
    CaptureSource = nullptr;
}
```

## 模块依赖

由于未提供具体的 `Build.cs` 文件，以下列出根据源码推断的、该插件整体可能依赖的独特模块。对于 `MetaHumanCaptureSource` 子模块，它很可能还依赖 `MediaAssets` 和 `ImageWriteQueue` 以处理视频和图像序列的读写。

| 模块 | 用途 |
|---|---|
| `ControlRig` | 用于驱动 MetaHuman 角色的骨骼网格和面部控制器。 |
| `CameraCalibrationCore` | 处理相机内参和畸变数据，用于深度图和视频的精确对齐。 |
| `LiveLinkInterface` | 提供 Live Link 框架接口，用于与外部设备（如 iPhone 应用）实时通信。 |
| `MediaUtils` | 底层媒体工具，用于读取视频、音频文件（如 MOV, WAV）。 |
| `AnimationCore` | 提供核心动画数据结构和工具。 |
| `RigLogicModule` | （可能）用于 MetaHuman 面部木偶系统的底层逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染伪影。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman动画师] 为已有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题。 |

### 维护评价

**综合评价：功能活跃但模块已废弃，建议关注新方案。**

*   **年龄**：插件整体约 3 年（🆕），属于较新的 Epic 官方工具。
*   **近期更新**：非常活跃，最近几天仍有针对渲染、导出、Sequencer 的 Bug 修复和功能调整。
*   **维护状态**：**积极维护中**。提交信息表明 Epic 团队仍在持续改进这个工作流，尤其是身体动画（Body Tracking）方面。
*   **已知问题/限制**：
    1.  **核心模块废弃**：`MetaHumanCaptureSource` 及其相关 API 在 UE 5.7 中被标记为废弃，功能正迁移至 `CaptureManager/CaptureManagerDevices`。这意味着当前文档中描述的捕获源工作流在未来版本中将不可用。
    2.  **功能庞大**：插件包含超过 20 个子模块，涵盖从数据导入到动画生成的完整管线，学习曲线较陡。
*   **推荐使用**：
    *   对于 **UE 5.6 或更早版本** 的项目，且需要导入 LiveLink Face 或 HMC 数据来驱动 MetaHuman，此插件是**官方且唯一**的选择，推荐使用。
    *   对于 **UE 5.7 及更高版本** 的新项目，应查阅官方文档，了解 `CaptureManagerDevices` 模块的最新用法，并计划迁移。不建议在新项目中继续使用已废弃的 `MetaHumanCaptureSource` 模块 API。

**⚠️ 警告**：虽然插件整体仍在更新，但 `MetaHumanCaptureSource` 子模块已是废弃状态。任何基于该模块的蓝图或 C++ 代码都可能在未来引擎版本中失效。请密切关注 Epic 官方关于迁移路径的公告。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-unreal-engine-guide/) （MetaHuman Animator 整体指南，可能包含此模块相关内容）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)
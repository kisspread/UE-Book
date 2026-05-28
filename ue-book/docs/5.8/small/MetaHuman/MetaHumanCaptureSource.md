# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCaptureSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 面部动画制作工具套件，用于将真实演员的面部表演数据转化为 MetaHuman 角色的动画序列。它解决了从面部捕捉到最终动画输出的完整工作流问题：

1. **面部捕获源管理**：支持从 LiveLink Face 应用、HMC（头戴式相机）档案、立体重建系统等多种设备/来源导入面部表演数据
2. **面部特征追踪**：自动追踪演员面部的轮廓和关键点
3. **面部拟合求解**：将追踪到的面部数据拟合到 MetaHuman 骨骼网格体上
4. **面部动画求解**：从面部特征生成最终的动画数据
5. **深度图生成**：从立体视频生成深度信息，提升追踪精度
6. **语音驱动面部**：从音频输入生成面部动画（Speech2Face）
7. **批量处理**：支持批量处理多个表演数据

**重要提示**：从 UE 5.7 开始，`MetaHumanCaptureSource` 模块已被标记为废弃（Deprecated），其功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。新项目应优先使用新模块。

## 使用场景

- 你使用 iPhone 上的 LiveLink Face 应用录制了演员的面部表演 → 用 MetaHuman Animator 将录制数据导入并生成 MetaHuman 动画
- 你使用专业 HMC（头戴式相机）设备拍摄了面部表演 → 用 MetaHuman Animator 处理立体视频并生成深度数据和动画
- 你有一批面部表演素材需要批量处理 → 用 MetaHumanBatchProcessor 自动化处理
- 你需要从音频生成面部动画 → 用 MetaHumanSpeech2Face
- 你需要将面部追踪数据拟合到自定义的 MetaHuman 模型 → 用 MetaHumanFaceFittingSolver

## 蓝图用法

> ⚠️ 以下 API 所在的 `MetaHumanCaptureSource` 模块自 UE 5.7 起已废弃，新项目应使用 `CaptureManager/CaptureManagerDevices` 模块。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanStartup` | 检查是否可以启动捕获源连接 | `UMetaHumanCaptureSourceSync` |
| `Startup` | 启动捕获源，获取可用 Take 信息 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新可用 Take 列表，返回 `TArray<FMetaHumanTakeInfo>` | `UMetaHumanCaptureSourceSync` |
| `Shutdown` | 关闭捕获源连接 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置导入目标目录和资产路径 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 获取指定 Take 的详细信息 | `UMetaHumanCaptureSourceSync` |
| `GetTakes` | 获取指定 Take 的媒体数据（视频、深度、音频） | `UMetaHumanCaptureSourceSync` |
| `GetNumTakes` | 获取可用 Take 数量 | `UMetaHumanCaptureSourceSync` |
| `GetTakeIds` | 获取所有 Take ID 列表 | `UMetaHumanCaptureSourceSync` |
| `CanIngestTakes` | 检查是否可以导入 Take 数据 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消正在进行的 Take 处理 | `UMetaHumanCaptureSourceSync` |
| `IsProcessing` | 检查是否正在处理中 | `UMetaHumanCaptureSourceSync` |
| `IsCancelling` | 检查是否正在取消中 | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

**从 LiveLink Face 档案导入 Take：**

1. 创建一个 `MetaHumanCaptureSourceSync` 资产，设置 `CaptureSourceType` 为 `LiveLinkFaceArchives`
2. 设置 `StoragePath` 指向包含 LiveLink Face 录制数据的目录
3. 调用 `Startup` → 连接到数据源
4. 调用 `Refresh` → 获取可用 Take 列表（返回 `TArray<FMetaHumanTakeInfo>`）
5. 调用 `SetTargetPath` → 设置项目内导入目标路径
6. 调用 `GetTakes` → 导入选中的 Take，回调中获取包含视频序列、深度序列、音频的 `FMetaHumanTake` 数据

**从 LiveLink Face 设备实时连接：**

1. 创建 `MetaHumanCaptureSourceSync` 资产，设置 `CaptureSourceType` 为 `LiveLinkFaceConnection`
2. 设置 `DeviceIpAddress` 为 iPhone 的 IP 地址
3. 设置 `DeviceControlPort`（默认 14785）
4. 调用 `Startup` → 建立与设备的控制连接
5. 调用 `Refresh` → 获取设备上可用的 Take 列表
6. 选择 Take 后调用 `GetTakes` → 从设备导出并导入数据

**数据结构说明：**

- `FMetaHumanTakeInfo`：Take 的元数据信息，包含名称、帧数、帧率、分辨率、日期等
- `FMetaHumanTakeView`：单个视角的视频和深度数据（`UImgMediaSource` 类型）
- `FMetaHumanTake`：完整的 Take 数据，包含多个视角、相机标定、音频和时间码信息

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCaptureSource.h"
#include "MetaHumanCaptureSourceSync.h"
#include "MetaHumanCaptureIngester.h"
#include "MetaHumanTakeData.h"
```

### 基本用法

> ⚠️ 以下代码展示了已废弃 API 的使用方式，仅作参考。新项目应使用 `CaptureManager/CaptureManagerDevices` 模块。

**创建和配置捕获源：**

```cpp
// 来源: MetaHumanCaptureSource/Public/MetaHumanCaptureSource.h
// 创建一个同步式捕获源对象
UMetaHumanCaptureSourceSync* CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();

// 配置为 LiveLink Face 档案模式
CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
CaptureSource->StoragePath.Path = TEXT("/Path/To/LiveLinkFace/Recordings");

// 启动并获取 Take 列表
CaptureSource->Startup();
TArray<FMetaHumanTakeInfo> Takes = CaptureSource->Refresh();

// 遍历可用的 Take
for (const FMetaHumanTakeInfo& TakeInfo : Takes)
{
    UE_LOG(LogTemp, Log, TEXT("Take: %s, Frames: %d, Rate: %.2f"),
        *TakeInfo.Name, TakeInfo.NumFrames, TakeInfo.FrameRate);
}

// 设置导入目标路径
CaptureSource->SetTargetPath(
    TEXT("/Game/MetaHuman/Captures"),
    TEXT("/Game/MetaHuman/Captures")
);
```

**导入 Take 数据：**

```cpp
// 来源: MetaHumanCaptureSource/Public/MetaHumanCaptureSourceSync.h
// 选择要导入的 Take
TArray<int32> TakeIds = CaptureSource->GetTakeIds();

// 获取 Take 数据（视频序列、深度序列、音频）
TArray<FMetaHumanTake> ImportedTakes = CaptureSource->GetTakes(TakeIds);

for (const FMetaHumanTake& Take : ImportedTakes)
{
    // 遍历视角
    for (const FMetaHumanTakeView& View : Take.Views)
    {
        UImgMediaSource* VideoSource = View.Video;   // 视频图像序列
        UImgMediaSource* DepthSource = View.Depth;   // 深度图像序列
        
        if (View.bVideoTimecodePresent)
        {
            FTimecode TC = View.VideoTimecode;
            FFrameRate Rate = View.VideoTimecodeRate;
        }
    }
    
    // 获取相机标定数据
    UCameraCalibration* Calibration = Take.CameraCalibration;
    
    // 获取音频数据
    USoundWave* Audio = Take.Audio;
}
```

### 进阶用法

**使用 FIngester 进行底层捕获控制：**

```cpp
// 来源: MetaHumanCaptureSource/Public/MetaHumanCaptureIngester.h
#include "MetaHumanCaptureIngester.h"

// 创建 Ingester 参数
UE::MetaHuman::FIngesterParams Params(
    EMetaHumanCaptureSourceType::HMCArchives,  // HMC 立体档案
    FDirectoryPath{ TEXT("/Path/To/HMC/Data") },
    FDeviceAddress{},                           // 档案模式无需设备地址
    0,                                          // 无端口
    true,                                       // 压缩深度文件
    true,                                       // 复制图像到项目
    10.0f,                                      // 最小深度距离 (cm)
    25.0f,                                      // 最大深度距离 (cm)
    EMetaHumanCaptureDepthPrecisionType::Eightieth,
    EMetaHumanCaptureDepthResolutionType::Full
);

// 创建 Ingester
UE::MetaHuman::FIngester Ingester(Params);

// 启动异步模式
Ingester.Startup(ETakeIngestMode::Async);

// 获取 Take 数量
int32 NumTakes = Ingester.GetNumTakes();
TArray<TakeId> Ids = Ingester.GetTakeIds();

// 获取 Take 信息
FMetaHumanTakeInfo Info;
if (Ingester.GetTakeInfo(Ids[0], Info))
{
    UE_LOG(LogTemp, Log, TEXT("Take: %s, Duration: %.2fs"),
        *Info.Name, Info.NumFrames / Info.FrameRate);
}
```

**使用 FBaseCommandArgs 控制实时连接录制：**

```cpp
// 来源: MetaHumanCaptureSource/Public/Commands/LiveLinkFaceConnectionCommands.h
// 开始录制
auto StartArgs = MakeShared<FStartCaptureCommandArgs>(
    TEXT("SlateName"),       // Slate 名称
    1,                        // Take 编号
    TOptional<FString>(TEXT("Subject")),  // 主题（可选）
    TOptional<FString>(),    // 场景（可选）
    TOptional<TArray<FString>>(TArray<FString>{ TEXT("tag1"), TEXT("tag2") })  // 标签（可选）
);
Ingester.ExecuteCommand(StartArgs);

// 停止录制并获取 Take
auto StopArgs = MakeShared<FStopCaptureCommandArgs>(true);  // true = 获取 Take
Ingester.ExecuteCommand(StopArgs);
```

## Demo 示例

> 以下示例展示如何使用已废弃的 `UMetaHumanCaptureSourceSync` API 从 LiveLink Face 档案导入面部表演数据。新项目应使用 `CaptureManager/CaptureManagerDevices` 模块。

### MetaHumanCaptureImporter.h

```cpp
// MetaHumanCaptureImporter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanCaptureImporter.generated.h"

class UMetaHumanCaptureSourceSync;
struct FMetaHumanTakeInfo;
struct FMetaHumanTake;

UCLASS(BlueprintType)
class AMetaHumanCaptureImporter : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanCaptureImporter();

    UPROPERTY(EditAnywhere, Category = "Capture")
    FString LiveLinkFaceDirectory;

    UPROPERTY(EditAnywhere, Category = "Capture")
    FString TargetAssetPath;

    UFUNCTION(BlueprintCallable, Category = "Capture")
    bool ImportCaptures();

    UFUNCTION(BlueprintCallable, Category = "Capture")
    int32 GetAvailableTakeCount() const;

protected:
    virtual void BeginDestroy() override;

private:
    UPROPERTY(Transient)
    TObjectPtr<UMetaHumanCaptureSourceSync> CaptureSource;

    TArray<FMetaHumanTakeInfo> CachedTakeInfos;
};
```

### MetaHumanCaptureImporter.cpp

```cpp
// MetaHumanCaptureImporter.cpp
#include "MetaHumanCaptureImporter.h"
#include "MetaHumanCaptureSourceSync.h"
#include "MetaHumanTakeData.h"

AMetaHumanCaptureImporter::AMetaHumanCaptureImporter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanCaptureImporter::BeginDestroy()
{
    if (CaptureSource)
    {
        CaptureSource->Shutdown();
        CaptureSource = nullptr;
    }
    Super::BeginDestroy();
}

bool AMetaHumanCaptureImporter::ImportCaptures()
{
    // 创建同步式捕获源
    CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();
    CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
    CaptureSource->StoragePath.Path = LiveLinkFaceDirectory;

    // 启动并检查是否就绪
    if (!CaptureSource->CanStartup())
    {
        UE_LOG(LogTemp, Error, TEXT("Capture source cannot startup"));
        return false;
    }

    CaptureSource->Startup();

    // 刷新 Take 列表
    TArray<FMetaHumanTakeInfo> Takes = CaptureSource->Refresh();
    if (Takes.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No takes found in: %s"), *LiveLinkFaceDirectory);
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("Found %d takes"), Takes.Num());
    CachedTakeInfos = Takes;

    // 设置导入目标
    CaptureSource->SetTargetPath(TargetAssetPath, TargetAssetPath);

    // 获取所有 Take
    TArray<int32> TakeIds;
    for (const FMetaHumanTakeInfo& Info : Takes)
    {
        TakeIds.Add(Info.Id);
    }

    if (!CaptureSource->CanIngestTakes())
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot ingest takes"));
        return false;
    }

    TArray<FMetaHumanTake> ImportedTakes = CaptureSource->GetTakes(TakeIds);

    for (const FMetaHumanTake& Take : ImportedTakes)
    {
        UE_LOG(LogTemp, Log, TEXT("Imported Take ID: %d, Views: %d"),
            Take.TakeId, Take.Views.Num());
    }

    // 完成后关闭
    CaptureSource->Shutdown();

    UE_LOG(LogTemp, Log, TEXT("Import complete: %d takes"), ImportedTakes.Num());
    return true;
}

int32 AMetaHumanCaptureImporter::GetAvailableTakeCount() const
{
    return CachedTakeInfos.Num();
}
```

## 模块依赖

以下列出该插件各模块的**独特**依赖关系（已省略 Core/Engine/Slate 等常见模块）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供底层面部追踪和拟合算法 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器功能 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具，用于 MetaHuman Identity 的网格体处理 |
| `ControlRigDeveloper` | ControlRig 开发者模块，用于面部动画控制绑定 |
| `MeshTrackerInterface` | 网格追踪器接口，用于面部网格追踪 |
| `MetaHumanCaptureProtocolStack` | 捕获协议栈，用于与 LiveLink Face 设备通信 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器，用于预览捕获的面部图像 |
| `MetaHumanPipeline` | 管道系统，用于处理 Take 数据的流水线 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **创建时间**：2022 年初，约 4 年历史
- **活跃程度**：**活跃维护中**。2026 年 5 月仍有频繁的功能更新和 bug 修复，最近的提交集中在身体追踪集成、渲染修复和动画导出改进
- **废弃状态**：`MetaHumanCaptureSource` 模块自 UE 5.7 起已废弃，功能迁移至 `CaptureManager/CaptureManagerDevices` 模块。这是 Epic 对捕获管理架构进行重构的一部分
- **整体评价**：MetaHuman Animator 是 Epic 官方维护的核心面部动画工具，持续活跃更新。主模块整体仍在积极开发中，但捕获源子模块已迁移。**建议新项目使用 `CaptureManager/CaptureManagerDevices` 模块替代 `MetaHumanCaptureSource`**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-unreal-engine-documentation/)
# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元人动画工具包 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

基于源码分析，**MetaHuman Animator** 是一个用于处理 MetaHuman 面部动画制作全流程的官方工具包。它主要解决以下核心问题：
1.  **捕获数据源管理**：通过 `MetaHumanCaptureSource` 模块定义资产，用于代表物理捕获设备（如 LiveLink Face 应用）或本地存档。这些资产是 MetaHuman 动画工作流的起点，负责管理视频、深度和音频等原始数据。
2.  **数据摄取与处理**：包含一个完整的 **Footage Ingest（素材摄取）** 管道，能够从不同来源（LiveLink Face 网络连接、LiveLink Face 本地存档、立体 HMC 设备存档等）导入原始拍摄数据，并将其转换为 Unreal Engine 可使用的资产（如图像序列、音频波形、相机标定数据）。
3.  **驱动 MetaHuman 表演**：结合 `MetaHumanIdentity` 工具生成的骨骼网格体，用于 `MetaHumanPerformance` 资产，通过自动跟踪演员在表演中的面部特征来生成动画序列。

**重要提示**：从源码中的大量 `UE_DEPRECATED` 宏标记可知，**此插件（特别是 `MetaHumanCaptureSource` 模块）在 5.7 版本已被官方标记为废弃**。其功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。本文档主要描述其历史架构和废弃前的用法。

## 使用场景

- **影视级数字人动画制作**：你正在使用 MetaHuman 框架制作电影或高质量数字人内容，需要从专业捕捉设备（如 Technoprops HMC）导入面部表演数据。
- **实时/准实时面部动捕工作流**：你使用 iPhone 的 LiveLink Face 应用进行面部捕捉，希望将捕捉结果直接导入到 Unreal Engine 中驱动 MetaHuman 角色。
- **批量处理捕捉数据**：你需要处理大量已录制的捕捉会话（Takes），并自动将其转换为引擎资产以供后续动画制作使用。

## 蓝图用法

`MetaHumanCaptureSource` 模块提供了用于管理捕获会话的蓝图 API，主要通过 `UMetaHumanCaptureSourceSync` 类暴露功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Startup` | 初始化捕获源，获取可用拍摄列表。这是开始使用的入口。 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新并重新获取当前捕获源下的可用拍摄列表。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 根据拍摄 ID 获取单个拍摄的详细信息。 | `UMetaHumanCaptureSourceSync` |
| `GetTakes` | 根据 ID 列表获取多个拍摄的完整数据（包括视图、音频等）。 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置摄取素材在引擎内容浏览器中的目标存储路径。 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消正在进行的素材摄取操作。 | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

1.  **创建捕获源资产**：在内容浏览器中右键，选择“创建” > “MetaHuman” > “Capture Source”或“Capture Source Sync”。根据实际设备类型（如“LiveLink Face Connection”）设置资产属性。
2.  **初始化并获取拍摄列表**：
    - 拖出一个 `Create Capture Source Sync` 节点（或直接引用创建好的资产）。
    - 连接 `Startup` 节点。
    - 连接 `Refresh` 节点，获取可用拍摄列表。
    - 使用 `Get Take Info` 节点查看每个拍摄的详细信息（如名称、帧数、分辨率）。
3.  **摄取特定拍摄**：
    - 通过 `Get Takes` 节点获取想要摄取的拍摄数据。
    - 系统会自动开始处理视频、深度数据转换，并创建对应的 `UImgMediaSource`、`USoundWave` 和 `UCameraCalibration` 资产。
    - 可以通过 `Set Target Path` 控制这些资产的存放位置。

## C++ 用法

由于该模块主要服务于蓝图和编辑器内部流程，C++ 直接调用相对较少，但核心类如 `FIngester` 提供了编程接口。

### 头文件引入

```cpp
#include “MetaHumanCaptureSource/MetaHumanCaptureIngester.h”
```

### 基本用法

以下示例展示了如何通过 C++ 使用 `FIngester` 来初始化一个连接模式的捕获源。
*(来源：根据 `UMetaHumanCaptureSourceSync` 和 `FIngester` 的公开接口推断)*

```cpp
#include “MetaHumanCaptureSource/MetaHumanCaptureIngester.h”

// 创建摄取参数（使用已废弃的枚举，仅作示例）
EMetaHumanCaptureSourceType SourceType = EMetaHumanCaptureSourceType::LiveLinkFaceConnection;
FDirectoryPath StoragePath;
StoragePath.Path = TEXT(“/Game/Captures/Raw”);
FDeviceAddress DeviceAddress;
DeviceAddress.IpAddress = TEXT(“192.168.1.100”);

// 构造参数
UE::MetaHuman::FIngesterParams IngesterParams(
    SourceType,
    StoragePath,
    DeviceAddress,
    14785, // 控制端口
    true,  // 压缩深度文件
    false, // 复制图像到项目
    10.0f, // 最小深度距离
    25.0f, // 最大深度距离
    EMetaHumanCaptureDepthPrecisionType::Eightieth,
    EMetaHumanCaptureDepthResolutionType::Full
);

// 创建摄取器实例
PRAGMA_DISABLE_DEPRECATION_WARNINGS
UE::MetaHuman::FIngester Ingester(IngesterParams);
PRAGMA_ENABLE_DEPRECATION_WARNINGS

// 启动摄取器（异步模式）
Ingester.Startup(ETakeIngestMode::Async);

// 刷新拍摄列表
Ingester.Refresh(UE::MetaHuman::FIngester::FRefreshCallback::CreateLambda(
    [](FMetaHumanCaptureVoidResult Result)
    {
        if (Result.bIsValid)
        {
            UE_LOG(LogTemp, Log, TEXT(“Refresh successful. Takes available.”));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT(“Refresh failed: %s”), *Result.Message);
        }
    }
));

// ... 后续可通过 Ingester.GetNumTakes() 等方法操作
```

## Demo 示例

一个最小化的示例，演示如何创建和配置 `UMetaHumanCaptureSource` 资产。
*(注意：该资产类型本身是纯数据资产，其实际操作通常通过蓝图的 `UMetaHumanCaptureSourceSync` 或编辑器UI完成)*

### MetaHumanCaptureSourceDemo.h

```cpp
#pragma once

#include “CoreMinimal.h”
#include “UObject/NoExportTypes.h”
#include “MetaHumanCaptureSource/MetaHumanCaptureSource.h” // 包含已废弃的类型
#include “MetaHumanCaptureSourceDemo.generated.h”

UCLASS(BlueprintType)
class UMetaHumanCaptureSourceDemo : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = “MetaHuman|Demo”)
    void CreateDemoCaptureSource();

    UPROPERTY()
    TObjectPtr<UMetaHumanCaptureSource> CreatedSource;
};
```

### MetaHumanCaptureSourceDemo.cpp

```cpp
#include “MetaHumanCaptureSourceDemo.h”
#include “UObject/SavePackage.h”

void UMetaHumanCaptureSourceDemo::CreateDemoCaptureSource()
{
    // 确保我们有编辑器环境
    if (!GIsEditor) return;

    // 定义资产路径
    FString PackagePath = TEXT(“/Game/Demo/”);
    FString AssetName = TEXT(“Demo_LiveLinkFace_Source”);
    FString FullPackagePath = PackagePath + AssetName;

    // 检查资产是否已存在
    UPackage* Package = CreatePackage(*FullPackagePath);
    UMetaHumanCaptureSource* ExistingAsset = FindObject<UMetaHumanCaptureSource>(Package, *AssetName);

    if (ExistingAsset)
    {
        CreatedSource = ExistingAsset;
        UE_LOG(LogTemp, Warning, TEXT(“Capture source asset already exists at %s”), *FullPackagePath);
        return;
    }

    // 创建新资产
    PRAGMA_DISABLE_DEPRECATION_WARNINGS
    CreatedSource = NewObject<UMetaHumanCaptureSource>(Package, *AssetName, RF_Public | RF_Standalone);
    PRAGMA_ENABLE_DEPRECATION_WARNINGS

    if (CreatedSource)
    {
        // 配置资产（示例为连接模式）
        CreatedSource->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceConnection;
        CreatedSource->DeviceIpAddress.IpAddress = TEXT(“192.168.1.100”);
        CreatedSource->DeviceControlPort = 14785;

        // 标记资产为脏并保存
        Package->MarkPackageDirty();
        FSavePackageArgs SaveArgs;
        SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
        UPackage::SavePackage(Package, CreatedSource, *FPaths::ConvertRelativePathToFull(FullPackagePath + TEXT(“.uasset”)), SaveArgs);

        UE_LOG(LogTemp, Log, TEXT(“Successfully created capture source asset at: %s”), *FullPackagePath);
    }
}
```

## 模块依赖

`MetaHumanCaptureSource` 模块依赖以下独特模块（常见依赖如Core, CoreUObject, Engine, Slate等已省略）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，提供基础数据类型和工具 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体实用工具，用于处理与捕获相关的网格体数据 |
| `ControlRigDeveloper` | Control Rig 开发者工具，用于与动画控制逻辑集成 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器，提供编辑器内查看和处理捕获数据的功能 |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器部分，提供编辑器集成接口 |
| `MeshTrackerInterface` | 网格体追踪器接口，用于深度或网格体追踪功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 启用身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复定序器缓存问题 |

### 维护评价

**维护状态：维护中，但关键模块已废弃。**

1.  **活跃度**：近期（2026年5月）仍有持续的更新提交，表明整个 MetaHuman 工具链仍在积极开发和维护中。
2.  **废弃警告**：**最核心的 `MetaHumanCaptureSource` 模块在源码中被明确标记为废弃（Deprecated 5.7）**。这意味着官方已不再推荐使用此模块，其功能已被迁移至新的 `CaptureManager/CaptureManagerDevices` 模块。
3.  **建议**：
    - 对于**新项目**，应避免使用 `MetaHumanCaptureSource` 模块，转而使用 Epic 最新的 `CaptureManager` 解决方案。
    - 对于**已有项目**，如果依赖此模块，应关注官方迁移指南，并规划向新模块的过渡。近期的提交主要是 bug 修复和功能微调，表明 Epic 仍在为其用户提供基本的支持，但新功能开发很可能已转向新架构。
    - 整个 `MetaHumanAnimator` 插件的其他子模块（如 Identity, Performance）似乎仍在使用和更新中。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/en-US/animation-and-characters/meta-humans/) (注意：此链接为 MetaHuman 整体文档，非此废弃模块的专属文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (模块名暗示了测试，但路径需确认)
# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置等） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

**当前文档模块**: MetaHumanCaptureSource

## 用途

MetaHuman Capture Source 模块是 MetaHuman Animator 工具包中的核心数据输入模块。其主要功能是将来自各种外部设备（如 iPhone 的 LiveLink Face 应用、立体头戴式摄像机系统 HMC）录制的面部表演视频素材（Footage），导入到 Unreal Engine 中，为后续的面部跟踪、拟合和动画生成流程提供原始数据。它充当了外部捕获设备与 UE 内部 MetaHuman 动画工作流之间的桥梁，负责处理设备连接、视频/深度流解码、元数据解析以及资产创建等关键任务。

**注意**：此模块在 UE 5.7 中已被标记为废弃，其功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。

## 使用场景

*   你使用 iPhone 上的 LiveLink Face 应用录制了演员的面部表情表演，并希望将其导入 UE 以驱动 MetaHuman 角色动画。
*   你使用专业的立体 HMC（头戴式摄像机）设备拍摄了面部表演，需要将带有深度信息的视频序列导入 UE 进行高保真面部重建。
*   你有一组已录制好的 LiveLink Face 或 HMC 格式的视频档案文件，希望批量导入到 UE 项目中。
*   你需要通过编程方式（C++ 或蓝图）自动控制捕获设备的连接、开始/停止录制以及数据导入流程。

## 蓝图用法

本模块的核心蓝图 API 集中在 `UMetaHumanCaptureSourceSync` 类中，用于同步地控制捕获源的整个生命周期。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Startup` | 初始化捕获源，连接到设备或读取文件列表。 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新可用 Take（录制片段）列表。 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置数据导入后存储到项目内的目标路径。 | `UMetaHumanCaptureSourceSync` |
| `Shutdown` | 关闭捕获源连接。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeIds` | 获取所有可用 Take 的 ID 列表。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 根据 Take ID 获取其详细信息（如分辨率、帧率）。 | `UMetaHumanCaptureSourceSync` |
| `GetTakes` | 异步获取指定 Take 的数据并创建 UE 资产。 | `UMetaHumanCaptureSourceSync` |
| `IsProcessing` | 检查是否有 Take 正在被处理/导入。 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消指定 Take 的处理流程。 | `UMetaHumanCaptureSourceSync` |
| `CanStartup` / `CanIngestTakes` / `CanCancel` | 查询当前状态是否允许执行特定操作。 | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

1.  **创建资产并初始化**：首先，在内容浏览器中右键创建 `MetaHumanCaptureSourceSync` 资产。在蓝图中获取此资产引用。
2.  **设置捕获源**：根据你的设备类型（如 `LiveLinkFaceArchives`），设置 `CaptureSourceType` 属性。如果使用存档，还需设置 `StoragePath` 指向文件夹。
3.  **连接与刷新**：调用 `Startup` 节点进行连接。随后调用 `Refresh` 节点以填充可用 Take 列表。
4.  **查询与选择**：使用 `GetTakeIds` 和 `GetTakeInfo` 循环列出或展示可用的 Take。
5.  **导入数据**：选定目标 Take 后，调用 `SetTargetPath` 指定项目内的存储位置，然后调用 `GetTakes` 并传入 Take ID 数组以开始导入。导入过程是异步的，可以通过 `IsProcessing` 节点查询进度。
6.  **清理**：完成后，调用 `Shutdown` 断开连接。

## C++ 用法

在 C++ 中，主要通过操作 `UMetaHumanCaptureSourceSync` 类来完成捕获数据导入。

### 头文件引入

```cpp
#include "MetaHumanCaptureSource/Public/MetaHumanCaptureSourceSync.h"
#include "MetaHumanCaptureSource/Public/MetaHumanTakeData.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建一个同步捕获源并执行基本的导入流程。

```cpp
// 创建一个 MetaHumanCaptureSourceSync 对象
UMetaHumanCaptureSourceSync* CaptureSourceSync = NewObject<UMetaHumanCaptureSourceSync>();

// 配置捕获源类型和路径（以读取 LiveLink Face 存档为例）
CaptureSourceSync->CaptureSourceType = EMetaHumanCaptureSourceType::LiveLinkFaceArchives;
CaptureSourceSync->StoragePath.Path = TEXT("/Path/To/Your/Captures");

// 初始化
if (CaptureSourceSync->CanStartup())
{
    CaptureSourceSync->Startup();
}

// 刷新可用 Take 列表
if (CaptureSourceSync->CanIngestTakes())
{
    TArray<FMetaHumanTakeInfo> Takes = CaptureSourceSync->Refresh();
    // ... 处理 Take 信息 ...
}

// 设置导入目标路径
FString ProjectContentDir = FPaths::ProjectContentDir();
FString TargetFolderAssetPath = TEXT("/Game/MetaHuman/ImportedTakes");
CaptureSourceSync->SetTargetPath(ProjectContentDir, TargetFolderAssetPath);

// 导入第一个 Take
TArray<int32> TakeIdsToIngest = { 0 }; // 假设 ID 为 0
if (!CaptureSourceSync->GetTakes(TakeIdsToIngest).IsEmpty())
{
    // 导入已在后台启动
}

// ... 在后续的 Tick 或通过委托检查 IsProcessing 状态 ...

// 完成后关闭
CaptureSourceSync->Shutdown();
```

### 进阶用法

处理异步操作和错误。`GetTakes` 是异步的，可以通过轮询 `IsProcessing` 来等待完成，或（在更高级的场景中）监听内部委托。

```cpp
// 轮询等待导入完成
while (CaptureSourceSync->IsProcessing())
{
    // 可以在这里更新 UI 进度条
    FPlatformProcess::Sleep(0.1f); // 避免忙等待
}

UE_LOG(LogTemp, Log, TEXT("Take import finished."));

// 检查可能的错误需要深入查看内部逻辑，因为公有 API 未直接暴露详细错误。
// 通常依赖编辑器内出现的导入警告或资产完整性。
```

## Demo 示例

一个最小的 C++ 示例，展示如何集成 MetaHumanCaptureSource 模块。

```cpp
// MetaHumanCaptureDemo.h
#pragma once
#include "CoreMinimal.h"

class UMetaHumanCaptureSourceSync;
class FMetaHumanTakeInfo;

class FMetaHumanCaptureDemo
{
public:
    FMetaHumanCaptureDemo();
    ~FMetaHumanCaptureDemo();

    void RunDemo();

private:
    UPROPERTY(Transient) // 注意：在非 UObject 类中使用需要特殊处理生命周期
    TObjectPtr<UMetaHumanCaptureSourceSync> CaptureSource;
};
```

```cpp
// MetaHumanCaptureDemo.cpp
#include "MetaHumanCaptureDemo.h"
#include "MetaHumanCaptureSource/Public/MetaHumanCaptureSourceSync.h"
#include "MetaHumanCaptureSource/Public/MetaHumanTakeData.h"

FMetaHumanCaptureDemo::FMetaHumanCaptureDemo()
{
    CaptureSource = NewObject<UMetaHumanCaptureSourceSync>();
}

FMetaHumanCaptureDemo::~FMetaHumanCaptureDemo()
{
    if (CaptureSource)
    {
        CaptureSource->Shutdown();
    }
}

void FMetaHumanCaptureDemo::RunDemo()
{
    if (!CaptureSource || !CaptureSource->CanStartup())
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot start capture source."));
        return;
    }

    // 配置为读取 HMC 存档
    CaptureSource->CaptureSourceType = EMetaHumanCaptureSourceType::HMCArchives;
    CaptureSource->StoragePath.Path = TEXT("C:/DemoCaptures/HMC");
    CaptureSource->CopyImagesToProject = true;

    // 启动
    CaptureSource->Startup();
    UE_LOG(LogTemp, Log, TEXT("Capture source started."));

    // 刷新并获取 Take 列表
    TArray<FMetaHumanTakeInfo> AvailableTakes = CaptureSource->Refresh();
    if (AvailableTakes.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("No takes found."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Found %d takes."), AvailableTakes.Num());

    // 设置导入目标
    FString ContentDir = FPaths::ConvertRelativePathToFull(FPaths::ProjectContentDir());
    CaptureSource->SetTargetPath(ContentDir, TEXT("/Game/DemoImportedTakes"));

    // 导入第一个 Take
    TArray<int32> Targets = { AvailableTakes[0].Id };
    CaptureSource->GetTakes(Targets);

    UE_LOG(LogTemp, Log, TEXT("Import initiated for Take ID: %d"), AvailableTakes[0].Id);

    // 实际应用中，需要通过游戏循环或委托等待导入完成
    // 此处仅为演示流程
}
```

## 模块依赖

本模块 (`MetaHumanCaptureSource`) 无特殊依赖，仅需标准的 Core/Engine/Slate 等模块。使用者的项目模块通常无需显式依赖此模块，因为其主要通过资产和蓝图节点进行交互。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体跟踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体跟踪时过滤掉可视化的对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复定序器缓存问题。 |

### 维护评价

**⚠️ 已废弃模块**

`MetaHumanCaptureSource` 模块已在 UE 5.7 中被明确标记为废弃（`Deprecated`）。其功能正在被迁移至 `CaptureManager/CaptureManagerDevices` 模块。虽然源码中仍有近期提交（2026年5月），但这些更新主要围绕整体 MetaHuman Animator 插件的修复和改进，并非针对此废弃模块的新功能开发。

**建议**：对于新的项目开发，**强烈建议**避免使用此模块的 API，并等待或直接使用 `CaptureManager` 模块作为替代。现有的使用此模块的项目应计划在合适时机进行迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureSource)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (UE通用文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests) (整个插件的测试目录)
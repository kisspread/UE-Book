# Capture Manager Editor

> The Capture Manager Editor plugin is used for importing the Capture archive data into UE/UEFN to create necessary assets

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置等） |
| 模块 | `CaptureManagerDeviceBlueprint` (Runtime), `CaptureManagerEditorSettings` (Runtime), `CaptureManagerIngestBlueprint` (Runtime), `DataIngestCoreEditor` (Runtime), `LiveLinkHubDiscoveryEditor` (Runtime), `LiveLinkHubExportServer` (Runtime), `LiveLinkHubWorkerManager` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor) | |

## 用途

该插件是一个**综合性工具集**，用于管理从专业捕获设备（如体感摄像棚）采集的复杂数据，并将其转换为 Unreal Engine 可用的资产。它不仅仅是导入文件，更提供了一套完整的工作流，包括：

1.  **配置与命名管理**：集中管理媒体存储目录、资产导入目录、各类资产（视频、音频、校准数据）的命名规则和模板。
2.  **批量处理与转换**：支持通过蓝图或脚本触发批量数据导入（Ingest），可以配置并发数量，并支持使用第三方编码器（如 FFmpeg）进行高效的格式转换。
3.  **与 Live Link Hub 集成**：可以自动发现并连接到 Live Link Hub 实例，实现与外部捕获服务的协同工作，甚至自动启动内置的 Ingest Server 来处理数据。
4.  **资产类型化创建**：在导入过程中，能够根据捕获数据的类型（如图像序列、深度序列、音频、校准数据、镜头文件）自动创建对应的 UE 资产（如 MediaSource、SoundWave、CameraCalibration、LensFile 等）。

## 使用场景

- 你在进行**虚拟制片**，使用了一套专业的体感摄像棚系统，需要将拍摄的多机位视频、音频、摄像机运动数据批量导入到 UE 项目中。
- 你需要**标准化**捕获数据的导入流程，确保每次导入的资产都遵循统一的命名规则和存放路径。
- 你的团队使用 **Live Link Hub** 作为数据中转站，希望 UE 编辑器能自动发现并与其对接，简化数据流转。
- 你需要使用 **FFmpeg 等第三方工具**对捕获的原始视频或音频进行转码，再将结果导入引擎。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Capture Manager Editor Settings` | 获取全局唯一的捕获管理器编辑器设置实例。 | `UCaptureManagerEditorSettings` |
| `Set Media Directory` | 设置捕获媒体文件的存储目录。 | `UCaptureManagerEditorSettings` |
| `Set Import Directory` | 设置导入后资产在内容浏览器中的存放目录。 | `UCaptureManagerEditorSettings` |
| `On Capture Manager Editor Settings Changed` | 委托，当任何设置发生变更时触发。 | `UCaptureManagerEditorSettings` |

### 使用示例（蓝图描述）

1.  **配置路径**：
    - 在任意蓝图的 `BeginPlay` 事件中，首先调用 `Get Capture Manager Editor Settings` 节点获取设置对象。
    - 接着调用 `Set Media Directory` 和 `Set Import Directory` 节点，分别传入 `FDirectoryPath` 结构体来指定路径。`Import Directory` 必须指向项目 `Content` 文件夹内的有效路径（例如 `/Game/CaptureManager/Imports`）。

2.  **响应设置变更**：
    - 绑定 `On Capture Manager Editor Settings Changed` 委托到自定义事件。
    - 当在项目设置中修改了捕获管理器的任何选项（如并发数、编码器开关等）时，该委托将被触发，允许蓝图执行相应的更新逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "Settings/CaptureManagerEditorSettings.h"
```

### 基本用法

```cpp
// 获取单例设置实例
UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
if (Settings)
{
    // 读取配置
    FDirectoryPath MediaDir = Settings->MediaDirectory;
    int32 ConcurrentJobs = Settings->MaxConcurrentIngests;
    bool bUseEncoder = Settings->bEnableThirdPartyEncoder;

    // 在编辑器环境下修改配置
#if WITH_EDITOR
    FDirectoryPath NewImportDir;
    NewImportDir.Path = TEXT("/Game/CaptureManager/NewImports");
    Settings->SetImportDirectory(NewImportDir);
#endif
}
```

### 进阶用法

监听设置变更：
```cpp
// 在某个 UObject（如 Actor 或 Manager 类）中
void AMyCaptureActor::BeginPlay()
{
    Super::BeginPlay();

    if (UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings())
    {
        // 绑定到设置变更委托
        Settings->OnCaptureManagerEditorSettingsChanged.AddDynamic(this, &AMyCaptureActor::OnSettingsChanged);
    }
}

void AMyCaptureActor::OnSettingsChanged()
{
    // 当设置变更时，重新读取配置
    UE_LOG(LogTemp, Log, TEXT("Capture Manager settings changed. Reloading..."));
    ReloadConfiguration();
}
```

## Demo 示例

一个简单的 Actor，用于演示如何在 C++ 中集成和响应捕获管理器设置。

**MyCaptureActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyCaptureActor.generated.h"

UCLASS()
class MYPROJECT_API AMyCaptureActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCaptureActor();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnSettingsChanged();

private:
    void PrintCurrentSettings();
};
```

**MyCaptureActor.cpp**
```cpp
#include "MyCaptureActor.h"
#include "Settings/CaptureManagerEditorSettings.h"

AMyCaptureActor::AMyCaptureActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyCaptureActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定到设置变更
    UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
    if (Settings)
    {
        Settings->OnCaptureManagerEditorSettingsChanged.AddDynamic(this, &AMyCaptureActor::OnSettingsChanged);
        PrintCurrentSettings();
    }
}

void AMyCaptureActor::OnSettingsChanged()
{
    UE_LOG(LogTemp, Warning, TEXT("AMyCaptureActor: Detected settings change!"));
    PrintCurrentSettings();
}

void AMyCaptureActor::PrintCurrentSettings()
{
    UCaptureManagerEditorSettings* Settings = UCaptureManagerEditorSettings::GetCaptureManagerEditorSettings();
    if (Settings)
    {
        UE_LOG(LogTemp, Log, TEXT("Current Media Directory: %s"), *Settings->MediaDirectory.Path);
        UE_LOG(LogTemp, Log, TEXT("Max Concurrent Ingests: %d"), Settings->MaxConcurrentIngests);
        UE_LOG(LogTemp, Log, TEXT("Use Third Party Encoder: %s"), Settings->bEnableThirdPartyEncoder ? TEXT("True") : TEXT("False"));
    }
}
```

## 模块依赖

该插件由多个运行时模块组成，其构建依赖反映了其核心功能。

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 用于处理媒体资产（如创建 ImageSequenceMediaSource）。 |
| `LiveLinkInterface`, `LiveLinkHubMessaging` | 实现与 Live Link Hub 的连接和通信。 |
| `NamingTokens` | 提供基础的命名令牌系统，用于资产模板化命名。 |
| `CaptureManagerUtils` | 提供捕获数据管理的通用工具函数和类型。 |
| `LiveLinkHubWorkerManager` | 管理与 Live Link Hub 相关的工作线程任务。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `175468f6` | [CaptureManager] Generalize device terminology in DeviceBlueprint | 将蓝图中的设备相关术语通用化，提高一致性。 |
| 2026-04-30 | `63a844fc` | [CaptureManager] Move blocking ingest Blueprint APIs to a Blocking subcategory. | 将蓝图中可能阻塞的摄取API移动到“Blocking”子类别，优化节点组织。 |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增了一个用于设备蓝图的运行时模块，扩展蓝图功能。 |
| 2026-04-29 | `5a664506` | [Backout] - CL53274396 | 撤销了之前的某个更改。 |
| 2026-04-29 | `1c481042` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 首次尝试添加设备蓝图模块，随后被撤销。 |

### 维护评价

- **维护状态**：**活跃维护**。尽管插件创建时间约1年，但最近一个月内（2026年4月底）有多次密集的功能性提交，表明该模块正在**积极开发**中。
- **功能完整性**：从设置、命名、编码、服务器到设备蓝图，功能模块齐全，且结构清晰。
- **推荐使用**：**强烈推荐**。对于需要将专业级捕获数据集成到虚拟制片流程中的项目，该插件是官方提供的核心解决方案。由于仍在快速迭代，使用时应关注官方更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)
- [官方文档]( )
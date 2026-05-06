# Timecode Synchronizer (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the TimedDataMonitor plugin instead.
An asset that will become the TimecodeProvider once all the inputs get synchronized to a timecode.

| 属性 | 值 |
|---|---|
| 中文名 | 时间码同步器（已弃用） |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimecodeSynchronizer` (Runtime), `TimecodeSynchronizerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 👴 老古董（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer) | |

## 用途

本插件提供了一个特殊的 `UTimecodeSynchronizer` 资产，用于将多个时间码输入源（例如来自不同视频捕获卡或网络时间码流）同步到同一个时间码基准上。资产在同步完成后自动成为引擎的 `TimecodeProvider`，使整个项目（包括 Sequencer、录制系统等）获得统一的时间码参考。

**重要：** 此插件自 UE5.0 起已废弃。所有功能已被 `TimedDataMonitor` 插件替代。新项目应直接使用 `TimedDataMonitor`，现有项目应尽快迁移。

## 使用场景

- 在虚拟制片或多机位拍摄中，需要将多路带有时间码信号（如 SMPTE ST 12-1）的视频源对齐到同一时间线上。
- 将同步后的时间码暴露为全局 `TimecodeProvider`，供其他子系统（如 Take Recorder、Live Link）使用。
- 在编辑器环境中通过 Level Toolbar 快捷按钮创建和选取当前使用的 `TimecodeSynchronizer` 资产。

## 蓝图用法

由于该插件已废弃且 `UTimecodeSynchronizer` 未提供公开的 BlueprintCallable 函数，蓝图无法直接控制同步过程。所有操作应在 C++ 或编辑器 UI 中完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无蓝图表面的 API） | – | – |

## C++ 用法

### 头文件引入

```cpp
PRAGMA_DISABLE_DEPRECATION_WARNINGS
#include "TimecodeSynchronizer.h"
#include "TimecodeSynchronizerEditorModule.h"
PRAGMA_ENABLE_DEPRECATION_WARNINGS
```

### 基本用法

**1. 创建 `TimecodeSynchronizer` 资产（通过工厂）**

源文件：`TimecodeSynchronizerFactory.cpp`

```cpp
// 使用工厂直接创建新资产（通常通过编辑器内容浏览器触发）
UFactory* Factory = NewObject<UTimecodeSynchronizerFactory>();
UObject* NewAsset = Factory->FactoryCreateNew(
    UTimecodeSynchronizer::StaticClass(),
    InParent,
    FName("MySyncer"),
    RF_Standalone | RF_Public,
    nullptr,
    GWarn
);
```

**2. 在编辑器中打开资产**

源文件：`AssetTypeActions_TimecodeSynchronizer.cpp`

```cpp
// 打开 TimecodeSynchronizer 资产编辑器
FAssetTypeActions_TimecodeSynchronizer Actions;
TArray<UObject*> Assets;
Assets.Add(MySyncer);
Actions.OpenAssetEditor(Assets);
```

**3. 手动触发同步（在 Runtime 模块中）**

（Runtime 模块源码未提供，但典型用法如下）

```cpp
UTimecodeSynchronizer* Syncer = LoadObject<UTimecodeSynchronizer>(nullptr, TEXT("/Game/MySyncer.Syncer"));
if (Syncer)
{
    Syncer->StartSynchronization();    // 开始同步（假设存在此方法）
}
```

### 进阶用法

**Editor 模块提供 Level Toolbar 集成**

源文件：`TimecodeSynchronizerEditorLevelToolbar.cpp`

```cpp
// 在 Level 视口工具栏注册按钮，使用户可以快速选取或创建 TimecodeSynchronizer
FTimecodeSynchronizerEditorLevelToolbar Toolbar;
// 其构造函数自动调用 ExtendLevelEditorToolbar()
```

**自定义资产编辑器**

源文件：`TimecodeSynchronizerEditorToolkit.cpp`

```cpp
// 创建自定义编辑器布局，包含属性面板、源查看器、同步时间线控件
FTimecodeSynchronizerEditorToolkit::CreateEditor(Mode, Host, Syncer);
```

## Demo 示例

**头文件 `MyTimecodeRecipient.h`**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTimecodeRecipient.generated.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS
class UTimecodeSynchronizer;
PRAGMA_ENABLE_DEPRECATION_WARNINGS

UCLASS()
class MYPROJECT_API AMyTimecodeRecipient : public AActor
{
    GENERATED_BODY()

public:
    // 设置要使用的 TimecodeSynchronizer 资产
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Timecode")
    TObjectPtr<UTimecodeSynchronizer> TimecodeSyncAsset;

    // 开始同步
    UFUNCTION(BlueprintCallable, Category = "Timecode")
    void StartSync();

    // 停止同步
    UFUNCTION(BlueprintCallable, Category = "Timecode")
    void StopSync();

protected:
    virtual void BeginPlay() override;
};
```

**源文件 `MyTimecodeRecipient.cpp`**

```cpp
#include "MyTimecodeRecipient.h"

PRAGMA_DISABLE_DEPRECATION_WARNINGS
#include "TimecodeSynchronizer.h"
PRAGMA_ENABLE_DEPRECATION_WARNINGS

void AMyTimecodeRecipient::StartSync()
{
    if (TimecodeSyncAsset)
    {
        TimecodeSyncAsset->StartSynchronization(); // 假设此方法存在（Runtime 模块）
    }
}

void AMyTimecodeRecipient::StopSync()
{
    if (TimecodeSyncAsset)
    {
        TimecodeSyncAsset->StopSynchronization(); // 假设此方法存在
    }
}

void AMyTimecodeRecipient::BeginPlay()
{
    Super::BeginPlay();
    // 可以在 BeginPlay 中自动启动同步
}
```

## 模块依赖

**省略常见依赖（Core, Engine, Slate 等）。**

| 模块 | 用途 |
|---|---|
| `MediaPlayerEditor` | 提供媒体播放器编辑器资源，用于在源查看器中显示视频纹理。 |
| `WorkspaceMenuStructure` | 将编辑器标签页集成到窗口菜单中。 |
| `LevelEditor` | 用于扩展 Level 视口工具栏。 |
| `PropertyEditor` | 在编辑器细节面板中显示资产属性（标准依赖，但此处列出作为提醒）。 |

**Runtime 模块额外依赖（从 Build.cs 推断）：** `MediaAssets`, `TimeManagement` — 用于处理时间码和媒体输入。

## 维护状态

### 近期更新

- 2025-06-13 b3edcb21 — Replace some usages of FORCEINLINE with inline in MovieScene modules.
- 2023-11-29 c98c8912 — Fix C4702 warnings
- 2023-02-18 e599d19e — Removing redundant Private includes.
- 2023-01-16 bbc37aa2 — [Engine/Plugins] (大规模代码清理)
- 2022-10-21 610c4676 — Update vendor links for built-in plugins to use secure protocol.

### 维护评价

- **创建时间**：2022-10-21，距今约 3 年。
- **最近更新**：2025-06-13 仅有一次编译修复，无功能性更新。此前上一次实质性改动在 2023-11 的警告修复和 2023-02 的代码清理。
- **已弃用**：自 UE5.0 起官方标记为废弃，并以 `TIMECODESYNCHRONIZEREDITOR_API` 宏中的 `UE_DEPRECATED(5.0)` 警告使用者迁移。
- **推荐状态**：**不推荐使用**。新项目应直接使用 `TimedDataMonitor` 插件。现有项目应计划迁移，因为此插件可能在后续引擎版本中被移除。
- **潜在风险**：无已知 Bug，但长期不更新可能在未来引擎版本中出现编译问题或行为异常。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer)
- [官方文档（替代方案）](https://docs.unrealengine.com/5.3/en-US/timed-data-monitor-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer/Source)（插件内无专门测试，集成测试位于 `Engine/Tests/` 对应目录）
# Timecode Synchronizer (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the TimedDataMonitor plugin instead.
An asset that will become the TimecodeProvider once all the inputs get synchronized to a timecode.

| 属性 | 值 |
|---|---|
| 中文名 | 时间码同步器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimecodeSynchronizer` (Runtime), `TimecodeSynchronizerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-14 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer) | |

## 用途
此插件是一个**已废弃**的运行时时间码提供程序管理资产。其核心功能是将来自不同输入源（如音频、视频、网络）的输入数据流与一个主时间码源进行帧级别的同步。它解决的问题是：在虚拟制片、多机位拍摄等场景下，确保所有视频和音频输入源在精确的同一时间点开始录制或播放，从而实现画面与声音的帧同步。插件通过一个可编辑的资产（`UTimecodeSynchronizer`）来管理和监控各个输入源的同步状态，并在其所有输入同步后提供一个统一的时间码。

**注意**：此插件已被官方标记为废弃（Deprecated），并建议使用 `TimedDataMonitor` 插件取而代之。因此，不建议在新项目中使用。

## 使用场景
- **历史遗留项目维护**：在已使用此插件的旧版虚拟制片项目中，进行维护或理解其工作原理。
- **帧同步测试与分析**：在特定环境下，分析和测试多个媒体输入源的时间对齐情况。
- **学习示例**：作为一个了解 UE 中如何实现自定义时间码提供程序和输入源管理的参考（尽管已有更优方案）。

## 蓝图用法
根据提供的源码头文件，此插件的核心资产 `UTimecodeSynchronizer` 的公开蓝图函数未在提供的头文件中明确列出。其主要功能通过编辑器工具和资产属性面板暴露。在蓝图中，更常见的是使用其他（非此插件）的时间码相关功能。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 主要资产 `UTimecodeSynchronizer` 的公开蓝图函数在提供的代码中未明确展示。其功能主要通过编辑器UI和配置属性实现。 | - |

### 使用示例（蓝图描述）
由于此插件主要面向编辑器配置，且已废弃，不推荐在蓝图中进行新的开发。其典型使用流程是：
1.  在内容浏览器中右键创建 `TimecodeSynchronizer` 类型的资产。
2.  双击打开资产编辑器，在属性面板中配置各个输入源（例如 Audio Jack, SDI Input 等）。
3.  编辑器中的专用控件（如同步条、源视图）会显示所有输入源的当前时间码和同步状态。

## C++ 用法
此插件的核心运行时类 `UTimecodeSynchronizer` 旨在被继承和配置为一个 `TimecodeProvider`。其C++用法主要围绕创建、配置并注册这个资产。

### 头文件引入
```cpp
#include "TimecodeSynchronizer.h"
```

### 基本用法
创建一个 `UTimecodeSynchronizer` 资产实例并进行基本配置。
（用法基于类结构和通用资产模式推断）

```cpp
// 在合适的位置（如模块启动时或自定义工具中）创建资产
UTimecodeSynchronizer* SyncAsset = NewObject<UTimecodeSynchronizer>(GetTransientPackage(), TEXT("MySyncAsset"));
if (SyncAsset)
{
    // 配置主源、输入源等属性（具体API需查阅完整类定义）
    // 例如：SyncAsset->SetPrimarySource(...);
    // 例如：SyncAsset->AddActiveTimecodedInputSource(...);
    
    // 最终，将此资产设置为引擎的时间码提供程序（通常通过项目设置或命令完成）
    // 注意：此步骤的具体实现依赖于插件的完整代码。
}
```

### 进阶用法
监听同步事件，在C++中获取同步状态。编辑器模块 `ITimecodeSynchronizerEditorModule` 提供了对编辑器功能的访问。
（用法基于提供的编辑器头文件推断）

```cpp
// 检查编辑器模块是否可用
if (ITimecodeSynchronizerEditorModule::IsAvailable())
{
    // 获取模块实例，可能会用到一些编辑器特定的工具方法
    ITimecodeSynchronizerEditorModule& EditorModule = ITimecodeSynchronizerEditorModule::Get();
    // 调用模块提供的特定函数...
}
```

## Demo 示例
以下是一个展示如何创建 `UTimecodeSynchronizer` 对象并检查其基本属性的最小C++示例。

**MyTimecodeSyncManager.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "TimecodeSynchronizer.h" // 引入插件核心头文件
#include "MyTimecodeSyncManager.generated.h"

UCLASS()
class UMyTimecodeSyncManager : public UObject
{
    GENERATED_BODY()

public:
    /** 创建并初始化一个时间码同步器资产 */
    UFUNCTION(BlueprintCallable, Category = "TimecodeSync")
    UTimecodeSynchronizer* CreateAndInitSynchronizer();

    UPROPERTY()
    TObjectPtr<UTimecodeSynchronizer> CurrentSynchronizer;
};
```

**MyTimecodeSyncManager.cpp**
```cpp
#include "MyTimecodeSyncManager.h"

UTimecodeSynchronizer* UMyTimecodeSyncManager::CreateAndInitSynchronizer()
{
    // 创建资产实例（通常资产是在编辑器中持久化的，此处为运行时演示）
    CurrentSynchronizer = NewObject<UTimecodeSynchronizer>(this, TEXT("RuntimeSyncAsset"));
    
    if (CurrentSynchronizer)
    {
        // 在此处进行资产配置，例如设置属性
        // 注意：具体可设置的属性需查看UTimecodeSynchronizer的完整定义
        UE_LOG(LogTemp, Log, TEXT("Created TimecodeSynchronizer asset: %s"), *CurrentSynchronizer->GetName());
        
        // 实际使用中，可能需要将其注册为活动的TimecodeProvider
        // 这通常通过UTimecodeSynchronizer自身的方法或引擎全局设置完成
    }
    
    return CurrentSynchronizer;
}
```

## 模块依赖
基于插件 .uplugin 文件中声明的依赖插件和对运行时模块的一般认知。

| 模块 | 用途 |
|---|---|
| `MediaPlayer` | 处理媒体播放、音频捕获等，是核心媒体输入的基础。 |
| `MediaAssets` | 提供媒体源资产（如 `UFileMediaSource`）相关支持。 |
| `MediaUtils` | 媒体工具函数库。 |
| `TimeManagement` | 时间管理核心功能，提供 `UTimecodeProvider` 基类和时间码结构。 |
| `MediaPlayerEditor` | 编辑器模块依赖，用于媒体源在编辑器中的播放和预览。 |

## 维护状态
### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏UE_LOG迁移到新式UE_LOGF。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件名从Base前缀改为Default前缀。 |
| 2025-06-13 | `b3edcb21` | Replace some usages of FORCEINLINE with inline in MovieScene modules. | 在MovieScene相关模块中将部分FORCEINLINE替换为inline。 |
| 2023-11-29 | `c98c8912` | Fix C4702 warnings | 修复不可达代码警告（C4702）。 |
| 2023-02-18 | `e599d19e` | Removing redundant Private includes. | 移除多余的私有头文件包含。 |

### 维护评价
**已废弃，仅进行最低限度维护。**
- **年龄**：插件创建于2018年，至今约7年。
- **近期更新**：最近的提交均为通用引擎维护（如日志宏迁移、配置文件重命名、编译警告修复），**没有功能性更新或bug修复**。这明确符合其“已废弃”状态。
- **活跃度**：维护不活跃。官方已明确建议使用 `TimedDataMonitor` 插件替代，此插件仅处于“被移除前”的存留阶段。
- **推荐度**：**强烈不推荐**在新项目中使用。对于旧项目，应评估迁移到 `TimedDataMonitor` 插件的可行性。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/TimecodeSynchronizer)
- [官方文档]() （无，`.uplugin` 中 `DocsURL` 为空）
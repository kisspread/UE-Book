# MetaHuman Footage Ingest

> ⚠️ **此模块已在 UE 5.7 中废弃**，功能已迁移至 `CaptureManager` 模块。本文档仅供历史参考。

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器 UI 样式、工具栏命令） |
| 模块 | `MetaHumanFootageIngest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest) | |

## 用途

MetaHumanFootageIngest 是 MetaHuman Animator 插件中的**素材导入管理模块**，负责：

1. **捕获源管理**：连接和管理各种面部捕获设备（iPhone、专业相机等），监控设备在线/离线状态
2. **素材摄取（Ingest）**：将捕获的面部表演素材（Takes）批量导入到 UE 项目中，生成 `UFootageCaptureData` 资产
3. **导入队列管理**：支持排队、暂停、取消导入任务，跟踪每个 Take 的导入状态
4. **录制控制**：通过 CaptureManager 界面远程控制捕获设备的录制开始/停止

该模块本质上是一个**编辑器工具窗口**（CaptureManager），为 MetaHuman Animator 的面部动画工作流提供素材采集的入口。

## 使用场景

- 你使用 iPhone + Live Link Face 捕获了大量面部表演 Take → 用此模块批量导入到项目
- 你需要管理多个捕获设备并监控录制状态 → 用 CaptureManager 窗口统一管理
- 你需要将捕获素材自动转换为 MetaHuman 可用的动画数据 → 此模块是工作流的第一步

## 蓝图用法

此模块主要提供编辑器 UI 组件，**不暴露蓝图 API**。所有类均为 C++ Slate Widget 或编辑器工具类，无 `BlueprintCallable` 函数。

### 核心类

| 类 | 说明 |
|---|---|
| `FCaptureManager` | 单例管理器，负责注册/显示 CaptureManager 编辑器标签页 |
| `SCaptureManagerWidget` | 主 UI 容器，组合捕获源列表和素材摄取面板 |
| `SCaptureSourcesWidget` | 捕获源列表视图，显示已连接设备及其 Takes |
| `SFootageIngestWidget` | 素材摄取面板，管理导入队列和目标路径 |
| `FCaptureManagerCommands` | 编辑器工具栏命令（Save/SaveAll/Refresh/StartStopCapture） |
| `FFootageCaptureSource` | 捕获源数据结构，封装设备状态和 Take 列表 |
| `FFootageTakeItem` | 单个 Take 的数据结构，包含预览图、帧数、导入状态等 |

## C++ 用法

### 头文件引入

```cpp
#include "CaptureManager.h"
#include "CaptureManagerWidget.h"
#include "CaptureSourcesWidget.h"
#include "FootageIngestWidget.h"
```

### 基本用法

```cpp
// 显示 CaptureManager 编辑器窗口
FCaptureManager::Get()->Show();

// 显示特定捕获源的监控标签页
FCaptureManager* Manager = FCaptureManager::Get();
if (Manager)
{
    TWeakPtr<SDockTab> MonitoringTab = Manager->ShowMonitoringTab(MyCaptureSource);
}
```

### 捕获源状态枚举

```cpp
// 捕获源连接状态
enum class EFootageCaptureSourceStatus
{
    Closed,   // 已关闭
    Offline,  // 离线
    Online    // 在线
};

// Take 导入状态
enum class EFootageTakeItemStatus
{
    Unqueued,                   // 未排队
    Queued,                     // 已排队
    Warning,                    // 有警告
    Ingest_Active,              // 导入中
    Ingest_Paused,              // 已暂停
    Ingest_Canceled,            // 已取消
    Ingest_Failed,              // 导入失败
    Ingest_Succeeded,           // 导入成功
    Ingest_Succeeded_with_Warnings  // 成功但有警告
};
```

## Demo 示例

此模块为纯编辑器 UI 模块，不提供运行时 API。典型使用方式是通过编辑器菜单打开 CaptureManager 窗口。

```cpp
// MyEditorModule.cpp - 在自定义编辑器模块中集成 CaptureManager
#include "CaptureManager.h"

void FMyEditorModule::StartupModule()
{
    // CaptureManager 作为单例自动初始化
    FCaptureManager::Initialize();
}

void FMyEditorModule::ShutdownModule()
{
    FCaptureManager::Terminate();
}

void FMyEditorModule::OpenCaptureManager()
{
    if (FCaptureManager* Manager = FCaptureManager::Get())
    {
        Manager->Show();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureSource` | 捕获源抽象层，提供 `UMetaHumanCaptureSource` 基类 |
| `MetaHumanCaptureUtils` | 捕获工具函数库 |
| `MetaHumanCaptureDataEditor` | 捕获数据资产编辑器支持 |
| `MetaHumanImageViewerEditor` | 图像预览查看器 |

## 维护状态

### 近期更新

```
- f207c623330f [MetaHuman] Fixed a couple of garbage collection issues during ingest.
- 77f392c7c872 [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
- 9afffeda15e1 [Backout] - CL45863710 [FYI] peter.wigg #rnx Original CL Desc --- [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
```

### 维护评价

**⚠️ 此模块已废弃，不推荐使用。**

- 所有公开类均标记 `UE_DEPRECATED(5.7, "...deprecated. This functionality is now available in the CaptureManager module")`
- 功能已完整迁移至独立的 `CaptureManager` 模块
- 最近的实质性更新仅为垃圾回收修复，之后即标记废弃
- 废弃标记经历了提交→回退→重新提交的过程，说明迁移过程有反复

**建议**：如果你正在开发新项目，请直接使用 `CaptureManager` 模块。此文档仅适用于维护使用 UE 5.6 或更早版本的遗留项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanFootageIngest)
- [父插件 MetaHumanAnimator](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
# Field Notification Trace

> Add support to trace field notification object.

| 属性 | 值 |
|---|---|
| 分类 | Developer (路径) / UI (.uplugin) |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | FieldNotificationTrace (Runtime), FieldNotificationTraceEditor (Editor) |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/FieldNotificationTrace) | |

## 用途

FieldNotificationTrace 是一个**调试/性能分析工具**，用于在 UE5 的 [Rewind Debugger](../RewindDebugger/index.md) 中追踪和可视化 [Field Notification](../../essential/FieldNotification/index.md) 系统的事件。

它解决的核心问题是：**当你的 ViewModel 或实现了 `INotifyFieldValueChanged` 的对象产生大量字段变更通知时，很难知道"什么时候、哪个字段、被谁触发了变更"**。这个 plugin 将这些事件记录到 Unreal Trace 系统中，然后在 Rewind Debugger 的时间线上以可视化的方式展示出来，让你可以回放和检查字段变更的时序。

简单来说：**Field Notification 的 "Chrome DevTools Performance 面板"**。

### 工作原理

整个数据流分为三个阶段：

1. **运行时记录** (FieldNotificationTrace 模块)：通过宏在 Field Notification 的关键生命周期节点（对象创建/销毁、字段值变更）写入 Trace 事件
2. **Trace 分析** (Editor 模块中的 Analyzer)：读取 `.utrace` 文件，将原始事件解析为结构化的 Provider 数据
3. **UI 可视化** (Editor 模块中的 Track)：在 Rewind Debugger 中为每个追踪对象创建轨道，用事件点标注字段变更

## 使用场景

- 你在用 **MVVM 框架**（ViewModel + View 绑定），需要调试数据绑定为什么没有更新 UI
- 你的 Field Notification 对象频繁触发 `FieldValueChanged`，需要排查**性能热点**
- 你需要验证**字段变更的时序**是否符合预期（例如：A 字段变更后 B 字段是否也跟着变了）
- 你在做**回放调试**（Rewind Debugger），想看到回放过程中字段通知的变化

## 蓝图用法

此 plugin 没有暴露任何蓝图节点。它是一个纯 C++ 的开发者/调试工具，通过 Trace 系统和控制台命令操作。

## C++ 用法

### 头文件引入

```cpp
#include "Trace/FieldNotificationTrace.h"
```

### 核心宏

FieldNotificationTrace 提供了三个 Trace 宏，用于在你的代码中埋点：

```cpp
// 在实现 INotifyFieldValueChanged 的对象构造时调用
UE_TRACE_FIELDNOTIFICATION_LIFETIME_BEGIN(Interface);

// 在对象销毁时调用（通常在析构函数中）
UE_TRACE_FIELDNOTIFICATION_LIFETIME_END(Interface);

// 当某个 FieldNotification 字段的值发生变更时调用
UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(Object, FieldId);
```

这些宏在 Shipping 构建中会被编译为空操作（由 `UE_FIELDNOTIFICATION_TRACE_ENABLED` 宏控制），不影响运行时性能。

### 编译条件

Trace 功能仅在以下条件下启用：

```cpp
#define UE_FIELDNOTIFICATION_TRACE_ENABLED (UE_TRACE_ENABLED && !IS_PROGRAM && UE_BUILD_SHIPPING)
```

即：Trace 系统已启用 + 不是独立程序 + 非 Shipping 构建。

### 控制台命令

Runtime 模块注册了两个控制台命令：

| 命令 | 说明 |
|---|---|
| `FieldNotification.StartTracing` | 开始录制 Field Notification 事件（同时启用 `FieldNotificationChannel` 和 `Object` 通道） |
| `FieldNotification.StopTracing` | 停止录制 |

### Trace 通道

录制的数据通过 `FieldNotificationChannel` 通道传输，包含以下事件类型：

| Trace 事件 | 数据 | 说明 |
|---|---|---|
| `ObjectBegin` | Cycle, ObjectId | 对象开始跟踪 |
| `ObjectEnd` | Cycle, ObjectId | 对象停止跟踪 |
| `FieldValueChanged` | Cycle, RecordingTime, ObjectId, FieldNotifyId | 字段值变更 |
| `StringId` | Id, Value | FName 到数字 ID 的映射（用于压缩传输） |

### 在 Rewind Debugger 中使用

1. 启用 FieldNotificationTrace 插件（默认关闭）
2. 打开 **Window → Developer Tools → Rewind Debugger**
3. 点击录制按钮开始录制
4. 运行游戏，执行会产生 Field Notification 的操作
5. 停止录制后，在时间线上选择一个对象
6. 对象下方会出现 **"Field Notify"** 轨道，每个被触发的 `FFieldNotificationId` 作为子轨道显示
7. 轨道上的白点表示该字段在该时刻被触发了变更通知

### Demo 示例

假设你有一个实现了 `INotifyFieldValueChanged` 的 ViewModel：

```cpp
// MyViewModel.h
#pragma once
#include "UObject/Interface.h"
#include "INotifyFieldValueChanged.h"
#include "MyViewModel.generated.h"

UCLASS(BlueprintType)
class UMyViewModel : public UObject, public INotifyFieldValueChanged
{
    GENERATED_BODY()

    // Field Notification 声明
    UPROPERTY(BlueprintReadWrite, FieldNotify)
    FString PlayerName;

    // ... FieldNotify 宏展开、实现 GetLifetimeFieldNotifies 等
};
```

要在 Trace 中追踪这个对象的字段变更，你可以在 `FieldValueChanged` 的回调中插入 Trace 宏：

```cpp
void UMyViewModel::SetPlayerName(const FString& NewName)
{
    if (PlayerName != NewName)
    {
        PlayerName = NewName;

        // 发送 Field Notification
        FFieldNotificationId FieldId(GET_MEMBER_NAME_CHECKED(UMyViewModel, PlayerName));
        BroadcastFieldValueChanged(FieldId);

        // 追踪此事件
        UE_TRACE_FIELDNOTIFICATION_FIELD_VALUE_CHANGED(this, FieldId);
    }
}
```

## 模块依赖

### FieldNotificationTrace (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、平台抽象 |
| `CoreUObject` | UObject 系统、FObjectTrace |
| `Engine` | 引擎核心 |
| `FieldNotification` | Field Notification 系统（`INotifyFieldValueChanged`, `FFieldId`） |
| `TraceLog` | (Private) Unreal Trace 系统 |
| `GameplayInsights` | (Private, Editor only) Gameplay 属性追踪（可选，编译开关 `UE_FIELDNOTIFICATION_TRACE_FIELDVALUE`） |

### FieldNotificationTraceEditor (Editor)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `FieldNotification` | Field Notification 系统 |
| `FieldNotificationTrace` | Runtime Trace 模块 |
| `GameplayInsights` | (Private) Gameplay 分析 Provider 接口 |
| `RewindDebuggerInterface` | (Private) Rewind Debugger 扩展接口 |
| `Slate` / `SlateCore` | (Private) UI 框架（时间线控件） |
| `TraceAnalysis` | (Private) Trace 数据分析框架 |
| `TraceLog` | (Private) Trace 日志 |
| `TraceServices` | (Private) Trace 分析服务（Provider/Analyzer 注册） |

## 架构总览

```
FieldNotificationTrace (Runtime)
└── FieldNotificationTrace.h/cpp
    ├── FTrace 类 — 提供静态方法输出 Trace 事件
    ├── 3 个 Trace 宏 — 用于代码埋点
    └── 控制台命令 — StartTracing / StopTracing

FieldNotificationTraceEditor (Editor)
├── FieldNotificationRewindDebugger — Rewind Debugger 扩展（录制时自动启用通道）
├── FieldNotificationTrack — 时间线 UI 轨道
│   ├── FObjectTrack — 对象级轨道（包含多个字段子轨道）
│   └── FFieldNotifyTrack — 单个字段的事件轨道
├── FieldNotificationTraceAnalyzer — Trace 事件解析器
├── FieldNotificationTraceProvider — 数据 Provider（存储分析结果）
├── FieldNotificationTraceServices — TraceServices 模块注册
└── FieldNotificationTraceEditorModule — 模块入口（注册 Modular Features）
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-22 | `72d0756` | [RewindDebugger] deprecated IterateSubTracksInternal and replaced it by GetChildrenInternal that can be use to iterate subtracks and to visit all tracks recursively | 跟随 RewindDebugger 框架的 API 重构，`IterateSubTracksInternal` → `GetChildrenInternal`，支持递归遍历子轨道 |
| 2025-05-14 | `971045e` | [RewindDebugger] replaced single uint64 identifier for traced object by a struct allowing more complex scenarios to add non-UObject based entries | 对象标识符从单个 `uint64` 升级为结构体（主 UObject + 子元素），支持非 UObject 的追踪条目 |
| 2024-11-22 | `36771d7` | Updated uplugin descriptor files marked as both Experimental and Beta | 批量更新 uplugin 标记，此 plugin 从 Experimental 移到 Developer 目录并标记为 Beta |

### 维护评价

- **创建时间**：2024-05-24，约 2 年前
- **维护状态**：**活跃维护** — 最近一次更新在 2025 年 7 月，跟随着 RewindDebugger 框架的 API 演进
- **Beta 状态**：`IsBetaVersion = true`，`EnabledByDefault = false` — 这意味着 API 可能会变化，且需要手动启用
- **依赖风险**：强依赖 RewindDebugger 和 GameplayInsights 插件，如果这些上游 API 变化，此 plugin 需要同步更新
- **代码质量**：代码结构清晰，模块划分合理，有完善的编译条件控制
- **已知限制**：
  - `UE_FIELDNOTIFICATION_TRACE_FIELDVALUE` 编译开关默认为 0（关闭），不会追踪具体的属性值变化，只记录字段变更事件
  - 双击轨道的 "打开资产编辑器" 功能被注释掉了（代码中有 TODO 注释），尚不完整
  - 没有测试用例
- **推荐**：如果你在使用 Field Notification / MVVM 框架做调试，推荐启用。这是一个轻量级的调试辅助工具，不增加运行时负担（Shipping 下完全禁用）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/FieldNotificationTrace)
- Field Notification 系统文档（参见本书 [FieldNotification](../../essential/FieldNotification/index.md) 章节）
- Rewind Debugger 文档（参见本书 [RewindDebugger](../RewindDebugger/index.md) 章节）

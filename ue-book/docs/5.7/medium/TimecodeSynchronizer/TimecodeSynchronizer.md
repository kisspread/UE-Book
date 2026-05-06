# Timecode Synchronizer (Deprecated)

> This plugin has been deprecated and will be removed in a future engine version. Please update your project to use the features of the TimedDataMonitor plugin instead.
> An asset that will become the TimecodeProvider once all the inputs get synchronized to a timecode.

| 属性 | 值 |
|---|---|
| 中文名 | 时间码同步器（已弃用） |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TimecodeSynchronizer` (Runtime), `TimecodeSynchronizerEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-21 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer) | |

## 用途

Timecode Synchronizer 旨在将多个时间码输入源（如 IP 视频流、NDI 源等）同步到同一个时间轴上，并产生一个统一的 `TimecodeProvider` 供引擎使用。它尝试通过用户定义的偏移或自动检测帧偏移，使所有源输出对应同一时间码的帧。

**⚠️ 重要警告**：该插件自 UE 5.0 起已标记为已弃用，并将在未来引擎版本中移除。Epic 官方推荐使用 **TimedDataMonitor** 插件作为替代方案。不建议在新项目中使用。

## 使用场景

- **虚拟制片**：需要将多个摄像机/视频源（如 Blackmagic、AJA 等）与时间码信号精确同步。
- **nDisplay 多机同步**：在多个 Unreal Engine 实例之间保持输入同步（早期方案）。

由于已弃用，以上场景应全部迁移至 `TimedDataMonitor`。

## 蓝图用法

该插件所有核心类型均已标记 `UE_DEPRECATED(5.0, ...)`，**不提供可调用的蓝图函数**。以下为枚举类（仅供了解，不可在蓝图中使用）：

| 枚举 | 说明 |
|---|---|
| `ETimecodeSynchronizationSyncMode` | 同步模式：UserDefinedOffset / Auto / AutoOldest |
| `ETimecodeSynchronizationTimecodeType` | 时间源类型：DefaultProvider / TimecodeProvider / InputSource |
| `ETimecodeSynchronizationFrameRateSources` | 帧率来源：EngineCustomTimeStepFrameRate / CustomFrameRate |

如需在蓝图中实现类似功能，请使用 `TimedDataMonitor` 插件提供的节点。

## C++ 用法

由于插件已弃用，**不建议在 C++ 代码中直接引用**。所有暴露的类、枚举、结构均被标记 `UE_DEPRECATED(5.0, ...)`。若仍需使用（仅限迁移期间），可参考以下示例：

### 头文件引入

```cpp
// 文件路径：Engine/Plugins/Media/TimecodeSynchronizer/Source/TimecodeSynchronizer/Public/TimecodeSynchronizer.h
#include "TimecodeSynchronizer.h"
```

### 基本用法（仅作迁移参考）

```cpp
PRAGMA_DISABLE_DEPRECATION_WARNINGS

// 创建 TimecodeSynchronizer 资产（需通过编辑器创建或加载）
UTimecodeSynchronizer* Synchronizer = NewObject<UTimecodeSynchronizer>();

// 设置属性（部分示例）
Synchronizer->TimecodeType = ETimecodeSynchronizationTimecodeType::InputSource;
Synchronizer->FrameRateSource = ETimecodeSynchronizationFrameRateSources::EngineCustomTimeStepFrameRate;

// 启动同步（假设已将源添加到 Synchronizer）
Synchronizer->StartSynchronization();

PRAGMA_ENABLE_DEPRECATION_WARNINGS
```

### 进阶用法

该插件内部通过 `FTickableGameObject` 每帧检查各源的时间码，并调整 `TimecodeProvider`。具体实现涉及 `FTimecodeSynchronizerCachedSyncState` 等内部结构，不再赘述。

**强烈建议**：直接使用 `TimedDataMonitor` 插件（`TimedDataMonitorSubsystem`）的 C++ API。

## Demo 示例

此插件已弃用，不提供演示示例。请参考 `TimedDataMonitor` 插件的官方示例。

## 模块依赖

仅列出本插件特有的依赖（省略标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `MediaPlayerEditor` | 编辑器模块，用于在细节面板中显示媒体播放器资源选择 |

其他隐式依赖（由 `TimecodeSynchronizer` 自身内部使用）：
- `MediaAssets`、`MediaUtils`、`TimeManagement`（标准媒体和时间码模块，无需手动添加）

## 维护状态

### 近期更新

| 日期 | Hash | Commit 解读 |
|---|---|---|
| 2025-06-13 | `b3edcb21` | 将某些 FORCEINLINE 替换为 inline（小规模代码清理） |
| 2023-11-29 | `c98c8912` | 修复 C4702 警告 |
| 2023-02-18 | `e599d19e` | 移除重复的 Private 包含 |
| 2023-01-16 | `bbc37aa2` | 引擎级插件维护 |
| 2022-10-21 | `610c4676` | 更新内置插件供应商链接为安全协议（创建之后的提交） |

### 维护评价

- **创建时间**：2022-10-21（约 3 年前）。
- **最近更新**：最后一次实质性功能更新在 2023 年。2025 年的提交仅为全局代码清理。
- **活跃度**：无活跃功能开发，已进入废弃状态。
- **已知问题**：插件本身已弃用，可能存在与新版本引擎的兼容性问题。官方建议使用 `TimedDataMonitor`。
- **推荐使用**：**不推荐**。任何新项目或现有项目都应迁移至 `TimedDataMonitor`。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TimecodeSynchronizer)
- [官方文档（暂无）]()
- 测试用例位于 `Engine/Plugins/Media/TimecodeSynchronizer/Source/TimecodeSynchronizer/Private/Tests/`（多个 `.cpp` 文件）
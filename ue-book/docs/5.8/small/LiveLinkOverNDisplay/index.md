# Live Link Over nDisplay

> LiveLink subjects synchronization for nDisplay setup

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 链路同步 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkOverNDisplay` (Runtime) |
| 实验性 | 否 |
| 创建时间 | ~2025（估算） |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LiveLinkOvernDisplay) | |

## 用途

在 nDisplay 多机渲染集群中，所有机器（Controller 和 Agents）需要使用完全一致的 LiveLink 数据才能保证画面同步。本插件解决的核心问题是：**将 Controller 机器上接收到的 LiveLink Subject 数据实时复制到集群中所有 Agent 机器**，确保每台机器在每帧都使用相同的角色动画、摄像机位置、追踪数据等。

插件的实现机制：
- **Controller 端**：捕获所有 LiveLink Subject 数据，通过 nDisplay 的集群同步对象（`IDisplayClusterClusterSyncObject`）序列化并广播
- **Agent 端**：反序列化数据后创建对应的 `UNDisplayAgentVirtualSubject`（虚拟 Subject），将其注入本地 LiveLink 系统，使 Agent 上运行的逻辑和渲染读取到与 Controller 完全一致的数据

此外支持 **failover**（主节点切换），当 Controller 故障时自动恢复。

## 使用场景

- 你有一个 LED Volume（LED 虚拟摄影棚），多台机器通过 nDisplay 驱动不同区域的 LED 屏幕 → 启用此插件确保所有机器的摄像机追踪和动画数据同步
- 你在用 nDisplay 做多屏投影（CAVE / Powerwall），各屏需要从同一 LiveLink 源获取追踪数据 → 启用此插件自动同步
- 你用 LiveLink 驱动虚拟角色在多机集群中的实时表演 → 所有 Agent 机器的虚拟角色动作保持一致

## 蓝图用法

本插件主要通过**项目设置**配置，不暴露 BlueprintCallable 节点。

### 项目设置配置

在 **项目设置 → LiveLinkOverNDisplay Settings** 中：

| 属性 | 说明 | 默认值 |
|---|---|---|
| `bIsEnabled` | 是否启用 nDisplay 集群间的 LiveLink 同步 | `true` |

也可通过命令行覆盖：
```
-EnableLiveLinkOverNDisplay=false
```

命令行参数优先级高于项目设置。

## C++ 用法

### 头文件引入

```cpp
#include "ILiveLinkOverNDisplayModule.h"
```

### 基本用法

**检查模块是否可用并获取 Subject Replicator：**

```cpp
// 检查模块是否已加载
if (ILiveLinkOverNDisplayModule::IsAvailable())
{
    // 获取 Subject 复制器引用
    FNDisplayLiveLinkSubjectReplicator& Replicator = ILiveLinkOverNDisplayModule::Get().GetSubjectReplicator();
    
    // Replicator 在模块启动时自动初始化，无需手动操作
}
```

**读取当前设置状态：**

```cpp
#include "LiveLinkOverNDisplaySettings.h"

const ULiveLinkOverNDisplaySettings* Settings = GetDefault<ULiveLinkOverNDisplaySettings>();
if (Settings && Settings->IsLiveLinkOverNDisplayEnabled())
{
    // LiveLink over nDisplay 当前已启用
    // 注意：命令行参数 -EnableLiveLinkOverNDisplay=false 会覆盖项目设置
}
```

### 进阶用法

**FNDisplayLiveLinkSubjectReplicator 内部工作流程（理解原理）：**

Replicator 实现了 `IDisplayClusterClusterSyncObject` 接口，其同步逻辑如下：

```cpp
// Controller 端（伪代码）：
// 1. 每帧通过 OnEngineBeginFrame 收集所有已启用的 LiveLink Subject
// 2. 在 nDisplay 同步点调用 SerializeDC()
// 3. 按 Subject 逐个序列化：帧类型标记 + SubjectKey + Role + 帧数据

// Agent 端（伪代码）：
// 1. 在同步点接收序列化数据
// 2. 对新 Subject 创建 UNDisplayAgentVirtualSubject
// 3. 调用 UpdateFrameData() 将数据注入虚拟 Subject
// 4. LiveLink 系统通过虚拟 Subject 向下游提供数据
```

帧类型枚举：
```cpp
enum class EFrameType : uint8
{
    DataOnly,      // 仅数据更新（常规情况）
    NewSubject,    // 本帧有新 Subject 出现
    UpdatedSubject // Subject 的静态数据或角色类型发生变化
};
```

## Demo 示例

本插件没有独立的运行时 API，属于**基础设施插件**——启用后自动工作。以下是最小验证示例：

**LiveLinkOverNDisplayTest.Build.cs**（模块依赖）：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "LiveLinkOverNDisplay",
    "LiveLink"
});
```

**检查插件工作状态：**

```cpp
// MyNDisplayCheck.h
#pragma once

#include "CoreMinimal.h"

class FMyNDisplayCheck
{
public:
    static bool IsLiveLinkSyncActive();
};
```

```cpp
// MyNDisplayCheck.cpp
#include "MyNDisplayCheck.h"
#include "ILiveLinkOverNDisplayModule.h"
#include "LiveLinkOverNDisplaySettings.h"

bool FMyNDisplayCheck::IsLiveLinkSyncActive()
{
    // 1. 检查模块是否加载
    if (!ILiveLinkOverNDisplayModule::IsAvailable())
    {
        return false;
    }

    // 2. 检查设置是否启用
    const ULiveLinkOverNDisplaySettings* Settings = GetDefault<ULiveLinkOverNDisplaySettings>();
    if (!Settings || !Settings->IsLiveLinkOverNDisplayEnabled())
    {
        return false;
    }

    // 3. 检查 Replicator 是否激活（已注册为 nDisplay 同步对象）
    FNDisplayLiveLinkSubjectReplicator& Replicator = ILiveLinkOverNDisplayModule::Get().GetSubjectReplicator();
    return Replicator.IsActive();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | LiveLink 框架核心：Subject、Role、FrameData、VirtualSubject、Client 接口 |
| `nDisplay` / `DisplayCluster` | 集群同步对象接口 `IDisplayClusterClusterSyncObject`，主节点切换回调 |

还需注意插件级依赖（.uplugin 中声明）：
```json
"Plugins": [
    { "Name": "nDisplay", "Enabled": true }
]
```

你的项目必须同时启用 **nDisplay** 和 **LiveLink** 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 新格式 |
| 2026-01-19 | `fce888f0` | [nDisplay] Binary replication of some internal data | 改用二进制方式复制部分内部数据，提升同步效率 |
| 2025-12-09 | `e71a3b95` | [nDisplay] Re-shaping a 5.7 hotfix | 将 5.7 版本的热修复整合到主线 |
| 2025-12-01 | `96e0e9b2` | [nDisplay] Fixed LivelinkOverNDisplay replication logic in order to support new failover | 修复复制逻辑以支持新的故障转移机制 |
| 2025-04-11 | `fc6b4560` | [LiveLinkOvernDisplay] A quick fix to let LL work | 修复使 LiveLink 正常工作的快速补丁 |

### 维护评价

- **活跃维护中**：过去 12 个月内有多次实质性更新，涵盖功能改进（二进制复制）、failover 支持、热修复整合
- 功能相对聚焦且稳定，没有频繁重构
- 作为 nDisplay 集群的 LiveLink 同步基础设施，属于**关键路径插件**，但使用场景限于多机渲染
- **注意**：默认未启用（`EnabledByDefault: false`），需要手动在项目中启用，并确保 nDisplay 插件同时启用
- **推荐使用**：如果你的项目使用 nDisplay 多机渲染且需要 LiveLink 数据同步，这是官方推荐的方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/LiveLinkOvernDisplay)
- [官方文档]()（暂无）
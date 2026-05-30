# DMX Display Cluster

> Allows integration between DMX and DisplayCluster（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | DMX 与集群显示集成 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXDisplayCluster` (Runtime), `DMXDisplayClusterLightCard` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-05-11 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster) | |

---

## 用途

本插件解决 **DMX 协议与 nDisplay 多机集群系统之间的数据同步**问题。

在虚拟制片场景中，多台投影仪/LED 墙组成 nDisplay 集群，每台机器都是一个 Cluster Node。当使用 DMX 信号控制灯光、色卡（LightCard）等元素时，需要确保集群中所有节点收到相同的 DMX 数据。本插件通过 **集群事件复制（Cluster Event Replication）** 机制实现这一点：

- **主节点（Emitter）**：每 Tick 读取最新的 DMX 输入信号，通过二进制集群事件广播给集群中的其他节点。
- **从节点（Receiver）**：监听集群事件，将接收到的 DMX 数据应用到本地的 DMX 输入端口。

插件包含两个模块：
1. **DMXDisplayCluster**：核心复制器，负责 DMX 输入端口的跨集群同步。
2. **DMXDisplayClusterLightCard**：将 DMX 通道映射到 nDisplay 的 LightCard（用于控制投影仪边缘遮罩/色卡的位置、旋转、颜色等属性）。

---

## 使用场景

- 你在用 **nDisplay 多机集群 + DMX** 控制 LED 墙上的灯光效果 → 需要本插件保证所有节点的 DMX 数据一致
- 你需要通过 **DMX 协议远程控制 nDisplay LightCard**（遮罩板的位置、缩放、颜色等）→ 使用 DMXDisplayClusterLightCard 模块
- 你在搭建 **xR Stage**（扩展现实舞台），用 DMX 控制器（如 GrandMA）驱动虚拟场景中的灯光和遮罩 → 需要本插件做桥梁

---

## 蓝图用法

本插件的主要逻辑在 C++ 层（复制器为 `FTickableGameObject`），蓝图层面的可交互节点主要来自 **DMXDisplayClusterLightCard** 子模块，用于将 DMX 通道映射到 LightCard 属性。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| LightCard 属性映射 | 将 DMX 通道映射到 LightCard 的位置/旋转/缩放/颜色等属性 | `UDMXDisplayClusterLightCardComponent` |

> **注意**：DMXDisplayCluster 核心模块的复制逻辑（`FDMXDisplayClusterReplicator`）为纯 C++ 自动运行，无需蓝图干预。插件加载后自动根据当前节点角色（Emitter/Receiver）启动对应逻辑。

---

## C++ 用法

### 头文件引入

```cpp
#include "DMXDisplayClusterModule.h"
```

### 基本用法（模块生命周期）

插件模块自动创建复制器实例，无需手动调用。以下展示模块内部实现原理：

```cpp
// DMXDisplayClusterModule.cpp - 模块启动时自动创建复制器
void FDMXDisplayClusterModule::StartupModule()
{
    CreateDMXDisplayClusterReplicator();
}

void FDMXDisplayClusterModule::CreateDMXDisplayClusterReplicator()
{
    // 创建 DMX 跨集群复制器
    DMXDisplayClusterReplicator = MakeShared<FDMXDisplayClusterReplicator>();
}

void FDMXDisplayClusterModule::ShutdownModule()
{
    // 模块关闭时释放复制器
    DMXDisplayClusterReplicator.Reset();
}
```

### 进阶用法（复制器工作原理）

复制器在每 Tick 处理 DMX 信号同步：

```cpp
// FDMXDisplayClusterReplicator 内部逻辑

// 构造时确定角色：emitter 或 receiver
FDMXDisplayClusterReplicator::FDMXDisplayClusterReplicator()
{
    // bClusterEventEmitter 根据当前是否为集群主节点决定
    // 如果是 emitter：每 Tick 采集 DMX 信号并广播集群事件
    // 如果是 receiver：监听集群事件并将数据写入本地输入端口
}

// Emitter 端：每 Tick 采集最新信号并复制
void FDMXDisplayClusterReplicator::Tick(float DeltaTime)
{
    // 1. 遍历所有已注册的 DMX 输入端口 (CachedInputPorts)
    // 2. 提取最新信号 (ExternUniverseToSignalForReplicationMap)
    // 3. 通过 FOnClusterEventBinaryListener 广播给集群其他节点
}

// Receiver 端：监听集群事件回调
void FDMXDisplayClusterReplicator::OnClusterEventReceived(
    const FDisplayClusterClusterEventBinary& Event)
{
    // 解析二进制事件数据
    // 将 DMX 信号写入本地对应的输入端口（通过 FDMXRawListener）
}
```

---

## Demo 示例

> 本插件为运行时自动集成模块，插件启用后无需编写额外代码。以下展示如何在项目中确认插件是否正常工作。

```cpp
// MyGameModule.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyGameModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        // 验证 DMXDisplayCluster 模块是否加载
        IModuleInterface* DMXClusterModule = FModuleManager::Get().LoadModule(TEXT("DMXDisplayCluster"));
        if (DMXClusterModule)
        {
            UE_LOG(LogTemp, Log, TEXT("DMXDisplayCluster 模块已加载，DMX 跨集群复制已激活"));
        }
    }
};
```

实际使用中，只需确保：
1. 在项目的 `.uproject` 中启用 `DMXDisplayCluster` 插件
2. 配置 nDisplay 集群（DisplayCluster 配置文件中定义节点角色）
3. 设置 DMX 输入端口（通过 DMX 插件的端口配置）
4. 插件会自动根据节点角色启动 Emitter 或 Receiver 逻辑

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 集群系统，提供集群事件通信（BinaryClusterEvent） |
| `DMXRuntime` | DMX 运行时库，提供 DMX 输入端口、信号、原始监听器等核心类型 |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-09-26 | `d63fc61b` | DMX: Let DMXDisplayClusterLightCardComponent follow the logic of latest DisplayClusterLightCardActor | LightCard 组件对齐最新 nDisplay LightCard Actor 的行为逻辑 |
| 2024-09-17 | `29962d04` | DMX: Remove experimental and beta flags from DMX plugins. All DMX plugins are now production ready | 移除实验性/Beta 标志，DMX 插件正式转为生产就绪 |
| 2023-09-06 | `66eba088` | nDisplay: Added invoke of OnObjectPropertyChanged to the DMX Light Card component when applying chan... | LightCard 组件应用属性变更时正确触发 OnObjectPropertyChanged 回调 |
| 2023-06-05 | `6509b485` | nDisplay: Fixed issue where the DMXDisplayClusterLightCard module was not loading in before the ligh... | 修复 DMXDisplayClusterLightCard 模块加载顺序导致的问题 |
| 2023-01-20 | `9ac9217c` | DMX - Keep light cards flush to wall when controlled via DMX and bAlwaysFlushToWall is set | DMX 控制 LightCard 时，当 bAlwaysFlushToWall 启用可保持与墙壁贴合 |

### 维护评价

- **状态**：✅ 活跃维护
- **年龄**：约 4 年（2021 年创建），处于成熟期
- **更新频率**：2024 年仍有功能性更新和 bug 修复，最新更新距今约 1 年
- **重要里程碑**：2024-09-17 正式从实验性转为生产就绪状态，表明 Epic 认为该插件已稳定可靠
- **注意事项**：本插件与 DMX 插件套件及 nDisplay 系统紧密耦合，需确保这两个系统的版本兼容
- **推荐**：✅ 如果你的虚拟制片工作流涉及 DMX + nDisplay 集群，推荐使用

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster)
- [DMX 插件套件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX)
- [nDisplay 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots)
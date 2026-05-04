# DMX DisplayCluster

> Allows integration between DMX and DisplayCluster

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | — |
| 包含内容 | true |
| 模块 | DMXDisplayCluster (Runtime), DMXDisplayClusterLightCard (Runtime, PostConfigInit) |
| 创建时间 | 2021-05-11 |
| 年龄标签 | 🆕 (≤5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster) | |

## 用途

DMXDisplayCluster 解决的是 **多节点 nDisplay 集群中的 DMX 数据同步** 以及 **通过 DMX 控制 nDisplay Light Card** 的问题。

它包含两个子模块：

1. **DMXDisplayCluster**（核心复制器）：在 nDisplay 集群运行时，由 Primary 节点接收 DMX 数据，通过 DisplayCluster 的二进制集群事件（Binary Cluster Event）将 DMX 信号复制到所有 Secondary 节点，确保集群中所有节点看到相同的 DMX 数据。
2. **DMXDisplayClusterLightCard**（Light Card 集成）：通过 Modular Features 机制，为 nDisplay Light Card Actor 自动附加 `UDMXDisplayClusterLightCardComponent`，使 Light Card 的位置、颜色、透明度等属性可以通过 DMX Fixture Patch 实时控制。

## 使用场景

- 你在做一个 LED Volume / Virtual Production 拍摄，使用 nDisplay 多节点渲染 LED 墙 → 需要所有节点同步接收 DMX 控制台的灯光数据
- 你想通过 DMX 控制台实时控制 nDisplay 的 Light Card（遮罩、颜色渐变等）→ 添加 DMXDisplayClusterLightCardComponent
- 你在 cluster 模式下运行，需要在 Primary 节点读取 DMX 并分发到所有 Secondary 节点

## 蓝图用法

本插件没有暴露任何 BlueprintCallable 节点。`UDMXDisplayClusterLightCardComponent` 标记为 `NotBlueprintable`，只能通过编辑器 Details 面板配置，或在 C++ 中使用。

## C++ 用法

### 核心模块：DMXDisplayCluster Replicator

Replicator 在模块启动时自动创建，无需手动实例化。它监听 `IDisplayCluster` 的 `OnDisplayClusterStartSession` 回调，在 Cluster 模式下自动激活。

#### 命令行参数

Replicator 支持以下命令行参数来控制 Primary/Secondary 角色：

| 参数 | 说明 |
|---|---|
| `-dc_dmx_primary` | 强制当前节点为 DMX 发送端（Emitter） |
| `-dc_dmx_secondary` | 强制当前节点为 DMX 接收端（Listener） |

默认行为（不指定参数）：自动由 DisplayCluster ClusterManager 判断是否为 Primary 节点。

#### 工作原理

```
Primary 节点（Emitter）：
  1. 创建 FDMXRawListener 监听所有 DMX Input Port
  2. 每 Tick 从 RawListener 中取出最新信号
  3. 序列化为 FDMXDisplayClusterPacket（包含 Signal + PortIndex）
  4. 通过 ClusterManager->EmitClusterEventBinary() 广播

Secondary 节点（Listener）：
  1. 挂载 BinaryListener 监听集群事件
  2. 收到 EventId == 0xDDDD0000 的事件后反序列化
  3. 通过 CachedInputPorts[portIndex]->GameThreadInjectDMXSignal() 注入数据
```

**重要**：集群中所有节点的 DMX Input Port 配置必须一致，否则 PortIndex 对应关系会出错。

### Light Card 模块：DMXDisplayClusterLightCardComponent

通过 Modular Features 自动注册，在编辑器中为 Light Card Actor 添加 DMX 控制能力。

#### 头文件引入

```cpp
#include "DMXDisplayClusterLightCardComponent.h"
```

#### DMX 属性映射

组件监听 Fixture Patch 的 DMX 数据，按以下属性名映射到 Light Card Actor：

| DMX 属性名 | Light Card 属性 | 说明 |
|---|---|---|
| `DMXInput` | 启用/禁用开关 | 值 > 128 时启用 DMX 输入 |
| `DistanceFromCenter` | DistanceFromCenter | 球面距离 |
| `Pan` | Longitude / UVCoordinates.X | 经度（或 UV 模式的 U） |
| `Tilt` | Latitude / UVCoordinates.Y | 纬度（或 UV 模式的 V） |
| `Rot_X` | Spin | 旋转 |
| `Rot_Y` | Pitch | 俯仰 |
| `Rot_Z` | Yaw | 偏航 |
| `Scale_X` | Scale.X | X 缩放 |
| `Scale_Y` | Scale.Y | Y 缩放 |
| `Mask` | Mask | 遮罩类型（0-255 映射到枚举） |
| `Red` / `Green` / `Blue` | Color.RGB | 颜色（归一化） |
| `ColorAdd_Alpha` | Color.A | Alpha 通道 |
| `CTC` | Temperature | 色温 |
| `Tint` | Tint | 色调 |
| `Exposure` | Exposure | 曝光 |
| `Gain` | Gain | 增益 |
| `Opacity` | Opacity | 不透明度 |
| `Feathering` | Feathering | 羽化 |
| `Alpha_Gradient_Enable` | AlphaGradient.bEnableAlphaGradient | 渐变开关 |
| `StartingAlpha` | AlphaGradient.StartingAlpha | 起始 Alpha |
| `EndingAlpha` | AlphaGradient.EndingAlpha | 结束 Alpha |
| `Gradient_Angle` | AlphaGradient.Angle | 渐变角度 |

#### 值范围配置

`UDMXDisplayClusterLightCardComponent` 暴露一个 `ValueRanges` 属性（`FDMXDisplayClusterLightCardActorDataValueRanges`），用于配置每个 DMX 属性的映射范围：

```cpp
// 范围配置示例（在 Details 面板中设置）
// MinDistanceFromCenter = 0.0, MaxDistanceFromCenter = 1000.0
// DMX 归一化值 0.0 → 0.0, 1.0 → 1000.0
```

大部分属性使用 `FMath::Lerp(Min, Max, NormalizedValue)` 进行映射，颜色通道（RGBA）直接使用归一化值。

## Demo 示例

本插件无需编写额外代码即可使用，配置步骤如下：

### 前置条件

1. 启用插件：`DMXDisplayCluster`、`DMXEngine`、`DMXProtocol`、`nDisplay`、`nDisplayModularFeatures`
2. 配置 DMX Input Port（项目设置 → DMX → Input Ports）

### 配置 DMX 复制

1. 在 nDisplay 集群配置中，确保所有节点使用相同的 DMX Port 配置
2. 启动时添加 `-dc_dmx_primary`（主节点）或使用默认自动模式
3. 无需额外 Blueprint 或代码，Replicator 会自动工作

### 配置 Light Card DMX 控制

1. 在场景中放置 `ADisplayClusterLightCardActor`
2. 在 Actor 的 Details 面板中，找到自动添加的 `DMXDisplayClusterLightCardComponent`（在 "DMX" 分类下）
3. 设置 `Fixture Patch` 引用到你的 DMX Fixture Patch
4. 配置 `ValueRanges` 中的最小/最大值范围
5. 确保 Fixture Patch 的 GDTF 匹配上表中的属性名

## 模块依赖

### DMXDisplayCluster 模块

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎基础 |
| `DMXRuntime` | DMX 运行时（端口管理、信号处理） |
| `DMXProtocol` | DMX 协议层 |
| `DisplayCluster` | nDisplay 核心（集群管理、回调） |

### DMXDisplayClusterLightCard 模块

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心 |
| `DisplayClusterLightCardExtender` | Light Card 扩展接口（Modular Features） |
| `DMXProtocol` | DMX 协议层 |
| `DMXRuntime` | DMX 运行时 |
| `Core` | 基础核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎基础 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `DMXEngine` | DMX 引擎核心 |
| `DMXProtocol` | DMX 协议（Art-Net, sACN 等） |
| `nDisplay` | 多显示器/多节点渲染 |
| `nDisplayModularFeatures` | nDisplay 模块化扩展框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2024-10-01 | `769b448` | DMX: Let DMXDisplayClusterLightCardComponent follow the logic of latest DisplayClusterLightCardActor to update lightcards | 跟进上游 LightCard Actor 的更新逻辑，保持兼容 |
| 2024-09-17 | `4692008` | DMX: Remove experimental and beta flags from DMX plugins | 所有 DMX 插件标记为正式版，不再标记为实验性 |
| 2023-09-06 | `66eba08` | nDisplay: Added invoke of OnObjectPropertyChanged to the DMX Light Card component | 修复 ICVFX 面板的 Light Card 代理不更新的问题 |

### 维护评价

- **状态**：正式版（2024-09 起移除 Beta 标记）
- **活跃度**：维护中，最近一次功能性更新在 2024-10
- **稳定性**：代码量小（8 个源文件），逻辑清晰，改动风险低
- **已知限制**：
  - 集群中所有节点的 DMX Input Port 配置必须完全一致，否则会报错
  - 仅在 Cluster 模式下激活（编辑器预览中不工作）
  - Light Card 组件为 `NotBlueprintable`，只能在 C++ 中使用
- **推荐使用**：如果你在使用 nDisplay + DMX 的 Virtual Production 工作流，这是必须启用的插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXDisplayCluster)

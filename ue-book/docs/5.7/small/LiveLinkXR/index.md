# LiveLinkXR

> Live Link plugin for using XR tracked devices

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ `EnabledByDefault: false` |
| Beta 版本 | ✅ `IsBetaVersion: true` |
| 包含内容 | ✅ `CanContainContent: true` |
| 平台限制 | Win64 |
| 模块 | LiveLinkXR (Runtime), LiveLinkXROpenXRExt (Runtime, PostConfigInit) |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 5.8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkXR) | |

## 用途

LiveLinkXR 是一个将 **OpenXR 追踪设备**（Tracker、Controller、HMD）的位姿数据通过 **Live Link** 框架实时传输到 UE5 的插件。它解决了这样一个问题：在虚拟制片（Virtual Production）工作流中，你可能需要将 VR 追踪器（如 Vive Tracker）的位姿数据作为 Live Link Subject 供蓝图或 C++ 消费，用于驱动虚拟摄像机、道具或角色动画。

插件底层通过 OpenXR 扩展（`XR_KHR_win32_convert_performance_counter_time`）获取精确的 XR 时间戳，然后在独立线程中以可配置的频率（默认 60Hz）轮询所有被追踪设备的位姿，并将它们作为 `LiveLinkTransformRole` 数据推送到 Live Link 系统。

**关键特性：**
- 仅支持 OpenXR 运行时（不支持 SteamVR 原生等其他 XR 系统）
- 支持追踪 Tracker Puck、Controller、HMD 三类设备（可分别开关）
- 新发现的 Subject 默认开启 `bRebroadcastSubject`，便于多播场景
- 内置 Vive Tracker 调试用 3D 网格（`SM_ViveTracker.uasset`）

## 使用场景

- **虚拟摄像机追踪**：将 Vive Tracker 绑定在实体摄像机上，通过 LiveLinkXR 将位姿实时传输到 UE5，驱动虚拟摄像机。
- **身体动捕**：多个 Tracker Puck 绑定在身体各部位，通过 Live Link 驱带动画蓝图中的骨骼。
- **XR 设备调试**：需要在编辑器中实时查看所有 OpenXR 追踪设备的位姿数据。

## 编辑器用法

### 启用插件

LiveLinkXR 默认未启用，且标记为 Beta。需要手动启用：

1. 打开 **Edit → Plugins**
2. 搜索 **LiveLinkXR**
3. 勾选启用，重启编辑器

### 添加 Live Link 源

1. 打开 **Window → Live Link**
2. 点击 **Source** 按钮
3. 在下拉菜单中选择 **LiveLinkXR Source**（显示名：`LiveLinkXR Source`，提示：`Allows creation of multiple LiveLink sources using the XR tracking system`）
4. 在弹出的配置面板中设置以下选项：

| 参数 | 说明 | 默认值 |
|---|---|---|
| Track Trackers | 追踪 Tracker Puck（如 Vive Tracker） | ✅ 开启 |
| Track Controllers | 追踪手柄控制器 | ❌ 关闭 |
| Track HMDs | 追踪头戴显示器 | ❌ 关闭 |
| Local Update Rate In Hz | 数据更新频率（1–1000 Hz） | 60 |

5. 点击 **Add** 按钮创建源

### 查看追踪数据

在 Live Link 面板中，每个被追踪的设备会自动注册为一个 Subject，角色类型为 `LiveLinkTransformRole`。Subject 名称基于 OpenXR 设备路径（如 `/user/hand/left`、`/user/vive_tracker_htcx/role/left_foot`）。

每个 Subject 的 MetaData 中包含 `DeviceControlId` 字段，值为 OpenXR 设备路径字符串。

## 蓝图用法

本插件不暴露 `BlueprintCallable` 函数。所有功能通过 Live Link 框架间接使用：

### 消费 Live Link 数据

1. 在蓝图中添加 **Live Link Transform Controller** 组件或使用 **Evaluate Live Link Frame** 节点
2. 选择 LiveLinkXR 创建的 Subject
3. 获取 Transform 数据驱动 Actor/Component 的位置和旋转

### 使用内容资产

插件包含两个蓝图资产（`Content/Blueprints/`）：

| 资产 | 说明 |
|---|---|
| `BP_LiveLinkXR_DataHandler` | 数据处理蓝图，处理 Live Link 接收到的 XR 数据 |
| `BP_LiveLinkXR_DebugVis` | 调试可视化蓝图，使用 `SM_ViveTracker` 网格显示追踪器位置 |

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkXRSource.h"
#include "LiveLinkXRConnectionSettings.h"
```

### 创建 LiveLinkXR 源

```cpp
// 配置连接设置
FLiveLinkXRConnectionSettings Settings;
Settings.bTrackTrackers = true;    // 追踪 Tracker Puck
Settings.bTrackControllers = false; // 不追踪控制器
Settings.bTrackHMDs = false;       // 不追踪 HMD
Settings.LocalUpdateRateInHz = 90;  // 90Hz 更新率

// 创建源（需要通过 Live Link Client 接口）
TSharedPtr<FLiveLinkXRSource> Source = MakeShared<FLiveLinkXRSource>(Settings);
```

> **注意**：直接创建 `FLiveLinkXRSource` 需要确保 OpenXR 系统已初始化且 `XR_KHR_win32_convert_performance_counter_time` 扩展可用。通常通过编辑器 UI 或 Live Link 预设来创建源更可靠。

### 自定义 Source Settings

源创建后可以通过 `ULiveLinkXRSourceSettings` 动态修改更新频率：

```cpp
#include "LiveLinkXRSourceSettings.h"

// Source Settings 允许在源运行时调整更新率
// LocalUpdateRateInHz: 1-1000 Hz，默认 60
```

## 模块依赖

### LiveLinkXR 模块

使用者需要在 Build.cs 中添加的公共依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |
| `LiveLinkInterface` | Live Link 接口定义 |

内部私有依赖（无需用户添加）：`CoreUObject`, `Engine`, `HeadMountedDisplay`, `LiveLinkXROpenXRExt`, `OpenXRHMD`, `Slate`, `SlateCore`

### LiveLinkXROpenXRExt 模块

这是 OpenXR 扩展模块，自动由 LiveLinkXR 加载，无需用户直接依赖。

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心模块 |

内部私有依赖：`CoreUObject`, `Engine`, `HeadMountedDisplay`, `InputCore`, `OpenXRHMD`

## 插件依赖

| 插件 | 说明 |
|---|---|
| [OpenXR](../OpenXR/) | 必需。LiveLinkXR 仅兼容 OpenXR 运行时 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-21 | `82674f1924` | OpenXR extension names: use openxr.h define rather than hard coding the names | 代码质量改进：使用 OpenXR 头文件中的宏定义替代硬编码的扩展名称字符串，提高可维护性（关联 UE-305876） |
| 2025-03-13 | `b059f7b463` | Fix trivial unreachable code warnings | 编译警告修复，清理不可达代码 |
| 2024-10-02 | `7810d15efa` | Minor refactor to remove dependency on private header in OpenXRHMD module | 解耦私有头文件依赖，改善模块边界（关联 UE-193727） |

### 维护评价

- **创建时间**：2020 年 6 月，已存在约 5.8 年
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，自创建以来一直是 Beta
- **最近更新**：最近一次功能性更新在 2025-07-21，最近 1 年内有 3 次提交
- **活跃度**：**维护中** — 更新频率较低但仍在维护，近期更新集中在代码质量和依赖清理
- **已知限制**：
  - 仅支持 Win64 平台
  - 仅支持 OpenXR 运行时
  - 标记为 Beta，API 可能变化
  - 没有自动化测试用例
- **推荐程度**：如果你的虚拟制片工作流基于 OpenXR + Live Link，可以使用，但需注意其 Beta 状态。如果是 SteamVR 原生环境，此插件不适用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LiveLinkXR)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）

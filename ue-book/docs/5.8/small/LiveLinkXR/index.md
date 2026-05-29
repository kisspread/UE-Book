# Live Link XR

> Live Link plugin for using XR tracked devices（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | XR 追踪 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（插件资产） |
| 模块 | `LiveLinkXR` (Runtime), `LiveLinkXROpenXRExt` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR) | |

## 用途

将 OpenXR 运行时追踪的 XR 设备（头显、手柄、追踪点）通过 Live Link 框架实时传输到引擎。解决了虚拟制片场景中需要将 XR 设备的位姿数据桥接到其他系统（如虚拟相机、动捕、蓝图驱动）的问题。插件在 OpenXR 扩展层注册回调，在每帧获取设备 pose 并通过 Live Link Subject 广播，使得任何消费 Live Link 的客户端都能实时接收 XR 追踪数据。

## 使用场景

- 你正在做虚拟制片，需要将 VR 头显或手柄的实时位姿送给 nDisplay / 虚拟摄像机
- 你需要在多机协作中，将一个 OpenXR 设备的追踪数据通过 Live Link 传输给远程 UE 实例
- 你在开发 XR 预览工具，需要在非 HMD 模式下消费 VR 控制器的位姿
- 你需要将 OpenXR 追踪设备作为动画/运动捕捉数据源接入 Sequencer 或蓝图

## 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| `LiveLinkXR` | Runtime | 核心模块：注册 OpenXR 扩展，获取 XR 设备位姿并通过 Live Link Subject 广播 |
| `LiveLinkXROpenXRExt` | Runtime | OpenXR 扩展接口模块：在 PostConfigInit 阶段加载，实现与 OpenXR 运行时的底层对接（仅 Win64） |

## 蓝图用法

本插件不暴露 BlueprintCallable 节点。XR 设备追踪数据通过 Live Link Subject 发布，在蓝图中通过标准的 **Live Link** 节点消费：

### 消费追踪数据

| 节点 | 说明 |
|---|---|
| `Get Live Link Subject Names` | 获取所有已发布的 Live Link Subject，含本插件发布的 XR 设备 |
| `Get Live Link Transform` | 按 Subject 名称获取实时 transform（位置/旋转） |

**典型蓝图连接**：在 Tick 中 → Get Live Link Subject Names → 过滤包含 "OpenXR" 关键字的 Subject → 对每个 Subject 调用 Get Live Link Transform → 驱动场景中的 Actor Transform。

## C++ 用法

### 头文件引入

```cpp
#include "LiveLinkClient.h"
#include "LiveLinkXRModule.h"
```

### 基本用法

注册 Live Link 面板中的 XR 源后，通过 C++ 订阅 XR 设备 Subject：

```cpp
// 获取 Live Link 客户端
ILiveLinkClient& LiveLinkClient = IModularFeatures::Get().GetModularFeature<ILiveLinkClient>(ILiveLinkClient::ModularFeatureName);

// 订阅 XR 设备的 Subject
FLiveLinkSubjectKey SubjectKey;
SubjectKey.SubjectName = FName(TEXT("OpenXRDevice_Head"));

// 在 Tick 中获取最新 Transform
FSubjectFrameHandle SubjectData;
LiveLinkClient.EvaluateFrame_AnyThread(SubjectKey.SubjectName, UAnimationTypes::StaticStruct(), SubjectData);
```

## Demo 示例

本插件无需额外 Demo——启用插件后，在 **Live Link 面板** 中即可看到 OpenXR Source 以及自动发布的 XR 追踪设备 Subject。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心框架 |
| `LiveLinkInterface` | Live Link 接口定义 |
| `OpenXR` | OpenXR 运行时与设备管理 |
| `OpenXRHMD` | OpenXR HMD 设备访问 |

无特殊依赖（仅标准 Core/Engine/LiveLink/OpenXR 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2025-07-21 | `82674f19` | OpenXR extension names: use openxr.h define rather than hard coding the names. | 改用 openxr.h 宏定义扩展名称，移除硬编码字符串 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复不可达代码编译警告 |
| 2024-10-02 | `7810d15e` | LiveLinkXR: Minor refactor to remove depedency on private header in OpenXRHMD module | 重构移除对 OpenXRHMD 私有头文件的依赖 |
| 2024-03-22 | `001e4d27` | LiveLinkXR: Remove Linux from supported platforms. | 移除 Linux 平台支持 |

### 维护评价

- 插件仍保持维护，近 2 年内有持续的代码清理和兼容性改进
- 最近一次实质性功能更新为 2025 年的 OpenXR 扩展名称优化，其余为代码质量维护
- **仍标记为 Beta**（`IsBetaVersion: true`），且 `EnabledByDefault: false`，需手动启用
- 仅支持 **Win64** 平台
- 对 OpenXRHMD 模块私有头文件的依赖已清理（2024-10），架构耦合度降低
- **推荐使用**：适合虚拟制片中需要 XR 设备追踪数据经 Live Link 传输的场景，但需接受 Beta 状态的限制

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR/Tests)（如有）
- 子模块文档：[LiveLinkXR.md](LiveLinkXR.md)、[LiveLinkXROpenXRExt.md](LiveLinkXROpenXRExt.md)
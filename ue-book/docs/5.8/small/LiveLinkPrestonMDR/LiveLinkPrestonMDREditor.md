# LiveLinkPrestonMDR

> Live Link support for the Preston MDR-3 Motor Driver

| 属性 | 值 |
|---|---|
| 中文名 | 普雷斯顿MDR马达驱动 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器UI） |
| 模块 | `LiveLinkPrestonMDR` (Runtime), `LiveLinkPrestonMDREditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-03-05 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR) | |

## 用途

该插件为 Unreal Engine 的 Live Link 系统提供了与 **Preston MDR-3 马达驱动器** 的集成支持。Preston MDR-3 是电影和高端广告制作中广泛使用的设备，用于远程精确控制摄影机镜头的焦距（Focus）、光圈（Iris）和变焦（Zoom）等参数。

插件的核心功能是：
1.  **数据接收**：通过串口（通常为 USB 转串口）与 Preston MDR-3 硬件建立连接，实时读取其状态数据。
2.  **协议解析**：将接收到的 Preston 专有串行数据包解析为引擎可理解的 Live Link 属性（如镜头参数、马达位置等）。
3.  **Live Link 源**：将这些数据封装为 Live Link 源，使得任何支持 Live Link 的对象（如 Actor、Component）都能订阅并实时接收镜头控制数据。

**为什么存在？** 在虚拟制作（Virtual Production）工作流中，尤其是使用 LED 墙进行实时渲染时，需要将摄影机和镜头的实时物理运动与引擎内的虚拟摄影机同步。Preston MDR-3 作为专业的镜头控制设备，此插件是实现该同步的关键数据桥梁。

## 使用场景

-   你在进行 **虚拟制作（Virtual Production）** 或 **实时渲染**，使用 LED 墙（如 Volume Stage）。
-   你的物理摄影机镜头由 **Preston MDR-3** 系统控制。
-   你需要将 MDR-3 控制的镜头焦距、光圈、变焦等参数 **实时、同步** 地输入到 UE 场景中的虚拟摄影机，以实现精确的透视匹配和镜头效果。

## 蓝图用法

本插件的蓝图功能主要集中在创建和管理与 MDR-3 的连接源。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create New Source` | 创建一个新的 LiveLinkPrestonMDR 数据源。在编辑器 UI 面板中调用。 | `SLiveLinkPrestonMDRSourcePanel` |

### 使用示例（蓝图描述）

在 Live Link 源面板中，你可以找到 “Preston MDR” 选项。点击后，会弹出一个设置面板。在该面板中，你需要：
1.  **选择串口**：从下拉列表中选择与 Preston MDR-3 连接的 COM 端口。
2.  **配置连接参数**：如波特率等（通常保持默认即可）。
3.  **点击“创建源”**：插件将尝试连接设备。成功后，一个新的 Live Link 源会出现在 Live Link 面板的源列表中。

之后，在任何支持 Live Link 的 Actor 或 Component（例如 `CineCameraActor`）上，你可以将 “Live Link Component Controller” 添加到组件中，并将其主题（Subject）设置为来自这个 MDR-3 源的对应主题。这样，虚拟摄影机就会实时接收并响应物理镜头的变化。

## C++ 用法

该插件主要通过编辑器 UI 和 Live Link 框架进行配置和使用。C++ 层面主要是内部实现，但你可以通过其模块接口进行一些底层控制。

### 头文件引入

```cpp
#include "LiveLinkPrestonMDRModule.h"
```

### 基本用法

了解模块的启动与关闭生命周期。
```cpp
// 获取 LiveLinkPrestonMDR 模块
ILiveLinkPrestonMDRModule* PrestonMDRModule = FModuleManager::GetModulePtr<ILiveLinkPrestonMDRModule>(TEXT("LiveLinkPrestonMDR"));
if (PrestonMDRModule)
{
    // 模块已加载，可以进行一些高级操作（如果接口暴露）
}
```
*（来源：基于 `LiveLinkPrestonMDRModule.h` 的模块接口设计推断）*

### 进阶用法

该插件的高级用法通常涉及对 Live Link 源工厂 (`ULiveLinkPrestonMDRSourceFactory`) 的继承或重写，以自定义连接逻辑或数据处理流程。但这属于非常规用法，需深入研究源码。

## Demo 示例

以下示例展示了如何在 C++ 中获取并检查 LiveLinkPrestonMDR 模块。

**LiveLinkPrestonMDRUsage.h**
```cpp
#pragma once
#include "CoreMinimal.h"

// 前向声明
class ILiveLinkPrestonMDRModule;

class FLiveLinkPrestonMDRUsage
{
public:
    /** 尝试获取 Preston MDR 模块并检查其状态 */
    static void CheckPrestonMDRStatus();

private:
    /** 内部引用 */
    static ILiveLinkPrestonMDRModule* CachedPrestonMDRModule;
};
```

**LiveLinkPrestonMDRUsage.cpp**
```cpp
#include "LiveLinkPrestonMDRUsage.h"
#include "Modules/ModuleManager.h"
#include "ILiveLinkPrestonMDRModule.h" // 核心模块头文件

// 初始化静态成员
ILiveLinkPrestonMDRModule* FLiveLinkPrestonMDRUsage::CachedPrestonMDRModule = nullptr;

void FLiveLinkPrestonMDRUsage::CheckPrestonMDRStatus()
{
    // 获取模块（如果已加载）
    CachedPrestonMDRModule = FModuleManager::GetModulePtr<ILiveLinkPrestonMDRModule>(TEXT("LiveLinkPrestonMDR"));

    if (CachedPrestonMDRModule)
    {
        UE_LOG(LogTemp, Log, TEXT("LiveLinkPrestonMDR 模块已加载。"));
        // 在此处可以进一步调用模块提供的接口函数（如果有）
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("LiveLinkPrestonMDR 模块未找到或未启用。请在插件设置中启用它。"));
    }
}
```

## 模块依赖

从 `LiveLinkPrestonMDR.Build.cs` 和 `LiveLinkPrestonMDREditor.Build.cs` 分析，使用此插件时，你的模块需要添加以下特殊依赖：

| 模块 | 用途 |
|---|---|
| `LiveLink` | Live Link 核心运行时框架 |
| `LiveLinkInterface` | Live Link 的公共接口定义 |
| `LiveLinkComponents` | 用于在 Actor 上添加 Live Link 控制器组件 |
| `Serial` | 提供底层串口通信能力，用于连接 MDR-3 设备 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统日志宏迁移为新的日志框架格式。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复编译时出现的“不可达代码”错误。 |
| 2024-01-25 | `f43fc1d7` | Fixed up more bool-taking calls to take EAllowShrinking instead. | 适配引擎API变更，将布尔参数改为枚举类型。 |
| 2023-11-20 | `763a6119` | Fix C4072 warnings | 修复了特定编译器警告（C4072）。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 一次跨多个插件的通用提交（可能为集成或小修复）。 |

### 维护评价

该插件自2021年创建以来，至今约有5年历史。从 Git 历史看，**最近两年内有数次更新**，主要集中在**编译兼容性修复**和**代码风格迁移**上，而非重大功能添加。这表明该插件处于**维护状态**，能够跟随主引擎版本编译，但功能已相对稳定。

**优势**：作为虚拟制作中连接特定硬件（Preston MDR-3）的官方插件，其稳定性和集成度有保障。
**局限性**：
1.  **硬件依赖性强**：必须有物理的 Preston MDR-3 设备才能使用。
2.  **实验性状态**：`.uplugin` 中标记为 `IsBetaVersion=true`，意味着其 API 或行为未来可能会有变动。
3.  **功能聚焦**：仅支持 Preston MDR-3 一种设备，不具备通用性。

**推荐**：如果你的工作流中确实使用 **Preston MDR-3** 进行镜头控制，并且正在进行 **虚拟制作**，那么这是必需且推荐的插件。否则，无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkPrestonMDR/Tests) （如果存在）
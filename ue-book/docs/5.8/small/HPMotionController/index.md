# HP Motion Controller

> Controller mappings for the HP Reverb G2 motion controller in OpenXR and SteamVR

| 属性 | 值 |
|---|---|
| 中文名 | HP运动控制器 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HPMotionController` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HPMotionController) | |

## 用途

本插件是为 HP Reverb G2 混合现实头显的动作控制器提供的专用 OpenXR 扩展插件。它通过实现 `IOpenXRExtensionPlugin` 接口，向 Unreal Engine 的 OpenXR 子系统注册了 HP Reverb G2 控制器的交互配置文件（Interaction Profile），使得引擎能够正确识别和映射 HP 控制器的按键、摇杆和触觉反馈功能。它确保了在支持 OpenXR 的 VR 运行时（如 Windows Mixed Reality、SteamVR）中，HP 控制器能够被识别为有效的输入设备，而不仅仅是通用的控制器。

## 使用场景

-   **使用 HP Reverb G2 进行 VR 开发**：当你的项目或目标用户使用 HP Reverb G2 头显及其配套的动作控制器时，需要启用此插件以确保控制器功能（如按键映射、摇杆、触觉）正常工作。
-   **需要精确的控制器模型支持**：插件提供了获取控制器模型路径的功能，可用于在 VR 中渲染与实体手柄外观一致的虚拟控制器模型。

## 蓝图用法

本插件没有暴露任何蓝图节点。其功能完全通过 OpenXR 插件的底层架构自动集成和调用，用户无需在蓝图层面进行直接操作。

## C++ 用法

本插件的核心是一个 `IModuleInterface` 和 `IOpenXRExtensionPlugin` 的实现类，主要由 OpenXR 子系统在后台调用。开发者通常不需要直接包含或使用此插件的头文件，其功能通过插件启用后自动生效。

### 头文件引入

通常情况下无需引入。若需在极端情况下引用模块接口：

```cpp
#include "HPMotionController.h" // 模块内部头文件，不对外公开
```

### 基本用法

本插件作为 OpenXR 扩展插件，其生命周期由引擎管理。开发者只需在项目的 `.uproject` 文件或插件列表中启用 `HPMotionController` 插件即可。启用后，引擎初始化 OpenXR 运行时时会自动调用插件的 `PostCreateInstance`、`GetInteractionProfiles` 等方法来注册 HP 控制器的支持。

（来源文件: `Engine/Plugins/Runtime/HPMotionController/Source/HPMotionController/Private/HPMotionController.h`）

## Demo 示例

本插件无独立的可运行示例。其效果体现在所有使用 HP Reverb G2 控制器的 OpenXR VR 项目中。正确的使用方法是在项目设置中启用此插件，然后正常使用 `MotionController` 组件和 Enhanced Input 系统来处理输入。

```cpp
// 无需编写代码。只需在项目的 Plugins 设置中确保“HP Motion Controller”插件已启用。
// 然后，你的 MotionController Actor 或 Enhanced Input 映射将自动接收来自 HP 控制器的输入。
```

## 模块依赖

从模块的 `.Build.cs` 文件依赖关系推断，本插件的核心功能依赖于 OpenXR 插件。

| 模块 | 用途 |
|---|---|
| `OpenXR` | 核心依赖。HPMotionController 作为 OpenXR 的扩展插件存在，必须依赖 OpenXR 模块以实现其扩展接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-21 | `82674f19` | OpenXR extension names: use openxr.h define rather than hard coding the names. | 将 OpenXR 扩展名称改为引用头文件宏定义，提高代码可维护性。 |
| 2024-08-01 | `0ba65eae` | [OpenXR]One extension plugin adds multiple interaction profiles | 架构更新，支持一个扩展插件添加多个交互配置文件。 |
| 2023-02-17 | `75ceaf89` | Removing redundant OpenXR include paths. Cleaning up some other include paths to make them easier to | 清理冗余的头文件包含路径，优化代码结构。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新厂商链接为安全协议（HTTPS）。 |

### 维护评价

本插件自 2020 年随 UE4 发布以来，仍在持续维护。最近的提交（2025年）表明 Epic 仍在随着 OpenXR API 的演进对其进行更新和代码优化。虽然更新频率不高，但与核心 VR 输入架构保持同步。它是一个官方支持的、专门用于特定硬件映射的插件，状态稳定。对于使用 HP Reverb G2 的项目，**推荐启用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/HPMotionController)
-   官方文档：无
-   测试用例：未发现公开的自动化测试用例
# Virtual Scouting

> Virtual Scouting lets filmmakers scout a digital environment in virtual reality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟勘景 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（OpenXR 扩展模块） |
| 模块 | `VirtualScouting` (Runtime), `VirtualScoutingEditor` (Runtime), `VirtualScoutingOpenXR` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-19 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting) | |

## 用途

Virtual Scouting 是一个虚拟制作插件，其核心功能是为电影制作人员提供一种在虚拟现实（VR）中勘景的解决方案。它允许导演、美术指导等创作者通过 VR 头显直接进入由 UE 构建的数字场景，进行空间感知、镜头规划和场景设计评估。该插件通过 `VirtualScoutingOpenXR` 模块深度集成 OpenXR 运行时，为 VR 交互提供底层支持，并与 UE 内置的 VR 编辑器 (`VREditor`) 协同工作，实现无缝的 VR 编辑体验。

## 使用场景

- **电影前期制作**：导演和美术团队可以在 VR 中“走遍”计划拍摄的数字场景或尚未搭建的物理片场模型，直观地评估空间尺度、光线氛围和镜头构图。
- **建筑与环境设计评审**：建筑师或关卡设计师可以邀请客户或团队成员戴上头显，共同沉浸在虚拟空间中进行方案评审和修改。
- **虚拟制片（Virtual Production）准备**：在 LED 虚拟影棚的拍摄前，使用此工具对虚拟背景进行最终的 VR 预览和确认。

## 蓝图用法

根据提供的源码分析，`VirtualScoutingOpenXR` 模块主要提供 C++ 级别的接口，用于集成 OpenXR 和管理 VR 编辑模式。在当前分析的头文件中，未发现标记为 `BlueprintCallable` 的函数。其功能主要通过引擎的 VR 编辑模式和模块接口来触发和访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 主要功能通过引擎 VR 编辑模式访问 | `FVirtualScoutingOpenXRModule` |

### 使用示例（蓝图描述）

虽然没有直接的蓝图函数节点，但该插件的功能会通过以下方式在蓝图中体现：
1.  在编辑器偏好设置或插件设置中启用 `VirtualScouting` 插件。
2.  通过编辑器工具栏的 **“VR 勘景”** 或类似按钮（由 `VirtualScoutingEditor` 模块提供）进入 VR 编辑模式。
3.  一旦进入 VR 编辑模式，`VirtualScoutingOpenXR` 模块会自动激活并处理 VR 设备输入、会话和场景同步。
4.  设计师在 VR 中的移动、视角和交互将直接反映在 UE 编辑器的视口中。

## C++ 用法

### 头文件引入

```cpp
#include "VirtualScoutingOpenXRModule.h"
// 如果需要直接操作 OpenXR 扩展
#include "Internal/VirtualScoutingOpenXR.h"
```

### 基本用法

获取 `VirtualScoutingOpenXR` 模块的单例实例，并访问其管理的 OpenXR 扩展。
（来源文件：`Engine/Plugins/VirtualProduction/VirtualScouting/Source/VirtualScoutingOpenXR/Internal/VirtualScoutingOpenXRModule.h`）

```cpp
// 获取模块单例
FVirtualScoutingOpenXRModule& Module = FVirtualScoutingOpenXRModule::Get();

// 获取 OpenXR 扩展对象（注意生命周期）
const TSharedPtr<FVirtualScoutingOpenXRExtension>& OpenXRExt = Module.GetOpenXRExt();
if (OpenXRExt.IsValid())
{
    // 获取 HMD 设备类型的异步 Future
    TFuture<FName>& DeviceTypeFuture = OpenXRExt->GetHmdDeviceTypeFuture();
    // 可以通过 .Then() 或 .Get() 来处理结果
}
```

### 进阶用法

理解 `FVirtualScoutingOpenXRExtension` 如何作为 OpenXR 扩展插件工作，并响应 VR 编辑模式状态变化。
（来源文件：`Engine/Plugins/VirtualProduction/VirtualScouting/Source/VirtualScoutingOpenXR/Internal/VirtualScoutingOpenXR.h`）

```cpp
class FMyCustomOpenXRExtension : public FVirtualScoutingOpenXRExtension
{
    // 可以继承并扩展 OpenXR 事件处理
    virtual void OnEvent(XrSession InSession, const XrEventDataBaseHeader* InHeader) override
    {
        // 先调用父类实现
        FVirtualScoutingOpenXRExtension::OnEvent(InSession, InHeader);

        // 处理自定义的 OpenXR 事件
        // ...
    }

    // 覆写会话后创建方法，用于初始化自定义资源
    virtual void PostCreateSession(XrSession InSession) override
    {
        FVirtualScoutingOpenXRExtension::PostCreateSession(InSession);
        // 在此处进行 OpenXR 会话相关的初始化
    }
};
```

**关键点**：
- `FVirtualScoutingOpenXRExtension` 实现了 `IOpenXRExtensionPlugin` 接口，是连接 UE OpenXR 子系统与虚拟勘景功能的核心。
- 它通过 `OnVREditingModeEnter()` 和 `OnVREditingModeExit()` 私有方法监听 VR 编辑模式的切换。
- `TryGetHmdDeviceType()` 和 `TryFulfillDeviceTypePromise()` 用于异步获取和确定当前连接的 HMD 设备类型，这对于适配不同 VR 硬件的功能至关重要。

## Demo 示例

一个最小化的示例，展示如何初始化模块并订阅其事件。这通常发生在插件自身的初始化代码中，但对于希望集成或观察该插件行为的其他模块，可以参考此模式。

**VirtualScoutingOpenXRDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FVirtualScoutingOpenXRDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    FDelegateHandle OnVRModeEnterHandle;
};
```

**VirtualScoutingOpenXRDemo.cpp**
```cpp
#include "VirtualScoutingOpenXRDemo.h"
#include "VirtualScoutingOpenXRModule.h"
#include "Internal/VirtualScoutingOpenXR.h"

#define LOCTEXT_NAMESPACE "FVirtualScoutingOpenXRDemoModule"

void FVirtualScoutingOpenXRDemoModule::StartupModule()
{
    // 确保 VirtualScoutingOpenXR 模块已加载
    if (FModuleManager::Get().IsModuleLoaded("VirtualScoutingOpenXR"))
    {
        FVirtualScoutingOpenXRModule& VSModule = FVirtualScoutingOpenXRModule::Get();
        const auto& Ext = VSModule.GetOpenXRExt();
        if (Ext.IsValid())
        {
            // 在此可以获取设备类型 Future 等
            UE_LOG(LogTemp, Log, TEXT("VirtualScouting OpenXR Extension is available."));
        }
    }
}

void FVirtualScoutingOpenXRDemoModule::ShutdownModule()
{
    // 清理工作
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FVirtualScoutingOpenXRDemoModule, VirtualScoutingOpenXRDemo)
```

## 模块依赖

要使用 `VirtualScoutingOpenXR` 模块，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `VREditor` | UE 的 VR 编辑器核心模块，提供 VR 模式管理、交互和 UI 支持。这是 `VirtualScoutingOpenXR` 功能运行的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中32位/64位说明符与参数不匹配的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移为使用更安全的 `UE_LOGF`。 |
| 2026-03-13 | `b1da5d8f` | [Gizmos] Remove GizmoEdMode from areas not covered by preflight checks | 从预检未覆盖的区域移除了 GizmoEdMode，属于 Gizmos 功能的清理工作。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将配置文件从 `Base<Plugin>.ini` 重命名为 `Default<Plugin>.ini`，遵循 UE 的配置命名规范。 |

### 维护评价

- **创建时间**：2024年9月创建，是一个相对年轻的插件。
- **更新频率**：最近一年内有多次提交，但主要是代码维护、编译警告修复和规范性调整，没有发现重大的功能更新或架构变动。
- **活跃度**：处于**维护中**状态。代码在持续被清理和优化，表明它仍在 Epic 的维护范围内，但功能上可能已趋于稳定。
- **已知问题**：无特别报道。作为一个 Runtime 且 `EnabledByDefault=false` 的插件，它属于“按需启用”的专业工具。
- **推荐使用**：**推荐**。如果你的虚拟制作流程需要在 VR 中进行沉浸式场景勘景和评审，这是一个官方提供的、与引擎深度集成的解决方案。尽管功能稳定，但确保了与 UE 最新版本和 OpenXR 标准的兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/VirtualScouting)
- [官方文档]() （暂无）
- [测试用例]() （源码目录中未发现明显测试文件）
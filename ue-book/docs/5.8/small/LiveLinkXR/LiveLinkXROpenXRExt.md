# LiveLinkXR

> Live Link plugin for using XR tracked devices

| 属性 | 值 |
|---|---|
| 中文名 | XR 追踪适配器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `LiveLinkXR` (Runtime), `LiveLinkXROpenXRExt` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR) | |

## 用途

LiveLinkXR 插件的核心功能是充当 **OpenXR 设备与虚幻引擎 Live Link 系统之间的桥梁**。它解决了在虚拟制片（Virtual Production）等场景中，统一获取来自不同厂商的 XR 设备（如 VR 头显、手柄）的实时追踪数据（位置、旋转）的问题。

**具体工作原理**：
1.  它作为一个 OpenXR 扩展插件 (`FLiveLinkXROpenXRExtension`) 集成到引擎的 OpenXR 运行时中。
2.  利用 OpenXR 提供的 `XR_KHR_win32_convert_performance_counter_time` 等扩展，在引擎的渲染/游戏线程上高效地查询 XR 设备（如头显、手柄）相对于参考空间（本地空间或舞台空间）的位姿。
3.  查询到的位姿数据（`FTransform`）被映射为 Live Link 的“主题”（Subject），例如 `XRHMD` 或 `XRController_{Hand}`。
4.  其他系统（如 Sequencer 虚拟摄像机、动画蓝图、特效系统）可以通过标准的 Live Link 接口订阅这些主题，实时获取并使用 XR 设备的追踪数据。

**为什么存在**：在 LiveLinkXR 出现之前，获取 XR 设备数据通常需要直接调用特定 SDK（如 Oculus SDK, SteamVR SDK）。这个插件通过标准化的 OpenXR 和 Live Link 协议，提供了一种统一、解耦的方式，使得项目可以更容易地适配不同的 XR 硬件，并将数据无缝整合到引擎的动画、渲染等管线中。

## 使用场景

-   **虚拟制片**：您正在使用 VR 头显来“预览”或“驾驶”一个虚拟摄像机。LiveLinkXR 可以将头显的位姿实时映射为虚拟摄像机的变换，让您在 VR 中所见即所得。
-   **XR 互动体验**：您正在开发一个需要利用手柄追踪数据的应用。可以通过 Live Link 将手柄的位姿应用到场景中的虚拟手部模型或交互指针上。
-   **动捕与动画**：虽然主要用于实时预览，但其原理可用于驱动简单的虚拟角色，或作为更复杂动捕系统的补充。
-   **开发基础**：作为其他高级 XR 功能（如手势识别、空间锚点）的底层数据来源。

## 蓝图用法

该插件主要在底层通过 C++ 与 Live Link 和 OpenXR 系统集成，直接暴露给蓝图的高级节点较少。其功能主要通过 Live Link 的通用蓝图接口来使用。

### 核心节点

由于是数据提供方，蓝图中主要使用标准的 **Live Link 蓝图库** 节点来消费其数据：

| 节点 | 说明 | 所在库 |
|---|---|---|
| `Get Live Link Subject Transform` | 根据主题名称（如 “XRHMD”）获取其最新的世界变换。 | `LiveLinkBlueprintLibrary` |
| `Get Live Link Subject Names` | 获取当前所有可用的 Live Link 主题名称，其中应包含 `XRHMD` 或 `XRController_*`。 | `LiveLinkBlueprintLibrary` |
| `Is Live Link Subject in Engine` | 检查特定主题（如 “XRHMD”）是否已连接并正在发送数据。 | `LiveLinkBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **驱动虚拟摄像机**：
    -   在 Sequencer 中，为您的 CineCameraActor 添加一个 “Live Link Controller” 组件。
    -   在该组件的属性中，将 “Subject” 设置为 `XRHMD`。
    -   当插件启用且 XR 设备运行时，摄像机的变换将自动由头显驱动。

2.  **在蓝图中获取手柄位置**：
    -   添加一个 “Get Live Link Subject Transform” 节点。
    -   将 “Subject Name” 参数设置为 `XRController_Right` (名称取决于具体设备映射)。
    -   输出的 “World Transform” 即为该手柄在引擎世界中的实时变换，可用于更新一个 Actor 的位置和旋转。

## C++ 用法

直接与插件交互通常发生在需要扩展或自定义其行为时，或者在其初始化阶段。

### 头文件引入

```cpp
#include "LiveLinkXROpenXRExtModule.h"
#include "LiveLinkXROpenXRExtension.h"
```

### 基本用法

获取扩展实例并检查其状态。
*（来源: `LiveLinkXROpenXRExtModule.h`）*

```cpp
// 1. 确保模块已加载
if (FLiveLinkXROpenXRExtModule::IsAvailable())
{
    // 2. 获取模块单例
    FLiveLinkXROpenXRExtModule& Module = FLiveLinkXROpenXRExtModule::Get();
    
    // 3. 获取 OpenXR 扩展实例
    TSharedPtr<FLiveLinkXROpenXRExtension> Extension = Module.GetExtension();
    
    if (Extension.IsValid())
    {
        // 4. 检查扩展是否在当前 OpenXR 运行时中受支持
        bool bSupported = Extension->IsSupported();
        UE_LOG(LogTemp, Log, TEXT("LiveLinkXR OpenXR Extension is supported: %s"), bSupported ? TEXT("True") : TEXT("False"));
        
        // 5. (高级) 直接获取主题位姿映射 (通常由系统内部调用)
        // TMap<FName, FTransform> PoseMap;
        // Extension->GetSubjectPoses(PoseMap);
    }
}
```

### 进阶用法

该插件的核心在于其 `IOpenXRExtensionPlugin` 接口实现。开发者通常不需要直接调用 `GetSubjectPoses`，而是作为系统的一部分工作。更常见的用法是**监听 Live Link 主题的更新**。
*（标准 Live Link C++ 用法）*

```cpp
// 在你的Actor或组件中订阅特定主题
#include "ILiveLinkClient.h"
#include "Roles/LiveLinkTransformRole.h"

// ... 在 BeginPlay 或类似函数中
ILiveLinkClient* LiveLinkClient = ILiveLinkClient::Get(); // 获取 Live Link 客户端接口
if (LiveLinkClient)
{
    FLiveLinkSubjectKey SubjectKey;
    SubjectKey.SubjectName = FName("XRHMD");
    
    // 设置一个回调，当“XRHMD”主题有新数据时触发
    FDelegateHandle Handle = LiveLinkClient->OnLiveLinkTicked().AddLambda([SubjectKey](const FLiveLinkTickedFrameData& TickedData)
    {
        // TickedData.FrameData 中包含了该时刻所有主题的最新数据
        // 可以通过 TickedData.SubjectKey 找到对应主题
        // 然后使用标准的 Live Link 帧数据评估函数来获取 FTransform
    });
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在你的模块中集成 LiveLinkXR 扩展。
*注意：需要将 `YourModule` 替换为你的实际模块名，并在 `Build.cs` 中添加对 `LiveLinkXROpenXRExt` 和 `OpenXR` 的依赖。*

**YourModule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FYourModule : public IModuleInterface
{
public:
    /** IModuleInterface implementation */
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    // 可选的：存储扩展实例的引用，用于生命周期管理
    // TSharedPtr<class FLiveLinkXROpenXRExtension> MyExtensionRef;
};
```

**YourModule.cpp**
```cpp
#include "YourModule.h"
#include "LiveLinkXROpenXRExtModule.h"
#include "LiveLinkXROpenXRExtension.h"

#define LOCTEXT_NAMESPACE "FYourModule"

void FYourModule::StartupModule()
{
    // 检查并记录 LiveLinkXR 扩展的状态，作为功能可用性的参考
    if (FLiveLinkXROpenXRExtModule::IsAvailable())
    {
        auto& LLM = FLiveLinkXROpenXRExtModule::Get();
        auto Ext = LLM.GetExtension();
        if (Ext.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("YourModule: LiveLinkXR Extension found. Supported: %s"), Ext->IsSupported() ? TEXT("Yes") : TEXT("No"));
            // MyExtensionRef = Ext; // 如果需要延长生命周期
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("YourModule: LiveLinkXR Extension module loaded but extension not created."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("YourModule: LiveLinkXROpenXRExt module not loaded."));
    }
}

void FYourModule::ShutdownModule()
{
    // MyExtensionRef.Reset();
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FYourModule, YourModule)
```

## 模块依赖

从模块的 `Build.cs` 推断，要使用此插件（尤其是 `LiveLinkXROpenXRExt` 模块），你的模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `OpenXR` | 提供 OpenXR 核心头文件、类型和基础接口。 |
| `LiveLinkInterface` | Live Link 系统的核心接口，用于定义角色、主题和数据评估。 |
| `LiveLink` | Live Link 的运行时客户端和服务器实现。 |

（同时隐含依赖 `OpenXRHMD`，它是 OpenXR 的 HMD 插件实现）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统日志宏迁移到新的格式化宏，属于代码维护。 |
| 2025-07-21 | `82674f19` | OpenXR extension names: use openxr.h define rather than hard coding the names. | 使用 OpenXR 头文件中的定义而非硬编码扩展名，提高兼容性。 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复代码中不可达的代码段警告，提升代码质量。 |
| 2024-10-02 | `7810d15e` | LiveLinkXR: Minor refactor to remove depedency on private header in OpenXRHMD module | 重构代码，移除了对 OpenXRHMD 模块私有头文件的依赖。 |
| 2024-03-22 | `001e4d27` | LiveLinkXR: Remove Linux from supported platforms. | 从支持平台中移除 Linux，仅保留 Win64。 |

### 维护评价

-   **状态**：**实验性（Beta）但持续维护中**。尽管标记为 `IsBetaVersion`，且默认未启用，但从 git 历史看，过去几年有持续的维护和代码优化。
-   **创建时间**：2020年6月，约5年历史。
-   **更新频率**：最近2年内有多次有意义的更新，包括兼容性改进、代码清理和平台调整。
-   **已知限制**：
    1.  标记为实验性功能，可能不稳定或存在功能缺失。
    2.  仅支持 **Win64** 平台（Linux 支持已被移除）。
    3.  默认未启用，需要在插件设置中手动开启，并确保 OpenXR 插件也已启用。
-   **推荐**：推荐用于 **Win64 平台上的虚拟制片项目**，特别是需要将 XR 设备数据实时映射到引擎中的场景。在使用前，建议在目标硬件上进行充分测试。对于跨平台需求，需注意其平台限制。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LiveLinkXR)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Plugins/LiveLinkXR) （如果存在，通常在 Engine/Tests/ 下）
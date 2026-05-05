# OpenXRMsftHandInteraction

> OpenXRMsftHandInteraction provides support for the XR_MSFT_hand_interaction OpenXR Extension. This allows hand tracking to act as a motion controller.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | OpenXRMsftHandInteraction (Runtime) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXRMsftHandInteraction) | |

## 用途

这个插件为 UE5 的 OpenXR 子系统注入了 Microsoft 的 `XR_MSFT_hand_interaction` 扩展支持。它的工作原理是向 OpenXR 运行时注册一个 Interaction Profile（`/interaction_profiles/microsoft/hand_interaction`），使得裸手追踪（hand tracking）的输入能够被 UE5 的输入系统识别为标准的运动控制器输入。

具体来说，它做了两件事：

1. **注册 OpenXR 扩展**：在 OpenXR 初始化时请求启用 `XR_MSFT_hand_interaction` 扩展
2. **注册输入按键**：创建 4 个自定义输入键（左右手的 Select 和 Grip 轴），将手部追踪的捏合（pinch）和握拳（grip）手势映射为可用的输入事件

为什么需要这个插件？因为 UE5 的 OpenXR 默认支持的是标准手柄控制器（如 Oculus Touch、Valve Index 控制器等），但不支持将裸手追踪当作控制器使用。如果你想在 HoloLens 2 或支持 `XR_MSFT_hand_interaction` 扩展的设备上用裸手交互，就需要启用这个插件。

## 使用场景

- 你在开发 HoloLens 2 的 MR 应用，需要用裸手进行捏合选择和握拳抓取 → 启用此插件
- 你的 OpenXR 运行时支持 `XR_MSFT_hand_interaction` 扩展（如 Windows Mixed Reality），想把手部追踪数据当作标准输入使用 → 启用此插件
- 你已经使用了 OpenXR 的通用 hand tracking 扩展（`XR_EXT_hand_tracking`）但需要更高级的手势交互语义（Select/Grip）→ 这个插件提供的是交互层面的语义，不只是追踪数据

**注意**：此插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 蓝图用法

此插件注册的输入键标记为 `NotBlueprintBindableKey`，因此不能直接在蓝图的增强输入或输入映射中作为 Action/Axis 绑定使用。它们通过 UE5 的底层输入系统（`EKeys`）注册，主要供 C++ 层的 OpenXR 运行时内部使用。

在蓝图中，你可以通过 `Get Motion Controller Data` 等节点获取手部姿态数据（前提是 OpenXR hand tracking 已启用）。此插件本身不暴露额外的蓝图 API。

## C++ 用法

此插件是一个纯 OpenXR 扩展插件，没有暴露公共 C++ API。它的功能完全在运行时内部自动工作——只要插件被启用且目标设备支持该扩展，手部追踪输入就会自动被映射到注册的按键上。

如果你需要在 C++ 中读取这些输入，可以通过标准的 UE5 输入系统查询已注册的键名：

### 头文件引入

```cpp
#include "InputCoreTypes.h"
```

### 读取手部交互输入

```cpp
// 插件注册的键名（来自源码定义）
// "OpenXRMsftHandInteraction_Left_Select_Axis"   - 左手 Select（捏合）
// "OpenXRMsftHandInteraction_Right_Select_Axis"  - 右手 Select（捏合）
// "OpenXRMsftHandInteraction_Left_Grip_Axis"     - 左手 Grip（握拳）
// "OpenXRMsftHandInteraction_Right_Grip_Axis"    - 右手 Grip（握拳）

FKey LeftSelectKey("OpenXRMsftHandInteraction_Left_Select_Axis");
if (LeftSelectKey.IsValid())
{
    float Value = PlayerInput->GetKeyValue(LeftSelectKey);
    // Value 为 0.0 ~ 1.0 的轴值
}
```

### 理解插件架构

这个插件是编写 OpenXR 扩展插件的极简范例。整个插件只有一个类 `FOpenXRMsftHandInteraction`，同时实现了两个接口：

- `IModuleInterface` — 标准的 UE5 模块接口
- `IOpenXRExtensionPlugin` — OpenXR 扩展插件接口

关键的两个虚函数：

```cpp
// 告诉 OpenXR 运行时我们需要这个扩展
virtual bool GetRequiredExtensions(TArray<const ANSICHAR*>& OutExtensions) override;

// 注册 Interaction Profile，让 UE5 输入系统知道这些按键
virtual bool GetInteractionProfiles(XrInstance InInstance, 
    TArray<FString>& OutKeyPrefixes, 
    TArray<XrPath>& OutPaths, 
    TArray<bool>& OutHasHaptics) override;
```

## Demo 示例

以下是如何创建一个类似的最简 OpenXR 扩展插件的骨架：

```cpp
// MyOpenXRExtension.h
#pragma once
#include "IOpenXRExtensionPlugin.h"
#include "Modules/ModuleInterface.h"

class FMyOpenXRExtension : public IModuleInterface, public IOpenXRExtensionPlugin
{
public:
    virtual void StartupModule() override;
    virtual FString GetDisplayName() override { return TEXT("MyOpenXRExtension"); }
    virtual bool GetRequiredExtensions(TArray<const ANSICHAR*>& OutExtensions) override;
    virtual bool GetInteractionProfiles(XrInstance InInstance, 
        TArray<FString>& OutKeyPrefixes, 
        TArray<XrPath>& OutPaths, 
        TArray<bool>& OutHasHaptics) override;
};
```

```cpp
// MyOpenXRExtension.cpp
#include "MyOpenXRExtension.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FMyOpenXRExtension, MyOpenXRExtension);

void FMyOpenXRExtension::StartupModule()
{
    RegisterOpenXRExtensionModularFeature();
    // 注册自定义输入键...
}

bool FMyOpenXRExtension::GetRequiredExtensions(TArray<const ANSICHAR*>& OutExtensions)
{
    OutExtensions.Add("XR_YOUR_EXTENSION_NAME");
    return true;
}
```

### Build.cs 依赖

```csharp
PrivateDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "OpenXRHMD",
    "InputCore",
});
AddEngineThirdPartyPrivateStaticDependencies(Target, "OpenXR");
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE5 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（GEngine 等） |
| `OpenXRHMD` | OpenXR HMD 运行时模块，提供 `IOpenXRExtensionPlugin` 接口 |
| `InputCore` | 输入系统核心，提供 `EKeys` 和 `FKey` 支持 |
| `OpenXR` (ThirdParty) | OpenXR SDK 头文件和库 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-21 | `82674f19` | Use openxr.h define rather than hard coding extension names | 代码质量改进：用 SDK 头文件中的宏替代硬编码字符串，减少维护负担 |
| 2024-08-01 | `0ba65eae` | One extension plugin adds multiple interaction profiles | 架构改进：`IOpenXRExtensionPlugin` 接口支持多 Interaction Profile，旧接口标记为 deprecated |
| 2022-10-21 | `610c4676` | Update vendor links to use secure protocol | 维护性修改：链接从 http 改为 https |

### 维护评价

- **创建时间**：2020 年 9 月，约 5.6 年历史
- **最近更新**：2025 年 7 月有实质性代码改进，属于**活跃维护**状态
- **代码规模**：极小（1 个 .h + 1 个 .cpp），逻辑简单稳定，不需要频繁更新
- **风险评估**：插件依赖 `IOpenXRExtensionPlugin` 接口，2024 年的接口变更说明该接口仍在演进中，但向后兼容
- **推荐使用**：✅ 如果你的目标平台支持 `XR_MSFT_hand_interaction` 扩展（如 HoloLens 2），这是官方推荐的手部交互方式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXRMsftHandInteraction)
- [XR_MSFT_hand_interaction 扩展规范](https://registry.khronos.org/OpenXR/specs/1.0/html/xrspec.html#XR_MSFT_hand_interaction)

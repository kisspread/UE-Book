# OpenXR

> OpenXR is an open VR/AR standard（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | OpenXR 运行时 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（控制器模型资产） |
| 模块 | `OpenXRHMD` (Runtime), `OpenXRInput` (Runtime), `OpenXRAR` (Runtime), `OpenXREditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-04-16 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR) | |

## 用途

OpenXR 插件为 Unreal Engine 提供基于 [Khronos OpenXR 标准](https://www.khronos.org/openxr/) 的 VR/AR 运行时支持。它解决了**VR/AR 设备碎片化**的核心问题——开发者无需针对 Oculus、SteamVR、WMR 等每个平台单独适配，只需对接 OpenXR 一套 API，即可在所有支持 OpenXR 的头显和运行时上运行。

插件的核心职责包括：
- **HMD 驱动**：通过 OpenXR API 管理 XR Session 生命周期（创建、激活、暂停、销毁）、帧同步（WaitFrame/BeginFrame/EndFrame）、视图定位、渲染目标交换链管理
- **立体渲染**：管理左右眼渲染目标（Swapchain）、视锥计算、像素密度调整、隐藏区域/可见区域网格
- **立体层（Stereo Layers）**：支持 Quad、Cylinder、Equirect、Cubemap 等多种合成层类型，以及深度合成、运动矢量、面部锁定层模拟
- **输入系统集成**：通过 `OpenXRInput` 模块对接 OpenXR Action 系统，与 UE 的 EnhancedInput 系统联动
- **AR 支持**：通过 `OpenXRAR` 模块提供透视（Passthrough）、锚点、相机捕获等 AR 功能
- **扩展机制**：通过 `IOpenXRExtensionPlugin` 接口允许第三方插件注册自定义 OpenXR 扩展（如手部追踪、眼动追踪、空间锚点等）
- **渲染桥接**：为 D3D11、D3D12、Vulkan、OpenGL、OpenGL ES 提供图形 API 绑定

需要注意：此插件**默认未启用**（`EnabledByDefault: false`），需手动在项目设置中启用。它依赖 `XRBase` 和 `EnhancedInput` 插件。

## 使用场景

- 你在开发 VR 游戏，需要支持多种头显（Quest、Vive、Index、WMR 等）→ 启用 OpenXR 插件作为统一的 XR 运行时
- 你在开发 MR/AR 应用，需要透视（Passthrough）效果 → 使用 OpenXR 的环境混合模式切换
- 你需要自定义控制器交互或添加眼动追踪功能 → 通过 `IOpenXRExtensionPlugin` 接口编写扩展插件
- 你需要在运行时切换 AR/VR 模式 → 使用 `SetEnvironmentBlendMode` 动态切换不透明/叠加/透明混合模式
- 你需要在 AR 场景中放置世界锚点（World Anchor） → 通过 `IOpenXRCustomAnchorSupport` 接口管理空间锚点
- 你的游戏需要支持固定注视点渲染（Foveated Rendering）以提升性能 → 启用 `XR_FB_foveation` 扩展

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Environment Blend Mode` | 设置 OpenXR 环境混合模式（不透明/叠加/透明） | `UOpenXRBlueprintFunctionLibrary` |
| `Get Environment Blend Mode` | 获取当前使用的环境混合模式 | `UOpenXRBlueprintFunctionLibrary` |
| `Get Supported Environment Blend Modes` | 获取运行时支持的环境混合模式列表（按优先级排序） | `UOpenXRBlueprintFunctionLibrary` |
| `Is Composition Layer Inverted Alpha Enabled` | 查询是否启用了合成层 alpha 反转 | `UOpenXRBlueprintFunctionLibrary` |

### 使用示例（蓝图描述）

**启用透视（Passthrough）效果：**
1. 调用 `Get Supported Environment Blend Modes` 获取支持的模式列表
2. 检查列表中是否包含 `AlphaBlend`
3. 如果支持，调用 `Set Environment Blend Mode` 设置为 `AlphaBlend`
4. 在项目的渲染设置中将背景色 alpha 设为 0，即可实现透视效果

**创建基本 VR 场景（纯 C++ 端）：**
蓝图本身不需要额外节点来启动 VR——启用 OpenXR 插件后，引擎会自动检测 HMD 并启用立体渲染。蓝图中可使用标准的 `UHeadMountedDisplayFunctionLibrary` 函数获取头部追踪数据。

## C++ 用法

### 头文件引入

```cpp
// 核心 OpenXR 接口
#include "IOpenXRHMD.h"
#include "IOpenXRHMDModule.h"

// OpenXR 标准类型和工具函数
#include "OpenXRCore.h"

// 扩展插件接口
#include "IOpenXRExtensionPlugin.h"

// 蓝图函数库
#include "OpenXRBlueprintFunctionLibrary.h"

// 插件设置
#include "OpenXRHMDSettings.h"
```

### 基本用法

**检查 OpenXR 是否可用并获取实例：**

```cpp
// 来源：Public/IOpenXRHMDModule.h
if (IOpenXRHMDModule::IsAvailable())
{
    IOpenXRHMDModule& OpenXRModule = IOpenXRHMDModule::Get();
    
    // 查询扩展是否可用/已启用
    bool bVulkanEnabled = OpenXRModule.IsExtensionEnabled(TEXT("XR_KHR_vulkan_enable2"));
    
    // 获取 XR 实例和系统 ID
    XrInstance Instance = OpenXRModule.GetInstance();
    XrSystemId SystemId = OpenXRModule.GetSystemId();
}
```

**获取 HMD 运行时接口（IOpenXRHMD）：**

```cpp
// 来源：Public/IOpenXRHMD.h
// 通过 XR 跟踪系统获取 IOpenXRHMD
if (GEngine && GEngine->XRSystem.IsValid())
{
    IXRTrackingSystem* XRSystem = GEngine->XRSystem.Get();
    IOpenXRHMD* OpenXRHMD = static_cast<IOpenXRHMD*>(XRSystem);
    
    if (OpenXRHMD && OpenXRHMD->IsInitialized())
    {
        XrSession Session = OpenXRHMD->GetSession();
        XrSpace TrackingSpace = OpenXRHMD->GetTrackingSpace();
        XrTime DisplayTime = OpenXRHMD->GetDisplayTime();
    }
}
```

**XrResult 错误检查宏：**

```cpp
// 来源：Public/OpenXRCore.h
// XR_ENSURE 宏：在 Debug 构建中自动调用 ensureMsgf 记录错误
XrPath Path;
if (XR_ENSURE(xrStringToPath(Instance, "/user/hand/left", &Path)))
{
    // 路径创建成功
}

// 手动保存结果供后续使用
XrResult Result = XR_ERROR_VALIDATION_FAILURE;
if (XR_ENSURE(Result = xrCreateSession(Instance, &CreateInfo, &Session)))
{
    // Session 创建成功
}
```

### 进阶用法

**XrPath 与 FName 的高效转换：**

```cpp
// 来源：Public/OpenXRCore.h - FOpenXRPath
// FOpenXRPath 提供高效的路径转换和操作
FOpenXRPath LeftHandPath(TEXT("/user/hand/left"));
FOpenXRPath ButtonPath = LeftHandPath / TEXT("input/trigger/value");

// 转换为 FName（内部缓存，避免重复查询）
FName PathName = LeftHandPath.ToName();

// 通过模块接口解析路径
if (IOpenXRHMDModule::IsAvailable())
{
    FName ResolvedName = IOpenXRHMDModule::Get().ResolvePathToName(XrPathHandle);
    XrPath ResolvedPath = IOpenXRHMDModule::Get().ResolveNameToPath(SomeFName);
}
```

**坐标系转换（OpenXR ↔ Unreal）：**

```cpp
// 来源：Public/OpenXRCore.h - 内联转换函数
// OpenXR 使用右手坐标系 (X=右, Y=上, Z=后)
// Unreal 使用左手坐标系 (X=前, Y=右, Z=上)

XrPosef XrPose = ...;
FTransform UeTransform = ToFTransform(XrPose, 100.0f); // 100 = WorldToMeters

XrQuaternionf XrQuat = ...;
FQuat UeQuat = ToFQuat(XrQuat);

FVector UePosition = ...;
XrVector3f XrPos = ToXrVector(UePosition, 100.0f);

// 时间转换（XrTime 是纳秒，FTimespan 是 100 纳秒）
XrTime XrTimestamp = ...;
FTimespan UeTime = ToFTimespan(XrTimestamp);
XrTime BackToXr = ToXrTime(UeTime);
```

**编写 OpenXR 扩展插件：**

```cpp
// 来源：Public/IOpenXRExtensionPlugin.h
// 步骤 1：实现 IOpenXRExtensionPlugin 接口
class FMyOpenXRExtension : public IOpenXRExtensionPlugin
{
public:
    virtual FString GetDisplayName() override
    {
        return TEXT("MyCustomExtension");
    }

    // 声明需要的 OpenXR 扩展
    virtual bool GetRequiredExtensions(TArray<const ANSICHAR*>& OutExtensions) override
    {
        OutExtensions.Add("XR_EPIC_my_custom_extension");
        return true;
    }

    // 在创建 Instance 时注入链式结构
    virtual const void* OnCreateInstance(IOpenXRHMDModule* InModule, const void* InNext) override
    {
        // 创建自定义结构体并链接到 next 链
        static XrMyCustomStructEPIC CustomStruct = {};
        CustomStruct.type = XR_TYPE_MY_CUSTOM_STRUCT_EPIC;
        CustomStruct.next = InNext;
        return &CustomStruct;
    }

    // 处理自定义事件
    virtual void OnEvent(XrSession InSession, const XrEventDataBaseHeader* InHeader) override
    {
        if (InHeader->type == XR_TYPE_EVENT_DATA_MY_CUSTOM_EPIC)
        {
            // 处理自定义事件
        }
    }

    // 提供自定义控制器模型
    virtual bool GetControllerModel(XrInstance InInstance, XrPath InInteractionProfile,
        XrPath InDevicePath, FSoftObjectPath& OutPath) override
    {
        if (/* 这是我们的控制器 */)
        {
            OutPath = FSoftObjectPath(TEXT("/MyPlugin/Meshes/MyController.MyController"));
            return true;
        }
        return false;
    }
};

// 步骤 2：在模块启动时注册
class FMyOpenXRExtensionModule : public IModuleInterface
{
    FMyOpenXRExtension Extension;
    
    virtual void StartupModule() override
    {
        Extension.RegisterOpenXRExtensionModularFeature();
    }
    
    virtual void ShutdownModule() override
    {
        Extension.UnregisterOpenXRExtensionModularFeature();
    }
};
```

**链式结构体管理（扩展功能注入）：**

```cpp
// 来源：Public/IOpenXRExtensionPluginDelegates.h
// 使用模板自动管理 OpenXR 链式结构体的生命周期

// 在 HMD 代码中，通过 Delegate 广播来添加链式结构
void MyExtension::OnLocateViewsAddChainStructs(XrSpaceLocation* SpaceLocation,
    FOpenXRExtensionChainStructPtrs& ChainStructPtrs)
{
    // TOpenXRExtensionChainStruct 自动将结构体链接到链头
    auto ChainStruct = MakeShared<TOpenXRExtensionChainStruct<XrSpaceVelocity>>(
        SpaceLocation, XR_TYPE_SPACE_VELOCITY);
    ChainStructPtrs.Add(ChainStruct);
    // ChainStruct 的生命周期由 ChainStructPtrs 管理，超出作用域自动析构
}
```

## Demo 示例

### 自定义 OpenXR 扩展插件（最小完整示例）

**MyOpenXRExtension.h**

```cpp
#pragma once

#include "IOpenXRExtensionPlugin.h"
#include "Modules/ModuleManager.h"

// 自定义 OpenXR 扩展插件
class FMyOpenXRExtension : public IOpenXRExtensionPlugin
{
public:
    virtual FString GetDisplayName() override
    {
        return TEXT("MyOpenXRExtension");
    }

    // 声明可选扩展
    virtual bool GetOptionalExtensions(TArray<const ANSICHAR*>& OutExtensions) override
    {
        OutExtensions.Add(XR_KHR_COMPOSITION_LAYER_DEPTH_EXTENSION_NAME);
        return true;
    }

    // Session 创建后的回调
    virtual void PostCreateSession(XrSession InSession) override
    {
        UE_LOG(LogTemp, Log, TEXT("MyOpenXRExtension: Session created successfully"));
    }

    // 注入自定义合成层
    virtual void UpdateCompositionLayers_RHIThread(
        XrSession InSession,
        TArray<XrCompositionLayerBaseHeader*>& Headers) override
    {
        // 可在此添加自定义合成层
    }

    // 获取首选交换链格式
    virtual const uint8 GetPreferredSwapchainFormat(uint8 RequestedFormat) override
    {
        // 返回 0 (PF_Unknown) 表示使用引擎默认选择
        return PF_Unknown;
    }
};

// 模块接口
class FMyOpenXRExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        Extension = MakeUnique<FMyOpenXRExtension>();
        Extension->RegisterOpenXRExtensionModularFeature();
    }

    virtual void ShutdownModule() override
    {
        if (Extension.IsValid())
        {
            Extension->UnregisterOpenXRExtensionModularFeature();
        }
    }

private:
    TUniquePtr<FMyOpenXRExtension> Extension;
};
```

**MyOpenXRExtension.Build.cs**

```csharp
using UnrealBuildTool;

public class MyOpenXRExtension : ModuleRules
{
    public MyOpenXRExtension(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "OpenXRHMD"
        });
    }
}
```

## 模块依赖

从各模块的 Build.cs 提取（排除 Core、CoreUObject、Engine、Slate、UnrealEd、EditorFramework 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | OpenXR 输入系统与 UE EnhancedInput 框架集成 |
| `InputEditor` | 编辑器中的输入配置支持 |
| `SourceControl` | 源代码管理集成（编辑器模块） |

插件级别依赖：

| 插件 | 用途 |
|---|---|
| `XRBase` | XR 基础抽象层（IXRTrackingSystem、IHeadMountedDisplay 等接口） |
| `EnhancedInput` | 增强输入系统（OpenXR Action → UE Input Key 映射） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `0421053e` | [OpenXR][Vulkan] Request TRANSFER_DST_BIT for XR render target swapchains | 修复 Vulkan 下 XR 渲染目标交换链缺少 TRANSFER_DST 标志的问题 |
| 2026-05-14 | `a57c6062` | Stereolayers with Supports Depth wobble: prevent dangling next-chain pointers in CompositionDepthTest | 修复立体层深度合成中 next 链指针悬挂问题 |
| 2026-04-30 | `da4fc827` | PR #14037: Fix no audio when xrGetAudioOutputDeviceGuidOculus returns failure | 修复 Oculus 设备获取音频输出 GUID 失败时无声音的问题 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致乱码输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的问题 |

### 维护评价

**维护状态：活跃维护 ✅**

- **创建于 2019 年**（约 7 年前），是 UE4.22 时代引入的实验性功能，现已成熟
- **近期更新活跃**：最近 1 个月内有多次实质性提交，涵盖 Vulkan 渲染修复、音频修复、深度合成修复等
- **非实验性**：`IsBetaVersion=false`，但需注意 `EnabledByDefault=false`，需手动启用
- **持续完善中**：从 commit 历史看，团队持续修复各平台（Vulkan、D3D、Oculus）的兼容性问题
- **推荐使用**：作为 Unreal Engine 官方支持的 OpenXR 实现，它是 VR/AR 开发的首选运行时，所有主流头显都支持 OpenXR 标准

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/OpenXR)
- [OpenXR 官方规范](https://www.khronos.org/openxr/)
- [OpenXR 规范文档](https://registry.khronos.org/OpenXR/specs/1.0/html/xrspec.html)
- [Unreal Engine VR 开发文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/vr-development-in-unreal-engine)
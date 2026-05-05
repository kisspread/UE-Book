# OpenXR

> OpenXR is an open VR/AR standard

| 属性 | 值 |
|---|---|
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OpenXRHMD` (Runtime), `OpenXRInput` (Runtime), `OpenXRAR` (Runtime), `OpenXREditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-04-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXR) | |

## 用途

OpenXR plugin 是 Unreal Engine 对 [OpenXR 标准](https://www.khronos.org/openxr/) 的完整实现，充当 UE5 XR 子系统与各种 VR/AR 硬件运行时（如 SteamVR、Oculus/Meta Quest、Windows Mixed Reality、Pico 等）之间的统一抽象层。

它解决的核心问题是：**XR 碎片化**。在 OpenXR 之前，每种 VR/AR 设备都需要单独的插件（如 OculusVR、SteamVR、WMR 等）。OpenXR plugin 通过实现 Khronos OpenXR 标准，让同一个 UE5 项目无需修改代码即可在所有支持 OpenXR 的设备上运行。

该 plugin 提供四大功能域：
- **HMD 管理**（OpenXRHMD）：XR 会话生命周期、立体渲染管线、帧合成、Swapchain 管理、追踪空间
- **输入系统**（OpenXRInput）：动作/动作集管理、交互配置文件绑定、控制器追踪、触觉反馈，与 Enhanced Input 深度集成
- **AR 支持**（OpenXRAR）：AR 锚点、网格追踪、平面检测、场景理解，桥接到 UE 的 AR 框架
- **编辑器支持**（OpenXREditor）：编辑器内 XR 预览和配置

## 使用场景

- 你要做一个跨平台 VR 游戏，需要支持 Quest、PC VR（SteamVR）、PSVR2 等 → 用 OpenXR，它是唯一覆盖所有主流 VR 平台的方案
- 你要做一个 AR 应用，需要平面检测、网格重建、锚点追踪 → 用 OpenXR AR 模块，通过 `UARSessionConfig` 配置
- 你要做一个 MR（混合现实）应用，需要 passthrough 功能 → 用 OpenXR 的 `EnvironmentBlendMode` 切换到 AlphaBlend/Additive 模式
- 你开发了自定义 XR 硬件，需要集成到 UE → 实现 `IOpenXRExtensionPlugin` 接口注册扩展
- 你需要高精度手部追踪 → OpenXR 支持 `XR_EXT_hand_tracking` 扩展

## 重要提示：默认未启用

该 plugin 的 `EnabledByDefault` 为 `false`。必须通过以下方式之一手动启用：
1. **编辑器**：Edit → Plugins → 搜索 "OpenXR" → 启用
2. **配置文件**：在 `DefaultEngine.ini` 中添加：
   ```ini
   [/Script/EngineSettings.GameMapsSettings]
   ```
   或通过 `.uproject` 文件的 `Plugins` 数组启用。
3. **命令行**：`-xr` 参数

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Environment Blend Mode` | 设置 OpenXR 环境混合模式（Opaque/Additive/AlphaBlend），用于 VR/AR/MR 切换 | `UOpenXRBlueprintFunctionLibrary` |
| `Get Environment Blend Mode` | 获取当前环境混合模式 | `UOpenXRBlueprintFunctionLibrary` |
| `Get Supported Environment Blend Modes` | 获取运行时支持的所有混合模式，按优先级排序 | `UOpenXRBlueprintFunctionLibrary` |
| `Is Composition Layer Inverted Alpha Enabled` | 查询是否启用了合成层 alpha 反转 | `UOpenXRBlueprintFunctionLibrary` |
| `Begin XR Session` | 使用指定的 Input Mapping Context 启动 XR 会话 | `UOpenXRInputFunctionLibrary` |
| `End XR Session` | 结束 XR 会话 | `UOpenXRInputFunctionLibrary` |

### 环境混合模式枚举（EOpenXREnvironmentBlendMode）

| 值 | 用途 |
|---|---|
| `Opaque` | 完全不透明，标准 VR 模式 |
| `Additive` | 叠加模式，将虚拟内容叠加在真实世界上（AR） |
| `AlphaBlend` | Alpha 混合模式，支持半透明 AR 渲染 |

### 使用示例（蓝图描述）

**切换到 AR Passthrough 模式：**
1. 创建一个 `BeginPlay` 事件
2. 连接到 `Get Supported Environment Blend Modes` 节点，检查设备是否支持 `AlphaBlend`
3. 如果支持，连接到 `Set Environment Blend Mode` 节点，选择 `AlphaBlend`
4. 此时渲染背景变为 passthrough，虚拟物体以半透明方式叠加

**使用 Enhanced Input 启动 XR 会话：**
1. 创建一个 `TSet` of `UInputMappingContext` 对象，包含你的 XR 输入映射
2. 调用 `Begin XR Session`，传入该集合
3. 返回 `true` 表示成功，XR 输入系统开始工作

## C++ 用法

### 头文件引入

```cpp
// HMD 核心接口
#include "IOpenXRHMD.h"
#include "IOpenXRHMDModule.h"

// 扩展插件接口
#include "IOpenXRExtensionPlugin.h"

// 蓝图函数库
#include "OpenXRBlueprintFunctionLibrary.h"

// 输入
#include "OpenXRInputFunctionLibrary.h"

// 核心工具（类型转换、XrPath 包装等）
#include "OpenXRCore.h"

// 设置
#include "OpenXRHMDSettings.h"
```

### 基本用法：获取 OpenXR HMD 实例

```cpp
// 通过 XRTrackingSystem 获取 IOpenXRHMD 接口
IXRTrackingSystem* TrackingSystem = GEngine->XRSystem.Get();
if (TrackingSystem)
{
    IOpenXRHMD* OpenXRHMD = TrackingSystem->GetIOpenXRHMD();
    if (OpenXRHMD && OpenXRHMD->IsInitialized())
    {
        // 获取底层 OpenXR 句柄
        XrInstance Instance = OpenXRHMD->GetInstance();
        XrSystemId System = OpenXRHMD->GetSystem();
        XrSession Session = OpenXRHMD->GetSession();
        
        // 查询扩展是否启用
        bool bHandTracking = OpenXRHMD->IsExtensionEnabled(TEXT("XR_EXT_hand_tracking"));
        
        // 获取当前环境混合模式
        XrEnvironmentBlendMode BlendMode = OpenXRHMD->GetEnvironmentBlendMode();
    }
}
```

来源：`IOpenXRHMD.h`，`OpenXRHMD.h`

### 基本用法：查询模块可用性

```cpp
// 检查 OpenXRHMD 模块是否已加载
if (IOpenXRHMDModule::IsAvailable())
{
    IOpenXRHMDModule& Module = IOpenXRHMDModule::Get();
    
    // 查询扩展可用性和启用状态
    bool bAvailable = Module.IsExtensionAvailable(TEXT("XR_KHR_composition_layer_depth"));
    bool bEnabled = Module.IsExtensionEnabled(TEXT("XR_KHR_composition_layer_depth"));
    
    // 查询 API Layer
    bool bLayerAvailable = Module.IsLayerAvailable(TEXT("XR_APILAYER_LUNARG_core_validation"));
    
    // 获取 XrInstance 和 XrSystemId
    XrInstance Instance = Module.GetInstance();
    XrSystemId SystemId = Module.GetSystemId();
}
```

来源：`IOpenXRHMDModule.h`

### 进阶用法：实现自定义 OpenXR 扩展插件

`IOpenXRExtensionPlugin` 是 OpenXR plugin 最强大的扩展点。通过实现此接口，你可以：
- 注册自定义 OpenXR 扩展
- 在 XR 生命周期的各个阶段注入代码
- 添加自定义交互配置文件和控制器绑定
- 提供自定义 AR 锚点和捕获支持

```cpp
// MyOpenXRExtension.h
#pragma once
#include "IOpenXRExtensionPlugin.h"

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
        OutExtensions.Add("XR_MY_custom_extension");
        return true;
    }

    // 在创建 XrInstance 时注入链式结构
    virtual const void* OnCreateInstance(IOpenXRHMDModule* InModule, const void* InNext) override
    {
        // 可以在 XrInstanceCreateInfo 的 next 链中添加自定义结构
        return InNext;
    }

    // 在创建 XrSession 时注入
    virtual const void* OnCreateSession(XrInstance InInstance, XrSystemId InSystem, const void* InNext) override
    {
        return InNext;
    }

    // 处理 OpenXR 事件
    virtual void OnEvent(XrSession InSession, const XrEventDataBaseHeader* InHeader) override
    {
        // 处理自定义事件类型
    }

    // 添加自定义合成层
    virtual void UpdateCompositionLayers_RHIThread(XrSession InSession, TArray<XrCompositionLayerBaseHeader*>& Headers) override
    {
        // 添加自定义合成层到帧提交
    }
};
```

注册扩展插件（在模块的 StartupModule 中）：

```cpp
// MyModule.cpp
void FMyModule::StartupModule()
{
    // 必须在 PostConfigInit 或更早的 LoadingPhase 注册
    ExtensionPlugin = MakeShared<FMyOpenXRExtension>();
    ExtensionPlugin->RegisterOpenXRExtensionModularFeature();
}

void FMyModule::ShutdownModule()
{
    if (ExtensionPlugin.IsValid())
    {
        ExtensionPlugin->UnregisterOpenXRExtensionModularFeature();
    }
}
```

来源：`IOpenXRExtensionPlugin.h`

### 进阶用法：坐标系转换工具

`OpenXRCore.h` 提供了一组内联函数用于在 OpenXR 和 UE 坐标系之间转换：

```cpp
#include "OpenXRCore.h"

// OpenXR 使用右手坐标系：X=右, Y=上, Z=后
// UE 使用左手坐标系：X=前, Y=右, Z=上

// 四元数转换
XrQuaternionf XrQuat = ...;
FQuat UEQuat = ToFQuat(XrQuat);

// 向量转换（带缩放，默认 1.0）
XrVector3f XrPos = ...;
FVector UEPos = ToFVector(XrPos, 100.0f); // 世界单位缩放

// 变换转换
XrPosef XrPose = ...;
FTransform UETransform = ToFTransform(XrPose, 100.0f);

// 反向转换
FQuat MyQuat = FQuat::Identity;
XrQuaternionf OutQuat = ToXrQuat(MyQuat);

// XrPath 包装器
FOpenXRPath Path(TEXT("/user/hand/left"));
FString PathString = Path.ToString();
FName PathName = Path.ToName();
XrPath RawPath = Path.ToXRPath();

// 路径拼接
FOpenXRPath FullPath = FOpenXRPath("/user/hand/left") / "input/select/click";
```

来源：`OpenXRCore.h`

### 进阶用法：扩展链结构管理

```cpp
#include "OpenXRCore.h"
#include "IOpenXRExtensionPluginDelegates.h"

// 使用 OpenXR 命名空间的链式结构工具
void* Head = &someXrStruct;

// 查找链中特定类型的结构
XrSpaceVelocity* Velocity = OpenXR::FindChainedStructByType<XrSpaceVelocity>(
    Head, XR_TYPE_SPACE_VELOCITY);

// 追加新结构到链尾
XrSpaceVelocity NewVelocity{XR_TYPE_SPACE_VELOCITY};
OpenXR::AppendChainStruct(Head, &NewVelocity);

// 使用 RAII 链结构管理（推荐在 delegate 中使用）
FOpenXRExtensionChainStructPtrs ScopedChainStructs;
ScopedChainStructs.Add(
    MakeShared<TOpenXRExtensionChainStruct<XrSpaceVelocity>>(Head, XR_TYPE_SPACE_VELOCITY)
);
```

来源：`OpenXRCore.h`，`IOpenXRExtensionPluginDelegates.h`

## Demo 示例

### 最小 AR Passthrough 示例

```cpp
// MyARPassthroughActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyARPassthroughActor.generated.h"

UCLASS()
class AMyARPassthroughActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    
    UFUNCTION(BlueprintCallable)
    bool EnablePassthrough();
    
    UFUNCTION(BlueprintCallable)
    bool DisablePassthrough();
};
```

```cpp
// MyARPassthroughActor.cpp
#include "MyARPassthroughActor.h"
#include "OpenXRBlueprintFunctionLibrary.h"

void AMyARPassthroughActor::BeginPlay()
{
    Super::BeginPlay();
    EnablePassthrough();
}

bool AMyARPassthroughActor::EnablePassthrough()
{
    // 检查是否支持 AlphaBlend 模式
    TArray<EOpenXREnvironmentBlendMode> SupportedModes = 
        UOpenXRBlueprintFunctionLibrary::GetSupportedEnvironmentBlendModes();
    
    if (SupportedModes.Contains(EOpenXREnvironmentBlendMode::AlphaBlend))
    {
        UOpenXRBlueprintFunctionLibrary::SetEnvironmentBlendMode(
            EOpenXREnvironmentBlendMode::AlphaBlend);
        return true;
    }
    else if (SupportedModes.Contains(EOpenXREnvironmentBlendMode::Additive))
    {
        UOpenXRBlueprintFunctionLibrary::SetEnvironmentBlendMode(
            EOpenXREnvironmentBlendMode::Additive);
        return true;
    }
    
    UE_LOG(LogTemp, Warning, TEXT("Passthrough not supported on this device"));
    return false;
}

bool AMyARPassthroughActor::DisablePassthrough()
{
    UOpenXRBlueprintFunctionLibrary::SetEnvironmentBlendMode(
        EOpenXREnvironmentBlendMode::Opaque);
    return true;
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "OpenXRHMD"  // 蓝图函数库所在模块
});
```

### 自定义 OpenXR 扩展插件完整示例

```cpp
// MyOpenXRExtensionModule.h
#pragma once
#include "Modules/ModuleInterface.h"
#include "IOpenXRExtensionPlugin.h"

class FMyExtensionPlugin : public IOpenXRExtensionPlugin
{
public:
    virtual FString GetDisplayName() override { return TEXT("MyExtension"); }
    virtual bool GetOptionalExtensions(TArray<const ANSICHAR*>& OutExtensions) override
    {
        OutExtensions.Add("XR_EXT_hand_tracking");
        return true;
    }
    virtual void OnEvent(XrSession InSession, const XrEventDataBaseHeader* InHeader) override;
};

class FMyOpenXRExtensionModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<FMyExtensionPlugin> ExtensionPlugin;
};
```

```cpp
// MyOpenXRExtensionModule.cpp
#include "MyOpenXRExtensionModule.h"

void FMyExtensionPlugin::OnEvent(XrSession InSession, const XrEventDataBaseHeader* InHeader)
{
    // 处理自定义 OpenXR 事件
}

void FMyOpenXRExtensionModule::StartupModule()
{
    ExtensionPlugin = MakeShared<FMyExtensionPlugin>();
    ExtensionPlugin->RegisterOpenXRExtensionModularFeature();
}

void FMyOpenXRExtensionModule::ShutdownModule()
{
    if (ExtensionPlugin.IsValid())
    {
        ExtensionPlugin->UnregisterOpenXRExtensionModularFeature();
    }
}

IMPLEMENT_MODULE(FMyOpenXRExtensionModule, MyOpenXRExtension)
```

**Build.cs：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "OpenXRHMD"  // 提供 IOpenXRExtensionPlugin 接口
});

// LoadingPhase 必须是 PostConfigInit 或更早
// 在 .uplugin 中设置: "LoadingPhase": "PostConfigInit"
```

## 模块依赖

### 自身模块关系

| 模块 | 说明 | 依赖关系 |
|---|---|---|
| `OpenXRHMD` | 核心 HMD 管理、渲染管线、会话生命周期 | 基础模块，其他模块依赖它 |
| `OpenXRInput` | 输入系统、动作管理、控制器追踪 | 依赖 OpenXRHMD |
| `OpenXRAR` | AR 功能（锚点、网格、平面、场景理解） | 依赖 OpenXRHMD |
| `OpenXREditor` | 编辑器集成 | 依赖 OpenXRHMD + OpenXRInput |

### 外部依赖（使用者需要引用的模块）

| 模块 | 用途 |
|---|---|
| `OpenXRHMD` | 访问 `IOpenXRHMD`、`IOpenXRExtensionPlugin`、`OpenXRCore` 工具函数、蓝图函数库 |
| `OpenXRInput` | 访问 `IOpenXRInputPlugin`、输入函数库 |
| `OpenXRAR` | 访问 `IOpenXRARModule`、AR 系统支持 |
| `XRBase` | UE XR 基础抽象层（OpenXR plugin 自动依赖） |
| `EnhancedInput` | UE 增强输入系统（OpenXR plugin 自动依赖） |
| `HeadMountedDisplay` | UE HMD 基础接口 |
| `AugmentedReality` | UE AR 框架接口（OpenXRAR 使用） |
| `MRMesh` | MR 网格渲染（OpenXRAR 使用） |

### 平台特定依赖

| 平台 | 图形 API | 额外模块 |
|---|---|---|
| Win64 | DX11, DX12, OpenGL, Vulkan | `D3D11RHI`, `D3D12RHI`, `OpenGLDrv`, `VulkanRHI` |
| Android | OpenGL ES, Vulkan | `OpenGLDrv`, `VulkanRHI`, `OculusOpenXRLoader` |
| Linux | Vulkan | `VulkanRHI` |

## 架构概述

### 渲染管线

OpenXRHMD 实现了完整的立体渲染管线：
1. **帧同步**：`xrWaitFrame` → `xrBeginFrame` → 渲染 → `xrEndFrame`
2. **Swapchain 管理**：颜色/深度/运动向量纹理的分配和交换
3. **合成层**：支持投影层（Projection）、四边形层（Quad）、圆柱层（Cylinder）、等距柱状层（Equirect）
4. **帧合成**：支持 `XR_EXT_frame_synthesis` / `XR_FB_space_warp` 用于异步空间扭曲（ASW）
5. **Foveated Rendering**：支持 `XR_FB_foveation` 扩展

### 输入系统

OpenXRInput 与 Enhanced Input 深度集成：
- `UInputMappingContext` → `XrActionSet`
- `UInputAction` → `XrAction`
- 支持 Grip、Aim、Palm 三种姿态空间
- 自动从 Enhanced Input 配置生成 OpenXR 交互配置文件绑定
- 支持触觉反馈（Haptic Feedback）

### 扩展系统

`IOpenXRExtensionPlugin` 通过 UE 的 Modular Feature 系统注册，提供 40+ 个生命周期回调点，覆盖从实例创建到帧提交的完整流程。

## 设置项

通过 Project Settings → Plugins → OpenXR Settings 配置：

| 设置 | 说明 | 默认值 |
|---|---|---|
| Enable XR_FB_foveation extension | 启用注视点渲染（需要硬件 VRS 支持） | `false` |
| Invert scene alpha for passthrough | 反转背景层 alpha 以支持 passthrough | `false` |
| Enable OpenXR 1.0 | 启用 OpenXR 1.0 支持 | `true` |
| Enable OpenXR 1.1 | 启用 OpenXR 1.1 支持 | `true` |

来源：`OpenXRHMDSettings.h`

### 控制台变量

| CVar | 说明 | 默认值 |
|---|---|---|
| `xr.OpenXRInvertAlpha` | 反转场景 alpha（passthrough） | `0` |
| `xr.OpenXRFrameSynthesis` | 启用帧合成/空间扭曲 | `false` |
| `r.Velocity.DirectlyRenderOpenXRMotionVectors` | 直接渲染 OpenXR 运动向量 | `false` |

## 已支持的控制器模型

OpenXR plugin 内置了以下控制器的 3D 模型（通过 `FOpenXRAssetDirectory` 管理）：

- HP Reverb G2（左右）
- HTC Vive / Vive Cosmos / Vive Focus / Vive Focus Plus
- Microsoft Mixed Reality（左右）
- Oculus Go / Touch V1 / Touch V2 / Touch V3（左右）
- Pico Neo 3（左右）
- Samsung Gear VR / Odyssey（左右）
- Valve Index（左右）

来源：`OpenXRAssetDirectory.h`

## 维护状态

### 近期更新

1. `6fbfd61e` | 2025-10-01 | Update OpenXRHMD to use XR_EXT_frame_synthesis on Quest, rather than XR_FB_space_warp
   - 将 Quest 3 的帧合成从 `XR_FB_space_warp` 迁移到 `XR_EXT_frame_synthesis`，添加了 `XR_FRAME_SYNTHESIS_INFO_REQUEST_RELAXED_FRAME_INTERVAL_BIT_EXT` 标志
   - 解读：Meta 的 OpenXR 扩展正在从私有扩展（`XR_FB_*`）向 EXT/KHR 标准扩展迁移，这是活跃维护的标志

2. `0db38215` | 2025-09-23 | Update OpenXR frame synthesis/space warp CVars to be false by default
   - 将帧合成相关 CVar 默认值改为 false
   - 解读：稳定性优化，避免在不支持的设备上出现问题

3. `62e78fef` | 2025-09-23 | Add xr.PreferFBSpaceWarp CVar to control extension preference
   - 新增 CVar 控制在两个扩展都可用时优先使用哪个
   - 解读：为过渡期提供灵活性

### 维护评价

- **活跃维护** ✅：最近 6 个月内有功能性更新（2025-10-01）
- **创建时间**：2019 年，约 7 年历史，是 UE5 XR 的核心组件
- **更新频率**：高频更新，紧跟 OpenXR 标准演进和硬件厂商扩展
- **重要性**：这是 UE5 官方推荐的 XR 入口点，取代了之前的 OculusVR、SteamVR 等独立插件
- **已知限制**：`EnabledByDefault=false`，需要手动启用；部分高级功能依赖特定 OpenXR 扩展
- **推荐使用**：强烈推荐。任何新 VR/AR/MR 项目都应该使用此 plugin 作为 XR 基础

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/OpenXR)
- [OpenXR 规范](https://www.khronos.org/openxr/)
- [UE XR 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/xr-development-in-unreal-engine)

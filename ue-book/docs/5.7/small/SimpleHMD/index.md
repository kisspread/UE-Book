# SimpleHMD

> SimpleHMD is a sample of a basic stereo HMD implementation

| 属性 | 值 |
|---|---|
| 中文名 | 简易头显 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SimpleHMD` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-05-12 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SimpleHMD) | |

## 用途

SimpleHMD 是一个用于**演示基本立体头戴显示器（HMD）实现**的参考插件。它实现了 `IHeadMountedDisplay`、`IXRTrackingSystem`、`IStereoRendering` 和 `ISceneViewExtension` 等核心 VR 接口，但没有绑定任何真实硬件，而是通过简单的数学计算（固定视差、虚拟头部姿态）模拟双目渲染效果。主要用途包括：

- **学习 XR 插件开发**：开发者可以参照此插件快速上手自定义 HMD 的接口实现流程。
- **VR 功能原型验证**：在没有真实头显的环境下快速测试立体渲染、视图扩展等逻辑。
- **单元测试桩**：可用于依赖 HMD 接口的模块的集成测试。

## 使用场景

- 你在开发一个**自定义 VR 头显驱动程序**，需要从零实现 `IHeadMountedDisplayModule` 和 `IXRTrackingSystem` —— 直接复制 SimpleHMD 的结构并替换具体算法。
- 你需要编写**依赖 HMD 功能的单元测试**，但 CI 环境没有真实头显 —— 启用 SimpleHMD 作为测试桩。
- 你想在编辑器里**快速预览立体效果**，但手边没有 VR 设备 —— 启用 SimpleHMD 并开启立体渲染（会看到两个略微偏移的视口）。

## 蓝图用法

此插件未暴露蓝图可调用函数（`UFUNCTION(BlueprintCallable)`）。所有 VR 接口通过引擎内部的 `GEngine->XRSystem` 间接访问，蓝图中可使用的节点（如 `IsHeadMountedDisplayConnected`、`GetDevicePose` 等）由引擎的 `HeadMountedDisplay` 模块提供，不依赖于 SimpleHMD 本身。

## C++ 用法

### 头文件引入

```cpp
#include "IHeadMountedDisplayModule.h"
#include "IXRTrackingSystem.h" // 如果需访问跟踪系统
```

### 基本用法

**1. 启用/加载插件**  
SimpleHMD 默认不启用，需在 `.uproject` 或 `.uplugin` 中显式启用，或在 C++ 中动态加载模块：

```cpp
// 插件加载后可通过模块接口获取
ISimpleHMDPlugin& SimpleHMDModule = FModuleManager::LoadModuleChecked<ISimpleHMDPlugin>("SimpleHMD");
```

**2. 获取 HMD 设备实例**  
通过引擎的 XR 系统访问：

```cpp
if (GEngine && GEngine->XRSystem.IsValid())
{
    auto HMD = GEngine->XRSystem->GetHMDDevice();
    if (HMD)
    {
        // 返回 IHeadMountedDisplay 接口指针
        HMD->EnableHMD(true);
        bool bStereoEnabled = HMD->IsStereoEnabled();
    }
}
```

**3. 获取当前姿态（模拟数据）**  
`FSimpleHMD::GetCurrentPose` 返回一个固定的朝向（无旋转）和原点位置：

```cpp
if (GEngine && GEngine->XRSystem.IsValid())
{
    TArray<int32> Devices;
    GEngine->XRSystem->EnumerateTrackedDevices(Devices);
    for (int32 DeviceId : Devices)
    {
        FQuat Orientation;
        FVector Position;
        if (GEngine->XRSystem->GetCurrentPose(DeviceId, Orientation, Position))
        {
            // Orientation 为恒等四元数，Position 为零向量
        }
    }
}
```

**4. 设置/获取瞳距（IPD）**  

```cpp
auto HMD = GEngine->XRSystem->GetHMDDevice();
if (HMD)
{
    HMD->SetInterpupillaryDistance(0.064f); // 设置为 64mm
    float IPD = HMD->GetInterpupillaryDistance();
}
```

**5. 重置方向与位置**  

```cpp
// 重置方向（保持当前偏航角不变）
HMD->ResetOrientation(0.f);
// 重置位置
HMD->ResetPosition();
// 同时重置
HMD->ResetOrientationAndPosition(0.f);
```

### 进阶用法

**实现自定义场景视图扩展**  
SimpleHMD 同时继承 `FHMDSceneViewExtension`，可以通过它修改渲染流程。例如禁用后期处理：

```cpp
// 在 ISceneViewExtension::PostRenderViewFamily 中
void FSimpleHMD::PostRenderViewFamily_RenderThread(FRDGBuilder& GraphBuilder, FSceneViewFamily& ViewFamily)
{
    // 可以在这里插入自定义渲染 Pass
}
```

更多视图扩展接口可参考 `ISceneViewExtension` 的纯虚方法，SimpleHMD 已提供默认实现。

## Demo 示例

以下是一个最小 C++ 示例，演示在游戏模块中检测并使用 SimpleHMD。

**MyHMDTest.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyHMDTestModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyHMDTest.cpp**

```cpp
#include "MyHMDTest.h"
#include "IHeadMountedDisplay.h"
#include "IXRTrackingSystem.h"
#include "Engine/Engine.h"

IMPLEMENT_MODULE(FMyHMDTestModule, MyHMDTest)

void FMyHMDTestModule::StartupModule()
{
    // 确保 SimpleHMD 已加载（可以在项目插件中启用）
    if (GEngine && GEngine->XRSystem.IsValid())
    {
        auto XR = GEngine->XRSystem;
        FName SystemName = XR->GetSystemName();
        UE_LOG(LogTemp, Log, TEXT("Current XR system: %s"), *SystemName.ToString());

        // 检查是否为 SimpleHMD
        if (SystemName == "SimpleHMD")
        {
            auto HMD = XR->GetHMDDevice();
            if (HMD)
            {
                UE_LOG(LogTemp, Log, TEXT("SimpleHMD is active. IPD: %f"), HMD->GetInterpupillaryDistance());
                // 启用立体渲染
                HMD->EnableStereo(true);
            }
        }
    }
}

void FMyHMDTestModule::ShutdownModule()
{
}
```

**模块依赖**在 `MyHMDTest.Build.cs` 中需包含：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "HeadMountedDisplay",   // 提供 IHeadMountedDisplay 接口
    "XRBase",               // SimpleHMD 依赖 XRBase
    // "SimpleHMD" 可选：若需要直接访问插件接口则添加
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `XRBase` | 提供 XR 系统基础框架（`IXRTrackingSystem`、`FHeadMountedDisplayBase` 等） |

无其他特殊依赖。

## 维护状态

### 近期更新

- 2025-01-21 `42de2ffc` Merging RHI CreateBuffer refactor to Main.
- 2024-11-25 `af0eb101` Removed pure virtual requirement for scene extension methods
- 2023-11-14 `ff336238` OpenXRVisionOS non-plugin support files
- 2023-06-22 `aa1b0c68` Deprecated non-command list RHI methods.
- 2023-05-12 `2907946c` Remove platform

### 维护评价

- **创建时间**：2023-05-12，至今约 2 年。
- **更新频率**：最近实质性更新（移除纯虚方法要求）在 2024-11-25，之后无功能修改。整体更新不频繁，但跟随引擎主线 RHI 重构进行了编译兼容性维护。
- **活跃度**：非活跃维护，仅为引擎基础变更适配。
- **推荐度**：👍 **推荐** —— 作为学习和示例插件非常有用；生产环境建议使用成熟的 XR 插件（如 OpenXR）。

**注意**：SimpleHMD 处于 Experimental 目录，未启用 `IsBetaVersion`，但引擎不保证其稳定性和长期支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SimpleHMD)
- 官方文档：无
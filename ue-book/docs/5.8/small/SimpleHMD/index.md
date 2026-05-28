# SimpleHMD

> SimpleHMD is a sample of a basic stereo HMD implementation

| 属性 | 值 |
|---|---|
| 中文名 | 简单头戴显示器 |
| 分类 | Virtual Reality |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SimpleHMD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2014-12-06 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SimpleHMD) | |

## 用途

SimpleHMD 是一个**最小化的立体 HMD（头戴显示器）参考实现**，用作开发新 HMD 集成的起点。它演示了 UE5 XR 系统中 HMD 设备需要实现的所有核心接口，包括：

- 立体渲染管线的初始化与控制
- 头部追踪姿态的模拟（固定值）
- 瞳距（IPD）配置
- 畸变网格渲染（测试用）
- 场景视图的左右眼偏移与投影矩阵计算

这个插件本身**不连接任何真实硬件**，所有追踪数据都是模拟值，纯粹作为代码模板供 VR 设备开发者参考。

## 使用场景

- 你在开发自定义 VR 头显驱动程序 → 以此为起点实现 IXRTrackingSystem
- 你想了解 UE5 的 XR 设备集成流程 → 阅读此插件的源码
- 你需要一个无硬件依赖的立体渲染测试环境 → 启用此插件验证立体渲染管线
- 你在学习 IHeadMountedDisplay 和 IStereoRendering 接口 → 这是最简实现参考

## 蓝图用法

SimpleHMD 是纯 C++ 运行时模块，**不暴露任何蓝图接口**。所有功能通过引擎的 XR 子系统自动集成。

启用后，引擎会自动将 SimpleHMD 识别为可用的 HMD 设备，以下引擎蓝图节点可正常使用：

### 核心节点（引擎内置）

| 节点 | 说明 |
|---|---|
| `Enable HMD` | 启用/禁用头显设备 |
| `Get HMD Device Position and Orientation` | 获取头部位置与朝向 |
| `Reset HMD Origin` | 重置头显原点位置 |
| `Set Stereo Enabled` | 启用/禁用立体渲染模式 |

## C++ 用法

### 头文件引入

```cpp
#include "ISimpleHMDPlugin.h"
```

### 基本用法

检查模块可用性并获取插件接口：

```cpp
// 检查 SimpleHMD 模块是否已加载
if (ISimpleHMDPlugin::IsAvailable())
{
    // 获取插件单例（模块会自动注册为 HMD 设备）
    ISimpleHMDPlugin& Plugin = ISimpleHMDPlugin::Get();
    
    // 此时引擎的 XR 系统已将 SimpleHMD 识别为活动设备
    // 可通过 GEngine->XRSystem() 访问完整的 IXRTrackingSystem 接口
}
```

### 进阶用法

通过引擎 XR 系统与 SimpleHMD 交互：

```cpp
#include "XRTrackingSystemBase.h"
#include "HeadMountedDisplayFunctionLibrary.h"

// 确保 XR 系统已初始化
if (GEngine && GEngine->XRSystem.IsValid())
{
    IXRTrackingSystem* XRSystem = GEngine->XRSystem.Get();
    
    // 获取系统名称验证是 SimpleHMD
    FName SystemName = XRSystem->GetSystemName();
    UE_LOG(LogTemp, Log, TEXT("XR System: %s"), *SystemName.ToString());
    
    // 枚举已连接的追踪设备
    TArray<int32> TrackedDevices;
    XRSystem->EnumerateTrackedDevices(TrackedDevices, EXRTrackedDeviceType::HeadMountedDisplay);
    
    // 获取头部姿态
    FQuat Orientation;
    FVector Position;
    if (XRSystem->GetCurrentPose(0, Orientation, Position))
    {
        UE_LOG(LogTemp, Log, TEXT("HMD Orientation: %s"), *Orientation.ToString());
        UE_LOG(LogTemp, Log, TEXT("HMD Position: %s"), *Position.ToString());
    }
    
    // 配置瞳距
    IHeadMountedDisplay* HMD = XRSystem->GetHMDDevice();
    if (HMD)
    {
        HMD->SetInterpupillaryDistance(0.064f); // 64mm
        
        // 获取当前视场角
        float HFOV, VFOV;
        HMD->GetFieldOfView(HFOV, VFOV);
        UE_LOG(LogTemp, Log, TEXT("FOV: H=%f V=%f"), HFOV, VFOV);
    }
    
    // 启用立体渲染
    TSharedPtr<IStereoRendering> StereoRendering = XRSystem->GetStereoRenderingDevice();
    if (StereoRendering.IsValid())
    {
        StereoRendering->EnableStereo(true);
    }
}
```

## Demo 示例

实现一个自定义 HMD（基于 SimpleHMD 的模式）：

```cpp
// MyCustomHMD.h
#pragma once

#include "HeadMountedDisplayBase.h"
#include "SceneViewExtension.h"

class FMyCustomHMD : public FHeadMountedDisplayBase, public FHMDSceneViewExtension
{
public:
    FMyCustomHMD(const FAutoRegister& AutoRegister);
    virtual ~FMyCustomHMD();
    
    // IXRTrackingSystem
    virtual FName GetSystemName() const override
    {
        static FName Name(TEXT("MyCustomHMD"));
        return Name;
    }
    
    virtual bool EnumerateTrackedDevices(TArray<int32>& OutDevices, 
        EXRTrackedDeviceType Type) override;
    
    virtual bool GetCurrentPose(int32 DeviceId, 
        FQuat& CurrentOrientation, FVector& CurrentPosition) override;
    
    virtual void ResetOrientationAndPosition(float Yaw = 0.f) override;
    
    // IHeadMountedDisplay
    virtual bool IsHMDConnected() override { return true; }
    virtual bool IsHMDEnabled() const override;
    virtual void EnableHMD(bool Allow = true) override;
    virtual void GetFieldOfView(float& OutHFOVInDegrees, 
        float& OutVFOVInDegrees) const override;
    virtual void SetInterpupillaryDistance(float NewIPD) override;
    virtual float GetInterpupillaryDistance() const override;
    
    // IStereoRendering
    virtual bool IsStereoEnabled() const override;
    virtual bool EnableStereo(bool Stereo = true) override;
    virtual void AdjustViewRect(int32 ViewIndex, int32& X, int32& Y, 
        uint32& SizeX, uint32& SizeY) const override;
    virtual void CalculateStereoViewOffset(const int32 ViewIndex, 
        FRotator& ViewRotation, const float InWorldToMeters, 
        FVector& ViewLocation) override;
    virtual FMatrix GetStereoProjectionMatrix(const int32 ViewIndex) const override;
    
    // FHMDSceneViewExtension
    virtual void SetupViewFamily(FSceneViewFamily& InViewFamily) override;
    virtual void SetupView(FSceneViewFamily& InViewFamily, FSceneView& InView) override;
    
    // 设备访问
    virtual class IHeadMountedDisplay* GetHMDDevice() override { return this; }
    virtual TSharedPtr<IStereoRendering, ESPMode::ThreadSafe> GetStereoRenderingDevice() override
    {
        return SharedThis(this);
    }

private:
    FQuat CurrentOrientation;
    FVector CurrentPosition;
    float IPD;
    bool bStereoEnabled;
    bool bHMDConnected;
};
```

```cpp
// MyCustomHMD.cpp
#include "MyCustomHMD.h"

FMyCustomHMD::FMyCustomHMD(const FAutoRegister& AutoRegister)
    : FHeadMountedDisplayBase()
    , FHMDSceneViewExtension()
    , CurrentOrientation(FQuat::Identity)
    , CurrentPosition(FVector::ZeroVector)
    , IPD(0.064f)  // 64mm 默认瞳距
    , bStereoEnabled(false)
    , bHMDConnected(true)
{
}

FMyCustomHMD::~FMyCustomHMD()
{
}

bool FMyCustomHMD::EnumerateTrackedDevices(TArray<int32>& OutDevices, EXRTrackedDeviceType Type)
{
    if (Type == EXRTrackedDeviceType::Any || Type == EXRTrackedDeviceType::HeadMountedDisplay)
    {
        OutDevices.Add(0); // 设备 ID 0 = HMD 本体
        return true;
    }
    return false;
}

bool FMyCustomHMD::GetCurrentPose(int32 DeviceId, FQuat& OutOrientation, FVector& OutPosition)
{
    if (DeviceId == 0)
    {
        // TODO: 从你的硬件 SDK 获取真实追踪数据
        OutOrientation = CurrentOrientation;
        OutPosition = CurrentPosition;
        return true;
    }
    return false;
}

void FMyCustomHMD::ResetOrientationAndPosition(float Yaw)
{
    CurrentOrientation = FRotator(0.f, Yaw, 0.f).Quaternion();
    CurrentPosition = FVector::ZeroVector;
}

bool FMyCustomHMD::IsHMDEnabled() const
{
    return bHMDConnected;
}

void FMyCustomHMD::EnableHMD(bool Allow)
{
    bHMDConnected = Allow;
}

void FMyCustomHMD::GetFieldOfView(float& OutHFOV, float& OutVFOV) const
{
    // TODO: 设置你的设备实际视场角
    OutHFOV = 100.0f;
    OutVFOV = 100.0f;
}

void FMyCustomHMD::SetInterpupillaryDistance(float NewIPD)
{
    IPD = NewIPD;
}

float FMyCustomHMD::GetInterpupillaryDistance() const
{
    return IPD;
}

bool FMyCustomHMD::IsStereoEnabled() const
{
    return bStereoEnabled;
}

bool FMyCustomHMD::EnableStereo(bool Stereo)
{
    bStereoEnabled = Stereo;
    return bStereoEnabled;
}

void FMyCustomHMD::AdjustViewRect(int32 ViewIndex, int32& X, int32& Y, 
    uint32& SizeX, uint32& SizeY) const
{
    // 左右眼各占一半宽度
    SizeX /= 2;
    if (ViewIndex == 1) // 右眼
    {
        X += SizeX;
    }
}

void FMyCustomHMD::CalculateStereoViewOffset(const int32 ViewIndex, 
    FRotator& ViewRotation, const float InWorldToMeters, FVector& ViewLocation)
{
    // 基于瞳距计算左右眼偏移
    const float HalfIPD = GetInterpupillaryDistance() * 0.5f * InWorldToMeters;
    const FVector EyeOffset = (ViewIndex == 0) ? 
        FVector(0, -HalfIPD, 0) : FVector(0, HalfIPD, 0);
    
    ViewLocation += ViewRotation.RotateVector(EyeOffset);
}

FMatrix FMyCustomHMD::GetStereoProjectionMatrix(const int32 ViewIndex) const
{
    // TODO: 根据你的设备光学参数计算投影矩阵
    const float HalfFOV = FMath::DegreesToRadians(50.0f);
    const float Width = 1920.0f;
    const float Height = 1080.0f;
    const float AspectRatio = (Width * 0.5f) / Height;
    
    return FReversedZPerspectiveMatrix(HalfFOV, AspectRatio, 1.0f, 100000.0f);
}

void FMyCustomHMD::SetupViewFamily(FSceneViewFamily& InViewFamily)
{
    InViewFamily.EngineShowFlags.MotionBlur = 0;
}

void FMyCustomHMD::SetupView(FSceneViewFamily& InViewFamily, FSceneView& InView)
{
    // 可在此处设置每只眼睛特有的渲染参数
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `XRBase` | XR 设备基础框架，提供 IXRTrackingSystem 等核心接口 |
| `HeadMountedDisplay` | HMD 设备基础类 FHeadMountedDisplayBase 和场景视图扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-11-14 | `e6a0fa04` | XR Crash reporting improvement | XR 崩溃报告改进，影响整体 XR 子系统 |
| 2025-01-21 | `42de2ffc` | Merging RHI CreateBuffer refactor to Main. | RHI 缓冲区创建重构合入主线 |
| 2024-11-25 | `af0eb101` | Removed pure virtual requirement for scene extension methods to reduce noise when searching for valid implementations | 移除场景扩展方法的纯虚函数要求，减少搜索实现时的噪音 |
| 2023-11-14 | `ff336238` | OpenXRVisionOS non-plugin support files | 为 VisionOS 添加 OpenXR 支持文件 |
| 2023-06-22 | `aa1b0c68` | Deprecated non-command list RHI methods. | 废弃非命令列表的 RHI 方法 |

### 维护评价

**⚠️ 实验性示例代码，不推荐用于生产环境**

- **创建时间**：2014 年 12 月，已有约 10 年历史
- **更新性质**：所有近期更新均为**被动更新**——引擎级基础设施重构（RHI、XR 基类接口变更）波及此插件，而非插件本身的功能迭代
- **最后实质性更新**：自 2014 年首次提交后，未见针对 SimpleHMD 本身的功能性更新
- **定位明确**：这是 Epic 官方提供的**代码模板**，用于指导开发者如何接入自定义 HMD 硬件
- **代码价值**：虽然代码未更新，但其展示的接口模式（IHeadMountedDisplay、IStereoRendering、FHMDSceneViewExtension）仍与当前 UE5 XR 架构兼容

**建议**：如需开发自定义 VR 设备驱动，可参考此插件的接口实现模式，但应基于最新的 FHeadMountedDisplayBase 基类进行开发，并参考 OpenXR 等现代实现获取更完整的参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SimpleHMD)
- 官方文档：无
- 测试用例：无
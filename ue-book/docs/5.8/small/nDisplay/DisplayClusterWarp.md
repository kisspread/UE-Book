# nDisplay Warp

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 视图扭曲模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（扭曲策略、数学计算、MPCDI支持、几何数据加载器、UI预览组件） |
| 模块 | `DisplayClusterWarp` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterWarp) | |

## 用途

DisplayClusterWarp 模块是 nDisplay 插件的核心组成部分，专门负责处理多显示器集群渲染中的**视图扭曲与融合**（Warp & Blend）功能。

**核心问题**：当使用多台 PC 或多个显示器创建沉浸式环境（如 CAVE、LED 墙、穹顶投影）时，每个显示器的物理位置、方向和曲率都不同。如果不进行校正，投影图像会出现几何失真、亮度不均和接缝。

**模块存在目的**：
1.  **几何校正**：将标准相机视图扭曲到符合物理屏幕几何形状（平面、曲面、任意网格）
2.  **边缘融合**：处理相邻显示器重叠区域的亮度混合，消除接缝
3.  **立体支持**：为单眼（Mono）和立体（Stereo）渲染提供正确的投影矩阵
4.  **标准格式支持**：支持行业标准的 MPCDI（Multi-Projector Common Data Interchange）校准文件格式
5.  **实时预览**：在编辑器中提供扭曲网格和融合区域的可视化预览

该模块通过加载外部校准数据（MPCDI文件、PFM文件或UE网格）来定义物理屏幕的真实几何形状，然后在渲染时实时计算每个像素的正确位置和颜色。

## 使用场景

- **CAVE虚拟现实系统**：多面投影墙环境，需要精确的几何校正和边缘融合
- **LED视频墙**：大型LED屏幕拼接显示，每个面板有独立的几何和亮度特性
- **穹顶/圆幕投影**：沉浸式穹顶影院，需要球面或柱面投影校正
- **汽车设计评审**：在物理比例的屏幕墙前进行车辆设计审查
- **飞行/驾驶模拟器**：多屏幕环绕显示器，提供连续的视野
- **舞台LED背景**：现场活动或演唱会的大型LED背景墙
- **虚拟制作（Virtual Production）**：LED Volume（如The Volume）中的屏幕校准

## 蓝图用法

### 核心组件

| 组件 | 说明 | 蓝图可创建 |
|---|---|---|
| `UDisplayClusterInFrustumFitCameraComponent` | 视锥体适配相机组件，用于计算整个屏幕组的联合视锥体 | ✅ 是 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetWarpPolicy` | 获取当前视口的扭曲策略对象 | `UDisplayClusterInFrustumFitCameraComponent` |
| `ShouldUseEntireClusterViewports` | 检查是否应使用整个集群的视口进行计算 | `UDisplayClusterInFrustumFitCameraComponent` |
| `ExportWarpMapGeometry` | 将扭曲几何导出为OBJ格式（用于调试） | `IDisplayClusterWarpBlend` |
| `ReadMPCDFileStructure` | 读取MPCDI文件的结构（缓冲区/区域信息） | `IDisplayClusterWarp` |

### 使用示例（蓝图描述）

1. **设置视锥体适配相机**：
   - 在 nDisplay 根角色（Root Actor）中添加 `InFrustumFitCameraComponent`
   - 设置 `bEnableCameraProjection = true`
   - 选择 `CameraProjectionMode`：Fit（适合几何）或 Fill（填充视锥）
   - 设置 `CameraViewTarget`：GeometricCenter（几何中心）或 MatchViewOrigin（匹配原点）

2. **读取MPCDI文件信息**：
   ```cpp
   // 获取Warp模块
   IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();
   
   // 读取MPCDI文件结构
   TMap<FString, TMap<FString, FDisplayClusterWarpMPCDIAttributes>> MPCDIFileStructure;
   WarpModule.ReadMPCDFileStructure(TEXT("Calibration.mpcdi"), MPCDIFileStructure);
   
   // 遍历结构获取缓冲区/区域信息
   for (auto& BufferPair : MPCDIFileStructure)
   {
       for (auto& RegionPair : BufferPair.Value)
       {
           // 获取特定区域的属性
           FDisplayClusterWarpMPCDIAttributes Attributes = RegionPair.Value;
           // 处理属性...
       }
   }
   ```

## C++ 用法

### 头文件引入

```cpp
// 核心模块接口
#include "IDisplayClusterWarp.h"

// 扭曲混合接口
#include "IDisplayClusterWarpBlend.h"

// 数据容器
#include "Containers/DisplayClusterWarpContainers.h"
#include "Containers/DisplayClusterWarpInitializer.h"
#include "Containers/DisplayClusterWarpEnums.h"

// 蓝图类型
#include "Blueprints/DisplayClusterWarpGeometry.h"
#include "Components/DisplayClusterInFrustumFitCameraComponent.h"
```

### 基本用法

**创建扭曲混合实例**（来源：`IDisplayClusterWarp.h`）：

```cpp
// 获取扭曲模块实例
IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();

// 1. 从MPCDI文件创建
FDisplayClusterWarpInitializer_MPCDIFile MPCDIParams;
MPCDIParams.MPCDIFileName = TEXT("Path/To/Calibration.mpcdi");
MPCDIParams.BufferId = TEXT("BufferName");
MPCDIParams.RegionId = TEXT("RegionName");

TSharedPtr<IDisplayClusterWarpBlend, ESPMode::ThreadSafe> WarpBlend = WarpModule.Create(MPCDIParams);

// 2. 从静态网格创建
FDisplayClusterWarpInitializer_StaticMesh MeshParams;
MeshParams.OriginComponent = OriginSceneComponent;
MeshParams.WarpMeshComponent = StaticMeshComponent;
MeshParams.PreviewMeshComponent = PreviewMeshComponent;
MeshParams.BaseUVIndex = 0;

TSharedPtr<IDisplayClusterWarpBlend, ESPMode::ThreadSafe> MeshWarpBlend = WarpModule.Create(MeshParams);
```

**计算视锥体**（来源：`IDisplayClusterWarpBlend.h`）：

```cpp
// 初始化场景
WarpBlend->HandleStartScene(Viewport);

// 更新几何上下文（世界缩放）
WarpBlend->UpdateGeometryContext(WorldScale);

// 创建视点数据
TSharedPtr<FDisplayClusterWarpEye> WarpEye = MakeShared<FDisplayClusterWarpEye>(Viewport, ContextNum);
WarpEye->ViewPoint.Location = CameraLocation;
WarpEye->ViewPoint.Rotation = CameraRotation;
WarpEye->ViewPoint.EyeOffset = EyeOffset; // 立体眼间距

// 计算视锥体上下文
bool bSuccess = WarpBlend->CalcFrustumContext(WarpEye);

if (bSuccess)
{
    // 获取扭曲数据
    const FDisplayClusterWarpData& WarpData = WarpBlend->GetWarpData(ContextNum);
    const FDisplayClusterWarpContext& WarpContext = WarpData.WarpContext;
    
    // 使用投影矩阵
    FMatrix ProjectionMatrix = WarpContext.ProjectionMatrix;
    FMatrix UVMatrix = WarpContext.UVMatrix;
    
    // 获取纹理资源
    FRHITexture* WarpMapTexture = WarpBlend->GetTexture(EDisplayClusterWarpBlendTextureType::WarpMap);
    FRHITexture* AlphaMapTexture = WarpBlend->GetTexture(EDisplayClusterWarpBlendTextureType::AlphaMap);
}
```

### 进阶用法

**自定义扭曲策略**（来源：`DisplayClusterWarpPolicyBase.h`）：

```cpp
// 创建自定义扭曲策略
class FMyCustomWarpPolicy : public FDisplayClusterWarpPolicyBase
{
public:
    FMyCustomWarpPolicy(const FString& InPolicyName)
        : FDisplayClusterWarpPolicyBase(TEXT("MyCustomPolicy"), InPolicyName)
    {}
    
    // 实现策略接口
    virtual void HandleNewFrame(const TArray<TSharedPtr<IDisplayClusterViewport, ESPMode::ThreadSafe>>& InViewports) override
    {
        // 自定义每帧处理逻辑
    }
    
    virtual void Tick(IDisplayClusterViewportManager* InViewportManager, float DeltaSeconds) override
    {
        // 自定义更新逻辑
    }
    
    virtual void BeginCalcFrustum(IDisplayClusterViewport* InViewport, const uint32 ContextNum) override
    {
        // 视锥体计算前的准备工作
    }
    
    virtual void EndCalcFrustum(IDisplayClusterViewport* InViewport, const uint32 ContextNum) override
    {
        // 视锥体计算后的清理工作
    }
};

// 注册策略工厂
FDisplayClusterWarpInFrustumFitPolicyFactory PolicyFactory;
// 通过工厂创建策略实例
TSharedPtr<IDisplayClusterWarpPolicy> Policy = PolicyFactory.Create(TEXT("MyCustomPolicy"), TEXT("MyPolicyInstance"));
```

**导出扭曲几何用于调试**（来源：`IDisplayClusterWarpBlend.h`）：

```cpp
// 导出扭曲几何为OBJ格式
FDisplayClusterWarpGeometryOBJ ExportedGeometry;
uint32 MaxDimension = 64; // 降低分辨率用于快速预览

if (WarpBlend->ExportWarpMapGeometry(ExportedGeometry, MaxDimension))
{
    // ExportedGeometry 包含顶点、法线、UV和三角形
    // 可以用于可视化调试或导出到其他工具
    
    // 保存为OBJ文件
    FString OBJContent;
    OBJContent += TEXT("# nDisplay Warp Geometry Export\n");
    
    for (const FVector& Vertex : ExportedGeometry.Vertices)
    {
        OBJContent += FString::Printf(TEXT("v %f %f %f\n"), Vertex.X, Vertex.Y, Vertex.Z);
    }
    
    for (const FVector2D& UV : ExportedGeometry.UV)
    {
        OBJContent += FString::Printf(TEXT("vt %f %f\n"), UV.X, UV.Y);
    }
    
    // ... 写入面数据
}
```

## Demo 示例

### 头文件：MyWarpController.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IDisplayClusterWarp.h"
#include "IDisplayClusterWarpBlend.h"
#include "MyWarpController.generated.h"

UCLASS()
class MYPROJECT_API AMyWarpController : public AActor
{
    GENERATED_BODY()
    
public:
    AMyWarpController();
    
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;
    
    UFUNCTION(BlueprintCallable, Category = "nDisplay|Warp")
    void InitializeWarpFromMPCDI(const FString& MPCDIFile, const FString& BufferId, const FString& RegionId);
    
    UFUNCTION(BlueprintCallable, Category = "nDisplay|Warp")
    void CalculateFrustumForViewport(class UDisplayClusterViewportComponent* Viewport, const FVector& EyeLocation, const FRotator& EyeRotation);
    
    UFUNCTION(BlueprintCallable, Category = "nDisplay|Warp")
    FMatrix GetProjectionMatrix() const;
    
private:
    TSharedPtr<IDisplayClusterWarpBlend, ESPMode::ThreadSafe> WarpBlend;
    
    UPROPERTY(VisibleAnywhere, Category = "Components")
    USceneComponent* OriginComponent;
    
    UPROPERTY(VisibleAnywhere, Category = "Components")
    UStaticMeshComponent* WarpMeshComponent;
    
    FDisplayClusterWarpData CurrentWarpData;
    bool bIsInitialized = false;
};
```

### 实现文件：MyWarpController.cpp

```cpp
#include "MyWarpController.h"
#include "Components/DisplayClusterViewportComponent.h"
#include "Containers/DisplayClusterWarpInitializer.h"
#include "DisplayClusterRootActor.h"

AMyWarpController::AMyWarpController()
{
    PrimaryActorTick.bCanEverTick = true;
    
    // 创建组件
    OriginComponent = CreateDefaultSubobject<USceneComponent>(TEXT("Origin"));
    RootComponent = OriginComponent;
    
    WarpMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WarpMesh"));
    WarpMeshComponent->SetupAttachment(RootComponent);
}

void AMyWarpController::BeginPlay()
{
    Super::BeginPlay();
    
    // 自动初始化（如果有MPCDI文件）
    InitializeWarpFromMPCDI(
        TEXT("Content/Calibrations/MyScreen.mpcdi"),
        TEXT("DefaultBuffer"),
        TEXT("DefaultRegion")
    );
}

void AMyWarpController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 在 Tick 中更新扭曲数据（如果需要）
    if (bIsInitialized && WarpBlend.IsValid())
    {
        WarpBlend->UpdateGeometryContext(GetWorld()->GetWorldSettings()->WorldToMeters / 100.0f);
    }
}

void AMyWarpController::InitializeWarpFromMPCDI(const FString& MPCDIFile, const FString& BufferId, const FString& RegionId)
{
    // 获取扭曲模块
    if (!IDisplayClusterWarp::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DisplayClusterWarp module not available"));
        return;
    }
    
    IDisplayClusterWarp& WarpModule = IDisplayClusterWarp::Get();
    
    // 设置初始化参数
    FDisplayClusterWarpInitializer_MPCDIFile Params;
    Params.MPCDIFileName = MPCDIFile;
    Params.BufferId = BufferId;
    Params.RegionId = RegionId;
    
    // 创建扭曲混合实例
    WarpBlend = WarpModule.Create(Params);
    
    if (WarpBlend.IsValid())
    {
        // 初始化场景
        WarpBlend->HandleStartScene(nullptr); // Viewport 可以为空
        bIsInitialized = true;
        
        UE_LOG(LogTemp, Log, TEXT("Warp blend initialized from MPCDI: %s"), *MPCDIFile);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create warp blend from MPCDI: %s"), *MPCDIFile);
    }
}

void AMyWarpController::CalculateFrustumForViewport(UDisplayClusterViewportComponent* Viewport, const FVector& EyeLocation, const FRotator& EyeRotation)
{
    if (!bIsInitialized || !WarpBlend.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Warp not initialized"));
        return;
    }
    
    // 创建视点数据
    TSharedPtr<FDisplayClusterWarpEye> WarpEye = MakeShared<FDisplayClusterWarpEye>(nullptr, 0); // Viewport 可以为空
    
    // 设置视点参数
    WarpEye->ViewPoint.Location = EyeLocation;
    WarpEye->ViewPoint.Rotation = EyeRotation;
    WarpEye->ViewPoint.EyeOffset = FVector::ZeroVector; // 单眼模式
    WarpEye->WorldScale = GetWorld()->GetWorldSettings()->WorldToMeters / 100.0f;
    
    // 计算视锥体
    bool bSuccess = WarpBlend->CalcFrustumContext(WarpEye);
    
    if (bSuccess)
    {
        // 获取扭曲数据
        CurrentWarpData = WarpBlend->GetWarpData(0); // Context 0
        
        UE_LOG(LogTemp, Log, TEXT("Frustum calculation successful"));
        UE_LOG(LogTemp, Log, TEXT("Projection Matrix: %s"), *CurrentWarpData.WarpContext.ProjectionMatrix.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Frustum calculation failed"));
    }
}

FMatrix AMyWarpController::GetProjectionMatrix() const
{
    return CurrentWarpData.WarpContext.ProjectionMatrix;
}
```

## 模块依赖

从 Build.cs 的依赖项分析，DisplayClusterWarp 模块主要依赖：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心模块，提供视口、根角色等基础架构 |
| `DisplayClusterProjection` | 投影基础设施，提供投影策略接口 |
| `DisplayClusterShaders` | 扭曲相关的渲染着色器 |
| `MPCDI` | 第三方 MPCDI 库，用于解析校准文件格式 |
| `RenderCore` | UE 渲染核心，用于纹理和网格操作 |
| `RHI` | 渲染硬件接口，用于纹理资源管理 |

**注意**：该模块需要在 `Build.cs` 中添加以下依赖才能使用：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "DisplayClusterWarp" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 添加多层 EXR 支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 MoviePipeline 中的 WarpBlendAlpha 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和 MPCDI 着色器中的不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时遵守非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**维护状态**：**活跃维护中**

**详细分析**：
- **创建时间**：2018年6月，作为 nDisplay 的核心组件，已有7年历史
- **最近更新**：最近一个月（2026年5月）有多次实质性更新，涉及功能增强和bug修复
- **活跃度**：持续有新功能添加（如多层EXR支持、MoviePipeline集成）和问题修复
- **功能成熟度**：支持多种校准格式（MPCDI、PFM）、多种投影类型（2D、3D、A3D、SL），功能完善
- **问题限制**：作为专业渲染模块，需要特定的校准数据和硬件配置

**推荐使用**：✅ **强烈推荐**

DisplayClusterWarp 是一个成熟、稳定且持续维护的专业渲染模块。虽然创建于2018年，但最近仍有频繁的功能更新和bug修复。对于需要多显示器集群渲染、沉浸式投影系统或虚拟制作的项目，这是一个不可或缺的模块。对于简单的单显示器项目则不需要使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterWarp)
- [nDisplay 官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/DisplayCluster/Overview/index.html)（UE官方文档）
- [MPCDI 规范](https://mpcdi.org/)（校准文件格式标准）
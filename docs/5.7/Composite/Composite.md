# Composite 模块（Runtime）

> 运行时核心模块，提供合成管线的 Actor、Layer、Pass 和 Component 基础设施。

## 模块信息

| 属性 | 值 |
|---|---|
| 模块名 | `Composite` |
| 类型 | Runtime |
| LoadingPhase | PostConfigInit |
| 源码路径 | `Source/Composite/` |

## 架构概览

Composite 模块采用 **Actor → Layer → Pass** 三层管线架构：

```
ACompositeActor（合成管线控制器）
├── UCompositeLayerMainRender    （主渲染层：获取场景颜色）
├── UCompositeLayerPlate         （媒体板层：投影纹理/视频到场景）
├── UCompositeLayerSceneCapture  （场景捕获层：自定义渲染通道）
├── UCompositeLayerShadowReflection（阴影/反射捕获层）
├── UCompositeLayerSingleLightShadow（单光源阴影层）
└── UCompositeLayerProcessing    （处理层：对前序输出做后处理）

每个 Layer 可挂载多个 Pass：
├── UCompositePassColorKeyer     （色键抠像）
├── UCompositePassColorGrade     （色彩校正）
├── UCompositePassMaterial       （自定义材质后处理）
├── UCompositePassDistortion     （镜头畸变/反畸变）
├── UCompositePassOpenColorIO    （OCIO 色彩空间转换）
├── UCompositePassCenteredScale  （居中缩放/裁切）
├── UCompositePassFXAA           （FXAA 抗锯齿）
└── UCompositePassSMAA           （SMAA 抗锯齿）
```

## 核心类

### ACompositeActor

合成管线的主控制器 Actor。放置到关卡中后，通过配置 Layer 和 Pass 来定义完整的合成管线。

**关键属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `bIsActive` | bool | 本地激活状态（主要用于 Multi-User） |
| `bIsEnabled` | bool | 启用状态（可 Interp） |
| `RenderResolution` | FIntPoint | 合成渲染分辨率 |
| `Camera` | FComponentReference | 主摄像机引用（CameraComponent 或 CineCameraComponent） |
| `CompositeLayers` | TArray\<UCompositeLayerBase*\> | 合成层数组 |
| `MainRenderOutput` | ECompositeMainRenderOutputMode | 主渲染输出模式（Default/HDR/HDR+ToneCurve） |
| `AllowedViewModes` | ECompositeAllowedViewModes | 允许的视口模式约束 |
| `bEnableScreenSpaceReflections` | bool | 是否将合成图传给 SSR |
| `ViewUserFlags` | int32 | 自定义 View User Flags（用于材质分支） |

**蓝图 API：**

| 函数 | 说明 |
|---|---|
| `IsActive()` / `SetActive()` | 获取/设置本地激活状态 |
| `IsEnabled()` / `SetEnabled()` | 获取/设置启用状态 |
| `GetCamera()` / `SetCamera()` | 获取/设置主摄像机引用 |
| `GetCompositeLayers()` / `SetCompositeLayers()` | 获取/设置合成层 |
| `IsRendering()` | 返回合成是否正在渲染 |

**C++ API：**

```cpp
// 查找或创建场景捕获组件（Layer 内部使用）
template<class RetType>
RetType* FindOrCreateSceneCapture(const UCompositeLayerBase* InLayer, int32 InIndex = 0, FName InBaseName = NAME_None);

// 销毁 Layer 关联的场景捕获组件
void DestroySceneCaptures(const UCompositeLayerBase* InLayer);
```

### UCompositeLayerBase（抽象基类）

所有合成层的基类。定义了层的启用/禁用、Solo 模式、合并操作和代理生成接口。

**关键属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `bIsSolo` | bool | Solo 模式（仅渲染此层） |
| `bIsEnabled` | bool | 启用状态 |
| `Operation` | ECompositeCoreMergeOp | 合并操作（Over/Add/Under 等） |
| `Name` | FString | 层名称（仅编辑器） |

**核心接口：**

```cpp
// 生成渲染线程代理对象
virtual bool GetProxy(FTraversalContext& InContext, FSceneRenderingBulkObjectAllocator& InFrameAllocator, FCompositeCorePassProxy*& OutProxy) const;

// 渲染状态变化回调
virtual void OnRenderingStateChange(bool bApply);

// 层被移除时回调
virtual void OnRemoved(const UWorld* World);
```

### UCompositePassBase（抽象基类）

所有合成 Pass 的基类。每个 Pass 对应一个 GPU 渲染操作。

**关键属性：**

| 属性 | 类型 | 说明 |
|---|---|---|
| `bIsEnabled` | bool | 启用状态 |
| `DisplayName` | FString | 显示名称（仅编辑器） |

**核心接口：**

```cpp
// 生成渲染线程代理
virtual bool GetProxy(const UE::CompositeCore::FPassInputDecl& InputDecl, FSceneRenderingBulkObjectAllocator& InFrameAllocator, FCompositeCorePassProxy*& OutProxy) const;

// 是否需要场景纹理
virtual bool NeedsSceneTextures() const;
```

## Layer 类型详解

### UCompositeLayerPlate（媒体板层）

最常用的层类型，用于将媒体纹理（视频/图像）投影到 3D 场景中。

**工作模式（ECompositePlateMode）：**
- **Texture**：直接在 2D 屏幕空间采样纹理
- **CompositeMesh**：通过 Composite Mesh 渲染自定义通道，将媒体纹理投影到场景几何体上（默认）。自动回退到 Texture 模式

**Pass 阶段：**
1. `MediaPasses` — 媒体纹理预处理（在渲染前应用于纹理）
2. `ScenePasses` — 仅应用于 Composite Mesh 的场景通道（如畸变）
3. `LayerPasses` — 最终合成阶段的后处理 Pass

**蓝图 API：**

| 函数 | 说明 |
|---|---|
| `GetCompositeTexture()` | 获取处理后的合成纹理（含预处理 Pass） |
| `GetCompositeMeshes()` / `SetCompositeMeshes()` | 获取/设置 Composite Mesh Actor |
| `GetPlateMode()` / `SetPlateMode()` | 获取/设置采样模式 |

### UCompositeLayerMainRender（主渲染层）

获取当前后处理位置的场景颜色（SSR Input 和/或 After Tonemap）。通常作为合成管线的第一个层。

### UCompositeLayerProcessing（处理层）

对前序层的输出进行后处理，不引入额外输入。挂载 `LayerPasses` 数组即可。

### UCompositeLayerSceneCapture（场景捕获层）

使用 SceneCapture2D 渲染指定 Actor 的层。支持：
- 指定要渲染的 Actor 列表
- 自定义渲染通道模式（`bCustomRenderPass`）：内联到主渲染器，无光照支持，性能更高
- `bVisibleInSceneCaptureOnly`：注册的 Mesh 仅在场景捕获中可见

### UCompositeLayerShadowReflection（阴影/反射捕获层）

通过两次场景捕获（有 CG / 无 CG）生成乘法遮罩，用于阴影和反射捕捉。

**Auto-Configure 模式（ECompositeHiddenInSceneCaptureConfiguration）：**
- `None`：不修改原始体属性
- `Visible`：设置 `bHiddenInSceneCapture=false`
- `Hidden`：设置 `bHiddenInSceneCapture=true`

### UCompositeLayerSingleLightShadow（单光源阴影层）

使用经典 PCF（Percentage Closer Filtering）阴影贴图技术，通过自定义渲染通道实现单方向光的阴影捕获。

| 属性 | 说明 |
|---|---|
| `Light` | 参考光源（仅支持方向光） |
| `ShadowCastingActors` | 投射阴影的 Actor 列表 |
| `OrthographicWidth` | 阴影视图宽度（世界单位） |
| `ShadowMapResolution` | 阴影贴图分辨率（默认 2048） |
| `ShadowStrength` | 阴影强度（0-1） |

## Pass 类型详解

### UCompositePassColorKeyer（色键抠像）

绿幕/蓝幕抠像 Pass，支持 Clean Plate 和 Spill 消除。

| 属性 | 说明 |
|---|---|
| `ScreenType` | 背景颜色类型（Red/Green/Blue） |
| `KeyColor` | 静态背景色 |
| `CleanPlate` | Clean Plate 纹理（分辨率须匹配合成分辨率） |
| `RedWeight/GreenWeight/BlueWeight` | 前景通道对遮罩硬度的贡献 |
| `AlphaThreshold` | Alpha 阈值范围 |
| `DespillStrength` | 溢色消除强度 |
| `DevignetteStrength` | 暗角消除强度 |
| `DenoiseMethod` | 降噪方法（None/Median 3x3） |
| `Visualization` | 可视化模式（Key/Fill/Alpha） |
| `bInvertAlpha` | 反转 Alpha |

### UCompositePassColorGrade（色彩校正）

假设输入为线性工作色彩空间，提供色温和色彩校正设置。

| 属性 | 说明 |
|---|---|
| `TemperatureSettings` | 色温设置（类型/温度/色调） |
| `ColorGradingSettings` | 完整色彩校正设置（与引擎后处理一致） |

### UCompositePassMaterial（自定义材质后处理）

使用自定义后处理材质执行渲染。Input0 连接到 `SceneTexture's PostprocessInput0`。

### UCompositePassDistortion（畸变 Pass）

应用镜头畸变或反畸变变换。使用 `CameraCalibrationCore` 插件的镜头畸变数据。

| 属性 | 说明 |
|---|---|
| `Distortion` | `Undistort`（反畸变）或 `Distort`（畸变） |

### UCompositePassOpenColorIO（OCIO Pass）

使用 OpenColorIO 进行色彩空间转换。

### UCompositePassCenteredScale（居中缩放 Pass）

处理带黑边的素材，支持自动/手动缩放和过扫描反裁切。

| 属性 | 说明 |
|---|---|
| `ScaleMode` | 缩放模式（None/Automatic/AspectRatio/Manual） |
| `SourceAspectRatio` / `TargetAspectRatio` | 源/目标宽高比 |
| `OverscanUncropMode` | 过扫描反裁切模式 |

### UCompositePassFXAA / UCompositePassSMAA

抗锯齿 Pass，主要用于 CG/运动图形的合成渲染通道。

## Components

### UCompositeSceneCapture2DComponent

继承自 `USceneCaptureComponent2D`，为合成管线定制的场景捕获组件。由 `ACompositeActor` 管理生命周期。

### UCompositeViewProjectionComponent

持续更新 Material Parameter Collection 中的摄像机视图投影矩阵，用于材质中的纹理投影。

**蓝图 API：**

| 函数 | 说明 |
|---|---|
| `ForceUpdate()` | 强制更新 MPC |
| `GetTargetComponent()` / `SetTargetComponent()` | 获取/设置目标摄像机组件 |

### UCompositeMeshComponent

继承自 `UStaticMeshComponent`，用于定义 Composite Mesh 的几何体。

| 材质类型 | 说明 |
|---|---|
| `DefaultLitMasked` | 默认光照遮罩材质（适合阴影/反射，Alpha 边缘质量较差） |
| `DefaultUnlitAlphaComposite` | 默认无光 Alpha 合成材质（预乘 Alpha） |
| `Custom` | 自定义用户材质 |

### UCompositeMeshActor

便捷 Actor，包含一个 `UCompositeMeshComponent`，供 `UCompositeLayerPlate` 引用。

### UCompositeAssetUserData

附加到 Composite Mesh 原始体组件上的 AssetUserData，用于跟踪编辑变更。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎基础 |
| `CompositeCore` | 合成核心框架（渲染代理、Pass 声明等） |
| `OpenColorIO` | OCIO 色彩空间转换 |
| `MediaAssets` | 媒体纹理支持 |
| `RenderCore` | 渲染核心（私有依赖） |
| `Renderer` | 渲染器（私有依赖） |
| `RHI` | RHI 层（私有依赖） |
| `CameraCalibrationCore` | 镜头畸变数据（私有依赖） |
| `MediaFrameworkUtilities` | 媒体框架工具（私有依赖） |
| `ConcertSyncCore` | Multi-User 同步（私有依赖） |

# Composure

> Modern system for real-time compositing. This plugin succeeds legacy Composure and extends CompositeCore.

| 属性 | 值 |
|---|---|
| 中文名 | 实时合成系统 |
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、网格体资产、组件蓝图） |
| 模块 | `Composite` (Runtime), `CompositeEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite) | |

## 用途

Composure 是 UE5 新一代实时合成系统，用于将 CG 内容与实拍媒体素材在渲染管线中进行实时合成。它是旧版 Composure 插件的继任者，基于 CompositeCore 子系统构建，采用层（Layer）+ 通道（Pass）的图层式架构：

- **层（Layer）**：代表一个合成图层，负责采集输入源（实拍板、场景捕获、阴影/反射捕捉等）并将其合并到合成栈中。
- **通道（Pass）**：附加在层上的 GPU 操作节点，对层的输入进行色键抠像、遮罩、变换、色彩校正、模糊等处理。

每个 `ACompositeActor` 是一个独立的合成管线实例，包含多个有序层。系统通过 **RDG（Render Dependency Graph）** 在渲染线程执行实际的 GPU 合成操作，并通过 **Render Proxy** 模式在游戏线程和渲染线程之间安全传递数据。

**解决的核心问题**：在虚拟制作（VP）、LED 墙拍摄、绿幕抠像等场景中，需要将实拍视频素材与 CG 场景实时混合，并确保光影交互（阴影、反射、环境光）正确。传统做法需要多个 Scene Capture 和手动后处理，Composure 将其统一为声明式的图层管线。

## 使用场景

- **虚拟制作 / LED 墙**：将实拍媒体投射到 3D 网格体（composite mesh）上，实现 LED 墙实时合成，支持阴影/反射交互
- **绿幕抠像**：使用 Color Keyer 从蓝/绿幕素材中提取 alpha，支持去溢色（despill）和干净板（clean plate）差异对比
- **CG 元素隔离渲染**：通过 Scene Capture 层将特定 Actor 从主渲染中分离，单独渲染后合成
- **阴影/反射捕捉**：在实拍板上叠加 CG 物体投射的阴影和反射，生成乘法遮罩
- **色彩空间转换**：使用 OpenColorIO 通道在不同色彩空间间转换，适配 ACES/OCIO 管线
- **镜头畸变校正/添加**：使用 Distortion 通道配合相机标定数据去除或添加镜头畸变
- **图像后处理**：对合成结果进行模糊、形态学膨胀/腐蚀、FXAA/SMAA 抗锯齿、2D 变换等处理

## 蓝图用法

### 核心层类型

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetCompositeLayers` / `SetCompositeLayers` | 获取/设置合成图层列表 | `ACompositeActor` |
| `GetCameraActor` / `SetCameraActor` | 获取/设置合成相机 | `ACompositeActor` |
| `GetIsEnabled` / `SetIsEnabled` | 启用/禁用合成 | `ACompositeActor` |
| `GetCompositeTexture` | 获取合成纹理（经过 Media Pass 处理后） | `UCompositeLayerPlate` |
| `GetCompositeMeshes` / `SetCompositeMeshes` | 获取/设置投射网格体 Actor | `UCompositeLayerPlate` |
| `GetActors` / `SetActors` | 获取/设置参与该层的 Actor | `UCompositeLayerSceneCapture` |

### 核心通道类型

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetIsEnabled` / `SetIsEnabled` | 启用/禁用通道 | `UCompositePassBase`（所有通道的基类） |
| `GetMaskingMode` / `SetMaskingMode` | 设置遮罩模式（纹理/几何体） | `UCompositePassMasking` |
| `GetMaskActors` / `SetMaskActors` | 设置遮罩 Actor | `UCompositePassMasking` |
| `CalculateScale` | 计算 2D 变换的 UV 缩放 | `UCompositePassTransform2D` |
| `GetShadowCastingActors` / `SetShadowCastingActors` | 设置阴影投射 Actor | `UCompositeLayerSingleLightShadow` |

### 蓝图使用示例

**创建绿幕合成管线**：

1. 放置一个 `ACompositeActor` 到场景
2. 添加 `Plate` 层 → 设置 `Texture` 为实拍媒体纹理
3. 在 Plate 层的 `MediaPasses` 中添加 `Color Keyer` → 设置 `ScreenType` 为 Green
4. 添加 `Main Render` 层到 Plate 层上方（Over 合并）
5. 将合成相机 Actor 设置到 `CompositeActor` 的 `CameraActor` 属性

**创建阴影捕捉管线**：

1. 放置 `ACompositeActor`，添加 `Plate` 层承载实拍素材
2. 添加 `Shadow Reflection Catcher` 层 → 指定 CG Actor 到 `Actors` 数组
3. 该层会自动生成阴影/反射遮罩并与下层 Plate 合并

## C++ 用法

### 头文件引入

```cpp
#include "CompositeActor.h"
#include "Layers/CompositeLayerPlate.h"
#include "Layers/CompositeLayerMainRender.h"
#include "Passes/CompositePassColorKeyer.h"
```

### 基本用法

从插件源码中的 Actor 生命周期和层管理逻辑提取：

```cpp
// 创建合成 Actor 并配置（来源: CompositeActor.h）
ACompositeActor* CompositeActor = World->SpawnActor<ACompositeActor>();

// 设置合成相机
CompositeActor->SetCameraActor(MyCameraActor);

// 启用合成
CompositeActor->SetIsEnabled(true);

// 获取和修改层
TArray<UCompositeLayerBase*> Layers = CompositeActor->GetCompositeLayers();
// Layers 通过 EditAnywhere/Instanced 属性在编辑器中配置
```

### 进阶用法

```cpp
// 使用 ViewProjection 组件将相机矩阵写入材质参数集合
// （来源: CompositeViewProjectionComponent.h）
UCompositeViewProjectionComponent* VpComp = CompositeActor->FindComponentByClass<UCompositeViewProjectionComponent>();
if (VpComp)
{
    VpComp->MaterialParameterCollection = MyMPC;
    VpComp->ViewProjectionMatrixParameter = FName("ViewProjMatrix");
    VpComp->ForceUpdate();
}

// 请求场景捕获组件（来源: CompositeActor.h 模板方法）
// Pass 内部使用 FindOrCreateSceneCapture 请求专用场景捕获
UCompositeSceneCapture2DComponent* Capture = CompositeActor->FindOrCreateSceneCapture<UCompositeSceneCapture2DComponent>(MyPass, 0, FName("MyCapture"));

// 管理渲染目标池（来源: CompositeRenderTargetPool.h）
FCompositeRenderTargetPool& Pool = FCompositeRenderTargetPool::Get();
TObjectPtr<UTextureRenderTarget2D> RT = Pool.AcquireTarget(Assignee, FIntPoint(1920, 1080));
// ... 使用完毕后释放
Pool.ReleaseTarget(RT);
```

## Demo 示例

```cpp
// CompositeDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "CompositeActor.h"
#include "CompositeDemoActor.generated.h"

/**
 * 演示如何在 C++ 中创建并管理一个合成管线
 */
UCLASS()
class ACompositeDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ACompositeDemoActor();

    virtual void BeginPlay() override;

    /** 合成管线 Actor */
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<ACompositeActor> CompositeActor;

    /** 合成相机 */
    UPROPERTY(EditAnywhere)
    TSoftObjectPtr<AActor> TargetCamera;

    /** 媒体纹理 */
    UPROPERTY(EditAnywhere)
    TObjectPtr<UTexture> PlateTexture;

    UFUNCTION(BlueprintCallable)
    void EnableCompositing(bool bEnable);
};
```

```cpp
// CompositeDemoActor.cpp
#include "CompositeDemoActor.h"
#include "Engine/World.h"

ACompositeDemoActor::ACompositeDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ACompositeDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (!CompositeActor)
    {
        // 在实际项目中，合成 Actor 通常在编辑器中手动放置并配置
        // 此处演示运行时的基本交互
        UE_LOG(LogTemp, Warning, TEXT("CompositeDemoActor: 请在编辑器中放置并配置 ACompositeActor"));
        return;
    }

    // 设置合成相机
    if (!TargetCamera.IsNull())
    {
        CompositeActor->SetCameraActor(TargetCamera);
    }

    // 启用合成
    CompositeActor->SetIsEnabled(true);

    // 获取当前层信息
    TArray<UCompositeLayerBase*> Layers = CompositeActor->GetCompositeLayers();
    UE_LOG(LogTemp, Log, TEXT("CompositeActor has %d layers"), Layers.Num());
}

void ACompositeDemoActor::EnableCompositing(bool bEnable)
{
    if (CompositeActor)
    {
        CompositeActor->SetIsEnabled(bEnable);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CompositeCore` | 底层合成核心框架，提供 Pass/Proxy 基础设施和子系统 |
| `LensDistortion` | 镜头畸变校正（Distortion 通道依赖） |
| `OpenColorIO` | 色彩空间转换（OpenColorIO 通道依赖） |
| `MediaAssets` | 媒体纹理支持（Plate 层用于 MediaTexture） |
| `MovieScene` / `LevelSequence` | Sequencer spawnable 绑定支持 |

> **注意**：使用前需在 `.uproject` 中启用 `Composite` 和 `CompositeCore` 插件。`Composite` 默认未启用（`EnabledByDefault: false`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `0d66152d` | Compositing: Add ChromaShift property to compensate for potential chroma subsampling offsets during | 为 Color Keyer 添加 ChromaShift 属性，补偿 4:2:2 色度子采样偏移 |
| 2026-05-22 | `90b2a9d0` | Composure: Default bRemoveOverscan to false on Transform2D pass. | 将 Transform2D 通道的 bRemoveOverscan 默认值改为 false |
| 2026-05-21 | `e1f95393` | Composure: Release r.Translucency.AutoBeforeDOF / r.Translucency.Holdout.Location override when the | 释放 translucency CVar 覆盖，避免 holdout 与 DOF 冲突 |
| 2026-05-20 | `4d6f2665` | Composure: Fixed custom pass pass details view so Interp properties show the keyframe button. | 修复自定义通道详情面板中 Interp 属性不显示关键帧按钮的问题 |
| 2026-05-20 | `de6434f1` | Composure: Add final new icons for composite actors, layers, and passes, and minor tweaks to menu co | 为合成 Actor/层/通道添加最终图标并调整菜单布局 |

### 维护评价

- **创建时间**：2025-09-17，约 1 年前，是较新的插件
- **实验性**：`IsBetaVersion = true`，`EnabledByDefault = false`，目前处于测试阶段
- **活跃维护**：最近 3 个月内持续有功能性更新（ChromaShift 新特性、CVar 修复、UI 改进）
- **架构特点**：作为旧版 Composure 的后继者，基于 CompositeCore 重构，采用 RDG 现代渲染架构
- **已知限制**：
  - 需要手动启用插件
  - 部分 API 可能在 Beta 阶段发生变更
  - 需要合理的项目设置（关闭自动曝光、100% 屏幕百分比）才能获得最佳效果
- **推荐**：适用于虚拟制作和实时合成项目，但由于是 Beta 状态，生产环境使用需做好升级准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/Composite)
- [官方文档]()（暂无）
- [CompositeCore 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Compositing/CompositeCore)
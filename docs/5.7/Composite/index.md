# Composure

> Modern system for real-time compositing. This plugin succeeds legacy Composure and extends CompositeCore.

| 属性 | 值 |
|---|---|
| 分类 | Compositing |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质函数、默认材质） |
| 模块 | `Composite` (Runtime), `CompositeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composite) | |

## 用途

Composure（Composite 插件）是 UE5 新一代的实时合成系统，取代了旧版 Composure 插件，基于 `CompositeCore` 框架构建。它解决的核心问题是：**在虚幻引擎中进行实时、高质量的 CG 与实拍素材合成**。

典型场景包括：
- 虚拟制片中将摄像机实拍画面与 CG 场景实时合成
- 绿幕/蓝幕实时抠像与背景替换
- CG 元素（阴影、反射）与实拍画面的混合
- 镜头畸变/反畸变处理
- 色彩空间转换（OCIO）
- 多层合成管线的构建与调试

## 使用场景

- **虚拟制片**：在 LED 墙场景中，将实拍演员与虚拟背景实时合成，包括阴影和反射
- **实时抠像**：使用色键器对绿幕素材进行实时抠像，替换背景
- **运动图形合成**：将 3D 运动图形与实拍画面混合，应用抗锯齿和色彩校正
- **镜头匹配**：通过镜头畸变、色彩校正和投影矩阵匹配虚拟摄像机与实拍摄像机

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetEnabled` | 启用/禁用合成管线 | `ACompositeActor` |
| `SetActive` | 设置本地激活状态（Multi-User） | `ACompositeActor` |
| `SetCompositeLayers` | 设置合成层数组 | `ACompositeActor` |
| `SetCamera` | 设置主摄像机引用 | `ACompositeActor` |
| `GetCompositeTexture` | 获取处理后的合成纹理 | `UCompositeLayerPlate` |
| `SetCompositeMeshes` | 设置 Composite Mesh Actor | `UCompositeLayerPlate` |
| `SetPlateMode` | 设置板层采样模式 | `UCompositeLayerPlate` |
| `SetActors` | 设置场景捕获/阴影 Actor | `UCompositeLayerSceneCapture` 等 |
| `SetCustomRenderPass` | 切换自定义渲染通道模式 | `UCompositeLayerSceneCapture` |
| `SetEnabled` | 启用/禁用单个 Layer 或 Pass | `UCompositeLayerBase` / `UCompositePassBase` |
| `ForceUpdate` | 强制更新视图投影矩阵 MPC | `UCompositeViewProjectionComponent` |
| `SetMaterialType` | 设置 Composite Mesh 材质类型 | `UCompositeMeshComponent` |
| `CalculateScale` | 计算居中缩放因子 | `UCompositePassCenteredScale` |

### 使用示例（蓝图描述）

**基本合成管线搭建：**
1. 在关卡中放置 `ACompositeActor`
2. 工厂会自动创建三个默认层：MainRender、ShadowReflection（禁用）、Plate
3. 在 Plate 层的 `Texture` 属性中指定媒体纹理（MediaTexture 或 Texture2D）
4. 在 Plate 层的 `CompositeMeshes` 中指定要投影的 Mesh Actor
5. 设置 `ACompositeActor` 的 `Camera` 引用为场景中的摄像机
6. 启用 `ACompositeActor` 的 `IsEnabled`

**添加抠像 Pass：**
1. 在 Plate 层的 `MediaPasses` 数组中添加 `Color Keyer Pass`
2. 设置 `ScreenType` 为绿幕或蓝幕
3. 调整 `AlphaThreshold`、`DespillStrength` 等参数
4. 使用 `Visualization` 选项检查抠像质量

## C++ 用法

### 头文件引入

```cpp
#include "CompositeActor.h"
#include "Layers/CompositeLayerPlate.h"
#include "Layers/CompositeLayerMainRender.h"
#include "Passes/CompositePassColorKeyer.h"
```

### 基本用法

```cpp
// 创建合成 Actor 并配置基本管线
ACompositeActor* CompositeActor = World->SpawnActor<ACompositeActor>();
CompositeActor->SetEnabled(true);
CompositeActor->RenderResolution = FIntPoint(1920, 1080);

// 设置摄像机引用
FComponentReference CameraRef;
CameraRef.OtherActor = CameraActor;
CameraRef.ComponentProperty = FName("CameraComponent");
CompositeActor->SetCamera(CameraRef);
```

### 进阶用法

```cpp
// 创建自定义合成层配置
TArray<UCompositeLayerBase*> Layers;

// 主渲染层
auto* MainRender = NewObject<UCompositeLayerMainRender>(CompositeActor);
Layers.Add(MainRender);

// 媒体板层
auto* Plate = NewObject<UCompositeLayerPlate>(CompositeActor);
Plate->Texture = MediaTexture;
Plate->SetPlateMode(ECompositePlateMode::CompositeMesh);
Plate->SetCompositeMeshes({MeshActor});

// 添加色键 Pass
auto* Keyer = NewObject<UCompositePassColorKeyer>(CompositeActor);
Keyer->ScreenType = ECompositeColorKeyerScreenType::Green;
Keyer->DespillStrength = 0.8f;
Plate->MediaPasses.Add(Keyer);

// 添加色彩校正 Pass
auto* ColorGrade = NewObject<UCompositePassColorGrade>(CompositeActor);
Plate->LayerPasses.Add(ColorGrade);

Layers.Add(Plate);
CompositeActor->SetCompositeLayers(Layers);
```

## Demo 示例

```cpp
// MyCompositor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyCompositor.generated.h"

UCLASS()
class AMyCompositor : public AActor
{
    GENERATED_BODY()
public:
    AMyCompositor();
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Compositing")
    TObjectPtr<UTexture> MediaTexture;

    UPROPERTY(EditAnywhere, Category = "Compositing")
    TObjectPtr<AActor> MeshActor;
};
```

```cpp
// MyCompositor.cpp
#include "MyCompositor.h"
#include "CompositeActor.h"
#include "Layers/CompositeLayerPlate.h"
#include "Layers/CompositeLayerMainRender.h"
#include "Passes/CompositePassColorKeyer.h"

AMyCompositor::AMyCompositor() {}

void AMyCompositor::BeginPlay()
{
    Super::BeginPlay();

    auto* CA = GetWorld()->SpawnActor<ACompositeActor>();
    CA->SetEnabled(true);

    // 创建板层
    auto* Plate = NewObject<UCompositeLayerPlate>(CA);
    Plate->Texture = MediaTexture;
    if (MeshActor)
    {
        Plate->SetCompositeMeshes({MeshActor});
    }

    // 添加抠像
    auto* Keyer = NewObject<UCompositePassColorKeyer>(CA);
    Keyer->ScreenType = ECompositeColorKeyerScreenType::Green;
    Plate->MediaPasses.Add(Keyer);

    TArray<UCompositeLayerBase*> Layers;
    Layers.Add(NewObject<UCompositeLayerMainRender>(CA));
    Layers.Add(Plate);
    CA->SetCompositeLayers(Layers);
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Composite" });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CompositeCore` | 合成核心框架（渲染代理、Pass 声明、子系统） |
| `OpenColorIO` | OCIO 色彩空间转换支持 |
| `CameraCalibrationCore` | 镜头畸变校准数据 |
| `MediaFrameworkUtilities` | 媒体框架工具 |
| `ConcertSyncClient` / `ConcertSyncCore` | Multi-User 编辑同步 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-11-18 | `6ed8cae` | Prevent "leaked" scene capture component after layer deletion | 修复层删除后场景捕获组件泄漏的问题 |
| 2025-10-17 | `c322ec9` | Fixed warning when creating a new composite mesh actor | 修复创建 CompositeMeshActor 时的警告 |
| 2025-10-15 | `6f4bb82` | Fixed pre-processing passes incorrectly running twice | 修复预处理 Pass 重复执行的 bug |

### 维护评价

- **创建时间**：2025-09-23，非常新的插件
- **维护状态**：活跃维护中，近期有多次 bug 修复
- **实验性标记**：`IsExperimentalVersion=true`，尚未稳定
- **默认未启用**：`EnabledByDefault=false`，需要手动在插件管理器中启用
- **建议**：适合虚拟制片等前沿场景的早期采用者，生产环境使用需关注后续 API 变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Compositing/Composite)
- 官方文档（无）

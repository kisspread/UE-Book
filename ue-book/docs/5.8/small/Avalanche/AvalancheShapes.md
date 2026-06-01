# Motion Design Shapes

> Compositing, designer and broadcasting tool.
>
> Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 动态图形组件 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvalancheShapes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheShapes) | |

## 用途

AvalancheShapes 模块是 Motion Design（Avalanche）插件的几何形状子系统，提供了一套**程序化参数化动态网格（Dynamic Mesh）形状生成器**。它解决的核心问题是：在虚拟制片和广播设计场景中，需要快速创建、编辑和动画化 2D/3D 基本几何体（矩形、圆、星形、球体、圆锥、圆环等），而不需要导入外部模型资产。

该模块基于 UE5 的 `UDynamicMeshComponent`，所有形状都是运行时程序化生成的，支持：
- **参数化材质系统**：内置纯色、渐变、纹理等样式，无需手动创建材质资产
- **多网格分段管理**：复杂形状（如球体、圆锥）可拆分为多个独立网格段，每段可单独设置材质和可见性
- **异步网格更新**：形状参数变更后可在后台线程重建网格，避免阻塞游戏线程
- **Sequencer 动画支持**：矩形圆角等属性可通过 Sequencer 轨道进行关键帧动画
- **材质桥接系统**：与 Motion Design 的材质设计器和远程控制系统集成

## 使用场景

- 你在制作虚拟制片的广播图文包装（下三分之一、标题卡、LOGO 动画）→ 用矩形、圆角矩形、星形等 2D 形状作为基础元素
- 你需要程序化生成参数化几何体（如可调边数的多边形、可调内径的圆环）→ 用对应的 Dynamic Mesh 组件
- 你希望形状属性可以通过 Sequencer 进行动画化（如圆角大小随时间变化）→ 使用 Sequencer 形状轨道
- 你在一个 Motion Design 工作流中需要快速切换材质样式（纯色/渐变/纹理）而不想创建材质实例 → 使用内置参数化材质系统
- 你需要导出运行时生成的动态网格为静态网格资产 → 使用 `ExportToStaticMesh` 功能

## 蓝图用法

### 核心节点 — 形状创建

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetRectangle` | 为 ShapeActor 设置矩形网格，指定大小和变换 | `UAvaShapeMeshFunctions` |
| `RefreshParametricMaterial` | 触发参数化材质刷新（供远程控制或蓝图调用） | `AAvaShapeActor` |

### 核心节点 — 形状属性（UAvaShapeDynamicMeshBase）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSize2D` / `GetSize2D` | 设置/获取 2D 形状尺寸 | `UAvaShapeDynamicMeshBase` |
| `SetSize3D` / `GetSize3D` | 设置/获取 3D 形状尺寸 | `UAvaShapeDynamicMeshBase` |
| `SetUniformScaledSize` / `GetUniformScaledSize` | 设置/获取统一缩放比例 | `UAvaShapeDynamicMeshBase` |
| `GetMeshSectionNames` | 获取所有网格段名称 | `UAvaShapeDynamicMeshBase` |
| `IsMeshSectionVisible` | 检查指定网格段是否可见 | `UAvaShapeDynamicMeshBase` |
| `SetMaterial` / `GetMaterial` | 设置/获取指定网格段的材质 | `UAvaShapeDynamicMeshBase` |
| `SetMaterialType` / `GetMaterialType` | 设置/获取材质类型（资产/参数化/材质设计器） | `UAvaShapeDynamicMeshBase` |
| `SetParametricMaterial` / `GetParametricMaterial` | 设置/获取参数化材质配置 | `UAvaShapeDynamicMeshBase` |
| `SetUsePrimaryMaterialEverywhere` | 是否将主材质应用于所有网格段 | `UAvaShapeDynamicMeshBase` |
| `ExportToStaticMesh` | 将动态网格导出为静态网格 | `UAvaShapeDynamicMeshBase` |
| `SetRunAsync` / `GetRunAsync` | 设置/获取是否异步更新网格 | `UAvaShapeDynamicMeshBase` |

### 核心节点 — UV 参数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMaterialUVMode` | 设置 UV 模式（拉伸/保持比例） | `UAvaShapeDynamicMeshBase` |
| `SetMaterialUVScale` / `SetMaterialUVOffset` | 设置 UV 缩放/偏移 | `UAvaShapeDynamicMeshBase` |
| `SetMaterialUVRotation` | 设置 UV 旋转角度 | `UAvaShapeDynamicMeshBase` |
| `SetMaterialHorizontalFlip` / `SetMaterialVerticalFlip` | 水平/垂直翻转 UV | `UAvaShapeDynamicMeshBase` |

### 核心节点 — 参数化材质属性

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStyle` | 设置材质样式（纯色/渐变/纹理） | `FAvaShapeParametricMaterial` |
| `SetPrimaryColor` / `SetSecondaryColor` | 设置主色/次色 | `FAvaShapeParametricMaterial` |
| `SetTexture` | 设置纹理 | `FAvaShapeParametricMaterial` |
| `SetGradientOffset` / `SetGradientRotation` | 设置渐变偏移/旋转 | `FAvaShapeParametricMaterial` |
| `SetUseUnlitMaterial` | 是否使用无光照材质 | `FAvaShapeParametricMaterial` |
| `SetUseTwoSidedMaterial` | 是否使用双面材质 | `FAvaShapeParametricMaterial` |

### 核心节点 — 矩形形状特有属性

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLeftSlant` / `SetRightSlant` | 设置左右倾斜角度 | `UAvaShapeRectangleDynamicMesh` |
| `SetGlobalBevelSize` / `SetGlobalBevelSubdivisions` | 设置全局圆角大小/细分 | `UAvaShapeRectangleDynamicMesh` |
| `SetTopLeft` / `SetTopRight` / `SetBottomLeft` / `SetBottomRight` | 设置各角的圆角参数 | `UAvaShapeRectangleDynamicMesh` |
| `SetHorizontalAlignment` / `SetVerticalAlignment` | 设置对齐方式 | `UAvaShapeRectangleDynamicMesh` |

### 核心节点 — 3D 形状特有属性

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetNumSides` | 设置球体/圆锥/圆环的边数（精度） | `UAvaShapeSphereDynamicMesh` / `UAvaShapeConeDynamicMesh` / `UAvaShapeTorusDynamicMesh` |
| `SetStartLatitude` / `SetLatitudeDegree` | 设置球体纬度起始/范围 | `UAvaShapeSphereDynamicMesh` |
| `SetStartLongitude` / `SetEndLongitude` | 设置球体经度起始/结束 | `UAvaShapeSphereDynamicMesh` |
| `SetTopRadius` / `SetAngleDegree` / `SetStartDegree` | 设置圆锥顶半径/角度/起始角度 | `UAvaShapeConeDynamicMesh` |
| `SetInnerSize` | 设置圆环内径比例 | `UAvaShapeTorusDynamicMesh` |
| `SetSegment` / `SetBevelSizeRatio` / `SetBevelNum` | 设置立方体分段/圆角大小/圆角分段数 | `UAvaShapeCubeDynamicMesh` |

### 核心节点 — 不规则多边形

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetPoints` | 设置多边形顶点数组 | `UAvaShapeIrregularPolygonDynamicMesh` |
| `AddPoint` / `RemovePoint` | 添加/移除顶点 | `UAvaShapeIrregularPolygonDynamicMesh` |
| `SetGlobalBevelSize` | 设置全局圆角大小 | `UAvaShapeIrregularPolygonDynamicMesh` |
| `RecalculateActorPosition` | 重新计算 Actor 位置 | `UAvaShapeIrregularPolygonDynamicMesh` |

### 使用示例（蓝图描述）

**创建一个带渐变材质的矩形：**

1. 在场景中放置一个 `AAvaShapeActor`
2. 调用 `UAvaShapeMeshFunctions::SetRectangle`，传入 ShapeActor 指针、`FVector2D(200, 100)` 大小和单位变换
3. 获取返回的 `UAvaShapeRectangleDynamicMesh` 指针
4. 通过 `SetUsePrimaryMaterialEverywhere(true)` 将主材质应用于所有网格段
5. 获取主网格段（索引 0）的 `GetParametricMaterial`
6. 设置样式为 `LinearGradient`，主色为蓝色，次色为青色，渐变旋转为 0.5

**在 Sequencer 中动画化圆角：**

1. 选中带矩形形状的 ShapeActor
2. 在 Sequencer 中添加轨道 → 选择 Shape 的 `RectCorner` 轨道
3. 在时间轴上为 `BevelSize`、`Type`、`BevelSubdivisions` 设置关键帧
4. 播放时圆角参数将随时间插值变化

## C++ 用法

### 头文件引入

```cpp
#include "AvaShapeActor.h"
#include "DynamicMeshes/AvaShapeDynMeshBase.h"
#include "DynamicMeshes/AvaShapeRectangleDynMesh.h"
#include "DynamicMeshes/AvaShapeEllipseDynMesh.h"
#include "DynamicMeshes/AvaShapeStarDynMesh.h"
#include "DynamicMeshes/AvaShapeSphereDynMesh.h"
#include "DynamicMeshes/AvaShapeConeDynMesh.h"
#include "DynamicMeshes/AvaShapeCubeDynMesh.h"
#include "DynamicMeshes/AvaShapeTorusDynMesh.h"
#include "AvaShapeParametricMaterial.h"
#include "AvaShapePrimitiveFunctions.h"
```

### 基本用法

**创建矩形形状并设置参数化材质：**

```cpp
// 创建 ShapeActor
FActorSpawnParameters SpawnParams;
AAvaShapeActor* ShapeActor = GetWorld()->SpawnActor<AAvaShapeActor>(SpawnParams);

// 设置为矩形形状
UAvaShapeRectangleDynamicMesh* RectMesh = UAvaShapeMeshFunctions::SetRectangle(
    ShapeActor,
    FVector2D(200.f, 100.f),  // 宽200cm，高100cm
    FTransform::Identity
);

// 设置圆角参数
RectMesh->SetGlobalBevelSize(0.3f);
RectMesh->SetGlobalBevelSubdivisions(16);

// 设置倾斜
RectMesh->SetLeftSlant(15.f);   // 左侧倾斜15度
RectMesh->SetRightSlant(-10.f); // 右侧倾斜-10度

// 设置参数化材质
RectMesh->SetMaterialType(0, EMaterialType::Parametric);
FAvaShapeParametricMaterial& ParamMat = *RectMesh->GetParametricMaterialPtr(0);
ParamMat.SetStyle(EAvaShapeParametricMaterialStyle::LinearGradient);
ParamMat.SetPrimaryColor(FLinearColor::Blue);
ParamMat.SetSecondaryColor(FLinearColor::Cyan);
ParamMat.SetGradientRotation(0.25f);
```

**导出动态网格为静态网格：**

```cpp
// 创建目标静态网格
UStaticMesh* ExportedMesh = NewObject<UStaticMesh>(GetTransientPackage(), NAME_None, RF_Transient);

// 导出
bool bSuccess = ShapeActor->GetDynamicMesh()->ExportToStaticMesh(ExportedMesh);
```

### 进阶用法

**创建和配置 3D 球体：**

```cpp
AAvaShapeActor* ShapeActor = GetWorld()->SpawnActor<AAvaShapeActor>();
UDynamicMeshComponent* MeshComp = ShapeActor->GetShapeMeshComponent();

// 创建球体动态网格
UAvaShapeSphereDynamicMesh* SphereMesh = NewObject<UAvaShapeSphereDynamicMesh>(ShapeActor);
ShapeActor->SetDynamicMesh(SphereMesh);

// 配置球体参数
SphereMesh->SetSize3D(FVector(100.f, 100.f, 100.f));
SphereMesh->SetNumSides(64);                // 精度64
SphereMesh->SetStartLatitude(0.f);
SphereMesh->SetLatitudeDegree(360.f);        // 完整360度
SphereMesh->SetStartLongitude(0.f);
SphereMesh->SetEndLongitude(180.f);          // 完整180度经度

// 为球体的不同网格段设置不同材质
// 主体段(index 0)用参数化材质
SphereMesh->SetMaterialType(0, EMaterialType::Parametric);
FAvaShapeParametricMaterial* ParamMat = SphereMesh->GetParametricMaterialPtr(0);
ParamMat->SetStyle(EAvaShapeParametricMaterialStyle::Solid);
ParamMat->SetPrimaryColor(FLinearColor::Red);
```

**自定义各角圆角设置（矩形）：**

```cpp
UAvaShapeRectangleDynamicMesh* Rect = ShapeActor->GetDynamicMesh<UAvaShapeRectangleDynamicMesh>();

// 单独设置每个角的圆角
FAvaShapeRectangleCornerSettings TopLeftCorner;
TopLeftCorner.Type = EAvaShapeCornerType::CurveOut;
TopLeftCorner.BevelSize = 0.5f;
TopLeftCorner.BevelSubdivisions = 32;
Rect->SetTopLeft(TopLeftCorner);

// 底部直角
FAvaShapeRectangleCornerSettings BottomCorner;
BottomCorner.Type = EAvaShapeCornerType::Point;
BottomCorner.BevelSize = 0.f;
Rect->SetBottomLeft(BottomCorner);
Rect->SetBottomRight(BottomCorner);
```

**不规则多边形的程序化构建：**

```cpp
UAvaShapeIrregularPolygonDynamicMesh* Polygon = /* 从 ShapeActor 获取 */;

// 定义顶点
TArray<FVector2D> Points = {
    FVector2D(0.f, 0.f),
    FVector2D(100.f, 0.f),
    FVector2D(150.f, 50.f),
    FVector2D(100.f, 100.f),
    FVector2D(0.f, 100.f),
    FVector2D(-50.f, 50.f)
};

// 检查并添加顶点
for (const FVector2D& Point : Points)
{
    if (Polygon->CanAddPoint(Point))
    {
        Polygon->AddPoint(Point);
    }
}

// 设置圆角
Polygon->SetGlobalBevelSize(0.3f);
Polygon->SetGlobalBevelSubdivisions(16);
```

**配置形状碰撞行为（全局设置）：**

```cpp
UAvaShapeSettings* ShapeSettings = GetMutableDefault<UAvaShapeSettings>();
// bForceDisableShapeCollision 默认为 true
// Motion Design 工作流通常不需要碰撞
// 可在 Editor Preferences → Motion Design Shapes 中修改
```

## Demo 示例

**创建一个带动画渐变材质的星形形状：**

```cpp
// StarShapeExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StarShapeExample.generated.h"

class AAvaShapeActor;
class UAvaShapeStarDynamicMesh;

UCLASS()
class AStarShapeExample : public AActor
{
    GENERATED_BODY()

public:
    AStarShapeExample();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    AAvaShapeActor* ShapeActor = nullptr;

    UPROPERTY()
    UAvaShapeStarDynamicMesh* StarMesh = nullptr;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Star")
    float RotationSpeed = 30.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Star")
    float GradientSpeed = 0.1f;

private:
    float ElapsedTime = 0.f;
};
```

```cpp
// StarShapeExample.cpp
#include "StarShapeExample.h"

#include "AvaShapeActor.h"
#include "DynamicMeshes/AvaShapeStarDynMesh.h"
#include "AvaShapeParametricMaterial.h"

AStarShapeExample::AStarShapeExample()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AStarShapeExample::BeginPlay()
{
    Super::BeginPlay();

    // 创建 ShapeActor
    FActorSpawnParameters Params;
    ShapeActor = GetWorld()->SpawnActor<AAvaShapeActor>(GetActorLocation(), GetActorRotation(), Params);

    if (!ShapeActor)
    {
        return;
    }

    // 创建星形动态网格
    StarMesh = NewObject<UAvaShapeStarDynamicMesh>(ShapeActor);
    ShapeActor->SetDynamicMesh(StarMesh);

    // 配置星形参数
    StarMesh->SetSize2D(FVector2D(200.f, 200.f));
    StarMesh->SetNumPoints(8);          // 8角星
    StarMesh->SetInnerSize(0.5f);       // 内径比例
    StarMesh->SetBevelSize(0.2f);       // 圆角
    StarMesh->SetBevelSubdivisions(16); // 圆角细分

    // 设置参数化材质
    StarMesh->SetMaterialType(0, EMaterialType::Parametric);
    FAvaShapeParametricMaterial* ParamMat = StarMesh->GetParametricMaterialPtr(0);
    if (ParamMat)
    {
        ParamMat->SetStyle(EAvaShapeParametricMaterialStyle::LinearGradient);
        ParamMat->SetPrimaryColor(FLinearColor::Red);
        ParamMat->SetSecondaryColor(FLinearColor::Yellow);
        ParamMat->SetGradientOffset(0.5f);
    }

    // 设置 UV 参数
    StarMesh->SetMaterialUVMode(0, EAvaShapeUVMode::Uniform);
}

void AStarShapeExample::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    ElapsedTime += DeltaSeconds;

    // 旋转渐变方向
    if (StarMesh)
    {
        float GradientRotation = FMath::Fmod(ElapsedTime * GradientSpeed, 1.0f);
        StarMesh->SetMaterialUVRotation(0, GradientRotation * 360.f);

        // 动态改变内径比例产生脉动效果
        float Pulse = 0.3f + 0.2f * FMath::Sin(ElapsedTime * RotationSpeed * 0.01f);
        StarMesh->SetInnerSize(FMath::Clamp(Pulse, 0.1f, 0.9f));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryScriptingCore` | 动态网格操作和网格数据处理 |
| `GeometryFramework` | `UDynamicMeshComponent` 支持 |
| `GeometryCore` | 底层几何计算（`FDynamicMesh3` 等） |
| `Sequencer` | Sequencer 轨道和关键帧动画模板 |
| `AvalancheCore` | Motion Design 核心功能（对齐、交互工具等） |
| `ActorModifierCore` | Actor 修改器框架集成 |
| `DynamicMaterial` | 动态材质和材质桥接系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 新增全局设置强制禁用形状碰撞，优化性能 |
| 2025-05-09 | `d53ec51` | Motion Design: moved the following plugins from /Plugins/Experimental to /Plugins/VirtualProduction | 从实验性目录迁移到正式 VirtualProduction 目录 |

### 维护评价

AvalancheShapes 模块自 2025 年 5 月从实验性插件迁移至正式 VirtualProduction 目录，标志着其从实验阶段进入正式生产就绪状态。最近的更新聚焦于性能优化（碰撞禁用设置），表明团队在关注实际生产环境中的性能问题。

该模块是 Motion Design 工作流的核心组件之一，包含完整的 2D/3D 形状生成器、参数化材质系统、Sequencer 集成和材质桥接系统。模块代码量大（约 32 个头文件），结构清晰，层次分明（基类 → 2D/3D 基类 → 具体形状）。

**推荐使用**：该模块处于活跃维护状态，适合在虚拟制片和广播设计项目中使用。注意默认启用了形状碰撞禁用，如果需要碰撞功能需手动在项目设置中关闭。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheShapes)
- [Avalanche 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
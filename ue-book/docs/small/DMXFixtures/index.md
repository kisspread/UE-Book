# DMX Fixtures

> DMX Light Fixtures Blueprints

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | 是 |
| 包含内容 | 是 |
| 模块 | DMXFixtures (Runtime) |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXFixtures) | |

## 用途

DMXFixtures 提供了一套可直接使用的 DMX 灯具 Actor 和组件框架，用于在 UE5 中模拟真实的舞台/影视灯光设备。它解决了以下问题：

- **标准化灯具控制**：将 DMX 协议的归一化属性值（0.0–1.0）映射到灯光参数（亮度、色温、缩放等），自动驱动聚光灯、点光源和材质效果
- **插值平滑**：内置通道插值系统，避免 DMX 值跳变导致的视觉闪烁
- **矩阵灯具支持**：通过 `ADMXFixtureActorMatrix` 和 `ProceduralMeshComponent` 支持 LED 像素矩阵灯（如 LED 面板），每个像素独立受 DMX 控制
- **视觉质量分级**：提供 Low/Medium/High/Ultra/Custom 五档光束渲染质量，平衡 GPU 开销与视觉效果

该 plugin 是 DMX 生态系统中的"运行时灯具"层，位于 DMXProtocol（协议层）和 DMXEngine（数据层）之上，为 Virtual Production 中的实时灯光预览提供开箱即用的 Actor。

## 使用场景

- 你在做虚拟制片（Virtual Production），需要在 UE 中实时预览 DMX 控制台控制的舞台灯光效果 → 使用 DMXFixtures
- 你需要一个 LED 矩阵墙（如 LED Volume），每个像素受独立 DMX 通道控制 → 使用 `ADMXFixtureActorMatrix`
- 你已通过 DMXProtocol 连接了 Art-Net 或 sACN 控制台，想快速放置可响应 DMX 信号的灯具 → 在蓝图中放置 `ADMXFixtureActor` 并关联 Fixture Patch
- 你基于 GDTF 文件导入了灯具描述，需要对应的运行时 Actor → DMXFixtures 的组件架构与 GDTF 模式兼容

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PushNormalizedValuesPerAttribute` | 向灯具推送归一化 DMX 值（0.0–1.0），自动分发给所有已启用的 FixtureComponent | `ADMXFixtureActorBase` |
| `InterpolateDMXComponents` | 每帧调用，驱动所有组件的插值计算（通常由 Tick 自动调用） | `ADMXFixtureActorBase` |
| `InitializeFixture` | 初始化灯具：创建动态材质、设置光源参数、初始化所有组件。需要传入透镜和光束的 StaticMesh | `ADMXFixtureActor` |
| `UpdateSpotLightIntensity` | 根据 LightIntensityMax、SpotlightIntensityScale 和锥角重新计算聚光灯强度 | `ADMXFixtureActor` |
| `SetLightIntensityMax` | 设置最大光照强度（流明），同时更新材质参数 | `ADMXFixtureActor` |
| `SetLightDistanceMax` | 设置最大光照距离（衰减半径） | `ADMXFixtureActor` |
| `SetLightColorTemp` | 设置色温（开尔文） | `ADMXFixtureActor` |
| `SetSpotlightIntensityScale` | 设置聚光灯强度缩放系数 | `ADMXFixtureActor` |
| `SetPointlightIntensityScale` | 设置点光源强度缩放系数 | `ADMXFixtureActor` |
| `SetLightCastShadow` | 启用/禁用阴影投射 | `ADMXFixtureActor` |
| `PushFixtureMatrixCellData` | 向矩阵灯具推送像素级颜色数据 | `ADMXFixtureActorMatrix` |
| `InitializeMatrixFixture` | 初始化矩阵灯具的网格和纹理 | `ADMXFixtureActorMatrix` |

### FixtureComponent 蓝图节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetValueNoInterp` | **蓝图实现事件** — 接收单通道 DMX 值并应用到灯具效果（如 Pan/Tilt 角度） | `UDMXFixtureComponentSingle` |
| `SetChannel1ValueNoInterp` | **蓝图实现事件** — 接收第一通道值（如 Pan 粗调） | `UDMXFixtureComponentDouble` |
| `SetChannel2ValueNoInterp` | **蓝图实现事件** — 接收第二通道值（如 Pan 细调） | `UDMXFixtureComponentDouble` |
| `SetColorNoInterp` | **蓝图实现事件** — 接收颜色值（RGB/CMY/RGBW） | `UDMXFixtureComponentColor` |
| `InterpolateComponent` | **蓝图实现事件** — 插值帧回调，用于平滑过渡 | `UDMXFixtureComponent` |
| `GetDMXInterpolatedValue` | 获取当前插值后的值 | `UDMXFixtureComponentSingle` |
| `GetDMXTargetValue` | 获取目标值（插值终点） | `UDMXFixtureComponentSingle` |
| `IsDMXInterpolationDone` | 插值是否已完成 | `UDMXFixtureComponentSingle` |
| `GetParentFixtureActor` | 获取所属的 Fixture Actor | `UDMXFixtureComponent` |
| `GetTextureCenterColors` | 从纹理图集读取中心像素颜色（会锁定 GPU，慎用） | `UDMXFixtureComponent` |

### 使用示例（蓝图描述）

**创建一个基本 DMX 灯具 Blueprint：**

1. 创建新的 Blueprint 类，父类选择 `DMXFixtureActor`
2. 添加 Static Mesh 组件作为灯具外壳（透镜和光束体积）
3. 添加 `DMXFixtureComponentSingle` 子组件（如 Pan、Tilt、Dimmer），每个组件配置一个 DMX 属性名和值范围
4. 添加 `DMXFixtureComponentColor` 子组件处理颜色通道
5. 在 Construction Script 中调用 `InitializeFixture`，传入透镜和光束的 StaticMesh 组件引用
6. 在 Tick 中调用 `InterpolateDMXComponents`（如启用了插值）
7. 通过 DMXComponent 关联 Fixture Patch，DMX 数据会自动调用 `PushNormalizedValuesPerAttribute`

**为 Single 组件实现值回调：**

1. 选中 `DMXFixtureComponentSingle` 子组件
2. 在蓝图中实现 `SetValueNoInterp` 事件
3. 例如 Pan 组件：将 `NewValue` 映射到 Yaw 旋转，应用到 `Yoke` 场景组件

## C++ 用法

### 头文件引入

```cpp
#include "DMXFixtureActor.h"
#include "DMXFixtureActorMatrix.h"
#include "DMXFixtureComponent.h"
#include "DMXFixtureComponentSingle.h"
#include "DMXFixtureComponentDouble.h"
#include "DMXFixtureComponentColor.h"
```

### 基本用法

**获取灯具并推送 DMX 值（来自 `DMXFixtureActorBase.cpp`）：**

```cpp
// 获取场景中的 DMX Fixture Actor
ADMXFixtureActorBase* FixtureActor = /* ... */;

// 构造归一化属性值映射
FDMXNormalizedAttributeValueMap ValueMap;
ValueMap.Add(FDMXAttributeName("Intensity"), 0.75f);  // 75% 亮度
ValueMap.Add(FDMXAttributeName("Pan"), 0.5f);          // 居中

// 推送值到灯具 — 会自动分发给所有已启用的 FixtureComponent
FixtureActor->PushNormalizedValuesPerAttribute(ValueMap);
```

来源：`Private/DMXFixtureActorBase.cpp`

**初始化灯具（来自 `DMXFixtureActor.cpp`）：**

```cpp
// 在 BeginPlay 或构造后调用
ADMXFixtureActor* Fixture = GetMyFixtureActor();
Fixture->InitializeFixture(LensMeshComponent, BeamMeshComponent);

// 设置光照参数
Fixture->SetLightIntensityMax(5000.0f);
Fixture->SetLightDistanceMax(2000.0f);
Fixture->SetLightColorTemp(5600.0f);  // 日光色温
Fixture->SetLightCastShadow(true);
```

来源：`Private/DMXFixtureActor.cpp`

### 进阶用法

**自定义 FixtureComponent Single — 在子类中实现值回调：**

```cpp
// UDMXFixtureComponentSingle 的子类蓝图中实现 SetValueNoInterp
// C++ 中可以直接覆盖 PushNormalizedValuesPerAttribute

void UMyPanComponent::PushNormalizedValuesPerAttribute(
    const FDMXNormalizedAttributeValueMap& ValuePerAttribute)
{
    Super::PushNormalizedValuesPerAttribute(ValuePerAttribute);

    // 获取插值后的值并应用
    float PanValue = GetDMXInterpolatedValue();
    float AbsolutePan = NormalizedToAbsoluteValue(PanValue);
    // 应用到旋转...
}
```

来源：`Public/DMXFixtureComponentSingle.h`

**矩阵灯具推送像素数据：**

```cpp
ADMXFixtureActorMatrix* MatrixFixture = GetMatrixFixture();

// 构造像素数据数组
TArray<FDMXCell> PixelData;
// ... 填充每个像素的 DMX 通道数据

MatrixFixture->PushFixtureMatrixCellData(PixelData);
```

来源：`Public/DMXFixtureActorMatrix.h`

## Demo 示例

### 最小 DMX 灯具 C++ Actor

**MyDMXLight.Build.cs：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "DMXFixtures",
    "DMXRuntime"
});
```

**MyDMXLight.h：**
```cpp
#pragma once

#include "DMXFixtureActor.h"
#include "MyDMXLight.generated.h"

UCLASS()
class AMyDMXLight : public ADMXFixtureActor
{
    GENERATED_BODY()

public:
    AMyDMXLight();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> LensMesh;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> BeamMesh;
};
```

**MyDMXLight.cpp：**
```cpp
#include "MyDMXLight.h"
#include "Components/StaticMeshComponent.h"

AMyDMXLight::AMyDMXLight()
{
    LensMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Lens"));
    LensMesh->SetupAttachment(Head);

    BeamMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Beam"));
    BeamMesh->SetupAttachment(Head);
}

void AMyDMXLight::BeginPlay()
{
    Super::BeginPlay();
    InitializeFixture(LensMesh, BeamMesh);
}

void AMyDMXLight::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    InterpolateDMXComponents(DeltaTime);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 反射系统 |
| `DMXFixtureActorInterface` | 灯具 Actor 接口（MVR/GDTF 兼容） |
| `DMXRuntime` | DMX 运行时核心（FixturePatch、DMXComponent 等） |
| `DMXProtocol` | DMX 协议类型定义（属性名、信号格式等） |
| `Engine` | 引擎核心（Actor、组件系统） |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口（矩阵纹理更新） |
| `ProceduralMeshComponent` | 程序化网格（矩阵灯具的 LED 像素网格） |

**Plugin 依赖：**
- DMXEngine — DMX 数据模型和编辑器
- DMXModularFeatures — 灯具 Actor 接口模块
- DMXProtocol — Art-Net / sACN 协议支持
- ProceduralMeshComponent — 程序化网格生成

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-23 | `ed12aec` | DMX: Remove any uses of FORCEINLINE, replace with inline where appropriate | 代码规范清理，移除滥用的 FORCEINLINE 宏 |
| 2024-02-16 | `531e7a4` | DMX - DMXFixtureComponentDouble now applies its value range correctly | Bug 修复：Double 组件的值范围映射修正 |
| 2024-01-25 | `dbdd172` | CIS fix. | CI/编译修复 |

### 维护评价

- **创建时间**：2020 年 9 月，随 UE 4.25+ 的 DMX 系统一同引入
- **最近更新**：2025 年 6 月有代码规范更新，2024 年有实质 bug 修复，属于**活跃维护**状态
- **维护频率**：约每 1-2 年有更新，更新内容以 bug 修复和代码清理为主
- **稳定性**：核心 API 从 4.27 起趋于稳定，大量 deprecated 函数已迁移到新命名
- **推荐程度**：✅ **推荐使用** — 这是 Epic 官方维护的 DMX 灯具运行时实现，与 DMX 生态系统深度集成，适合所有 Virtual Production DMX 项目

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXFixtures)
- [DMXEngine Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXEngine) — DMX 数据模型和编辑器
- [DMXProtocol Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXProtocol) — Art-Net / sACN 协议实现
- [DMXModularFeatures Plugin](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/DMX/DMXModularFeatures) — 灯具 Actor 接口

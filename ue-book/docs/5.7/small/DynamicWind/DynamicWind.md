# Dynamic Wind

> Extremely experimental dynamic wind support for Nanite foliage.

| 属性 | 值 |
|---|---|
| 中文名 | 动态风 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图类型、参数结构体、资产用户数据） |
| 模块 | `DynamicWind` (Runtime), `DynamicWindEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind) | |

## 用途

Dynamic Wind 是一个**实验性**插件，为 **Nanite 实例化植被**（Instance Foliage with Nanite foliage types）提供基于骨骼动画（Skinning）的动态风模拟效果。它通过在运行时计算每根骨骼的风位移数据，驱动 Nanite 实例化骨骼网格组件的顶点变形，从而使大范围植被（如草地、灌木、树木）产生自然、流畅的摇摆动画。

核心原理：
- 利用 `UDynamicWindSkeletalData` 作为资产级别的配置（每根骨骼的风响应用力、组衰减等），附着在用于植被的 SkeletalMesh 上。
- 通过 `UDynamicWindSubsystem`（世界子系统）管理全局风参数（方向、速度、振幅、纹理等），并每帧将参数下发给渲染线程。
- 内部使用 `FDynamicWindTransformProvider` 连接 Nanite 的蒙皮变换管线，将风位移转化为骨骼变换数据，最终影响 Nanite 网格的呈现。

该插件解决的核心问题是：**为大规模 Nanite 植被提供高性能、可配置的动态风动画**，替代传统用 BoneAnim 或材质驱动的低效方案，利用 Nanite 的实例化渲染与 GPU 骨骼变形能力实现高效率。

## 使用场景

- 你需要为大规模植被（如草地、麦田、森林）添加流畅的风吹动画
- 项目使用 **Nanite Foliage** 以及**实例化骨骼网格组件**（`UInstancedSkinnedMeshComponent`）
- 希望精确控制每种植被（不同骨骼配置）对风的响应差异（如树干坚硬、树冠柔软、地面植被无上下衰减）
- 正在开发开放世界、自然环境类的游戏或模拟项目

## 蓝图用法

该插件主要暴露了一个世界子系统 `UDynamicWindSubsystem` 和一个结构体 `FDynamicWindParameters`，以及可在 SkeletalMesh 资产上配置的 `UDynamicWindSkeletalData`（Asset User Data）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Update Wind Parameters` | 更新全局动态风参数（方向、速度、振幅等） | `UDynamicWindSubsystem` |
| `Get Blended Wind Amplitude` | 获取当前平滑后的风振幅（可用于调试或次要效果） | `UDynamicWindSubsystem` |
| `FDynamicWindParameters` | 结构体，包含风模拟的所有可调属性（风速、方向、纹理等） | - |
| `Dynamic Wind Skeletal Data` | 可添加到 SkeletalMesh 资产中的自定义资产数据，用于启用并配置风对该骨骼的影响 | `UDynamicWindSkeletalData` |

### 使用示例（蓝图描述）

1. **启用植被的动态风**：  
   - 在内容浏览器中选择用作植被的 SkeletalMesh。  
   - 在资产详情面板中，添加 “Dynamic Wind Skeletal Data” 资产用户数据。  
   - 设置 `bIsEnabled = true`，并根据需要配置 `SimulationGroups`（定义骨骼影响组，如树干组、枝叶组）及各组的衰减参数。  

2. **驱动全局风参数**：  
   - 在关卡中获取 `Dynamic Wind Subsystem`（通过 “Get Dynamic Wind Subsystem” 节点）。  
   - 调用 `Update Wind Parameters`，将一个 `FDynamicWindParameters` 结构体传入（可在别处预填充）。  
   - 风参数会实时影响所有已注册的 Nanite 实例化骨骼植被。  

3. **读取当前风振幅（可选）**：  
   - 调用 `Get Blended Wind Amplitude` 获取平滑后的振幅值，可用于驱动其他效果（如音效、粒子系统）。  

## C++ 用法

### 头文件引入

```cpp
#include "DynamicWindSubsystem.h"         // 世界子系统
#include "DynamicWindSkeletalData.h"      // 骨骼数据配置
#include "DynamicWindParameters.h"        // 风参数结构体
```

### 基本用法

以下示例演示如何在 `AActor` 的 `BeginPlay` 中启用风并设置全局参数。

```cpp
// 来源示例：根据源码中的使用模式编写，非直接测试用例
void AMyWindController::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取 DynamicWind 世界子系统
    if (UWorld* World = GetWorld())
    {
        UDynamicWindSubsystem* WindSubsystem = World->GetSubsystem<UDynamicWindSubsystem>();
        if (WindSubsystem)
        {
            // 2. 构建风参数结构体
            FDynamicWindParameters Params;
            Params.WindDirection = FVector(1.0f, 0.0f, 0.0f); // 风向
            Params.WindSpeed = 20.0f;
            Params.WindAmplitude = 1.5f;
            Params.SimulationCenter = GetActorLocation();
            Params.SimulationExtents = 5000.0f; // 模拟半径

            // 3. 更新风参数
            WindSubsystem->UpdateWindParameters(Params);

            // 4. 可选：读取当前振幅（用于调试）
            float BlendedAmplitude = WindSubsystem->GetBlendedWindAmplitude();
            UE_LOG(LogTemp, Log, TEXT("Dynamic Wind blended amplitude: %f"), BlendedAmplitude);
        }
    }
}
```

### 进阶用法

**为 SkeletalMesh 资产注册风骨骼数据**（C++ 中动态添加 `UDynamicWindSkeletalData`）：

```cpp
#include "DynamicWindSkeletalData.h"

void RegisterWindForSkeletalMesh(USkeletalMesh* Mesh)
{
    if (!Mesh) return;

    // 检查是否已有 DynamicWind 数据
    UDynamicWindSkeletalData* WindData = Mesh->GetAssetUserData<UDynamicWindSkeletalData>();
    if (!WindData)
    {
        WindData = NewObject<UDynamicWindSkeletalData>(Mesh);
        Mesh->AddAssetUserData(WindData);
    }

    // 启用风
    WindData->bIsEnabled = true;

    // 配置模拟组（每个组定义骨骼影响）
    // 例如：组0为树干（高刚度），组1为树冠（低刚度）
    FDynamicWindSimulationGroupData TrunkGroup;
    TrunkGroup.bUseDualInfluence = false;
    TrunkGroup.Influence = 0.1f;               // 微弱影响
    TrunkGroup.bIsTrunkGroup = true;

    FDynamicWindSimulationGroupData CrownGroup;
    CrownGroup.bUseDualInfluence = true;
    CrownGroup.MinInfluence = 0.3f;
    CrownGroup.MaxInfluence = 0.9f;
    CrownGroup.ShiftTop = 1.0f;                // 从骨骼顶部开始影响

    WindData->SimulationGroups.Add(TrunkGroup);
    WindData->SimulationGroups.Add(CrownGroup);

    // 注意：SimulationGroupBones 映射由工具或算法自动填充，此处仅演示配置结构体
}
```

**使用风参数结构体**（在任意 Actor 中构建 `FDynamicWindParameters`）：

```cpp
FDynamicWindParameters CreateWindForTimeOfDay(float TimeOfDay)
{
    FDynamicWindParameters Params;
    // 模拟白天强风，夜晚轻风
    Params.WindAmplitude = FMath::Lerp(0.5f, 2.0f, FMath::Sin(TimeOfDay * PI));
    Params.WindDirection = FVector(1.0f, 0.5f, 0.0f).GetSafeNormal();
    Params.WindSpeed = 15.0f;
    // 可选：使用 WindTexture 来控制空间变化
    return Params;
}
```

## Demo 示例

以下是一个最小化可编译 `AActor` 类，它启动时启用风并每帧更新风方向以产生旋转效果。

**WindDemoActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DynamicWindParameters.h"
#include "WindDemoActor.generated.h"

UCLASS()
class AWindDemoActor : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    float ElapsedTime = 0.0f;
};
```

**WindDemoActor.cpp**

```cpp
#include "WindDemoActor.h"
#include "DynamicWindSubsystem.h"

void AWindDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (UWorld* World = GetWorld())
    {
        UDynamicWindSubsystem* WindSubsystem = World->GetSubsystem<UDynamicWindSubsystem>();
        if (WindSubsystem)
        {
            // 初始风参数
            FDynamicWindParameters Params;
            Params.WindDirection = FVector::ForwardVector;
            Params.WindSpeed = 20.0f;
            Params.WindAmplitude = 1.0f;
            Params.SimulationCenter = GetActorLocation();
            Params.SimulationExtents = 10000.0f;
            WindSubsystem->UpdateWindParameters(Params);
        }
    }
}

void AWindDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    ElapsedTime += DeltaTime;

    if (UWorld* World = GetWorld())
    {
        UDynamicWindSubsystem* WindSubsystem = World->GetSubsystem<UDynamicWindSubsystem>();
        if (WindSubsystem)
        {
            // 旋转风向
            float Angle = FMath::Sin(ElapsedTime * 0.1f) * 90.0f; // 缓慢左右摆动
            FVector NewDir = FRotator(0.0f, Angle, 0.0f).RotateVector(FVector::ForwardVector);

            FDynamicWindParameters Params;
            Params.WindDirection = NewDir;
            Params.WindSpeed = 20.0f;
            Params.WindAmplitude = 1.0f + 0.5f * FMath::Sin(ElapsedTime * 0.5f); // 振幅脉动
            Params.SimulationCenter = GetActorLocation();
            Params.SimulationExtents = 10000.0f;

            WindSubsystem->UpdateWindParameters(Params);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 变换提供数据基类（`UTransformProviderData`） |
| `Skinning` | 蒙皮变换提供器接口（`FSkinningTransformProvider`） |
| `Nanite` | 纳米网格场景代理（`Nanite::FSkinnedSceneProxy`） |
| `RenderCore` | HLSL 类型别名（`HLSLTypeAliases.h`） |

> 所有依赖均为 UE5 标准引擎模块，无需额外插件。

## 维护状态

### 近期更新

- 2025-12-18 e62fa711 — [DynamicWind] 修复 GT/RT 交互中的线程安全问题
- 2025-10-14 650ef5e2 — 移除析构函数中显式的 UnregisterProvider 调用（FScene 自行负责清理）
- 2025-09-10 89a482da — 修复使用实例化蒙皮组件时 DynamicWind 提供的崩溃
- 2025-09-08 1182f57f — 全局风方向对每实例旋转的正确支持
- 2025-09-03 06e395f9 — 初始提交，创建插件并集成到 ProceduralVegetationEditor

### 维护评价

- 该插件于 2025-09-03 创建，非常新（约 4 个月）。
- 截至最新提交（2025-12-18），平均每 3-4 周有功能性或稳定性更新，修复了几个关键崩溃和线程安全问题，表明团队正在积极维护。
- **实验性标注依然存在**，API 有弃用标记（`UE_DEPRECATED`），说明内部架构仍在调整中，不建议在正式产品中依赖其稳定性。
- 推荐在原型开发或研究项目中使用，追踪后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DynamicWind)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（暂无独立页面，可关注 Nanite 文档）
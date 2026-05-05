# Apex Destruction

> APEX implementation of destruction

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApexDestruction` (Runtime), `ApexDestructionEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2017-07-26 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ApexDestruction) | |

## 用途

Apex Destruction 是基于 NVIDIA APEX 物理库的可破坏网格（Destructible Mesh）系统。它允许将静态网格体（StaticMesh）预切割为多个碎片（chunk），在运行时通过物理模拟实现物体的破碎效果。

**⚠️ 重要警告：此插件已被废弃。** 从 UE 4.26 起，APEX 相关类型均标记为 `UE_DEPRECATED`，引擎在运行时会输出警告日志。Epic 官方推荐使用 **Chaos Destruction**（通过 `GeometryCollection` + `GeometryCollectionComponent`）替代此插件。此插件仅保留用于旧项目的兼容性迁移。

在 APEX 废弃之前，这个插件是 UE4 中实现可破坏环境的主要方式，广泛用于射击游戏中的掩体破坏、建筑坍塌、玻璃破碎等场景。

## 使用场景

> ⚠️ 以下为历史参考。新项目应使用 Chaos Destruction。

- 你需要让墙壁/柱子等静态物体在被射击或爆炸时碎裂 → 使用 DestructibleMesh + DestructibleActor
- 你需要对可破坏物体施加点伤害或范围伤害 → 使用 `ApplyDamage` / `ApplyRadiusDamage`
- 你需要控制碎片的生命周期、最大分离距离等行为 → 通过 `FDestructibleParameters` 配置
- 你需要从 StaticMesh 创建破碎效果 → 在编辑器中使用 DestructibleMesh 资产工作流

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyDamage` | 对可破坏物体施加点伤害（指定命中位置和冲击方向） | `UDestructibleComponent` |
| `ApplyRadiusDamage` | 对可破坏物体施加范围伤害（指定原点和半径） | `UDestructibleComponent` |
| `SetDestructibleMesh` | 设置可破坏网格资产 | `UDestructibleComponent` |
| `GetDestructibleMesh` | 获取当前可破坏网格资产 | `UDestructibleComponent` |
| `OnComponentFracture` | 碎裂事件委托（组件级别） | `UDestructibleComponent` |
| `OnActorFracture` | 碎裂事件委托（Actor 级别） | `ADestructibleActor` |

### 关键属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `bFractureEffectOverride` | `bool` | 是否使用组件级别的碎裂效果覆盖资产默认效果 | `UDestructibleComponent` |
| `FractureEffects` | `TArray<FFractureEffect>` | 各层级的碎裂效果（粒子/声效） | `UDestructibleComponent` |
| `bEnableHardSleeping` | `bool` | 启用硬睡眠：碎片休眠时变为 kinematic，受到足够伤害可重新激活 | `UDestructibleComponent` |
| `LargeChunkThreshold` | `float` | 判定大碎片的最小尺寸阈值（默认 25.0） | `UDestructibleComponent` |

### 使用示例（蓝图描述）

**施加点伤害：**
1. 拥有一个 `ADestructibleActor`（或带 `UDestructibleComponent` 的 Actor）
2. 从该 Actor 获取 `DestructibleComponent` 引用
3. 调用 `ApplyDamage`，传入伤害值、命中位置（`HitLocation`）、冲击方向（`ImpulseDir`）和冲量强度（`ImpulseStrength`）

**施加范围伤害：**
1. 获取目标 `UDestructibleComponent` 引用
2. 调用 `ApplyRadiusDamage`，传入基础伤害、爆炸原点（`HurtOrigin`）、伤害半径（`DamageRadius`）、冲量强度和是否全伤害（`bFullDamage`）

**监听碎裂事件：**
1. 获取目标组件引用
2. 绑定 `OnComponentFracture` 或 Actor 上的 `OnActorFracture` 委托
3. 委托提供 `HitPoint`（命中点）和 `HitDirection`（命中方向）两个参数

## C++ 用法

### 头文件引入

```cpp
#include "DestructibleComponent.h"
#include "DestructibleActor.h"
#include "DestructibleMesh.h"
```

### 基本用法

从 `DestructibleComponent.cpp` 和 `DestructibleActor.cpp` 提取的典型用法：

```cpp
// 获取 DestructibleActor 上的组件
ADestructibleActor* DestActor = /* ... */;
UDestructibleComponent* DestComp = DestActor->GetDestructibleComponent();

// 施加点伤害
DestComp->ApplyDamage(
    100.0f,                    // DamageAmount - 伤害量
    HitLocation,               // HitLocation - 命中世界坐标
    ImpulseDirection,          // ImpulseDir - 冲击方向
    500.0f                     // ImpulseStrength - 冲量强度
);

// 施加范围伤害
DestComp->ApplyRadiusDamage(
    200.0f,                    // BaseDamage - 基础伤害
    ExplosionOrigin,           // HurtOrigin - 爆炸原点
    500.0f,                    // DamageRadius - 伤害半径
    1000.0f,                   // ImpulseStrength - 冲量强度
    false                      // bFullDamage - 是否在半径内全伤害
);
```

*来源：`Source/ApexDestruction/Private/DestructibleComponent.cpp`*

### 监听碎裂事件

```cpp
// 绑定组件碎裂委托
DestComp->OnComponentFracture.AddDynamic(this, &AMyActor::OnFracture);

// 回调函数
UFUNCTION()
void OnFracture(const FVector& HitPoint, const FVector& HitDirection);
```

*来源：`Source/ApexDestruction/Public/DestructibleComponent.h`，`FComponentFractureSignature` 委托定义*

### 进阶用法

**从 StaticMesh 构建 DestructibleMesh（编辑器代码）：**

```cpp
#include "DestructibleMesh.h"

// 从 StaticMesh 创建 DestructibleMesh
UDestructibleMesh* DestMesh = NewObject<UDestructibleMesh>();
bool bSuccess = DestMesh->BuildFromStaticMesh(*SourceStaticMesh);

// 创建断裂设置
DestMesh->CreateFractureSettings();

// 从 FBX 碎片网格设置子块
TArray<UStaticMesh*> ChunkMeshes;
DestMesh->SetupChunksFromStaticMeshes(ChunkMeshes);
```

*来源：`Source/ApexDestruction/Private/DestructibleMesh.cpp`*

**配置破坏参数（通过 C++ 设置 FDestructibleParameters）：**

```cpp
#include "DestructibleMesh.h"

UDestructibleMesh* Mesh = DestComp->GetDestructibleMesh();
FDestructibleParameters& Params = Mesh->DefaultDestructibleParameters;

// 伤害参数
Params.DamageParameters.DamageThreshold = 10.0f;    // 碎裂伤害阈值
Params.DamageParameters.DamageSpread = 0.2f;         // 伤害传播系数
Params.DamageParameters.bEnableImpactDamage = true;  // 启用碰撞伤害
Params.DamageParameters.ImpactDamage = 0.1f;         // 碰撞伤害系数

// 碎片参数
Params.DebrisParameters.DebrisLifetimeMin = 2.0f;    // 碎片最短存活时间
Params.DebrisParameters.DebrisLifetimeMax = 10.0f;   // 碎片最长存活时间

// 标志
Params.Flags.bAccumulateDamage = true;       // 累积伤害（多次小伤害最终碎裂）
Params.Flags.bFormExtendedStructures = true; // 与相邻可破坏物体形成支撑结构
```

*来源：`Source/ApexDestruction/Public/DestructibleMesh.h`*

### 接口使用（IDestructibleInterface）

`UDestructibleComponent` 实现了 `IDestructibleInterface`，该接口定义在引擎核心模块中：

```cpp
// Engine/Source/Runtime/Engine/Public/DestructibleInterface.h
class IDestructibleInterface
{
    virtual void ApplyDamage(float DamageAmount, const FVector& HitLocation,
                             const FVector& ImpulseDir, float ImpulseStrength) = 0;
    virtual void ApplyRadiusDamage(float BaseDamage, const FVector& HurtOrigin,
                                   float DamageRadius, float ImpulseStrength,
                                   bool bFullDamage) = 0;
};
```

可以通过 `IDestructibleInterface` 多态调用，无需知道具体类型。

## Demo 示例

> ⚠️ 此插件已被废弃，以下示例仅用于理解历史 API 结构。新项目请使用 Chaos Destruction。

### 最小使用示例（C++）

**MyDestructibleActor.h：**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDestructibleActor.generated.h"

class UDestructibleComponent;

UCLASS()
class AMyDestructibleActor : public AActor
{
    GENERATED_BODY()

public:
    AMyDestructibleActor();

    UFUNCTION(BlueprintCallable)
    void TakeHit(float Damage, FVector HitLocation, FVector HitDir);

    UFUNCTION()
    void OnFracture(const FVector& HitPoint, const FVector& HitDirection);

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UDestructibleComponent> DestructibleComp;
};
```

**MyDestructibleActor.cpp：**
```cpp
#include "MyDestructibleActor.h"
#include "DestructibleComponent.h"

AMyDestructibleActor::AMyDestructibleActor()
{
    DestructibleComp = CreateDefaultSubobject<UDestructibleComponent>(TEXT("Destructible"));
    RootComponent = DestructibleComp;
    DestructibleComp->OnComponentFracture.AddDynamic(this, &AMyDestructibleActor::OnFracture);
}

void AMyDestructibleActor::TakeHit(float Damage, FVector HitLocation, FVector HitDir)
{
    DestructibleComp->ApplyDamage(Damage, HitLocation, HitDir, 500.0f);
}

void AMyDestructibleActor::OnFracture(const FVector& HitPoint, const FVector& HitDirection)
{
    UE_LOG(LogTemp, Log, TEXT("Fractured at %s, direction %s"),
        *HitPoint.ToString(), *HitDirection.ToString());
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ApexDestruction",
    "Core",
    "CoreUObject",
    "Engine"
});
```

## 模块依赖

### ApexDestruction（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor、Component、物理系统等 |
| `RHI` | 渲染硬件接口 |
| `RenderCore` | 渲染核心功能 |
| `NavigationSystem` | 导航网格几何体导出 |

### ApexDestructionEditor（UncookedOnly 模块）

| 模块 | 用途 |
|---|---|
| `ApexDestruction` | 运行时模块依赖 |
| `AssetTools` | 资产类型注册 |
| `InputCore` | 编辑器输入 |
| `Slate` / `SlateCore` | UI 框架 |
| `EditorStyle` | 编辑器样式 |
| `EditorFramework` / `UnrealEd` | 编辑器框架 |
| `DesktopPlatform` | 桌面平台功能 |
| `AssetRegistry` | 资产注册表 |
| `ContentBrowser` | 内容浏览器集成 |
| `Projects` | 项目信息 |
| `FBX`（ThirdParty） | FBX 导入支持 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-14 | `8c4cad9` | Changed all WITH_EDITORONLY_DATA properties in StaticMesh to have accessor | 引擎重构 StaticMesh 属性访问器，ApexDestruction 被动适配 |
| 2024-11-22 | `04a0ec7` | Fix errors with latest compiler | 编译器兼容性修复，非功能更新 |
| 2023-11-15 | `b64f2e2` | [Deprecation Cleanup] Remove deprecated code in actor factory class | 清理废弃代码，缩减编辑器模块 |

### 维护评价

- **创建时间**：2017 年 7 月，由 APEX 模块从 UE4 主仓库拆分为独立插件时创建
- **废弃时间**：UE 4.26（2020 年）标记全部 APEX 类型为 `UE_DEPRECATED`
- **功能状态**：核心物理模拟功能已掏空——`ApplyDamage`、`ApplyRadiusDamage`、力/冲量方法等的函数体均为空实现（`{}`），仅保留接口签名和序列化兼容性
- **最近更新**：仅被动适配引擎重构（编译修复、接口变化），无实质性功能更新
- **维护评价**：**可能废弃** — 已超过 5 年无功能性更新，所有 APEX 物理依赖（PhysX、APEX 库）已从 Build.cs 中注释掉
- **建议**：**不要在新项目中使用此插件**。现有项目应迁移至 Chaos Destruction（`GeometryCollection` + `GeometryCollectionComponent`）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ApexDestruction)
- [DestructibleInterface 源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Public/DestructibleInterface.h)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）

## 迁移指引

如果你的项目仍在使用 Apex Destruction，应迁移到 Chaos Destruction：

| Apex Destruction | Chaos Destruction 替代 |
|---|---|
| `UDestructibleMesh` | `UGeometryCollection` |
| `UDestructibleComponent` | `UGeometryCollectionComponent` |
| `ADestructibleActor` | 带 `UGeometryCollectionComponent` 的 Actor |
| `ApplyDamage()` | `ApplyExternalStrain()` / `ApplyBreakingLinearVelocity()` |
| `ApplyRadiusDamage()` | `ApplyBreakingLinearVelocity()` + `ApplyBreakingAngularVelocity()` |
| `FDestructibleParameters` | `FGeometryCollectionDamagePropagationData` |
| Voronoi 碎裂 | 编辑器内置 Geometry Editing 工具或外部 DCC（Houdini 等）预切割 |

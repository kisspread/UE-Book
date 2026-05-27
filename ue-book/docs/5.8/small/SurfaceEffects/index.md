# SurfaceEffects

> A flexible, context-driven surface system

| 属性 | 值 |
|---|---|
| 中文名 | 表面效果系统 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SurfaceEffects` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-16 |
| 年龄标签 | 👴 老古董（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects) | |

## 用途

该插件提供了一个数据驱动的框架，用于管理游戏中的“表面类型”或“物理材质类型”。传统上，表面类型（如草地、金属、木头）通常在物理材质或资产属性中硬编码，导致与特定资产（如网格体）强耦合。

SurfaceEffects 插件的核心是一个子系统（`USurfaceEffectsSubsystem`），它通过一个可配置的**数据表**和**规则资产**来动态地解析表面类型。规则可以根据任意上下文（例如角色移动方向、武器类型、天气条件等）来决定返回哪种表面效果。这解决了硬编码的耦合问题，为声音、粒子特效、脚印、车辆行为等提供了极大的灵活性和可配置性。

## 使用场景

- 你需要为不同类型的角色（或武器）在同样的地面上播放不同的脚步声或特效。
- 你正在开发一个开放世界游戏，希望根据天气、地形坡度或游戏内时间动态改变地面材质的表现。
- 你希望美术或设计师能够通过数据表而非代码来调整和迭代表面效果逻辑。
- 你希望实现一个统一的表面查询接口，避免在代码各处散落复杂的条件判断。

## 蓝图用法

该插件主要通过C++接口使用。蓝图层面的主要交互点是**数据表**和**规则数据资产**的编辑。核心的查询函数 `GetSurface` 是一个C++模板函数，在蓝图中不易直接使用。通常需要创建一个包装函数或宏来暴露给蓝图。

### 核心节点（概念）

| 节点 | 说明 | 所在类 |
|---|---|---|
| （配置）数据表 | 在项目设置中指定用于存放表面规则的数据表资产 | `USurfaceEffectsSettings` |
| （配置）规则行 | 在数据表中，每一行对应一个 `UEnum` 类型（如 `EPhysicalSurface`），并关联一个规则资产 `USurfaceEffectRule` | `FSurfaceEffectTableRow` |

### 使用示例（蓝图描述）

1.  **创建一个表面枚举**：例如，创建一个 `EPhysicalSurface` 的枚举，包含 `Grass`, `Metal`, `Wood` 等值。
2.  **创建规则数据资产**：创建一个继承自 `USurfaceEffectRule` 的蓝图或C++类。在类的蓝图或 `GetSurface` 虚函数中实现你的逻辑，根据传入的 `Context` 决定返回哪个表面枚举值。
3.  **配置数据表**：
    - 在项目设置（Project Settings）中找到 “Surface Effects” 分类，指定你的数据表资产。
    - 在该数据表中添加一行，行名设置为你的枚举类型名称（例如 `EPhysicalSurface`）。
    - 在该行的 `Rule` 属性中，指向你创建的规则数据资产。
4.  **C++查询**：在C++代码中，获取 `USurfaceEffectsSubsystem`，然后调用 `GetSurface<YourSurfaceEnum>(Context)` 来获取动态确定的表面类型。

## C++ 用法

### 头文件引入

```cpp
#include "SurfaceEffectsSubsystem.h"
```

### 基本用法

1.  **定义你的表面枚举和上下文**。
2.  **创建自定义规则**。
3.  **通过子系统查询**。

```cpp
// 1. 定义你的表面枚举和上下文 (示例，假设已有)
UENUM(BlueprintType)
enum class EMySurfaceType : uint8
{
    Default,
    Grass,
    Metal,
    Wood,
    NUM UMETA(Hidden)
};

struct FMyMovementContext : public FSurfaceEffectContextBase
{
    // 可添加自定义上下文数据，例如：
    // FVector ImpactNormal;
    // AActor* Instigator;
};

// 2. 创建自定义规则 (通常在单独的文件中)
UCLASS()
class UMySurfaceEffectRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        // 将基类Context转换为你定义的上下文
        const FMyMovementContext& MyContext = static_cast<const FMyMovementContext&>(Context);
        // 根据MyContext中的信息进行判断
        // 例如，如果撞击法线Z分量大于0.7，则返回草地
        // OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Grass);
        // return true;
        return false; // 示例
    }
};

// 3. 通过子系统查询表面类型
void SomeActorFunction()
{
    if (USurfaceEffectsSubsystem* SurfaceSubsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>())
    {
        FMyMovementContext Context;
        // 填充Context...

        TSurfaceEffectResult<EMySurfaceType> Result = SurfaceSubsystem->GetSurface<EMySurfaceType>(Context);
        if (Result.bSuccess)
        {
            EMySurfaceType ResolvedSurface = Result.OutSurface;
            // 根据ResolvedSurface播放对应的声音、特效等
        }
    }
}
```
*（示例结构参考 `Source/SurfaceEffects/Public/SurfaceEffectsSubsystem.h` 中的 `GetSurface` 模板函数和 `FSurfaceEffectTableRow`）*

### 进阶用法

利用上下文实现更复杂的规则。例如，创建一个考虑“玩家当前持有武器”和“地面材质”的复合规则：

```cpp
struct FWeaponImpactContext : public FSurfaceEffectContextBase
{
    FName WeaponName;
    FVector ImpactLocation;
};

UCLASS()
class UWeaponBasedSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        const FWeaponImpactContext& WeaponContext = static_cast<const FWeaponImpactContext&>(Context);
        if (WeaponContext.WeaponName == FName("EnergySword"))
        {
            // 能量剑碰撞总是产生特殊的能量表面效果，忽略地面材质
            OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Energy);
            return true;
        }
        // 否则，可以查询另一个基础规则或使用默认逻辑
        return false;
    }
};
```

## Demo 示例

一个最小的可运行示例，展示如何创建自定义规则并查询。

```cpp
// MySurfaceEffectsDemo.h
#pragma once

#include "CoreMinimal.h"
#include "SurfaceEffectsSubsystem.h" // 关键头文件
#include "MySurfaceEffectsDemo.generated.h"

// 自定义表面枚举
UENUM(BlueprintType)
enum class EDemoSurface : uint8
{
    Hard,
    Soft,
    NUM UMETA(Hidden)
};

// 自定义上下文
struct FDemoContext : public FSurfaceEffectContextBase
{
    float SurfaceHardness; // 例如，通过物理材质计算得到
};

// 自定义规则
UCLASS()
class UDemoSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()
public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        const FDemoContext& DemoCtx = static_cast<const FDemoContext&>(Context);
        if (DemoCtx.SurfaceHardness > 0.8f)
        {
            OutSurfaceValue = static_cast<uint8>(EDemoSurface::Hard);
            return true;
        }
        else
        {
            OutSurfaceValue = static_cast<uint8>(EDemoSurface::Soft);
            return true;
        }
    }
};

// 示例Actor
UCLASS()
class ADemoSurfaceActor : public AActor
{
    GENERATED_BODY()
public:
    void QuerySurface();
};

// MySurfaceEffectsDemo.cpp
#include "MySurfaceEffectsDemo.h"

void ADemoSurfaceActor::QuerySurface()
{
    // 假设项目设置中已配置好包含 EDemoSurface 行的数据表
    USurfaceEffectsSubsystem* Subsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();
    if (Subsystem)
    {
        FDemoContext Context;
        Context.SurfaceHardness = 0.9f; // 模拟一个硬表面

        TSurfaceEffectResult<EDemoSurface> Result = Subsystem->GetSurface<EDemoSurface>(Context);
        if (Result.bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Resolved Surface: %s"), Result.OutSurface == EDemoSurface::Hard ? TEXT("Hard") : TEXT("Soft"));
        }
    }
}
```

## 模块依赖

该插件本身只依赖其自有的 `SurfaceEffects` 模块。使用它的项目模块需要添加对 `SurfaceEffects` 的依赖。

| 模块 | 用途 |
|---|---|
| `SurfaceEffects` | 提供表面效果子系统、规则基类和数据结构。**你的项目模块必须依赖此模块** |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 构建相关更新，为Fortnite客户端目标添加DLL导出规范，涉及方法和静态变量 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 修复插件描述文件，更新同时标记为实验性和测试版的插件配置 |
| 2024-01-30 | `fac760fa` | First implementation of Surface Effects MVP - Footsteps | 表面效果系统的MVP首次实现，用于脚步声效果 |

### 维护评价

该插件创建于 2024 年初，目前处于 **实验性（Experimental）** 阶段。从 Git 历史看，自 2024 年 1 月的初始实现和 2024 年 11 月的配置更新后，最近一次功能性更新是 2025 年 4 月，但主要是构建层面的调整，而非功能增强或Bug修复。

**核心功能（子系统、规则、数据表结构）已经稳定且可用**，其设计理念（数据驱动、上下文感知）非常先进和实用。然而，作为实验性插件，它可能还未经过大规模生产项目的验证，API 未来可能会有变动。

**推荐**：如果你的项目正在寻找一种灵活、数据驱动的表面效果解决方案，并且愿意接受其“实验性”状态可能带来的未来变更，可以考虑使用它并从中受益。否则，建议基于类似思想构建自己的系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的信息中发现标准测试用例)
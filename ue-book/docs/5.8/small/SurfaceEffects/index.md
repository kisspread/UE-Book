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
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects) | |

## 用途

`SurfaceEffects` 插件提供了一个灵活、可扩展的框架，用于根据上下文（例如游戏状态、玩家输入、环境条件）动态确定表面类型（通常表示为枚举值）。它解决了在复杂游戏逻辑中，需要根据不同情况返回不同表面效果（如脚步声、材质着色、粒子效果）时，避免硬编码逻辑和大量条件判断的问题。

该系统的核心是一个基于数据表的规则引擎。开发者通过定义 `USurfaceEffectRule` 的子类来实现具体的匹配逻辑，并将这些规则配置在数据表中。运行时，通过 `USurfaceEffectsSubsystem` 子系统查询，传入上下文，即可得到正确的表面枚举值。

## 使用场景

- **音效系统**：根据角色状态（如蹲伏、奔跑）和地面材质，播放不同的脚步声。例如，雨天泥地上的跑步声与晴天木地板上的脚步声不同。
- **物理交互**：子弹或物体击中不同表面时，需要产生不同的音效、弹痕或粒子效果。
- **角色动画**：角色在雪地、沙地、水面上的移动动画可能需要有不同的视觉效果或混合权重。
- **任何需要根据上下文动态决定“表面类型”或“材质类型”的游戏系统**，而不仅仅是物理材质。

## 蓝图用法

该插件的设计更偏向于 C++ 数据驱动，但蓝图系统可以通过 `USurfaceEffectsSubsystem` 进行访问。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSurface<TEnum>` | 模板函数，根据上下文查询并返回一个特定枚举类型的表面结果。是系统的核心查询接口。 | `USurfaceEffectsSubsystem` |

### 使用示例（蓝图描述）

虽然该插件没有直接提供蓝图节点，但可以通过以下方式在蓝图中使用：
1.  **获取子系统**：在蓝图中通过 `Get Game Instance Subsystem` 节点获取 `USurfaceEffectsSubsystem`。
2.  **查询表面**：调用子系统的函数（需要 C++ 暴露或自定义蓝图函数库包装）。由于 `GetSurface` 是模板函数，在蓝图中直接调用不便，通常会在 C++ 中创建非模板化的包装函数供蓝图使用。

## C++ 用法

### 头文件引入

```cpp
#include "SurfaceEffectsSubsystem.h"
#include "SurfaceEffectsSettings.h"
#include "SurfaceEffectContextBase.h" // 上下文基类，通常已包含
```

### 基本用法

**1. 配置数据表**
首先，需要在项目设置中指定一个数据表资产（路径见 `USurfaceEffectsSettings`）。
**来源文件**: `Source/SurfaceEffects/Public/SurfaceEffectsSettings.h`

**2. 定义自定义表面枚举**
```cpp
UENUM()
enum class EMySurfaceType : uint8
{
    Default,
    Concrete,
    Wood,
    Metal,
    Water,
    Snow,
    MAX // 枚举最大值标记
};
```

**3. 实现自定义规则**
从 `USurfaceEffectRule` 派生，重写 `GetSurface` 函数，根据上下文决定返回的枚举值。
**来源文件**: `Source/SurfaceEffects/Public/SurfaceEffectsSubsystem.h` 中的 `USurfaceEffectRule` 定义。

```cpp
UCLASS()
class UMySurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        // 示例逻辑：根据上下文中的某个布尔值决定返回木头还是默认表面
        const FMySurfaceContext* MyContext = static_cast<const FMySurfaceContext*>(&Context);
        if (MyContext && MyContext->bIsIndoors)
        {
            OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Wood);
            return true;
        }
        OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Default);
        return true;
    }
};
```

**4. 在运行时查询表面**
```cpp
// 获取子系统
USurfaceEffectsSubsystem* SurfaceSubsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();

// 准备上下文
FMySurfaceContext Context;
Context.bIsIndoors = true;
Context.Location = GetActorLocation();

// 查询表面（指定枚举类型）
TSurfaceEffectResult<EMySurfaceType> Result = SurfaceSubsystem->GetSurface<EMySurfaceType>(Context);

if (Result.bSuccess)
{
    EMySurfaceType Surface = Result.OutSurface;
    // 根据 Surface 执行相应逻辑，播放音效等
}
```
**来源文件**: `Source/SurfaceEffects/Public/SurfaceEffectsSubsystem.h` 中的 `GetSurface` 模板函数。

### 进阶用法

结合数据资产和数据表，实现完全数据驱动的表面规则分配。
1.  在编辑器中创建 `UMySurfaceRule` 的数据资产子类。
2.  将该数据资产指派给一个 `FSurfaceEffectTableRow` 结构体。
3.  将该行添加到项目设置中指定的 `UDataTable` 中，行名为你的表面枚举 `UEnum` 的名称（例如 `“EMySurfaceType”`）。
4.  在代码中查询时，系统会自动根据行名找到对应的规则资产并执行。

## Demo 示例

**自定义枚举与规则 (MySurfaceTypes.h):**
```cpp
// MySurfaceTypes.h
#pragma once

#include "CoreMinimal.h"
#include "SurfaceEffectsSubsystem.h"
#include "MySurfaceTypes.generated.h"

UENUM()
enum class EMySurfaceType : uint8
{
    Default,
    Concrete,
    Wood,
    Metal,
    Water,
    Snow,
    MAX
};

USTRUCT()
struct FMySurfaceContext : public FSurfaceEffectContextBase
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bIsIndoors = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    FVector Location = FVector::ZeroVector;
};

UCLASS()
class UMySurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()
public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        const FMySurfaceContext* MyContext = static_cast<const FMySurfaceContext*>(&Context);
        if (MyContext)
        {
            // 简单的示例逻辑
            if (MyContext->bIsIndoors)
            {
                OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Wood);
                return true;
            }
            // 可以加入基于 Location 的更复杂逻辑
            if (MyContext->Location.Z < 0) // 例如水下
            {
                OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Water);
                return true;
            }
        }
        OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Default);
        return true;
    }
};
```

**使用示例 (MyActor.cpp):**
```cpp
// MyActor.cpp
#include "MySurfaceTypes.h"
#include "GameFramework/GameInstance.h"

void AMyActor::PlayStepSound()
{
    USurfaceEffectsSubsystem* Subsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();
    if (!Subsystem) return;

    FMySurfaceContext Context;
    Context.bIsIndoors = IsIndoors(); // 假设的函数
    Context.Location = GetActorLocation();

    TSurfaceEffectResult<EMySurfaceType> Result = Subsystem->GetSurface<EMySurfaceType>(Context);

    if (Result.bSuccess)
    {
        switch (Result.OutSurface)
        {
        case EMySurfaceType::Wood:
            // 播放木地板脚步声
            UGameplayStatics::PlaySoundAtLocation(this, WoodStepSound, GetActorLocation());
            break;
        case EMySurfaceType::Concrete:
            // 播放水泥地脚步声
            UGameplayStatics::PlaySoundAtLocation(this, ConcreteStepSound, GetActorLocation());
            break;
        // ... 其他情况
        default:
            UGameplayStatics::PlaySoundAtLocation(this, DefaultStepSound, GetActorLocation());
            break;
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 可能与规则系统或配置相关联，用于标记上下文或表面类型。（基于设置类的 Category 推断） |

**注意**: 插件本身依赖很少，但你的项目需要依赖 `SurfaceEffects` 模块才能使用其功能。在 `.Build.cs` 文件中添加 `"SurfaceEffects"` 到 `PublicDependencyModuleNames` 或 `PrivateDependencyModuleNames`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 针对 Fortnite 项目的构建目标调整，修改了方法和静态变量的 DLL 导出属性，属于构建配置优化。 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 更新了同时标记为实验性和测试版的 .uplugin 文件，统一描述格式。 |
| 2024-01-30 | `fac760fa` | First implementation of Surface Effects MVP - Footsteps | 表面效果系统首个最小可行版本实现，用于处理脚步声。 |
| 2024-01-29 | `962fd46c` | [Backout] - CL30970339 | 回退了之前的某个提交。 |
| 2024-01-29 | `03f7e039` | First implementation of Surface Effects MVP - Footsteps | 表面效果系统首个最小可行版本的首次提交（随后被回退）。 |

### 维护评价

该插件创建于 2024 年初，是一个相对较新的实验性插件。
- **近期更新频率**：最近一次实质性功能提交是 2024 年 1 月底的 MVP 实现。2024 年 11 月和 2025 年 4 月的更新主要是构建系统和描述文件的维护性调整，没有新的功能开发。
- **活跃度**：功能开发处于**不活跃**状态。作为实验性插件，其核心功能（基于上下文和数据表的表面查询）已基本实现，但可能未在大型项目中广泛验证。
- **已知问题/限制**：作为 MVP，其规则系统相对简单。复杂的上下文组合可能需要编写大量的自定义规则类。
- **推荐使用**：**谨慎推荐**。适合需要简单、数据驱动表面效果系统的小型或原型项目。如果项目对表面效果的需求非常复杂，可能需要评估是否自行实现更定制化的系统。使用时请注意其“实验性”状态，意味着 API 可能发生破坏性变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects)
- 官方文档：暂无
- 测试用例：未在插件目录内发现标准测试文件。
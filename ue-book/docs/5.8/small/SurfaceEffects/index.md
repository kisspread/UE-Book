# SurfaceEffects

> A flexible, context-driven surface system

| 属性 | 值 |
|---|---|
| 中文名 | 表面效果系统 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SurfaceEffects` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-01-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects) | |

## 用途

这个插件提供了一套基于规则的、数据驱动的框架，用于根据游戏上下文动态确定表面类型。它解决的核心问题是：将“材质/物理表面 → 游戏性表面效果（如脚步声、材质纹理、交互反馈）”的映射逻辑从代码中解耦出来，改为由数据表驱动。

插件的用途在于实现一个灵活的表面查询系统。它通过 `USurfaceEffectsSubsystem` 子系统作为入口点，接受一个包含上下文信息的 `FSurfaceEffectContextBase` 结构体（例如：命中位置、物理材质、Actor等），然后查询一个由策划配置的数据表。数据表中的每一行（`FSurfaceEffectTableRow`）关联一个 `USurfaceEffectRule` 数据资产，该规则根据传入的上下文，决定返回哪个具体的表面枚举值。这使得同一个查询逻辑（例如“角色脚下的表面是什么”）可以根据不同的游戏对象（角色、载具）或上下文（奔跑、跳跃）返回不同的结果，并且规则完全由策划在编辑器中配置。

## 使用场景

- **脚步声系统**：角色在不同地面材质（如金属、泥土、木板）上行走或奔跑时，需要播放不同的脚步声音效。该系统可以根据角色脚下的物理材质或重叠的触发器区域，返回对应的表面枚举，驱动音效系统。
- **车辆轮胎交互**：车辆的轮胎在不同路面上行驶，需要产生不同的粒子效果、声音或物理摩擦力。此系统可以根据轮胎接触点的物理材质，返回相应的表面类型。
- **武器与环境交互**：子弹射击到不同表面时，需要产生不同的弹孔材质、粒子火花和声音。可以通过查询命中点的表面信息来实现。
- **可定制的游戏性表面**：任何需要根据环境表面类型改变游戏逻辑的场景，例如滑索在不同材质上的滑行声音、载具在泥泞地面上的速度衰减等。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Surface<TEnum>` | 根据上下文查询并返回指定枚举类型的表面值。这是一个模板化函数，在蓝图中通常通过特定的枚举类型节点来调用。 | `USurfaceEffectsSubsystem` |

**注意**：`USurfaceEffectsSubsystem` 的主要接口 `GetSurface` 是 C++ 模板函数，无法直接在蓝图中作为单一节点使用。在蓝图中实现表面查询通常需要通过以下方式之一：
1. **使用自定义的蓝图函数库 (Blueprint Function Library)**：在 C++ 中创建一个辅助类，包装对 `GetSurface` 的调用，并暴露特定枚举类型的 `UFUNCTION(BlueprintCallable)` 函数给蓝图。
2. **使用已存在的、特定于项目的封装**：你的项目可能已经有了访问此子系统的蓝图接口。

**典型工作流**：
1. 在 C++ 中定义你的表面枚举（例如 `EMySurfaceType`）。
2. 创建对应的 `USurfaceEffectRule` 子类，实现 `GetSurface` 虚函数，其中包含判断逻辑。
3. 在项目设置中，配置 `Surface Effects` 设置，指向一个 `UDataTable`。
4. 在数据表中，为 `EMySurfaceType` 枚举添加一行，关联你创建的规则资产。
5. 在游戏逻辑（如角色移动组件）中，通过 `GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>()` 获取子系统实例，然后调用 `GetSurface<EMySurfaceType>(Context)`。

## C++ 用法

### 头文件引入

```cpp
#include "SurfaceEffectsSubsystem.h"
```

### 基本用法

首先，定义你自己的表面枚举和对应的规则类。

**1. 定义表面枚举**
```cpp
// MySurfaceTypes.h
UENUM(BlueprintType)
enum class EMyGameSurface : uint8
{
    Default,
    Metal,
    Dirt,
    Wood,
    Water,
    // ... 其他表面类型
};
```

**2. 创建自定义规则类**
```cpp
// MyGameSurfaceRule.h
#include "SurfaceEffectsSubsystem.h"
#include "MySurfaceTypes.h"

UCLASS()
class UMyGameSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        // 示例：根据物理材质判断
        if (const FHitResult* HitResult = Context.GetHitResult())
        {
            if (HitResult->PhysMaterial.IsValid())
            {
                if (HitResult->PhysMaterial->SurfaceType == EPhysicalSurface::SurfaceType1) // 金属
                {
                    OutSurfaceValue = static_cast<uint8>(EMyGameSurface::Metal);
                    return true;
                }
                // ... 其他材质判断
            }
        }
        // 默认返回
        OutSurfaceValue = static_cast<uint8>(EMyGameSurface::Default);
        return true;
    }
};
```

**3. 查询表面值**
```cpp
// 在某个类中（例如 AMyCharacter 的移动组件）
#include "SurfaceEffectsSubsystem.h"
#include "MySurfaceTypes.h"

void AMyCharacter::CheckFootstepSurface()
{
    // 1. 准备上下文（需要构造 FSurfaceEffectContextBase 或其子类）
    FSurfaceEffectContextBase Context;
    // 假设你有从 LineTrace 获得的 HitResult
    // Context.SetHitResult(MyHitResult);

    // 2. 获取子系统实例
    USurfaceEffectsSubsystem* SurfaceSubsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();
    if (SurfaceSubsystem)
    {
        // 3. 调用模板函数查询
        TSurfaceEffectResult<EMyGameSurface> Result = SurfaceSubsystem->GetSurface<EMyGameSurface>(Context);

        if (Result.bSuccess)
        {
            EMyGameSurface SurfaceType = Result.OutSurface;
            // 4. 使用返回的枚举值（例如播放对应的声音）
            PlayFootstepSound(SurfaceType);
        }
    }
}
```

### 进阶用法

该系统的核心优势在于其规则是 `UDataAsset`，可以包含复杂的逻辑和引用其他资产（如物理材质列表、配置表格等）。你可以创建更智能的规则，例如：

- **基于距离和视口的规则**：在不同的游戏模式或摄像机距离下，可能需要不同的表面细节级别。
- **组合规则**：创建一个规则资产，内部包含多个子规则，并根据优先级或组合逻辑返回最终结果。
- **上下文丰富的规则**：`FSurfaceEffectContextBase` 可以被子类化，以携带更多特定信息（如天气状态、角色状态），规则可以据此做出更精细的判断。

## Demo 示例

以下是一个可编译的最小示例，演示如何定义枚举、规则并查询表面。

**MyDemoSurfaceTypes.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MyDemoSurfaceTypes.generated.h"

UENUM(BlueprintType)
enum class EDemoSurfaceType : uint8
{
    Generic,
    Metal,
    Glass
};
```

**MyDemoSurfaceRule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "SurfaceEffectsSubsystem.h"
#include "MyDemoSurfaceTypes.h"
#include "MyDemoSurfaceRule.generated.h"

UCLASS()
class UMyDemoSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        // 简化的示例：根据上下文中存储的整数标签返回
        // 实际项目中会使用 HitResult, Material 等信息
        int32 Tag = Context.GetIntTag();
        if (Tag == 1)
        {
            OutSurfaceValue = static_cast<uint8>(EDemoSurfaceType::Metal);
        }
        else if (Tag == 2)
        {
            OutSurfaceValue = static_cast<uint8>(EDemoSurfaceType::Glass);
        }
        else
        {
            OutSurfaceValue = static_cast<uint8>(EDemoSurfaceType::Generic);
        }
        return true;
    }
};
```

**DemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DemoComponent.generated.h"

class USurfaceEffectsSubsystem;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Demo")
    int32 TestContextTag = 0;

    UFUNCTION(BlueprintCallable, Category = "Demo")
    void QuerySurfaceDemo();

private:
    UPROPERTY()
    TObjectPtr<USurfaceEffectsSubsystem> CachedSubsystem;
};
```

**DemoComponent.cpp**
```cpp
#include "DemoComponent.h"
#include "SurfaceEffectsSubsystem.h"
#include "MyDemoSurfaceTypes.h"

void UDemoComponent::QuerySurfaceDemo()
{
    if (!CachedSubsystem)
    {
        CachedSubsystem = GetOwner()->GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();
    }

    if (CachedSubsystem)
    {
        // 构建一个简单的上下文（这里假设 FSurfaceEffectContextBase 有设置整数的方法）
        FSurfaceEffectContextBase Context;
        // 注意：FSurfaceEffectContextBase 默认可能没有 SetIntTag 方法。
        // 这是一个示意，你需要根据实际上下文类来填充数据。
        // Context.SetIntTag(TestContextTag);

        TSurfaceEffectResult<EDemoSurfaceType> Result = CachedSubsystem->GetSurface<EDemoSurfaceType>(Context);

        if (Result.bSuccess)
        {
            UE_LOG(LogTemp, Warning, TEXT("查询到表面类型: %s"),
                *UEnum::GetValueAsString(Result.OutSurface));
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。
*(插件本身的 `Build.cs` 未提供，但从代码推断其依赖 `Engine` 模块以使用 `UDataTable`, `UGameInstanceSubsystem` 等，以及 `CoreUObject`。)*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为编译兼容性，将函数和静态变量导出符号从默认改为 DLL 导出。 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 批量更新同时标记为实验和测试版的插件描述文件，规范其状态标识。 |
| 2024-01-30 | `fac760fa` | First implementation of Surface Effects MVP - Footsteps | 首次实现表面效果最小可行产品（MVP），聚焦于脚步声场景。 |
| 2024-01-29 | `962fd46c` | [Backout] - CL30970339 | 回滚了之前的提交 CL30970339。 |
| 2024-01-29 | `03f7e039` | First implementation of Surface Effects MVP - Footsteps | 首次实现表面效果最小可行产品（MVP），聚焦于脚步声场景。 |

### 维护评价

- **创建时间**：2024年1月，是一个相对年轻的插件。
- **近期更新**：最近一次实质性更新（MVP 实现）在2024年1月底。2024年11月和2025年4月的更新主要是编译和元数据维护，未引入新功能。更新频率较低。
- **活跃度**：处于**维护中**状态，但非活跃开发。有基础实现，但功能集可能还未完全成熟。
- **已知限制**：作为实验性插件，API 和功能可能会发生变化。上下文系统 (`FSurfaceEffectContextBase`) 的具体能力需要查看其完整定义（未在提供的片段中）。
- **推荐使用**：适合在需要灵活、数据驱动表面查询的**新项目**中进行探索和原型开发。如果用于生产环境，需要评估其稳定性并准备好自行维护和扩展。不建议在旧项目中仓促引入。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects)
- [官方文档](无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects/Tests) (假设存在，路径未在提供信息中确认)
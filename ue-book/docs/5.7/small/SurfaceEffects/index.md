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
| 创建时间 | 2024-01-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SurfaceEffects) | |

## 用途

SurfaceEffects 是一个轻量级的运行时系统，帮助开发者根据物理表面或其他上下文条件（例如脚步接触地面的材质）动态选择枚举值，从而实现“表面感知”的游戏效果（如脚步声、粒子特效、材质变化等）。它通过可配置的规则（`USurfaceEffectRule`）和数据表（`SurfaceEffectsDataTable`）将物理表面（`EPhysicalSurface`）映射到自定义的游戏逻辑表面枚举，避免了硬编码，提高了灵活性和可扩展性。

## 使用场景

- 你正在开发一个需要根据不同地面材质（草地、石板、水洼等）播放不同音效或 VFX 的第三人称游戏 → 使用 SurfaceEffects 定义规则，让角色行走时自动触发对应的表面效果。
- 你需要一个统一、可配置的物理表面响应框架，支持设计师在运行时通过数据表调整映射关系，而不需要修改 C++ 代码。
- 你希望在项目初期就建立一个可扩展的表面上下文系统，未来能轻松加入更多规则（如根据武器类型、天气等上下文选择表面效果）。

## 蓝图用法

> **注意**：当前版本的插件主要以 C++ 数据结构和子系统方式提供，未直接公开 BlueprintCallable 函数。开发者需通过 C++ 调用 `USurfaceEffectsSubsystem` 的接口，或将自定义逻辑包装为蓝图函数库。

以下为插件中可用的蓝图相关资源与用法：

| 节点/资源 | 说明 | 所在类 |
|---|---|---|
| `SurfaceEffectsSettings` | 项目设置中可配置的数据表路径 | `USurfaceEffectsSettings` |
| `Surface Effects Data Table` | 存放 `FSurfaceEffectTableRow` 的数据表，每个行绑定一个 `USurfaceEffectRule` 数据资产 | 无（通过设置引用） |

要在蓝图中使用，需在 C++ 中实现自定义的 `USurfaceEffectRule` 子类，并将其标记为 `BlueprintType`。然后可以在数据表中引用这些规则资产，并在项目设置中指定数据表。

## C++ 用法

### 头文件引入

```cpp
#include "SurfaceEffectsSubsystem.h"
#include "SurfaceEffectsSettings.h"
#include "SurfaceEffectRule.h" // 自定义规则子类
```

### 基本用法

从查询物理表面到获取自定义表面枚举：

```cpp
// 1. 获取 Subsystem（通常在 GameInstance 中）
UGameInstance* GameInstance = GetWorld()->GetGameInstance();
USurfaceEffectsSubsystem* SurfaceSystem = GameInstance->GetSubsystem<USurfaceEffectsSubsystem>();

// 2. 准备上下文（基于物理表面）
EPhysicalSurface PhysSurface = FSurfaceSystem::GetSurfaceType(HitResult); // 或自定义获取
FSurfaceEffectContextBase Context(PhysSurface);

// 3. 定义目标枚举类型（例如 EFoleySurfaceType）
//    假设在代码中已有枚举，需要注册到子系统或使用模板方法
//    SurfaceSystem 内部使用 USurfaceEffectRule::GetSurface(uint8& OutSurfaceValue, Context) 进行查询
//    实际调用需要开发者自行实现，或借助插件的泛型函数
```

**注意**：当前 `USurfaceEffectsSubsystem` 的实现细节未完全公开，建议参考插件源码的 `.cpp` 文件获取完整 API。

### 进阶用法

创建一个自定义规则，根据物理表面返回特定的脚步声类型：

```cpp
// MySurfaceRule.h
UCLASS(BlueprintType)
class UMySurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Surface")
    TMap<TEnumAsByte<EPhysicalSurface>, EFoleySurfaceType> Mapping;

    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        if (auto* Found = Mapping.Find(Context.PhysicalSurface))
        {
            OutSurfaceValue = static_cast<uint8>(*Found);
            return true;
        }
        return false;
    }
};
```

然后将该规则资产引用到 `FSurfaceEffectTableRow` 所在的数据表行中，并在项目设置的 `Surface Effects Data Table` 中选择该数据表。

## Demo 示例

以下是一个最小 C++ 示例，演示如何在项目中使用 SurfaceEffects 系统。假设你有一个枚举 `EFootstepSurface`。

**FootstepSurfaceExample.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "SurfaceEffectsSubsystem.h"
#include "FootstepSurfaceExample.generated.h"

// 自定义脚步声表面枚举
UENUM(BlueprintType)
enum class EFootstepSurface : uint8
{
    Footsteps_Default	UMETA(DisplayName="Default"),
    Footsteps_Grass		UMETA(DisplayName="Grass"),
    Footsteps_Stone		UMETA(DisplayName="Stone"),
    Footsteps_Water		UMETA(DisplayName="Water"),
};

// 自定义规则：将物理表面映射到脚步声表面
UCLASS(BlueprintType)
class UFootstepSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "Mapping")
    TMap<TEnumAsByte<EPhysicalSurface>, EFootstepSurface> SurfaceMap;

    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        if (const EFootstepSurface* Result = SurfaceMap.Find(Context.PhysicalSurface))
        {
            OutSurfaceValue = static_cast<uint8>(*Result);
            return true;
        }
        return false;
    }
};
```

**FootstepSurfaceExample.cpp**

```cpp
#include "FootstepSurfaceExample.h"
// 在实际的 gameplay 代码中调用：
void AMyCharacter::OnFootstep(const FHitResult& Hit)
{
    UGameInstance* GI = GetGameInstance();
    if (!GI) return;
    USurfaceEffectsSubsystem* Subsystem = GI->GetSubsystem<USurfaceEffectsSubsystem>();
    if (!Subsystem) return;

    // 上下文
    EPhysicalSurface PhysSurface = UPhysicalMaterial::DetermineSurfaceType(Hit.PhysMaterial.Get());
    FSurfaceEffectContextBase Context(PhysSurface);

    // 查询规则（需要子系统内部的规则管理，此为例子）
    // 实际可调用 Subsystem->GetSurfaceForRule<UFootstepSurfaceRule>(Context); 
    // 假设子系统提供了这样的接口（未公开，需自行扩展）。
}
```

> 注意：以上示例为概念验证，实际使用时需适配子系统的实现细节。建议阅读插件完整源码。

## 模块依赖

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/DeveloperSettings） | |

## 维护状态

### 近期更新

- 2025-04-23 `939cc6e5` — Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv（构建系统调整）
- 2024-11-22 `36771d79` — Updated uplugin descriptor files marked as both Experimental and Beta（描述符清理）
- 2024-01-30 `fac760fa` — First implementation of Surface Effects MVP - Footsteps（功能首次实装）
- 2024-01-29 `962fd46c` — Backout CL30970339（回滚）
- 2024-01-29 `03f7e039` — First implementation of Surface Effects MVP - Footsteps（回滚前的提交）

### 维护评价

- 创建于 2024 年 1 月，属于较新的实验性插件。
- 最近一次实质性功能更新是 2024 年 1 月（MVP），之后仅进行了构建系统和描述符的维护工作。
- 截至 2025 年 4 月，已有超过 1 年没有新增功能或 bug 修复，维护不活跃。考虑到其 `IsExperimentalVersion=true` 状态，可能仍处于早期试验阶段，不建议在正式项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SurfaceEffects)
- [官方文档](https://docs.unrealengine.com/)（搜索 SurfaceEffects，目前无专页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/SurfaceEffects/Tests)（如果存在）
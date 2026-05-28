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
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects) | |

## 用途

SurfaceEffects 是一个基于上下文（Context）驱动的表面材质类型判定系统。它解决的核心问题是：**在运行时根据不同的上下文数据（如物理材质、环境条件等），动态确定当前交互的表面类型**。

典型应用是脚步声系统——角色踩在不同表面上（木板、金属、泥土）时，需要返回对应的表面枚举值，从而播放不同的音效或生成不同的粒子效果。传统做法是直接查询物理材质并硬编码映射关系，而该插件将这个过程抽象为数据驱动的规则系统：通过数据表（DataTable）配置规则，运行时由子系统统一查询。

为什么存在：
- 将表面类型判定逻辑从具体游戏逻辑中解耦
- 支持多种枚举类型，不需要为每种表面分类写单独的查询逻辑
- 通过数据资产和数据表实现配置化，策划人员可直接编辑规则

## 使用场景

- 你需要根据脚步接触的表面类型播放不同音效 → 用 SurfaceEffects 查询表面枚举
- 你的游戏有多种表面交互（子弹击中效果、载具轮胎痕迹等） → 用 SurfaceEffects 统一管理表面规则
- 你希望表面映射规则由数据驱动而非硬编码 → 配置 DataTable + 自定义 Rule 资产

## 蓝图用法

该插件的核心 API 主要面向 C++，蓝图端的直接可用节点有限。子系统通过模板函数暴露，需要在 C++ 层封装后才能在蓝图中使用。

### 核心节点

该插件没有直接暴露 BlueprintCallable 节点。所有核心功能通过 C++ 模板函数 `GetSurface<TEnum>()` 访问，蓝图使用需要自行封装 BlueprintCallable 包装函数。

## C++ 用法

### 头文件引入

```cpp
#include "SurfaceEffectsSubsystem.h"
```

### 基本用法

**定义你的表面枚举和上下文**

```cpp
// 自定义表面类型枚举
UENUM()
enum class EMySurfaceType : uint8
{
    Default,
    Wood,
    Metal,
    Dirt,
    Water,
    Max UMETA(Hidden)
};

// 自定义上下文数据（可携带物理材质等信息）
USTRUCT()
struct FMySurfaceContext : public FSurfaceEffectContextBase
{
    GENERATED_BODY()

    UPROPERTY()
    TWeakObjectPtr<UPhysicalMaterial> PhysicalMaterial;
};
```

**查询表面类型**

```cpp
// 获取子系统
USurfaceEffectsSubsystem* Subsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();

// 构造上下文
FMySurfaceContext Context;
Context.PhysicalMaterial = HitResult.PhysicalMaterial;

// 查询表面枚举值（模板参数传入你的枚举类型）
TSurfaceEffectResult<EMySurfaceType> Result = Subsystem->GetSurface<EMySurfaceType>(Context);

if (Result.bSuccess)
{
    switch (Result.OutSurface)
    {
    case EMySurfaceType::Wood:
        // 播放木头脚步声
        break;
    case EMySurfaceType::Metal:
        // 播放金属脚步声
        break;
    // ...
    }
}
```

### 进阶用法

**自定义规则资产（继承 USurfaceEffectRule）**

```cpp
// .h
UCLASS()
class UMySurfaceEffectRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override;

    UPROPERTY(EditAnywhere)
    TMap<TObjectPtr<UPhysicalMaterial>, EMySurfaceType> MaterialMap;

    UPROPERTY(EditAnywhere)
    EMySurfaceType DefaultSurface = EMySurfaceType::Default;
};

// .cpp
bool UMySurfaceEffectRule::GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context)
{
    const FMySurfaceContext& MyContext = static_cast<const FMySurfaceContext&>(Context);

    if (MyContext.PhysicalMaterial.IsValid())
    {
        if (const EMySurfaceType* Found = MaterialMap.Find(MyContext.PhysicalMaterial.Get()))
        {
            OutSurfaceValue = static_cast<uint8>(*Found);
            return true;
        }
    }

    OutSurfaceValue = static_cast<uint8>(DefaultSurface);
    return true;
}
```

**配置数据表**

1. 创建一个 DataTable，行类型选择 `SurfaceEffectTableRow`
2. 行名称设为你的枚举类名（如 `MySurfaceType`）
3. 该行的 `Rule` 字段指向你创建的 `UMySurfaceEffectRule` 资产
4. 在 Project Settings → Surface Effects 中指定该 DataTable

## Demo 示例

### SurfaceEffectRule 示例（.h）

```cpp
#pragma once

#include "CoreMinimal.h"
#include "SurfaceEffectsSubsystem.h"
#include "MySurfaceEffectRule.generated.h"

UENUM()
enum class EGroundType : uint8
{
    Default,
    Stone,
    Grass,
    Sand,
    Max UMETA(Hidden)
};

USTRUCT()
struct FGroundContext : public FSurfaceEffectContextBase
{
    GENERATED_BODY()

    UPROPERTY()
    FName MaterialTag;
};

UCLASS()
class UGroundSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override;

    UPROPERTY(EditAnywhere)
    TMap<FName, EGroundType> TagToSurface;

    UPROPERTY(EditAnywhere)
    EGroundType DefaultSurface = EGroundType::Default;
};
```

### SurfaceEffectRule 示例（.cpp）

```cpp
#include "MySurfaceEffectRule.h"

bool UGroundSurfaceRule::GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context)
{
    const FGroundContext& Ctx = static_cast<const FGroundContext&>(Context);

    if (const EGroundType* Found = TagToSurface.Find(Ctx.MaterialTag))
    {
        OutSurfaceValue = static_cast<uint8>(*Found);
        return true;
    }

    OutSurfaceValue = static_cast<uint8>(DefaultSurface);
    return true;
}
```

### 运行时查询示例

```cpp
// 在 Actor 或 Component 中查询
void AMyCharacter::PlayFootstepSound(const FHitResult& Hit)
{
    USurfaceEffectsSubsystem* Subsystem = GetGameInstance()->GetSubsystem<USurfaceEffectsSubsystem>();
    if (!Subsystem) return;

    FGroundContext Context;
    Context.MaterialTag = /* 从 Hit 中提取材质标签 */;

    TSurfaceEffectResult<EGroundType> Result = Subsystem->GetSurface<EGroundType>(Context);

    if (Result.bSuccess)
    {
        // 根据 Result.OutSurface 播放对应音效
        USoundBase* Sound = GetFootstepSound(Result.OutSurface);
        if (Sound)
        {
            UGameplayStatics::PlaySoundAtLocation(this, Sound, Hit.ImpactPoint);
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

| 模块 | 用途 |
|---|---|
| `DeveloperSettings` | 提供 `UDeveloperSettings` 基类用于项目设置配置 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为所有方法和静态变量添加 DLL 导出宏，修复跨模块链接问题 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 批量清理同时标记为 Experimental 和 Beta 的插件描述符 |
| 2024-01-30 | `fac760fa` | First implementation of Surface Effects MVP - Footsteps | 表面效果系统 MVP 首次实现，聚焦脚步声场景 |
| 2024-01-29 | `962fd46c` | [Backout] - CL30970339 | 回退了一次提交 |
| 2024-01-29 | `03f7e039` | First implementation of Surface Effects MVP - Footsteps | 表面效果系统 MVP 首次实现（后被回退再重新提交） |

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，标记为实验性，API 可能随时变更
- **功能稳定但不活跃**：核心功能在 2024-01 完成 MVP 后，后续仅有一批 DLL 导出修复（2025-04），无功能性更新
- **代码量极小**：仅 5 个源文件，属于最小级别的插件
- **使用前提**：需要手动在 Project Settings 中配置数据表才能生效
- **推荐程度**：⚠️ 谨慎使用。作为实验性插件，适合内部项目或原型验证，不建议在生产环境中强依赖。如果你只需要简单的物理材质→脚步声映射，自己写一个更简单的方案可能更合适。但如果你需要一个支持多枚举类型、数据驱动的通用表面判定系统，这个插件的架构设计是合理的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects)
- 官方文档：无
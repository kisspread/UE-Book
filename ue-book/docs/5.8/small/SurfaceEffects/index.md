# Surface Effects

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

SurfaceEffects 提供了一个**上下文驱动的表面类型查询系统**。它解决的核心问题是：在游戏运行时，根据当前场景上下文（如脚落地面材质、轮胎接触的路面类型等）动态判断应该使用哪种表面效果。

工作原理：
1. 开发者定义一个枚举类型表示表面（如 `EFootStepSurface`：草地、水泥、金属、水面等）
2. 创建 `USurfaceEffectRule` 的子类作为"规则"，根据上下文数据决定返回哪个枚举值
3. 规则存入 DataTable，以枚举类型名作为行名
4. 运行时通过 `USurfaceEffectsSubsystem::GetSurface<TEnum>(Context)` 查询

这个系统的设计非常通用——同一套框架可以用于脚印音效、轮胎粒子效果、弹道撞击反馈等任何需要"根据表面类型产生不同效果"的场景。

## 使用场景

- 你需要根据角色脚踩的地面材质播放不同脚步音效 → 用 SurfaceEffects 存储地面表面类型
- 你需要根据车辆轮胎接触的路面类型产生不同粒子效果 → 用 SurfaceEffects 查询路面表面
- 你需要一个可配置的、数据驱动的表面判断系统，而非硬编码的物理材质映射 → 用 SurfaceEffects + DataTable

## 蓝图用法

此插件的核心查询函数 `GetSurface` 是模板函数，**仅限 C++ 使用**。但 `USurfaceEffectRule` 是 `UDataAsset`，可以在蓝图中创建子类。

### 核心类

| 类 | 说明 |
|---|---|
| `USurfaceEffectRule` | 抽象数据资产基类，用于定义表面判断规则 |
| `USurfaceEffectsSubsystem` | 游戏实例子系统，负责查询表面效果 |
| `USurfaceEffectsSettings` | 开发者设置，配置数据表路径 |
| `FSurfaceEffectTableRow` | DataTable 行结构，包装一个 Rule 引用 |

### 设置配置

在 **项目设置 → Plugins → Surface Effects** 中，指定 SurfaceEffectsDataTable 的路径，指向包含所有规则的 DataTable 资产。

## C++ 用法

### 头文件引入

```cpp
#include "SurfaceEffectsSubsystem.h"
```

### 基本用法

首先定义表面枚举和上下文：

```cpp
// 自定义表面类型枚举
UENUM()
enum class EMySurfaceType : uint8
{
    Default,
    Grass,
    Concrete,
    Metal,
    Water,
    Max UMETA(Hidden)
};

// 使用子系统查询表面类型
UGameInstance* GameInstance = GetGameInstance();
USurfaceEffectsSubsystem* SurfaceSubsystem = GameInstance->GetSubsystem<USurfaceEffectsSubsystem>();

// 构造上下文并查询
FSurfaceEffectContextBase Context; // 需要根据实际需求填充上下文数据
TSurfaceEffectResult<EMySurfaceType> Result = SurfaceSubsystem->GetSurface<EMySurfaceType>(Context);

if (Result.bSuccess)
{
    EMySurfaceType Surface = Result.OutSurface;
    // 根据 Surface 播放对应效果...
}
```

*来源：`SurfaceEffectsSubsystem.h` 中的 `GetSurface` 模板函数*

### 创建自定义规则

```cpp
// 创建一个表面效果规则子类
UCLASS()
class UMySurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override
    {
        // 根据 Context 判断表面类型
        // 例如：检测物理材质、位置等
        OutSurfaceValue = static_cast<uint8>(EMySurfaceType::Grass);
        return true;
    }
};
```

*来源：`SurfaceEffectsSubsystem.h` 中的 `USurfaceEffectRule` 定义*

### 进阶用法

将规则存入 DataTable 并通过设置系统引用：

```cpp
// DataTable 配置：
// 1. 创建 DataTable，Row Structure 选择 FSurfaceEffectTableRow
// 2. 行名 = 枚举类名（如 "MySurfaceType"）
// 3. 行内容 = 你的 USurfaceEffectRule 子类资产引用
// 4. 在 Project Settings → Surface Effects 中指定该 DataTable 路径

// 查询时，系统自动用枚举类名在 DataTable 中查找对应行的 Rule
TSurfaceEffectResult<EMySurfaceType> Result = Subsystem->GetSurface<EMySurfaceType>(Context);
```

*来源：`SurfaceEffectsSubsystem.h` 中 `GetSurface` 的实现逻辑*

## Demo 示例

### MySurfaceRule.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "SurfaceEffectsSubsystem.h"
#include "MySurfaceRule.generated.h"

UENUM()
enum class EGroundSurface : uint8
{
    Default,
    Grass,
    Concrete,
    Dirt,
    Water,
    Max UMETA(Hidden)
};

UCLASS()
class UGroundSurfaceRule : public USurfaceEffectRule
{
    GENERATED_BODY()

public:
    virtual bool GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context) override;
};
```

### MySurfaceRule.cpp

```cpp
#include "MySurfaceRule.h"

bool UGroundSurfaceRule::GetSurface(uint8& OutSurfaceValue, const FSurfaceEffectContextBase& Context)
{
    // 简单示例：默认返回 Grass
    // 实际项目中可根据 Context 中的位置、物理材质等信息判断
    OutSurfaceValue = static_cast<uint8>(EGroundSurface::Grass);
    return true;
}
```

### 使用示例（C++）

```cpp
// 在任意运行时代码中
void AMyCharacter::OnFootstep()
{
    if (UGameInstance* GI = GetGameInstance())
    {
        if (USurfaceEffectsSubsystem* Sub = GI->GetSubsystem<USurfaceEffectsSubsystem>())
        {
            FSurfaceEffectContextBase Context;
            // 填充 Context 数据...

            auto Result = Sub->GetSurface<EGroundSurface>(Context);
            if (Result.bSuccess)
            {
                // 播放对应地面的脚步声
                PlayFootstepSound(Result.OutSurface);
            }
        }
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）

该插件的 Build.cs 未提供依赖详情，但从头文件来看仅依赖 `CoreUObject`、`Engine`、`DeveloperSettings` 等标准模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为方法和静态变量添加 DLL 导出标记以支持 Fortnite 构建 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta. Plugins with both flags in th | 清理同时标记为实验性和测试版的插件描述文件 |
| 2024-01-30 | `fac760fa` | First implementation of Surface Effects MVP - Footsteps | 首次实现 Surface Effects MVP，用于脚步效果 |
| 2024-01-29 | `962fd46c` | [Backout] - CL30970339 | 回退了之前的提交 |
| 2024-01-29 | `03f7e039` | First implementation of Surface Effects MVP - Footsteps | 首次实现 Surface Effects MVP（被后续回退） |

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，尚未稳定
- **活跃度一般**：创建于 2024 年初，核心功能在 2024-01-30 完成后，后续仅有构建兼容性修复（2025-04）和元数据清理（2024-11），无实质性功能更新
- **代码量小**：仅 5 个源文件，属于 MVP（最小可行产品）阶段
- **局限性**：`FSurfaceEffectContextBase` 的具体定义未在提供的头文件中展示，可能需要进一步查阅源码
- **建议**：适用于需要表面效果分类的项目，但由于是实验性插件，生产环境使用需谨慎。建议关注后续更新，或将其作为参考实现集成到自定义系统中

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/SurfaceEffects)（未发现独立测试文件）
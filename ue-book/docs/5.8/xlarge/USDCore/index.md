# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 中文名 | USD 基础支持 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 资产与模板） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore) | |

## 用途

**USDCore** 是 Unreal Engine 中 **USD (Universal Scene Description) 支持的基础插件**。它的核心作用是将原本分散在引擎各处的 USD 相关代码（包括底层 SDK 绑定、数据模型类和通用转换工具）整合到一个独立的插件中。

这个插件本身**不直接处理 USD 文件的导入或导出**，而是为其他更高级的 USD 插件（如 `USDImporter`, `USDStage`）提供统一的底层支持。它解决了 USD 相关功能模块化、代码复用和版本管理的问题，是 UE 中 USD 生态系统的基础。

## 使用场景

- **开发 USD 资产管线**：当你的团队或项目需要深度集成 USD 工作流时，`USDCore` 是必需的底层依赖。
- **自定义 USD 工作流**：需要编写 C++ 代码来处理 USD Stage、Prim 或属性，或者需要自定义 USD 数据的转换逻辑。
- **扩展 UE 的 USD 支持**：如果你打算开发一个扩展或替换默认 USD 导入/导出流程的插件，你需要基于 `USDCore` 提供的类和函数进行开发。

## 模块列表

| 模块 | 职责简述 |
|---|---|
| `UnrealUSDWrapper` | 对 Pixar USD SDK 的底层 C++ 绑定层，提供对 USD 核心库的直接访问。 |
| `USDClasses` | 定义 UE 侧与 USD 概念对应的数据类（如 `FUsdStage`, `FUsdPrim`），是 UE 处理 USD 数据的主要对象。 |
| `USDUtilities` | 提供一系列用于 UE 类型与 USD 类型相互转换、属性操作等的静态工具函数库。 |

## 蓝图用法

本插件主要为 C++ 开发提供底层支持。其公开的蓝图接口（如 `UUsdStageActor`）通常封装在其他更高级的插件中（如 `USDStage`）。直接在此插件层面进行蓝图开发的情况较少。

## C++ 用法

本插件的 API 主要面向 C++ 开发者，用于编写与 USD 交互的自定义逻辑。

### 头文件引入

```cpp
// 访问 USD 类（如 FUsdStage, FUsdPrim）
#include "USDClassesModule.h"

// 使用 USD 工具函数
#include "USDConversionUtils.h" // 示例，具体头文件取决于使用的功能

// 访问底层 USD SDK 绑定（通常不直接使用）
#include "UnrealUSDWrapper.h"
```

### 基本用法

以下是一个简化的示例，展示如何获取一个 USD Stage 并查询信息。

```cpp
// 假设我们有一个有效的 USD Stage 对象 (例如，从 USDImporter 或 USDStage 插件获得)
FUsdStage Stage = /* ... */;

if (Stage)
{
    // 获取 Stage 的默认 Prim (根 Prim)
    FUsdPrim DefaultPrim = Stage.GetDefaultPrim();
    if (DefaultPrim)
    {
        UE_LOG(LogTemp, Log, TEXT("Stage Default Prim Path: %s"), *DefaultPrim.GetPrimPath());
    }

    // 遍历 Stage 的所有 Prim
    TArray<FUsdPrim> Prims = Stage.GetPrims();
    for (const FUsdPrim& Prim : Prims)
    {
        UE_LOG(LogTemp, Log, TEXT("Found Prim: %s, Type: %s"), *Prim.GetPrimPath(), *Prim.GetPrimType());
    }
}
```

### 进阶用法

结合 `USDUtilities` 模块进行类型转换。

```cpp
#include "USDUtilities.h"

// 假设我们有一个 FVector
FVector UnrealLocation(100.0f, 200.0f, 300.0f);

// 使用工具函数转换为 USD 理解的类型 (例如 GfVec3d 或类似的表示)
// 具体函数名可能为 UsdUtils::ConvertToUsdType 或类似形式
auto UsdVec = UsdUtils::ConvertToUsdType(UnrealLocation);
// ... 将 UsdVec 设置到某个 USD Prim 的属性上 ...
```

## Demo 示例

一个最小化的示例，展示如何从 C++ 代码中初始化和使用 `USDClasses` 模块。

**MyUsdActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "USDClassesModule.h" // 引入 USD 核心类
#include "MyUsdActor.generated.h"

UCLASS()
class AMyUsdActor : public AActor
{
    GENERATED_BODY()

public:
    // 用于存储加载的 USD Stage
    UPROPERTY(BlueprintReadWrite, Category = "USD")
    FUsdStage MyStage;

    // 打开一个 USD 文件
    UFUNCTION(BlueprintCallable, Category = "USD")
    bool OpenUsdFile(const FString& FilePath);

    // 获取 Stage 信息
    UFUNCTION(BlueprintCallable, Category = "USD")
    FString GetStageInfo() const;
};
```

**MyUsdActor.cpp**
```cpp
#include "MyUsdActor.h"
#include "UnrealUSDWrapper.h" // 底层工具，可能用于底层操作

bool AMyUsdActor::OpenUsdFile(const FString& FilePath)
{
    // 使用 UnrealUSDWrapper 或 USDClasses 提供的方法打开 Stage
    // 这里仅为示意，具体 API 需查阅模块文档
    MyStage = FUsdStage::Open(FilePath);
    return MyStage.IsValid();
}

FString AMyUsdActor::GetStageInfo() const
{
    if (!MyStage)
    {
        return TEXT("No Stage Loaded");
    }
    return FString::Printf(TEXT("Stage has %d Prims"), MyStage.GetPrimCount());
}
```

## 模块依赖

本插件的模块依赖关系如下。开发基于 `USDCore` 的插件时，你的 `Build.cs` 可能需要添加对其中一些模块的依赖。

| 模块 | 用途 |
|---|---|
| `Python3` | `UnrealUSDWrapper` 模块依赖 Python3，用于 USD SDK 的部分功能（如脚本化）。 |

（无其他特殊或不常见的运行时依赖）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复了实例化对象内部材质未正确去重的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量转换为浮点数产生警告的代码。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的作用域枚举可能导致输出乱码的问题。 |
| 2026-04-28 | `5b5d2b22` | [USD] Harden USDZ extraction in InterchangeUSD against path traversal (Zip Slip) and unsafe archive | 加固了 InterchangeUSD 中 USDZ 的解压功能，防止路径遍历（Zip Slip）和不安全存档攻击。 |
| 2026-04-28 | `bf5d0e5b` | USD: Add Nanite/mesh build settings schemas | 添加了用于 Nanite 和网格构建设置的 USD Schema。 |

### 维护评价

`USDCore` 插件创建于 **2024 年 5 月**，是一个相对年轻的插件。从 git 历史来看，**维护非常活跃**。最近的提交记录（截至 2026 年 5 月）持续在修复 Bug、改进功能（如材质去重、安全加固）以及扩展能力（添加新 Schema）。

该插件标记为 **实验性 (IsBetaVersion=true)** 且 **默认不启用 (EnabledByDefault=false)**，这表明其 API 和功能可能还未完全稳定，仍在积极开发中。

**结论**：对于需要在 UE 中深度使用 USD 功能的 C++ 开发者来说，这是一个**核心且处于积极维护状态**的基础插件。可以放心依赖和使用，但需要关注其 API 可能随版本迭代而发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore/Tests)
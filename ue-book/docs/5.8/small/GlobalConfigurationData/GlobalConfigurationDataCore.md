# Global Configuration Data

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GlobalConfigurationData` (Runtime), `GlobalConfigurationDataCore` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData) | |

## 用途

`GlobalConfigurationData` 插件实现了一个**多源、可扩展的全局配置数据查询系统**。它解决了以下问题：

1.  **配置来源解耦**：游戏代码无需关心配置数据具体来自何处（`.ini` 文件、控制台命令、远程服务器、A/B 测试平台等），只需通过统一的键名（`EntryName`）进行查询。
2.  **优先级管理**：支持多个数据源（路由器）按优先级排序。例如，默认配置文件优先级最低，用于承载基础值；控制台命令优先级最高，可用于调试时临时覆盖。
3.  **数据类型统一处理**：数据以字符串形式存储，对于基本类型（`bool`, `int32`, `float`）采用类似控制台变量的解析规则；对于复杂结构体（`UStruct`）和对象（`UObject`），则使用 JSON 格式进行序列化和反序列化。

其核心设计是通过 `IGlobalConfigurationRouter` 接口注册不同的数据源（路由器），系统自动管理它们的生命周期和查询顺序。

## 使用场景

- **热修复（Hotfix）**：服务器下发一个紧急配置值，覆盖客户端本地配置。
- **A/B 测试与数据实验**：不同的实验组使用不同的配置值，通过一个实验路由器动态提供。
- **多平台/多SKU配置**：为不同平台或游戏版本预设不同的配置基线，通过不同路由器加载。
- **开发调试**：开发者通过控制台命令快速修改运行时配置，无需重新打包。
- **模块化配置**：不同游戏功能模块（插件）可以提供自己的配置路由器，将配置数据集中在该系统中管理。

## 蓝图用法

该插件的核心逻辑由 `GlobalConfigurationDataCore` 模块提供，这是一个纯 C++ 运行时模块，**不直接暴露蓝图节点**。蓝图交互通常通过 `GlobalConfigurationData` 模块（可能提供蓝图函数库）或游戏逻辑封装实现。

### 潜在的蓝图封装示例

虽然直接的 `BlueprintCallable` 函数在提供的源码头文件中未明确列出，但根据其 C++ API，典型的蓝图封装可能如下：

```cpp
// 在你的蓝图函数库中
UCLASS()
class UMyBlueprintFunctionLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category = "Config", meta = (DisplayName = "Get Config Float"))
    static bool GetConfigFloat(const FString& EntryName, float& OutValue, float Default);
};
```

实现时调用 `UE::GlobalConfigurationData::GetDataWithDefault`。

## C++ 用法

### 头文件引入

```cpp
#include "GlobalConfigurationData.h" // 用于查询数据
#include "GlobalConfigurationRouter.h" // 用于创建自定义路由器（通常不需要）
```

### 基本用法：查询数据

从头文件 `GlobalConfigurationData.h` 中的命名空间 `UE::GlobalConfigurationData` 调用查询函数。

```cpp
// 查询一个浮点值
float GravityScale;
if (UE::GlobalConfigurationData::TryGetData(TEXT("Game.GravityScale"), GravityScale))
{
    // 使用 GravityScale
}
else
{
    // 使用默认值
}

// 查询一个字符串值
FString DefaultSkin;
UE::GlobalConfigurationData::TryGetData(TEXT("Character.DefaultSkin"), DefaultSkin);

// 使用模板版本查询结构体
FMyConfigStruct Config;
if (UE::GlobalConfigurationData::TryGetData(TEXT("Game.MyConfig"), Config))
{
    // 应用配置结构体
}

// 查询带有默认值的简便方法
float MaxSpeed = UE::GlobalConfigurationData::GetDataWithDefault(TEXT("Vehicle.MaxSpeed"), 1500.0f);
```

### 进阶用法：创建自定义路由器

通过继承 `IGlobalConfigurationRouter` 来添加新的数据源。

```cpp
#include "GlobalConfigurationRouter.h"

class FMyGameServiceRouter : public IGlobalConfigurationRouter
{
public:
    // 在构造函数中定义路由器的名称和优先级（高于默认配置，低于控制台命令）
    FMyGameServiceRouter()
        : IGlobalConfigurationRouter(TEXT("GameService"), 1000)
    {
    }

    virtual ~FMyGameServiceRouter() = default;

protected:
    // 实现从该路由器获取特定键名的数据
    virtual TSharedPtr<FJsonValue> TryGetDataFromRouter(const FString& EntryName) const override
    {
        // 这里可以调用你的后端服务API来获取数据
        // 例如：return MakeShared<FJsonValueNumber>(BackendService->GetConfig(EntryName));
        return nullptr;
    }

    // 实现获取该路由器拥有的所有数据（用于调试、序列化等）
    virtual void GetAllDataFromRouter(TMap<FString, TSharedRef<FJsonValue>>& DataOut) const override
    {
        // 遍历你管理的所有配置并填充 DataOut
    }
};

// 在合适的地方（如游戏实例初始化时）实例化，它会自动注册
TSharedRef<FMyGameServiceRouter> MyRouter = MakeShared<FMyGameServiceRouter>();
```

## Demo 示例

### 头文件 (`CustomConfigRouter.h`)

```cpp
// CustomConfigRouter.h
#pragma once
#include "GlobalConfigurationRouter.h"

class FCustomConfigRouter : public IGlobalConfigurationRouter
{
public:
    FCustomConfigRouter();
    virtual ~FCustomConfigRouter() override;

protected:
    virtual TSharedPtr<FJsonValue> TryGetDataFromRouter(const FString& EntryName) const override;
    virtual void GetAllDataFromRouter(TMap<FString, TSharedRef<FJsonValue>>& DataOut) const override;

private:
    // 用于存储你的配置数据
    TMap<FString, FString> CustomConfigStore;
};
```

### 实现文件 (`CustomConfigRouter.cpp`)

```cpp
// CustomConfigRouter.cpp
#include "CustomConfigRouter.h"

FCustomConfigRouter::FCustomConfigRouter()
    // 优先级设置为 500，介于默认配置 (INT32_MIN) 和控制台命令 (INT32_MAX) 之间
    : IGlobalConfigurationRouter(TEXT("Custom"), 500)
{
    // 模拟加载一些自定义配置
    CustomConfigStore.Add(TEXT("Game.Difficulty"), TEXT("Hard"));
    CustomConfigStore.Add(TEXT("UI.ShowFPS"), TEXT("true"));
    CustomConfigStore.Add(TEXT("Graphics.ViewDistance"), TEXT("10000"));
}

FCustomConfigRouter::~FCustomConfigRouter()
{
    // 路由器销毁时会自动反注册，无需手动操作
}

TSharedPtr<FJsonValue> FCustomConfigRouter::TryGetDataFromRouter(const FString& EntryName) const
{
    if (const FString* FoundValue = CustomConfigStore.Find(EntryName))
    {
        // 使用基类的工具函数将字符串解析为合适的 FJsonValue
        return IGlobalConfigurationRouter::TryParseString(*FoundValue);
    }
    return nullptr;
}

void FCustomConfigRouter::GetAllDataFromRouter(TMap<FString, TSharedRef<FJsonValue>>& DataOut) const
{
    for (const auto& Pair : CustomConfigStore)
    {
        if (TSharedPtr<FJsonValue> JsonValue = IGlobalConfigurationRouter::TryParseString(Pair.Value))
        {
            DataOut.Add(Pair.Key, JsonValue.ToSharedRef());
        }
    }
}
```

### 使用示例

```cpp
// 在游戏代码中使用
#include "GlobalConfigurationData.h"
#include "CustomConfigRouter.h"

void InitializeGameSystems()
{
    // 实例化自定义路由器，它会自动注册到全局系统中
    TSharedRef<FCustomConfigRouter> MyRouter = MakeShared<FCustomConfigRouter>();

    // 现在可以查询它提供的数据了
    FString Difficulty;
    if (UE::GlobalConfigurationData::TryGetData(TEXT("Game.Difficulty"), Difficulty))
    {
        // Difficulty 的值将是 “Hard”，来自我们的自定义路由器
        UE_LOG(LogTemp, Log, TEXT("Game difficulty is: %s"), *Difficulty);
    }

    bool bShowFPS = UE::GlobalConfigurationData::GetDataWithDefault(TEXT("UI.ShowFPS"), false);
    // bShowFPS 将是 true
}
```

## 模块依赖

从模块结构和 API 推断，无特殊依赖（仅标准 Core/Engine 等）。具体依赖关系需查看 `GlobalConfigurationDataCore.Build.cs`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-10 | `79a1090c` | [GCD] Add support to auto flatten json objects with a single entry | 新增自动扁平化单属性JSON对象的功能，提升易用性 |
| 2025-07-18 | `10de61f9` | [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting | 调整路由器策略：控制台命令路由仅限调试，新增高优先级“热修复”配置路由 |
| 2025-06-23 | `bfa3140f` | [Misc] Fix GlobalConfigurationData test ensures | 修复测试用例中的断言错误 |
| 2025-06-17 | `8a2ca4d6` | [UE] Add experimental Global Configuration Data | 首次提交，创建实验性全局配置数据系统 |

### 维护评价

- **状态**：**活跃维护**。创建仅数月，近期有明确的功能性更新（JSON扁平化、路由器策略优化）。
- **实验性**：插件目前标记为 `IsExperimentalVersion=true`，表明 API 和功能可能发生变化。
- **推荐度**：对于需要灵活、多源配置管理的项目（尤其是进行AB测试、热修复的），这是一个值得关注和试用的实验性插件。由于其仍在积极开发中，建议在非关键路径或原型阶段集成，并准备应对 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData)
- 测试用例：位于插件内的 `Tests/GlobalConfigurationDataTests` 目录（路径示例：`Engine/Plugins/Experimental/GlobalConfigurationData/Tests/`）
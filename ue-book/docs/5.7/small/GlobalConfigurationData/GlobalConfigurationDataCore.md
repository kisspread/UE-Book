# Global Configuration Data Core

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据核心 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GlobalConfigurationDataCore` (Runtime), `GlobalConfigurationData` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData) | |

## 用途

**Global Configuration Data** 提供了一种统一查询配置数据的机制，其数据可来自多个不同的来源（路由器），而消费者无需关心数据的具体来源。  
该系统的核心价值在于：

- **数据源解耦**：通过抽象路由器接口 `IGlobalConfigurationRouter`，将配置数据的获取与具体实现分离。
- **优先级排序**：路由器具有优先级，使高优先级源（如控制台命令）可以覆盖低优先级源（如 ini 配置文件），便于测试与热修复。
- **扩展性**：用户可创建自定义路由器，从任意后端（如远程服务、数据库）拉取数据，无需修改现有查询代码。

内置了两个默认路由器：

- `FGlobalConfigurationConfigRouter`：从 `GEngineIni` 的 `[GlobalConfigurationData]` 节读取配置，优先级最低（`INT32_MIN`）。
- `FGlobalConfigurationConsoleCommandRouter`：通过控制台命令 `GCD.RegisterValue` / `GCD.UnregisterValue` 动态注册/注销数据，优先级最高（`INT32_MAX`）。

插件分为两个模块：

- `GlobalConfigurationDataCore`：核心查询 API 与路由器接口，不包含任何绑定或业务逻辑。
- `GlobalConfigurationData`：提供蓝图函数库、控制台命令注册等上层便利功能（本文档未覆盖）。

## 使用场景

- 你需要一个系统来**从多种来源**获取配置数据，并支持动态覆盖（如开发环境中用控制台临时修改，生产环境中用远程配置服务）。
- 你想**隐藏数据源的细节**，使上层代码只需通过名称查询数据，无需关心数据来自 ini、控制台还是远程服务器。
- 你正在开发一个需要**热修复**或**A/B 测试**的功能，希望在不重新编译的情况下修改数值。
- 你需要**集中管理**游戏中的可调参数（如倍率、开关、文本），同时允许不同环境有不同的覆盖策略。

## 蓝图用法

> 本模块（`GlobalConfigurationDataCore`）的 API 全部为 C++ 模板函数，**未暴露 UFUNCTION**，因此无法在蓝图中直接调用。  
> 若需在蓝图中使用，请参考 `GlobalConfigurationData` 模块提供的蓝图节点（如 `GetGlobalConfigurationData` 等），或自行封装蓝图函数库。

## C++ 用法

### 头文件引入

```cpp
#include "GlobalConfigurationData.h"
#include "GlobalConfigurationRouter.h"
#include "Routers/GlobalConfigurationConfigRouter.h"
#include "Routers/GlobalConfigurationConsoleCommandRouter.h"
```

### 基本用法

**查询基本类型数据**

```cpp
// 尝试获取名为 "MyFloatValue" 的配置，类型为 float
float MyValue = 0.0f;
if (UE::GlobalConfigurationData::TryGetData(TEXT("MyFloatValue"), MyValue))
{
    UE_LOG(LogTemp, Log, TEXT("MyFloatValue = %f"), MyValue);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("MyFloatValue not found"));
}

// 使用默认值
int32 MyInt = UE::GlobalConfigurationData::GetDataWithDefault<int32>(TEXT("MyIntValue"), 42);
```

**查询结构体/类类型**

```cpp
// 假设有一个 USTRUCT，例如 FMyConfigData
USTRUCT(BlueprintType)
struct FMyConfigData
{
    GENERATED_BODY()
    UPROPERTY() float Speed;
    UPROPERTY() FString Name;
};

FMyConfigData Config;
if (UE::GlobalConfigurationData::TryGetData(TEXT("MyStructEntry"), Config))
{
    // 使用 Config
}
// 注：该结构体的数据应以 JSON 格式存储，路由器会尝试解析。
```

**自定义路由器注册**

路由器通常在其构造函数中自动注册（通过基类 `IGlobalConfigurationRouter`），因此只需创建实例。

```cpp
// 示例：创建配置路由器，从指定的 ini 节读取数据
// 注意：基类构造函数自动调用内部注册逻辑
auto ConfigRouter = MakeShared<FGlobalConfigurationConfigRouter>(
    TEXT("MyCustomSection"),  // 自定义 ini 节名
    TEXT("MyCustomRouter"),   // 路由器名称（用于调试/日志）
    0                         // 优先级，介于 INT32_MIN 和 INT32_MAX 之间
);
// ConfigRouter 会一直存在，直到被销毁或程序退出
```

### 进阶用法

**获取所有已注册的数据（调试用）**

```cpp
TMap<FString, TMap<FString, TSharedRef<FJsonValue>>> AllData;
IGlobalConfigurationRouter::GetAllRegisteredData(AllData);
for (const auto& EntryPair : AllData)
{
    const FString& EntryName = EntryPair.Key;
    UE_LOG(LogTemp, Log, TEXT("Entry: %s"), *EntryName);
    for (const auto& RouterPair : EntryPair.Value)
    {
        UE_LOG(LogTemp, Log, TEXT("  From Router '%s': %s"),
            *RouterPair.Key,
            *IGlobalConfigurationRouter::TryPrintString(RouterPair.Value));
    }
}
```

**使用控制台命令路由（仅 Debug 构建）**

在控制台输入：

```
GCD.RegisterValue MyTestValue "100"
GCD.RegisterValue MyTestStruct "{\"Speed\": 10.0, \"Name\": \"Test\"}"
GCD.UnregisterValue MyTestValue
```

然后通过 `TryGetData` 查询即可获取对应值。

**自定义路由器示例**

```cpp
// 从远程 HTTP 服务获取数据的自定义路由器
class FRemoteConfigRouter : public IGlobalConfigurationRouter
{
public:
    FRemoteConfigRouter()
        : IGlobalConfigurationRouter(TEXT("RemoteConfig"), 500) // 优先级 500
    {
        // 初始化 HTTP 请求等
    }

protected:
    virtual TSharedPtr<FJsonValue> TryGetDataFromRouter(const FString& EntryName) const override
    {
        // 向远程服务发送请求并返回 JSON 值
        // 如果未找到返回 nullptr
        return nullptr;
    }

    virtual void GetAllDataFromRouter(TMap<FString, TSharedRef<FJsonValue>>& DataOut) const override
    {
        // 填充所有数据（可选实现）
    }
};

// 使用时：只需创建实例
auto RemoteRouter = MakeShared<FRemoteConfigRouter>();
```

## Demo 示例

以下是一个完整的可运行示例，演示如何查询配置数据并注册自定义路由器。

### MyConfigurationSubsystem.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "GlobalConfigurationData.h"
#include "GlobalConfigurationRouter.h"
#include "Routers/GlobalConfigurationConfigRouter.h"
#include "MyConfigurationSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FMyDemoConfig
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadWrite, EditAnywhere) float Gravity = 1.0f;
    UPROPERTY(BlueprintReadWrite, EditAnywhere) FString LevelName = TEXT("Default");
};

UCLASS()
class UMyConfigurationSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override
    {
        // 1. 创建一个配置路由器（从 DefaultEngine.ini 读取 [GlobalConfigurationData]）
        //    由于基类自动注册，无需手动持有引用（但最好保持存活直到子系统销毁）
        ConfigRouter = MakeShared<FGlobalConfigurationConfigRouter>(
            TEXT("GlobalConfigurationData"),
            TEXT("DemoConfigRouter"),
            -100 // 低优先级
        );

        // 2. 查询几个值
        float Speed;
        if (UE::GlobalConfigurationData::TryGetData(TEXT("PlayerSpeed"), Speed))
        {
            UE_LOG(LogTemp, Log, TEXT("PlayerSpeed = %f"), Speed);
        }

        FMyDemoConfig DemoConfig;
        if (UE::GlobalConfigurationData::TryGetData(TEXT("DemoConfig"), DemoConfig))
        {
            UE_LOG(LogTemp, Log, TEXT("DemoConfig.Gravity = %f, Level = %s"),
                DemoConfig.Gravity, *DemoConfig.LevelName);
        }

        // 3. 使用默认值
        int32 MaxPlayers = UE::GlobalConfigurationData::GetDataWithDefault<int32>(TEXT("MaxPlayers"), 8);
        UE_LOG(LogTemp, Log, TEXT("MaxPlayers = %d"), MaxPlayers);
    }

    virtual void Deinitialize() override
    {
        ConfigRouter.Reset();
    }

private:
    TSharedPtr<FGlobalConfigurationConfigRouter> ConfigRouter;
};
```

### MyConfigurationSubsystem.cpp

```cpp
#include "MyConfigurationSubsystem.h"
```

### 对应 ini 配置 (DefaultEngine.ini)

```ini
[GlobalConfigurationData]
PlayerSpeed=500.0
DemoConfig={"Gravity":9.81,"LevelName":"TestMap"}
MaxPlayers=16
```

## 模块依赖

以下依赖为 `GlobalConfigurationDataCore` 模块的公共依赖（使用者需添加）：

| 模块 | 用途 |
|---|---|
| `Json` | 解析与序列化 JSON 格式的配置数据 |
| `JsonUtilities` | JSON 值辅助操作 |

其他依赖（如 `Core`, `CoreUObject`, `Engine`）为标准引擎模块，无需额外列出。

## 维护状态

### 近期更新

- 2025-09-10 `61b63b3f` — [GCD] Add support to auto flatten json objects with a single entry  
- 2025-07-18 `10de61f9` — [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting  
- 2025-06-23 `bfa3140f` — [Misc] Fix GlobalConfigurationData test ensures  
- 2025-06-17 `8a2ca4d6` — [UE] Add experimental Global Configuration Data  

### 维护评价

- **创建时间**：2025年6月（至今不足半年），属于全新系统。
- **近期更新**：最近一次更新为2025年9月，引入了 JSON 对象自动展平功能；更新频率约每1-2个月一次，符合实验性插件的活跃度。
- **活跃度**：仍在积极开发中，无废弃迹象。
- **已知限制**：目前尚未发布正式版本（Version 0.1），API 可能随迭代变化；部分功能（如控制台路由）仅在 Debug/Development 构建中可用。
- **推荐使用**：适合作为配置查询的底层框架，尤其是在需要多源覆盖的场景；但应做好 API 不稳定的心理准备，建议对关键功能编写适配层。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/)（无专属页面，参考实验性功能文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData/Tests)
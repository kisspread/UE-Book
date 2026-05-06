# Global Configuration Data

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据查询 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GlobalConfigurationData` (Runtime), `GlobalConfigurationDataCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData) | |

---

## 用途

`Global Configuration Data` 提供了一套统一的查询接口，允许游戏或工具在**不依赖具体配置来源（如本地文件、远程服务器、命令行参数、热修复等）**的情况下，获取各种类型（bool、int、float、string、text、struct、object）的配置数据。插件内部维护了一个“配置路由器”系统，可根据优先级或来源类型自动选择最合适的配置数据提供者。

该插件解决了以下问题：
- 项目中有多种配置源（如 .ini、命令行、DB、热更新补丁），业务逻辑需要与具体来源解耦。
- 希望统一配置数据的访问路径，避免每个模块自行实现配置查询。
- 需要支持运行时动态注入/覆盖配置（如热修复、A/B 测试）。

---

## 使用场景

- **全局游戏设定**：例如是否开启调试模式、显示帧率、语言选择等，可以在启动时由启动参数或服务器下发覆盖。
- **特性开关**：通过外部来源（如后端配置面板）控制某些功能是否启用，无需重新打包。
- **多环境配置**：开发、测试、正式环境下使用不同的配置源，插件自动识别并返回对应值。
- **运行时调试**：通过控制台命令注入临时配置覆盖，方便开发和QA。

---

## 蓝图用法

插件通过 `UGlobalConfigurationDataBlueprintLibrary` 提供了一套**纯函数**，所有函数均为 `BlueprintPure`，可直接在蓝图中调用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Config Data Bool` | 通过名称查询 bool 值，成功返回 true，失败返回 false | `UGlobalConfigurationDataBlueprintLibrary` |
| `Get Config Data Int` | 查询 int32 值 | 同上 |
| `Get Config Data Float` | 查询 float 值 | 同上 |
| `Get Config Data String` | 查询 FString 值 | 同上 |
| `Get Config Data Text` | 查询 FText 值 | 同上 |
| `Get Config Data Struct` | 查询结构体（需传入 `UScriptStruct`），输出 `FInstancedStruct` | 同上 |
| `Get Config Data Object` | 查询 UObject 引用（`ValueInOut` 为输入输出对象） | 同上 |
| `Get Config Data Bool (with Default)` | 查询 bool 值，若不存在则返回默认值 | 同上 |
| `Get Config Data Int (with Default)` | 查询 int32，支持默认值 | 同上 |
| `Get Config Data Float (with Default)` | 查询 float，支持默认值 | 同上 |
| `Get Config Data String (with Default)` | 查询 FString，支持默认值 | 同上 |
| `Get Config Data Text (with Default)` | 查询 FText，支持默认值 | 同上 |

### 使用示例（蓝图描述）

1. **获取配置中的 bool 值**  
   - 将 `Get Config Data Bool` 节点拖入事件图表。
   - 在 `EntryName` 引脚输入配置名称（如 `"bEnableDebugOverlay"`）。
   - 连接 `Return Value` 判断查询是否成功，成功则从 `Value Out` 引脚读取结果。

2. **带默认值的整数查询**  
   - 使用 `Get Config Data Int (with Default)`，输入 `EntryName` 和 `Default Value`。
   - 直接获取整数值（查询不到时返回默认值），适合简单的固定默认场景。

3. **结构体查询**  
   - 先拖入 `Get Config Data Struct`，在 `Struct Type` 引脚选择目标结构体类型（如 `Vector2D`）。
   - `Value Out` 输出 `FInstancedStruct`，可再通过 `Break Instanced Struct` 转换为具体结构体。

> **注意**：查询失败时（`Return Value = false`），输出值不保证有效，建议先检查返回值再使用。

---

## C++ 用法

### 头文件引入

```cpp
#include "GlobalConfigurationDataBlueprintLibrary.h"
```

### 基本用法

从 `UGlobalConfigurationDataBlueprintLibrary` 静态函数直接查询：

```cpp
// 查询 bool 配置
bool bValue = false;
bool bFound = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataBool(TEXT("bEnableFeatureX"), bValue);
if (bFound)
{
    // 使用 bValue
}

// 查询带默认值的字符串
FString Name = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataStringWithDefault(
    TEXT("PlayerName"), TEXT("DefaultName"));
```

### 进阶用法

如果需要查询结构体，需提供 `UScriptStruct*` 和输出 `FInstancedStruct`：

```cpp
// 查询 FVector 结构体配置
UScriptStruct* VectorStruct = TBaseStructure<FVector>::Get();
FInstancedStruct ValueOut;
bool bFound = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataStruct(
    TEXT("MyLocation"), VectorStruct, ValueOut);

if (bFound && ValueOut.IsValid())
{
    const FVector& Location = *ValueOut.GetPtr<FVector>();
    // ...
}
```

> **注意**：插件本身还包含 `GlobalConfigurationDataCore` 模块，若需直接访问底层的配置路由器系统（`IConfigurationRouter`），可包含 `"GlobalConfigurationData.h"` 并链接对应模块。上述蓝图库是推荐的统一接口。

---

## Demo 示例

一个简单的 C++ 示例，展示在 `AGameMode` 中读取配置：

### MyGameMode.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class AMyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
};
```

### MyGameMode.cpp

```cpp
#include "MyGameMode.h"
#include "GlobalConfigurationDataBlueprintLibrary.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 查询是否启用调试模式
    bool bDebugMode = false;
    bool bFound = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataBool(
        TEXT("bDebugMode"), bDebugMode);
    if (bFound && bDebugMode)
    {
        UE_LOG(LogTemp, Warning, TEXT("Debug mode is ON"));
    }

    // 获取玩家初始生命值，默认 100
    int32 MaxHealth = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataIntWithDefault(
        TEXT("PlayerMaxHealth"), 100);
    UE_LOG(LogTemp, Log, TEXT("Max Health: %d"), MaxHealth);
}
```

> **注意**：需在 `Build.cs` 中添加 `"GlobalConfigurationData"` 依赖（见下一节）。

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GlobalConfigurationDataCore` | 配置路由核心逻辑（自动隐式依赖） |

**其他依赖**：无特殊依赖（仅标准 Core/Engine/Slate 等）。

如果要在你的模块中使用蓝图函数库，只需在 `PublicDependencyModuleNames` 中添加 `"GlobalConfigurationData"`：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "GlobalConfigurationData" });
```

若需直接使用底层 Core 类型（如 `IGlobalConfigurationSourceInterface`），还需添加 `"GlobalConfigurationDataCore"`。

---

## 维护状态

### 近期更新

- 2025-09-10 `61b63b3f` [GCD] Add support to auto flatten json objects with a single entry  
- 2025-07-18 `10de61f9` [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting  
- 2025-06-23 `bfa3140f` [Misc] Fix GlobalConfigurationData test ensures  
- 2025-06-17 `8a2ca4d6` [UE] Add experimental Global Configuration Data  

### 维护评价

- **创建时间**：2025-06-17，距今约 4 个月，属于全新插件。
- **近期更新**：最近一次 commit 在 2025-09-10（约 1 个月前），添加了 JSON 扁平化支持；之前有控制台路由和测试修复，说明功能仍在积极开发中。
- **活跃度**：频繁更新，解决了实际问题（热修复路由、JSON 处理）。
- **是否推荐使用**：插件处于**实验性**阶段，API 可能发生变化，但核心架构已可用。适合需要多源配置查询的先行项目，建议在非生产环境下试用并关注后续更新。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData)
- [官方文档](https://docs.unrealengine.com)（当前插件暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GlobalConfigurationData/Tests)
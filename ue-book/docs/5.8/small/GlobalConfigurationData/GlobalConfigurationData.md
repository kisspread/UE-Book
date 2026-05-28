# Global Configuration Data

> A system that is used to query configuration data that can come from many different sources without knowing specifically which one.

| 属性 | 值 |
|---|---|
| 中文名 | 全局配置数据 |
| 分类 | Misc |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `GlobalConfigurationData` (Runtime), `GlobalConfigurationDataCore` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData) | |

## 用途

GlobalConfigurationData (GCD) 插件的核心目的是**为引擎和游戏提供一个统一的、与数据源解耦的配置查询系统**。它解决了以下问题：
1.  **配置源异构**：游戏中的配置数据可能来自多个地方，如命令行参数、配置文件、游戏模式设置、运行时状态等。
2.  **查询接口统一**：上层逻辑（如角色行为、UI显示）无需关心配置数据具体从哪个系统获取，只需通过统一的接口（如 `GetConfigDataBool`）按名称查询。
3.  **运行时可变**：配置值可以在运行时被不同的“配置路由器”动态覆盖或修改（如通过控制台命令），方便调试和快速迭代。

它本质上是一个**配置数据的服务定位器**，解耦了配置数据的提供者和消费者。

## 使用场景

-   你的游戏或插件需要从多个独立的系统（如在线服务、本地文件、游戏内设置）读取配置项。
-   你希望在测试环境中（如自动化测试、开发人员快速测试）能够方便地覆盖或注入配置值，而不修改核心游戏逻辑。
-   你需要一个中央节点来管理那些可能影响多处代码的全局设置（如游戏难度倍数、功能开关）。

## 蓝图用法

该插件主要通过 `UGlobalConfigurationDataBlueprintLibrary` 提供蓝图节点。所有节点均为纯函数（`BlueprintPure`），并返回 `bool` 指示是否成功获取数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetConfigDataBool` | 根据名称查询布尔型配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataInt` | 根据名称查询整型配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataFloat` | 根据名称查询浮点型配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataString` | 根据名称查询字符串配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataText` | 根据名称查询本地化文本配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataStruct` | 根据名称和UScriptStruct类型查询结构体配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataObject` | 根据名称查询对象指针配置数据。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataBoolWithDefault` | 查询布尔配置，若未找到则返回默认值。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataIntWithDefault` | 查询整型配置，若未找到则返回默认值。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataFloatWithDefault` | 查询浮点配置，若未找到则返回默认值。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataStringWithDefault` | 查询字符串配置，若未找到则返回默认值。 | `UGlobalConfigurationDataBlueprintLibrary` |
| `GetConfigDataTextWithDefault` | 查询文本配置，若未找到则返回默认值。 | `UGlobalConfigurationDataBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **基本查询**：在蓝图中，从 `GetConfigDataFloat` 节点的 `EntryName` 引脚拉出，连接一个字符串常量节点（例如 `DifficultyMultiplier`）。`ValueOut` 引脚可连接到需要使用该配置值的变量或函数输入。
2.  **带默认值的查询**：使用 `GetConfigDataFloatWithDefault` 节点，除了输入 `EntryName`，还需为 `DefaultValue` 引脚提供一个默认浮点值。该节点会直接返回配置值或默认值，简化分支逻辑。
3.  **成功判断**：利用返回的 `bool` 值进行分支判断，确保在配置不存在时程序有合理的后备逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "GlobalConfigurationDataBlueprintLibrary.h" // 用于蓝图库静态函数
#include "GlobalConfigurationDataSubsystem.h"        // 用于子系统接口（更底层）
```

### 基本用法

使用蓝图库的静态函数进行查询，这是最简单的使用方式。

```cpp
// 在角色或某个管理器类中查询一个配置值
bool bSuccess = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataBool(TEXT("bEnableDoubleJump"), bCanDoubleJump);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Double Jump enabled: %s"), bCanDoubleJump ? TEXT("True") : TEXT("False"));
}
else
{
    UE_LOG(LogWarning, TEXT("Failed to query 'bEnableDoubleJump' config."));
}
```

### 进阶用法

直接使用 `UGlobalConfigurationDataSubsystem` 可以更灵活地操作，并可能涉及到自定义配置路由器。

```cpp
// 获取子系统
UGlobalConfigurationDataSubsystem* GCDSubsystem = GetWorld()->GetSubsystem<UGlobalConfigurationDataSubsystem>();
if (GCDSubsystem)
{
    // 使用 FName 版本查询（内部使用更高效）
    float PlayerSpeed = 0.f;
    if (GCDSubsystem->GetConfigDataFloat(FName("PlayerSpeed"), PlayerSpeed))
    {
        // 应用速度到角色移动组件
        CharacterMovement->MaxWalkSpeed = PlayerSpeed;
    }

    // 查询一个结构体配置（需要 FInstancedStruct）
    // FInstancedStruct MyStruct;
    // if (GCDSubsystem->GetConfigDataStruct(FName("SomeStructData"), FMyConfigStruct::StaticStruct(), MyStruct))
    // {
    //     const FMyConfigStruct& Config = MyStruct.Get<FMyConfigStruct>();
    //     // ... 使用结构体数据
    // }
}
```

## Demo 示例

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
	virtual void StartPlay() override;
};
```

### MyGameMode.cpp
```cpp
#include "MyGameMode.h"
#include "GlobalConfigurationDataBlueprintLibrary.h"
#include "Kismet/GameplayStatics.h"

void AMyGameMode::StartPlay()
{
	Super::StartPlay();

	// 从GCD系统查询游戏难度相关配置
	bool bSuccess;
	float DifficultyScale = 1.0f;
	int32 MaxEnemies = 10;
	FString GameVersion = TEXT("Unknown");

	bSuccess = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataFloatWithDefault(TEXT("DifficultyScale"), 1.0f);
	if (bSuccess) // 对于WithDefault版本，此检查其实总是成功
	{
		DifficultyScale = bSuccess; // 修正：WithDefault直接返回值
	}

	// 正确使用WithDefault节点
	DifficultyScale = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataFloatWithDefault(TEXT("DifficultyScale"), 1.0f);
	MaxEnemies = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataIntWithDefault(TEXT("MaxEnemyCount"), 10);
	GameVersion = UGlobalConfigurationDataBlueprintLibrary::GetConfigDataStringWithDefault(TEXT("GameVersion"), TEXT("1.0.0"));

	UE_LOG(LogTemp, Log, TEXT("GCD Config: Difficulty=%f, MaxEnemies=%d, Version=%s"),
		DifficultyScale, MaxEnemies, *GameVersion);
}
```

## 模块依赖

从 `Build.cs` 文件分析，使用此插件的核心模块 `GlobalConfigurationData` 需要以下依赖：

| 模块 | 用途 |
|---|---|
| `GlobalConfigurationDataCore` | 提供核心数据类型和接口定义 |
| `StructUtils` | 用于支持 `FInstancedStruct`，实现对任意结构体的存储和查询 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-09-10 | `79a1090c` | [GCD] Add support to auto flatten json objects with a single entry | 新增功能：支持自动扁平化仅含单个条目的JSON对象，简化配置输入格式。 |
| 2025-07-18 | `10de61f9` | [GCD] Make console command router debug only, add a 'hotfix' config router for high priority setting | 将控制台命令路由器改为仅调试可用，新增用于高优先级设置的“热修复”配置路由器。 |
| 2025-06-23 | `bfa3140f` | [Misc] Fix GlobalConfigurationData test ensures | 修复GCD测试中的断言（Ensure）问题，提升测试稳定性。 |
| 2025-06-17 | `8a2ca4d6` | [UE] Add experimental Global Configuration Data | 初始提交：添加实验性全局配置数据插件。 |

### 维护评价

-   **状态**: **活跃维护中**。
-   **依据**: 该插件于2025年6月创建，截至2025年9月，最近一次更新（添加JSON扁平化支持）距今仅1个多月。从提交历史看，插件处于积极开发和功能迭代阶段。
-   **实验性**: 插件当前标记为 `IsExperimentalVersion=true`，表明其API和功能可能尚未稳定，未来版本中可能会有破坏性更改。
-   **推荐使用**: **可以谨慎使用和研究**。适合作为项目内配置系统架构的参考，或用于内部工具和实验性功能。不建议在即将发布、要求高度稳定的项目核心逻辑中深度依赖，应持续关注其API变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData)
-   [官方文档]() (无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GlobalConfigurationData/Tests)
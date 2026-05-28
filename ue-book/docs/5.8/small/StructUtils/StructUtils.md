# Struct Utils

> Experimental Struct Utilities supplying InstancedStruct type

| 属性 | 值 |
|---|---|
| 中文名 | 结构体工具 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `StructUtils` (Runtime), `StructUtilsEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-04-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils) | |

## 用途

StructUtils 插件的核心是提供 `FInstancedStruct` 类型，这是一个可以在运行时持有任何 `UStruct` 实例的通用结构体容器。它解决了在蓝图和 C++ 中需要存储和传递不同结构体类型（运行时多态）的场景，避免了使用 `UObject` 或 `UProperty` 反射的复杂性。它为技能系统、数据驱动配置、网络复制等需要灵活数据容器的功能提供了基础。

## 使用场景

- 你需要一个统一的容器来存储不同类型的数据结构（例如，技能的不同伤害参数、物品的不同附加属性）。
- 你正在实现一个数据驱动的系统，其中配置表的列可以是多种不同的 `UStruct` 类型。
- 你需要在蓝图中传递和操作具有不同内部结构的数据包。

## 蓝图用法

`FInstancedStruct` 是一个 `FStruct`，在蓝图中主要通过其暴露的属性和通过蓝图反射系统生成的函数节点进行操作。核心操作是设置其类型（即要实例化的 `UStruct` 类）和数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Struct` | 设置 FInstancedStruct 实例所包含的结构体数据。 | `FInstancedStruct` |
| `Reset` | 重置 FInstancedStruct，清除其持有的类型和数据。 | `FInstancedStruct` |
| `Get Struct` | 获取 FInstancedStruct 实例当前持有的结构体数据（需使用正确的类型）。 | `FInstancedStruct` |
| `IsValid` | 检查 FInstancedStruct 是否持有有效的结构体实例。 | `FInstancedStruct` |

### 使用示例（蓝图描述）

1.  在蓝图中声明一个 `FInstancedStruct` 类型的变量（例如命名为 `SkillData`）。
2.  使用 **Set Struct** 节点。
3.  连接 **Struct Value** 引脚：创建一个具体的结构体（如 `FDamageInfo` 或 `FHealingEffect`）并将其连接到此引脚。
4.  **Instanced Struct** 引脚应连接到你的 `SkillData` 变量。
5.  后续，当需要读取数据时，使用 **Get Struct** 节点，并确保你连接到的结构体输出引脚的类型与当初存入的类型完全一致，否则会获取失败。

## C++ 用法

### 头文件引入

```cpp
#include "StructUtils/InstancedStruct.h"
```

### 基本用法

```cpp
#include "StructUtils/InstancedStruct.h"

// 定义一个示例 UStruct
USTRUCT(BlueprintType)
struct FMyTestData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 Value = 0;
};

// 在代码中使用 FInstancedStruct
void AMyActor::TestInstancedStruct()
{
	// 1. 创建一个空的 FInstancedStruct
	FInstancedStruct InstancedData;

	// 2. 设置它持有的结构体类型和数据
	FMyTestData TestData;
	TestData.Value = 42;
	InstancedData.SetStruct<FMyTestData>(TestData);

	// 3. 检查有效性并读取数据
	if (InstancedData.IsValid())
	{
		// 安全地获取指针
		if (const FMyTestData* DataPtr = InstancedData.GetStructPtr<FMyTestData>())
		{
			UE_LOG(LogTemp, Log, TEXT("Value is: %d"), DataPtr->Value); // 输出 42
		}

		// 或者直接获取引用（确保类型安全）
		const FMyTestData& DataRef = InstancedData.Get<FMyTestData>();
		UE_LOG(LogTemp, Log, TEXT("Value is: %d"), DataRef.Value); // 输出 42
	}

	// 4. 重置
	InstancedData.Reset();
}
```
*代码基于通用的 FInstancedStruct API 模式编写。*

### 进阶用法

```cpp
// 用于需要运行时多态的容器
TArray<FInstancedStruct> ActionEffects;

// 添加不同类型的效果
FMyDamageEffect DamageEffect;
DamageEffect.DamageAmount = 10.0f;
ActionEffects.Add(FInstancedStruct::Make<FMyDamageEffect>(DamageEffect));

FMyBuffEffect BuffEffect;
BuffEffect.Duration = 5.0f;
ActionEffects.Add(FInstancedStruct::Make<FMyBuffEffect>(BuffEffect));

// 遍历处理
for (const FInstancedStruct& Effect : ActionEffects)
{
	if (Effect.IsValid())
	{
		// 通常需要知道具体类型，或使用基类/接口
		if (const FMyDamageEffect* DmgEffect = Effect.GetStructPtr<FMyDamageEffect>())
		{
			// 处理伤害效果
		}
		else if (const FMyBuffEffect* BuffEffect = Effect.GetStructPtr<FMyBuffEffect>())
		{
			// 处理 Buff 效果
		}
	}
}
```

## Demo 示例

```cpp
// MyStructUtilsActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StructUtils/InstancedStruct.h"
#include "MyStructUtilsActor.generated.h"

USTRUCT(BlueprintType)
struct FSampleStructA
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite)
	float Alpha = 0.0f;
};

USTRUCT(BlueprintType)
struct FSampleStructB
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadWrite)
	FString Name = TEXT("Default");
};

UCLASS()
class AMyStructUtilsActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyStructUtilsActor();

	virtual void BeginPlay() override;

private:
	UPROPERTY()
	FInstancedStruct ActiveData;
};
```

```cpp
// MyStructUtilsActor.cpp
#include "MyStructUtilsActor.h"

AMyStructUtilsActor::AMyStructUtilsActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyStructUtilsActor::BeginPlay()
{
	Super::BeginPlay();

	// 演示切换持有不同类型
	FSampleStructA StructA;
	StructA.Alpha = 3.14f;
	ActiveData.SetStruct(FSampleStructA::StaticStruct(), reinterpret_cast<uint8*>(&StructA));

	if (const FSampleStructA* APtr = ActiveData.GetStructPtr<FSampleStructA>())
	{
		UE_LOG(LogTemp, Log, TEXT("Alpha: %f"), APtr->Alpha);
	}

	FSampleStructB StructB;
	StructB.Name = TEXT("Hello StructUtils");
	ActiveData.SetStruct(FSampleStructB::StaticStruct(), reinterpret_cast<uint8*>(&StructB));

	if (const FSampleStructB* BPtr = ActiveData.GetStructPtr<FSampleStructB>())
	{
		UE_LOG(LogTemp, Log, TEXT("Name: %s"), *BPtr->Name);
	}
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。`StructUtils` 模块依赖 `Engine`，`StructUtilsEngine` 模块无显式公开依赖，通常依赖 `CoreUObject`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-08-05 | `5bf7f335` | Iris - Move InstancedStructNetSerializer to IrisCore. | 将InstancedStruct网络序列化器移至IrisCore模块。 |
| 2024-08-01 | `0e320e33` | Iris - Crash fix for removing InstancedStruct from a replicated array and adding the same struct typ | 修复从复制数组中移除再添加同类型InstancedStruct导致的崩溃。 |
| 2024-06-28 | `8083cf8c` | Iris - Adjust includes due to StructUtils moving. | 因StructUtils移动调整头文件包含。 |
| 2024-06-28 | `3680fd08` | Iris - Initial naive but working version of FInstancedStructNetSerializer to be able to replicate FI | Iris模块中FInstancedStruct网络序列化器的初始可用版本。 |
| 2024-06-19 | `e6d36d75` | Remove references to deprecated plugin StructUtils (now part of CoreUObject) | 移除对已废弃插件StructUtils的引用（现已成为CoreUObject的一部分）。 |

### 维护评价

**维护不活跃，可能废弃**。该插件创建于2021年，是实验性质。从2024年6月的提交信息可以看出，其核心功能（`FInstancedStruct` 及其网络序列化）正在被迁移到引擎的核心模块 **Iris** 和 **CoreUObject** 中。最近的更新主要是为了处理这次迁移以及相关的bug修复。这意味着该独立插件很可能在未来版本中被移除，其功能将由引擎核心直接提供。

**不建议在新项目中作为长期依赖使用**。应关注 `FInstancedStruct` 在引擎核心（如 `CoreUObject`）中的新位置和用法。如果现有项目依赖它，需做好未来迁移的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/StructUtils)
# Render Grid

> Advanced pipeline for use in creating rendered cinematics.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染网格 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderGrid` (Runtime), `RenderGridDeveloper` (Runtime), `RenderGridEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid) | |

## 用途

RenderGrid 插件旨在提供一个用于创建和渲染过场动画的高级管线。它允许用户在编辑器内定义、组织和批量管理渲染作业（Jobs）。核心功能是通过蓝图（Blueprint Graph）来驱动渲染过程，使得非程序员也能配置复杂的渲染序列。`RenderGridDeveloper` 模块是该管线的运行时开发支持模块，提供了在蓝图和C++中查询、获取和操作 `RenderGrid` 资产的核心API。

## 使用场景

- **过场动画批量渲染**：当你的项目需要渲染大量包含不同镜头、参数或场景配置的过场动画序列时，可以使用 RenderGrid 来定义和管理这些作业，实现一键批量渲染。
- **非程序员驱动渲染管线**：游戏设计师或技术美术希望通过蓝图来动态调整渲染设置、控制渲染流程或响应渲染事件，无需编写C++代码。
- **资产化管理渲染配置**：将复杂的渲染作业序列保存为可复用的资产（`RenderGrid` Asset），方便在团队中共享、版本控制和迭代。

## 蓝图用法

核心的 `URenderGridDeveloperLibrary` 类提供了在蓝图中访问所有 `RenderGrid` 资产的静态函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All Render Grid Assets` | 获取项目中所有现存的渲染网格资产（包括磁盘和内存中，会加载未加载的资产）。 | `URenderGridDeveloperLibrary` |
| `Get Render Grid Asset` | 根据给定的对象路径获取单个渲染网格资产（会加载未加载的资产）。 | `URenderGridDeveloperLibrary` |

### 使用示例（蓝图描述）

1.  **遍历项目中的所有RenderGrid资产**：
    *   添加一个 `Get All Render Grid Assets` 节点。
    *   将其输出的数组连接到一个 `For Each Loop` 节点。
    *   在循环体中，可以使用 `Get Render Grid` (来自 `URenderGridBlueprint`) 或直接使用 `URenderGrid` 对象来访问和控制每个渲染网格资产。

2.  **通过路径加载特定RenderGrid资产**：
    *   添加一个 `Get Render Grid Asset` 节点。
    *   将一个包含资产路径的字符串变量（例如 “/Game/Cinematics/MyRenderGrid”）连接到 `Object Path` 输入引脚。
    *   获取返回的 `URenderGrid*` 对象，即可对其属性和方法进行操作。

## C++ 用法

### 头文件引入

```cpp
#include "RenderGridDeveloper/RenderGridDeveloperLibrary.h"
#include "RenderGridDeveloper/Blueprints/RenderGridBlueprint.h"
```

### 基本用法

从 `RenderGridDeveloperLibrary` 的接口推断，可以同步获取所有渲染网格资产。
```cpp
// 获取项目中所有的渲染网格资产实例（较慢，避免每帧调用）
TArray<URenderGrid*> AllGridAssets = URenderGridDeveloperLibrary::GetAllRenderGridAssets();
for (URenderGrid* GridAsset : AllGridAssets)
{
    UE_LOG(LogTemp, Log, TEXT("Found RenderGrid Asset: %s"), *GridAsset->GetName());
    // 可以在此处对 GridAsset 进行操作
}

// 通过路径获取单个资产
URenderGrid* SpecificGrid = URenderGridDeveloperLibrary::GetRenderGridAsset(TEXT("/Game/Path/To/Your/Grid"));
if (SpecificGrid)
{
    // 使用 SpecificGrid
}
```

### 进阶用法

结合 `URenderGridBlueprint`，可以访问资产的蓝图图部分。
```cpp
// 获取所有蓝图类型的资产，可能包含用户自定义的蓝图逻辑
TArray<URenderGridBlueprint*> AllBlueprints = URenderGridDeveloperLibrary::GetAllRenderGridBlueprintAssets();
for (URenderGridBlueprint* BP : AllBlueprints)
{
    // 获取纯数据的渲染网格（无蓝图图）
    URenderGrid* DataGrid = BP->GetRenderGrid();
    // 获取包含蓝图图的渲染网格（蓝图实例或默认对象）
    URenderGrid* GraphGrid = BP->GetRenderGridWithBlueprintGraph();
    
    // 注意：GetRenderGridWithBlueprintGraph() 和 GetRenderGridClassDefaultObject() 的区别
    // 前者返回蓝图类的实例（如果存在），后者返回蓝图子类的CDO（类默认对象）。
}
```

## Demo 示例

以下是一个使用 `RenderGridDeveloper` 模块功能的 Actor 类最小示例。

**RenderGridActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RenderGridActor.generated.h"

class URenderGrid;

UCLASS()
class YOURPROJECT_API ARenderGridActor : public AActor
{
	GENERATED_BODY()
	
public:	
	ARenderGridActor();

protected:
	virtual void BeginPlay() override;

public:	
	// 要加载的RenderGrid资产路径
	UPROPERTY(EditAnywhere, Category = "RenderGrid")
	FString GridAssetPath = TEXT("/Game/Path/To/Your/Grid");

private:
	UPROPERTY()
	TObjectPtr<URenderGrid> LoadedGrid;
};
```

**RenderGridActor.cpp**
```cpp
#include "RenderGridActor.h"
#include "RenderGridDeveloper/RenderGridDeveloperLibrary.h"
#include "RenderGridDeveloper/Blueprints/RenderGridBlueprint.h"

ARenderGridActor::ARenderGridActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ARenderGridActor::BeginPlay()
{
	Super::BeginPlay();

	// 使用Developer库加载指定的RenderGrid资产
	LoadedGrid = URenderGridDeveloperLibrary::GetRenderGridAsset(GridAssetPath);
	if (LoadedGrid)
	{
		UE_LOG(LogTemp, Warning, TEXT("Successfully loaded RenderGrid: %s"), *LoadedGrid->GetName());
		// 在这里可以对LoadedGrid进行进一步的操作，例如：
		// - 获取其作业列表
		// - 启动渲染队列
		// - 蓝图中通过LoadedGrid的引用调用自定义函数
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to load RenderGrid at path: %s"), *GridAssetPath);
	}
}
```

## 模块依赖

基于 `RenderGridDeveloper` 作为运行时模块，以及 `RenderGridBlueprint` 继承自 `UEditorUtilityBlueprint` 的事实，其独特依赖主要包括：

| 模块 | 用途 |
|---|---|
| `RenderGridCore` | 提供 `URenderGrid` 等核心数据类型定义。 |
| `UnrealEd` | 用于蓝图编译器集成和编辑器功能（`URenderGridBlueprint` 依赖）。 |
| `Kismet` | 用于蓝图编译相关的基础设施（`FRenderGridBlueprintCompiler` 依赖）。 |

*注意：`RenderGridCore` 可能是一个未在提供信息中列出的内部模块，但根据 `URenderGridBlueprint` 和 `URenderGrid` 的关系推断其存在。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构FJsonObject以支持FString和UE::FSharedString，优化内存使用。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移为UE_LOGF，统一日志格式。 |
| 2026-03-02 | `9758fa58` | FORT-984709 - Remove string duplication in FJsonObject to free memory | 移除FJsonObject中的字符串重复以释放内存。 |
| 2025-09-15 | `60737405` | Render Grid: fixed crash when passing in an empty string when setting remote control values | 修复设置远程控制值传入空字符串时导致的崩溃。 |
| 2025-06-11 | `b57e00bc` | Replace some usages of FORCEINLINE with inline in Rendering modules. | 在渲染模块中将部分FORCEINLINE替换为inline。 |

### 维护评价

- **实验性**：该插件明确标记为实验性 (`IsExperimentalVersion=true`)，且默认未启用 (`EnabledByDefault=false`)。
- **活跃维护**：根据提交历史，该插件在近 1 年内（2025-2026）仍有持续的功能更新、优化和Bug修复，表明它处于**活跃开发与维护**状态。
- **推荐使用**：对于需要在项目中探索或实现高级渲染管线的团队，该插件是一个有价值的实验性工具。但由于其**实验性**标签，在生产环境中使用需自行评估风险和稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/RenderGrid)
- [官方文档]() (无)
- [测试用例]() (未在提供的信息中找到，可能位于 `Engine/Tests/` 或插件内部)
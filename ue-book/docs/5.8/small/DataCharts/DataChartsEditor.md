# Data Charts

> Generate charts based on data tables（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据图表 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（图表资产模板、编辑器扩展） |
| 模块 | `DataCharts` (Runtime), `DataChartsEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-01-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataCharts) | |

## 用途

这是一个**数据可视化工具**，旨在解决从 DataTable（数据表）资产快速创建图表（Chart）资产的问题。它简化了在编辑器中将结构化数据转换为直观可视化图表的过程，主要用于数据分析、调试和展示。该插件通过扩展编辑器的放置模式，允许用户直接将数据表资产拖入场景，从而自动生成对应的图表资产，省去了手动创建和配置的繁琐步骤。

## 使用场景

- 你是一名游戏策划或数据分析师，已经为游戏内容（如角色属性、物品掉落率、经济系统数值）创建了 DataTable，但需要快速生成柱状图、折线图等来可视化这些数据，以便检查数据分布和平衡性。
- 你是一名技术美术或程序员，在编辑器调试时，希望将某张 DataTable 中的特定数据实时渲染成图表，以监控或分析动态变化的数据（例如性能指标、玩家行为数据）。
- 你在使用虚拟制片工具链，需要基于场景或资产管理数据生成分析图表。

## 蓝图用法

插件通过扩展编辑器的放置模式（Placement Mode）提供核心功能，主要操作在编辑器的“放置”面板完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| **Placeable Item Registration** | 将 DataTable 注册为可放置项，使其出现在“放置”面板的特定类别下。 | `FDataChartsPlacement` |

### 使用示例（蓝图描述）

1.  **启用插件**：在编辑器中，通过 `编辑 -> 插件` 找到并启用 `DataCharts` 插件。
2.  **放置图表**：在编辑器的内容浏览器中选中一个 `DataTable` 资产。
3.  打开 `放置` 面板（`窗口 -> 放置`），你应该能看到一个新的类别（可能名为 “Data Charts” 或类似名称）。
4.  从该类别中，将代表你所选 DataTable 的图标拖拽到关卡或场景视图中。
5.  系统会基于该 DataTable 自动创建并放置一个 `Chart` 资产或 Actor。

## C++ 用法

由于提供的源码片段有限且未包含测试用例，以下用法基于对模块接口和放置注册机制的分析。

### 头文件引入

```cpp
// 使用图表资产相关功能
#include "DataCharts.h"

// 在编辑器模块中操作放置模式
#include "DataChartsEditor.h"
```

### 基本用法

要扩展插件的功能或理解其工作原理，需要与 `FDataChartsPlacement` 交互。该类负责在编辑器中注册可放置的数据图表项。

```cpp
// 示例：在某个自定义编辑器模块的 StartupModule 中，参考 DataChartsEditor 的方式注册放置项
// 假设我们有一个自定义的放置类别，也可以使用类似的机制。
#include "DataChartsPlacement.h"

void FMyEditorModule::StartupModule()
{
    // 插件自身的放置项已在 DataChartsEditor 模块的 StartupModule 中通过 FDataChartsPlacement::Register() 注册
    // 这里演示如何注册一个自定义的放置项
    FPlaceableItem* PlaceableItem = new FPlaceableItem(
        UAssetEditor::StaticClass(), // 要放置的资产类（示例）
        FAssetData(), // 相关的资产数据
        FName("My Custom Category") // 放置类别
    );
    
    // 通常使用 FEditorModeRegistry 或其他编辑器 API 注册，具体实现需参考 FDataChartsPlacement 的源码
}
```

### 进阶用法

插件的核心可能涉及将 `UDataTable` 的数据读取并转换为图表库（如 Slate 内置的 SGraphEditor 或第三方库）可理解的数据格式。一个简化的数据处理流程如下：

```cpp
// 假设流程 (非插件实际 API，仅为说明逻辑)
// 1. 获取选中的 DataTable
UDataTable* MyDataTable = /* ... */;

// 2. 读取表中的数据行
TArray<FMyRowStruct*> AllRows;
MyDataTable->GetAllRows<FMyRowStruct>(TEXT("Context"), AllRows);

// 3. 将数据转换为图表所需的点集或系列
TArray<FVector2D> ChartPoints;
for (const FMyRowStruct* Row : AllRows)
{
    ChartPoints.Add(FVector2D(Row->X_Value, Row->Y_Value));
}

// 4. 使用数据创建或更新图表资产 (假设存在 UDataChartAsset 类)
UDataChartAsset* ChartAsset = NewObject<UDataChartAsset>();
ChartAsset->SetDataPoints(ChartPoints);
ChartAsset->SetChartType(EChartType::Bar); // 设置图表类型
```

## Demo 示例

以下是一个创建并设置简单数据图表资产的 C++ 示例。

**DataChartDemo.h**
```cpp
// DataChartDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DataChartDemo.generated.h"

class UDataChartAsset;
class UDataTable;

UCLASS()
class ADataChartDemo : public AActor
{
	GENERATED_BODY()
	
public:	
	ADataChartDemo();

	// 要用于生成图表的数据表资产
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "DataChart")
	TObjectPtr<UDataTable> SourceDataTable;

	// 生成的目标图表资产
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "DataChart")
	TObjectPtr<UDataChartAsset> GeneratedChart;

	// 生成图表的函数
	UFUNCTION(BlueprintCallable, Category = "DataChart")
	void GenerateChartFromTable();
};
```

**DataChartDemo.cpp**
```cpp
// DataChartDemo.cpp
#include "DataChartDemo.h"
// 假设存在这些头文件，实际需要根据插件源码调整
#include "Engine/DataTable.h"
#include "DataChartAsset.h" // 假设这是插件定义的图表资产类

ADataChartDemo::ADataChartDemo()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ADataChartDemo::GenerateChartFromTable()
{
	if (!SourceDataTable)
	{
		UE_LOG(LogTemp, Warning, TEXT("SourceDataTable is null. Cannot generate chart."));
		return;
	}

	// 1. 创建或获取图表资产
	if (!GeneratedChart)
	{
		GeneratedChart = NewObject<UDataChartAsset>(this);
	}

	// 2. 从数据表读取数据 (假设数据表行结构为 FSampleRow)
	// TArray<FSampleRow*> AllRows;
	// SourceDataTable->GetAllRows<FSampleRow>(TEXT("ADataChartDemo"), AllRows);

	// 3. 将数据转换并设置给图表资产 (此为示意，实际接口需参考插件)
	// TMap<FName, float> DataMap;
	// for (const FSampleRow* Row : AllRows)
	// {
	//     DataMap.Add(Row->Label, Row->Value);
	// }
	// GeneratedChart->SetDataFromMap(DataMap);
	// GeneratedChart->SetChartTitle(SourceDataTable->GetName());
	
	UE_LOG(LogTemp, Log, TEXT("Chart generated from table: %s"), *SourceDataTable->GetName());
}
```

## 模块依赖

根据插件的编辑器功能和放置模式扩展的常见模式，其依赖关系推断如下：

| 模块 | 用途 |
|---|---|
| `DataCharts` | 提供核心的图表资产类型定义和运行时数据结构 |
| `PlacementMode` | 用于在编辑器“放置”面板中注册自定义可放置项 |
| `ToolMenus` | 用于扩展编辑器的菜单和工具栏 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 一次批量的插件目录结构或路径调整，未涉及功能变更。 |
| 2022-11-03 | `fa90b399` | Added includes for future change. This changelist only contains added #include and a couple of empty | 为未来的代码变更做准备，添加了头文件包含，本身无功能影响。 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 将插件内的供应商链接更新为HTTPS协议，属于安全与维护性更新。 |
| 2021-01-26 | `d52549d8` | Placement Mode: shape category special icon handling and updates to plugins using FPlaceableItem | 针对放置模式API的更新，本插件的放置项注册方式可能随之调整。 |
| 2020-09-03 | `7a7c1c0c` | Updated Data Charts Plugin for new Placement Mode API. Included temporary icon that will be replace | 为适配新的放置模式API进行了更新，并添加了临时图标。 |

### 维护评价

该插件**维护不活跃**，处于**实验性（Beta）** 状态。

- **年龄**：插件创建于2020年初，至今已超过5年。
- **更新频率**：自2023年1月后，该插件目录下再无任何功能性提交。之前的提交也多为全局性调整（如安全链接更新、目录重构）或为未来代码预留的占位提交，而非实质性的功能开发或问题修复。
- **功能状态**：作为 Beta 版本，其API和功能可能不稳定，且缺乏近期活跃的维护，意味着可能存在未修复的bug或与新版UE引擎不完全兼容的风险。
- **推荐程度**：**不推荐用于生产项目**。该插件更适合作为学习参考或在内部工具开发中谨慎尝试。对于正式的图表需求，建议评估更活跃、功能更完善的第三方图表插件或库。

**警告：该插件已超过两年没有实质性功能更新，且标记为实验性，使用时需自行承担兼容性和稳定性风险。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DataCharts)
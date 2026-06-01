# Interchange Tests

> Plugin for Interchange automation tests.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 互换测试 |
| 分类 | Testing |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeTestEditor` (Runtime), `InterchangeTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-20 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests) | |

## 用途

该插件为 Unreal Engine 的 **Interchange** 资产导入/导出框架提供了一套**结构化的自动化测试框架**。它并非用于运行时功能，而是为开发者提供了一种验证 Interchange 管线正确性的标准化方法。

其核心是 **测试计划 (Test Plan)** 资产 (`UInterchangeImportTestPlan`)。开发者可以创建测试计划来定义一系列测试用例，每个用例指定要导入的资产类型、要执行的检查函数以及必要的参数。该插件会自动化执行这些计划，从而系统性地测试各种资产（如静态网格、骨骼网格、材质等）的导入流程是否正确。

## 使用场景

- 你是 **Interchange 框架或自定义导入管线的开发者** → 使用此插件创建测试计划，确保你的代码变更没有破坏已有的导入功能。
- 你需要 **为新支持的资产格式或导入器编写测试** → 在测试计划中添加新的测试用例，快速建立回归测试套件。
- 你在 **调试资产导入问题** → 通过测试计划复现特定的导入场景，便于定位问题。

## 蓝图用法

此插件主要是一个编辑器工具和测试框架，其核心操作在编辑器内完成，**并未在运行时暴露蓝图可调用的节点**。

### 核心交互（编辑器内操作）

| 操作 | 说明 | 所在类/资产 |
|---|---|---|
| 创建测试计划 | 在内容浏览器中右键创建 “Interchange Import Test Plan” 资产。 | `UAssetDefinition_InterchangeImportTestPlan` |
| 配置测试函数 | 在测试计划的细节面板中，为每个测试步骤选择要检查的资产类和对应的检查函数。 | `FInterchangeTestFunctionLayout` |
| 编辑管线设置 | 配置测试所使用的特定导入管线（Pipeline）参数。 | `FInterchangeTestPlanPipelineSettingsLayout` |
| 运行测试 | 通过引擎的自动化测试系统（Automation窗口）执行已配置的测试计划。 | `FInterchangeTestsModule` |

### 使用示例（蓝图描述）
1.  在内容浏览器中，右键选择 “资产” -> “其他” -> “Interchange Import Test Plan” 创建一个新资产。
2.  打开该资产，在其细节面板中，点击 “添加元素” 来添加一个测试函数。
3.  在 “资产类” 下拉菜单中选择要测试的资产类型（如 `StaticMesh`）。
4.  在 “检查函数” 下拉菜单中选择一个用于验证导入结果的函数（如某个 `CheckStaticMesh` 函数）。
5.  配置该函数所需的参数。
6.  保存测试计划。在 “自动化” 窗口中搜索相关测试并执行。

## C++ 用法

主要通过编写测试用例来驱动该框架，或扩展其检查函数。

### 头文件引入

```cpp
#include "InterchangeImportTestPlan.h"
#include "InterchangeTestFunction.h"
```

### 基本用法

以下示例展示了如何以编程方式创建一个简单的测试计划资产。
*（来源：基于框架设计的伪代码，类似于 `InterchangeTests` 模块中的测试用例创建逻辑）*

```cpp
// 创建一个新的测试计划资产
UPackage* TestPackage = CreatePackage(TEXT("/Game/Test/MyTestPlan"));
UInterchangeImportTestPlan* TestPlan = NewObject<UInterchangeImportTestPlan>(TestPackage, FName("MyTestPlan"), RF_Public | RF_Standalone);

// 获取其测试函数列表
TArray<FInterchangeTestFunction>& TestFunctions = TestPlan->GetTestFunctions();

// 添加一个测试函数（通常通过编辑器界面操作更直观，这里展示数据结构）
FInterchangeTestFunction NewTestFunc;
NewTestFunc.AssetClass = UStaticMesh::StaticClass();
NewTestFunc.CheckFunctionName = GET_FUNCTION_NAME_CHECKED(UStaticMesh, CheckImportResult); // 假设存在此函数
TestFunctions.Add(NewTestFunc);

// 保存资产
FAssetRegistryModule::AssetCreated(TestPlan);
TestPackage->MarkPackageDirty();
```

### 进阶用法

实现一个自定义的检查函数，该函数将在测试计划执行时被调用。

```cpp
// 在某个测试工具类中
UCLASS()
class UMyInterchangeTestUtils : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    // 自定义的检查函数，用于验证骨骼网格导入后的骨骼数量
    UFUNCTION(BlueprintCallable, Category = "InterchangeTest")
    static bool CheckSkeletalMeshBoneCount(UObject* ImportedAsset, int32 ExpectedBoneCount)
    {
        const USkeletalMesh* SkelMesh = Cast<USkeletalMesh>(ImportedAsset);
        if (!SkelMesh)
        {
            UE_LOG(LogTemp, Error, TEXT("Asset is not a SkeletalMesh!"));
            return false;
        }

        // 获取骨骼数据
        const FReferenceSkeleton& RefSkeleton = SkelMesh->GetRefSkeleton();
        if (RefSkeleton.GetNum() != ExpectedBoneCount)
        {
            UE_LOG(LogTemp, Error, TEXT("Bone count mismatch! Expected: %d, Got: %d"), ExpectedBoneCount, RefSkeleton.GetNum());
            return false;
        }
        
        return true;
    }
};
```

## Demo 示例

一个最小的、定义自定义检查函数的测试工具类。
*（注：此函数随后可在 InterchangeImportTestPlan 资产的“检查函数”下拉列表中找到并使用）*

```cpp
// MyInterchangeTestUtils.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "MyInterchangeTestUtils.generated.h"

UCLASS()
class MYTESTMODULE_API UMyInterchangeTestUtils : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * 自定义检查函数：验证静态网格导入后是否包含指定数量的材质槽。
	 * @param ImportedAsset 导入后的资产对象（由测试框架传入）
	 * @param ExpectedMaterialCount 期望的材质槽数量
	 * @return 测试是否通过
	 */
	UFUNCTION(BlueprintCallable, Category = "InterchangeTest|StaticMesh")
	static bool CheckStaticMeshMaterialSlotCount(UObject* ImportedAsset, int32 ExpectedMaterialCount);
};

// MyInterchangeTestUtils.cpp
#include "MyInterchangeTestUtils.h"
#include "Engine/StaticMesh.h"

bool UMyInterchangeTestUtils::CheckStaticMeshMaterialSlotCount(UObject* ImportedAsset, int32 ExpectedMaterialCount)
{
	const UStaticMesh* StaticMesh = Cast<UStaticMesh>(ImportedAsset);
	if (!StaticMesh)
	{
		UE_LOG(LogTemp, Error, TEXT("MyInterchangeTestUtils::CheckStaticMeshMaterialSlotCount - Imported asset is not a UStaticMesh."));
		return false;
	}

	const int32 ActualMaterialCount = StaticMesh->GetStaticMaterials().Num();
	if (ActualMaterialCount != ExpectedMaterialCount)
	{
		UE_LOG(LogTemp, Error, TEXT("Material slot count mismatch for StaticMesh '%s'. Expected: %d, Actual: %d"), 
			*StaticMesh->GetName(), ExpectedMaterialCount, ActualMaterialCount);
		return false;
	}

	return true;
}
```

## 模块依赖

要使用或扩展此插件的测试功能，你的模块需要依赖以下模块。

| 模块 | 用途 |
|---|---|
| `InterchangeFramework` | Interchange 核心导入/导出框架 |
| `InterchangeImport` | Interchange 的资产导入功能实现 |
| `InterchangeTests` | 本插件提供的测试计划和测试函数核心数据结构 |
| `AutomationController` | 用于运行和管理自动化测试 |
| `FunctionalTesting` | 提供更高级的功能测试支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版UE_LOGF格式。 |
| 2026-04-06 | `a3591f26` | [ContentBrowser] New Add Menu Interchange Menu | 内容浏览器新增Interchange测试计划资产的创建菜单。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了部分旧的遍历函数，并引入新的替代方法。 |
| 2026-03-18 | `44060456` | Interchange - Added support for import containing both SM and SKM at the same time. | 测试框架新增支持同时包含静态网格和骨骼网格的复合资产导入测试。 |
| 2026-03-04 | `7ceb4698` | Interchange - New Skeletal Mesh Combine Options | 新增对骨骼网格合并导入选项的测试支持。 |

### 维护评价

**活跃维护**。
- **创建时间**：约 4 年前（2022年）。
- **近期更新**：在近 2 个月内有多次提交，包括功能增强（新测试场景支持）、API 适配（日志宏、废弃函数）和编辑器集成改进。
- **维护状态**：持续活跃，更新内容聚焦于框架本身的完善和与 Interchange 核心功能的同步。
- **已知限制**：作为测试插件，其 `IsBetaVersion=true`，表明其 API 或内部结构仍可能调整。
- **推荐**：如果你是 Interchange 框架的开发者或需要对其进行深度测试，**强烈推荐使用**此插件作为标准测试工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/InterchangeTests/Source/InterchangeTests)
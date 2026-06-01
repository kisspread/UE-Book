# Functional Testing Editor

> （无描述）

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器功能测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FunctionalTestingEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2016-10-05 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/FunctionalTestingEditor) | |

## 用途

`FunctionalTestingEditor` 插件是为**编辑器环境**扩展标准功能测试 (`FunctionalTesting`) 框架的专用插件。它解决的核心问题是允许开发者创建和运行**仅在编辑器中**才有意义或需要编辑器特定API才能执行的功能测试。

其主要价值在于：
1.  **提供编辑器专属测试基类**：定义了 `AEditorFunctionalTest` 和 `AEditorScreenshotFunctionalTest`，这些测试 Actor 被明确标记为“仅编辑器加载”，确保它们不会包含在最终的游戏构建中，但可以在编辑器PIE（Play In Editor）中被自动发现和执行。
2.  **支持编辑器级截图比较测试**：为基于视觉比较的自动化测试（如UI渲染、材质效果）提供了编辑器端的基础设施。

简而言之，它使得开发者能够为编辑器工具、蓝图、材质编辑器操作等编写自动化验证用例。

## 使用场景

-   你正在开发或维护一个**编辑器工具插件**，需要验证其在编辑器中的交互和输出是否正确。
-   你需要对**蓝图节点**、**材质编辑器**或**UI Widget** 在编辑器中的特定状态进行视觉回归测试（截图比较）。
-   你的功能测试**必须依赖编辑器模块**（如 `EditorSubsystem`）或访问编辑器专有对象，因此无法在独立游戏运行时（非PIE）中执行。
-   你希望将测试与游戏代码解耦，确保这些测试只在开发阶段的编辑器环境中运行。

## 蓝图用法

此插件主要通过C++类提供基础功能，其蓝图用法核心在于**继承其提供的测试基类**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsEditorOnly` (Override) | 返回 `true`，标识此测试仅在编辑器中有效。 | `AEditorFunctionalTest`, `AEditorScreenshotFunctionalTest` |
| `IsEditorOnlyLoadedInPIE` (Override) | 返回 `true`，确保此测试在PIE模式下被加载和执行。 | `AEditorFunctionalTest`, `AEditorScreenshotFunctionalTest` |

### 使用示例（蓝图描述）

1.  **创建新蓝图**：在内容浏览器中，右键创建一个蓝图类，父类选择 `EditorFunctionalTest` (来自此插件)。
2.  **实现测试逻辑**：在蓝图事件图表中，实现 `ReceivePrepareTest` (测试准备)、`ReceiveStartTest` (测试开始) 等事件来编写你的编辑器自动化测试逻辑。例如，你可以模拟在编辑器中添加一个Actor，然后检查其属性。
3.  **运行测试**：通过编辑器的“自动化测试”窗口（通常在 `开发工具` -> `自动化`）找到并运行你的测试。由于基类标记了 `IsEditorOnly`，它只会在编辑器环境中被列出和执行。

## C++ 用法

### 头文件引入

```cpp
// 如果你需要访问插件的模块接口
#include "FunctionalTestingEditorModule.h"
// 主要用于继承编辑器功能测试基类
#include "EditorFunctionalTest.h"
```

### 基本用法

通过继承 `AEditorFunctionalTest` 来创建一个C++版本的编辑器专属功能测试。

```cpp
// MyEditorTest.h
#pragma once

#include "CoreMinimal.h"
#include "EditorFunctionalTest.h"
#include "MyEditorTest.generated.h"

UCLASS()
class AMyEditorTest : public AEditorFunctionalTest
{
	GENERATED_BODY()
	
public:
	// 测试开始时被框架调用
	virtual void StartTest() override;

protected:
	// 实现测试成功或失败的逻辑
	virtual void FinishTest(EFunctionalTestResult TestResult, const FString& Message) override;
};
```

```cpp
// MyEditorTest.cpp
#include "MyEditorTest.h"

void AMyEditorTest::StartTest()
{
	Super::StartTest();
	
	// 在这里编写你的编辑器测试逻辑
	// 例如：检查某个编辑器子系统是否已加载
	UE_LOG(LogTemp, Display, TEXT("Editor functional test started."));
	
	// 模拟一些操作...
	
	// 调用FinishTest来结束测试
	FinishTest(EFunctionalTestResult::Succeeded, TEXT("All checks passed."));
}
```

### 进阶用法

结合 `UGroundTruthData` 进行截图比较测试。你需要配合 `AScreenshotFunctionalTest` 的逻辑。

```cpp
// 在你的EditorScreenshotFunctionalTest子类中
virtual void StartTest() override
{
    Super::StartTest();
    // 设置好要比较的视口、Actor等
    // 框架会自动进行截图并与GroundTruthData进行比较
}
```

## Demo 示例

一个最小的、可编译的编辑器功能测试示例。

```cpp
// SimpleEditorTest.h
#pragma once

#include "CoreMinimal.h"
#include "EditorFunctionalTest.h"
#include "SimpleEditorTest.generated.h"

UCLASS()
class ASimpleEditorTest : public AEditorFunctionalTest
{
	GENERATED_BODY()

public:
	ASimpleEditorTest();
	
	virtual void StartTest() override;
	
private:
	UPROPERTY()
	UStaticMeshComponent* PreviewMesh;
};
```

```cpp
// SimpleEditorTest.cpp
#include "SimpleEditorTest.h"
#include "Components/StaticMeshComponent.h"

ASimpleEditorTest::ASimpleEditorTest()
{
	PrimaryActorTick.bCanEverTick = false;
	
	PreviewMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PreviewMesh"));
	RootComponent = PreviewMesh;
}

void ASimpleEditorTest::StartTest()
{
	Super::StartTest();
	
	// 在编辑器PIE中，检查刚创建的组件是否有效
	if (PreviewMesh && PreviewMesh->IsValidLowLevel())
	{
		FinishTest(EFunctionalTestResult::Succeeded, TEXT("Test Actor and component created successfully in editor."));
	}
	else
	{
		FinishTest(EFunctionalTestResult::Failed, TEXT("Failed to create test component."));
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `FunctionalTesting` | 核心功能测试框架，提供了基类 `AFunctionalTest` 和 `AScreenshotFunctionalTest`，以及测试结果枚举等。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 与内容浏览器新菜单相关的提交，可能影响资产创建流程。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的UE_LOG宏迁移到新的UE_LOGF格式。 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理了针对UE5.2版本的旧式头文件包含保护宏。 |
| 2024-10-22 | `cdf71bcf` | Rename confusing IsNonPIEEditorOnly actor function to IsEditorOnlyLoadedInPIE. | 将易混淆的`IsNonPIEEditorOnly`函数重命名为更清晰的`IsEditorOnlyLoadedInPIE`。 |
| 2024-09-13 | `7de8b5db` | EditorFunctionalTest actor instances are now available in PIE. | 修复了EditorFunctionalTest的Actor实例在PIE模式下不可用的严重问题。 |

### 维护评价

**总体评价：稳定维护中的基础设施插件。**

-   **年龄与活跃度**：该插件自2016年创建，已超过8年。最近的更新（2024-2026年）主要是代码维护、API重命名和兼容性修复，而非重大新功能。这表明其核心功能已成熟稳定。
-   **重要性**：作为 Epic Games 官方自动化测试框架的一部分，它是引擎持续集成和质量保障流程的基石，因此会持续获得必要的维护。
-   **使用建议**：**推荐使用**。对于需要编辑器环境自动化测试的开发者来说，这是官方且可靠的基础。需要注意它默认不启用（`EnabledByDefault: false`），你需要在项目的 `.uproject` 文件或插件设置中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/FunctionalTestingEditor)
-   [测试用例（可能位于引擎测试目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/FunctionalTests)
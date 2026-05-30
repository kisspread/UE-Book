# DMX Control Console

> Console that can be patched from DMX Libraries and sends DMX to Output Ports

| 属性 | 值 |
|---|---|
| 中文名 | DMX 控制台 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DMXControlConsole` (Runtime), `DMXControlConsoleEditor` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2023-03-17 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole) | |

## 用途

DMX Control Console 插件提供了一个功能全面的 **DMX 控制台编辑器**。它允许灯光设计师在 Unreal Engine 内直接创建、编辑和回放 DMX 场景。核心功能包括：
1.  **场景打补丁**：从 DMX Library 中选择灯具补丁（Fixture Patches）并将其添加到控制台。
2.  **参数控制**：通过虚拟推子（Faders）实时控制 DMX 通道值。支持绝对值、相对值、物理单位等多种控制模式。
3.  **布局与组织**：提供灵活的布局系统（水平、垂直、网格），可以创建多个自定义布局来组织控制器。
4.  **场景存储与回放**：通过 Cue Stack 系统存储和调用不同的 DMX 场景（Cue）。
5.  **实时发送**：将控制台中的值实时发送到配置的 DMX 输出端口。

这个插件存在的意义是将一个功能完善的灯光控制台集成到虚拟制作工作流中，让灯光师和虚拟制作团队能够在一个统一的环境中进行灯光编程、预览和实时调整，无需依赖外部的硬件控制台。

## 使用场景

*   你在进行**虚拟制作**（Virtual Production）或**现场活动灯光设计**，需要在引擎内实时控制舞台灯光（如聚光灯、洗光灯、LED 面板）。
*   你需要在拍摄前或排练中**预编程复杂的灯光场景**（Cues），并快速在不同场景间切换。
*   你希望用鼠标或触控板直观地调整大量 DMX 参数，而不是通过数字输入框。
*   你需要为不同的控制器组（Fader Groups）创建自定义的**工作区布局**，以提高效率。
*   你已经在使用 Unreal 的 **DMX 插件**进行灯光控制，需要一个官方的、集成的编辑器界面来管理 DMX 数据流。

## 蓝图用法

该插件的核心逻辑主要由编辑器模块 (`DMXControlConsoleEditor`) 提供，专注于提供 Slate UI 交互体验。运行时模块 (`DMXControlConsole`) 包含数据模型和控制器类。虽然大部分高级交互发生在编辑器 UI 中，但以下核心类提供了可供蓝图或C++调用的接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddToLayout` | 将一个或多个 Fader Group 添加到布局中，并返回对应的控制器 | `UDMXControlConsoleEditorGlobalLayoutBase` |
| `Possess` | 让一个 Fader Group Controller 接管一个或多个 Fader Group | `UDMXControlConsoleFaderGroupController` |
| `SetValue` | 设置 Element Controller 及其所有下属元素的值 | `UDMXControlConsoleElementController` |
| `GenerateElementControllers` | 为 Controller 下的所有 Fader Group 元素自动生成 Element Controller | `UDMXControlConsoleFaderGroupController` |
| `CreateElementController` | 为指定的元素创建一个新的 Element Controller | `UDMXControlConsoleFaderGroupController` |

### 使用示例（蓝图描述）

1.  **获取编辑器模型**：通常通过 `UDMXControlConsoleEditorModel` 来访问和操作当前的控制台状态。在编辑器工具中，此模型通常由 `FDMXControlConsoleEditorToolkit` 持有。
2.  **操作布局**：获取 `UDMXControlConsoleEditorLayouts` 对象，然后使用 `GetActiveLayout()` 获取当前布局，调用 `AddToLayout` 来添加 Fader Group。
3.  **控制数值**：定位到一个 `UDMXControlConsoleElementController`，然后直接设置其 `Value` 属性，或调用 `SetValue` 函数，该值会传播到它控制的所有 DMX 元素。
4.  **场景管理**：通过 `UDMXControlConsoleEditorPlayMenuModel` 或直接操作 `FDMXControlConsoleCueStackModel` 来添加、存储、调用和删除 Cue。

## C++ 用法

该插件的 C++ API 专注于数据模型和控制器的程序化操作。由于没有提供具体的测试用例，以下示例基于头文件分析。

### 头文件引入

```cpp
#include "DMXControlConsole.h" // 运行时数据模型
#include "DMXControlConsoleEditorModel.h" // 编辑器模型
#include "DMXControlConsoleFaderGroupController.h" // 控制器核心类
#include "DMXControlConsoleElementController.h"
```

### 基本用法

```cpp
// 获取当前编辑的控制台（假设在编辑器上下文中）
UDMXControlConsole* ControlConsole = ...; // 通过某种方式获取
UDMXControlConsoleEditorModel* EditorModel = NewObject<UDMXControlConsoleEditorModel>();
EditorModel->Initialize(ControlConsole);

// 获取或创建一个 Fader Group Controller
UDMXControlConsoleData* ConsoleData = EditorModel->GetControlConsoleData();
if (ConsoleData && ConsoleData->GetFaderGroups().Num() > 0)
{
    UDMXControlConsoleFaderGroup* FirstFaderGroup = ConsoleData->GetFaderGroups()[0];
    
    // 创建一个控制器来管理这个 Fader Group
    UDMXControlConsoleFaderGroupController* Controller = NewObject<UDMXControlConsoleFaderGroupController>();
    Controller->Possess(FirstFaderGroup);
    
    // 为控制器内的元素生成子控制器
    Controller->GenerateElementControllers();
    
    // 设置第一个 Element Controller 的值
    TArray<UDMXControlConsoleElementController*> ElementControllers = Controller->GetElementControllers();
    if (ElementControllers.Num() > 0)
    {
        ElementControllers[0]->SetValue(0.75f); // 设置为 75%
    }
}
```

### 进阶用法

```cpp
// 创建一个自定义布局
UDMXControlConsoleEditorLayouts* Layouts = EditorModel->GetControlConsoleLayouts();
UDMXControlConsoleEditorGlobalLayoutBase* CustomLayout = Layouts->AddUserLayout(TEXT(“MyLayout”));

// 将多个 Fader Group 分组到一个控制器中，并添加到布局
TArray<UDMXControlConsoleFaderGroup*> GroupsToGroup = { GroupA, GroupB };
UDMXControlConsoleFaderGroupController* GroupedController = CustomLayout->AddToLayout(GroupsToGroup, TEXT(“GroupA+B”));
GroupedController->Group(); // 执行分组操作以优化控制器

// 应用一个全局过滤器
TSharedPtr<FDMXControlConsoleGlobalFilterModel> FilterModel = EditorModel->GetGlobalFilterModel();
FilterModel->SetGlobalFilter(TEXT(“Wash 1”)); // 过滤名字包含“Wash 1”的控制器
```

## Demo 示例

以下示例创建了一个简单的程序化 DMX 控制台控制器。

**ControlConsoleDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "ControlConsoleDemo.generated.h"

class UDMXControlConsole;
class UDMXControlConsoleEditorModel;
class UDMXControlConsoleFaderGroupController;

UCLASS()
class AControlConsoleDemoActor : public AActor
{
    GENERATED_BODY()

public:
    AControlConsoleDemoActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "DMX")
    UDMXControlConsole* ControlConsoleAsset;

private:
    UPROPERTY()
    TObjectPtr<UDMXControlConsoleEditorModel> EditorModel;

    UPROPERTY()
    TObjectPtr<UDMXControlConsoleFaderGroupController> TestController;

    void CreateDemoController();
};
```

**ControlConsoleDemo.cpp**
```cpp
#include "ControlConsoleDemo.h"
#include "DMXControlConsole.h"
#include "DMXControlConsoleData.h"
#include "DMXControlConsoleEditorModel.h"
#include "DMXControlConsoleFaderGroupController.h"
#include "DMXControlConsoleFaderGroup.h"
#include "DMXControlConsoleElementController.h"

AControlConsoleDemoActor::AControlConsoleDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AControlConsoleDemoActor::BeginPlay()
{
    Super::BeginPlay();

    if (ControlConsoleAsset)
    {
        // 初始化编辑器模型
        EditorModel = NewObject<UDMXControlConsoleEditorModel>(this);
        EditorModel->Initialize(ControlConsoleAsset);
        CreateDemoController();
    }
}

void AControlConsoleDemoActor::CreateDemoController()
{
    UDMXControlConsoleData* ConsoleData = EditorModel->GetControlConsoleData();
    if (!ConsoleData || ConsoleData->GetFaderGroups().IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("No Fader Groups found in Control Console."));
        return;
    }

    // 为第一个 Fader Group 创建控制器
    TestController = NewObject<UDMXControlConsoleFaderGroupController>(this);
    TestController->Possess(ConsoleData->GetFaderGroups()[0]);
    TestController->GenerateElementControllers();

    // 将所有元素的值设置为一半
    for (UDMXControlConsoleElementController* ElemController : TestController->GetElementControllers())
    {
        float Min = ElemController->GetMinValue();
        float Max = ElemController->GetMaxValue();
        float Mid = (Min + Max) / 2.0f;
        ElemController->SetValue(Mid);
    }

    UE_LOG(LogTemp, Log, TEXT("Created a controller with %d element controllers."),
        TestController->GetElementControllers().Num());
}
```

## 模块依赖

从代码结构推断，要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `DMX` | 核心 DMX 框架，提供 DMX Library, Fixture Patch 等基础数据类型。 |
| `DMXControlConsole` | 本插件的运行时数据模型和控制器。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制作：将多个VP资产移动到不同的资产类别。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | [回退] - CL51314860。 |
| 2026-02-27 | `7723864b` | Move FCoreDelegates::OnPostEngineInit to FCoreDelegates::GetOnPostEngineInit() to fix missing regist | 将FCoreDelegates::OnPostEngineInit迁移为GetOnPostEngineInit()以修复缺失的注册。 |

### 维护评价

*   **创建时间**：插件于 2023 年创建，相对年轻。
*   **最近更新**：最后实质性更新在 2026 年 2 月和 5 月，**维护活跃**。更新内容包括代码清理、兼容性修复和功能迁移。
*   **维护状态**：**活跃维护中**。作为 Epic 官方虚拟制作工具链的一部分，其更新频率和内容质量较高。
*   **已知限制**：`.uplugin` 中 `IsExperimentalVersion=true`，表明此插件仍处于**实验阶段**，API 和功能可能在未来版本中发生变化。
*   **推荐使用**：对于需要在 UE 内进行 DMX 灯光控制和预览的虚拟制作项目，**强烈推荐使用**。应留意其“实验性”状态，并在升级引擎版本时进行充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/DMX/DMXControlConsole)
- [官方文档]() （.uplugin 中 DocsURL 为空）
- [测试用例]() （未在提供信息中发现）
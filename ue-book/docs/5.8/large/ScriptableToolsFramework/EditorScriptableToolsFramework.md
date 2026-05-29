# Scriptable Tools Framework

> Blueprint-Scriptable extension to the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 可脚本化工具框架 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ScriptableToolsFramework` (Runtime), `EditorScriptableToolsFramework` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ScriptableToolsFramework) | |

## 用途

此插件为 Unreal Engine 的交互工具框架（Interactive Tools Framework, ITF）提供了一个蓝图可编程的扩展层。它允许开发者（尤其是技术美术和设计师）无需编写 C++ 代码，仅使用蓝图即可快速创建、组合和定制编辑器内的交互式工具，例如自定义的建模、绘制或场景操作工具。这解决了传统上创建自定义编辑器工具需要深厚 C++ 知识的问题，极大地提高了工具开发的效率和可及性。

## 使用场景

- **快速原型制作**：当你需要为特定的美术资产创建流程（如批量调整材质参数、生成程序化组件）快速搭建一个编辑器工具时，使用此框架进行蓝图原型设计。
- **技术美术定制**：作为技术美术，你需要为团队创建一套简单易用的场景布局、光影调整或物理模拟工具，但又不想深入底层 C++ 代码。
- **扩展编辑器功能**：开发者希望为现有的编辑器功能（如地形编辑、植被刷）添加新的子模式或参数控制，可以通过蓝图派生和扩展现有的工具基类。
- **教育培训**：用于教学演示如何构建交互式编辑器工具，蓝图可视化脚本更易于理解和调试。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ReinitializeScriptableTools` | 重新扫描并加载项目中所有可脚本化的工具类。这是刷新工具列表的核心方法。 | `UScriptableToolSet` |
| `ForEachScriptableTool` | 遍历当前已加载的所有可脚本化工具类及其构建器，执行自定义操作。 | `UScriptableToolSet` |
| `OnClicked` | 当单击工具被激活时调用。可在此重写自定义点击行为。 | `UEditorScriptableSingleClickTool` |
| `OnClickedAndDragged` | 当点击并拖拽工具被激活时调用。可在此重写拖拽行为。 | `UEditorScriptableClickDragTool` |
| `OnDragStarted` | 在点击拖拽工具中，鼠标按下并开始拖拽时调用。 | `UEditorScriptableClickDragTool` |
| `OnDragUpdated` | 在点击拖拽工具中，鼠标持续拖拽时每帧调用。 | `UEditorScriptableClickDragTool` |
| `OnDragEnded` | 在点击拖拽工具中，鼠标释放结束拖拽时调用。 | `UEditorScriptableClickDragTool` |

### 使用示例（蓝图描述）

1.  **获取工具集**：在任意蓝图中，通过 `Get Scriptable Tool Set` 节点获取 `UScriptableToolSet` 实例。
2.  **刷新工具列表**：调用 `Reinitialize Scriptable Tools` 节点。这将异步加载项目中所有标记为可脚本化的工具类。
3.  **列出工具**：调用 `For Each Scriptable Tool` 节点，并连接一个 `For Each Loop` 循环体。在循环体内，你可以访问每个工具的 `Tool Class` 和 `Tool Builder` 信息，并填充到列表视图或组合框中。
4.  **使用工具**：当用户从列表中选择一个工具后，你可以通过 ITF 的标准流程激活该工具，蓝图中定义的重写函数（如 `OnClicked`）将在工具运行时被调用。

## C++ 用法

### 头文件引入

```cpp
#include "ScriptableToolsFramework/ScriptableInteractiveTool.h"
#include "ScriptableToolsFramework/BaseTools/ScriptableSingleClickTool.h"
// 如果在编辑器模块中使用编辑器扩展工具：
#include "EditorScriptableToolsFramework/BaseTools/EditorScriptableSingleClickTool.h"
```

### 基本用法

从提供的类定义可以看出，创建自定义工具的最基本方式是继承一个基类并重写其蓝图可实现的事件。

**创建一个简单的点击工具：**

```cpp
// MySimpleClickTool.h
#pragma once
#include "EditorScriptableToolsFramework/BaseTools/EditorScriptableSingleClickTool.h"
#include "MySimpleClickTool.generated.h"

UCLASS()
class UMySimpleClickTool : public UEditorScriptableSingleClickTool
{
    GENERATED_BODY()
public:
    // 重写蓝图可调用的点击事件
    virtual void OnClicked_Implementation(const FInputDeviceRay& ClickPos) override;
};

// MySimpleClickTool.cpp
#include "MySimpleClickTool.h"

void UMySimpleClickTool::OnClicked_Implementation(const FInputDeviceRay& ClickPos)
{
    // 获取点击位置的世界坐标
    FVector WorldPos = ClickPos.WorldRay.Origin + ClickPos.WorldRay.Direction * ClickPos.WorldRay.Length;
    UE_LOG(LogTemp, Log, TEXT("Clicked at World Position: %s"), *WorldPos.ToString());
    // 在此添加你的自定义逻辑...
}
```

### 进阶用法

结合 `UScriptableToolSet` 进行工具管理和查询。

```cpp
// 在某个编辑器工具或自定义面板的代码中
#include "EditorScriptableToolsFramework/ScriptableToolSet.h"

void FMyEditorPanel::ListAllScriptableTools()
{
    // 获取或创建工具集单例
    UScriptableToolSet* ToolSet = GEditor->GetEditorSubsystem<UScriptableToolSet>();
    if (ToolSet)
    {
        // 使用 ForEach 遍历所有工具
        ToolSet->ForEachScriptableTool(
            [](UClass* ToolClass, UBaseScriptableToolBuilder* ToolBuilder)
            {
                if (ToolClass)
                {
                    UE_LOG(LogTemp, Log, TEXT("Found Scriptable Tool: %s"), *ToolClass->GetName());
                }
            }
        );
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，定义了一个简单的点击工具，在点击位置生成一个临时的调试球体。

```cpp
// SimpleClickSpawnTool.h
#pragma once
#include "EditorScriptableToolsFramework/BaseTools/EditorScriptableSingleClickTool.h"
#include "SimpleClickSpawnTool.generated.h"

UCLASS()
class USimpleClickSpawnTool : public UEditorScriptableSingleClickTool
{
    GENERATED_BODY()
public:
    virtual void OnClicked_Implementation(const FInputDeviceRay& ClickPos) override;
    virtual void OnPropertyModified(UObject* PropertySet, FProperty* Property) override;
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;

private:
    UPROPERTY()
    float SpawnRadius = 100.0f;
};
```

```cpp
// SimpleClickSpawnTool.cpp
#include "SimpleClickSpawnTool.h"
#include "Engine/World.h"
#include "Components/SphereComponent.h"
#include "GameFramework/Actor.h"
#include "UObject/ConstructorHelpers.h"

void USimpleClickSpawnTool::Setup()
{
    Super::Setup();
    // 在工具栏中显示一个属性，允许用户修改 SpawnRadius
    AddPropertySet<USimpleClickSpawnTool>();
}

void USimpleClickSpawnTool::Shutdown(EToolShutdownType ShutdownType)
{
    Super::Shutdown(ShutdownType);
}

void USimpleClickSpawnTool::OnPropertyModified(UObject* PropertySet, FProperty* Property)
{
    // 可选：当用户在细节面板修改属性时，实时预览或更新状态
}

void USimpleClickSpawnTool::OnClicked_Implementation(const FInputDeviceRay& ClickPos)
{
    UWorld* World = GetWorld();
    if (!World) return;

    FHitResult HitResult;
    // 进行一个简单的线性检测来找到点击表面
    if (World->LineTraceSingleByChannel(HitResult, ClickPos.WorldRay.Origin, ClickPos.WorldRay.Origin + ClickPos.WorldRay.Direction * 10000.f, ECC_WorldStatic))
    {
        FVector SpawnLocation = HitResult.Location + HitResult.ImpactNormal * 10.f; // 沿法线偏移一点
        FActorSpawnParameters SpawnParams;
        SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

        // 生成一个带有球体组件的临时Actor
        AActor* SpawnedActor = World->SpawnActor<AActor>(AActor::StaticClass(), SpawnLocation, FRotator::ZeroRotator, SpawnParams);
        if (SpawnedActor)
        {
            USphereComponent* SphereComp = NewObject<USphereComponent>(SpawnedActor);
            SphereComp->SetSphereRadius(SpawnRadius);
            SphereComp->SetVisibility(true);
            SphereComp->SetCollisionProfileName(TEXT("NoCollision"));
            SphereComp->RegisterComponent();
            SpawnedActor->SetRootComponent(SphereComp);
            UE_LOG(LogTemp, Log, TEXT("Spawned debug sphere at: %s"), *SpawnLocation.ToString());
        }
    }
}
```

## 模块依赖

从 .uplugin 的 `Plugins` 字段和模块定义推断。

| 模块 | 用途 |
|---|---|
| `MeshModelingToolset` | 提供核心建模工具框架，本插件基于此框架扩展。 |
| `MeshModelingToolsetExp` | 提供实验性的建模工具集，本插件可能引用其中的实验性功能。 |
| `ToolWidgets` | 提供工具 UI 组件（如可拖拽覆盖层），用于构建工具界面。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `6cab4de5` | ScriptableTools: Refactor SDraggableBoxOverlay usage to isolate ToolWidgets dependency to Scriptable | 重构UI依赖，将ToolWidgets组件隔离到脚本化工具模块中，提升模块化。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的UE_LOGF宏格式，保持代码一致性。 |
| 2026-02-06 | `fca152ce` | ScriptableToolsFramework: Only reference ToolWidgets if building developer tools | 优化依赖，仅在构建开发工具时才引用ToolWidgets模块。 |
| 2026-02-06 | `ac856ee6` | Updating tooltips to make Capture Priority values clearer. | 更新工具提示文本，使“捕获优先级”参数更易于理解。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了日志输出中格式化字符串的错误。 |

### 维护评价

- **创建时间**：插件于 2024 年 1 月底创建，历史相对较短。
- **更新频率**：最近一次实质性更新（模块化重构、UI 依赖隔离）发生在 2026 年 4 月，表明它仍在**积极维护和改进**。
- **当前状态**：插件仍处于 **Beta 版本** (`IsBetaVersion: true`)，且默认不启用 (`EnabledByDefault: false`)，这意味着 API 和功能可能会发生变化，不建议在对稳定性要求极高的正式项目核心功能中依赖它。
- **综合评价**：这是一个**活跃开发中**的**实验性/Beta** 插件。它代表了 Epic Games 在让编辑器工具开发更易用方面所做的努力。推荐用于**内部工具开发、原型设计和技术探索**。由于其 Beta 状态，使用时需关注版本更新日志，并为未来可能的 API 变动做好准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ScriptableToolsFramework)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
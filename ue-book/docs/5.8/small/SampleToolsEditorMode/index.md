# Sample Tools Editor Mode

> Sample Tools Mode includes a set of sample Tools demonstrating capabilities of the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 示例工具编辑模式 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SampleToolsEditorMode` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2024-01-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/SampleToolsEditorMode) | |

## 用途

这是一个教学和示例性质的编辑器插件。其主要用途是向开发者演示如何利用 **Unreal Engine 的交互式工具框架 (Interactive Tools Framework)** 来构建自定义的编辑器工具模式。它本身不是一个面向最终用户的生产工具，而是一个开发者学习、参考和快速原型化的起点。通过分析这个插件的源码，开发者可以理解 `UEdMode` 如何与 `UInteractiveTool`、`UInteractiveToolBuilder`、输入路由、属性面板等核心组件协同工作，从而创建自己的复杂编辑器交互工具。

## 使用场景

*   **你是引擎或工具开发者**，想要学习如何从零开始构建一个带有自定义交互式工具的编辑器模式。
*   **你正在开发一个需要复杂编辑器交互（如网格表面绘制、距离测量、放置物体）的插件**，可以参考此插件的架构和实现模式。
*   **你想快速验证一个工具想法**，可以基于此插件进行修改和扩展，而无需从头搭建整个框架。

## 蓝图用法

此插件未暴露任何可供蓝图直接调用的函数或属性。其核心功能通过 C++ 实现，并在编辑器界面（工具面板）中提供用户交互入口。

## C++ 用法

### 头文件引入

若要基于此插件进行扩展或学习，通常需要引入以下头文件：

```cpp
#include “SampleToolsEditorMode.h”
// 可能还需要引入各个示例工具的头文件，例如：
#include “SampleTools/MeasureDistanceSampleTool.h”
```

### 基本用法：理解模式入口

一个自定义编辑器模式的核心是继承 `UEdMode`。`USampleToolsEditorMode` 展示了最小实现：

```cpp
// 来自：Source/Public/SampleToolsEditorMode.h
UCLASS()
class USampleToolsEditorMode : public UEdMode
{
    GENERATED_BODY()

public:
    // 定义此模式的唯一标识符
    const static FEditorModeID EM_SampleToolsEditorModeId;

    USampleToolsEditorMode();
    virtual ~USampleToolsEditorMode();

    // 进入此模式时调用，是初始化工具和上下文的理想位置
    virtual void Enter() override;
    // 当场景中 Actor 选择变化时通知此模式
    virtual void ActorSelectionChangeNotify() override;
    // 创建此模式的工具栏 UI (Toolkit)
    virtual void CreateToolkit() override;
    // 返回此模式所包含的所有命令（工具）的映射
    virtual TMap<FName, TArray<TSharedPtr<FUICommandInfo>>> GetModeCommands() const override;
};
```

### 进阶用法：自定义一个交互式工具

要添加一个新工具，需要遵循 Builder 模式。以 `UMeasureDistanceSampleTool` 为例：
1.  **创建工具构建器** (`UInteractiveToolBuilder` 的子类)，用于判断是否能构建工具并实际构建它。
2.  **创建属性集** (`UInteractiveToolPropertySet` 的子类)，用于在详细面板中暴露可编辑的参数。
3.  **实现工具本身** (`UInteractiveTool` 的子类)，并实现 `IClickDragBehaviorTarget` 等接口来处理输入。

```cpp
// 示例：一个简化的自定义工具结构（非完整代码，仅供参考模式）
// 1. 构建器
UCLASS()
class UMySampleToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()
public:
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override;
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};

// 2. 属性集
UCLASS(Transient)
class UMySampleToolProperties : public UInteractiveToolPropertySet
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = Options)
    float SomeParameter;
};

// 3. 工具实现
UCLASS()
class UMySampleTool : public UInteractiveTool, public IClickDragBehaviorTarget
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void Render(IToolsContextRenderAPI* RenderAPI) override;

    // IClickDragBehaviorTarget 接口实现
    virtual FInputRayHit CanBeginClickDragSequence(const FInputDeviceRay& PressPos) override;
    virtual void OnClickPress(const FInputDeviceRay& PressPos) override;
    virtual void OnClickDrag(const FInputDeviceRay& DragPos) override;
    // ... 其他虚函数

protected:
    UPROPERTY()
    TObjectPtr<UMySampleToolProperties> Properties;
};
```

## Demo 示例

一个最小的、可编译的自定义编辑器模式插件框架，仅包含一个进入时输出日志的“空”模式。

**MyEditorModeModule.h**
```cpp
#pragma once

#include "Modules/ModuleManager.h"

class FMyEditorModeModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MyEditorMode.h**
```cpp
#pragma once

#include "EdMode.h"

UCLASS()
class UMyEditorMode : public UEdMode
{
    GENERATED_BODY()

public:
    const static FEditorModeID EM_MyEditorModeId;

    virtual void Enter() override;
    virtual void Exit() override;
};
```

**MyEditorMode.cpp**
```cpp
#include "MyEditorMode.h"
#include "MyEditorModeModule.h"

#define LOCTEXT_NAMESPACE "MyEditorMode"

const FEditorModeID UMyEditorMode::EM_MyEditorModeId = TEXT("MyEditorMode");

void UMyEditorMode::Enter()
{
    UE_LOG(LogTemp, Warning, TEXT("Entering My Custom Editor Mode!"));
    // 在此初始化你的工具、输入处理器等
    UEdMode::Enter();
}

void UMyEditorMode::Exit()
{
    UE_LOG(LogTemp, Warning, TEXT("Exiting My Custom Editor Mode."));
    // 清理资源
    UEdMode::Exit();
}

#undef LOCTEXT_NAMESPACE
```

**MyEditorModeModule.cpp**
```cpp
#include "MyEditorModeModule.h"
#include "MyEditorMode.h"
#include "EditorModeRegistry.h"

#define LOCTEXT_NAMESPACE "FMyEditorModeModule"

void FMyEditorModeModule::StartupModule()
{
    FEditorModeRegistry::Get().RegisterMode<UMyEditorMode>(
        UMyEditorMode::EM_MyEditorModeId,
        LOCTEXT("MyEditorModeName", "My Custom Mode"),
        FSlateIcon(),
        false);
}

void FMyEditorModeModule::ShutdownModule()
{
    FEditorModeRegistry::Get().UnregisterMode(UMyEditorMode::EM_MyEditorModeId);
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModeModule, MyEditorMode)
```

## 模块依赖

从源码分析，此插件依赖于以下核心模块来实现交互式工具功能。

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 提供 `UInteractiveTool`, `UInteractiveToolBuilder`, `UInteractiveToolPropertySet`, `FInputDeviceRay`, `IToolsContextRenderAPI` 等核心框架类。 |
| `ToolWidgets` | 提供工具面板（Tool Palette）和详细视图（Details View）的 UI 支持。 |
| `EditorFramework` | 提供 `FModeToolkit`, `UEdMode` 等编辑器模式基础设施。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-10-30 | `f2983507` | Replaced include SceneManagement.h with PrimitiveDrawingUtils.h in files that only need primitive dr | 更新头文件依赖，将 `SceneManagement.h` 替换为更精确的 `PrimitiveDrawingUtils.h`。 |
| 2024-02-14 | `0d5635a9` | Removed some headers dependencies on 'FHitResult' and 'FOverlapResult' | 移除了对 `FHitResult` 和 `FOverlapResult` 的一些不必要的头文件依赖。 |
| 2024-01-31 | `681cf949` | Move SampleToolsEditorMode into Editor plugins folder | 首次提交，将插件从旧位置移至当前的 Editor 插件目录。 |

### 维护评价

此插件是一个**实验性**的示例和教学项目。
*   **活跃度**：最近一次更新在 2024 年 10 月，主要是编译和依赖关系的清理，而非功能性更新。
*   **状态**：作为 Epic 官方提供的示例，其代码质量有保障，但不会像生产级插件那样频繁迭代。它更适合作为学习和参考的“静态”模板。
*   **推荐**：**强烈推荐**用于学习交互式工具框架的开发者阅读和模仿。**不推荐**在生产项目中直接使用此插件，而是应将其作为蓝图，构建自己的、经过充分测试的工具集。
*   **警告**：由于是实验性 (`IsBetaVersion=true`) 插件，其 API 和结构可能在引擎更新中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/SampleToolsEditorMode)
- 官方文档: (`.uplugin` 中 `DocsURL` 为空，请参考引擎文档中关于 [Interactive Tools Framework](https://docs.unrealengine.com/5.0/en-US/InteractiveToolsFramework/) 的部分)